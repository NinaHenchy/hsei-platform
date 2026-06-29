"""
HSEI Data Entry — Log real HSE events directly to the database.
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent.parent
for _p in [str(_root), "/app"]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import pandas as pd
from datetime import date, datetime
from sqlalchemy import text

from dashboards.components.ui_components import (
    inject_css, page_header, section_header, THEME
)


def get_engine():
    from database.db_connection import get_engine as _get
    return _get()


def render_data_entry():
    inject_css()
    page_header(
        "HSE Data Entry",
        "Log real HSE events — saved permanently to the database",
        "➕"
    )

    st.info(
        "All entries are saved directly to the database and immediately "
        "reflected across all dashboard pages."
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚠️ Incident / Near Miss",
        "✅ Corrective Action",
        "🔍 Inspection",
        "📡 Safety Observation",
    ])

    with tab1:
        section_header("Log New Incident or Near Miss")
        with st.form("incident_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                inc_date      = st.date_input("Incident Date *", value=date.today())
                inc_time      = st.time_input("Incident Time *")
                inc_type      = st.selectbox("Incident Type *", [
                    "Near Miss","First Aid","Medical Treatment",
                    "Restricted Work","Lost Time Injury","Fatality",
                    "Property Damage","Environmental Release","Process Safety Event"
                ])
                severity      = st.selectbox("Severity *", ["Critical","High","Medium","Low","Negligible"])
                department    = st.selectbox("Department *", [
                    "Operations","Maintenance","HSE","Drilling",
                    "Process Engineering","Logistics","Contractor","Management"
                ])
            with col2:
                location      = st.text_input("Location / Area *")
                reported_by   = st.text_input("Reported By")
                days_lost     = st.number_input("Days Lost (LTI only)", min_value=0, max_value=365, value=0)
                api_tier      = st.selectbox("API RP 754 Tier", ["N/A","Tier 1","Tier 2","Tier 3","Tier 4"])
                regulatory    = st.checkbox("Regulatory Reportable?")
                is_recurring  = st.checkbox("Recurring incident?")

            description      = st.text_area("Incident Description *",
                placeholder="What happened, where, who was involved, immediate consequences...")
            immediate_action = st.text_area("Immediate Action Taken",
                placeholder="What was done immediately after the incident?")

            if st.form_submit_button("💾 Save Incident", use_container_width=True, type="primary"):
                if not description or not location:
                    st.error("Please fill in all required fields marked with *")
                else:
                    try:
                        engine = get_engine()
                        ref = f"INC-{inc_date.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                        with engine.connect() as conn:
                            conn.execute(text("""
                                INSERT INTO incidents (
                                    incident_date, incident_time, incident_type,
                                    severity, department, location,
                                    description, immediate_action_taken,
                                    days_lost, api_rp754_tier,
                                    regulatory_reportable, is_recurring,
                                    reported_by, incident_reference
                                ) VALUES (
                                    :inc_date, :inc_time, :inc_type,
                                    :severity, :dept, :location,
                                    :description, :immediate,
                                    :days_lost, :api_tier,
                                    :regulatory, :recurring,
                                    :reported_by, :ref
                                )
                            """), {
                                "inc_date": str(inc_date), "inc_time": str(inc_time),
                                "inc_type": inc_type, "severity": severity,
                                "dept": department, "location": location,
                                "description": description, "immediate": immediate_action,
                                "days_lost": days_lost, "api_tier": api_tier,
                                "regulatory": int(regulatory), "recurring": int(is_recurring),
                                "reported_by": reported_by, "ref": ref,
                            })
                            conn.commit()
                        st.success(f"✅ Incident logged! Reference: {ref}")
                    except Exception as e:
                        st.error(f"Error saving incident: {e}")

    with tab2:
        section_header("Log New Corrective Action")
        with st.form("ca_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ca_ref        = st.text_input("CA Reference *", placeholder="CA-2024-001")
                ca_title      = st.text_input("Action Title *")
                ca_type       = st.selectbox("Action Type *", [
                    "Corrective Action","Preventive Action",
                    "Improvement Action","Immediate Action"
                ])
                priority      = st.selectbox("Priority *", ["Critical","High","Medium","Low"])
                dept_ca       = st.selectbox("Responsible Department *", [
                    "Operations","Maintenance","HSE","Drilling",
                    "Process Engineering","Logistics","Management"
                ])
            with col2:
                assigned_to   = st.text_input("Assigned To *")
                due_date      = st.date_input("Due Date *", value=date.today())
                open_date     = st.date_input("Date Raised", value=date.today())
                status        = st.selectbox("Status", ["Open","In Progress","Completed","Overdue","Cancelled"])
                completion_date = st.date_input("Completion Date", value=None)

            ca_description = st.text_area("Action Description *",
                placeholder="Describe the corrective action required...")
            verification   = st.text_area("Verification Method",
                placeholder="How will completion be verified?")

            if st.form_submit_button("💾 Save Corrective Action", use_container_width=True, type="primary"):
                if not ca_title or not assigned_to or not ca_ref:
                    st.error("Please fill in all required fields marked with *")
                else:
                    try:
                        engine = get_engine()
                        with engine.connect() as conn:
                            conn.execute(text("""
                                INSERT INTO corrective_actions (
                                    ca_reference, title, action_type,
                                    priority, responsible_department,
                                    assigned_to, due_date, open_date,
                                    status, description, verification_method,
                                    completion_date
                                ) VALUES (
                                    :ref, :title, :ca_type,
                                    :priority, :dept,
                                    :assigned_to, :due_date, :open_date,
                                    :status, :description, :verification,
                                    :completion_date
                                )
                            """), {
                                "ref": ca_ref, "title": ca_title, "ca_type": ca_type,
                                "priority": priority, "dept": dept_ca,
                                "assigned_to": assigned_to,
                                "due_date": str(due_date),
                                "open_date": str(open_date),
                                "status": status,
                                "description": ca_description,
                                "verification": verification,
                                "completion_date": str(completion_date) if completion_date else None,
                            })
                            conn.commit()
                        st.success(f"✅ Corrective action saved! Reference: {ca_ref}")
                    except Exception as e:
                        st.error(f"Error saving corrective action: {e}")

    with tab3:
        section_header("Log New Inspection")
        with st.form("inspection_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                insp_date     = st.date_input("Inspection Date *", value=date.today())
                insp_type     = st.selectbox("Inspection Type *", [
                    "General HSE Inspection","Process Safety Inspection",
                    "PTW Audit","Housekeeping Inspection",
                    "Emergency Equipment Check","Environmental Inspection",
                    "Contractor HSE Inspection","Regulatory Inspection"
                ])
                dept_insp     = st.selectbox("Area / Department *", [
                    "Operations","Maintenance","HSE","Drilling",
                    "Process Engineering","Logistics","Site-Wide"
                ])
                inspector     = st.text_input("Inspector Name *")
            with col2:
                score         = st.slider("Inspection Score *", 0, 100, 80)
                findings      = st.number_input("Number of Findings", min_value=0, max_value=50, value=0)
                critical_findings = st.number_input("Critical Findings", min_value=0, max_value=10, value=0)
                action_required = st.checkbox("Corrective Action Required?")

            insp_notes = st.text_area("Inspection Notes",
                placeholder="Summary of key observations and findings...")

            if st.form_submit_button("💾 Save Inspection", use_container_width=True, type="primary"):
                if not inspector:
                    st.error("Please provide inspector name")
                else:
                    try:
                        engine = get_engine()
                        ref = f"INSP-{insp_date.strftime('%Y%m')}-{datetime.now().strftime('%H%M%S')}"
                        with engine.connect() as conn:
                            conn.execute(text("""
                                INSERT INTO inspections (
                                    inspection_date, inspection_type,
                                    department, inspector_name,
                                    inspection_score, findings_count,
                                    critical_findings, action_required,
                                    notes, inspection_reference
                                ) VALUES (
                                    :date, :type, :dept, :inspector,
                                    :score, :findings, :critical,
                                    :action_req, :notes, :ref
                                )
                            """), {
                                "date": str(insp_date), "type": insp_type,
                                "dept": dept_insp, "inspector": inspector,
                                "score": score, "findings": findings,
                                "critical": critical_findings,
                                "action_req": int(action_required),
                                "notes": insp_notes, "ref": ref,
                            })
                            conn.commit()
                        st.success(f"✅ Inspection saved! Ref: {ref} | Score: {score}/100")
                    except Exception as e:
                        st.error(f"Error saving inspection: {e}")

    with tab4:
        section_header("Log Safety Observation")
        with st.form("obs_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                obs_date      = st.date_input("Observation Date *", value=date.today())
                obs_type      = st.selectbox("Observation Type *", [
                    "Safe Behaviour","Unsafe Behaviour","Unsafe Condition",
                    "Near Miss","Environmental Concern","Stop Work Authority",
                    "Positive Observation","Housekeeping"
                ])
                dept_obs      = st.selectbox("Department *", [
                    "Operations","Maintenance","HSE","Drilling",
                    "Process Engineering","Logistics","Contractor","Management"
                ])
                observed_by   = st.text_input("Observed By *")
            with col2:
                risk_level    = st.selectbox("Risk Level", ["Low","Medium","High","Critical"])
                immediate_act = st.checkbox("Immediate Action Taken?")
                acknowledged  = st.checkbox("Acknowledged by Supervisor?")

            obs_description = st.text_area("Observation Description *",
                placeholder="What did you observe? Be specific about location, activity, and conditions...")
            action_taken = st.text_area("Action Taken",
                placeholder="What action was taken or recommended?")

            if st.form_submit_button("💾 Save Observation", use_container_width=True, type="primary"):
                if not obs_description or not observed_by:
                    st.error("Please fill in all required fields marked with *")
                else:
                    try:
                        engine = get_engine()
                        ref = f"OBS-{obs_date.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                        with engine.connect() as conn:
                            conn.execute(text("""
                                INSERT INTO safety_observations (
                                    observation_date, observation_type,
                                    department, observed_by,
                                    risk_level, description,
                                    action_taken, immediate_action_taken,
                                    acknowledged_by_supervisor,
                                    observation_reference
                                ) VALUES (
                                    :date, :obs_type, :dept, :observed_by,
                                    :risk, :description, :action,
                                    :immediate, :acknowledged, :ref
                                )
                            """), {
                                "date": str(obs_date), "obs_type": obs_type,
                                "dept": dept_obs, "observed_by": observed_by,
                                "risk": risk_level, "description": obs_description,
                                "action": action_taken,
                                "immediate": int(immediate_act),
                                "acknowledged": int(acknowledged),
                                "ref": ref,
                            })
                            conn.commit()
                        st.success(f"✅ Observation saved! Reference: {ref}")
                    except Exception as e:
                        st.error(f"Error saving observation: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Recent Entries")
    engine = get_engine()
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**Recent Incidents**")
        try:
            df = pd.read_sql("""
                SELECT incident_date, incident_type, severity, department
                FROM incidents ORDER BY rowid DESC LIMIT 5
            """, engine)
            st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty \
                else st.caption("No incidents logged yet.")
        except Exception:
            st.caption("No incidents logged yet.")
    with col_r2:
        st.markdown("**Recent Corrective Actions**")
        try:
            df = pd.read_sql("""
                SELECT ca_reference, title, priority, status, assigned_to
                FROM corrective_actions ORDER BY rowid DESC LIMIT 5
            """, engine)
            st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty \
                else st.caption("No corrective actions logged yet.")
        except Exception:
            st.caption("No corrective actions logged yet.")