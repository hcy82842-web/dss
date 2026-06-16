from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dss_frontend.data_loader import (
    build_manual_scoring_row,
    build_missing_field_notice,
    load_customer_frame,
    load_scoring_frame,
)


def test_load_customer_frame_adds_display_columns(tmp_path: Path):
    csv_path = tmp_path / "bank.csv"
    pd.DataFrame(
        [
            {
                "age": 35,
                "job": "Management",
                "marital": "married",
                "education": "university.degree",
                "default": "no",
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "month": "MaY",
                "duration": 180,
                "campaign": 2,
                "pdays": 999,
                "previous": 0,
                "poutcome": "nonexistent",
                "y": " YES ",
            }
        ]
    ).to_csv(csv_path, index=False, sep=";")

    frame = load_customer_frame(csv_path)

    assert "customer_id" in frame.columns
    assert "customer_label" in frame.columns
    assert "response_flag" in frame.columns
    assert "age_group" in frame.columns
    assert frame.loc[0, "customer_label"] == "\u5ba2\u6237 1001"
    assert frame.loc[0, "response_flag"] == 1
    assert frame.loc[0, "age_group"] == "35\u53ca\u4ee5\u4e0b"
    assert frame.loc[0, "month"] == "may"
    assert frame.loc[0, "job"] == "management"


def test_load_customer_frame_rejects_missing_required_columns(tmp_path: Path):
    csv_path = tmp_path / "broken.csv"
    pd.DataFrame([{"age": 42, "job": "management"}]).to_csv(csv_path, index=False, sep=";")

    try:
        load_customer_frame(csv_path)
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing columns")


def test_load_customer_frame_assigns_consistent_age_groups(tmp_path: Path):
    csv_path = tmp_path / "ages.csv"
    pd.DataFrame(
        [
            {**_base_customer_row(), "age": 35, "job": "services", "month": "jun", "y": "yes"},
            {**_base_customer_row(), "age": 36, "job": "admin.", "month": "jul", "y": "no"},
            {**_base_customer_row(), "age": 51, "job": "technician", "month": "aug", "y": "yes"},
            {**_base_customer_row(), "age": 50, "job": "blue-collar", "month": "sep", "y": "no"},
            {**_base_customer_row(), "age": 120, "job": "retired", "month": "oct", "y": "yes"},
        ]
    ).to_csv(csv_path, index=False, sep=";")

    frame = load_customer_frame(csv_path)

    assert frame["age_group"].tolist() == ["35\u53ca\u4ee5\u4e0b", "36-50", "51+", "36-50", "51+"]


def test_load_customer_frame_rejects_unknown_response_values(tmp_path: Path):
    csv_path = tmp_path / "unknown-response.csv"
    pd.DataFrame([{**_base_customer_row(), "y": "maybe"}]).to_csv(csv_path, index=False, sep=";")

    try:
        load_customer_frame(csv_path)
    except ValueError as exc:
        assert "Unknown response values" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown y values")


def test_load_customer_frame_rejects_invalid_age_values(tmp_path: Path):
    invalid_rows = [
        ("missing-age.csv", None),
        ("text-age.csv", "unknown"),
        ("decimal-age.csv", 35.5),
        ("zero-age.csv", 0),
        ("out-of-range-age.csv", 130),
    ]

    for filename, age_value in invalid_rows:
        csv_path = tmp_path / filename
        row = _base_customer_row()
        row["age"] = age_value
        pd.DataFrame([row]).to_csv(csv_path, index=False, sep=";")

        try:
            load_customer_frame(csv_path)
        except ValueError as exc:
            assert "Invalid age values" in str(exc)
        else:
            raise AssertionError("Expected ValueError for invalid age values")


def test_load_customer_frame_rejects_blank_job_or_month(tmp_path: Path):
    invalid_rows = [
        ("blank-job.csv", "   ", "may"),
        ("blank-month.csv", "management", ""),
    ]

    for filename, job_value, month_value in invalid_rows:
        csv_path = tmp_path / filename
        row = _base_customer_row()
        row["job"] = job_value
        row["month"] = month_value
        pd.DataFrame([row]).to_csv(csv_path, index=False, sep=";")

        try:
            load_customer_frame(csv_path)
        except ValueError as exc:
            assert "Blank values found" in str(exc)
        else:
            raise AssertionError("Expected ValueError for blank job/month values")


def test_load_scoring_frame_accepts_business_input_without_target_column(tmp_path: Path):
    csv_path = tmp_path / "scoring.csv"
    pd.DataFrame(
        [
            {
                "age": 41,
                "job": "management",
                "marital": "married",
                "education": "university.degree",
                "default": "no",
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "month": "jun",
                "duration": 210,
                "campaign": 1,
                "pdays": 999,
                "previous": 1,
                "poutcome": "success",
            }
        ]
    ).to_csv(csv_path, index=False, sep=";")

    frame = load_scoring_frame(csv_path)

    assert "y" not in frame.columns
    assert "response_flag" not in frame.columns
    assert frame.loc[0, "customer_label"] == "客户 1001"
    assert frame.loc[0, "age_group"] == "36-50"


def test_build_manual_scoring_row_fills_optional_fields_with_defaults():
    row = build_manual_scoring_row(
        {
            "age": 39,
            "job": "management",
            "contact": "cellular",
            "month": "may",
            "campaign": 2,
            "previous": 1,
        }
    )

    assert row["marital"] == "unknown"
    assert row["education"] == "unknown"
    assert row["default"] == "unknown"
    assert row["housing"] == "unknown"
    assert row["loan"] == "unknown"
    assert row["duration"] == 0
    assert row["pdays"] == 999
    assert row["poutcome"] == "unknown"


def test_build_manual_scoring_row_rejects_missing_required_fields():
    try:
        build_manual_scoring_row(
            {
                "age": 39,
                "job": "management",
                "month": "may",
                "campaign": 2,
                "previous": 1,
            }
        )
    except ValueError as exc:
        assert "contact" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing required business fields")


def test_build_missing_field_notice_summarizes_completeness_and_impact():
    row = build_manual_scoring_row(
        {
            "age": 39,
            "job": "management",
            "contact": "cellular",
            "month": "may",
            "campaign": 2,
            "previous": 1,
        }
    )

    notice = build_missing_field_notice(row)

    assert notice["completeness_ratio"] < 1.0
    assert "default" in notice["missing_fields"]
    assert "会影响结果" in notice["impact_text"]


def test_build_manual_scoring_row_accepts_numeric_fields_from_text_inputs():
    row = build_manual_scoring_row(
        {
            "age": "39",
            "job": "management",
            "contact": "cellular",
            "month": "may",
            "campaign": "2",
            "previous": "1",
            "duration": "180",
            "pdays": "999",
        }
    )

    assert row["age"] == 39
    assert row["campaign"] == 2
    assert row["previous"] == 1
    assert row["duration"] == 180
    assert row["pdays"] == 999


def _base_customer_row() -> dict[str, object]:
    return {
        "age": 42,
        "job": "management",
        "marital": "married",
        "education": "university.degree",
        "default": "no",
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "month": "may",
        "duration": 180,
        "campaign": 2,
        "pdays": 999,
        "previous": 0,
        "poutcome": "nonexistent",
        "y": "yes",
    }
