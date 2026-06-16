# DSS Frontend Homepage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit homepage for the bank retail marketing decision support system with `summary metrics + filters + customer list + single-customer detail`, where LLM explanation and sales script are strictly bound to the currently selected customer.

**Architecture:** Use a single Streamlit entrypoint plus a small `src` package to separate data loading, filtering, metrics, recommendation logic, and explanation generation. The first implementation uses local CSV data and deterministic template-based explanation generation so the UI can run end-to-end before real model and API integration.

**Tech Stack:** Python, Streamlit, pandas, plotly, pytest

---

## File Structure

- Create: `E:\决策支持系统\requirements.txt`
  - Python dependencies for local run and test.
- Create: `E:\决策支持系统\README.md`
  - Project startup instructions for the course demo.
- Create: `E:\决策支持系统\app.py`
  - Streamlit entrypoint, page layout, session state wiring.
- Create: `E:\决策支持系统\src\dss_frontend\__init__.py`
  - Package marker.
- Create: `E:\决策支持系统\src\dss_frontend\schema.py`
  - Centralized field names and UI labels.
- Create: `E:\决策支持系统\src\dss_frontend\data_loader.py`
  - Read CSV, normalize columns, prepare display fields.
- Create: `E:\决策支持系统\src\dss_frontend\filters.py`
  - Filter model and customer subset logic.
- Create: `E:\决策支持系统\src\dss_frontend\metrics.py`
  - Summary KPI calculation.
- Create: `E:\决策支持系统\src\dss_frontend\decision_engine.py`
  - Local scoring proxy, priority level, channel suggestion, product suggestion.
- Create: `E:\决策支持系统\src\dss_frontend\llm_cards.py`
  - Template-based explanation and sales script bound to one customer.
- Create: `E:\决策支持系统\src\dss_frontend\ui_components.py`
  - Focused rendering helpers for Streamlit sections.
- Create: `E:\决策支持系统\src\dss_frontend\theme.py`
  - CSS injection and design tokens matching the approved visual direction.
- Create: `E:\决策支持系统\tests\test_data_loader.py`
  - Data normalization tests.
- Create: `E:\决策支持系统\tests\test_filters.py`
  - Filter behavior tests.
- Create: `E:\决策支持系统\tests\test_decision_engine.py`
  - Recommendation logic tests.
- Create: `E:\决策支持系统\tests\test_llm_cards.py`
  - Single-customer explanation binding tests.

### Task 1: Bootstrap Project Skeleton

**Files:**
- Create: `E:\决策支持系统\requirements.txt`
- Create: `E:\决策支持系统\README.md`
- Create: `E:\决策支持系统\src\dss_frontend\__init__.py`

- [ ] **Step 1: Create dependency file**

```txt
streamlit==1.46.1
pandas==2.3.0
plotly==6.1.2
pytest==8.4.1
```

- [ ] **Step 2: Create startup README**

````md
# 决策支持系统前端

## 运行

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
````

## 数据文件

将 `bank-additional-full.csv` 放在以下路径之一：

- `data/bank-additional-full.csv`
- `C:/Users/郏天宇/Desktop/bank-additional-full.csv`

## 当前范围

