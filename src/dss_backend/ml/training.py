from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.dss_frontend.data_loader import load_customer_frame
from src.dss_frontend.schema import MODEL_EXCLUDED_COLUMNS, MODEL_FEATURE_COLUMNS

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
) -> dict[str, float]:
    frame = load_customer_frame(csv_path)
    features = frame[MODEL_FEATURE_COLUMNS]
    target = frame["response_flag"]

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.3,
        random_state=42,
        stratify=target,
    )

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
                "metrics": metrics,
                "feature_influences": feature_influences,
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
