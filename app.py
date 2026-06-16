from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dss_backend.ml.inference import load_model_bundle
from src.dss_frontend.data_loader import REQUIRED_BUSINESS_FIELDS
from src.dss_frontend.llm_cards import generate_llm_sections, get_llm_config_summary, test_llm_connection
from src.dss_frontend.report_service import (
    build_case_options,
    build_case_option_label,
    build_confusion_matrix_business_rows,
    build_dataset_summary,
    build_feature_display_rows,
    build_metric_cards,
    build_priority_distribution,
    build_priority_rule_rows,
    build_prediction_context_from_manual,
    build_prediction_context_from_validation,
    build_probability_distribution,
    build_variable_reference_rows,
    build_validation_result_summary,
    load_evaluation_summary,
    load_validation_predictions,
)
from src.dss_frontend.schema import BUSINESS_INPUT_COLUMNS
from src.dss_frontend.theme import apply_theme
from src.dss_frontend.ui_components import (
    render_decision_cards,
    render_llm_card,
    render_llm_config_cards,
    render_metric_card,
    render_metric_cards,
    render_report_card,
    render_section_title,
    render_status_card,
    render_priority_rule_cards,
    render_static_table,
    render_variable_summary_cards,
)

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
    _init_session_state()

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
        _render_prediction_tab(validation_frame, summary, bundle)
    with tab_llm:
        _render_llm_tab()