- 首页工作台
- 筛选器
- 客户候选名单
- 单客户决策详情
- 模板化解释与建议话术
```

- [ ] **Step 3: Create package marker**

```python
"""Frontend package for the DSS course project."""
```

- [ ] **Step 4: Verify files exist**

Run: `Get-ChildItem E:\决策支持系统\requirements.txt, E:\决策支持系统\README.md, E:\决策支持系统\src\dss_frontend\__init__.py`
Expected: 3 files listed

- [ ] **Step 5: Commit**

```bash
git add requirements.txt README.md src/dss_frontend/__init__.py
git commit -m "chore: bootstrap dss frontend project skeleton"
```

### Task 2: Define Dataset Schema And Loader

**Files:**
- Create: `E:\决策支持系统\src\dss_frontend\schema.py`
- Create: `E:\决策支持系统\src\dss_frontend\data_loader.py`
- Test: `E:\决策支持系统\tests\test_data_loader.py`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pandas as pd

from src.dss_frontend.data_loader import load_customer_frame


def test_load_customer_frame_adds_display_columns(tmp_path: Path):
    csv_path = tmp_path / "bank.csv"
    pd.DataFrame(
        [
            {
                "age": 42,
                "job": "management",
                "marital": "married",
                "education": "university.degree",
                "default": "no",
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "month": "may",
                "duration": 180,
                "campaign": 2,
                "pdays": 999,
                "previous": 0,
                "poutcome": "nonexistent",
                "y": "yes",
            }
        ]
    ).to_csv(csv_path, index=False, sep=";")

    frame = load_customer_frame(csv_path)

    assert "customer_id" in frame.columns
    assert "customer_label" in frame.columns
    assert "response_flag" in frame.columns
    assert "age_group" in frame.columns
    assert frame.loc[0, "customer_label"] == "客户 1001"
    assert frame.loc[0, "response_flag"] == 1


def test_load_customer_frame_rejects_missing_required_columns(tmp_path: Path):
    csv_path = tmp_path / "broken.csv"
    pd.DataFrame([{"age": 42, "job": "management"}]).to_csv(csv_path, index=False, sep=";")

    try:
        load_customer_frame(csv_path)
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing columns")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest E:\决策支持系统\tests\test_data_loader.py -v`
Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'load_customer_frame'`

- [ ] **Step 3: Create schema constants**

```python
REQUIRED_COLUMNS = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "y",
]

DISPLAY_LABELS = {
    "age": "年龄",
    "job": "职业",
    "marital": "婚姻",
    "education": "教育",
    "default": "违约",
    "housing": "房贷",
    "loan": "个人贷",
    "contact": "联系渠道",
    "month": "月份",
    "duration": "通话时长",
    "campaign": "本次联系次数",
    "pdays": "历史联系间隔",
    "previous": "历史联系次数",
    "poutcome": "历史结果",
    "y": "目标结果",
}
```

- [ ] **Step 4: Implement customer loader**

```python
from pathlib import Path

import pandas as pd

from .schema import REQUIRED_COLUMNS


def load_customer_frame(csv_path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path, sep=";")
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    normalized = frame.copy()
    normalized = normalized.reset_index(drop=True)
    normalized["customer_id"] = normalized.index + 1001
    normalized["customer_label"] = normalized["customer_id"].map(lambda value: f"客户 {value}")
    normalized["response_flag"] = normalized["y"].map({"yes": 1, "no": 0}).fillna(0).astype(int)
    normalized["age_group"] = pd.cut(
        normalized["age"],
        bins=[0, 35, 50, 120],
        labels=["25-35", "36-50", "50+"],
        include_lowest=True,
    ).astype(str)
    normalized["month"] = normalized["month"].astype(str).str.lower()
    normalized["job"] = normalized["job"].astype(str).str.lower()
    return normalized
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest E:\决策支持系统\tests\test_data_loader.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/dss_frontend/schema.py src/dss_frontend/data_loader.py tests/test_data_loader.py
git commit -m "feat: add dataset schema and loader"
```

### Task 3: Implement Filter Model

**Files:**
- Create: `E:\决策支持系统\src\dss_frontend\filters.py`
- Test: `E:\决策支持系统\tests\test_filters.py`

- [ ] **Step 1: Write the failing tests**

```python
import pandas as pd

from src.dss_frontend.filters import apply_filters


def test_apply_filters_supports_job_month_contact_age_and_priority():
    frame = pd.DataFrame(
        [
            {
                "customer_label": "客户 1001",
                "job": "management",
                "month": "may",
                "contact": "cellular",
                "age_group": "36-50",
                "priority_level": "高价值客户",
            },
            {
                "customer_label": "客户 1002",
                "job": "admin.",
                "month": "jun",
                "contact": "telephone",
                "age_group": "25-35",
                "priority_level": "低响应客户",
            },
        ]
    )

    filtered = apply_filters(
        frame,
        selected_priority_levels=["高价值客户"],
        selected_jobs=["management"],
        selected_months=["may"],
        selected_contacts=["cellular"],
        selected_age_groups=["36-50"],
    )

    assert filtered["customer_label"].tolist() == ["客户 1001"]


