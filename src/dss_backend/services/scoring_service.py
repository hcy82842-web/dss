from __future__ import annotations

from sqlalchemy.orm import Session

from src.dss_backend.decision_policy import build_decision_from_probability
from src.dss_frontend.llm_cards import build_customer_explanation, build_customer_script

from ..repositories.business_customer_repository import BusinessCustomerRepository
from ..repositories.scoring_result_repository import ScoringResultRepository


class ScoringService:
    def __init__(self, session: Session, model_service, llm_client) -> None:
        self.customer_repository = BusinessCustomerRepository(session)
        self.result_repository = ScoringResultRepository(session)
        self.model_service = model_service
        self.llm_client = llm_client

    def run_for_customer(self, customer_id: int):
        customer = self.customer_repository.get(customer_id)
        if customer is None:
            return None

        customer_dict = _customer_to_dict(customer)
        probability = float(self.model_service.predict_probability(customer_dict))
        decision = build_decision_from_probability(probability)

        try:
            llm_payload = self.llm_client.generate_customer_messages(customer_dict, decision)
            explanation = llm_payload["customer_explanation"]
            script = llm_payload["marketing_script"]
            llm_status = "success"
        except Exception:
            explanation = build_customer_explanation(customer_dict, decision)
            script = build_customer_script(customer_dict, decision)
            llm_status = "failed_fallback"

        return self.result_repository.create(
            {
                "customer_id": customer.id,
                "conversion_probability": probability,
                "priority_level": decision["priority_level"],
                "recommended_channel": decision["recommended_channel"],
                "product_name": decision["product_name"],
                "recommended_action": decision["recommended_action"],
                "customer_explanation": explanation,
                "marketing_script": script,
                "llm_status": llm_status,
            }
        )

    def run_batch(self, customer_ids: list[int] | None = None):
        customers = self.customer_repository.list_all()
        if customer_ids:
            customer_set = set(customer_ids)
            customers = [customer for customer in customers if customer.id in customer_set]
        results = []
        for customer in customers:
            result = self.run_for_customer(customer.id)
            if result is not None:
                results.append(result)
        return results

    def list_results(self):
        return self.result_repository.list_all()

    def get_latest_result(self, customer_id: int):
        return self.result_repository.get_latest_for_customer(customer_id)

def _customer_to_dict(customer) -> dict[str, object]:
    return {
        "customer_id": customer.id,
        "customer_label": customer.customer_label,
        "age": customer.age,
        "job": customer.job,
        "marital": customer.marital,
        "education": customer.education,
        "default": customer.default,
        "housing": customer.housing,
        "loan": customer.loan,
        "contact": customer.contact,
        "month": customer.month,
        "duration": customer.duration,
        "campaign": customer.campaign,
        "pdays": customer.pdays,
        "previous": customer.previous,
        "poutcome": customer.poutcome,
        "age_group": customer.age_group,
        "missing_field_notice": {
            "missing_fields": customer.missing_fields,
            "completeness_ratio": customer.completeness_ratio,
            "impact_text": customer.impact_text,
        },
    }
