from __future__ import annotations

from src.dss_frontend.schema import CHANNEL_LABELS, PRIORITY_LEVELS

HIGH_PRIORITY_THRESHOLD = 0.70
MEDIUM_PRIORITY_THRESHOLD = 0.40


def build_decision_from_probability(probability: float) -> dict[str, object]:
    if probability >= HIGH_PRIORITY_THRESHOLD:
        return {
            "conversion_probability": probability,
            "priority_level": PRIORITY_LEVELS[0],
            "recommended_channel": CHANNEL_LABELS[0],
            "product_name": "6个月定期存款",
            "recommended_action": "建议在48小时内电话触达，主推6个月定期存款。",
        }
    if probability >= MEDIUM_PRIORITY_THRESHOLD:
        return {
            "conversion_probability": probability,
            "priority_level": PRIORITY_LEVELS[1],
            "recommended_channel": CHANNEL_LABELS[1],
            "product_name": "稳健型存款产品",
            "recommended_action": "建议先短信触达，再根据反馈决定是否电话跟进。",
        }
    return {
        "conversion_probability": probability,
        "priority_level": PRIORITY_LEVELS[2],
        "recommended_channel": CHANNEL_LABELS[2],
        "product_name": "基础存款产品",
        "recommended_action": "建议暂不优先电话触达，先使用低成本渠道观察。",
    }
