from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class BusinessCustomer(Base):
    __tablename__ = "business_customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_label: Mapped[str] = mapped_column(String(64), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    job: Mapped[str] = mapped_column(String(64), nullable=False)
    marital: Mapped[str] = mapped_column(String(64), nullable=False)
    education: Mapped[str] = mapped_column(String(128), nullable=False)
    default: Mapped[str] = mapped_column(String(32), nullable=False)
    housing: Mapped[str] = mapped_column(String(32), nullable=False)
    loan: Mapped[str] = mapped_column(String(32), nullable=False)
    contact: Mapped[str] = mapped_column(String(32), nullable=False)
    month: Mapped[str] = mapped_column(String(16), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    campaign: Mapped[int] = mapped_column(Integer, nullable=False)
    pdays: Mapped[int] = mapped_column(Integer, nullable=False)
    previous: Mapped[int] = mapped_column(Integer, nullable=False)
    poutcome: Mapped[str] = mapped_column(String(32), nullable=False)
    age_group: Mapped[str] = mapped_column(String(32), nullable=False)
    missing_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    completeness_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    impact_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    scoring_results: Mapped[list["ScoringResult"]] = relationship(
        "ScoringResult",
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class ScoringResult(Base):
    __tablename__ = "scoring_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("business_customers.id"), nullable=False, index=True)
    conversion_probability: Mapped[float] = mapped_column(Float, nullable=False)
    priority_level: Mapped[str] = mapped_column(String(64), nullable=False)
    recommended_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    customer_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    marketing_script: Mapped[str] = mapped_column(Text, nullable=False)
    llm_status: Mapped[str] = mapped_column(String(32), nullable=False)
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    customer: Mapped[BusinessCustomer] = relationship("BusinessCustomer", back_populates="scoring_results")
