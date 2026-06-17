"""
HSEI Platform — Main Application Entry Point
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
for _p in [str(_root), "/app"]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

st.set_page_config(
    page_title="HSEI | HSE Incident Analytics Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

_db = Path("database/hsei_dev.db")
if not _db.exists():
    with st.spinner("First run — initialising HSE database (~30 seconds)..."):
        import subprocess
        subprocess.run([sys.executable, "scripts/setup_database.py"], check=True)
    st.rerun()

from dashboards.components.ui_components import inject_css
inject_css()

with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 8px 0;">
        <div style="font-size:16px;font-weight:700;color:#1a1a2e;">🛡️ HSEI Platform</div>
        <div style="font-size:11px;color:#4a4a6a;margin-top:3px;">
            HSE Incident Analytics & Process Safety Intelligence
        </div>
        <div style="font-size:10px;color:#9a9ab0;margin-top:2px;">
            Offshore Production Complex · OPC-Alpha
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#dde1e7;margin:6px 0 8px;">', unsafe_allow_html=True)

    page = st.radio(
        "nav",
        options=[
            "🛡️  HSE Executive Overview",
            "📋  Incident Register & Analysis",
            "⚗️  Process Safety (API RP 754)",
            "✅  Corrective Actions Tracker",
            "📡  Leading Indicators",
            "🔍  HSE Inspections & Audit",
            "📄  Permit to Work Analytics",
            "🎓  Training & Competency",
            "➕  HSE Data Entry",
        ],
        label_visibility="collapsed",
    )

    st.markdown('<hr style="border-color:#dde1e7;margin:10px 0 10px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:10px;color:#9a9ab0;line-height:2.1;">
        <div>📅 Data Period: Jan – Dec 2024</div>
        <div>📐 Standard: API RP 754 · ISO 45001</div>
        <div>🏛️ Regulator: NUPRC · NOSDRA</div>
        <div style="margin-top:6px;color:#1e7e34;font-weight:600;">● Platform Online</div>
    </div>
    """, unsafe_allow_html=True)


if "HSE Executive Overview" in page:
    from dashboards.pages.p1_hse_overview import render_hse_overview
    render_hse_overview()
elif "Incident Register" in page:
    from dashboards.pages.p2_to_p8 import render_incident_analysis
    render_incident_analysis()
elif "Process Safety" in page:
    from dashboards.pages.p2_to_p8 import render_process_safety
    render_process_safety()
elif "Corrective Actions" in page:
    from dashboards.pages.p2_to_p8 import render_corrective_actions
    render_corrective_actions()
elif "Leading Indicators" in page:
    from dashboards.pages.p2_to_p8 import render_leading_indicators
    render_leading_indicators()
elif "Inspections" in page:
    from dashboards.pages.p2_to_p8 import render_inspections
    render_inspections()
elif "Permit to Work" in page:
    from dashboards.pages.p2_to_p8 import render_ptw_analytics
    render_ptw_analytics()
elif "Training" in page:
    from dashboards.pages.p2_to_p8 import render_training_competency
    render_training_competency()
elif "Data Entry" in page:
    from dashboards.pages.p_data_entry import render_hsei_data_entry
    render_hsei_data_entry()
