"""Shared styling for BizLens app - OCBC red + white theme."""
import streamlit as st

OCBC_RED = "#D7262E"
OCBC_RED_SOFT = "#FBECED"
OCBC_RED_LINE = "#F0C5C8"
OCBC_RED_2 = "#E86E73"
OCBC_RED_3 = "#F2B5B8"
MUTED = "#8A8A8A"
PANEL = "#FFFFFF"
BORDER = "#E6E4E0"
BG_SOFT = "#F8F6F3"


def inject_css():
    """Inject global CSS for the OCBC red/white BizLens theme."""
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        /* Hide default Streamlit chrome a bit */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* Section heading */
        .bz-sec-h {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 1.25rem 0 0.25rem;
            font-size: 1.15rem;
            font-weight: 600;
            color: #1A1A1A;
        }}
        .bz-sec-h::before {{
            content: "";
            width: 4px;
            height: 1.1em;
            border-radius: 2px;
            background: {OCBC_RED};
            display: inline-block;
        }}
        .bz-sec-note {{
            margin: 0 0 1rem;
            color: {MUTED};
            font-size: 0.85rem;
        }}

        /* Hero header */
        .bz-hero {{
            background: linear-gradient(135deg, {OCBC_RED_SOFT}, {PANEL} 70%);
            border: 1px solid {OCBC_RED_LINE};
            border-radius: 14px;
            padding: 2rem 2.25rem;
            margin-bottom: 1.5rem;
        }}
        .bz-eyebrow {{
            color: {OCBC_RED};
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .bz-title {{
            margin: 0.25rem 0 0.5rem;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
            color: #1A1A1A;
        }}
        .bz-sub {{
            margin: 0;
            color: #333;
            font-size: 1rem;
            line-height: 1.5;
            max-width: 42rem;
        }}

        /* Navigation card for homepage */
        .bz-nav-card {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-top: 4px solid {OCBC_RED};
            border-radius: 12px;
            padding: 1.5rem;
            min-height: 190px;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }}
        .bz-nav-card:hover {{
            box-shadow: 0 6px 20px rgba(215, 38, 46, 0.1);
            transform: translateY(-2px);
        }}
        .bz-nav-icon {{
            font-size: 1.75rem;
            line-height: 1;
        }}
        .bz-nav-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
            color: #1A1A1A;
        }}
        .bz-nav-desc {{
            font-size: 0.9rem;
            color: #4a4a4a;
            line-height: 1.5;
            margin: 0;
        }}
        .bz-nav-meta {{
            margin-top: auto;
            font-size: 0.8rem;
            color: {MUTED};
        }}

        /* KPI card */
        .bz-kpi {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-top: 3px solid {OCBC_RED};
            border-radius: 10px;
            padding: 1rem 1.25rem;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}
        .bz-kpi-label {{
            font-size: 0.78rem;
            color: {MUTED};
            font-weight: 500;
        }}
        .bz-kpi-big {{
            font-size: 1.8rem;
            font-weight: 700;
            line-height: 1.1;
            color: #1A1A1A;
            font-variant-numeric: tabular-nums;
        }}
        .bz-kpi-foot {{
            font-size: 0.78rem;
            color: {MUTED};
            margin-top: auto;
        }}
        .bz-kpi-up {{ color: #166534; font-weight: 600; }}
        .bz-kpi-down {{ color: {OCBC_RED}; font-weight: 600; }}

        /* Card */
        .bz-card {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 0.75rem;
        }}
        .bz-card-h {{
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
            color: #1A1A1A;
        }}
        .bz-card-note {{
            margin: 0.15rem 0 0.75rem;
            color: {MUTED};
            font-size: 0.78rem;
        }}

        /* Tier badge */
        .bz-tier {{
            display: inline-block;
            padding: 3px 11px;
            border-radius: 999px;
            background: {OCBC_RED};
            color: #fff;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }}
        .bz-tier.tier-2 {{ background: {OCBC_RED_2}; }}
        .bz-tier.tier-3 {{ background: {OCBC_RED_3}; color: #5a1619; }}
        .bz-tier.tier-4 {{ background: {BORDER}; color: #5a5a5a; }}

        /* Info box soft */
        .bz-info-soft {{
            background: {OCBC_RED_SOFT};
            border: 1px solid {OCBC_RED_LINE};
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
        }}

        /* Streamlit tweaks */
        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1.25rem;
        }}
        .stButton > button[kind="primary"] {{
            background: {OCBC_RED};
            border-color: {OCBC_RED};
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #B01E25;
            border-color: #B01E25;
        }}

        /* Table tweaks */
        [data-testid="stDataFrame"] {{
            border-radius: 8px;
            overflow: hidden;
        }}

        /* Progress bar in OCBC red */
        .stProgress > div > div > div > div {{
            background-color: {OCBC_RED} !important;
        }}

        /* Streamlit bordered container -> look like our .bz-card */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: {BORDER} !important;
            border-radius: 10px !important;
            background: {PANEL};
        }}
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            padding: 0.75rem 1rem;
        }}

        /* Big number used inside containers */
        .bz-big-num {{
            font-size: 1.75rem;
            font-weight: 700;
            line-height: 1.1;
            color: #1A1A1A;
            font-variant-numeric: tabular-nums;
            margin: 0;
        }}
        .bz-big-num.red {{ color: {OCBC_RED}; }}
        .bz-sub-cap {{
            font-size: 0.8rem;
            color: {MUTED};
            margin: 0.1rem 0 0.5rem;
        }}
        .bz-chip {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: 999px;
            background: {OCBC_RED_SOFT};
            border: 1px solid {OCBC_RED_LINE};
            font-size: 0.78rem;
            margin-left: 0.5rem;
        }}
        .bz-chip b {{ color: {OCBC_RED}; }}

        /* Mini info box inside cards */
        .bz-mini {{
            background: {OCBC_RED_SOFT};
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            margin: 0.25rem 0;
        }}
        .bz-mini-v {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {OCBC_RED};
            line-height: 1.1;
        }}
        .bz-mini-l {{
            font-size: 0.72rem;
            color: {MUTED};
        }}

        /* Category card for 360 assessment on home */
        .bz-cat-head {{
            display: flex;
            flex-direction: column;
            gap: 0.1rem;
        }}
        .bz-cat-eyebrow {{
            font-size: 0.7rem;
            color: {MUTED};
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 600;
        }}
        .bz-cat-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #1A1A1A;
            margin: 0;
            line-height: 1.3;
        }}
        .bz-cat-total {{
            font-size: 2.1rem;
            font-weight: 700;
            line-height: 1;
            margin: 0.35rem 0 0.1rem;
        }}
        .bz-cat-cat {{
            font-size: 0.8rem;
            color: {MUTED};
        }}

        /* Insight box */
        .bz-insight {{
            background: {OCBC_RED_SOFT};
            border: 1px solid {OCBC_RED_LINE};
            border-radius: 10px;
            padding: 1rem 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }}
        .bz-insight-item {{
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }}
        .bz-insight-num {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {OCBC_RED};
            min-width: 3ch;
            line-height: 1.1;
        }}
        .bz-insight-text {{
            font-size: 0.85rem;
            line-height: 1.5;
            color: #333;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str = ""):
    """Render a section header with the OCBC red accent bar."""
    st.markdown(f'<h2 class="bz-sec-h">{title}</h2>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<p class="bz-sec-note">{note}</p>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, foot: str = "", trend: str = ""):
    """Render a KPI tile card."""
    trend_html = ""
    if trend == "up":
        foot = f'<span class="bz-kpi-up">▲</span> {foot}'
    elif trend == "down":
        foot = f'<span class="bz-kpi-down">▼</span> {foot}'
    st.markdown(
        f'<div class="bz-kpi">'
        f'<div class="bz-kpi-label">{label}</div>'
        f'<div class="bz-kpi-big">{value}</div>'
        f'<div class="bz-kpi-foot">{foot}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def tier_badge(tier_label: str) -> str:
    """Return HTML for a tier badge, color-coded by tier number if present."""
    tier_label = str(tier_label)
    cls = "tier-1"
    if "02" in tier_label or "Tier 2" in tier_label:
        cls = "tier-2"
    elif "03" in tier_label or "Tier 3" in tier_label:
        cls = "tier-3"
    elif "04" in tier_label or "Tier 4" in tier_label:
        cls = "tier-4"
    return f'<span class="bz-tier {cls}">{tier_label}</span>'
