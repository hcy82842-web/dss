import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

        :root {
            --page-bg: #eef3f8;
            --page-mesh-a: rgba(38, 99, 235, 0.10);
            --page-mesh-b: rgba(15, 118, 110, 0.08);
            --card-bg: rgba(255, 255, 255, 0.92);
            --card-bg-strong: #ffffff;
            --line: #d8e3ef;
            --line-strong: #c6d5e6;
            --title: #0f172a;
            --body: #334155;
            --muted: #6b7a90;
            --blue: #2563eb;
            --blue-soft: #eaf2ff;
            --blue-ink: #23457c;
            --green: #10b981;
            --amber: #f59e0b;
            --shell-shadow: 0 18px 48px rgba(15, 23, 42, 0.07);
            --card-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
        }

        html, body, .stApp {
            background:
                radial-gradient(circle at top left, var(--page-mesh-a), transparent 32%),
                radial-gradient(circle at top right, var(--page-mesh-b), transparent 28%),
                linear-gradient(180deg, #f5f8fc 0%, var(--page-bg) 100%);
            color: var(--body);
            font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
        }

        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
        }

        .block-container {
            max-width: 1360px;
            padding-top: 1rem;
            padding-bottom: 2.75rem;
        }

        h1, h2, h3, h4 {
            color: var(--title);
        }

        .stMarkdown,
        .stCaption,
        .stApp p,
        .stApp label,
        .stApp li,
        .stApp span {
            color: var(--body);
        }

        .st-key-hero_shell,
        .st-key-summary_shell,
        .st-key-workflow_shell,
        .st-key-filter_shell,
        .st-key-filter_summary_shell,
        .st-key-analytics_shell,
        .st-key-workspace_shell {
            margin-bottom: 1rem;
        }

        .st-key-filter_shell,
        .st-key-analytics_shell,
        .st-key-workspace_shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(248,251,255,0.92) 100%);
            border: 1px solid rgba(198, 213, 230, 0.92);
            border-radius: 28px;
            box-shadow: var(--shell-shadow);
            padding: 1.2rem 1.2rem 1.05rem;
            position: relative;
            overflow: hidden;
        }

        .st-key-filter_shell::before,
        .st-key-analytics_shell::before,
        .st-key-workspace_shell::before {
            content: "";
            position: absolute;
            inset: 0 auto auto 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, rgba(37,99,235,0.92) 0%, rgba(96,165,250,0.72) 48%, rgba(16,185,129,0.42) 100%);
        }

        .dashboard-hero {
            background:
                radial-gradient(circle at top right, rgba(37,99,235,0.16), transparent 28%),
                linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(245,249,255,0.96) 100%);
            border: 1px solid rgba(198, 213, 230, 0.92);
            border-radius: 30px;
            box-shadow: var(--shell-shadow);
            padding: 1.35rem 1.4rem 1.2rem;
            margin-bottom: 0.25rem;
            position: relative;
            overflow: hidden;
        }

        .dashboard-hero::after {
            content: "";
            position: absolute;
            right: -80px;
            top: -80px;
            width: 240px;
            height: 240px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(37,99,235,0.16), transparent 68%);
        }

        .dashboard-kicker,
        .panel-eyebrow,
        .section-banner-kicker,
        .toolbar-kicker {
            color: #6d88af;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .dashboard-title {
            color: var(--title);
            font-family: "IBM Plex Sans SC", "Noto Sans SC", sans-serif;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
            margin-top: 0.28rem;
            max-width: 760px;
        }

        .dashboard-subtitle {
            color: var(--muted);
            font-size: 0.96rem;
            line-height: 1.78;
            max-width: 880px;
            margin-top: 0.4rem;
        }

        .hero-inline-metrics {
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-top: 0.95rem;
            position: relative;
            z-index: 1;
        }

        .hero-inline-metrics span,
        .filter-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.42rem 0.78rem;
            background: rgba(255,255,255,0.74);
            border: 1px solid rgba(212, 225, 242, 0.98);
            border-radius: 999px;
            color: var(--blue-ink);
            font-size: 0.82rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.92);
        }

        .section-banner {
            margin-bottom: 0.9rem;
        }

        .section-banner-title {
            color: var(--title);
            font-family: "IBM Plex Sans SC", "Noto Sans SC", sans-serif;
            font-size: 1.28rem;
            font-weight: 700;
            margin-top: 0.22rem;
        }

        .section-banner-copy {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.7;
            max-width: 920px;
            margin-top: 0.28rem;
        }

        .summary-card,
        .decision-card,
        .decision-note,
        .candidate-strip,
        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"] {
            background: var(--card-bg-strong);
            border: 1px solid rgba(215, 227, 239, 0.96);
            border-radius: 24px;
            box-shadow: var(--card-shadow);
        }

        .summary-card {
            min-height: 160px;
            padding: 1.15rem 1.15rem 1rem;
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(249,251,255,0.94) 100%);
        }

        .summary-card::before {
            content: "";
            position: absolute;
            right: 16px;
            top: 16px;
            width: 44px;
            height: 44px;
            border-radius: 16px;
            background: rgba(37, 99, 235, 0.08);
        }

        .summary-card.accent-blue {
            border-color: rgba(191, 219, 254, 0.96);
        }

        .summary-card.accent-blue::after,
        .summary-card.accent-green::after,
        .summary-card.accent-amber::after {
            content: "";
            position: absolute;
            left: 18px;
            top: 16px;
            width: 14px;
            height: 14px;
            border-radius: 999px;
        }

        .summary-card.accent-blue::after {
            background: var(--blue);
            box-shadow: 0 0 0 6px rgba(37,99,235,0.10);
        }

        .summary-card.accent-green {
            border-color: rgba(167, 243, 208, 0.96);
        }

        .summary-card.accent-green::after {
            background: var(--green);
            box-shadow: 0 0 0 6px rgba(16,185,129,0.10);
        }

        .summary-card.accent-amber {
            border-color: rgba(253, 230, 138, 0.96);
        }

        .summary-card.accent-amber::after {
            background: var(--amber);
            box-shadow: 0 0 0 6px rgba(245,158,11,0.10);
        }

        .summary-card-topline {
            color: #6f84a6;
            font-size: 0.83rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            padding-left: 1.4rem;
        }

        .summary-card-value {
            color: var(--title);
            font-family: "IBM Plex Sans SC", "Noto Sans SC", sans-serif;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.1;
            margin: 1rem 0 0.38rem;
        }

        .summary-card-footnote {
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.62;
            max-width: 220px;
        }

        .summary-row-gap {
            height: 0.82rem;
        }

        .workflow-strip {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.7rem;
            margin: 0;
        }

        .workflow-step {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(214, 225, 238, 0.96);
            border-radius: 22px;
            padding: 0.95rem 0.95rem 0.82rem;
            box-shadow: var(--card-shadow);
        }

        .workflow-step.active {
            background: linear-gradient(135deg, #2f6ff0 0%, #2563eb 100%);
            border-color: #2563eb;
        }

        .workflow-step.active .workflow-label,
        .workflow-step.active .workflow-copy {
            color: #ffffff;
        }

        .workflow-label {
            color: var(--blue-ink);
            font-size: 0.9rem;
            font-weight: 700;
        }

        .workflow-copy {
            color: var(--muted);
            font-size: 0.78rem;
            line-height: 1.52;
            margin-top: 0.18rem;
        }

        .toolbar-card {
            background: transparent;
            border: none;
            box-shadow: none;
            padding: 0 0 0.85rem;
            margin-bottom: 0.15rem;
        }

        .toolbar-title,
        .panel-head-title,
        .decision-title {
            color: var(--title);
            font-family: "IBM Plex Sans SC", "Noto Sans SC", sans-serif;
            font-size: 1.12rem;
            font-weight: 700;
        }

        .toolbar-copy {
            color: var(--muted);
            margin-top: 0.2rem;
            font-size: 0.9rem;
            line-height: 1.7;
            max-width: 900px;
        }

        .filter-chip-row {
            display: flex;
            gap: 0.52rem;
            flex-wrap: wrap;
            margin: -0.1rem 0 0.35rem;
            padding: 0 0.2rem;
        }

        .filter-chip {
            background: rgba(255,255,255,0.84);
        }

        .filter-chip strong {
            color: #36557f;
            font-weight: 700;
        }

        .panel-head {
            margin: 0;
            padding: 1rem 1rem 0.3rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(249,251,255,0.96) 100%);
            border: 1px solid rgba(215, 227, 239, 0.96);
            border-bottom: none;
            border-radius: 24px 24px 0 0;
            box-shadow: var(--card-shadow);
        }

        .panel-eyebrow {
            display: inline-flex;
            align-items: center;
            padding: 0.18rem 0.5rem;
            background: #eef4ff;
            border: 1px solid #d6e5fb;
            border-radius: 999px;
            margin-bottom: 0.45rem;
        }

        .panel-head-title {
            margin-top: 0.05rem;
            font-size: 1rem;
            line-height: 1.35;
        }

        div[data-testid="stPlotlyChart"] {
            padding: 0.4rem 0.55rem 0.32rem;
            margin-bottom: 1rem;
            border-top: none;
            border-radius: 0 0 24px 24px;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(250,252,255,0.96) 100%);
        }

        .candidate-strip {
            padding: 0.88rem 0.92rem;
            margin-bottom: 0.62rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(249,251,255,0.96) 100%);
        }

        .candidate-strip.selected {
            border-color: rgba(147, 197, 253, 0.98);
            box-shadow: 0 0 0 2px rgba(37,99,235,0.08), var(--card-shadow);
        }

        .candidate-strip-title {
            color: var(--title);
            font-size: 1rem;
            font-weight: 700;
        }

        .candidate-strip-sub {
            color: var(--muted);
            font-size: 0.83rem;
            margin-top: 0.16rem;
        }

        .candidate-strip-tags {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.6rem;
            align-items: center;
        }

        .mini-tag,
        .detail-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 0.34rem 0.72rem;
            font-size: 0.79rem;
            font-weight: 700;
        }

        .mini-tag.priority-high {
            background: #e8f8f1;
            color: #0f766e;
        }

        .mini-tag.priority-mid {
            background: #fff5e1;
            color: #9a6700;
        }

        .mini-tag.priority-low {
            background: #eef2f7;
            color: #64748b;
        }

        .mini-tag.channel,
        .detail-chip {
            background: var(--blue-soft);
            color: #295dbe;
        }

        .mini-score {
            margin-left: auto;
            color: var(--blue);
            font-weight: 700;
        }

        .decision-card {
            padding: 1.05rem 1.12rem;
            margin-bottom: 0.8rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.99) 0%, rgba(249,251,255,0.96) 100%);
        }

        .detail-chip-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin: 0.6rem 0 0.78rem;
        }

        .detail-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.62rem 0;
            border-top: 1px solid #edf2f7;
        }

        .detail-row span {
            color: var(--muted);
        }

        .detail-row strong,
        .detail-stat strong {
            color: var(--title);
        }

        .detail-stat-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.72rem;
            margin: 0.96rem 0;
        }

        .detail-stat {
            border: 1px solid #e8eef6;
            border-radius: 18px;
            padding: 0.78rem 0.84rem;
            background: #fbfdff;
        }

        .detail-stat span {
            color: var(--muted);
            display: block;
            font-size: 0.8rem;
        }

        .detail-stat strong {
            display: block;
            margin-top: 0.18rem;
            font-size: 1rem;
        }

        .decision-action {
            background: linear-gradient(90deg, rgba(37,99,235,0.08), rgba(255,255,255,0.55));
            border: 1px solid #d9e8ff;
            border-radius: 18px;
            padding: 0.9rem 0.95rem;
            color: var(--title);
            font-weight: 600;
            line-height: 1.72;
        }

        .decision-note {
            padding: 0.92rem 1rem;
            margin-bottom: 0.8rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(249,251,255,0.96) 100%);
        }

        .decision-note.info {
            border-color: rgba(191, 219, 254, 0.98);
        }

        .decision-note.warn {
            border-color: rgba(253, 230, 138, 0.98);
        }

        .decision-note-title {
            color: var(--title);
            font-size: 0.96rem;
            font-weight: 700;
            margin-bottom: 0.26rem;
        }

        .decision-note-body {
            color: var(--body);
            line-height: 1.76;
        }

        .stForm {
            background: linear-gradient(180deg, rgba(255,255,255,0.72) 0%, rgba(245,249,255,0.86) 100%);
            border: 1px solid rgba(207, 223, 242, 0.92);
            border-radius: 26px;
            padding: 1rem 1rem 0.8rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
        }

        div[data-testid="stTextInput"],
        div[data-testid="stNumberInput"],
        div[data-testid="stSelectbox"],
        div[data-testid="stMultiSelect"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(249,251,255,0.92) 100%);
            border: 1px solid rgba(215, 227, 239, 0.96);
            border-radius: 22px;
            box-shadow: var(--card-shadow);
            padding: 0.8rem 0.82rem 0.64rem;
        }

        .stMultiSelect label,
        .stSelectbox label,
        .stTextInput label,
        .stNumberInput label {
            color: #36557f !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.4rem;
            letter-spacing: 0.02em;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            min-height: 48px !important;
            background: #f8fbff !important;
            color: #23457c !important;
            border-radius: 16px !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            -webkit-appearance: none !important;
            appearance: none !important;
        }

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stNumberInput"] input::placeholder {
            color: #8ea2c2 !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="base-input"],
        div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="base-input"] > div,
        div[data-testid="stNumberInput"] div[data-baseweb="base-input"] > div {
            min-height: 48px !important;
            background: #f8fbff !important;
            border-radius: 16px !important;
            border: 1px solid rgba(212, 224, 239, 0.98) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.92) !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within > div,
        div[data-testid="stNumberInput"] div[data-baseweb="base-input"]:focus-within > div,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stTextInput"] input:focus-visible,
        div[data-testid="stNumberInput"] input:focus-visible {
            outline: none !important;
            box-shadow: none !important;
            border-color: #bfd7fb !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] > div {
            min-height: 48px;
            background: #f8fbff;
            border-radius: 16px;
            border: 1px solid rgba(212, 224, 239, 0.98);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
        }

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {
            background: #eaf2ff;
            border-radius: 999px;
        }

        div[data-testid="stMultiSelect"] input::placeholder,
        div[data-testid="stSelectbox"] input::placeholder {
            color: #8ea2c2;
        }

        div[data-baseweb="popover"] > div {
            background: rgba(255, 255, 255, 0.98) !important;
            border: 1px solid rgba(215, 227, 239, 0.96) !important;
            border-radius: 18px !important;
            box-shadow: var(--card-shadow) !important;
        }

        div[role="listbox"] {
            background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%) !important;
            border-radius: 18px !important;
            padding: 0.35rem !important;
        }

        div[role="listbox"] ul,
        div[role="listbox"] li,
        div[role="listbox"] li > div,
        div[role="listbox"] li > div > div,
        div[role="listbox"] li > div > div > div {
            background: transparent !important;
        }

        div[role="option"],
        li[role="option"] {
            color: #31527f !important;
            background: transparent !important;
            border-radius: 12px !important;
            margin: 0.1rem 0 !important;
        }

        div[role="option"][aria-selected="true"],
        li[role="option"][aria-selected="true"] {
            background: linear-gradient(90deg, rgba(37,99,235,0.14), rgba(96,165,250,0.06)) !important;
            color: #1f4070 !important;
        }

        div[role="option"]:hover,
        li[role="option"]:hover {
            background: #edf4ff !important;
            color: #1f4070 !important;
        }

        div[data-baseweb="popover"] ul {
            background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%) !important;
        }

        div[data-baseweb="popover"] li {
            background: #ffffff !important;
            border-radius: 14px !important;
            margin: 0.12rem 0 !important;
        }

        div[data-baseweb="popover"] li:hover {
            background: #edf4ff !important;
        }

        div[data-baseweb="popover"] li *,
        div[data-baseweb="popover"] [id^="bui"] *,
        div[data-baseweb="popover"] [id*="__anchor"] * {
            color: #31527f !important;
            background: transparent !important;
            opacity: 1 !important;
        }

        div[data-baseweb="popover"] li[aria-selected="true"],
        div[data-baseweb="popover"] li[aria-selected="true"] *,
        div[data-baseweb="popover"] [aria-selected="true"] * {
            background: linear-gradient(90deg, rgba(37,99,235,0.14), rgba(96,165,250,0.06)) !important;
            color: #1f4070 !important;
        }

        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] span,
        div[data-baseweb="popover"] button {
            color: var(--body) !important;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.55rem;
            margin-bottom: 0.75rem;
        }

        button[data-baseweb="tab"] {
            height: auto;
            padding: 0.5rem 0.95rem;
            border-radius: 999px;
            background: #edf3fb;
            color: #49668f;
            border: 1px solid #d8e3ef;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #2f6ff0 0%, #2563eb 100%);
            color: #ffffff;
            border-color: #2563eb;
        }

        div[data-testid="stDataFrame"] {
            padding: 0.42rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(249,251,255,0.96) 100%);
        }

        .stCode,
        .stCodeBlock,
        .stCode pre,
        .stCode code {
            background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%) !important;
            color: #31527f !important;
            border: 1px solid rgba(191, 219, 254, 0.96) !important;
            border-radius: 18px !important;
        }

        .stCode pre {
            padding: 0.95rem 1rem !important;
            font-size: 0.92rem !important;
            line-height: 1.6 !important;
            white-space: pre-wrap !important;
            word-break: break-word !important;
            box-shadow: var(--card-shadow);
        }

        section[data-testid="stFileUploader"] > div {
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,251,255,0.94) 100%);
            border: 1px solid rgba(215, 227, 239, 0.96);
            border-radius: 22px;
            padding: 0.8rem 0.82rem 0.64rem;
            box-shadow: var(--card-shadow);
        }

        section[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(180deg, #f8fbff 0%, #edf4ff 100%) !important;
            border: 1.5px dashed #bfd7fb !important;
            border-radius: 16px !important;
            min-height: 118px;
        }

        section[data-testid="stFileUploader"] small,
        section[data-testid="stFileUploader"] span,
        section[data-testid="stFileUploader"] label,
        section[data-testid="stFileUploader"] p {
            color: #4a6388 !important;
        }

        section[data-testid="stFileUploader"] button {
            background: #ffffff !important;
            color: #23457c !important;
            border: 1px solid #cfe0fb !important;
            border-radius: 999px !important;
        }

        .stForm button,
        .stForm button[kind="secondary"],
        .stForm button[kind="primary"] {
            background: linear-gradient(135deg, #eef5ff 0%, #f8fbff 100%) !important;
            color: #23457c !important;
            border: 1px solid #cfe0fb !important;
            border-radius: 16px !important;
            min-height: 48px !important;
            font-weight: 700 !important;
            box-shadow: var(--card-shadow);
        }

        div[data-testid="stDataEditor"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,251,255,0.94) 100%);
            border: 1px solid rgba(215, 227, 239, 0.96);
            border-radius: 24px;
            box-shadow: var(--card-shadow);
            padding: 0.7rem;
        }

        div[data-testid="stDataEditor"] [data-testid="stDataFrameResizable"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid #dbe5f0;
        }

        div[data-testid="stAlertContainer"] > div {
            border-radius: 20px;
            border: 1px solid rgba(215, 227, 239, 0.96);
        }

        button[kind="secondary"] {
            border-radius: 14px;
        }

        @media (max-width: 1100px) {
            .workflow-strip {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 900px) {
            .dashboard-title {
                font-size: 1.56rem;
            }

            .detail-stat-grid {
                grid-template-columns: 1fr;
            }

            .workflow-strip {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
