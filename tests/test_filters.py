from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.filters import apply_filters, default_selected_customer_id


def test_apply_filters_supports_priority_job_month_contact_and_age_group():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1001,
                "customer_label": "\u5ba2\u6237 1001",
                "job": "management",
                "month": "may",
                "contact": "cellular",
                "age_group": "36-50",
                "priority_level": "\u9ad8\u4ef7\u503c\u5ba2\u6237",
            },
            {
                "customer_id": 1002,
                "customer_label": "\u5ba2\u6237 1002",
                "job": "admin.",
                "month": "jun",
                "contact": "telephone",
                "age_group": "35\u53ca\u4ee5\u4e0b",
                "priority_level": "\u4f4e\u54cd\u5e94\u5ba2\u6237",
            },
        ]
    )

    filtered = apply_filters(
        frame,
        selected_priority_levels=["\u9ad8\u4ef7\u503c\u5ba2\u6237"],
        selected_jobs=["management"],
        selected_months=["may"],
        selected_contacts=["cellular"],
        selected_age_groups=["36-50"],
    )

    assert filtered["customer_label"].tolist() == ["\u5ba2\u6237 1001"]


def test_apply_filters_returns_original_when_no_filters():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1001,
                "customer_label": "\u5ba2\u6237 1001",
                "job": "management",
                "month": "may",
                "contact": "cellular",
                "age_group": "36-50",
                "priority_level": "\u9ad8\u4ef7\u503c\u5ba2\u6237",
            },
            {
                "customer_id": 1002,
                "customer_label": "\u5ba2\u6237 1002",
                "job": "admin.",
                "month": "jun",
                "contact": "telephone",
                "age_group": "35\u53ca\u4ee5\u4e0b",
                "priority_level": "\u4f4e\u54cd\u5e94\u5ba2\u6237",
            },
        ]
    ).set_index(pd.Index([10, 20], name="row_id"))

    filtered = apply_filters(frame, [], [], [], [], [])

    assert filtered.equals(frame)
    assert filtered.index.tolist() == [10, 20]


def test_default_selected_customer_id_returns_first_customer():
    frame = pd.DataFrame(
        [
            {"customer_id": 1005, "customer_label": "\u5ba2\u6237 1005"},
            {"customer_id": 1009, "customer_label": "\u5ba2\u6237 1009"},
        ]
    )

    assert default_selected_customer_id(frame) == 1005


def test_default_selected_customer_id_returns_none_for_empty_frame():
    frame = pd.DataFrame(columns=["customer_id", "customer_label"])

    assert default_selected_customer_id(frame) is None
