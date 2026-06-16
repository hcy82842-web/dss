from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.dss_frontend.data_loader import (
    REQUIRED_BUSINESS_FIELDS,
    build_manual_scoring_row,
    load_customer_frame,
    load_scoring_frame,
)
from src.dss_backend.ml.inference import load_model_bundle
from src.dss_frontend.decision_engine import build_decision_view, enrich_with_model_decisions
from src.dss_frontend.schema import AGE_GROUP_LABELS, BUSINESS_INPUT_COLUMNS, PRIORITY_LEVELS
from src.dss_frontend.service_layer import build_dashboard_state
from src.dss_frontend.theme import apply_theme
from src.dss_frontend.ui_components import (
    render_candidate_snapshot_panel,
    render_candidate_table,
    render_customer_detail,
    render_dashboard_header,
    render_distribution_panel,
    render_filter_summary,
    render_filter_toolbar_title,
    render_month_trend_panel,
    render_priority_heatmap_panel,
    render_section_banner,
    render_summary_cards,
    render_workflow_steps,
    render_channel_matrix_panel,
)

DATA_CANDIDATES = [
    Path("data/bank-additional-full.csv"),
    Path("C:/Users/郏天宇/Desktop/bank-additional-full.csv"),
]
MODEL_ARTIFACT_PATH = Path("artifacts/logistic_regression.joblib")
MODEL_METADATA_PATH = Path("artifacts/model_metadata.json")


def resolve_data_path() -> Path:
    for candidate in DATA_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Cannot find bank-additional-full.csv")


@st.cache_resource(show_spinner=False)
def build_model_bundle():
    return load_model_bundle(MODEL_ARTIFACT_PATH, MODEL_METADATA_PATH)


def enrich_decision_frame(frame: pd.DataFrame) -> pd.DataFrame:
    try:
        bundle = build_model_bundle()
        return enrich_with_model_decisions(frame, bundle)
    except Exception as exc:
        st.session_state["model_fallback_warning"] = str(exc)
        decisions = frame.apply(build_decision_view, axis=1, result_type="expand")
        return frame.join(decisions.drop(columns=["customer_label"]))


@st.cache_data(show_spinner=False)
def build_training_frame() -> pd.DataFrame:
    frame = load_customer_frame(resolve_data_path())
    return enrich_decision_frame(frame)


@st.cache_data(show_spinner=False)
def build_scoring_frame(csv_text: str) -> pd.DataFrame:
    csv_buffer = StringIO(csv_text)
    frame = load_scoring_frame(csv_buffer)
    return enrich_decision_frame(frame)


def build_default_scoring_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
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
            },
            {
                "age": 34,
                "job": "technician",
                "marital": "single",
                "education": "professional.course",
                "default": "no",
                "housing": "no",
                "loan": "yes",
                "contact": "telephone",
                "month": "nov",
                "duration": 120,
                "campaign": 4,
                "pdays": 999,
                "previous": 0,
                "poutcome": "nonexistent",
            },
            {
                "age": 56,
                "job": "retired",
                "marital": "married",
                "education": "basic.9y",
                "default": "no",
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "month": "may",
                "duration": 310,
                "campaign": 2,
                "pdays": 12,
                "previous": 2,
                "poutcome": "success",
            },
        ]
    )


def submit_manual_customer_form() -> None:
    raw_values = {
        "age": st.session_state.get("manual_age"),
        "job": st.session_state.get("manual_job"),
        "marital": st.session_state.get("manual_marital"),
        "education": st.session_state.get("manual_education"),
        "default": st.session_state.get("manual_default"),
        "housing": st.session_state.get("manual_housing"),
        "loan": st.session_state.get("manual_loan"),
        "contact": st.session_state.get("manual_contact"),
        "month": st.session_state.get("manual_month"),
        "duration": st.session_state.get("manual_duration"),
        "campaign": st.session_state.get("manual_campaign"),
        "pdays": st.session_state.get("manual_pdays"),
        "previous": st.session_state.get("manual_previous"),
        "poutcome": st.session_state.get("manual_poutcome"),
    }
    st.session_state["manual_form_error"] = None
    try:
        row = build_manual_scoring_row(raw_values)
    except ValueError as exc:
        st.session_state["manual_form_error"] = str(exc)
        return
    manual_frame = st.session_state["manual_scoring_data"].copy()
    st.session_state["manual_scoring_data"] = pd.concat([manual_frame, pd.DataFrame([row])], ignore_index=True)


