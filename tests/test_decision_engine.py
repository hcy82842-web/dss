from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.decision_engine import build_decision_view


def test_build_decision_view_generates_high_value_phone_strategy():
    row = pd.Series(
        {
            "customer_label": "\u5ba2\u6237 1001",
            "age": 42,
            "job": "management",
            "contact": "cellular",
            "campaign": 2,
            "previous": 1,
            "housing": "yes",
            "loan": "no",
            "poutcome": "success",
            "default": "no",
        }
    )

    decision = build_decision_view(row)

    assert 0.0 <= decision["conversion_probability"] <= 1.0
    assert decision["priority_level"] == "\u9ad8\u4ef7\u503c\u5ba2\u6237"
    assert decision["recommended_channel"] == "\u7535\u8bdd"
    assert "\u5b9a\u671f\u5b58\u6b3e" in decision["product_name"]
    assert isinstance(decision["recommended_action"], str)


def test_build_decision_view_generates_low_value_email_strategy():
    row = pd.Series(
        {
            "customer_label": "\u5ba2\u6237 1002",
            "age": 31,
            "job": "technician",
            "contact": "telephone",
            "campaign": 5,
            "previous": 0,
            "housing": "no",
            "loan": "yes",
            "response_flag": 0,
        }
    )

    decision = build_decision_view(row)

    assert decision["priority_level"] == "\u4f4e\u54cd\u5e94\u5ba2\u6237"
    assert decision["recommended_channel"] == "\u90ae\u4ef6"
    assert decision["customer_label"] == "\u5ba2\u6237 1002"


def test_build_decision_view_can_score_business_customer_without_response_flag():
    row = pd.Series(
        {
            "customer_label": "客户 2001",
            "age": 45,
            "job": "management",
            "contact": "cellular",
            "campaign": 1,
            "previous": 2,
            "housing": "yes",
            "loan": "no",
        }
    )

    decision = build_decision_view(row)

    assert decision["customer_label"] == "客户 2001"
    assert decision["conversion_probability"] >= 0.55
    assert decision["recommended_channel"] in {"电话", "短信", "邮件"}