def test_apply_filters_returns_original_when_no_filters():
    frame = pd.DataFrame(
        [
            {"customer_label": "客户 1001", "job": "management", "month": "may", "contact": "cellular"},
            {"customer_label": "客户 1002", "job": "admin.", "month": "jun", "contact": "telephone"},
        ]
    )

    filtered = apply_filters(frame, [], [], [], [], [])

    assert filtered.equals(frame)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest E:\决策支持系统\tests\test_filters.py -v`
Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'apply_filters'`

- [ ] **Step 3: Implement filter function**

```python
import pandas as pd


def apply_filters(
    frame: pd.DataFrame,
    selected_priority_levels: list[str],
    selected_jobs: list[str],
    selected_months: list[str],
    selected_contacts: list[str],
    selected_age_groups: list[str],
) -> pd.DataFrame:
    filtered = frame.copy()

    if selected_priority_levels:
        filtered = filtered[filtered["priority_level"].isin(selected_priority_levels)]
    if selected_jobs:
        filtered = filtered[filtered["job"].isin(selected_jobs)]
    if selected_months:
        filtered = filtered[filtered["month"].isin(selected_months)]
    if selected_contacts:
        filtered = filtered[filtered["contact"].isin(selected_contacts)]
    if selected_age_groups:
        filtered = filtered[filtered["age_group"].isin(selected_age_groups)]

    return filtered.reset_index(drop=True)
```

- [ ] **Step 4: Add helper for default selected customer**

```python
def default_selected_customer_id(frame: pd.DataFrame) -> int | None:
    if frame.empty:
        return None
    return int(frame.iloc[0]["customer_id"])
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest E:\决策支持系统\tests\test_filters.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/dss_frontend/filters.py tests/test_filters.py
git commit -m "feat: add homepage filter logic"
```

### Task 4: Implement Decision Engine

**Files:**
- Create: `E:\决策支持系统\src\dss_frontend\decision_engine.py`
- Test: `E:\决策支持系统\tests\test_decision_engine.py`

- [ ] **Step 1: Write the failing tests**

```python
import pandas as pd

from src.dss_frontend.decision_engine import build_decision_view


def test_build_decision_view_generates_probability_and_channel():
    row = pd.Series(
        {
            "customer_label": "客户 1001",
            "age": 42,
            "job": "management",
            "contact": "cellular",
            "campaign": 2,
            "previous": 1,
            "housing": "yes",
            "loan": "no",
            "response_flag": 1,
        }
    )

    decision = build_decision_view(row)

    assert 0.0 <= decision["conversion_probability"] <= 1.0
    assert decision["priority_level"] in {"高价值客户", "中价值客户", "低响应客户"}
    assert decision["recommended_channel"] in {"电话", "短信", "邮件"}
    assert isinstance(decision["recommended_action"], str)


def test_build_decision_view_binds_output_to_customer():
    row = pd.Series(
        {
            "customer_label": "客户 1002",
            "age": 31,
            "job": "technician",
            "contact": "telephone",
            "campaign": 5,
            "previous": 0,
            "housing": "no",
            "loan": "yes",
            "response_flag": 0,
        }
    )

    decision = build_decision_view(row)

    assert decision["customer_label"] == "客户 1002"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest E:\决策支持系统\tests\test_decision_engine.py -v`
Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'build_decision_view'`

- [ ] **Step 3: Implement scoring and recommendation logic**

```python
import pandas as pd


