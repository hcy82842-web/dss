from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from sqlalchemy.orm import Session

from .api.routes import create_root_router, create_router
from .config import BackendSettings
from .db import Base, build_engine_and_session_factory
from .integrations.deepseek_client import DeepSeekClient
from .ml.inference import SklearnModelService, UnavailableModelService, load_model_bundle
from .services.customer_service import CustomerService
from .services.scoring_service import ScoringService


def create_app(
    settings: BackendSettings | None = None,
    model_service=None,
    llm_client=None,
) -> FastAPI:
    settings = settings or BackendSettings.from_env()
    engine, session_factory = build_engine_and_session_factory(settings.database_url)
    Base.metadata.create_all(bind=engine)

    resolved_model_service = model_service
    if resolved_model_service is None:
        bundle = load_model_bundle(settings.model_artifact_path, settings.model_metadata_path)
        resolved_model_service = SklearnModelService(bundle)

    resolved_llm_client = llm_client or DeepSeekClient(settings)

    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.state.session_factory = session_factory
    app.state.model_service = resolved_model_service
    app.state.llm_client = resolved_llm_client

    def customer_service_factory() -> CustomerService:
        session: Session = app.state.session_factory()
        return _SessionBoundCustomerService(session)

    def scoring_service_factory() -> ScoringService:
        session: Session = app.state.session_factory()
        return _SessionBoundScoringService(session, app.state.model_service, app.state.llm_client)

    app.include_router(create_root_router())
    app.include_router(create_router(customer_service_factory, scoring_service_factory))
    return app


class _SessionBoundCustomerService(CustomerService):
    def __del__(self) -> None:
        self.repository.session.close()


class _SessionBoundScoringService(ScoringService):
    def __del__(self) -> None:
        self.customer_repository.session.close()
def create_default_app() -> FastAPI:
    try:
        return create_app()
    except Exception:
        fallback_settings = BackendSettings.from_env()
        return create_app(
            settings=fallback_settings,
            model_service=UnavailableModelService(),
            llm_client=DeepSeekClient(fallback_settings),
        )
