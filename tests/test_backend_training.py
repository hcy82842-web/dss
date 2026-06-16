from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_backend.ml.training import train_logistic_regression_model
from src.dss_backend.ml.inference import load_model_bundle, predict_probability_for_customer


def test_train_and_load_logistic_regression_model(tmp_path: Path):
    csv_path = tmp_path / "bank.csv"
    model_path = tmp_path / "logistic_regression.joblib"
    metadata_path = tmp_path / "model_metadata.json"
    pd.DataFrame(
        [
            _training_row(41, "management", "cellular", "may", 1, 2, "yes"),
            _training_row(35, "technician", "telephone", "jun", 4, 0, "no"),
            _training_row(56, "retired", "cellular", "nov", 2, 1, "yes"),
            _training_row(31, "services", "telephone", "jul", 5, 0, "no"),
            _training_row(44, "admin.", "cellular", "aug", 1, 3, "yes"),
            _training_row(29, "blue-collar", "telephone", "oct", 6, 0, "no"),
        ]
    ).to_csv(csv_path, sep=";", index=False)

    metrics = train_logistic_regression_model(csv_path, model_path, metadata_path)
    bundle = load_model_bundle(model_path, metadata_path)
    probability = predict_probability_for_customer(
        bundle,
        {
            "age": 39,
            "job": "management",
            "marital": "married",
            "education": "university.degree",
            "default": "no",
            "housing": "yes",
            "loan": "no",
            "contact": "cellular",
            "month": "may",
            "duration": 99999,
            "campaign": 2,
            "pdays": 999,
            "previous": 1,
            "poutcome": "success",
        },
    )

    assert model_path.exists()
    assert metadata_path.exists()
    assert 0.0 <= metrics["auc"] <= 1.0
    assert 0.0 <= metrics["precision"] <= 1.0
    assert 0.0 <= metrics["recall"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert 0.0 <= probability <= 1.0
    assert bundle.metadata["model_name"] == "logistic_regression"
    assert "duration" not in bundle.metadata["feature_columns"]
    assert "duration" in bundle.metadata["excluded_columns"]
    assert "confusion_matrix" in bundle.metadata["metrics"]


def _training_row(age: int, job: str, contact: str, month: str, campaign: int, previous: int, y: str) -> dict[str, object]:
    return {
        "age": age,
        "job": job,
        "marital": "married",
        "education": "university.degree",
        "default": "no",
        "housing": "yes" if y == "yes" else "no",
        "loan": "no",
        "contact": contact,
        "month": month,
        "duration": 180 if y == "yes" else 90,
        "campaign": campaign,
        "pdays": 999,
        "previous": previous,
        "poutcome": "success" if y == "yes" else "nonexistent",
        "y": y,
    }
