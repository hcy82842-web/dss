from __future__ import annotations

import json
from os import getenv
from typing import Any

import httpx
from dotenv import load_dotenv

from src.dss_frontend.report_service import translate_field_value


load_dotenv()


def _feature_text(features: dict[str, Any], field: str) -> str:
    return translate_field_value(field, features.get(field))


def _risk_phrase(features: dict[str, Any]) -> str:
    risks = []
    if str(features.get("loan")) == "yes":
        risks.append("客户存在个人贷款，沟通时应避免造成资金压力")
    if str(features.get("housing")) == "yes":
        risks.append("客户存在住房贷款，建议强调资金流动性安排")
    if str(features.get("campaign", 0)).isdigit() and int(features.get("campaign", 0)) >= 3:
        risks.append("本轮联系次数较多，需要控制打扰频率")
    if str(features.get("poutcome")) == "failure":
        risks.append("历史营销结果失败，需要降低强推语气")
    return "；".join(risks) if risks else "当前字段未显示明显触达风险，仍需遵守合规沟通要求"


def _script_angle(features: dict[str, Any], result: dict[str, Any]) -> str:
    job = str(features.get("job"))
    age = int(features.get("age", 0) or 0)
    if job in {"retired", "management"} or age >= 55:
        return "突出稳健、期限清晰和资金安排确定性"
    if job in {"student", "unemployed"} or age <= 30:
        return "语气保持轻量，强调可了解、不施压和按需配置"
    if str(features.get("housing")) == "yes" or str(features.get("loan")) == "yes":
        return "强调不影响日常资金周转，建议从小额或短期限方案了解"
    if "高" in str(result.get("priority_level")):
        return "突出匹配度较高，可直接邀请客户了解产品细节"
    return "先建立兴趣，再根据反馈决定是否深入介绍"


def build_customer_explanation(customer: dict, decision: dict) -> str:
    notice = customer.get("missing_field_notice")
    notice_text = ""
    if isinstance(notice, dict):
        notice_text = f"当前字段完整度为 {int(notice['completeness_ratio'] * 100)}%，{notice['impact_text']}"
    return (
        f"{customer['customer_label']} "
        f"\u5f53\u524d\u9884\u6d4b\u8f6c\u5316\u6982\u7387\u4e3a "
        f"{decision['conversion_probability']:.2f}\uff0c"
        f"\u5efa\u8bae\u4f18\u5148\u4f7f\u7528{decision['recommended_channel']}"
        "\u89e6\u8fbe\u3002"
        f"\u8be5\u5ba2\u6237\u804c\u4e1a\u4e3a {customer['job']}\uff0c"
        f"\u6700\u8fd1\u8054\u7cfb\u6708\u4efd\u4e3a {customer['month']}\uff0c"
        "\u5ba2\u6237\u7279\u5f81\u4e0e\u5f53\u524d\u63a8\u8350\u52a8\u4f5c\u4fdd\u6301\u4e00\u81f4\uff0c"
        "\u56e0\u6b64\u9002\u5408\u8fdb\u5165\u672c\u8f6e\u91cd\u70b9\u8425\u9500\u540d\u5355\u3002"
        f"{notice_text}"
    )


def build_customer_script(customer: dict, decision: dict) -> str:
    return (
        f"{customer['customer_label']} "
        "\u5efa\u8bae\u8bdd\u672f\uff1a\u60a8\u597d\uff0c"
        "\u6211\u4eec\u7ed3\u5408\u60a8\u7684\u8d44\u91d1\u5b89\u6392\u504f\u597d\uff0c"
        f"\u63a8\u8350\u60a8\u4e86\u89e3\u4e00\u4e0b {decision['product_name']}\uff0c"
        "\u8fd9\u7c7b\u65b9\u6848\u66f4\u9002\u5408\u7a33\u5065\u578b\u914d\u7f6e\u9700\u6c42\u3002"
    )


