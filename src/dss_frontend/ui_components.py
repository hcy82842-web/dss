from __future__ import annotations

from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


def render_section_title(title: str, kicker: str | None = None) -> None:
    kicker_html = f"<div class='section-kicker'>{escape(kicker)}</div>" if kicker else ""
    st.markdown(
        f"{kicker_html}<div class='report-section-title'>{escape(title)}</div>",
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        (
            "<div class='metric-card'>"
            f"<div class='metric-label'>{escape(label)}</div>"
            f"<div class='metric-value'>{escape(value)}</div>"
            f"<div class='metric-note'>{escape(note)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_metric_cards(cards: list[dict[str, str]]) -> None:
    columns = st.columns(len(cards), gap="medium")
    for column, card in zip(columns, cards):
        with column:
            render_metric_card(card["label"], card["value"], card.get("explanation", ""))


def render_report_card(title: str, body: str) -> None:
    st.markdown(
        (
            "<div class='report-card'>"
            f"<div class='report-card-title'>{escape(title)}</div>"
            f"<div class='report-card-body'>{escape(body)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_decision_cards(cards: list[dict[str, str]]) -> None:
    html = ["<div class='decision-grid'>"]
    for card in cards:
        html.append(
            (
                "<div class='decision-card'>"
                f"<div class='metric-label'>{escape(card['label'])}</div>"
                f"<div class='metric-value'>{escape(card['value'])}</div>"
                f"<div class='metric-note'>{escape(card.get('note', ''))}</div>"
                "</div>"
            )
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def render_status_card(title: str, body: str, ok: bool = True) -> None:
    status_class = "status-ok" if ok else "status-warn"
    st.markdown(
        (
            f"<div class='status-card {status_class}'>"
            f"<div class='status-card-title'>{escape(title)}</div>"
            f"<div class='status-card-body'>{escape(body)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_llm_card(title: str, body: str) -> None:
    st.markdown(
        (
            "<div class='llm-card'>"
            f"<div class='llm-card-title'>{escape(title)}</div>"
            f"<div class='llm-card-body'>{escape(body)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def build_filter_summary_items(
    selected_priority_levels: list[str],
    selected_jobs: list[str],
    selected_months: list[str],
    selected_contacts: list[str],
    selected_age_groups: list[str],
) -> list[tuple[str, str]]:
    return [
        ("价值层级", " / ".join(selected_priority_levels) if selected_priority_levels else "全部"),
        ("职业", " / ".join(selected_jobs) if selected_jobs else "全部"),
        ("月份", " / ".join(selected_months) if selected_months else "全部"),
        ("渠道", " / ".join(selected_contacts) if selected_contacts else "全部"),
        ("年龄层级", " / ".join(selected_age_groups) if selected_age_groups else "全部"),
    ]


def build_candidate_snapshot(
    frame: pd.DataFrame,
    selected_customer_id: int | None,
    limit: int = 8,
) -> list[dict[str, str | int | bool]]:
    snapshot: list[dict[str, str | int | bool]] = []
    for _, row in frame.head(limit).iterrows():
        snapshot.append(
            {
                "customer_id": int(row["customer_id"]),
                "customer_label": str(row["customer_label"]),
                "priority_level": str(row["priority_level"]),
                "recommended_channel": str(row["recommended_channel"]),
                "probability_text": f"{float(row['conversion_probability']) * 100:.1f}%",
                "profile_text": f"{row['job']} / {row['month']}",
                "is_selected": int(row["customer_id"]) == selected_customer_id,
            }
        )
    return snapshot


def _priority_class(priority_level: str) -> str:
    if "高" in priority_level:
        return "priority-high"
    if "中" in priority_level:
        return "priority-mid"
    return "priority-low"


def _plotly_base_layout(height: int) -> dict:
    return {
        "height": height,
        "paper_bgcolor": "rgba(255,255,255,0)",
        "plot_bgcolor": "rgba(255,255,255,0)",
        "margin": dict(l=18, r=18, t=14, b=14),
        "font": dict(family="Noto Sans SC, Microsoft YaHei, sans-serif", color="#64748b", size=12),
        "showlegend": False,
    }


def render_dashboard_header(total_customers: int, candidate_count: int) -> None:
    st.markdown(
        (
            "<div class='dashboard-hero'>"
            "<div class='dashboard-kicker'>BANK RETAIL MARKETING ANALYTICS</div>"
            "<div class='dashboard-title'>银行零售业务智能营销决策支持系统</div>"
            "<div class='dashboard-subtitle'>"
            "展示层围绕“筛选客户、锁定名单、渠道推荐、单客户解释”四个动作展开，"
            "重点表达这不是一个单纯的预测页面，而是一个帮助老师看到决策闭环的营销工作台。"
            "</div>"
            "<div class='hero-inline-metrics'>"
            f"<span>总样本 {total_customers:,}</span>"
            f"<span>当前候选 {candidate_count:,}</span>"
            "<span>LLM 解释绑定单客户</span>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_summary_cards(summary_cards: list[dict[str, object]]) -> None:
    first_row = summary_cards[:3]
    second_row = summary_cards[3:]

    for row_index, row_cards in enumerate((first_row, second_row)):
        if not row_cards:
            continue
        columns = st.columns(len(row_cards), gap="medium")
        for column, card in zip(columns, row_cards):
            column.markdown(
                (
                    f"<div class='summary-card accent-{escape(str(card['accent']))}'>"
                    f"<div class='summary-card-topline'>{escape(str(card['label']))}</div>"
                    f"<div class='summary-card-value'>{escape(str(card['value']))}</div>"
                    f"<div class='summary-card-footnote'>{escape(str(card['footnote']))}</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
        if row_index == 0 and second_row:
            st.markdown("<div class='summary-row-gap'></div>", unsafe_allow_html=True)


def render_workflow_steps(steps: list[dict[str, object]]) -> None:
    step_html = []
    for step in steps:
        step_html.append(
            (
                f"<div class='workflow-step {'active' if step['active'] else ''}'>"
                f"<div class='workflow-label'>{escape(str(step['label']))}</div>"
                f"<div class='workflow-copy'>{escape(str(step['description']))}</div>"
                "</div>"
            )
        )
    st.markdown(f"<div class='workflow-strip'>{''.join(step_html)}</div>", unsafe_allow_html=True)


def render_filter_toolbar_title() -> None:
    st.markdown(
        (
            "<div class='toolbar-card'>"
            "<div class='toolbar-kicker'>CONTROL PANEL</div>"
            "<div class='toolbar-title'>营销筛选控制台</div>"
            "<div class='toolbar-copy'>先圈定营销池，再把有限资源集中投到最值得联系的客户上。这里的筛选器不只是查数据，而是在模拟营销经理的资源配置动作。</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_filter_summary(
    selected_priority_levels: list[str],
    selected_jobs: list[str],
    selected_months: list[str],
    selected_contacts: list[str],
    selected_age_groups: list[str],
) -> None:
    items = build_filter_summary_items(
        selected_priority_levels,
        selected_jobs,
        selected_months,
        selected_contacts,
        selected_age_groups,
    )
    chips = "".join(
        f"<span class='filter-chip'><strong>{escape(label)}</strong>{escape(value)}</span>"
        for label, value in items
    )
    st.markdown(f"<div class='filter-chip-row'>{chips}</div>", unsafe_allow_html=True)


def render_section_banner(title: str, copy: str, kicker: str) -> None:
    st.markdown(
        (
            "<div class='section-banner'>"
            f"<div class='section-banner-kicker'>{escape(kicker)}</div>"
            f"<div class='section-banner-title'>{escape(title)}</div>"
            f"<div class='section-banner-copy'>{escape(copy)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_distribution_panel(channel_mix: list[dict[str, object]], job_rank: list[dict[str, object]]) -> None:
    st.markdown(
        (
            "<div class='panel-head'>"
            "<div class='panel-eyebrow'>渠道与客群</div>"
            "<div class='panel-head-title'>客户来源与职业分布</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "domain"}, {"type": "xy"}]],
        column_widths=[0.42, 0.58],
        horizontal_spacing=0.12,
    )
    fig.add_trace(
        go.Pie(
            labels=[str(item["contact"]) for item in channel_mix],
            values=[int(item["count"]) for item in channel_mix],
            hole=0.68,
            marker=dict(colors=["#2563eb", "#60a5fa", "#93c5fd", "#dbeafe"]),
            textinfo="label+percent",
            textfont=dict(size=11, color="#64748b"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=[int(item["count"]) for item in reversed(job_rank)],
            y=[str(item["job"]) for item in reversed(job_rank)],
            orientation="h",
            marker=dict(color="#4f8df7", line=dict(color="#cfe0fb", width=1)),
        ),
        row=1,
        col=2,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.14)", zeroline=False, row=1, col=2)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11), row=1, col=2)
    fig.add_annotation(
        text=f"渠道数 {sum(int(item['count']) for item in channel_mix)}",
        x=0.2,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=15, color="#1e3a8a"),
    )
    fig.update_layout(**_plotly_base_layout(340))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_priority_heatmap_panel(matrix: dict[str, object]) -> None:
    st.markdown(
        (
            "<div class='panel-head'>"
            "<div class='panel-eyebrow'>年龄与分层</div>"
            "<div class='panel-head-title'>年龄层级与客户价值热力图</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix["values"],
            x=matrix["priority_levels"],
            y=matrix["age_groups"],
            colorscale=[
                [0, "#f8fbff"],
                [0.35, "#bfdbfe"],
                [0.7, "#60a5fa"],
                [1, "#2563eb"],
            ],
            text=matrix["values"],
            texttemplate="%{text}",
            hoverongaps=False,
            colorbar=dict(thickness=12, outlinewidth=0),
        )
    )
    fig.update_layout(**_plotly_base_layout(340))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_month_trend_panel(month_trend: list[dict[str, object]]) -> None:
    st.markdown(
        (
            "<div class='panel-head'>"
            "<div class='panel-eyebrow'>月度趋势</div>"
            "<div class='panel-head-title'>候选名单数量与转化率走势</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    months = [str(item["month"]) for item in month_trend]
    counts = [int(item["count"]) for item in month_trend]
    probabilities = [float(item["avg_probability"]) * 100 for item in month_trend]
    fig.add_trace(
        go.Scatter(
            x=months,
            y=counts,
            mode="lines+markers",
            line=dict(color="#3b82f6", width=3),
            marker=dict(size=7, color="#3b82f6"),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.16)",
            name="候选数量",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=months,
            y=probabilities,
            mode="lines",
            line=dict(color="#f59e0b", width=2.5, dash="dot"),
            name="平均转化率",
        ),
        secondary_y=True,
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.14)", zeroline=False, secondary_y=False)
    fig.update_yaxes(showgrid=False, secondary_y=True)
    fig.update_layout(**_plotly_base_layout(340))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_channel_matrix_panel(channel_matrix: list[dict[str, object]]) -> None:
    st.markdown(
        (
            "<div class='panel-head'>"
            "<div class='panel-eyebrow'>渠道矩阵</div>"
            "<div class='panel-head-title'>职业群体优先渠道矩阵</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    color_map = {"电话": "#3b82f6", "短信": "#10b981", "邮件": "#f59e0b"}
    fig = go.Figure()
    for row in channel_matrix:
        fig.add_trace(
            go.Scatter(
                x=[row["avg_duration"]],
                y=[float(row["avg_probability"]) * 100],
                mode="markers+text",
                text=[row["job"]],
                textposition="top center",
                marker=dict(
                    size=max(16, int(row["customer_count"]) * 2),
                    color=color_map.get(str(row["dominant_channel"]), "#3b82f6"),
                    opacity=0.78,
                    line=dict(color="#ffffff", width=1.4),
                ),
                hovertemplate=(
                    f"职业: {row['job']}<br>"
                    f"客户数: {row['customer_count']}<br>"
                    f"平均通话时长: {row['avg_duration']}<br>"
                    f"平均转化率: {float(row['avg_probability']) * 100:.1f}%<br>"
                    f"主导渠道: {row['dominant_channel']}<extra></extra>"
                ),
                showlegend=False,
            )
        )
    fig.update_xaxes(title="平均通话时长（秒）", showgrid=True, gridcolor="rgba(148, 163, 184, 0.14)", zeroline=False)
    fig.update_yaxes(title="平均转化率（%）", showgrid=True, gridcolor="rgba(148, 163, 184, 0.14)", zeroline=False)
    fig.update_layout(**_plotly_base_layout(340))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_candidate_snapshot_panel(frame: pd.DataFrame, selected_customer_id: int | None) -> None:
    st.markdown(
        (
            "<div class='panel-head'>"
            "<div class='panel-eyebrow'>候选池快照</div>"
            "<div class='panel-head-title'>优先跟进客户列表</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    cards = []
    for item in build_candidate_snapshot(frame, selected_customer_id, limit=6):
        cards.append(
            (
                f"<div class='candidate-strip {'selected' if item['is_selected'] else ''}'>"
                f"<div class='candidate-strip-title'>{escape(str(item['customer_label']))}</div>"
                f"<div class='candidate-strip-sub'>{escape(str(item['profile_text']))}</div>"
                "<div class='candidate-strip-tags'>"
                f"<span class='mini-tag {_priority_class(str(item['priority_level']))}'>{escape(str(item['priority_level']))}</span>"
                f"<span class='mini-tag channel'>{escape(str(item['recommended_channel']))}</span>"
                f"<span class='mini-score'>{escape(str(item['probability_text']))}</span>"
                "</div>"
                "</div>"
            )
        )
    st.markdown("".join(cards), unsafe_allow_html=True)


def render_candidate_table(frame: pd.DataFrame) -> None:
    table = frame[
        [
            "customer_label",
            "job",
            "month",
            "priority_level",
            "recommended_channel",
            "conversion_probability",
            "duration",
        ]
    ].copy()
    table["conversion_probability"] = table["conversion_probability"].map(lambda value: f"{value * 100:.1f}%")
    table = table.rename(
        columns={
            "customer_label": "客户",
            "job": "职业",
            "month": "月份",
            "priority_level": "价值层级",
            "recommended_channel": "推荐渠道",
            "conversion_probability": "预测转化率",
            "duration": "通话时长",
        }
    )
    st.dataframe(table, hide_index=True, use_container_width=True)


def render_customer_detail(
    customer: dict,
    decision: dict,
    explanation: str,
    script: str,
) -> None:
    chips = [customer.get("contact", "-"), customer.get("month", "-"), customer.get("age_group", "-")]
    chip_html = "".join(f"<span class='detail-chip'>{escape(str(item))}</span>" for item in chips)
    rows = [
        ("客户", customer.get("customer_label", "-")),
        ("年龄 / 婚姻", f"{customer.get('age', '-')} / {customer.get('marital', '-')}"),
        ("职业", customer.get("job", "-")),
        ("教育", customer.get("education", "-")),
    ]
    info_rows = "".join(
        (
            "<div class='detail-row'>"
            f"<span>{escape(label)}</span>"
            f"<strong>{escape(str(value))}</strong>"
            "</div>"
        )
        for label, value in rows
    )
    stats = [
        ("预测转化率", f"{decision['conversion_probability'] * 100:.1f}%"),
        ("客户分层", decision["priority_level"]),
        ("推荐渠道", decision["recommended_channel"]),
        ("主推产品", decision["product_name"]),
    ]
    stat_html = "".join(
        (
            "<div class='detail-stat'>"
            f"<span>{escape(label)}</span>"
            f"<strong>{escape(str(value))}</strong>"
            "</div>"
        )
        for label, value in stats
    )
    st.markdown(
        (
            "<div class='decision-card'>"
            "<div class='panel-eyebrow'>单客户决策</div>"
            "<div class='decision-title'>当前客户决策详情</div>"
            f"<div class='detail-chip-row'>{chip_html}</div>"
            f"{info_rows}"
            f"<div class='detail-stat-grid'>{stat_html}</div>"
            f"<div class='decision-action'>{escape(str(decision['recommended_action']))}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        (
            "<div class='decision-note info'>"
            "<div class='decision-note-title'>LLM 决策解释</div>"
            f"<div class='decision-note-body'>{escape(explanation)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        (
            "<div class='decision-note warn'>"
            "<div class='decision-note-title'>建议话术</div>"
            f"<div class='decision-note-body'>{escape(script)}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
