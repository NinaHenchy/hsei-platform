"""
HSEI Data Entry Page
Log real HSE incidents, observations, actions, inspections and training.
All entries saved permanently to the SQLite database.
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
from config.settings import (
    INCIDENT_TYPES, INCIDENT_CATEGORIES, WORK_AREAS,
    DEPARTMENTS, BODY_PARTS, ROOT_CAUSE_CATEGORIES,
    INCIDENT_COST_ESTIMATES
)


def get_engine():
    from database.db_connection import get_engine as _get
    return _get()


def render_hsei_data_entry():
    inject_css()
    page_header(
        "HSE Data Entry",
        "Log real HSE events — saved permanently to the database",
        "➕"
    )

    st.info(
        "All entries are saved to the SQLite database and immediately "
        "reflected across all HSEI dashboard pages."
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚨 Incident Report",
        "👁️ Safety Observation",
        "✅ Corrective Action",
        "🔍 HSE Inspection",
        "🎓 Training Record",
    ])

    # ── TAB 1: INCIDENT REPORT ────────────────────────────────────────
    with tab1:
        section_header("Report New HSE Incident")

        with st.form("incident_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                inc_type = st.selectbox("Incident Type *", INCIDENT_TYPES)
                inc_category = st.selectbox("Incident Category *", INCIDENT_CATEGORIES)
                inc_date = st.date_input("Incident Date *", value=date.today())
                inc_time = st.time_input("Incident Time *")
                severity = st.selectbox(
                    "Severity *",
                    ["Critical", "High", "Medium", "Low", "Negligible"]
                )
                work_area = st.selectbox("Work Area *", WORK_AREAS)

            with col2:
                department = st.selectbox("Department *", DEPARTMENTS)
                body_part = st.selectbox("Body Part Affected", BODY_PARTS)
                days_lost = st.number_input(
                    "Days Lost", min_value=0, max_value=365, value=0
                )
                days_restricted = st.number_input(
                    "Days Restricted Work", min_value=0, max_value=365, value=0
                )
                emp_type = st.selectbox(
                    "Employee Type", ["Direct", "Contractor", "Visitor"]
                )
                reported_by = st.text_input("Reported By *")

            description = st.text_area(
                "Incident Description *",
                placeholder="What happened? Where? When? Who was involved?"
            )

            col3, col4 = st.columns(2)
            with col3:
                immediate_cause = st.text_area(
                    "Immediate Cause",
                    placeholder="What directly caused the incident?"
                )
                root_cause_cat = st.selectbox(
                    "Root Cause Category", ROOT_CAUSE_CATEGORIES
                )
            with col4:
                root_cause_desc = st.text_area(
                    "Root Cause Description",
                    placeholder="Explain the underlying root cause..."
                )
                contributing = st.text_area(
                    "Contributing Factors",
                    placeholder="What other factors contributed?"
                )

            col5, col6 = st.columns(2)
            with col5:
                reg_reportable = st.checkbox("Regulatory Reportable?")
                is_recurring = st.checkbox("Is this a recurring incident?")
            with col6:
                env_impact = st.checkbox("Environmental Impact?")
                spill_vol = st.number_input(
                    "Spill Volume (litres)", min_value=0.0, value=0.0,
                    step=1.0
                ) if env_impact else 0.0

            inc_submitted = st.form_submit_button(
                "🚨 Submit Incident Report",
                use_container_width=True,
                type="primary"
            )

            if inc_submitted:
                if not description or not reported_by:
                    st.error("Please fill in all required fields (*).")
                else:
                    try:
                        engine = get_engine()
                        cost = INCIDENT_COST_ESTIMATES.get(inc_type, 5000)

                        with engine.connect() as conn:
                            count = conn.execute(
                                text("SELECT COUNT(*) FROM incidents")
                            ).scalar()
                            inc_number = f"INC-LIVE-{count+1:04d}"

                            conn.execute(text("""
                                INSERT INTO incidents (
                                    incident_number, incident_date, incident_time,
                                    incident_type, incident_category, severity,
                                    work_area, department, description,
                                    immediate_cause, root_cause_category,
                                    root_cause_description, contributing_factors,
                                    body_part_affected, days_lost, days_restricted,
                                    employee_type, reported_by,
                                    regulatory_reportable, is_recurring,
                                    environmental_impact, spill_volume_litres,
                                    estimated_cost_usd, is_closed
                                ) VALUES (
                                    :number, :inc_date, :inc_time,
                                    :inc_type, :category, :severity,
                                    :area, :dept, :description,
                                    :immediate, :rc_cat,
                                    :rc_desc, :contributing,
                                    :body_part, :days_lost, :days_restricted,
                                    :emp_type, :reported_by,
                                    :reg_report, :recurring,
                                    :env_impact, :spill_vol,
                                    :cost, 0
                                )
                            """), {
                                "number": inc_number,
                                "inc_date": str(inc_date),
                                "inc_time": str(inc_time),
                                "inc_type": inc_type,
                                "category": inc_category,
                                "severity": severity,
                                "area": work_area,
                                "dept": department,
                                "description": description,
                                "immediate": immediate_cause,
                                "rc_cat": root_cause_cat,
                                "rc_desc": root_cause_desc,
                                "contributing": contributing,
                                "body_part": body_part,
                                "days_lost": days_lost,
                                "days_restricted": days_restricted,
                                "emp_type": emp_type,
                                "reported_by": reported_by,
                                "reg_report": int(reg_reportable),
                                "recurring": int(is_recurring),
                                "env_impact": int(env_impact),
                                "spill_vol": spill_vol if env_impact else None,
                                "cost": cost,
                            })
                            conn.commit()

                        level = "critical" if severity in ["Critical","High"] else "warning"
                        if severity in ["Critical","High"]:
                            st.error(
                                f"🚨 {severity.upper()} incident logged: **{inc_number}**\n\n"
                                f"Notify HSE Manager and line management immediately.\n\n"
                                f"Navigate to **Incident Register** to see the record."
                            )
                        else:
                            st.success(
                                f"✅ Incident logged: **{inc_number}**\n\n"
                                f"**Type:** {inc_type} | **Area:** {work_area}\n\n"
                                f"Navigate to **Incident Register** to see the record."
                            )

                    except Exception as e:
                        st.error(f"Error saving incident: {e}")

    # ── TAB 2: SAFETY OBSERVATION ─────────────────────────────────────
    with tab2:
        section_header("Submit Safety Observation / Near Miss")

        with st.form("obs_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                obs_type = st.selectbox(
                    "Observation Type *",
                    ["Near Miss", "Unsafe Act", "Unsafe Condition",
                     "Good Practice", "Safety Walk", "Stop Work Authority",
                     "Dropped Object Potential", "Environmental Concern"]
                )
                obs_date = st.date_input("Date *", value=date.today(), key="obs_d")
                obs_area = st.selectbox("Work Area *", WORK_AREAS, key="obs_a")
                obs_dept = st.selectbox("Department", DEPARTMENTS, key="obs_dept")

            with col2:
                pot_severity = st.selectbox(
                    "Potential Severity *",
                    ["Critical", "High", "Medium", "Low"]
                )
                obs_reporter = st.text_input("Reported By (leave blank to stay anonymous)")
                is_anonymous = not bool(obs_reporter)
                followup_needed = st.checkbox(
                    "Follow-up action required?",
                    value=obs_type in ["Near Miss","Unsafe Act","Unsafe Condition",
                                       "Stop Work Authority"]
                )

            obs_description = st.text_area(
                "Description *",
                placeholder="Describe what you observed. Be specific about location, activity, and hazard."
            )
            immediate_action = st.text_area(
                "Immediate Action Taken",
                placeholder="What was done immediately to control the hazard?"
            )
            followup_action = st.text_area(
                "Recommended Follow-up Action",
                placeholder="What further action should be taken?"
            ) if followup_needed else ""

            obs_submitted = st.form_submit_button(
                "👁️ Submit Observation",
                use_container_width=True,
                type="primary"
            )

            if obs_submitted:
                if not obs_description:
                    st.error("Please provide an observation description.")
                else:
                    try:
                        engine = get_engine()
                        with engine.connect() as conn:
                            count = conn.execute(
                                text("SELECT COUNT(*) FROM safety_observations")
                            ).scalar()
                            obs_number = f"OBS-LIVE-{count+1:04d}"

                            conn.execute(text("""
                                INSERT INTO safety_observations (
                                    observation_number, observation_date,
                                    observation_type, work_area, department,
                                    description, potential_severity,
                                    reported_by, is_anonymous,
                                    immediate_action_taken,
                                    followup_required, followup_action,
                                    followup_complete
                                ) VALUES (
                                    :number, :obs_date,
                                    :obs_type, :area, :dept,
                                    :description, :severity,
                                    :reporter, :anon,
                                    :immediate,
                                    :followup_req, :followup_act,
                                    0
                                )
                            """), {
                                "number": obs_number,
                                "obs_date": str(obs_date),
                                "obs_type": obs_type,
                                "area": obs_area,
                                "dept": obs_dept,
                                "description": obs_description,
                                "severity": pot_severity,
                                "reporter": obs_reporter or "Anonymous",
                                "anon": int(is_anonymous),
                                "immediate": immediate_action,
                                "followup_req": int(followup_needed),
                                "followup_act": followup_action,
                            })
                            conn.commit()

                        st.success(
                            f"✅ Observation submitted: **{obs_number}**\n\n"
                            f"**Type:** {obs_type} | **Potential Severity:** {pot_severity}\n\n"
                            f"Thank you for reporting. Every observation improves safety.\n\n"
                            f"Navigate to **Leading Indicators** to see the update."
                        )

                    except Exception as e:
                        st.error(f"Error saving observation: {e}")

    # ── TAB 3: CORRECTIVE ACTION ──────────────────────────────────────
    with tab3:
        section_header("Raise Corrective Action")
        st.caption("Raise a standalone corrective action or close out an existing one.")

        engine = get_engine()

        # Show open actions for close-out
        open_actions = pd.read_sql("""
            SELECT ca.action_number, ca.description, ca.status, ca.due_date,
                   ca.assigned_to
            FROM corrective_actions ca
            WHERE ca.status IN ('Open','In Progress','Overdue')
            ORDER BY ca.due_date
            LIMIT 20
        """, engine)

        if not open_actions.empty:
            st.markdown("**Open Actions — Update Status**")
            selected_action = st.selectbox(
                "Select action to update (optional)",
                options=["-- Raise New Action --"] + open_actions["action_number"].tolist()
            )

            if selected_action != "-- Raise New Action --":
                action_row = open_actions[
                    open_actions["action_number"] == selected_action
                ].iloc[0]
                st.info(f"**{selected_action}:** {action_row['description'][:100]}")

                new_status = st.selectbox(
                    "Update Status",
                    ["In Progress", "Closed", "Cancelled"]
                )
                completion_notes = st.text_area("Completion Notes")

                if st.button("✅ Update Action Status", type="primary"):
                    try:
                        with engine.connect() as conn:
                            conn.execute(text("""
                                UPDATE corrective_actions
                                SET status = :status,
                                    completion_date = :comp_date,
                                    notes = :notes
                                WHERE action_number = :number
                            """), {
                                "status": new_status,
                                "comp_date": str(date.today()) if new_status == "Closed" else None,
                                "notes": completion_notes,
                                "number": selected_action,
                            })
                            conn.commit()
                        st.success(f"✅ Action **{selected_action}** updated to **{new_status}**")
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("**Raise New Corrective Action**")

        with st.form("ca_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ca_type = st.selectbox("Action Type *", [
                    "Immediate Corrective Action",
                    "Root Cause Corrective Action",
                    "Preventive Action",
                    "System Improvement",
                    "Training Requirement",
                    "Engineering Control",
                    "Administrative Control",
                ])
                ca_priority = st.selectbox("Priority *", ["Critical","High","Medium","Low"])
                ca_due = st.date_input("Due Date *", value=date.today())

            with col2:
                ca_assigned_to = st.text_input("Assigned To *")
                ca_dept = st.selectbox("Assigned Department", DEPARTMENTS, key="ca_dept")

            ca_description = st.text_area(
                "Action Description *",
                placeholder="What action needs to be taken? Be specific and measurable."
            )

            ca_submitted = st.form_submit_button(
                "✅ Raise Corrective Action",
                use_container_width=True,
                type="primary"
            )

            if ca_submitted:
                if not ca_description or not ca_assigned_to:
                    st.error("Please fill in all required fields.")
                else:
                    try:
                        with engine.connect() as conn:
                            count = conn.execute(
                                text("SELECT COUNT(*) FROM corrective_actions")
                            ).scalar()
                            ca_number = f"CA-LIVE-{count+1:04d}"

                            conn.execute(text("""
                                INSERT INTO corrective_actions (
                                    action_number, action_type, description,
                                    assigned_to, assigned_department,
                                    due_date, status, priority,
                                    verification_required
                                ) VALUES (
                                    :number, :ca_type, :description,
                                    :assigned, :dept,
                                    :due_date, 'Open', :priority,
                                    1
                                )
                            """), {
                                "number": ca_number,
                                "ca_type": ca_type,
                                "description": ca_description,
                                "assigned": ca_assigned_to,
                                "dept": ca_dept,
                                "due_date": str(ca_due),
                                "priority": ca_priority,
                            })
                            conn.commit()

                        st.success(
                            f"✅ Action raised: **{ca_number}**\n\n"
                            f"**Assigned to:** {ca_assigned_to} | **Due:** {ca_due}\n\n"
                            f"Navigate to **Corrective Actions Tracker** to monitor."
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── TAB 4: HSE INSPECTION ─────────────────────────────────────────
    with tab4:
        section_header("Log HSE Inspection / Audit")

        with st.form("insp_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                insp_type = st.selectbox("Inspection Type *", [
                    "Daily Safety Walk", "Weekly HSE Inspection",
                    "Monthly Audit", "Quarterly Management Audit",
                    "Regulatory Inspection", "Third Party Audit",
                    "Pre-Job Safety Inspection", "Emergency Response Drill",
                ])
                insp_date = st.date_input("Inspection Date *", value=date.today(), key="insp_d")
                insp_area = st.selectbox("Work Area *", WORK_AREAS, key="insp_a")
                inspector = st.text_input("Inspector Name *")

            with col2:
                insp_score = st.slider("Inspection Score *", 0, 100, 85)
                items_inspected = st.number_input("Items Inspected", min_value=1, value=10)
                findings = st.number_input("Total Findings", min_value=0, value=0)
                critical_f = st.number_input("Critical Findings", min_value=0, value=0)
                major_f = st.number_input("Major Findings", min_value=0, value=0)

            if insp_score >= 90:   rating = "Excellent"
            elif insp_score >= 80: rating = "Good"
            elif insp_score >= 70: rating = "Satisfactory"
            elif insp_score >= 60: rating = "Unsatisfactory"
            else:                  rating = "Critical"

            st.info(f"Overall Rating: **{rating}**")
            insp_notes = st.text_area("Inspection Notes / Findings Summary")

            insp_submitted = st.form_submit_button(
                "🔍 Save Inspection Record",
                use_container_width=True,
                type="primary"
            )

            if insp_submitted:
                if not inspector:
                    st.error("Please enter inspector name.")
                else:
                    try:
                        engine = get_engine()
                        with engine.connect() as conn:
                            count = conn.execute(
                                text("SELECT COUNT(*) FROM hse_inspections")
                            ).scalar()
                            insp_number = f"INSP-LIVE-{count+1:04d}"

                            conn.execute(text("""
                                INSERT INTO hse_inspections (
                                    inspection_number, inspection_date,
                                    inspection_type, work_area, inspector,
                                    inspection_score, items_inspected,
                                    findings_count, critical_findings,
                                    major_findings, minor_findings,
                                    actions_raised, overall_rating, notes
                                ) VALUES (
                                    :number, :date, :type, :area, :inspector,
                                    :score, :items, :findings, :critical,
                                    :major, :minor, :actions, :rating, :notes
                                )
                            """), {
                                "number": insp_number,
                                "date": str(insp_date),
                                "type": insp_type,
                                "area": insp_area,
                                "inspector": inspector,
                                "score": insp_score,
                                "items": items_inspected,
                                "findings": findings,
                                "critical": critical_f,
                                "major": major_f,
                                "minor": max(0, findings - critical_f - major_f),
                                "actions": findings,
                                "rating": rating,
                                "notes": insp_notes,
                            })
                            conn.commit()

                        st.success(
                            f"✅ Inspection logged: **{insp_number}**\n\n"
                            f"**Score:** {insp_score}/100 — {rating}\n\n"
                            f"Navigate to **HSE Inspections & Audit** to see the update."
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── TAB 5: TRAINING RECORD ────────────────────────────────────────
    with tab5:
        section_header("Log Training Completion")

        with st.form("training_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                emp_name = st.text_input("Employee Name *")
                emp_id = st.text_input("Employee ID", placeholder="e.g. EMP-0001")
                dept = st.selectbox("Department *", DEPARTMENTS, key="tr_dept")
                emp_type = st.selectbox("Employee Type", ["Direct","Contractor","Visitor"])

            with col2:
                course = st.text_input(
                    "Training Course *",
                    placeholder="e.g. Basic H2S Safety"
                )
                category = st.selectbox("Training Category", [
                    "Process Safety", "Emergency Response", "Safety Management",
                    "Physical Hazards", "Chemical Safety", "Environmental",
                    "Electrical Safety", "Offshore Safety", "Ergonomics",
                ])
                train_date = st.date_input("Training Date *", value=date.today(), key="tr_date")
                validity_days = st.selectbox(
                    "Certificate Validity",
                    [365, 730, 1095, 1825],
                    format_func=lambda x: f"{x} days ({x//365} year{'s' if x//365>1 else ''})"
                )
                score = st.slider("Assessment Score (%)", 0, 100, 85)
                trainer = st.text_input("Trainer / Provider")

            tr_submitted = st.form_submit_button(
                "🎓 Save Training Record",
                use_container_width=True,
                type="primary"
            )

            if tr_submitted:
                if not emp_name or not course:
                    st.error("Please fill in employee name and course name.")
                else:
                    try:
                        from datetime import timedelta
                        engine = get_engine()
                        expiry = train_date + timedelta(days=validity_days)
                        cert_number = f"CERT-LIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        emp_id_final = emp_id or f"EMP-{datetime.now().strftime('%H%M%S')}"

                        with engine.connect() as conn:
                            conn.execute(text("""
                                INSERT INTO training_records (
                                    employee_id, employee_name, department,
                                    employee_type, training_course, training_category,
                                    training_date, expiry_date, is_expired,
                                    score_pct, passed, trainer,
                                    training_provider, certificate_number, mandatory
                                ) VALUES (
                                    :emp_id, :name, :dept,
                                    :emp_type, :course, :category,
                                    :train_date, :expiry, 0,
                                    :score, 1, :trainer,
                                    :provider, :cert, 1
                                )
                            """), {
                                "emp_id": emp_id_final,
                                "name": emp_name,
                                "dept": dept,
                                "emp_type": emp_type,
                                "course": course,
                                "category": category,
                                "train_date": str(train_date),
                                "expiry": str(expiry),
                                "score": score,
                                "trainer": trainer,
                                "provider": trainer,
                                "cert": cert_number,
                            })
                            conn.commit()

                        st.success(
                            f"✅ Training record saved!\n\n"
                            f"**Employee:** {emp_name} | **Course:** {course}\n\n"
                            f"**Certificate:** {cert_number} | **Expires:** {expiry}\n\n"
                            f"Navigate to **Training & Competency** to see the update."
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── RECENT ENTRIES ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Recent Live Entries")

    engine = get_engine()
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("**Recent Incidents**")
        try:
            df = pd.read_sql("""
                SELECT incident_number, incident_date, incident_type,
                       severity, work_area
                FROM incidents
                WHERE incident_number LIKE 'INC-LIVE-%'
                ORDER BY rowid DESC LIMIT 5
            """, engine)
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("No live incidents logged yet.")
        except Exception:
            pass

    with col_r2:
        st.markdown("**Recent Observations**")
        try:
            df = pd.read_sql("""
                SELECT observation_number, observation_date,
                       observation_type, potential_severity
                FROM safety_observations
                WHERE observation_number LIKE 'OBS-LIVE-%'
                ORDER BY rowid DESC LIMIT 5
            """, engine)
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("No live observations logged yet.")
        except Exception:
            pass
