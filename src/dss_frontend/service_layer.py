from __future__ import annotations

from typing import Any

import pandas as pd

from .filters import apply_filters, default_selected_customer_id
from .llm_cards import build_customer_explanation, build_customer_script
from .metrics import build_summary_metrics
from .schema import AGE_GROUP_LABELS, MONTH_ORDER, PRIORITY_LEVELS

DECISION_FIELDS = [
    "conversion_probability",
    "priority_level",
    "recommended_channel",
    "product_name",
    "recommended_action",
]


def _build_selected_decision(selected_customer: dict[str, Any] | None) -> dict[str, Any] | None:
    if selected_customer is None:
        return None
    return {field: selected_customer[field] for field in DECISION_FIELDS}


def _build_workflow_steps() -> list[dict[str, str | bool]]:
    return [
        {"label": "客群筛选", "description": "分层锁定高优先客户", "active": True},
        {"label": "候选排序", "description": "按转化概率生成名单", "active": False},
        {"label": "渠道决策", "description": "推荐电话、短信或邮件", "active": False},
        {"label": "话术生成", "description": "绑定单客户生成话术", "active": False},
        {"label": "结果解释", "description": "输出答辩可用解释文本", "active": False},
    ]


def _build_month_trend(candidate_frame: pd.DataFrame) -> list[dict[str, Any]]:
    if candidate_frame.empty:
        return []

    month_summary = (
        candidate_frame.groupby("month", as_index=False)
        .agg(
            count=("customer_id", "count"),
            avg_probability=("conversion_probability", "mean"),
        )
        .assign(month_order=lambda df: df["month"].map(lambda value: MONTH_ORDER.index(value)))
        .sort_values("month_order")
    )

    return [
        {
            "month": row["month"],
            "count": int(row["count"]),
            "avg_probability": round(float(row["avg_probability"]), 3),
        }
        for _, row in month_summary.iterrows()
    ]


def _build_channel_mix(candidate_frame: pd.DataFrame) -> list[dict[str, Any]]:
    if candidate_frame.empty:
        return []

    channel_summary = (
        candidate_frame.groupby("contact", as_index=False)
        .agg(count=("customer_id", "count"))
        .sort_values(["count", "contact"], ascending=[False, True])
    )
    return [
        {"contact": row["contact"], "count": int(row["count"])}
        for _, row in channel_summary.iterrows()
    ]


def _build_job_rank(candidate_frame: pd.DataFrame) -> list[dict[str, Any]]:
    if candidate_frame.empty:
        return []

    job_summary = (
        candidate_frame.groupby("job", as_index=False)
        .agg(
            count=("customer_id", "count"),
            avg_probability=("conversion_probability", "mean"),
        )
        .sort_values(["count", "avg_probability"], ascending=[False, False])
        .head(6)
    )
    return [
        {
            "job": row["job"],
            "count": int(row["count"]),
            "avg_probability": round(float(row["avg_probability"]), 3),
        }
        for _, row in job_summary.iterrows()
    ]


def _build_age_priority_matrix(candidate_frame: pd.DataFrame) -> dict[str, Any]:
    matrix = (
        candidate_frame.pivot_table(
            index="age_group",
            columns="priority_level",
            values="customer_id",
            aggfunc="count",
            fill_value=0,
        )
        .reindex(index=AGE_GROUP_LABELS, columns=PRIORITY_LEVELS, fill_value=0)
    )

    return {
        "age_groups": AGE_GROUP_LABELS,
        "priority_levels": PRIORITY_LEVELS,
        "values": matrix.values.tolist(),
    }


def _build_channel_matrix(candidate_frame: pd.DataFrame) -> list[dict[str, Any]]:
    if candidate_frame.empty:
        return []

    summary = (
        candidate_frame.groupby("job", as_index=False)
        .agg(
            customer_count=("customer_id", "count"),
            avg_duration=("duration", "mean"),
            avg_probability=("conversion_probability", "mean"),
        )
        .sort_values(["customer_count", "avg_probability"], ascending=[False, False])
        .head(6)
    )

    dominant_channel = (
        candidate_frame.groupby(["job", "recommended_channel"])
        .size()
        .reset_index(name="channel_count")
        .sort_values(["job", "channel_count"], ascending=[True, False])
        .drop_duplicates(subset=["job"])
        .rename(columns={"recommended_channel": "dominant_channel"})
    )

    merged = summary.merge(dominant_channel[["job", "dominant_channel"]], on="job", how="left")
    return [
        {
            "job": row["job"],
            "customer_count": int(row["customer_count"]),
            "avg_duration": round(float(row["avg_duration"]), 1),
            "avg_probability": round(float(row["avg_probability"]), 3),
            "dominant_channel": row["dominant_channel"],
        }
        for _, row in merged.iterrows()
    ]


