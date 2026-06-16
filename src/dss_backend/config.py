from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class BackendSettings:
    app_name: str = "Bank Retail Marketing DSS Backend"
    database_url: str = "sqlite:///artifacts/backend-demo.db"
    model_artifact_path: str = "artifacts/logistic_regression.joblib"
    model_metadata_path: str = "artifacts/model_metadata.json"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> "BackendSettings":
        defaults = cls()
        return cls(
            app_name=os.getenv("DSS_BACKEND_APP_NAME", defaults.app_name),
            database_url=os.getenv("DSS_DATABASE_URL", defaults.database_url),
            model_artifact_path=os.getenv("DSS_MODEL_ARTIFACT_PATH", defaults.model_artifact_path),
            model_metadata_path=os.getenv("DSS_MODEL_METADATA_PATH", defaults.model_metadata_path),
            deepseek_api_key=os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY", defaults.deepseek_api_key),
            deepseek_base_url=os.getenv("LLM_BASE_URL") or os.getenv("DEEPSEEK_BASE_URL", defaults.deepseek_base_url),
            deepseek_model=os.getenv("LLM_MODEL") or os.getenv("DEEPSEEK_MODEL", defaults.deepseek_model),
            deepseek_timeout_seconds=float(
                os.getenv("LLM_TIMEOUT_SECONDS")
                or os.getenv("DEEPSEEK_TIMEOUT_SECONDS", str(defaults.deepseek_timeout_seconds))
            ),
        )
