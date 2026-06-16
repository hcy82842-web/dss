from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.service_layer import build_dashboard_state


def test_build_dashboard_state_sorts_candidates_and_uses_first_customer():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1001,
                "customer_label": "客户 1001",
                "job": "management",
                "month": "may",
                "contact": "cellular",
                "age_group": "36-50",
                "marital": "married",
                "priority_level": "中价值客户",
                "conversion_probability": 0.62,
                "recommended_channel": "短信",
                "recommended_action": "建议先短信触达，再根据反馈决定是否电话跟进。",
                "product_name": "稳健型存款产品",
                "duration": 180,
            },
            {
                "customer_id": 1002,
                "customer_label": "客户 1002",
                "job": "technician",
                "month": "nov",
                "contact": "cellular",
                "age_group": "35及以下",
                "marital": "single",
                "priority_level": "高价值客户",
                "conversion_probability": 0.83,
                "recommended_channel": "电话",
                "recommended_action": "建议在48小时内电话触达，主推6个月定期存款。",
                "product_name": "6个月定期存款",
                "duration": 320,
            },
        ]
    )

    state = build_dashboard_state(
        enriched_frame=frame,
        selected_priority_levels=[],
        selected_jobs=[],
        selected_months=[],
        selected_contacts=[],
        selected_age_groups=[],
        selected_customer_id=None,
    )

    assert state["candidate_frame"]["customer_id"].tolist() == [1002, 1001]
    assert state["selected_customer_id"] == 1002
    assert state["selected_customer"]["customer_label"] == "客户 1002"


def test_build_dashboard_state_keeps_requested_customer_when_present():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1001,
                "customer_label": "客户 1001",
                "job": "management",
                "month": "may",
                "contact": "cellular",
                "age_group": "36-50",
                "marital": "married",
                "priority_level": "中价值客户",
                "conversion_probability": 0.62,
                "recommended_channel": "短信",
                "recommended_action": "建议先短信触达，再根据反馈决定是否电话跟进。",
                "product_name": "稳健型存款产品",
                "duration": 180,
            },
            {
                "customer_id": 1002,
                "customer_label": "客户 1002",
                "job": "technician",
                "month": "nov",
                "contact": "cellular",
                "age_group": "35及以下",
                "marital": "single",
                "priority_level": "高价值客户",
                "conversion_probability": 0.83,
                "recommended_channel": "电话",
                "recommended_action": "建议在48小时内电话触达，主推6个月定期存款。",
                "product_name": "6个月定期存款",
                "duration": 320,
            },
        ]
    )

    state = build_dashboard_state(
        enriched_frame=frame,
        selected_priority_levels=[],
        selected_jobs=["management"],
        selected_months=[],
        selected_contacts=[],
        selected_age_groups=[],
        selected_customer_id=1001,
    )

    assert state["candidate_frame"]["customer_id"].tolist() == [1001]
    assert state["selected_customer_id"] == 1001
    assert state["selected_customer"]["recommended_channel"] == "短信"


def test_build_dashboard_state_builds_single_customer_explanation_and_script():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1001,
                "customer_label": "客户 1001",
                "job": "management",
                "month": "may",
                "contact": "cellular",
                "age_group": "36-50",
                "marital": "married",
                "priority_level": "高价值客户",
                "conversion_probability": 0.81,
                "recommended_channel": "电话",
                "recommended_action": "建议在48小时内电话触达，主推6个月定期存款。",
                "product_name": "6个月定期存款",
                "duration": 320,
            }
        ]
    )

    state = build_dashboard_state(
        enriched_frame=frame,
        selected_priority_levels=[],
        selected_jobs=[],
        selected_months=[],
        selected_contacts=[],
        selected_age_groups=[],
        selected_customer_id=1001,
    )

    assert state["selected_decision"]["recommended_channel"] == "电话"
    assert "客户 1001" in state["customer_explanation"]
    assert "客户 1001" in state["customer_script"]
    assert "6个月定期存款" in state["customer_script"]


