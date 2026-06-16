from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.dss_backend.decision_policy import build_decision_from_probability
from src.dss_backend.ml.inference import ModelBundle, predict_probability_for_customer

from .data_loader import build_missing_field_notice, build_manual_scoring_row, load_customer_frame
from .schema import BUSINESS_INPUT_COLUMNS, MODEL_FEATURE_COLUMNS


def load_evaluation_summary(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_validation_predictions(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "is_correct" in frame.columns:
        frame["is_correct"] = frame["is_correct"].astype(bool)
    return frame


def build_dataset_summary(csv_path: str | Path, evaluation_summary: dict[str, Any]) -> dict[str, Any]:
    frame = load_customer_frame(csv_path)
    return {
        "sample_count": int(len(frame)),
        "raw_feature_count": int(len(frame.columns)),
        "model_feature_count": len(MODEL_FEATURE_COLUMNS),
        "target_distribution": frame["y"].value_counts().to_dict(),
        "split": evaluation_summary["split"],
        "excluded_columns": evaluation_summary.get("excluded_columns", {}),
    }


def build_case_options(validation_frame: pd.DataFrame, representative_cases: dict[str, int | None]) -> list[int]:
    ordered_ids: list[int] = []
    for value in representative_cases.values():
        if value is not None and value not in ordered_ids:
            ordered_ids.append(int(value))

    top_cases = (
        validation_frame.sort_values("conversion_probability", ascending=False)["customer_id"]
        .head(20)
        .astype(int)
        .tolist()
    )
    for customer_id in top_cases:
        if customer_id not in ordered_ids:
            ordered_ids.append(customer_id)
    return ordered_ids


def build_prediction_context_from_validation(row: pd.Series, feature_influences: list[dict[str, Any]]) -> dict[str, Any]:
    customer = row.to_dict()
    return {
        "customer_id": int(customer["customer_id"]),
        "source": "validation_set",
        "features": {column: customer[column] for column in BUSINESS_INPUT_COLUMNS},
        "model_result": {
            "conversion_probability": float(customer["conversion_probability"]),
            "predicted_label": customer["predicted_label"],
            "actual_label": customer["actual_label"],
            "is_correct": bool(customer["is_correct"]),
            "priority_level": customer["priority_level"],
            "recommended_channel": customer["recommended_channel"],
            "product_name": customer["product_name"],
            "recommended_action": customer["recommended_action"],
        },
        "explanation_context": _build_explanation_context(customer, feature_influences, 1.0),
    }


def build_prediction_context_from_manual(raw_values: dict[str, object], bundle: ModelBundle) -> dict[str, Any]:
    row = build_manual_scoring_row(raw_values)
    probability = predict_probability_for_customer(bundle, row)
    decision = build_decision_from_probability(probability)
    notice = build_missing_field_notice(row)
    return {
        "customer_id": 0,
        "source": "manual_input",
        "features": row,
        "model_result": {
            "conversion_probability": probability,
            "predicted_label": "yes" if probability >= 0.5 else "no",
            "actual_label": None,
            "is_correct": None,
            "priority_level": decision["priority_level"],
            "recommended_channel": decision["recommended_channel"],
            "product_name": decision["product_name"],
            "recommended_action": decision["recommended_action"],
        },
        "explanation_context": _build_explanation_context(
            row,
            bundle.metadata.get("feature_influences", []),
            float(notice["completeness_ratio"]),
        )
        | {"missing_fields": notice["missing_fields"], "impact_text": notice["impact_text"]},
    }


def _build_explanation_context(
    customer: dict[str, Any],
    feature_influences: list[dict[str, Any]],
    data_completeness: float,
) -> dict[str, Any]:
    matched_positive: list[str] = []
    matched_negative: list[str] = []
    for influence in feature_influences:
        feature = str(influence["feature"])
        direction = str(influence["direction"])
        if _feature_matches_customer(feature, customer):
            if "提高" in direction:
                matched_positive.append(feature)
            else:
                matched_negative.append(feature)
    return {
        "positive_factors": matched_positive[:4],
        "negative_factors": matched_negative[:4],
        "data_completeness": data_completeness,
    }


def _feature_matches_customer(feature: str, customer: dict[str, Any]) -> bool:
    for column in MODEL_FEATURE_COLUMNS:
        value = customer.get(column)
        if feature == column:
            return True
        if value is not None and feature == f"{column}_{value}":
            return True
    return False
