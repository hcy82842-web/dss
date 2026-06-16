from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BusinessCustomerCreate(BaseModel):
    age: int
    job: str
    contact: str
    month: str
    campaign: int
    previous: int
    marital: str | None = None
    education: str | None = None
    default: str | None = None
    housing: str | None = None
    loan: str | None = None
    duration: int | None = None
    pdays: int | None = None
    poutcome: str | None = None


class BusinessCustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_label: str
    age: int
    job: str
    marital: str
    education: str
    default: str
    housing: str
    loan: str
    contact: str
    month: str
    duration: int
    campaign: int
    pdays: int
    previous: int
    poutcome: str
    age_group: str
    missing_fields: list[str]
    completeness_ratio: float
    impact_text: str
    created_at: datetime


class BusinessCustomerListResponse(BaseModel):
    items: list[BusinessCustomerRead]


class BusinessCustomerImportResponse(BaseModel):
    success_count: int
    failure_count: int
    failures: list[str]


class BatchScoringRequest(BaseModel):
    customer_ids: list[int] | None = None


class ScoringResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    conversion_probability: float
    priority_level: str
    recommended_channel: str
    product_name: str
    recommended_action: str
    customer_explanation: str
    marketing_script: str
    llm_status: str
    scored_at: datetime


class ScoringResultListResponse(BaseModel):
    items: list[ScoringResultRead]


class BatchScoringResponse(BaseModel):
    processed_count: int
    items: list[ScoringResultRead]
