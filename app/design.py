from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@500;700;800&display=swap');

            :root {
                --bg-start: #02050c;
                --bg-mid: #07111d;
                --bg-end: #0c1726;
                --panel: rgba(8, 18, 32, 0.72);
                --panel-strong: rgba(10, 22, 38, 0.94);
                --panel-soft: rgba(255, 255, 255, 0.05);
                --line-soft: rgba(148, 163, 184, 0.12);
                --line-bright: rgba(125, 211, 252, 0.36);
                --text-main: #eef8ff;
                --text-soft: #9eb6ca;
                --cyan: #7dd3fc;
                --blue: #2563eb;
                --amber: #f59e0b;
                --rose: #f43f5e;
                --mint: #34d399;
                --shadow: 0 30px 110px rgba(2, 8, 23, 0.48);
            }

            html, body, [class*="css"] {
                font-family: 'Manrope', sans-serif;
                color: var(--text-main);
            }

            .stApp {
                background:
                    radial-gradient(circle at 0% 0%, rgba(125, 211, 252, 0.18), transparent 24%),
                    radial-gradient(circle at 100% 12%, rgba(245, 158, 11, 0.14), transparent 21%),
                    radial-gradient(circle at 82% 100%, rgba(244, 63, 94, 0.14), transparent 24%),
                    radial-gradient(circle at 48% 30%, rgba(37, 99, 235, 0.10), transparent 28%),
                    linear-gradient(145deg, var(--bg-start) 0%, var(--bg-mid) 45%, var(--bg-end) 100%);
            }

            .stApp::before {
                content: "";
                position: fixed;
                inset: 0;
                pointer-events: none;
                background-image:
                    linear-gradient(rgba(103, 232, 249, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(103, 232, 249, 0.03) 1px, transparent 1px);
                background-size: 84px 84px;
                mask-image: radial-gradient(circle at center, black 38%, transparent 85%);
                opacity: 0.45;
            }

            [data-testid="stAppViewContainer"] > .main {
                padding-top: 1.15rem;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(6, 15, 27, 0.98) 0%, rgba(8, 18, 32, 0.96) 100%);
                border-right: 1px solid var(--line-soft);
            }

            [data-testid="stSidebar"] .stRadio > div {
                background: rgba(15, 23, 42, 0.45);
                border: 1px solid var(--line-soft);
                padding: 0.48rem;
                border-radius: 18px;
            }

            [data-testid="stSidebar"] .stButton button {
                background: linear-gradient(135deg, #0f172a 0%, #16283f 100%);
                color: #f8fafc;
                border: 1px solid rgba(251, 113, 133, 0.24);
            }

            .app-shell {
                max-width: 1500px;
                margin: 0 auto;
            }

            .hero-shell {
                position: relative;
                overflow: hidden;
                background:
                    linear-gradient(135deg, rgba(8, 19, 34, 0.95) 0%, rgba(10, 28, 49, 0.84) 48%, rgba(18, 38, 67, 0.98) 100%);
                border: 1px solid var(--line-soft);
                border-radius: 34px;
                padding: 2rem 2rem 1.8rem 2rem;
                box-shadow: var(--shadow);
                margin-bottom: 1.35rem;
            }

            .hero-shell::after {
                content: "";
                position: absolute;
                inset: 0;
                background:
                    radial-gradient(circle at top right, rgba(125, 211, 252, 0.18), transparent 28%),
                    radial-gradient(circle at bottom left, rgba(37, 99, 235, 0.14), transparent 25%),
                    linear-gradient(135deg, rgba(255, 255, 255, 0.04), transparent 42%);
                pointer-events: none;
            }

            .eyebrow {
                display: inline-block;
                padding: 0.45rem 0.92rem;
                border-radius: 999px;
                background: rgba(103, 232, 249, 0.1);
                border: 1px solid rgba(103, 232, 249, 0.25);
                color: #bff6ff;
                font-size: 0.82rem;
                font-weight: 800;
                letter-spacing: 0.09em;
                text-transform: uppercase;
                margin-bottom: 1rem;
            }

            .hero-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 3.5rem;
                line-height: 0.98;
                letter-spacing: -0.05em;
                font-weight: 700;
                color: #f8fbff;
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
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.018));
                border: 1px solid var(--line-soft);
                border-radius: 22px;
                padding: 1rem 1.05rem;
                min-height: 116px;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
            }

            .feature-kicker {
                font-size: 0.74rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                color: #89e0f3;
                font-weight: 800;
                margin-bottom: 0.45rem;
            }

            .feature-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1rem;
                color: #f8fbff;
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
                    linear-gradient(180deg, rgba(17, 30, 50, 0.8) 0%, rgba(8, 16, 28, 0.9) 100%);
                border: 1px solid var(--line-soft);
                border-radius: 28px;
                padding: 1.45rem;
                margin-bottom: 1rem;
                box-shadow: var(--shadow);
                backdrop-filter: blur(18px);
            }

            .glass-card::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(103, 232, 249, 0.08), transparent 36%, rgba(251, 191, 36, 0.05));
                pointer-events: none;
            }

            .section-label {
                text-transform: uppercase;
                letter-spacing: 0.15em;
                color: #8de8f9;
                font-size: 0.74rem;
                font-weight: 800;
                margin-bottom: 0.45rem;
            }

            .card-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.2rem;
                color: #f8fbff;
                margin-bottom: 0.35rem;
            }

            .card-copy {
                color: var(--text-soft);
                line-height: 1.65;
                font-size: 0.95rem;
            }

            .metric-ribbon {
                background: linear-gradient(135deg, rgba(125, 211, 252, 0.09), rgba(37, 99, 235, 0.08), rgba(245, 158, 11, 0.04));
                border: 1px solid var(--line-soft);
                border-radius: 24px;
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
                border: 1px solid rgba(148, 163, 184, 0.18);
                background: rgba(255, 255, 255, 0.04);
                color: #e2eefb;
                font-size: 0.86rem;
                font-weight: 800;
                letter-spacing: 0.01em;
            }

            .status-pill.detected {
                background: linear-gradient(135deg, rgba(244, 63, 94, 0.18), rgba(245, 158, 11, 0.14));
                border-color: rgba(244, 63, 94, 0.28);
            }

            .status-pill.clear {
                background: linear-gradient(135deg, rgba(52, 211, 153, 0.16), rgba(125, 211, 252, 0.12));
                border-color: rgba(52, 211, 153, 0.28);
            }

            .status-pill.neutral {
                background: rgba(255, 255, 255, 0.035);
            }

            .insight-strip {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.75rem;
                margin-top: 0.9rem;
            }

            .insight-strip > div {
                padding: 0.95rem 1rem;
                border-radius: 20px;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.02));
                border: 1px solid var(--line-soft);
            }

            .insight-strip span {
                display: block;
                color: var(--text-soft);
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 0.35rem;
            }

            .insight-strip strong {
                color: #f8fbff;
                font-size: 0.97rem;
                line-height: 1.45;
            }

            [data-testid="stMetric"] {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.038), rgba(255, 255, 255, 0.018));
                border: 1px solid rgba(148, 163, 184, 0.12);
                border-radius: 22px;
                padding: 1rem 1rem 0.9rem 1rem;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.025);
            }

            [data-testid="stMetricLabel"] {
                color: #9eb6ca;
                font-weight: 700;
            }

            [data-testid="stMetricValue"] {
                font-family: 'Space Grotesk', sans-serif;
                color: #f8fbff;
            }

            .stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {
                border-radius: 18px;
                min-height: 3rem;
                border: 1px solid rgba(125, 211, 252, 0.24);
                background: linear-gradient(135deg, #0284c7 0%, #2563eb 55%, #1d4ed8 100%);
                color: white;
                font-weight: 800;
                letter-spacing: 0.01em;
                box-shadow: 0 18px 40px rgba(37, 99, 235, 0.24);
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            }

            .stButton button:hover, .stDownloadButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
                transform: translateY(-1px);
                box-shadow: 0 20px 38px rgba(14, 165, 233, 0.26);
                border-color: rgba(103, 232, 249, 0.38);
            }

            .stTextInput input, .stNumberInput input, .stFileUploader, .stSelectbox > div > div {
                border-radius: 16px !important;
                background: rgba(255, 255, 255, 0.045) !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                color: #f8fafc !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--line-soft);
                padding: 0.35rem;
                border-radius: 18px;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 14px;
                color: var(--text-soft);
                font-weight: 800;
                min-height: 44px;
            }

            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(37, 99, 235, 0.2));
                color: #f8fbff !important;
            }

            .history-shell {
                background: linear-gradient(180deg, rgba(8, 18, 31, 0.84) 0%, rgba(7, 14, 24, 0.92) 100%);
                border: 1px solid var(--line-soft);
                border-radius: 28px;
                padding: 1.1rem;
            }

            .empty-panel {
                text-align: center;
                padding: 2rem 1rem;
                border-radius: 24px;
                border: 1px dashed rgba(148, 163, 184, 0.24);
                background: rgba(255, 255, 255, 0.025);
                color: var(--text-soft);
            }

            .sidebar-profile {
                padding: 1rem 1rem 0.95rem 1rem;
                border-radius: 22px;
                border: 1px solid var(--line-soft);
                background: linear-gradient(180deg, rgba(10, 24, 42, 0.92), rgba(7, 16, 28, 0.84));
                margin-bottom: 1rem;
            }

            .sidebar-profile strong {
                display: block;
                font-size: 1rem;
                color: #f8fbff;
                margin-bottom: 0.25rem;
            }

            .sidebar-profile span {
                color: var(--text-soft);
                font-size: 0.9rem;
            }

            .db-badge {
                margin: 0.85rem 0 1rem 0;
                padding: 0.85rem 1rem;
                border-radius: 18px;
                border: 1px solid rgba(125, 211, 252, 0.18);
                background: linear-gradient(135deg, rgba(125, 211, 252, 0.08), rgba(52, 211, 153, 0.06));
                color: var(--text-soft);
            }

            .db-badge strong {
                color: #f8fbff;
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
