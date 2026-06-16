from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_backend.ml.training import train_logistic_regression_model


def main() -> None:
    csv_candidates = [
        Path("data/bank-additional-full.csv"),
    ]
    csv_path = next((candidate for candidate in csv_candidates if candidate.exists()), None)
    if csv_path is None:
        raise FileNotFoundError("Cannot find bank-additional-full.csv")

    metrics = train_logistic_regression_model(
        csv_path=csv_path,
        model_path="artifacts/logistic_regression.joblib",
        metadata_path="artifacts/model_metadata.json",
    )
    print(metrics)


if __name__ == "__main__":
    main()
