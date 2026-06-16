from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dss_backend.ml.inference import load_model_bundle
from src.dss_frontend.data_loader import REQUIRED_BUSINESS_FIELDS
from src.dss_frontend.llm_cards import build_structured_llm_sections
from src.dss_frontend.report_service import (
    build_case_options,
    build_dataset_summary,
    build_prediction_context_from_manual,
    build_prediction_context_from_validation,
    load_evaluation_summary,
    load_validation_predictions,
)
from src.dss_frontend.schema import BUSINESS_INPUT_COLUMNS, MODEL_FEATURE_COLUMNS
from src.dss_frontend.theme import apply_theme

DATA_PATH = Path("data/bank-additional-full.csv")
MODEL_ARTIFACT_PATH = Path("artifacts/logistic_regression.joblib")
MODEL_METADATA_PATH = Path("artifacts/model_metadata.json")
VALIDATION_PREDICTIONS_PATH = Path("artifacts/validation_predictions.csv")
EVALUATION_SUMMARY_PATH = Path("artifacts/evaluation_summary.json")


@st.cache_resource(show_spinner=False)
def get_model_bundle():
    return load_model_bundle(MODEL_ARTIFACT_PATH, MODEL_METADATA_PATH)


@st.cache_data(show_spinner=False)
def get_evaluation_summary() -> dict:
    return load_evaluation_summary(EVALUATION_SUMMARY_PATH)


@st.cache_data(show_spinner=False)
def get_validation_predictions() -> pd.DataFrame:
    return load_validation_predictions(VALIDATION_PREDICTIONS_PATH)


@st.cache_data(show_spinner=False)
def get_dataset_summary() -> dict:
    return build_dataset_summary(DATA_PATH, get_evaluation_summary())


