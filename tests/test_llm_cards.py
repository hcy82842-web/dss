from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.llm_cards import build_customer_explanation, build_customer_script, generate_llm_sections


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


def test_generate_llm_sections_falls_back_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    context = {
        "customer_id": 1001,
        "features": {
            "age": 58,
            "job": "retired",
            "marital": "married",
            "education": "university.degree",
            "default": "no",
            "housing": "yes",
            "loan": "no",
            "contact": "cellular",
            "month": "jun",
            "campaign": 1,
            "pdays": 999,
            "previous": 1,
            "poutcome": "success",
        },
        "model_result": {
            "conversion_probability": 0.73,
            "predicted_label": "yes",
            "actual_label": "yes",
            "is_correct": True,
            "priority_level": "高价值客户",
            "recommended_channel": "电话",
            "product_name": "6个月定期存款",
            "recommended_action": "建议在48小时内电话触达。",
        },
        "explanation_context": {
            "positive_factors": ["contact_cellular"],
            "negative_factors": [],
            "data_completeness": 1.0,
        },
    }

    result = generate_llm_sections(context)

    assert result["llm_status"] == "fallback模板生成"
    assert "退休" in result["sections"]["customer_profile"]
    assert "有住房贷款" in result["sections"]["customer_profile"]
    assert "稳健" in result["sections"]["marketing_script"]
