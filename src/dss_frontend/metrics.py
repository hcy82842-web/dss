import pandas as pd


def build_summary_metrics(frame: pd.DataFrame) -> dict[str, str | int]:
    total_customers = len(frame)
    high_priority = (
        int((frame["priority_level"] == "\u9ad8\u4ef7\u503c\u5ba2\u6237").sum())
        if total_customers
        else 0
    )
    conversion_rate = round(float(frame["conversion_probability"].mean()) * 100, 1) if total_customers else 0.0
    suggested_budget = high_priority * 300
    return {
        "\u5f85\u8bc4\u4f30\u5ba2\u6237": total_customers,
        "\u9ad8\u6f5c\u540d\u5355": high_priority,
        "\u9884\u4f30\u8f6c\u5316\u7387": f"{conversion_rate}%",
        "\u5efa\u8bae\u9884\u7b97": f"\u00a5{suggested_budget:,}",
    }