def _init_session_state() -> None:
    defaults = {
        "prediction_context": None,
        "llm_sections": None,
        "llm_status": None,
        "selected_customer_id": None,
        "prediction_mode": None,
        "llm_connection_status": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
    render_metric_cards(
        [
            {"label": "数据集来源", "value": "UCI", "explanation": "Bank Marketing 真实银行营销数据"},
            {"label": "总样本量", "value": f"{dataset['sample_count']:,}", "explanation": "用于训练与验证的历史营销记录"},
            {"label": "训练集", "value": f"{split['train_size']:,}", "explanation": "70% 分层抽样，用于训练模型"},
            {"label": "验证/预测集", "value": f"{split['validation_size']:,}", "explanation": "30% 分层抽样，用于评估与案例验证"},
        ]
    )

    left, right = st.columns([1.1, 1], gap="large")
    with left:
        render_section_title("建模边界", "DATA SPLIT")
        render_report_card(
            "训练与验证划分",
            "系统使用 70%/30% 随机分层抽样划分训练集和验证集，保持购买/未购买比例一致。"
            "逻辑回归只在训练集上训练，验证集用于模型评估和前端案例验证。",
        )
        render_report_card(
            "duration 字段处理",
            "duration 是通话发生后才知道的结果变量，因此只用于历史复盘展示，不参与营销前客户筛选预测。",
        )
        render_section_title("变量中英文对照", "VARIABLES")
        variable_rows = build_variable_reference_rows()
        render_variable_summary_cards(variable_rows)
        with st.expander("查看变量中英文对照", expanded=False):
            render_static_table(variable_rows, ["英文变量", "中文含义", "是否进入模型", "说明"])
    with right:
        render_section_title("目标变量分布", "TARGET")
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
    validation_frame = get_validation_predictions()
    validation_summary = build_validation_result_summary(validation_frame)

    render_section_title("模型效果指标", "MODEL METRICS")
    metric_cards = build_metric_cards(metrics)
    render_metric_cards(metric_cards)

    render_section_title("验证集预测摘要", "VALIDATION SUMMARY")
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    with col1:
        render_metric_card("验证集客户数", f"{validation_summary['total']:,}", "用于评估模型效果的样本数")
    with col2:
        render_metric_card("预测正确", f"{validation_summary['correct']:,}", "真实标签与预测标签一致")
    with col3:
        render_metric_card("预测错误", f"{validation_summary['incorrect']:,}", "需要在报告中说明局限")
    with col4:
        render_metric_card("真实购买客户", f"{validation_summary['actual_yes']:,}", "验证集中实际购买定期存款")
    with col5:
        render_metric_card("预测购买客户", f"{validation_summary['predicted_yes']:,}", "模型建议优先营销的人群")

    left, right = st.columns([0.95, 1.05], gap="large")
    with left:
        render_section_title("混淆矩阵", "CONFUSION MATRIX")
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
        business_rows = pd.DataFrame(build_confusion_matrix_business_rows(metrics))
        st.dataframe(business_rows, hide_index=True, use_container_width=True)
    with right:
        render_section_title("主要影响因素", "FEATURE EFFECTS")
        influence_frame = pd.DataFrame(summary["feature_influences"])
        st.dataframe(
            influence_frame.rename(
                columns={"feature": "特征", "coefficient": "系数", "direction": "影响方向"}
            ),
            hide_index=True,
            use_container_width=True,
        )
        render_report_card("解释边界", "系数方向用于辅助解释模型，不等同于因果关系。")

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        render_section_title("验证集预测概率分布", "VALIDATION PROBABILITY")
        probability_frame = build_probability_distribution(validation_frame)
        fig = go.Figure()
        for label, color in [("未购买 no", "#93c5fd"), ("购买 yes", "#2563eb")]:
            values = probability_frame.loc[probability_frame["真实标签"] == label, "预测概率"]
            fig.add_trace(
                go.Histogram(
                    x=values,
                    name=label,
                    opacity=0.72,
                    marker_color=color,
                    xbins=dict(start=0, end=1, size=0.05),
                )
            )
        fig.update_layout(
            barmode="overlay",
            height=360,
            margin=dict(l=36, r=24, t=34, b=42),
            xaxis_title="模型预测购买概率",
            yaxis_title="客户数",
            legend_title="真实标签",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        render_report_card(
            "图表来源与解读",
            "该图来自 artifacts/validation_predictions.csv，即 30% 验证集。"
            "它展示模型在验证集上给出的购买概率分布，不包含训练集，也不是全体数据集。"
            "如果真实购买客户更多集中在高概率区间，说明模型具有一定客户排序能力。",
        )
    with right:
        render_section_title("营销优先级分布", "PRIORITY")
        priority_frame = build_priority_distribution(validation_frame)
        fig = go.Figure(
            data=[
                go.Bar(
                    x=priority_frame["营销优先级"],
                    y=priority_frame["客户数"],
                    marker_color=["#2563eb", "#f59e0b", "#94a3b8"],
                    text=priority_frame["客户数"],
                    textposition="outside",
                    cliponaxis=False,
                )
            ]
        )
        fig.update_layout(
            height=330,
            margin=dict(l=36, r=24, t=52, b=42),
            yaxis_title="客户数",
            yaxis=dict(range=[0, float(priority_frame["客户数"].max()) * 1.18]),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        display_frame = priority_frame.copy()
        display_frame["真实购买率"] = display_frame["真实购买率"].map(lambda value: f"{value * 100:.1f}%")
        display_frame["平均预测概率"] = display_frame["平均预测概率"].map(lambda value: f"{value * 100:.1f}%")
        render_static_table(
            display_frame.to_dict("records"),
            ["营销优先级", "客户数", "真实购买数", "真实购买率", "平均预测概率"],
        )
        render_section_title("客户分组依据", "RULES")
        render_priority_rule_cards(build_priority_rule_rows())


def _render_prediction_tab(validation_frame: pd.DataFrame, summary: dict, bundle) -> None:
    render_section_title("选择验证集样本或手动输入客户", "CASE VALIDATION")
    mode = st.radio(
        "验证方式",
        ["验证集样本", "手动输入客户"],
        horizontal=True,
    )
    if st.session_state.get("prediction_mode") != mode:
        st.session_state["prediction_mode"] = mode
        st.session_state["prediction_context"] = None
        st.session_state["llm_sections"] = None
        st.session_state["llm_status"] = None

    if mode == "验证集样本":
        context = _build_validation_case_context(validation_frame, summary)
    else:
        context = _build_manual_case_context(bundle)

    if context is not None:
        _render_prediction_result(context)
        if st.button("生成客户画像与营销建议", use_container_width=True):
            with st.spinner("正在生成画像与营销建议..."):
                result = generate_llm_sections(context)
                st.session_state["llm_sections"] = result["sections"]
                st.session_state["llm_status"] = result["llm_status"]
            render_status_card("画像与营销建议已生成", "请切换到第 4 个 Tab 查看 LLM 画像与营销建议。", ok=True)


def _build_validation_case_context(validation_frame: pd.DataFrame, summary: dict) -> dict | None:
    case_options = build_case_options(validation_frame, summary["representative_cases"])
    label_map = {
        int(row["customer_id"]): build_case_option_label(row)
        for _, row in validation_frame.iterrows()
        if int(row["customer_id"]) in case_options
    }
    selected_id = st.selectbox(
        "选择验证集客户",
        options=case_options,
        format_func=lambda value: label_map.get(int(value), f"客户 {value}"),
    )
    st.session_state["selected_customer_id"] = int(selected_id)
    if st.button("运行逻辑回归预测", use_container_width=True):
        row = validation_frame.loc[validation_frame["customer_id"] == selected_id].iloc[0]
        context = build_prediction_context_from_validation(row, summary["feature_influences"])
        st.session_state["prediction_context"] = context
        st.session_state["llm_sections"] = None
        st.session_state["llm_status"] = None
    context = st.session_state.get("prediction_context")
    if context is None:
        render_status_card("等待预测", "请选择一个验证集客户，并点击“运行逻辑回归预测”查看结果。", ok=True)
        return None
    return context


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
            submitted = st.form_submit_button("运行逻辑回归预测", use_container_width=True)

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
    if submitted:
        context = build_prediction_context_from_manual(raw_values, bundle)
        st.session_state["prediction_context"] = context
        st.session_state["llm_sections"] = None
        st.session_state["llm_status"] = None
    context = st.session_state.get("prediction_context")
    if context is None:
        render_status_card("等待预测", "请填写客户字段，并点击“运行逻辑回归预测”查看结果。", ok=True)
        return None
    return context


def _render_prediction_result(context: dict) -> None:
    result = context["model_result"]
    features = context["features"]
    render_decision_cards(
        [
            {
                "label": "预测购买概率",
                "value": f"{result['conversion_probability'] * 100:.1f}%",
                "note": "逻辑回归模型输出",
            },
            {"label": "预测类别", "value": result["predicted_label"], "note": "阈值 0.5 转换"},
            {"label": "营销优先级", "value": result["priority_level"], "note": "用于资源分配"},
            {"label": "推荐渠道", "value": result["recommended_channel"], "note": "基于概率规则生成"},
        ]
    )

    left, right = st.columns([1, 1], gap="large")
    with left:
        render_section_title("客户特征", "FEATURES")
        render_static_table(build_feature_display_rows(features), ["字段", "英文变量", "取值"])
    with right:
        render_section_title("验证结果", "RESULT")
        if result.get("actual_label") is None:
            render_status_card("手动输入客户", "该客户来自手动输入，没有真实标签。", ok=True)
        else:
            status_text = "预测正确" if result["is_correct"] else "预测错误"
            render_status_card(status_text, result["error_type"], ok=bool(result["is_correct"]))
            validation_rows = pd.DataFrame(
                [
                    {"项目": "真实标签", "结果": result["actual_label"]},
                    {"项目": "预测标签", "结果": result["predicted_label"]},
                    {"项目": "预测是否正确", "结果": "是" if result["is_correct"] else "否"},
                    {"项目": "误判类型", "结果": result["error_type"]},
                ]
            )
            st.dataframe(validation_rows, hide_index=True, use_container_width=True)
        render_report_card("推荐动作", f"{result['product_name']}。{result['recommended_action']}")


def _render_llm_tab() -> None:
    render_section_title("LLM连接检测", "CONNECTION")
    render_llm_config_cards(get_llm_config_summary())
    if st.button("测试 LLM 连接", use_container_width=True):
        with st.spinner("正在测试 LLM 连接..."):
            st.session_state["llm_connection_status"] = test_llm_connection()
    connection_status = st.session_state.get("llm_connection_status")
    if connection_status is not None:
        render_status_card(
            connection_status["title"],
            connection_status["message"],
            ok=bool(connection_status["ok"]),
        )

    context = st.session_state.get("prediction_context")
    sections = st.session_state.get("llm_sections")
    llm_status = st.session_state.get("llm_status")
    if context is None:
        render_status_card("尚未完成预测", "请先在第 3 个 Tab 选择或输入客户，并运行逻辑回归预测。", ok=False)
        return
    if sections is None:
        render_status_card("尚未生成画像", "请回到第 3 个 Tab 点击“生成客户画像与营销建议”。", ok=False)
        return
    render_status_card(
        f"LLM状态：{llm_status}",
        "LLM 解释基于模型输出和客户字段生成，不参与购买概率预测，也不改变营销优先级。",
        ok=str(llm_status).endswith("生成成功"),
    )
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        render_llm_card("客户画像", sections["customer_profile"])
    with col2:
        render_llm_card("营销建议", sections["marketing_strategy"])
    with col3:
        render_llm_card("风险与注意事项", sections["risk_note"])
    render_section_title("推荐话术", "SCRIPT")
    render_report_card("客户沟通话术", sections["marketing_script"])


if __name__ == "__main__":
    main()