def build_decision_view(row: pd.Series) -> dict:
    probability = 0.35
    probability += 0.18 if row.get("response_flag", 0) == 1 else 0.0
    probability += 0.08 if row.get("campaign", 0) <= 2 else -0.04
    probability += 0.07 if row.get("previous", 0) > 0 else 0.0
    probability += 0.06 if row.get("contact") == "cellular" else 0.0
    probability = max(0.05, min(0.95, round(probability, 2)))

    if probability >= 0.75:
        priority_level = "高价值客户"
        recommended_channel = "电话"
        product_name = "6个月定期存款"
        recommended_action = "建议在48小时内电话触达，主推6个月定期存款。"
    elif probability >= 0.55:
        priority_level = "中价值客户"
        recommended_channel = "短信"
        product_name = "稳健型存款产品"
        recommended_action = "建议先短信触达，再根据反馈决定是否电话跟进。"
    else:
        priority_level = "低响应客户"
        recommended_channel = "邮件"
        product_name = "基础存款产品"
        recommended_action = "建议暂不优先电话触达，先使用低成本渠道观察。"

    return {
        "customer_label": row["customer_label"],
        "conversion_probability": probability,
        "priority_level": priority_level,
        "recommended_channel": recommended_channel,
        "product_name": product_name,
        "recommended_action": recommended_action,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest E:\决策支持系统\tests\test_decision_engine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/dss_frontend/decision_engine.py tests/test_decision_engine.py
git commit -m "feat: add local decision engine for customer recommendations"
```

### Task 5: Implement Single-Customer Explanation Cards

**Files:**
- Create: `E:\决策支持系统\src\dss_frontend\llm_cards.py`
- Test: `E:\决策支持系统\tests\test_llm_cards.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.dss_frontend.llm_cards import build_customer_explanation, build_customer_script


def test_build_customer_explanation_mentions_selected_customer_context():
    customer = {
        "customer_label": "客户 1001",
        "job": "management",
        "month": "may",
        "housing": "yes",
    }
    decision = {
        "conversion_probability": 0.82,
        "recommended_channel": "电话",
    }

    explanation = build_customer_explanation(customer, decision)

    assert "客户 1001" in explanation
    assert "电话" in explanation
    assert "0.82" in explanation


def test_build_customer_script_is_bound_to_same_customer():
    customer = {
        "customer_label": "客户 1002",
        "job": "technician",
        "month": "jun",
        "housing": "no",
    }
    decision = {
        "product_name": "稳健型存款产品",
    }

    script = build_customer_script(customer, decision)

    assert "客户 1002" in script
    assert "稳健型存款产品" in script
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest E:\决策支持系统\tests\test_llm_cards.py -v`
Expected: FAIL with `ModuleNotFoundError` or `cannot import name 'build_customer_explanation'`

- [ ] **Step 3: Implement explanation generator**

```python
def build_customer_explanation(customer: dict, decision: dict) -> str:
    return (
        f"{customer['customer_label']} 当前预测转化概率为 {decision['conversion_probability']:.2f}，"
        f"建议优先使用{decision['recommended_channel']}触达。"
        f"该客户职业为 {customer['job']}，最近联系月份为 {customer['month']}，"
        "客户特征与当前推荐动作保持一致，因此适合进入本轮重点营销名单。"
    )
```

- [ ] **Step 4: Implement suggestion script generator**

```python
def build_customer_script(customer: dict, decision: dict) -> str:
    return (
        f"{customer['customer_label']} 建议话术：您好，我们结合您的资金安排偏好，"
        f"推荐您了解一下 {decision['product_name']}，这类方案更适合稳健型配置需求。"
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest E:\决策支持系统\tests\test_llm_cards.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/dss_frontend/llm_cards.py tests/test_llm_cards.py
git commit -m "feat: add single-customer explanation cards"
```

### Task 6: Implement Metrics And UI Components

**Files:**
- Create: `E:\决策支持系统\src\dss_frontend\metrics.py`
- Create: `E:\决策支持系统\src\dss_frontend\ui_components.py`
- Create: `E:\决策支持系统\src\dss_frontend\theme.py`

- [ ] **Step 1: Implement KPI helpers**

```python
import pandas as pd


def build_summary_metrics(frame: pd.DataFrame) -> dict:
    total_customers = len(frame)
    high_priority = int((frame["priority_level"] == "高价值客户").sum())
    conversion_rate = round(float(frame["conversion_probability"].mean()) * 100, 1) if total_customers else 0.0
    suggested_budget = high_priority * 300
    return {
        "待评估客户": total_customers,
        "高潜名单": high_priority,
        "预估转化率": f"{conversion_rate}%",
        "建议预算": f"¥{suggested_budget:,}",
    }
```

- [ ] **Step 2: Implement theme injection**

```python
import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15,118,110,0.08), transparent 24%),
                radial-gradient(circle at bottom right, rgba(184,106,44,0.08), transparent 18%),
                linear-gradient(180deg, #f8f4ec 0%, #f2ede5 100%);
        }
        .metric-card, .panel-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(14, 32, 48, 0.08);
            border-radius: 18px;
            padding: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
