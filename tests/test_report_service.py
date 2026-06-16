from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dss_frontend.llm_cards import build_structured_llm_sections
from src.dss_frontend.report_service import (
    build_case_options,
    build_case_option_label,
    build_confusion_matrix_business_rows,
    build_feature_display_rows,
    build_metric_cards,
    build_prediction_context_from_validation,
    build_prediction_error_type,
    build_priority_distribution,
    build_priority_rule_rows,
    build_probability_distribution,
    build_variable_reference_rows,
    build_validation_result_summary,
    translate_field_value,
)


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


def test_validation_summary_and_priority_distribution_are_business_readable():
    frame = pd.DataFrame(
        [
            {
                "customer_id": 1,
                "actual_label": "yes",
                "predicted_label": "yes",
                "is_correct": True,
                "conversion_probability": 0.82,
                "priority_level": "高价值客户",
            },
            {
                "customer_id": 2,
                "actual_label": "no",
                "predicted_label": "yes",
                "is_correct": False,
                "conversion_probability": 0.61,
                "priority_level": "中价值客户",
            },
            {
                "customer_id": 3,
                "actual_label": "no",
                "predicted_label": "no",
                "is_correct": True,
                "conversion_probability": 0.22,
                "priority_level": "低响应客户",
            },
        ]
    )

    summary = build_validation_result_summary(frame)
    priority = build_priority_distribution(frame)
    probability = build_probability_distribution(frame)

    assert summary == {
        "total": 3,
        "correct": 2,
        "incorrect": 1,
        "actual_yes": 1,
        "predicted_yes": 2,
        "accuracy": 0.6667,
    }
    assert priority["营销优先级"].tolist() == ["高价值客户", "中价值客户", "低响应客户"]
    assert priority["真实购买率"].tolist() == [1.0, 0.0, 0.0]
    assert probability.columns.tolist() == ["真实标签", "预测概率"]
    assert probability["真实标签"].tolist() == ["购买 yes", "未购买 no", "未购买 no"]


def test_metric_cards_confusion_rows_and_error_type_are_explainable():
    metrics = {
        "auc": 0.77,
        "accuracy": 0.8,
        "precision": 0.3,
        "recall": 0.58,
        "f1": 0.39,
        "confusion_matrix": {"values": [[90, 20], [5, 15]]},
    }

    cards = build_metric_cards(metrics)
    rows = build_confusion_matrix_business_rows(metrics)

    assert [card["label"] for card in cards] == ["AUC", "Accuracy", "Precision", "Recall", "F1"]
    assert "真实购买客户中" in cards[3]["explanation"]
    assert rows[0]["业务含义"] == "正确识别未购买客户"
    assert rows[2]["数量"] == 5
    assert build_prediction_error_type("no", "yes").startswith("假阳性")
    assert build_prediction_error_type("yes", "no").startswith("假阴性")
    assert build_prediction_error_type("yes", "yes") == "预测正确"


def test_variable_reference_priority_rules_and_translations_are_report_ready():
    variables = build_variable_reference_rows()
    rules = build_priority_rule_rows()

    duration = next(row for row in variables if row["英文变量"] == "duration")
    age = next(row for row in variables if row["英文变量"] == "age")

    assert age["中文含义"] == "年龄"
    assert age["是否进入模型"] == "是"
    assert duration["中文含义"] == "通话时长"
    assert duration["是否进入模型"] == "否"
    assert "不参与" in duration["说明"]
    assert rules[0]["概率区间"] == ">= 70%"
    assert rules[1]["客户分类"] == "中价值客户"
    assert translate_field_value("job", "management") == "管理人员"
    assert translate_field_value("month", "jun") == "6月"


def test_case_option_label_does_not_leak_prediction_result():
    row = pd.Series(
        {
            "customer_id": 1001,
            "job": "management",
            "month": "jun",
            "contact": "cellular",
            "actual_label": "yes",
            "predicted_label": "no",
            "conversion_probability": 0.88,
        }
    )

    label = build_case_option_label(row)

    assert "客户 1001" in label
    assert "管理人员" in label
    assert "6月" in label
    assert "yes" not in label
    assert "no" not in label
    assert "0.88" not in label


def test_feature_display_rows_translate_customer_values():
    rows = build_feature_display_rows(
        {
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
        }
    )

    lookup = {row["英文变量"]: row["取值"] for row in rows}
    assert lookup["job"] == "管理人员"
    assert lookup["marital"] == "已婚"
    assert lookup["housing"] == "有住房贷款"
    assert lookup["contact"] == "手机联系"
