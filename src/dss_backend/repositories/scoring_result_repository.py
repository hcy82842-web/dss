from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import ScoringResult


class ScoringResultRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: dict) -> ScoringResult:
        result = ScoringResult(**payload)
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result

    def list_all(self) -> list[ScoringResult]:
        return list(self.session.scalars(select(ScoringResult).order_by(desc(ScoringResult.scored_at))))

    def get_latest_for_customer(self, customer_id: int) -> ScoringResult | None:
        statement = (
            select(ScoringResult)
            .where(ScoringResult.customer_id == customer_id)
            .order_by(desc(ScoringResult.scored_at), desc(ScoringResult.id))
            .limit(1)
        )
        return self.session.scalars(statement).first()