```

- [ ] **Step 3: Implement UI helper functions**

```python
import streamlit as st


def render_metric_cards(metrics: dict) -> None:
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics.items()):
        column.markdown(f"<div class='metric-card'><div>{label}</div><h3>{value}</h3></div>", unsafe_allow_html=True)


def render_customer_detail(customer: dict, decision: dict, explanation: str, script: str) -> None:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.subheader("单客户决策详情")
    st.write(f"客户：{customer['customer_label']}")
    st.write(f"职业：{customer['job']} / 婚姻：{customer['marital']} / 月份：{customer['month']}")
    st.write(f"转化概率：{decision['conversion_probability']:.2f}")
    st.info(decision["recommended_action"])
    st.success(explanation)
    st.warning(script)
    st.markdown("</div>", unsafe_allow_html=True)
```

- [ ] **Step 4: Verify imports are valid**

Run: `python -c "from src.dss_frontend.metrics import build_summary_metrics; from src.dss_frontend.theme import apply_theme; from src.dss_frontend.ui_components import render_metric_cards"`
Expected: no output, exit code 0

- [ ] **Step 5: Commit**

```bash
git add src/dss_frontend/metrics.py src/dss_frontend/theme.py src/dss_frontend/ui_components.py
git commit -m "feat: add homepage metrics and UI components"
```

### Task 7: Wire The Streamlit Homepage

**Files:**
- Create: `E:\决策支持系统\app.py`

- [ ] **Step 1: Create the Streamlit entrypoint**

```python
from pathlib import Path

import streamlit as st

from src.dss_frontend.data_loader import load_customer_frame
from src.dss_frontend.decision_engine import build_decision_view
from src.dss_frontend.filters import apply_filters, default_selected_customer_id
from src.dss_frontend.llm_cards import build_customer_explanation, build_customer_script
from src.dss_frontend.metrics import build_summary_metrics
from src.dss_frontend.theme import apply_theme
from src.dss_frontend.ui_components import render_customer_detail, render_metric_cards


DATA_CANDIDATES = [
    Path("data/bank-additional-full.csv"),
    Path(r"C:\Users\郏天宇\Desktop\bank-additional-full.csv"),
]


def resolve_data_path() -> Path:
    for candidate in DATA_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Cannot find bank-additional-full.csv")


