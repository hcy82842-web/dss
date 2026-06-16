from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas import (
    BatchScoringRequest,
    BatchScoringResponse,
    BusinessCustomerCreate,
    BusinessCustomerImportResponse,
    BusinessCustomerListResponse,
    BusinessCustomerRead,
    ScoringResultListResponse,
    ScoringResultRead,
)


def create_router(customer_service_factory, scoring_service_factory) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/business-customers", response_model=BusinessCustomerRead, status_code=201)
    def create_business_customer(payload: BusinessCustomerCreate):
        service = customer_service_factory()
        customer = service.create_customer(payload.model_dump())
        return customer

    @router.post("/business-customers/import", response_model=BusinessCustomerImportResponse)
    def import_business_customers(file: UploadFile = File(...)):
        content = file.file.read().decode("utf-8")
        service = customer_service_factory()
        return service.import_customers(content)

    @router.get("/business-customers", response_model=BusinessCustomerListResponse)
    def list_business_customers():
        service = customer_service_factory()
        return {"items": service.list_customers()}

    @router.post("/scoring/run/{customer_id}", response_model=ScoringResultRead)
    def run_scoring(customer_id: int):
        service = scoring_service_factory()
        result = service.run_for_customer(customer_id)
        if result is None:
            raise HTTPException(status_code=404, detail="customer not found")
        return result

    @router.post("/scoring/run-batch", response_model=BatchScoringResponse)
    def run_batch_scoring(payload: BatchScoringRequest | None = None):
        service = scoring_service_factory()
        customer_ids = payload.customer_ids if payload is not None else None
        results = service.run_batch(customer_ids)
        return {"processed_count": len(results), "items": results}

    @router.get("/scoring-results", response_model=ScoringResultListResponse)
    def list_scoring_results():
        service = scoring_service_factory()
        return {"items": service.list_results()}

    @router.get("/scoring-results/{customer_id}", response_model=ScoringResultRead)
    def get_latest_scoring_result(customer_id: int):
        service = scoring_service_factory()
        result = service.get_latest_result(customer_id)
        if result is None:
            raise HTTPException(status_code=404, detail="scoring result not found")
        return result

    return router
