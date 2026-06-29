"""
HSEI Platform — HSE Incident Analytics & Process Safety Intelligence
Inline setup — no subprocess — works on Streamlit Cloud, Docker, Local
Deep Amber Slate Theme
"""

import sys
import os
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

_db = _root / "database" / "hsei_dev.db"

def _setup():
    os.makedirs(str(_root / "database"), exist_ok=True)
    os.makedirs(str(_root / "logs"), exist_ok=True)
    os.makedirs(str(_root / "data" / "raw"), exist_ok=True)
    os.makedirs(str(_root / "data" / "processed"), exist_ok=True)
    from database.db_connection import initialize_database
    initialize_database()
    from etl.run_etl import run_etl_pipeline
    run_etl_pipeline()

def _db_has_data():
    try:
        from sqlalchemy import text
        from database.db_connection import get_engine
        eng = get_engine()
        with eng.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM incidents")).scalar()
        return count > 0
    except Exception:
        return False

if not _db.exists():
    with st.spinner("First run — initialising HSEI database (~60 seconds)..."):
        try:
            _setup()
        except Exception as e:
            st.error(f"Database setup failed: {e}")
            st.exception(e)
            st.stop()
    st.rerun()

if not _db_has_data():
    with st.spinner("Loading data into database (~60 seconds)..."):
        try:
            _setup()
        except Exception as e:
            st.error(f"Data load failed: {e}")
            st.exception(e)
            st.stop()
    st.rerun()

from dashboards.components.ui_components import inject_css
inject_css()

with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 8px 0;">
        <div style="font-size:16px;font-weight:700;color:#d4a017;">🛡️ HSEI Platform</div>
        <div style="font-size:11px;color:#9a8a6a;margin-top:3px;">
            HSE Incident Analytics &amp; Process Safety
        </div>
        <div style="font-size:10px;color:#5a5040;margin-top:2px;">
            Offshore Production Complex · OPC-Alpha
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#3a3020;margin:6px 0 12px;">', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "🛡️  HSE Executive Overview",
            "📋  Incident Register & Analysis",
            "⚗️  Process Safety (API RP 754)",
            "✅  Corrective Actions Tracker",
            "📡  Leading Indicators",
            "🔍  HSE Inspections & Audit",
            "📄  Permit to Work Analytics",
            "🎓  Training & Competency",
            "➕  Data Entry",
        ],
        label_visibility="collapsed",
    )

    st.markdown('<hr style="border-color:#3a3020;margin:12px 0 10px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:10px;color:#9a8a6a;line-height:2.1;">
        <div>📅 Data Period: Jan–Dec 2024</div>
        <div>📐 API RP 754 · ISO 45001</div>
        <div>🏛️ NUPRC · NOSDRA</div>
        <div style="margin-top:6px;color:#4ade80;font-weight:600;">● Platform Online</div>
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
    from dashboards.pages.p_data_entry import render_data_entry
    render_data_entry()