from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import BusinessCustomer


class BusinessCustomerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: dict) -> BusinessCustomer:
        customer = BusinessCustomer(**payload, customer_label="pending")
        self.session.add(customer)
        self.session.flush()
        customer.customer_label = f"客户 {customer.id}"
        self.session.commit()
        self.session.refresh(customer)
        return customer

    def bulk_create(self, payloads: list[dict]) -> list[BusinessCustomer]:
        created: list[BusinessCustomer] = []
        for payload in payloads:
            created.append(self.create(payload))
        return created

    def get(self, customer_id: int) -> BusinessCustomer | None:
        return self.session.get(BusinessCustomer, customer_id)

    def list_all(self) -> list[BusinessCustomer]:
        return list(self.session.scalars(select(BusinessCustomer).order_by(BusinessCustomer.id.desc())))
