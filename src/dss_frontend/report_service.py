from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.dss_backend.decision_policy import build_decision_from_probability
from src.dss_backend.ml.inference import ModelBundle, predict_probability_for_customer

from .data_loader import build_missing_field_notice, build_manual_scoring_row, load_customer_frame
from .schema import BUSINESS_INPUT_COLUMNS, MODEL_FEATURE_COLUMNS


METRIC_EXPLANATIONS = {
    "auc": "衡量模型把购买客户排在更高概率位置的能力，越接近 1 越好。",
    "accuracy": "验证集中预测正确的总体比例，但在类别不平衡数据上不能单独作为判断依据。",
    "precision": "模型预测会购买的客户中，实际购买的比例，反映营销触达的准确性。",
    "recall": "真实购买客户中被模型识别出来的比例，反映潜在客户覆盖能力。",
    "f1": "Precision 和 Recall 的综合指标，适合观察准确性与覆盖率的平衡。",
}


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
    error_type = build_prediction_error_type(customer["actual_label"], customer["predicted_label"])
    return {
        "customer_id": int(customer["customer_id"]),
        "source": "validation_set",
        "features": {column: customer[column] for column in BUSINESS_INPUT_COLUMNS},
        "model_result": {
            "conversion_probability": float(customer["conversion_probability"]),
            "predicted_label": customer["predicted_label"],
            "actual_label": customer["actual_label"],
            "is_correct": bool(customer["is_correct"]),
            "error_type": error_type,
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
            "error_type": "无真实标签",
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


def build_metric_cards(metrics: dict[str, Any]) -> list[dict[str, str]]:
    labels = {
        "auc": "AUC",
        "accuracy": "Accuracy",
        "precision": "Precision",
        "recall": "Recall",
        "f1": "F1",
    }
    return [
        {
            "key": key,
            "label": labels[key],
            "value": f"{float(metrics[key]):.4f}",
            "explanation": METRIC_EXPLANATIONS[key],
        }
        for key in ["auc", "accuracy", "precision", "recall", "f1"]
    ]


def build_validation_result_summary(validation_frame: pd.DataFrame) -> dict[str, int | float]:
    total = int(len(validation_frame))
    correct = int(validation_frame["is_correct"].sum())
    actual_yes = int((validation_frame["actual_label"] == "yes").sum())
    predicted_yes = int((validation_frame["predicted_label"] == "yes").sum())
    return {
        "total": total,
        "correct": correct,
        "incorrect": total - correct,
        "actual_yes": actual_yes,
        "predicted_yes": predicted_yes,
        "accuracy": round(correct / total, 4) if total else 0.0,
    }


def build_confusion_matrix_business_rows(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = metrics["confusion_matrix"]["values"]
    true_no_pred_no = int(matrix[0][0])
    true_no_pred_yes = int(matrix[0][1])
    true_yes_pred_no = int(matrix[1][0])
    true_yes_pred_yes = int(matrix[1][1])
    return [
        {
            "业务含义": "正确识别未购买客户",
            "矩阵位置": "真实 no / 预测 no",
            "数量": true_no_pred_no,
            "管理解释": "可减少不必要的营销资源投入。",
        },
        {
            "业务含义": "误判为购买客户",
            "矩阵位置": "真实 no / 预测 yes",
            "数量": true_no_pred_yes,
            "管理解释": "可能造成额外触达成本，适合低成本渠道复核。",
        },
        {
            "业务含义": "漏掉购买客户",
            "矩阵位置": "真实 yes / 预测 no",
            "数量": true_yes_pred_no,
            "管理解释": "代表错失营销机会，是后续优化重点。",
        },
        {
            "业务含义": "正确识别购买客户",
            "矩阵位置": "真实 yes / 预测 yes",
            "数量": true_yes_pred_yes,
            "管理解释": "可作为优先触达客户池的重要来源。",
        },
    ]


def build_priority_distribution(validation_frame: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        validation_frame.groupby("priority_level", dropna=False)
        .agg(
            客户数=("customer_id", "count"),
            真实购买数=("actual_label", lambda values: int((values == "yes").sum())),
            平均预测概率=("conversion_probability", "mean"),
        )
        .reset_index()
        .rename(columns={"priority_level": "营销优先级"})
    )
    grouped["真实购买率"] = (grouped["真实购买数"] / grouped["客户数"]).round(4)
    grouped["平均预测概率"] = grouped["平均预测概率"].round(4)
    order = {"高价值客户": 0, "中价值客户": 1, "低响应客户": 2}
    grouped["_order"] = grouped["营销优先级"].map(order).fillna(99)
    return grouped.sort_values("_order").drop(columns=["_order"]).reset_index(drop=True)


def build_probability_distribution(validation_frame: pd.DataFrame) -> pd.DataFrame:
    frame = validation_frame[["actual_label", "conversion_probability"]].copy()
    frame["真实标签"] = frame["actual_label"].map({"no": "未购买 no", "yes": "购买 yes"})
    frame["预测概率"] = frame["conversion_probability"].astype(float)
    return frame[["真实标签", "预测概率"]]


def build_prediction_error_type(actual_label: Any, predicted_label: Any) -> str:
    if actual_label is None:
        return "无真实标签"
    if actual_label == predicted_label:
        return "预测正确"
    if actual_label == "no" and predicted_label == "yes":
        return "假阳性：实际未购买，但模型预测会购买"
    if actual_label == "yes" and predicted_label == "no":
        return "假阴性：实际购买，但模型没有识别出来"
    return "预测不一致"


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
