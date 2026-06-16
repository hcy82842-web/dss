from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.dss_frontend.data_loader import load_customer_frame
from src.dss_frontend.schema import MODEL_EXCLUDED_COLUMNS, MODEL_FEATURE_COLUMNS
from src.dss_backend.decision_policy import build_decision_from_probability

CATEGORICAL_COLUMNS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "poutcome",
]
NUMERICAL_COLUMNS = ["age", "campaign", "pdays", "previous"]


def train_logistic_regression_model(
    csv_path: str | Path,
    model_path: str | Path,
    metadata_path: str | Path,
    validation_predictions_path: str | Path | None = None,
    evaluation_summary_path: str | Path | None = None,
) -> dict[str, float]:
    raw_frame = pd.read_csv(csv_path, sep=";")
    frame = load_customer_frame(csv_path)
    features = frame[MODEL_FEATURE_COLUMNS]
    target = frame["response_flag"]

    train_frame, validation_frame = train_test_split(
        frame,
        test_size=0.3,
        random_state=42,
        stratify=target,
    )
    X_train = train_frame[MODEL_FEATURE_COLUMNS]
    y_train = train_frame["response_flag"]
    X_test = validation_frame[MODEL_FEATURE_COLUMNS]
    y_test = validation_frame["response_flag"]

    preprocessing = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
            ("numeric", "passthrough", NUMERICAL_COLUMNS),
        ]
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("classifier", LogisticRegression(max_iter=3000, class_weight="balanced", solver="liblinear")),
        ]
    )
    pipeline.fit(X_train, y_train)

    test_probability = pipeline.predict_proba(X_test)[:, 1]
    test_prediction = pipeline.predict(X_test)
    matrix = confusion_matrix(y_test, test_prediction, labels=[0, 1])
    metrics = {
        "auc": round(float(roc_auc_score(y_test, test_probability)), 4),
        "accuracy": round(float(accuracy_score(y_test, test_prediction)), 4),
        "precision": round(float(precision_score(y_test, test_prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, test_prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, test_prediction, zero_division=0)), 4),
        "positive_class_recall": round(float(recall_score(y_test, test_prediction, zero_division=0)), 4),
        "confusion_matrix": {
            "labels": ["no", "yes"],
            "values": matrix.tolist(),
        },
    }
    feature_influences = _extract_feature_influences(pipeline)
    validation_predictions = _build_validation_predictions(validation_frame, test_probability)

    model_path = Path(model_path)
    metadata_path = Path(metadata_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    metadata_path.write_text(
        json.dumps(
            {
                "model_name": "logistic_regression",
                "feature_columns": MODEL_FEATURE_COLUMNS,
                "excluded_columns": MODEL_EXCLUDED_COLUMNS,
                "split": {
                    "strategy": "train_test_split",
                    "train_ratio": 0.7,
                    "validation_ratio": 0.3,
                    "random_state": 42,
                    "stratify": "y",
                    "train_size": int(len(train_frame)),
                    "validation_size": int(len(validation_frame)),
                },
                "metrics": metrics,
                "feature_influences": feature_influences,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if validation_predictions_path is not None:
        validation_predictions_path = Path(validation_predictions_path)
        validation_predictions_path.parent.mkdir(parents=True, exist_ok=True)
        validation_predictions.to_csv(validation_predictions_path, index=False)

    if evaluation_summary_path is not None:
        evaluation_summary_path = Path(evaluation_summary_path)
        evaluation_summary_path.parent.mkdir(parents=True, exist_ok=True)
        evaluation_summary_path.write_text(
            json.dumps(
                {
                    "dataset": {
                    "source": "UCI Bank Marketing bank-additional-full.csv",
                    "sample_count": int(len(frame)),
                    "raw_feature_count": int(len(raw_frame.columns)),
                    "model_feature_count": int(len(MODEL_FEATURE_COLUMNS)),
                    "target_distribution": frame["y"].value_counts().to_dict(),
                },
                    "split": {
                        "train_size": int(len(train_frame)),
                        "validation_size": int(len(validation_frame)),
                        "validation_ratio": 0.3,
                        "stratified_by": "y",
                    },
                    "metrics": metrics,
                    "feature_influences": feature_influences,
                    "representative_cases": _pick_representative_cases(validation_predictions),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return metrics


def _extract_feature_influences(pipeline: Pipeline) -> list[dict[str, object]]:
    preprocessing = pipeline.named_steps["preprocessing"]
    classifier = pipeline.named_steps["classifier"]
    feature_names = preprocessing.get_feature_names_out()
    coefficients = classifier.coef_[0]
    ranked = sorted(
        zip(feature_names, coefficients),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    return [
        {
            "feature": _clean_feature_name(name),
            "coefficient": round(float(coef), 4),
            "direction": "提高购买概率" if coef > 0 else "降低购买概率",
        }
        for name, coef in ranked[:12]
    ]


def _clean_feature_name(raw_name: str) -> str:
    for prefix in ("categorical__", "numeric__"):
        if raw_name.startswith(prefix):
            return raw_name[len(prefix) :]
    return raw_name


def _build_validation_predictions(validation_frame: pd.DataFrame, probabilities) -> pd.DataFrame:
    rows = validation_frame.reset_index(drop=True).copy()
    rows["conversion_probability"] = [round(float(value), 4) for value in probabilities]
    rows["predicted_label"] = rows["conversion_probability"].map(lambda value: "yes" if value >= 0.5 else "no")
    rows["actual_label"] = rows["y"]
    rows["is_correct"] = rows["predicted_label"] == rows["actual_label"]

    decisions = rows["conversion_probability"].map(build_decision_from_probability)
    rows["priority_level"] = decisions.map(lambda item: item["priority_level"])
    rows["recommended_channel"] = decisions.map(lambda item: item["recommended_channel"])
    rows["product_name"] = decisions.map(lambda item: item["product_name"])
    rows["recommended_action"] = decisions.map(lambda item: item["recommended_action"])
    rows["source"] = "validation_set"
    return rows


def _pick_representative_cases(validation_predictions: pd.DataFrame) -> dict[str, int | None]:
    cases = {
        "high_probability_correct_yes": _first_customer_id(
            validation_predictions.loc[
                (validation_predictions["actual_label"] == "yes")
                & (validation_predictions["predicted_label"] == "yes")
            ].sort_values("conversion_probability", ascending=False)
        ),
        "medium_probability_case": _first_customer_id(
            validation_predictions.loc[
                validation_predictions["conversion_probability"].between(0.4, 0.7, inclusive="left")
            ].sort_values("conversion_probability", ascending=False)
        ),
        "low_probability_correct_no": _first_customer_id(
            validation_predictions.loc[
                (validation_predictions["actual_label"] == "no")
                & (validation_predictions["predicted_label"] == "no")
            ].sort_values("conversion_probability", ascending=True)
        ),
        "misclassified_case": _first_customer_id(
            validation_predictions.loc[~validation_predictions["is_correct"]].sort_values(
                "conversion_probability", ascending=False
            )
        ),
    }
    return cases


def _first_customer_id(frame: pd.DataFrame) -> int | None:
    if frame.empty:
        return None
    return int(frame.iloc[0]["customer_id"])
