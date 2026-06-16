import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

        :root {
            --page-bg: #f6f7f9;
            --card-bg: #ffffff;
            --line: #e5e7eb;
            --line-strong: #d1d5db;
            --title: #111827;
            --body: #374151;
            --muted: #6b7280;
            --blue: #2563eb;
            --blue-soft: #eff6ff;
            --green: #059669;
            --amber: #d97706;
            --shadow: 0 1px 2px rgba(17, 24, 39, 0.04);
        }

        html, body, .stApp {
            background: var(--page-bg);
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
            max-width: 1280px;
            padding-top: 1.1rem;
            padding-bottom: 2.5rem;
        }

        h1, h2, h3, h4 {
            color: var(--title);
        }

        .stMarkdown, .stCaption, .stApp p, .stApp label, .stApp li, .stApp span {
            color: var(--body);
        }

        .dashboard-hero {
            background: var(--card-bg);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: 1.25rem 1.35rem;
            margin-bottom: 0.9rem;
        }

        .dashboard-kicker, .section-kicker {
            color: var(--blue);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .dashboard-title {
            color: var(--title);
            font-size: 1.8rem;
            font-weight: 700;
            line-height: 1.25;
            margin-top: 0.35rem;
        }

        .dashboard-subtitle {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.72;
            max-width: 920px;
            margin-top: 0.45rem;
        }

        .report-section-title {
            color: var(--title);
            font-size: 1.05rem;
            font-weight: 700 !important;
            margin: 1.05rem 0 0.55rem;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.4rem;
            margin-bottom: 0.9rem;
        }

        button[data-baseweb="tab"] {
            height: auto;
            padding: 0.48rem 0.85rem;
            border-radius: 8px;
            background: #ffffff;
            color: var(--muted);
            border: 1px solid var(--line);
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: var(--blue-soft);
            color: var(--blue);
            border-color: var(--blue);
        }

        div[data-baseweb="tab-highlight"] {
            background-color: var(--blue) !important;
            height: 2px !important;
        }

        .metric-card,
        .report-card,
        .decision-card,
        .llm-card,
        .status-card,
        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"] {
            background: var(--card-bg);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: var(--shadow);
        }

        .metric-card {
            min-height: 148px;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
            gap: 0.42rem;
            margin-bottom: 0.75rem;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .metric-value {
            color: var(--title);
            font-size: 1.75rem;
            line-height: 1.1;
            font-weight: 700;
        }

        .metric-note {
            color: var(--muted);
            font-size: 0.8rem;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }

        .report-card,
        .decision-card,
        .llm-card,
        .status-card {
            padding: 1rem;
            margin-bottom: 0.75rem;
        }

        .report-card-title,
        .llm-card-title,
        .status-card-title {
            color: var(--title);
            font-size: 0.96rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .report-card-body,
        .llm-card-body,
        .status-card-body {
            color: var(--body);
            font-size: 0.9rem;
            line-height: 1.72;
        }

        .llm-card {
            min-height: 180px;
        }

        .decision-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin-bottom: 0.9rem;
        }

        .decision-card {
            min-height: 126px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 0.4rem;
        }

        .variable-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin-bottom: 0.85rem;
        }

        .variable-card {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.85rem;
            min-height: 142px;
        }

        .variable-card-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            margin-bottom: 0.5rem;
        }

        .variable-name {
            color: var(--title) !important;
            font-family: Consolas, "Microsoft YaHei", sans-serif;
            font-weight: 700;
            font-size: 0.92rem;
        }

        .variable-badge {
            border-radius: 999px;
            padding: 0.16rem 0.48rem;
            font-size: 0.72rem;
            font-weight: 700;
            white-space: nowrap;
        }

        .variable-badge.included {
            background: var(--blue-soft);
            color: var(--blue);
        }

        .variable-badge.excluded {
            background: #f3f4f6;
            color: var(--muted);
        }

        .variable-cn {
            color: var(--title);
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .variable-desc {
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.62;
        }

        .static-table-wrap {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: var(--shadow);
            overflow: visible;
            margin-bottom: 0.85rem;
        }

        .static-table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            font-size: 0.86rem;
        }

        .static-table th {
            color: var(--muted);
            background: #f9fafb;
            font-weight: 700;
            text-align: left;
            padding: 0.72rem;
            border-bottom: 1px solid var(--line);
        }

        .static-table td {
            color: var(--body);
            padding: 0.72rem;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
            white-space: normal;
            word-break: break-word;
        }

        .static-table tr:last-child td {
            border-bottom: none;
        }

        .status-ok {
            border-left: 4px solid var(--green);
        }

        .status-warn {
            border-left: 4px solid var(--amber);
        }

        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"] {
            padding: 0.45rem;
            margin-bottom: 0.85rem;
        }

        .stForm {
            background: var(--card-bg);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem 1rem 0.85rem;
            box-shadow: var(--shadow);
        }

        div[data-testid="stTextInput"],
        div[data-testid="stNumberInput"],
        div[data-testid="stSelectbox"] {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.65rem 0.7rem 0.5rem;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] > div {
            min-height: 42px;
            background: #ffffff;
            border-radius: 6px;
            border: 1px solid var(--line);
        }

        .stCode pre {
            background: #f9fafb !important;
            color: var(--body) !important;
            border: 1px solid var(--line) !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            white-space: pre-wrap !important;
            word-break: break-word !important;
        }

        div[data-testid="stAlertContainer"] > div {
            border-radius: 8px;
            border: 1px solid var(--line);
        }

        button[kind="secondary"],
        .stForm button,
        .stForm button[kind="secondary"],
        .stForm button[kind="primary"] {
            border-radius: 8px !important;
            min-height: 42px !important;
            font-weight: 700 !important;
        }

        @media (max-width: 1100px) {
            .decision-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .variable-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 900px) {
            .dashboard-title {
                font-size: 1.45rem;
            }

            .decision-grid {
                grid-template-columns: 1fr;
            }

            .variable-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