def main() -> None:
    st.set_page_config(page_title="银行营销决策支持系统", layout="wide")
    apply_theme()
    st.title("银行零售业务智能营销决策支持系统")

    frame = load_customer_frame(resolve_data_path())

    with st.sidebar:
        st.header("筛选器")
        selected_priority_levels = st.multiselect("客户价值层级", ["高价值客户", "中价值客户", "低响应客户"])
        selected_jobs = st.multiselect("职业", sorted(frame["job"].unique().tolist()))
        selected_months = st.multiselect("月份", sorted(frame["month"].unique().tolist()))
        selected_contacts = st.multiselect("联系渠道", sorted(frame["contact"].unique().tolist()))
        selected_age_groups = st.multiselect("年龄层级", sorted(frame["age_group"].unique().tolist()))

    decisions = frame.apply(build_decision_view, axis=1, result_type="expand")
    enriched = frame.join(decisions.drop(columns=["customer_label"]))
    filtered = apply_filters(
        enriched,
        selected_priority_levels,
        selected_jobs,
        selected_months,
        selected_contacts,
        selected_age_groups,
    )

    render_metric_cards(build_summary_metrics(filtered))

    left, middle, right = st.columns([0.85, 1.1, 1.35])

    with left:
        st.subheader("当前筛选摘要")
        st.write(f"价值层级筛选：{selected_priority_levels or '全部'}")
        st.write(f"职业筛选：{selected_jobs or '全部'}")
        st.write(f"月份筛选：{selected_months or '全部'}")
        st.write(f"渠道筛选：{selected_contacts or '全部'}")
        st.write(f"年龄层级筛选：{selected_age_groups or '全部'}")

    with middle:
        st.subheader("客户候选名单")
        if filtered.empty:
            st.warning("当前条件下没有候选客户")
            selected_customer_id = None
        else:
            options = filtered["customer_id"].tolist()
            labels = dict(zip(filtered["customer_id"], filtered["customer_label"]))
            default_id = default_selected_customer_id(filtered)
            selected_customer_id = st.radio(
                "选择客户",
                options=options,
                format_func=lambda item: labels[item],
                index=options.index(default_id),
                label_visibility="collapsed",
            )
            st.dataframe(
                filtered[["customer_label", "conversion_probability", "priority_level", "recommended_channel"]],
                hide_index=True,
                use_container_width=True,
            )

    with right:
        if selected_customer_id is not None:
            customer = filtered.loc[filtered["customer_id"] == selected_customer_id].iloc[0].to_dict()
            decision = {
                "conversion_probability": customer["conversion_probability"],
                "priority_level": customer["priority_level"],
                "recommended_channel": customer["recommended_channel"],
                "product_name": customer["product_name"],
                "recommended_action": customer["recommended_action"],
            }
            explanation = build_customer_explanation(customer, decision)
            script = build_customer_script(customer, decision)
            render_customer_detail(customer, decision, explanation, script)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the app locally**

Run: `streamlit run E:\决策支持系统\app.py`
Expected: browser opens a page with summary metrics, sidebar filters, candidate list, and single-customer detail

- [ ] **Step 3: Verify the critical UX rule manually**

Run: `streamlit run E:\决策支持系统\app.py`
Expected:
- selecting a different customer changes the right-side explanation
- explanation text still references the currently selected customer
- sales script still references the same currently selected customer

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: wire streamlit homepage workbench"
```

### Task 8: Add End-To-End Test Sweep And Demo Polish

**Files:**
- Modify: `E:\决策支持系统\README.md`

- [ ] **Step 1: Run the unit test suite**

Run: `pytest E:\决策支持系统\tests -v`
Expected: PASS

- [ ] **Step 2: Add demo checklist to README**

```md
## 演示检查清单

- 首页能正常打开
- 顶部能看到 4 个摘要指标
- 左侧筛选器能改变候选客户范围
- 中间能看到客户候选名单
- 右侧解释与建议话术会随着所选客户变化
- 右侧内容始终绑定当前选中的单个客户
```

- [ ] **Step 3: Smoke-test the full demo flow**

Run: `streamlit run E:\决策支持系统\app.py`
Expected:
- first screen loads without traceback
- one customer is selected by default
- after changing filters, the list and detail panel still stay consistent

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add demo checklist for dss homepage"
```

## Self-Review

### Spec Coverage

- 顶部摘要指标带：Task 6 + Task 7
- 左侧筛选器：Task 3 + Task 7
- 中间客户候选名单：Task 7
- 右侧单客户决策详情：Task 4 + Task 5 + Task 6 + Task 7
- LLM 解释绑定单客户：Task 5 + Task 7 + Task 8 manual verification
- 适合课堂演示的视觉方向：Task 6 + Task 7

No spec gaps found for the approved homepage scope.

### Placeholder Scan

- No `TODO`
- No `TBD`
- No unresolved “later implement” steps
- Every code-writing step includes concrete code

### Type Consistency

- `customer_id` / `customer_label` defined in loader and reused consistently
- `conversion_probability` / `priority_level` / `recommended_channel` defined in decision engine and reused consistently
- `build_customer_explanation` and `build_customer_script` both accept the same `customer` and `decision` shape

## Notes Before Execution

- The CSV uses `;` as separator, so `pd.read_csv(..., sep=';')` is required.
- The first implementation deliberately uses template-based explanation generation instead of a real API call.
- This plan is scoped to the homepage frontend only, not full multi-page system delivery.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-16-dss-frontend-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
