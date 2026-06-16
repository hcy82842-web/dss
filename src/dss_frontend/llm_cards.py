from __future__ import annotations

from typing import Any


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

    profile = (
        f"该客户年龄为 {features.get('age')}，职业为 {features.get('job')}，"
        f"婚姻状态为 {features.get('marital')}，最近联系月份为 {features.get('month')}。"
        f"模型预测其订购定期存款的概率为 {probability_text}，"
        f"对应预测类别为 {result['predicted_label']}，营销优先级为 {result['priority_level']}。"
    )
    strategy = (
        f"建议采用{result['recommended_channel']}触达，主推{result['product_name']}。"
        f"主要正向依据包括：{positive}；需要关注的负向或不确定因素包括：{negative}。"
        f"具体执行动作：{result['recommended_action']}"
    )
    risk = (
        "LLM 解释仅基于逻辑回归模型输出和当前客户字段生成，不参与概率预测。"
        f"当前字段完整度为 {float(context.get('data_completeness', 1.0)) * 100:.0f}%。"
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
            f"您好，我们结合您的资金配置需求，为您推荐了解{result['product_name']}。"
            "该产品更适合稳健型资金安排，您可以根据自身资金流动性需要进一步确认。"
        ),
    }
