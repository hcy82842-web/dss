from __future__ import annotations

import json

import httpx

from ..config import BackendSettings


class DeepSeekClient:
    def __init__(self, settings: BackendSettings) -> None:
        self.settings = settings

    def generate_customer_messages(self, customer: dict, decision: dict) -> dict[str, str]:
        if not self.settings.deepseek_api_key:
            raise RuntimeError("missing DeepSeek API key")

        response = httpx.post(
            f"{self.settings.deepseek_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.deepseek_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "你是银行零售营销决策支持系统的解释层。"
                            "逻辑回归模型已经完成概率预测，你不得修改概率、优先级、渠道或产品建议。"
                            "只能基于用户提供的 customer 和 decision 字段解释原因、生成营销话术和风险提示，"
                            "不得编造未提供的收入、资产、偏好、历史交易或身份信息。"
                            "请严格返回 JSON，字段只有 customer_explanation 和 marketing_script。"
                            "customer_explanation 面向银行营销人员，必须包含推荐理由和谨慎提示；"
                            "marketing_script 面向客户沟通，必须简短、合规、不过度承诺收益。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "customer": customer,
                                "decision": decision,
                            },
                            ensure_ascii=False,
                        ),
                    },
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
            timeout=self.settings.deepseek_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return {
            "customer_explanation": parsed["customer_explanation"],
            "marketing_script": parsed["marketing_script"],
        }
