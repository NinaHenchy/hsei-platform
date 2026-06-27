"""HSEI Dashboard — Deep Amber Slate Industrial Theme"""
import streamlit as st
import plotly.graph_objects as go

THEME = {
    "bg_primary":     "#141210",
    "bg_secondary":   "#1c1810",
    "bg_card":        "#1c1810",
    "bg_elevated":    "#252018",
    "border":         "#3a3020",
    "border_light":   "#4a4030",
    "text_primary":   "#f5f0e8",
    "text_secondary": "#9a8a6a",
    "text_muted":     "#5a5040",
    "green":   "#4ade80",
    "amber":   "#fbbf24",
    "red":     "#f87171",
    "orange":  "#e07b39",
    "gold":    "#d4a017",
    "blue":    "#818cf8",
    "cyan":    "#48cae4",
    "plotly_bg":    "#1c1810",
    "plotly_paper": "#141210",
    "grid_color":   "#3a3020",
    "axis_color":   "#5a5040",
}

SEVERITY_COLORS = {
    "Critical":   "#f87171",
    "High":       "#e07b39",
    "Medium":     "#fbbf24",
    "Low":        "#4ade80",
    "Negligible": "#818cf8",
}

TIER_COLORS = {
    "Tier 1": "#f87171",
    "Tier 2": "#fbbf24",
    "Tier 3": "#4ade80",
    "Tier 4": "#818cf8",
}

GLOBAL_CSS = """
<style>
.stApp{background-color:#141210}
[data-testid="stSidebar"]{background-color:#0e0c08!important;border-right:1px solid #3a3020}
[data-testid="stSidebar"] *{color:#c8b898!important}
[data-testid="stSidebar"] .stRadio label{color:#c8b898!important;font-size:13px!important}
[data-testid="stSidebar"] .stRadio label:hover{color:#d4a017!important}
[data-testid="stMetric"]{background:linear-gradient(135deg,#1c1810,#252018);border:1px solid #3a3020;border-left:3px solid #d4a017;border-radius:8px;padding:14px 18px}
[data-testid="stMetric"] label{color:#9a8a6a!important;font-size:11px!important;text-transform:uppercase;letter-spacing:.08em}
[data-testid="stMetricValue"]{color:#f5f0e8!important;font-size:24px!important;font-weight:700!important}
.stTabs [data-baseweb="tab"]{background-color:#1c1810;border:1px solid #3a3020;color:#9a8a6a;border-radius:6px 6px 0 0}
.stTabs [aria-selected="true"]{background-color:#252018!important;color:#d4a017!important;border-bottom:2px solid #d4a017!important}
[data-testid="stForm"]{background-color:#1c1810;border:1px solid #3a3020;border-radius:10px;padding:20px}
.stButton>button{background:linear-gradient(135deg,#d4a017,#e07b39);color:#141210;border:none;font-weight:700;border-radius:6px}
.stButton>button:hover{background:linear-gradient(135deg,#c49010,#d06b29);color:#fff}
hr{border-color:#3a3020}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#141210}
::-webkit-scrollbar-thumb{background:#3a3020;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#d4a017}
</style>
"""

def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1c1810,#252018);border:1px solid #3a3020;
                border-left:4px solid #d4a017;border-radius:10px;padding:18px 24px;margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:28px;">{icon}</span>
            <div>
                <h1 style="color:#f5f0e8;font-size:22px;font-weight:800;margin:0;">{title}</h1>
                {"<p style='color:#9a8a6a;font-size:13px;margin:4px 0 0;'>"+subtitle+"</p>" if subtitle else ""}
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

def section_header(text: str):
    st.markdown(f"""
    <div style="font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#d4a017;
                border-bottom:1px solid #3a3020;padding-bottom:8px;margin-bottom:16px;
                margin-top:8px;font-weight:700;">{text}</div>""", unsafe_allow_html=True)

def alert_banner(message: str, level: str = "critical"):
    colors = {
        "critical": ("#f87171", "#1a0808"),
        "warning":  ("#fbbf24", "#1a1400"),
        "info":     ("#d4a017", "#1a1208"),
        "success":  ("#4ade80", "#081a10"),
    }
    color, bg = colors.get(level, colors["info"])
    icons = {"critical": "🔴", "warning": "🟡", "info": "🟠", "success": "🟢"}
    st.markdown(f"""
    <div style="background:{bg};border:1px solid {color};border-left:4px solid {color};
                border-radius:8px;padding:12px 18px;margin:8px 0;color:{color};
                font-size:13px;font-weight:600;">{icons.get(level,"")} {message}</div>
    """, unsafe_allow_html=True)

def apply_layout(fig: go.Figure, title: str = "", height: int = 340) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(color="#9a8a6a", size=12), x=0),
        paper_bgcolor="#141210",
        plot_bgcolor="#1c1810",
        font=dict(color="#f5f0e8", size=12),
        height=height,
        margin=dict(l=50, r=20, t=40 if title else 20, b=50),
        xaxis=dict(gridcolor="#3a3020", linecolor="#3a3020",
                   tickfont=dict(size=11, color="#5a5040"), zeroline=False),
        yaxis=dict(gridcolor="#3a3020", linecolor="#3a3020",
                   tickfont=dict(size=11, color="#5a5040"), zeroline=False),
        hoverlabel=dict(bgcolor="#252018", bordercolor="#3a3020",
                        font=dict(size=12, color="#f5f0e8")),
        legend=dict(bgcolor="rgba(28,24,16,0.9)", bordercolor="#3a3020",
                    borderwidth=1, font=dict(size=11, color="#f5f0e8")),
    )
    return fig