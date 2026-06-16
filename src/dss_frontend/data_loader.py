from pathlib import Path

import pandas as pd

from .schema import AGE_GROUP_LABELS, BUSINESS_INPUT_COLUMNS, REQUIRED_COLUMNS

REQUIRED_BUSINESS_FIELDS = ["age", "job", "contact", "month", "campaign", "previous"]
OPTIONAL_FIELD_DEFAULTS = {
    "marital": "unknown",
    "education": "unknown",
    "default": "unknown",
    "housing": "unknown",
    "loan": "unknown",
    "duration": 0,
    "pdays": 999,
    "poutcome": "unknown",
}
SCORING_IMPACT_FIELDS = {"contact", "campaign", "previous", "default", "housing", "loan", "poutcome"}
INTEGER_FIELDS = {"age", "duration", "campaign", "pdays", "previous"}


def load_customer_frame(csv_path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path, sep=";")
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    normalized = frame.copy().reset_index(drop=True)
    normalized["age"] = pd.to_numeric(normalized["age"], errors="coerce")
    invalid_age_mask = (
        normalized["age"].isna()
        | normalized["age"].mod(1).ne(0)
        | (normalized["age"] <= 0)
        | (normalized["age"] > 120)
    )
    if invalid_age_mask.any():
        raise ValueError("Invalid age values found")

    normalized["job"] = normalized["job"].astype(str).str.strip().str.lower()
    normalized["month"] = normalized["month"].astype(str).str.strip().str.lower()
    blank_text_columns = [
        column
        for column in ("job", "month")
        if normalized[column].eq("").any() or normalized[column].eq("nan").any()
    ]
    if blank_text_columns:
        raise ValueError(f"Blank values found in columns: {blank_text_columns}")

    normalized["y"] = normalized["y"].astype(str).str.strip().str.lower()
    unknown_response_values = sorted(set(normalized["y"]) - {"yes", "no"})
    if unknown_response_values:
        raise ValueError(f"Unknown response values: {unknown_response_values}")

    normalized["customer_id"] = normalized.index + 1001
    normalized["customer_label"] = normalized["customer_id"].map(lambda value: f"客户 {value}")
    normalized["response_flag"] = normalized["y"].map({"yes": 1, "no": 0}).astype(int)
    normalized["age_group"] = pd.cut(
        normalized["age"],
        bins=[0, 35, 50, 120],
        labels=AGE_GROUP_LABELS,
        include_lowest=True,
    ).astype(str)
    return normalized


def build_manual_scoring_row(raw_values: dict[str, object]) -> dict[str, object]:
    missing_required = [
        field
        for field in REQUIRED_BUSINESS_FIELDS
        if raw_values.get(field) in (None, "", [])
    ]
    if missing_required:
        raise ValueError(f"Missing required business fields: {missing_required}")

    row: dict[str, object] = {}
    for column in BUSINESS_INPUT_COLUMNS:
        value = raw_values.get(column)
        if value in (None, "") and column in OPTIONAL_FIELD_DEFAULTS:
            row[column] = OPTIONAL_FIELD_DEFAULTS[column]
        elif value in (None, ""):
            row[column] = value
        else:
            row[column] = _coerce_field_value(column, value)
    return row


def _coerce_field_value(column: str, value: object) -> object:
    if column in INTEGER_FIELDS and isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return value
        return int(stripped)
    return value


def build_missing_field_notice(row: pd.Series | dict[str, object]) -> dict[str, object]:
    row_data = dict(row)
    missing_fields = [
        column
        for column in BUSINESS_INPUT_COLUMNS
        if row_data.get(column) in (None, "", "unknown")
        or (column == "duration" and row_data.get(column) == 0)
        or (column == "pdays" and row_data.get(column) == 999)
    ]
    completeness_ratio = round((len(BUSINESS_INPUT_COLUMNS) - len(missing_fields)) / len(BUSINESS_INPUT_COLUMNS), 2)
    impactful_missing_fields = [field for field in missing_fields if field in SCORING_IMPACT_FIELDS]
    if impactful_missing_fields:
        impact_text = f"部分关键字段缺失，会影响结果稳定性：{', '.join(impactful_missing_fields)}。"
    elif missing_fields:
        impact_text = f"存在信息缺失，主要影响解释文本完整度：{', '.join(missing_fields)}。"
    else:
        impact_text = "字段完整，可直接参考当前判断结果。"
    return {
        "completeness_ratio": completeness_ratio,
        "missing_fields": missing_fields,
        "impact_text": impact_text,
    }


def load_scoring_frame(csv_path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path, sep=";")
    missing = [column for column in BUSINESS_INPUT_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    normalized = frame.copy().reset_index(drop=True)
    normalized["age"] = pd.to_numeric(normalized["age"], errors="coerce")
    invalid_age_mask = (
        normalized["age"].isna()
        | normalized["age"].mod(1).ne(0)
        | (normalized["age"] <= 0)
        | (normalized["age"] > 120)
    )
    if invalid_age_mask.any():
        raise ValueError("Invalid age values found")

    normalized["job"] = normalized["job"].astype(str).str.strip().str.lower()
    normalized["month"] = normalized["month"].astype(str).str.strip().str.lower()
    blank_text_columns = [
        column
        for column in ("job", "month")
        if normalized[column].eq("").any() or normalized[column].eq("nan").any()
    ]
    if blank_text_columns:
        raise ValueError(f"Blank values found in columns: {blank_text_columns}")

    normalized["customer_id"] = normalized.index + 1001
    normalized["customer_label"] = normalized["customer_id"].map(lambda value: f"客户 {value}")
    normalized["age_group"] = pd.cut(
        normalized["age"],
        bins=[0, 35, 50, 120],
        labels=AGE_GROUP_LABELS,
        include_lowest=True,
    ).astype(str)
    normalized["missing_field_notice"] = normalized.apply(build_missing_field_notice, axis=1)
    return normalized
