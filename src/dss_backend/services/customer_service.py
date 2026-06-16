from __future__ import annotations

from io import StringIO

import pandas as pd
from sqlalchemy.orm import Session

from src.dss_frontend.data_loader import build_manual_scoring_row, build_missing_field_notice, load_scoring_frame
from src.dss_frontend.schema import AGE_GROUP_LABELS

from ..repositories.business_customer_repository import BusinessCustomerRepository


class CustomerService:
    def __init__(self, session: Session) -> None:
        self.repository = BusinessCustomerRepository(session)

    def create_customer(self, payload: dict) -> object:
        row = build_manual_scoring_row(payload)
        normalized_payload = self._normalize_customer_payload(row)
        return self.repository.create(normalized_payload)

    def import_customers(self, csv_text: str) -> dict[str, object]:
        frame = load_scoring_frame(StringIO(csv_text))
        payloads = []
        for _, row in frame.iterrows():
            payloads.append(
                {
                    "age": int(row["age"]),
                    "job": str(row["job"]),
                    "marital": str(row["marital"]),
                    "education": str(row["education"]),
                    "default": str(row["default"]),
                    "housing": str(row["housing"]),
                    "loan": str(row["loan"]),
                    "contact": str(row["contact"]),
                    "month": str(row["month"]),
                    "duration": int(row["duration"]),
                    "campaign": int(row["campaign"]),
                    "pdays": int(row["pdays"]),
                    "previous": int(row["previous"]),
                    "poutcome": str(row["poutcome"]),
                    "age_group": str(row["age_group"]),
                    "missing_fields": list(row["missing_field_notice"]["missing_fields"]),
                    "completeness_ratio": float(row["missing_field_notice"]["completeness_ratio"]),
                    "impact_text": str(row["missing_field_notice"]["impact_text"]),
                }
            )
        created = self.repository.bulk_create(payloads)
        return {"success_count": len(created), "failure_count": 0, "failures": []}

    def list_customers(self) -> list[object]:
        return self.repository.list_all()

    def get_customer(self, customer_id: int) -> object | None:
        return self.repository.get(customer_id)

    def _normalize_customer_payload(self, row: dict[str, object]) -> dict[str, object]:
        notice = build_missing_field_notice(row)
        return {
            "age": int(row["age"]),
            "job": str(row["job"]).strip().lower(),
            "marital": str(row["marital"]),
            "education": str(row["education"]),
            "default": str(row["default"]),
            "housing": str(row["housing"]),
            "loan": str(row["loan"]),
            "contact": str(row["contact"]).strip().lower(),
            "month": str(row["month"]).strip().lower(),
            "duration": int(row["duration"]),
            "campaign": int(row["campaign"]),
            "pdays": int(row["pdays"]),
            "previous": int(row["previous"]),
            "poutcome": str(row["poutcome"]),
            "age_group": _age_group_for(int(row["age"])),
            "missing_fields": notice["missing_fields"],
            "completeness_ratio": float(notice["completeness_ratio"]),
            "impact_text": str(notice["impact_text"]),
        }


def _age_group_for(age: int) -> str:
    if age <= 35:
        return AGE_GROUP_LABELS[0]
    if age <= 50:
        return AGE_GROUP_LABELS[1]
    return AGE_GROUP_LABELS[2]
