"""
Custom CSS Injector & Plotly Command Center Theme for Streamlit UI.
"""

import streamlit as st
import plotly.graph_objects as go


def inject_custom_css():
    """Injects high-tech Command Center dark styling into Streamlit."""
    css = """
    <style>
    /* Main App Background & Font */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Top Header Bar */
    header[data-testid="stHeader"] {
        background: rgba(11, 14, 20, 0.8) !important;
        backdrop-filter: blur(8px);
    }

    /* Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #131722;
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid #1E293B;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 500;
        padding: 0 16px;
        border: none !important;
        background-color: transparent;
        transition: all 0.2s ease-in-out;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC;
        background-color: #1E293B;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    /* Metric Cards Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #38BDF8 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Container Card Borders */
    [data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {
        border-color: #1E293B !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }

    /* Buttons Styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #334155;
        background-color: #1E293B;
        color: #F8FAFC;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #38BDF8;
        background-color: #2563EB;
        color: #FFFFFF;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    /* Custom KPI HTML Card Class */
    .kpi-card {
        background: #131722;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #38BDF8;
        margin-top: 4px;
    }
    .kpi-badge-green {
        color: #4ADE80;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .kpi-badge-red {
        color: #F87171;
        font-size: 0.8rem;
        font-weight: 600;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def apply_theme_to_plotly(fig):
    """Applies a dark 'Command Center' theme to any Plotly chart."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#131722",
        font=dict(family="Inter, sans-serif", color="#E2E8F0"),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor="rgba(19, 23, 34, 0.8)",
            bordercolor="#1E293B",
            borderwidth=1
        ),
        xaxis=dict(
            gridcolor="#1E293B",
            zerolinecolor="#1E293B",
            showline=True,
            linecolor="#334155"
        ),
        yaxis=dict(
            gridcolor="#1E293B",
            zerolinecolor="#1E293B",
            showline=True,
            linecolor="#334155"
        )
    )
    return fig


def render_kpi_card(title: str, value: str, subtext: str = "", status: str = "normal"):
    """Renders a custom HTML metric card."""
    badge_class = "kpi-badge-green" if status == "good" else "kpi-badge-red" if status == "bad" else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            {"<div class='" + badge_class + "'>" + subtext + "</div>" if subtext else ""}
        </div>
        """,
        unsafe_allow_html=True
    )