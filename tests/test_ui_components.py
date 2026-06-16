from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.ui_components import build_candidate_snapshot, build_filter_summary_items
from src.dss_frontend.ui_components import render_decision_cards, render_metric_card, render_report_card


def test_build_filter_summary_items_formats_selected_values():
    items = build_filter_summary_items(
        selected_priority_levels=["高价值客户"],
        selected_jobs=["management"],
        selected_months=[],
        selected_contacts=["cellular"],
        selected_age_groups=["36-50"],
    )

    assert items == [
        ("价值层级", "高价值客户"),
        ("职业", "management"),
        ("月份", "全部"),
        ("渠道", "cellular"),
        ("年龄层级", "36-50"),
    ]


def test_build_candidate_snapshot_marks_selected_customer():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1002,
                "customer_label": "客户 1002",
                "priority_level": "高价值客户",
                "recommended_channel": "电话",
                "conversion_probability": 0.83,
                "job": "technician",
                "month": "nov",
            },
            {
                "customer_id": 1001,
                "customer_label": "客户 1001",
                "priority_level": "中价值客户",
                "recommended_channel": "短信",
                "conversion_probability": 0.62,
                "job": "management",
                "month": "may",
            },
        ]
    )

    snapshot = build_candidate_snapshot(frame, selected_customer_id=1002, limit=1)

    assert snapshot == [
        {
            "customer_id": 1002,
            "customer_label": "客户 1002",
            "priority_level": "高价值客户",
            "recommended_channel": "电话",
            "probability_text": "83.0%",
            "profile_text": "technician / nov",
            "is_selected": True,
        }
    ]


def test_report_card_components_render_expected_markup(monkeypatch):
    rendered: list[str] = []

    def fake_markdown(body: str, unsafe_allow_html: bool = False):
        rendered.append(body)
        assert unsafe_allow_html is True

    monkeypatch.setattr("src.dss_frontend.ui_components.st.markdown", fake_markdown)

    render_metric_card("AUC", "0.7693", "区分购买和未购买客户的排序能力。")
    render_report_card("解释边界", "系数方向不等同于因果关系。")
    render_decision_cards([{"label": "推荐渠道", "value": "电话", "note": "高价值客户优先触达"}])

    joined = "\n".join(rendered)
    assert "metric-card" in joined
    assert "report-card" in joined
    assert "decision-grid" in joined
    assert "区分购买和未购买客户" in joined
