from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@500;700;800&display=swap');

            :root {
                --bg-start: #f7fbf8;
                --bg-mid: #edf8f6;
                --bg-end: #f9f3ea;
                --panel: rgba(255, 255, 255, 0.86);
                --panel-strong: rgba(255, 255, 255, 0.96);
                --panel-soft: rgba(16, 185, 129, 0.08);
                --line-soft: rgba(38, 84, 92, 0.16);
                --line-bright: rgba(20, 184, 166, 0.34);
                --text-main: #14313a;
                --text-soft: #557078;
                --teal: #0f9f94;
                --aqua: #46c4b2;
                --leaf: #70b86d;
                --coral: #e76f63;
                --gold: #d69e2e;
                --ink: #102f39;
                --shadow: 0 22px 60px rgba(36, 95, 93, 0.14);
            }

            html, body, [class*="css"] {
                font-family: 'Manrope', sans-serif;
                color: var(--text-main);
            }

            .stApp {
                background:
                    linear-gradient(120deg, rgba(70, 196, 178, 0.12) 0%, transparent 36%),
                    linear-gradient(230deg, rgba(231, 111, 99, 0.11) 0%, transparent 34%),
                    linear-gradient(145deg, var(--bg-start) 0%, var(--bg-mid) 48%, var(--bg-end) 100%);
            }

            .stApp::before {
                content: "";
                position: fixed;
                inset: 0;
                pointer-events: none;
                background-image:
                    linear-gradient(rgba(20, 95, 103, 0.055) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(20, 95, 103, 0.055) 1px, transparent 1px);
                background-size: 72px 72px;
                opacity: 0.32;
            }

            [data-testid="stAppViewContainer"] > .main {
                padding-top: 1.15rem;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, #fffefa 0%, #edf8f6 100%);
                border-right: 1px solid var(--line-soft);
            }

            [data-testid="stSidebar"] .stRadio > div {
                background: rgba(255, 255, 255, 0.7);
                border: 1px solid var(--line-soft);
                padding: 0.48rem;
                border-radius: 8px;
            }

            [data-testid="stSidebar"] .stButton button {
                background: linear-gradient(135deg, #fdf4ef 0%, #ffe3dc 100%);
                color: #8f332c;
                border: 1px solid rgba(231, 111, 99, 0.32);
            }

            .app-shell {
                max-width: 1500px;
                margin: 0 auto;
            }

            .hero-shell {
                position: relative;
                overflow: hidden;
                background:
                    linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(238, 250, 247, 0.94) 52%, rgba(255, 246, 234, 0.98) 100%);
                border: 1px solid var(--line-soft);
                border-radius: 8px;
                padding: 2rem 2rem 1.8rem 2rem;
                box-shadow: var(--shadow);
                margin-bottom: 1.35rem;
            }

            .hero-shell::after {
                content: "";
                position: absolute;
                inset: 0;
                background:
                    linear-gradient(90deg, rgba(70, 196, 178, 0.12), transparent 36%),
                    linear-gradient(160deg, transparent 58%, rgba(214, 158, 46, 0.12));
                pointer-events: none;
            }

            .eyebrow {
                display: inline-block;
                padding: 0.45rem 0.92rem;
                border-radius: 999px;
                background: rgba(70, 196, 178, 0.14);
                border: 1px solid rgba(15, 159, 148, 0.26);
                color: #0b766f;
                font-size: 0.82rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 1rem;
            }

            .hero-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 3.5rem;
                line-height: 0.98;
                letter-spacing: 0;
                font-weight: 700;
                color: var(--ink);
                margin-bottom: 0.75rem;
                max-width: 12ch;
                text-wrap: balance;
            }

            .hero-subtitle {
                color: var(--text-soft);
                font-size: 1.05rem;
                line-height: 1.8;
                max-width: 54rem;
            }

            .feature-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.9rem;
                margin-top: 1.25rem;
            }

            .feature-tile {
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid var(--line-soft);
                border-radius: 8px;
                padding: 1rem 1.05rem;
                min-height: 116px;
                box-shadow: inset 4px 0 0 rgba(70, 196, 178, 0.28);
                transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
            }

            .feature-tile:hover {
                transform: translateY(-3px);
                box-shadow: inset 4px 0 0 rgba(70, 196, 178, 0.7), 0 12px 24px rgba(36, 95, 93, 0.08);
                background: rgba(255, 255, 255, 0.95);
            }

            .feature-kicker {
                font-size: 0.74rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: #0f8d84;
                font-weight: 800;
                margin-bottom: 0.45rem;
            }

            .feature-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1rem;
                color: var(--ink);
                margin-bottom: 0.25rem;
            }

            .feature-copy {
                font-size: 0.9rem;
                color: var(--text-soft);
                line-height: 1.55;
            }

            .glass-card {
                position: relative;
                overflow: hidden;
                background:
                    linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(248, 253, 250, 0.92) 100%);
                border: 1px solid var(--line-soft);
                border-radius: 8px;
                padding: 1.45rem;
                margin-bottom: 1rem;
                box-shadow: var(--shadow);
                backdrop-filter: blur(12px);
                transition: transform 0.25s ease, box-shadow 0.25s ease;
            }

            .glass-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 28px 65px rgba(36, 95, 93, 0.18);
            }

            .glass-card::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(70, 196, 178, 0.08), transparent 42%, rgba(231, 111, 99, 0.05));
                pointer-events: none;
            }

            .section-label {
                text-transform: uppercase;
                letter-spacing: 0.11em;
                color: #0f8d84;
                font-size: 0.74rem;
                font-weight: 800;
                margin-bottom: 0.45rem;
            }

            .card-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.2rem;
                color: var(--ink);
                margin-bottom: 0.35rem;
            }

            .card-copy {
                color: var(--text-soft);
                line-height: 1.65;
                font-size: 0.95rem;
            }

            .metric-ribbon {
                background: linear-gradient(135deg, rgba(70, 196, 178, 0.13), rgba(112, 184, 109, 0.09), rgba(214, 158, 46, 0.08));
                border: 1px solid var(--line-soft);
                border-radius: 8px;
                padding: 0.8rem;
                margin-bottom: 1rem;
            }

            .status-board {
                display: flex;
                flex-wrap: wrap;
                gap: 0.7rem;
                margin-bottom: 0.9rem;
            }

            .status-pill {
                display: inline-flex;
                align-items: center;
                padding: 0.62rem 0.95rem;
                border-radius: 999px;
                border: 1px solid rgba(38, 84, 92, 0.16);
                background: rgba(255, 255, 255, 0.72);
                color: var(--ink);
                font-size: 0.86rem;
                font-weight: 800;
                letter-spacing: 0;
            }

            .status-pill.detected {
                background: linear-gradient(135deg, rgba(255, 235, 231, 0.95), rgba(255, 246, 218, 0.95));
                border-color: rgba(231, 111, 99, 0.34);
                color: #9b3d35;
            }

            .status-pill.clear {
                background: linear-gradient(135deg, rgba(226, 250, 240, 0.95), rgba(226, 248, 245, 0.95));
                border-color: rgba(15, 159, 148, 0.32);
                color: #0b766f;
            }

            .status-pill.neutral {
                background: rgba(255, 255, 255, 0.68);
            }

            .insight-strip {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.75rem;
                margin-top: 0.9rem;
            }

            .insight-strip > div {
                padding: 0.95rem 1rem;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.74);
                border: 1px solid var(--line-soft);
            }

            .insight-strip span {
                display: block;
                color: var(--text-soft);
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.09em;
                margin-bottom: 0.35rem;
            }

            .insight-strip strong {
                color: var(--ink);
                font-size: 0.97rem;
                line-height: 1.45;
            }

            [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid rgba(38, 84, 92, 0.14);
                border-radius: 8px;
                padding: 1rem 1rem 0.9rem 1rem;
                box-shadow: inset 3px 0 0 rgba(112, 184, 109, 0.24);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            [data-testid="stMetric"]:hover {
                transform: translateY(-2px);
                box-shadow: inset 3px 0 0 rgba(112, 184, 109, 0.5), 0 8px 16px rgba(36, 95, 93, 0.1);
            }

            [data-testid="stMetricLabel"] {
                color: #557078;
                font-weight: 700;
            }

            [data-testid="stMetricValue"] {
                font-family: 'Space Grotesk', sans-serif;
                color: var(--ink);
            }

            .stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {
                border-radius: 8px;
                min-height: 3rem;
                border: 1px solid rgba(15, 159, 148, 0.26);
                background: linear-gradient(135deg, #0f9f94 0%, #46c4b2 58%, #70b86d 100%);
                color: white;
                font-weight: 800;
                letter-spacing: 0;
                box-shadow: 0 16px 32px rgba(15, 159, 148, 0.22);
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            }

            .stButton button:hover, .stDownloadButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
                transform: translateY(-1px);
                box-shadow: 0 18px 34px rgba(15, 159, 148, 0.28);
                border-color: rgba(15, 159, 148, 0.48);
            }

            .stTextInput input, .stNumberInput input, .stFileUploader, .stSelectbox > div > div {
                border-radius: 8px !important;
                background: rgba(255, 255, 255, 0.86) !important;
                border: 1px solid rgba(38, 84, 92, 0.18) !important;
                color: var(--ink) !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid var(--line-soft);
                padding: 0.35rem;
                border-radius: 8px;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 6px;
                color: var(--text-soft);
                font-weight: 800;
                min-height: 44px;
            }

            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, rgba(70, 196, 178, 0.2), rgba(112, 184, 109, 0.18));
                color: var(--ink) !important;
            }

            .history-shell {
                background: rgba(255, 255, 255, 0.84);
                border: 1px solid var(--line-soft);
                border-radius: 8px;
                padding: 1.1rem;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            .history-shell:hover {
                box-shadow: 0 12px 30px rgba(36, 95, 93, 0.12);
                transform: translateY(-1px);
            }

            .empty-panel {
                text-align: center;
                padding: 2rem 1rem;
                border-radius: 8px;
                border: 1px dashed rgba(38, 84, 92, 0.26);
                background: rgba(255, 255, 255, 0.68);
                color: var(--text-soft);
            }

            .sidebar-profile {
                padding: 1rem 1rem 0.95rem 1rem;
                border-radius: 8px;
                border: 1px solid var(--line-soft);
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(237, 248, 246, 0.9));
                margin-bottom: 1rem;
            }

            .sidebar-profile strong {
                display: block;
                font-size: 1rem;
                color: var(--ink);
                margin-bottom: 0.25rem;
            }

            .sidebar-profile span {
                color: var(--text-soft);
                font-size: 0.9rem;
            }

            .db-badge {
                margin: 0.85rem 0 1rem 0;
                padding: 0.85rem 1rem;
                border-radius: 8px;
                border: 1px solid rgba(15, 159, 148, 0.2);
                background: linear-gradient(135deg, rgba(70, 196, 178, 0.12), rgba(112, 184, 109, 0.08));
                color: var(--text-soft);
            }

            .db-badge strong {
                color: var(--ink);
            }

            /* --- Force Text Visibility Safeguards --- */
            /* If the user's browser is in dark mode, Streamlit defaults text to white.
               Since our background is light glassmorphism, we must force text to be dark. */
            label p,
            .stRadio label p,
            .stRadio div[data-baseweb="radio"] div,
            .stTextInput label p,
            .stNumberInput label p,
            .stFileUploader label p,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] div[data-baseweb="radio"] div,
            .stMarkdown p {
                color: var(--ink) !important;
            }
            
            /* Except for buttons which are already styled with white text */
            .stButton button p, .stDownloadButton button p, [data-testid="stFormSubmitButton"] button p {
                color: white !important;
            }

            @media (max-width: 900px) {
                .hero-title {
                    font-size: 2.45rem;
                    max-width: none;
                }

                .feature-grid {
                    grid-template-columns: 1fr;
                }

                .insight-strip {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def start_shell() -> None:
    st.markdown("<div class='app-shell'>", unsafe_allow_html=True)


def end_shell() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def hero_section(eyebrow: str, title: str, subtitle: str, features: list[dict[str, str]]) -> None:
    feature_markup = "".join(
        f"""
        <div class='feature-tile'>
            <div class='feature-kicker'>{feature["kicker"]}</div>
            <div class='feature-title'>{feature["title"]}</div>
            <div class='feature-copy'>{feature["copy"]}</div>
        </div>
        """
        for feature in features
    )

    st.markdown(
        f"""
        <div class='hero-shell'>
            <div class='eyebrow'>{eyebrow}</div>
            <div class='hero-title'>{title}</div>
            <div class='hero-subtitle'>{subtitle}</div>
            <div class='feature-grid'>{feature_markup}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def glass_intro(label: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class='glass-card'>
            <div class='section-label'>{label}</div>
            <div class='card-title'>{title}</div>
            <div class='card-copy'>{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_profile(doctor_name: str) -> None:
    st.markdown(
        f"""
        <div class='sidebar-profile'>
            <strong>Dr. {doctor_name}</strong>
            <span>NeuroScan AI review console</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class='empty-panel'>
            <div class='card-title'>{title}</div>
            <div class='card-copy'>{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
