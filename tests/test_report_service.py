from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.llm_cards import build_structured_llm_sections
from src.dss_frontend.report_service import build_case_options, build_prediction_context_from_validation


def test_build_case_options_prioritizes_representative_cases():
    frame = pd.DataFrame(
        [
            {"customer_id": 1, "conversion_probability": 0.91},
            {"customer_id": 2, "conversion_probability": 0.55},
            {"customer_id": 3, "conversion_probability": 0.12},
        ]
    )

    options = build_case_options(
        frame,
        {
            "high_probability_correct_yes": 2,
            "medium_probability_case": 3,
            "low_probability_correct_no": None,
            "misclassified_case": 1,
        },
    )

    assert options[:3] == [2, 3, 1]


def test_validation_context_and_llm_sections_are_report_ready():
    row = pd.Series(
        {
            "customer_id": 1001,
            "age": 41,
            "job": "management",
            "marital": "married",
            "education": "university.degree",
            "default": "no",
            "housing": "yes",
            "loan": "no",
            "contact": "cellular",
            "month": "jun",
            "duration": 220,
            "campaign": 1,
            "pdays": 999,
            "previous": 1,
            "poutcome": "success",
            "conversion_probability": 0.73,
            "predicted_label": "yes",
            "actual_label": "yes",
            "is_correct": True,
            "priority_level": "高价值客户",
            "recommended_channel": "电话",
            "product_name": "6个月定期存款",
            "recommended_action": "建议在48小时内电话触达。",
        }
    )

    context = build_prediction_context_from_validation(
        row,
        [
            {"feature": "contact_cellular", "coefficient": 0.7, "direction": "提高购买概率"},
            {"feature": "month_jun", "coefficient": -0.2, "direction": "降低购买概率"},
        ],
    )
    sections = build_structured_llm_sections(context)

    assert context["source"] == "validation_set"
    assert context["model_result"]["is_correct"] is True
    assert "contact_cellular" in context["explanation_context"]["positive_factors"]
    assert "客户画像" not in sections["customer_profile"]
    assert "模型输出" not in sections["marketing_strategy"]
    assert "不参与概率预测" in sections["risk_note"]