def main() -> None:
    st.set_page_config(
        page_title="银行营销 DSS 报告验证系统",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_theme()

    _render_header()
    _assert_required_artifacts()

    summary = get_evaluation_summary()
    validation_frame = get_validation_predictions()
    bundle = get_model_bundle()

    tab_dataset, tab_metrics, tab_prediction, tab_llm = st.tabs(
        [
            "1 数据集与模型概览",
            "2 训练与验证结果",
            "3 客户预测验证",
            "4 LLM画像与营销建议",
        ]
    )

    with tab_dataset:
        _render_dataset_tab(summary)
    with tab_metrics:
        _render_metrics_tab(summary)
    with tab_prediction:
        context = _render_prediction_tab(validation_frame, summary, bundle)
    with tab_llm:
        _render_llm_tab(context)


def _assert_required_artifacts() -> None:
    missing = [
        path
        for path in [
            DATA_PATH,
            MODEL_ARTIFACT_PATH,
            MODEL_METADATA_PATH,
            VALIDATION_PREDICTIONS_PATH,
            EVALUATION_SUMMARY_PATH,
        ]
        if not path.exists()
    ]
    if missing:
        missing_text = "\n".join(str(path) for path in missing)
        st.error(
            "缺少系统运行所需文件，请先运行：python scripts/train_logistic_regression.py\n\n"
            f"{missing_text}"
        )
        st.stop()


def _render_header() -> None:
    st.markdown(
        """
        <div class='dashboard-hero'>
          <div class='dashboard-kicker'>REPORT-ORIENTED DECISION SUPPORT SYSTEM</div>
          <div class='dashboard-title'>银行零售营销资源配置决策支持系统</div>
          <div class='dashboard-subtitle'>
            页面按报告写作顺序组织：真实数据集、训练验证、单客户预测、LLM解释与营销建议。
            模型负责可验证预测，LLM负责管理解释，不替代模型决策。
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_dataset_tab(summary: dict) -> None:
    dataset = get_dataset_summary()
    split = dataset["split"]
    distribution = dataset["target_distribution"]
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    col1.metric("数据集来源", "UCI Bank Marketing")
    col2.metric("总样本量", f"{dataset['sample_count']:,}")
    col3.metric("训练集", f"{split['train_size']:,}")
    col4.metric("验证/预测集", f"{split['validation_size']:,}")

    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.subheader("建模边界")
        st.write(
            "系统使用 70%/30% 分层抽样划分训练集和验证集，保持购买/未购买比例一致。"
            "逻辑回归只在训练集上训练，验证集用于模型评估和前端案例验证。"
        )
        st.write("模型输入特征：")
        st.code(" / ".join(MODEL_FEATURE_COLUMNS), language="text")
        st.info("`duration` 是通话发生后才知道的结果变量，因此只用于历史复盘展示，不参与前置预测。")
    with right:
        st.subheader("目标变量分布")
        fig = go.Figure(
            data=[
                go.Bar(
                    x=["未购买 no", "购买 yes"],
                    y=[distribution.get("no", 0), distribution.get("yes", 0)],
                    marker_color=["#93c5fd", "#2563eb"],
                )
            ]
        )
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_metrics_tab(summary: dict) -> None:
    metrics = summary["metrics"]
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    col1.metric("AUC", f"{metrics['auc']:.4f}")
    col2.metric("Accuracy", f"{metrics['accuracy']:.4f}")
    col3.metric("Precision", f"{metrics['precision']:.4f}")
    col4.metric("Recall", f"{metrics['recall']:.4f}")
    col5.metric("F1", f"{metrics['f1']:.4f}")

    left, right = st.columns([0.9, 1.1], gap="large")
    with left:
        st.subheader("混淆矩阵")
        matrix = metrics["confusion_matrix"]["values"]
        fig = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=["预测 no", "预测 yes"],
                y=["真实 no", "真实 yes"],
                text=matrix,
                texttemplate="%{text}",
                colorscale="Blues",
            )
        )
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.subheader("主要影响因素")
        influence_frame = pd.DataFrame(summary["feature_influences"])
        st.dataframe(
            influence_frame.rename(
                columns={"feature": "特征", "coefficient": "系数", "direction": "影响方向"}
            ),
            hide_index=True,
            use_container_width=True,
        )
        st.caption("系数方向用于辅助解释模型，不等同于因果关系。")


def _render_prediction_tab(validation_frame: pd.DataFrame, summary: dict, bundle) -> dict:
    st.subheader("选择验证集样本或手动输入客户")
    mode = st.radio(
        "验证方式",
        ["验证集样本", "手动输入客户"],
        horizontal=True,
    )

    if mode == "验证集样本":
        context = _build_validation_case_context(validation_frame, summary)
    else:
        context = _build_manual_case_context(bundle)

    _render_prediction_result(context)
    st.session_state["current_prediction_context"] = context
    return context


def _build_validation_case_context(validation_frame: pd.DataFrame, summary: dict) -> dict:
    case_options = build_case_options(validation_frame, summary["representative_cases"])
    label_map = {
        int(row.customer_id): (
            f"客户 {int(row.customer_id)} | 真实 {row.actual_label} | "
            f"预测 {row.predicted_label} | 概率 {row.conversion_probability * 100:.1f}%"
        )
        for row in validation_frame.itertuples()
        if int(row.customer_id) in case_options
    }
    selected_id = st.selectbox(
        "选择验证集客户",
        options=case_options,
        format_func=lambda value: label_map.get(int(value), f"客户 {value}"),
    )
    row = validation_frame.loc[validation_frame["customer_id"] == selected_id].iloc[0]
    return build_prediction_context_from_validation(row, summary["feature_influences"])


def _build_manual_case_context(bundle) -> dict:
    with st.form("manual_prediction_form"):
        cols = st.columns(3, gap="medium")
        with cols[0]:
            age = st.number_input("年龄*", min_value=18, max_value=100, value=40)
            job = st.text_input("职业*", value="management")
            contact = st.selectbox("联系渠道*", ["cellular", "telephone"])
            month = st.selectbox("月份*", ["mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])
            campaign = st.number_input("本次联系次数*", min_value=1, max_value=20, value=1)
        with cols[1]:
            previous = st.number_input("历史联系次数*", min_value=0, max_value=20, value=0)
            marital = st.selectbox("婚姻", ["unknown", "single", "married", "divorced"])
            education = st.text_input("教育", value="university.degree")
            default = st.selectbox("违约", ["unknown", "no", "yes"])
            housing = st.selectbox("房贷", ["unknown", "no", "yes"])
        with cols[2]:
            loan = st.selectbox("个人贷", ["unknown", "no", "yes"])
            duration = st.number_input("通话时长（仅复盘展示）", min_value=0, max_value=5000, value=0)
            pdays = st.number_input("距上次联系天数", min_value=0, max_value=999, value=999)
            poutcome = st.selectbox("历史结果", ["unknown", "success", "failure", "nonexistent"])
            st.form_submit_button("生成预测结果", use_container_width=True)

    raw_values = {
        "age": age,
        "job": job,
        "marital": marital,
        "education": education,
        "default": default,
        "housing": housing,
        "loan": loan,
        "contact": contact,
        "month": month,
        "duration": duration,
        "campaign": campaign,
        "pdays": pdays,
        "previous": previous,
        "poutcome": poutcome,
    }
    return build_prediction_context_from_manual(raw_values, bundle)


def _render_prediction_result(context: dict) -> None:
    result = context["model_result"]
    features = context["features"]
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    col1.metric("预测购买概率", f"{result['conversion_probability'] * 100:.1f}%")
    col2.metric("预测类别", result["predicted_label"])
    col3.metric("营销优先级", result["priority_level"])
    col4.metric("推荐渠道", result["recommended_channel"])

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("客户特征")
        feature_frame = pd.DataFrame(
            [{"字段": key, "取值": value} for key, value in features.items() if key in BUSINESS_INPUT_COLUMNS]
        )
        st.dataframe(feature_frame, hide_index=True, use_container_width=True)
    with right:
        st.subheader("验证结果")
        if result.get("actual_label") is None:
            st.info("该客户来自手动输入，没有真实标签。")
        else:
            st.write(f"真实标签：`{result['actual_label']}`")
            st.write(f"预测是否正确：`{'是' if result['is_correct'] else '否'}`")
        st.write(f"推荐产品：`{result['product_name']}`")
        st.write(result["recommended_action"])


def _render_llm_tab(context: dict) -> None:
    if context is None:
        context = st.session_state.get("current_prediction_context")
    if context is None:
        st.info("请先在“客户预测验证”页选择或输入一个客户。")
        return

    sections = build_structured_llm_sections(context)
    st.info("LLM 解释基于模型输出和客户字段生成，不参与购买概率预测，也不改变营销优先级。")
    col1, col2, col3 = st.columns(3, gap="medium")
    col1.markdown("#### 客户画像")
    col1.write(sections["customer_profile"])
    col2.markdown("#### 营销建议")
    col2.write(sections["marketing_strategy"])
    col3.markdown("#### 风险与注意事项")
    col3.write(sections["risk_note"])
    st.markdown("#### 推荐话术")
    st.success(sections["marketing_script"])


if __name__ == "__main__":
    main()