def build_structured_llm_sections(prediction_context: dict[str, Any]) -> dict[str, str]:
    features = prediction_context["features"]
    result = prediction_context["model_result"]
    context = prediction_context["explanation_context"]

    probability_text = f"{float(result['conversion_probability']) * 100:.1f}%"
    positive = "、".join(context.get("positive_factors") or ["当前可用特征整体支持该判断"])
    negative = "、".join(context.get("negative_factors") or ["未发现明显负向主导因素"])
    risk_phrase = _risk_phrase(features)
    script_angle = _script_angle(features, result)

    profile = (
        f"该客户年龄为 {features.get('age')} 岁，职业为{_feature_text(features, 'job')}，"
        f"婚姻状态为{_feature_text(features, 'marital')}，教育水平为{_feature_text(features, 'education')}。"
        f"贷款情况显示：{_feature_text(features, 'housing')}，{_feature_text(features, 'loan')}。"
        f"最近联系月份为{_feature_text(features, 'month')}，联系渠道为{_feature_text(features, 'contact')}。"
        f"模型预测其订购定期存款的概率为 {probability_text}，"
        f"对应营销优先级为{result['priority_level']}。"
    )
    strategy = (
        f"建议采用{result['recommended_channel']}触达，主推{result['product_name']}。"
        f"主要正向依据包括：{positive}；需要关注的负向或不确定因素包括：{negative}。"
        f"具体执行动作：{result['recommended_action']}沟通侧重点建议为：{script_angle}。"
    )
    risk = (
        "LLM 解释仅基于逻辑回归模型输出和当前客户字段生成，不参与概率预测。"
        f"当前字段完整度为 {float(context.get('data_completeness', 1.0)) * 100:.0f}%。"
        f"风险提示：{risk_phrase}。"
    )
    if result.get("actual_label") is not None:
        correctness = "预测正确" if result.get("is_correct") else "预测错误"
        risk += f"该样本来自验证集，真实标签为 {result['actual_label']}，{correctness}。"
    if context.get("impact_text"):
        risk += str(context["impact_text"])

    return {
        "customer_profile": profile,
        "marketing_strategy": strategy,
        "risk_note": risk,
        "marketing_script": (
            f"您好，我们根据您当前的资金安排场景，想邀请您了解一下{result['product_name']}。"
            f"这次建议主要考虑到您的职业和历史联系情况，沟通重点是{script_angle}。"
            "您可以先了解期限、起点和流动性安排，再决定是否进一步办理。"
        ),
    }


def generate_llm_sections(prediction_context: dict[str, Any]) -> dict[str, Any]:
    config = _resolve_llm_config()
    api_key = config["api_key"]
    if not api_key:
        return {
            "sections": build_structured_llm_sections(prediction_context),
            "llm_status": "fallback模板生成",
        }

    try:
        sections = _call_openai_compatible_llm(prediction_context, config)
        return {"sections": sections, "llm_status": f"{config['provider_name']}生成成功"}
    except Exception:
        return {
            "sections": build_structured_llm_sections(prediction_context),
            "llm_status": "fallback模板生成",
        }


def get_llm_config_summary() -> dict[str, str]:
    config = _resolve_llm_config()
    return {
        "provider_name": config["provider_name"],
        "base_url": config["base_url"],
        "model": config["model"],
        "api_key_status": "已配置" if config["api_key"] else "未配置",
    }