def _build_candidate_rows(candidate_frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows = candidate_frame.head(8).copy()
    if rows.empty:
        return []

    return [
        {
            "customer_id": int(row["customer_id"]),
            "customer_label": row["customer_label"],
            "job": row["job"],
            "month": row["month"],
            "priority_level": row["priority_level"],
            "recommended_channel": row["recommended_channel"],
            "conversion_probability": round(float(row["conversion_probability"]), 3),
            "duration": int(row["duration"]),
        }
        for _, row in rows.iterrows()
    ]


def _build_summary_cards(candidate_frame: pd.DataFrame, month_trend: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_customers = len(candidate_frame)
    high_priority = int((candidate_frame["priority_level"] == PRIORITY_LEVELS[0]).sum()) if total_customers else 0
    avg_probability = float(candidate_frame["conversion_probability"].mean()) if total_customers else 0.0
    phone_share = (
        float((candidate_frame["recommended_channel"] == "电话").mean()) if total_customers else 0.0
    )
    avg_duration = float(candidate_frame["duration"].mean()) if total_customers else 0.0

    month_counts = [item["count"] for item in month_trend] or [0]
    month_probs = [round(item["avg_probability"] * 100, 1) for item in month_trend] or [0]
    high_month_counts = []
    if total_customers:
        high_month_frame = candidate_frame.loc[candidate_frame["priority_level"] == PRIORITY_LEVELS[0]]
        high_month_counts = [
            int(high_month_frame.loc[high_month_frame["month"] == item["month"], "customer_id"].count())
            for item in month_trend
        ] or [0]
    else:
        high_month_counts = [0]

    phone_series = []
    duration_series = []
    for item in month_trend:
        month_frame = candidate_frame.loc[candidate_frame["month"] == item["month"]]
        phone_series.append(
            round(float((month_frame["recommended_channel"] == "电话").mean()) * 100, 1) if not month_frame.empty else 0
        )
        duration_series.append(
            round(float(month_frame["duration"].mean()), 1) if not month_frame.empty else 0
        )

    return [
        {
            "label": "待评估客户",
            "value": f"{total_customers:,}",
            "footnote": "当前筛选营销池规模",
            "series": month_counts,
            "accent": "blue",
        },
        {
            "label": "高潜名单",
            "value": f"{high_priority:,}",
            "footnote": "高价值客户数量",
            "series": high_month_counts,
            "accent": "blue",
        },
        {
            "label": "预估转化率",
            "value": f"{avg_probability * 100:.1f}%",
            "footnote": "全名单平均转化概率",
            "series": month_probs,
            "accent": "green",
        },
        {
            "label": "电话优先占比",
            "value": f"{phone_share * 100:.1f}%",
            "footnote": "推荐电话触达的客户占比",
            "series": phone_series or [0],
            "accent": "blue",
        },
        {
            "label": "平均通话时长",
            "value": f"{avg_duration:.0f}s",
            "footnote": "筛选名单平均联系时长",
            "series": duration_series or [0],
            "accent": "amber",
        },
    ]


def _build_dashboard_analytics(candidate_frame: pd.DataFrame) -> dict[str, Any]:
    month_trend = _build_month_trend(candidate_frame)
    return {
        "workflow_steps": _build_workflow_steps(),
        "summary_cards": _build_summary_cards(candidate_frame, month_trend),
        "channel_mix": _build_channel_mix(candidate_frame),
        "job_rank": _build_job_rank(candidate_frame),
        "month_trend": month_trend,
        "age_priority_matrix": _build_age_priority_matrix(candidate_frame),
        "channel_matrix": _build_channel_matrix(candidate_frame),
        "candidate_rows": _build_candidate_rows(candidate_frame),
    }


def build_dashboard_state(
    enriched_frame: pd.DataFrame,
    selected_priority_levels: list[str],
    selected_jobs: list[str],
    selected_months: list[str],
    selected_contacts: list[str],
    selected_age_groups: list[str],
    selected_customer_id: int | None,
) -> dict[str, Any]:
    filtered = apply_filters(
        enriched_frame,
        selected_priority_levels,
        selected_jobs,
        selected_months,
        selected_contacts,
        selected_age_groups,
    )
    candidate_frame = filtered.sort_values(by="conversion_probability", ascending=False).reset_index(drop=True)

    if candidate_frame.empty:
        resolved_customer_id = None
        selected_customer = None
    else:
        if selected_customer_id not in candidate_frame["customer_id"].tolist():
            selected_customer_id = default_selected_customer_id(candidate_frame)
        resolved_customer_id = selected_customer_id
        selected_customer = candidate_frame.loc[
            candidate_frame["customer_id"] == resolved_customer_id
        ].iloc[0].to_dict()

    selected_decision = _build_selected_decision(selected_customer)
    customer_explanation = (
        build_customer_explanation(selected_customer, selected_decision)
        if selected_customer is not None and selected_decision is not None
        else None
    )
    customer_script = (
        build_customer_script(selected_customer, selected_decision)
        if selected_customer is not None and selected_decision is not None
        else None
    )

    return {
        "metrics": build_summary_metrics(candidate_frame),
        "candidate_frame": candidate_frame,
        "selected_customer_id": resolved_customer_id,
        "selected_customer": selected_customer,
        "selected_decision": selected_decision,
        "customer_explanation": customer_explanation,
        "customer_script": customer_script,
        "dashboard_analytics": _build_dashboard_analytics(candidate_frame),
    }
