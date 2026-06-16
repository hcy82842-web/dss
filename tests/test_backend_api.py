from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_backend.config import BackendSettings
from src.dss_backend.main import create_app


class StubModelService:
    def predict_probability(self, customer: dict) -> float:
        return 0.82


class FailingLlmClient:
    def generate_customer_messages(self, customer: dict, decision: dict) -> dict[str, str]:
        raise RuntimeError("llm unavailable")


def test_create_customer_and_run_scoring_with_llm_fallback(tmp_path: Path):
    client = TestClient(
        create_app(
            settings=BackendSettings(
                database_url=f"sqlite:///{tmp_path / 'app.db'}",
                model_artifact_path=str(tmp_path / "unused.joblib"),
                model_metadata_path=str(tmp_path / "unused.json"),
                deepseek_api_key="test-key",
            ),
            model_service=StubModelService(),
            llm_client=FailingLlmClient(),
        )
    )

    create_response = client.post(
        "/api/business-customers",
        json={
            "age": 39,
            "job": "management",
            "contact": "cellular",
            "month": "may",
            "campaign": 2,
            "previous": 1,
        },
    )
    assert create_response.status_code == 201
    customer_id = create_response.json()["id"]
    assert create_response.json()["completeness_ratio"] < 1.0

    scoring_response = client.post(f"/api/scoring/run/{customer_id}")
    assert scoring_response.status_code == 200
    assert scoring_response.json()["llm_status"] == "failed_fallback"
    assert 0.0 <= scoring_response.json()["conversion_probability"] <= 1.0

    latest_response = client.get(f"/api/scoring-results/{customer_id}")
    assert latest_response.status_code == 200
    assert latest_response.json()["customer_id"] == customer_id
    assert latest_response.json()["llm_status"] == "failed_fallback"


def test_import_business_customers_csv_and_query_list(tmp_path: Path):
    client = TestClient(
        create_app(
            settings=BackendSettings(
                database_url=f"sqlite:///{tmp_path / 'import.db'}",
                model_artifact_path=str(tmp_path / "unused.joblib"),
                model_metadata_path=str(tmp_path / "unused.json"),
                deepseek_api_key="test-key",
            ),
            model_service=StubModelService(),
            llm_client=FailingLlmClient(),
        )
    )

    csv_content = (
        "age;job;marital;education;default;housing;loan;contact;month;duration;campaign;pdays;previous;poutcome\n"
        "41;management;married;university.degree;no;yes;no;cellular;may;180;1;999;1;success\n"
        "34;technician;single;professional.course;no;no;yes;telephone;jun;120;3;999;0;nonexistent\n"
    )

    import_response = client.post(
        "/api/business-customers/import",
        files={"file": ("customers.csv", csv_content, "text/csv")},
    )
    assert import_response.status_code == 200
    assert import_response.json()["success_count"] == 2
    assert import_response.json()["failure_count"] == 0

    list_response = client.get("/api/business-customers")
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 2


def test_health_endpoint_reports_ok(tmp_path: Path):
    client = TestClient(
        create_app(
            settings=BackendSettings(
                database_url=f"sqlite:///{tmp_path / 'health.db'}",
                model_artifact_path=str(tmp_path / "unused.joblib"),
                model_metadata_path=str(tmp_path / "unused.json"),
                deepseek_api_key="test-key",
            ),
            model_service=StubModelService(),
            llm_client=FailingLlmClient(),
        )
    )

    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint_guides_user_to_frontend(tmp_path: Path):
    client = TestClient(
        create_app(
            settings=BackendSettings(
                database_url=f"sqlite:///{tmp_path / 'root.db'}",
                model_artifact_path=str(tmp_path / "unused.joblib"),
                model_metadata_path=str(tmp_path / "unused.json"),
                deepseek_api_key="test-key",
            ),
            model_service=StubModelService(),
            llm_client=FailingLlmClient(),
        )
    )

    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert "后端已启动" in payload["message"]
    assert payload["frontend_url"] == "http://127.0.0.1:8501"
    assert payload["health_url"].endswith("/api/health")
