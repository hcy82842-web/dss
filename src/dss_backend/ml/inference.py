from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import joblib
import pandas as pd

from src.dss_frontend.schema import MODEL_FEATURE_COLUMNS


@dataclass(slots=True)
class ModelBundle:
    pipeline: object
    metadata: dict


def load_model_bundle(model_path: str | Path, metadata_path: str | Path) -> ModelBundle:
    return ModelBundle(
        pipeline=joblib.load(model_path),
        metadata=json.loads(Path(metadata_path).read_text(encoding="utf-8")),
    )


def predict_probability_for_customer(bundle: ModelBundle, customer: dict[str, object]) -> float:
    frame = pd.DataFrame([{column: customer[column] for column in MODEL_FEATURE_COLUMNS}])
    probability = bundle.pipeline.predict_proba(frame)[0][1]
    return round(float(probability), 4)


class SklearnModelService:
    def __init__(self, bundle: ModelBundle) -> None:
        self.bundle = bundle

    def predict_probability(self, customer: dict[str, object]) -> float:
        return predict_probability_for_customer(self.bundle, customer)


class UnavailableModelService:
    def predict_probability(self, customer: dict[str, object]) -> float:
        raise RuntimeError("model artifact is unavailable")
