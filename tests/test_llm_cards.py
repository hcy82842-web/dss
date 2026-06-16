from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.llm_cards import build_customer_explanation, build_customer_script


def test_build_customer_explanation_mentions_selected_customer_context():
    customer = {
        "customer_label": "\u5ba2\u6237 1001",
        "job": "management",
        "month": "may",
        "housing": "yes",
    }
    decision = {
        "conversion_probability": 0.82,
        "recommended_channel": "\u7535\u8bdd",
    }

    explanation = build_customer_explanation(customer, decision)

    assert "\u5ba2\u6237 1001" in explanation
    assert "\u7535\u8bdd" in explanation
    assert "0.82" in explanation


def test_build_customer_script_is_bound_to_same_customer():
    customer = {
        "customer_label": "\u5ba2\u6237 1002",
        "job": "technician",
        "month": "jun",
        "housing": "no",
    }
    decision = {
        "product_name": "\u7a33\u5065\u578b\u5b58\u6b3e\u4ea7\u54c1",
    }

    script = build_customer_script(customer, decision)

    assert "\u5ba2\u6237 1002" in script
    assert "\u7a33\u5065\u578b\u5b58\u6b3e\u4ea7\u54c1" in script