def test_build_dashboard_state_builds_dashboard_analytics():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1001,
                "customer_label": "客户 1001",
                "job": "management",
                "month": "may",
                "contact": "cellular",
                "age_group": "36-50",
                "marital": "married",
                "priority_level": "中价值客户",
                "conversion_probability": 0.62,
                "recommended_channel": "短信",
                "recommended_action": "建议先短信触达，再根据反馈决定是否电话跟进。",
                "product_name": "稳健型存款产品",
                "duration": 180,
            },
            {
                "customer_id": 1002,
                "customer_label": "客户 1002",
                "job": "technician",
                "month": "nov",
                "contact": "cellular",
                "age_group": "35及以下",
                "marital": "single",
                "priority_level": "高价值客户",
                "conversion_probability": 0.83,
                "recommended_channel": "电话",
                "recommended_action": "建议在48小时内电话触达，主推6个月定期存款。",
                "product_name": "6个月定期存款",
                "duration": 320,
            },
            {
                "customer_id": 1003,
                "customer_label": "客户 1003",
                "job": "technician",
                "month": "may",
                "contact": "telephone",
                "age_group": "51+",
                "marital": "married",
                "priority_level": "高价值客户",
                "conversion_probability": 0.77,
                "recommended_channel": "电话",
                "recommended_action": "建议优先电话触达。",
                "product_name": "6个月定期存款",
                "duration": 250,
            },
        ]
    )

    state = build_dashboard_state(
        enriched_frame=frame,
        selected_priority_levels=[],
        selected_jobs=[],
        selected_months=[],
        selected_contacts=[],
        selected_age_groups=[],
        selected_customer_id=None,
    )

    analytics = state["dashboard_analytics"]

    assert analytics["workflow_steps"][0]["label"] == "客群筛选"
    assert analytics["channel_mix"] == [
        {"contact": "cellular", "count": 2},
        {"contact": "telephone", "count": 1},
    ]
    assert analytics["month_trend"] == [
        {"month": "may", "count": 2, "avg_probability": 0.695},
        {"month": "nov", "count": 1, "avg_probability": 0.83},
    ]
    assert analytics["candidate_rows"][0]["customer_label"] == "客户 1002"


def test_build_dashboard_state_handles_business_input_without_training_label():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 2001,
                "customer_label": "客户 2001",
                "job": "management",
                "month": "jun",
                "contact": "cellular",
                "age_group": "36-50",
                "marital": "married",
                "priority_level": "高价值客户",
                "conversion_probability": 0.79,
                "recommended_channel": "电话",
                "recommended_action": "建议优先电话触达。",
                "product_name": "6个月定期存款",
                "duration": 220,
                "education": "university.degree",
                "age": 41,
            }
        ]
    )

    state = build_dashboard_state(
        enriched_frame=frame,
        selected_priority_levels=[],
        selected_jobs=[],
        selected_months=[],
        selected_contacts=[],
        selected_age_groups=[],
        selected_customer_id=2001,
    )

    assert state["selected_customer"]["customer_label"] == "客户 2001"
    assert "客户 2001" in state["customer_explanation"]


def test_build_dashboard_state_preserves_missing_field_notice_for_business_input():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 2001,
                "customer_label": "客户 2001",
                "job": "management",
                "month": "jun",
                "contact": "cellular",
                "age_group": "36-50",
                "marital": "unknown",
                "education": "unknown",
                "default": "unknown",
                "housing": "unknown",
                "loan": "unknown",
                "poutcome": "unknown",
                "age": 41,
                "campaign": 1,
                "previous": 1,
                "duration": 0,
                "pdays": 999,
                "priority_level": "高价值客户",
                "conversion_probability": 0.79,
                "recommended_channel": "电话",
                "recommended_action": "建议优先电话触达。",
                "product_name": "6个月定期存款",
                "missing_field_notice": {
                    "completeness_ratio": 0.57,
                    "missing_fields": ["education", "default", "housing", "loan", "poutcome"],
                    "impact_text": "部分关键字段缺失，会影响结果稳定性。",
                },
            }
        ]
    )

    state = build_dashboard_state(
        enriched_frame=frame,
        selected_priority_levels=[],
        selected_jobs=[],
        selected_months=[],
        selected_contacts=[],
        selected_age_groups=[],
        selected_customer_id=2001,
    )

    assert state["selected_customer"]["missing_field_notice"]["completeness_ratio"] == 0.57
