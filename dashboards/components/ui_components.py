"""
HSEI Platform — UI Components
Light Industrial Theme
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

THEME = {
    "bg_primary":    "#f5f7fa",
    "bg_secondary":  "#ffffff",
    "bg_card":       "#ffffff",
    "border":        "#dde1e7",
    "text_primary":  "#1a1a2e",
    "text_secondary":"#4a4a6a",
    "text_muted":    "#9a9ab0",
    "green":  "#1e7e34",
    "amber":  "#b45309",
    "red":    "#c0392b",
    "blue":   "#1a6fa8",
    "purple": "#6f42c1",
    "orange": "#c05621",
    "plotly_bg":    "#ffffff",
    "plotly_paper": "#f5f7fa",
    "grid_color":   "#e8eaed",
    "axis_color":   "#9a9ab0",
}

SEVERITY_COLORS = {
    "Critical":   "#c0392b",
    "High":       "#b45309",
    "Medium":     "#1a6fa8",
    "Low":        "#1e7e34",
    "Negligible": "#6f42c1",
}

TIER_COLORS = {
    "Tier 1": "#c0392b",
    "Tier 2": "#e67e22",
    "Tier 3": "#f39c12",
    "Tier 4": "#27ae60",
}

GLOBAL_CSS = """
<style>
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #dde1e7;
    border-radius: 8px;
    padding: 14px 18px;
}
[data-testid="stMetric"] label {
    color: #4a4a6a !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    color: #1a1a2e !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}
.orpmi-card {
    background:#ffffff; border:1px solid #dde1e7;
    border-radius:8px; padding:16px 20px; margin-bottom:8px;
}
.section-header {
    font-size:13px; text-transform:uppercase; letter-spacing:0.12em;
    color:#4a4a6a; border-bottom:2px solid #dde1e7;
    padding-bottom:8px; margin-bottom:16px;
}
.badge-green  {background:#e6f4ea;color:#1e7e34;border:1px solid #a8d5b5;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;}
.badge-amber  {background:#fff8e1;color:#b45309;border:1px solid #fcd34d;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;}
.badge-red    {background:#fdecea;color:#c0392b;border:1px solid #f5b7b1;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;}
.badge-blue   {background:#e8f4fd;color:#1a6fa8;border:1px solid #aed6f1;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;}
.alert-critical {background:#fdecea;border:1px solid #c0392b;border-left:4px solid #c0392b;border-radius:6px;padding:12px 16px;margin:8px 0;color:#c0392b;}
.alert-warning  {background:#fff8e1;border:1px solid #b45309;border-left:4px solid #b45309;border-radius:6px;padding:12px 16px;margin:8px 0;color:#b45309;}
.alert-ok       {background:#e6f4ea;border:1px solid #1e7e34;border-left:4px solid #1e7e34;border-radius:6px;padding:12px 16px;margin:8px 0;color:#1e7e34;}
hr {border-color:#dde1e7;margin:20px 0;}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:20px;border-bottom:2px solid #dde1e7;padding-bottom:14px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:22px;">{icon}</span>
            <h1 style="color:#1a1a2e;font-size:22px;font-weight:700;margin:0;">{title}</h1>
        </div>
        {"<p style='color:#4a4a6a;font-size:13px;margin:4px 0 0 32px;'>"+subtitle+"</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def alert_banner(message: str, level: str = "critical"):
    icons = {"critical": "🔴", "warning": "🟡", "ok": "🟢"}
    st.markdown(f'<div class="alert-{level}">{icons.get(level,"")} {message}</div>',
                unsafe_allow_html=True)


def apply_layout(fig: go.Figure, title: str = "", height: int = 350) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(color=THEME["text_secondary"], size=13), x=0),
        paper_bgcolor=THEME["plotly_paper"],
        plot_bgcolor=THEME["plotly_bg"],
        font=dict(color=THEME["text_primary"], size=12),
        height=height,
        margin=dict(l=50, r=20, t=40 if title else 20, b=50),
        xaxis=dict(gridcolor=THEME["grid_color"], linecolor=THEME["axis_color"],
                   tickfont=dict(size=11, color=THEME["text_secondary"]), zeroline=False),
        yaxis=dict(gridcolor=THEME["grid_color"], linecolor=THEME["axis_color"],
                   tickfont=dict(size=11, color=THEME["text_secondary"]), zeroline=False),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor=THEME["border"],
                        font=dict(size=12, color=THEME["text_primary"])),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=THEME["border"],
                    borderwidth=1, font=dict(size=11)),
    )
    return fig