def main() -> None:
    st.set_page_config(
        page_title="银行零售业务智能营销决策支持系统",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_theme()

    training_frame = build_training_frame()
    model_warning = st.session_state.get("model_fallback_warning")
    if model_warning:
        st.warning(f"当前未能加载逻辑回归模型，页面已回退到离线规则演示：{model_warning}")

    uploaded_file = st.session_state.get("uploaded_scoring_file")
    selected_business_customer_id = st.session_state.get("selected_business_customer_id")

    if "manual_scoring_seeded" not in st.session_state:
        st.session_state["manual_scoring_seeded"] = True
        st.session_state["manual_scoring_data"] = build_default_scoring_frame()

    header_slot = st.container(key="hero_shell")
    summary_slot = st.container(key="summary_shell")
    workflow_slot = st.container(key="workflow_shell")

    training_state = build_dashboard_state(
        enriched_frame=training_frame,
        selected_priority_levels=[],
        selected_jobs=[],
        selected_months=[],
        selected_contacts=[],
        selected_age_groups=[],
        selected_customer_id=None,
    )

    with header_slot:
        render_dashboard_header(
            total_customers=len(training_frame),
            candidate_count=len(training_state["candidate_frame"]),
        )

    with summary_slot:
        render_summary_cards(training_state["dashboard_analytics"]["summary_cards"])

    with workflow_slot:
        render_workflow_steps(training_state["dashboard_analytics"]["workflow_steps"])

    with st.container(key="analytics_shell"):
        render_section_banner(
            "训练数据与模型概览",
            "这里展示的是课程作业里的训练样本和分析结果，用来支撑模型训练、效果对比和答辩展示，不直接当作真实业务客户池使用。",
            "TRAINING DATA",
        )
        analytics = training_state["dashboard_analytics"]
        top_left, top_middle, top_right = st.columns([1.02, 0.92, 1.26], gap="medium")
        with top_left:
            render_distribution_panel(analytics["channel_mix"], analytics["job_rank"])
        with top_middle:
            render_priority_heatmap_panel(analytics["age_priority_matrix"])
        with top_right:
            render_month_trend_panel(analytics["month_trend"])

    with st.container(key="filter_shell"):
        render_section_banner(
            "业务客户导入",
            "真实业务判断应由银行员工导入待触达客户，或者现场手动录入单个客户信息。训练集只用于模型训练，不直接进入营销执行。",
            "BUSINESS INPUT",
        )
        upload_col, manual_col = st.columns([1.05, 1.35], gap="medium")
        with upload_col:
            render_filter_toolbar_title()
            st.caption("导入文件字段应包含以下列，并使用分号分隔。")
            st.code("; ".join(BUSINESS_INPUT_COLUMNS), language="text")
            uploaded_file = st.file_uploader(
                "上传待判断客户 CSV",
                type=["csv"],
                help="导入后系统会按当前规则对每个客户生成优先级、渠道建议和单客户解释。",
            )
        with manual_col:
            st.markdown("#### 手动录入单个客户")
            st.caption("必填字段：age / job / contact / month / campaign / previous。其他字段可先留空，系统会自动补默认值并提示影响。")
            with st.form("manual_customer_form", clear_on_submit=False):
                form_col1, form_col2, form_col3 = st.columns(3, gap="medium")
                with form_col1:
                    st.text_input("年龄*", value="40", key="manual_age")
                    st.text_input("职业*", value="management", key="manual_job")
                    st.selectbox("联系渠道*", options=["cellular", "telephone"], key="manual_contact")
                    st.selectbox("月份*", options=["mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], key="manual_month")
                    st.text_input("本次联系次数*", value="1", key="manual_campaign")
                with form_col2:
                    st.text_input("历史联系次数*", value="0", key="manual_previous")
                    st.selectbox("婚姻", options=["", "single", "married", "divorced"], key="manual_marital")
                    st.text_input("教育", value="", key="manual_education")
                    st.selectbox("违约", options=["", "no", "yes"], key="manual_default")
                    st.selectbox("房贷", options=["", "no", "yes"], key="manual_housing")
                with form_col3:
                    st.selectbox("贷款", options=["", "no", "yes"], key="manual_loan")
                    st.text_input("通话时长", value="", key="manual_duration")
                    st.text_input("距上次联系天数", value="", key="manual_pdays")
                    st.selectbox("历史结果", options=["", "success", "failure", "nonexistent"], key="manual_poutcome")
                    submitted = st.form_submit_button("加入业务客户池", use_container_width=True, on_click=submit_manual_customer_form)
            if st.session_state.get("manual_form_error"):
                st.warning(st.session_state["manual_form_error"])
            required_text = "、".join(REQUIRED_BUSINESS_FIELDS)
            st.markdown(
                f"<div class='filter-chip-row'><span class='filter-chip'><strong>必填字段</strong>{required_text}</span><span class='filter-chip'><strong>缺失处理</strong>选填项将自动补默认值并降低结果可信度</span></div>",
                unsafe_allow_html=True,
            )

    if uploaded_file is not None:
        scoring_csv_text = uploaded_file.getvalue().decode("utf-8")
        scoring_frame = build_scoring_frame(scoring_csv_text)
        data_source_label = "当前来源：上传的业务客户 CSV"
    else:
        manual_frame = st.session_state["manual_scoring_data"].copy()
        scoring_csv_text = manual_frame.to_csv(index=False, sep=";")
        scoring_frame = build_scoring_frame(scoring_csv_text)
        data_source_label = "当前来源：手动录入的业务客户"

    with st.container(key="filter_summary_shell"):
        st.markdown(
            f"<div class='filter-chip-row'><span class='filter-chip'><strong>业务数据</strong>{data_source_label}</span><span class='filter-chip'><strong>待判断客户数</strong>{len(scoring_frame):,}</span></div>",
            unsafe_allow_html=True,
        )

    with st.container(key="workspace_shell"):
        render_section_banner(
            "业务客户决策工作台",
            "这里展示的才是实际待判断客户。系统会对导入客户生成分层、推荐渠道、单客户解释和建议话术，直接对应你的 DSS 业务逻辑。",
            "EXECUTION DESK",
        )

        filter_columns = st.columns(5, gap="medium")
        with filter_columns[0]:
            selected_priority_levels = st.multiselect(
                "客户价值层级",
                PRIORITY_LEVELS,
                placeholder="选择价值层级",
            )
        with filter_columns[1]:
            selected_jobs = st.multiselect(
                "职业",
                sorted(scoring_frame["job"].unique().tolist()),
                placeholder="选择职业",
            )
        with filter_columns[2]:
            selected_months = st.multiselect(
                "月份",
                sorted(scoring_frame["month"].unique().tolist()),
                placeholder="选择月份",
            )
        with filter_columns[3]:
            selected_contacts = st.multiselect(
                "联系渠道",
                sorted(scoring_frame["contact"].unique().tolist()),
                placeholder="选择联系渠道",
            )
        with filter_columns[4]:
            selected_age_groups = st.multiselect(
                "年龄层级",
                AGE_GROUP_LABELS,
                placeholder="选择年龄层级",
            )

        render_filter_summary(
            selected_priority_levels,
            selected_jobs,
            selected_months,
            selected_contacts,
            selected_age_groups,
        )

        base_state = build_dashboard_state(
            enriched_frame=scoring_frame,
            selected_priority_levels=selected_priority_levels,
            selected_jobs=selected_jobs,
            selected_months=selected_months,
            selected_contacts=selected_contacts,
            selected_age_groups=selected_age_groups,
            selected_customer_id=selected_business_customer_id,
        )

        final_state = base_state
        if base_state["candidate_frame"].empty:
            st.info("当前业务筛选条件下没有待判断客户，请调整筛选器或导入新的客户数据。")
        else:
            options = base_state["candidate_frame"]["customer_id"].tolist()
            labels = dict(zip(base_state["candidate_frame"]["customer_id"], base_state["candidate_frame"]["customer_label"]))
            chosen_customer_id = st.selectbox(
                "当前查看业务客户",
                options=options,
                index=options.index(base_state["selected_customer_id"]),
                format_func=lambda item: labels[item],
            )
            st.session_state["selected_business_customer_id"] = chosen_customer_id
            final_state = build_dashboard_state(
                enriched_frame=scoring_frame,
                selected_priority_levels=selected_priority_levels,
                selected_jobs=selected_jobs,
                selected_months=selected_months,
                selected_contacts=selected_contacts,
                selected_age_groups=selected_age_groups,
                selected_customer_id=chosen_customer_id,
            )

        bottom_left, bottom_right = st.columns([0.82, 1.38], gap="medium")
        with bottom_left:
            render_candidate_snapshot_panel(final_state["candidate_frame"], final_state["selected_customer_id"])
            render_channel_matrix_panel(final_state["dashboard_analytics"]["channel_matrix"])

        with bottom_right:
            if final_state["selected_customer"] is None:
                st.info("请选择一个业务客户查看决策详情。")
            else:
                notice = final_state["selected_customer"].get("missing_field_notice")
                if isinstance(notice, dict):
                    st.warning(
                        f"字段完整度 {int(notice['completeness_ratio'] * 100)}%。{notice['impact_text']}"
                    )
                decision_tab, table_tab = st.tabs(["单客户决策", "业务客户明细表"])
                with decision_tab:
                    render_customer_detail(
                        final_state["selected_customer"],
                        final_state["selected_decision"],
                        final_state["customer_explanation"],
                        final_state["customer_script"],
                    )
                with table_tab:
                    render_candidate_table(final_state["candidate_frame"])


if __name__ == "__main__":
    main()
