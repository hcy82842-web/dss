from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import httpx

from src.dss_frontend.llm_cards import (
    build_customer_explanation,
    build_customer_script,
    generate_llm_sections,
    get_llm_config_summary,
    test_llm_connection as run_llm_connection_test,
)


def _prediction_context():
    return {
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
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    context = _prediction_context()

    result = generate_llm_sections(context)

    assert result["llm_status"] == "fallback模板生成"
    assert "退休" in result["sections"]["customer_profile"]
    assert "有住房贷款" in result["sections"]["customer_profile"]
    assert "稳健" in result["sections"]["marketing_script"]


def test_generate_llm_sections_uses_generic_llm_config(monkeypatch):
    calls = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"customer_profile":"画像","marketing_strategy":"策略",'
                                '"risk_note":"风险","marketing_script":"话术"}'
                            )
                        }
                    }
                ]
            }

    def fake_post(url, headers, json, timeout):
        calls["url"] = url
        calls["headers"] = headers
        calls["json"] = json
        calls["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("LLM_PROVIDER_NAME", "MiMo v2.5")
    monkeypatch.setenv("LLM_API_KEY", "mimo-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://mimo.example.com/v1/")
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "12")
    monkeypatch.setattr("src.dss_frontend.llm_cards.httpx.post", fake_post)

    result = generate_llm_sections(_prediction_context())

    assert result["llm_status"] == "MiMo v2.5生成成功"
    assert result["sections"]["marketing_script"] == "话术"
    assert calls["url"] == "https://mimo.example.com/v1/chat/completions"
    assert calls["headers"]["Authorization"] == "Bearer mimo-key"
    assert calls["json"]["model"] == "mimo-v2.5"
    assert calls["timeout"] == 12.0


def test_llm_config_summary_does_not_expose_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER_NAME", "MiMo v2.5")
    monkeypatch.setenv("LLM_API_KEY", "secret-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://mimo.example.com/v1/")
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")

    summary = get_llm_config_summary()

    assert summary["provider_name"] == "MiMo v2.5"
    assert summary["base_url"] == "https://mimo.example.com/v1"
    assert summary["model"] == "mimo-v2.5"
    assert summary["api_key_status"] == "已配置"
    assert "secret-key" not in str(summary)


def test_llm_connection_reports_missing_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = run_llm_connection_test()

    assert result["ok"] is False
    assert "未配置" in result["title"]


def test_llm_connection_uses_openai_compatible_endpoint(monkeypatch):
    calls = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

    def fake_post(url, headers, json, timeout):
        calls["url"] = url
        calls["headers"] = headers
        calls["json"] = json
        calls["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("LLM_PROVIDER_NAME", "MiMo v2.5")
    monkeypatch.setenv("LLM_API_KEY", "mimo-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://mimo.example.com/v1/")
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "9")
    monkeypatch.setattr("src.dss_frontend.llm_cards.httpx.post", fake_post)

    result = run_llm_connection_test()

    assert result["ok"] is True
    assert result["title"] == "MiMo v2.5 连接成功"
    assert calls["url"] == "https://mimo.example.com/v1/chat/completions"
    assert calls["headers"]["Authorization"] == "Bearer mimo-key"
    assert calls["json"]["model"] == "mimo-v2.5"
    assert calls["json"]["max_tokens"] == 8
    assert calls["timeout"] == 9.0


def test_llm_connection_reports_http_status(monkeypatch):
    request = httpx.Request("POST", "https://mimo.example.com/v1/chat/completions")
    response = httpx.Response(401, request=request)

    class FakeResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError("unauthorized", request=request, response=response)

    monkeypatch.setenv("LLM_PROVIDER_NAME", "MiMo v2.5")
    monkeypatch.setenv("LLM_API_KEY", "mimo-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://mimo.example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")
    monkeypatch.setattr("src.dss_frontend.llm_cards.httpx.post", lambda *args, **kwargs: FakeResponse())

    result = run_llm_connection_test()

    assert result["ok"] is False
    assert result["title"] == "MiMo v2.5 连接失败"
    assert "HTTP 401" in result["message"]