def test_llm_connection() -> dict[str, Any]:
    config = _resolve_llm_config()
    if not config["api_key"]:
        return {
            "ok": False,
            "title": "LLM API Key 未配置",
            "message": "请在 .env 中配置 LLM_API_KEY，或使用兼容的 DEEPSEEK_API_KEY。",
            "provider_name": config["provider_name"],
            "base_url": config["base_url"],
            "model": config["model"],
        }

    try:
        response = httpx.post(
            f"{config['base_url']}/chat/completions",
            headers={"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"},
            json={
                "model": config["model"],
                "messages": [
                    {"role": "system", "content": "你是一个连接测试助手，只回复 pong。"},
                    {"role": "user", "content": "ping"},
                ],
                "temperature": 0,
                "max_tokens": 8,
            },
            timeout=float(config["timeout_seconds"]),
        )
        response.raise_for_status()
        return {
            "ok": True,
            "title": f"{config['provider_name']} 连接成功",
            "message": "接口已通过基础鉴权和 chat/completions 调用测试。",
            "provider_name": config["provider_name"],
            "base_url": config["base_url"],
            "model": config["model"],
        }
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        return {
            "ok": False,
            "title": f"{config['provider_name']} 连接失败",
            "message": f"HTTP {status_code}。请检查 API Key、Base URL、模型名和账号权限。",
            "provider_name": config["provider_name"],
            "base_url": config["base_url"],
            "model": config["model"],
        }
    except Exception as exc:
        return {
            "ok": False,
            "title": f"{config['provider_name']} 连接失败",
            "message": f"{type(exc).__name__}: {exc}。请检查网络、Base URL 和接口兼容性。",
            "provider_name": config["provider_name"],
            "base_url": config["base_url"],
            "model": config["model"],
        }


def _resolve_llm_config() -> dict[str, str]:
    return {
        "provider_name": getenv("LLM_PROVIDER_NAME") or getenv("DEEPSEEK_PROVIDER_NAME") or "DeepSeek",
        "api_key": getenv("LLM_API_KEY") or getenv("DEEPSEEK_API_KEY", ""),
        "base_url": (getenv("LLM_BASE_URL") or getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip("/"),
        "model": getenv("LLM_MODEL") or getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "timeout_seconds": getenv("LLM_TIMEOUT_SECONDS") or getenv("DEEPSEEK_TIMEOUT_SECONDS", "30"),
    }


def _call_openai_compatible_llm(prediction_context: dict[str, Any], config: dict[str, str]) -> dict[str, str]:
    payload = _build_chinese_context(prediction_context)
    response = httpx.post(
        f"{config['base_url']}/chat/completions",
        headers={"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"},
        json={
            "model": config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是银行零售营销决策支持系统的解释层。"
                        "逻辑回归模型已经完成预测，你不得修改概率、预测类别、优先级、渠道或产品建议。"
                        "不得编造收入、资产、交易流水、家庭情况等未提供信息。"
                        "请输出中文 JSON，字段必须为 customer_profile、marketing_strategy、risk_note、marketing_script。"
                        "内容要根据客户特征差异化，不要只复述字段。话术合规、克制，不承诺收益。"
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "temperature": 0.45,
            "response_format": {"type": "json_object"},
        },
        timeout=float(config["timeout_seconds"]),
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    return {
        "customer_profile": str(parsed["customer_profile"]),
        "marketing_strategy": str(parsed["marketing_strategy"]),
        "risk_note": str(parsed["risk_note"]),
        "marketing_script": str(parsed["marketing_script"]),
    }


def _build_chinese_context(prediction_context: dict[str, Any]) -> dict[str, Any]:
    features = prediction_context["features"]
    translated_features = {
        "年龄": features.get("age"),
        "职业": _feature_text(features, "job"),
        "婚姻": _feature_text(features, "marital"),
        "教育": _feature_text(features, "education"),
        "违约": _feature_text(features, "default"),
        "住房贷款": _feature_text(features, "housing"),
        "个人贷款": _feature_text(features, "loan"),
        "联系渠道": _feature_text(features, "contact"),
        "联系月份": _feature_text(features, "month"),
        "本轮联系次数": features.get("campaign"),
        "距上次联系天数": features.get("pdays"),
        "历史联系次数": features.get("previous"),
        "历史营销结果": _feature_text(features, "poutcome"),
    }
    return {
        "customer_id": prediction_context.get("customer_id"),
        "features": translated_features,
        "model_result": prediction_context["model_result"],
        "explanation_context": prediction_context["explanation_context"],
    }
