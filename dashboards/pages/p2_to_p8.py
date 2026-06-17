"""
HSEI Pages 2–8
"""

import sys
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

_root = Path(__file__).resolve().parent.parent.parent
for _p in [str(_root), "/app"]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
from dashboards.data_access import (
    get_incidents, get_monthly_kpis, get_corrective_actions,
    get_safety_observations, get_hse_inspections, get_ptw_records,
    get_training_records, get_incident_pareto, get_open_actions,
    get_facility_hse_summary
)
from dashboards.components.ui_components import (
    inject_css, page_header, section_header, alert_banner, apply_layout,
    THEME, SEVERITY_COLORS, TIER_COLORS
)
from config.settings import KPI_THRESHOLDS, WORK_AREAS, DEPARTMENTS


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — INCIDENT REGISTER & ANALYSIS
# ═══════════════════════════════════════════════════════════════
def render_incident_analysis():
    inject_css()
    page_header("Incident Register & Analysis",
                "Full incident log · Root cause analysis · Severity trending · Cost impact", "📋")

    incidents = get_incidents()
    if incidents.empty:
        st.warning("No incidents found.")
        return

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sel_types = st.multiselect("Incident Type", options=sorted(incidents["incident_type"].unique()),
                                   default=list(incidents["incident_type"].unique()))
    with col_f2:
        sel_sev = st.multiselect("Severity", options=["Critical","High","Medium","Low","Negligible"],
                                 default=["Critical","High","Medium","Low","Negligible"])
    with col_f3:
        sel_dept = st.multiselect("Department", options=sorted(incidents["department"].dropna().unique()),
                                  default=list(incidents["department"].dropna().unique()))

    filtered = incidents[
        incidents["incident_type"].isin(sel_types) &
        incidents["severity"].isin(sel_sev) &
        incidents["department"].isin(sel_dept)
    ]

    # Summary metrics
    section_header("Filtered Incident Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Incidents", len(filtered))
    with c2: st.metric("Days Lost", int(filtered["days_lost"].sum()))
    with c3: st.metric("Total Cost", f"${filtered['estimated_cost_usd'].sum():,.0f}")
    with c4: st.metric("Regulatory Reportable", int(filtered["regulatory_reportable"].sum()))
    with c5: st.metric("Recurring Incidents", int(filtered["is_recurring"].sum()))

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        section_header("Incident Pareto — By Category")
        pareto = filtered.groupby("incident_category").agg(
            count=("id","count"),
            total_cost=("estimated_cost_usd","sum"),
            days_lost=("days_lost","sum")
        ).reset_index().sort_values("count", ascending=True)

        fig_p = go.Figure(go.Bar(
            x=pareto["count"], y=pareto["incident_category"],
            orientation="h",
            marker_color=THEME["red"], opacity=0.8,
            text=pareto["count"], textposition="outside",
        ))
        apply_layout(fig_p, height=320)
        fig_p.update_layout(margin=dict(l=210, r=40, t=20, b=40), showlegend=False,
                            xaxis_title="Count")
        st.plotly_chart(fig_p, use_container_width=True, key="p2_to_p8_chart_1")

    with col_r:
        section_header("Cost Impact by Incident Type")
        cost_data = filtered.groupby("incident_type")["estimated_cost_usd"].sum().sort_values(ascending=True)
        fig_cost = go.Figure(go.Bar(
            x=cost_data.values, y=cost_data.index,
            orientation="h", marker_color=THEME["amber"], opacity=0.8,
            text=[f"${v:,.0f}" for v in cost_data.values],
            textposition="outside", textfont=dict(size=9),
        ))
        apply_layout(fig_cost, height=320)
        fig_cost.update_layout(margin=dict(l=185, r=80, t=20, b=40), showlegend=False,
                               xaxis_title="Total Cost (USD)")
        st.plotly_chart(fig_cost, use_container_width=True, key="p2_to_p8_chart_2")

    st.markdown("<br>", unsafe_allow_html=True)

    section_header("Severity Distribution & Work Area Analysis")
    col_sev, col_area = st.columns(2)

    with col_sev:
        sev_counts = filtered["severity"].value_counts()
        fig_sev = go.Figure(go.Pie(
            labels=sev_counts.index.tolist(),
            values=sev_counts.values.tolist(),
            marker_colors=[SEVERITY_COLORS.get(s, THEME["blue"]) for s in sev_counts.index],
            hole=0.5,
            textinfo="label+percent",
        ))
        apply_layout(fig_sev, "Severity Distribution", height=280)
        fig_sev.update_layout(showlegend=False, margin=dict(l=20,r=20,t=35,b=20))
        st.plotly_chart(fig_sev, use_container_width=True, key="p2_to_p8_chart_3")

    with col_area:
        area_counts = filtered["work_area"].value_counts().head(8)
        fig_area = go.Figure(go.Bar(
            x=area_counts.values, y=area_counts.index,
            orientation="h", marker_color=THEME["blue"], opacity=0.8,
            text=area_counts.values, textposition="outside",
        ))
        apply_layout(fig_area, "Incidents by Work Area", height=280)
        fig_area.update_layout(margin=dict(l=160, r=30, t=35, b=40), showlegend=False)
        st.plotly_chart(fig_area, use_container_width=True, key="p2_to_p8_chart_4")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Incident Register — Full Log")
    cols = ["incident_number","incident_date","incident_type","severity",
            "work_area","department","days_lost","estimated_cost_usd",
            "root_cause_category","is_closed"]
    display = filtered[cols].copy()
    display.columns = ["Number","Date","Type","Severity","Area","Dept",
                       "Days Lost","Cost $","Root Cause Category","Closed"]
    display["Cost $"] = display["Cost $"].apply(lambda x: f"${x:,.0f}")
    display["Closed"] = display["Closed"].map({1:"✅","0":"⏳",0:"⏳"})
    st.dataframe(display, use_container_width=True, hide_index=True, height=320)


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — PROCESS SAFETY (API RP 754)
# ═══════════════════════════════════════════════════════════════
def render_process_safety():
    inject_css()
    page_header("Process Safety Intelligence",
                "API RP 754 Tier Classification · PSE Trending · Bow-Tie Risk Visibility", "⚗️")

    incidents = get_incidents()
    pse_all   = incidents[incidents["api_rp754_tier"].notna()].copy()

    # Tier summary
    section_header("API RP 754 — Process Safety Event Register")
    for tier in ["Tier 1","Tier 2","Tier 3","Tier 4"]:
        tier_inc = pse_all[pse_all["api_rp754_tier"] == tier]
        if tier_inc.empty:
            continue
        color = TIER_COLORS.get(tier, THEME["blue"])
        from config.settings import API_RP_754_TIERS
        tier_info = API_RP_754_TIERS.get(tier, {})
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid {color}55;border-left:4px solid {color};
                     border-radius:8px;padding:12px 18px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-size:14px;font-weight:700;color:{color};">{tier}</span>
                    <span style="font-size:11px;color:#4a4a6a;margin-left:12px;">
                        {tier_info.get('description','')}
                    </span>
                </div>
                <div style="display:flex;gap:24px;">
                    <div style="text-align:center;">
                        <div style="font-size:9px;color:#9a9ab0;text-transform:uppercase;">Events</div>
                        <div style="font-size:22px;font-weight:700;color:{color};">{len(tier_inc)}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:9px;color:#9a9ab0;text-transform:uppercase;">Cost</div>
                        <div style="font-size:16px;font-weight:600;color:#1a1a2e;">
                            ${tier_inc['estimated_cost_usd'].sum():,.0f}
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:9px;color:#9a9ab0;text-transform:uppercase;">Reportable</div>
                        <div style="font-size:14px;font-weight:600;color:{'#c0392b' if tier_info.get('regulatory_reportable') else '#1e7e34'};">
                            {"YES" if tier_info.get('regulatory_reportable') else "Internal"}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("PSE Tier Distribution")
        tier_counts = pse_all["api_rp754_tier"].value_counts()
        fig_tier = go.Figure(go.Pie(
            labels=tier_counts.index.tolist(),
            values=tier_counts.values.tolist(),
            marker_colors=[TIER_COLORS.get(t, THEME["blue"]) for t in tier_counts.index],
            hole=0.5,
            textinfo="label+value+percent",
        ))
        apply_layout(fig_tier, height=300)
        fig_tier.update_layout(showlegend=False, margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig_tier, use_container_width=True, key="p2_to_p8_chart_5")

    with col_r:
        section_header("PSE Monthly Trend")
        kpis = get_monthly_kpis()
        fig_pse = go.Figure()
        for tier, col, color in [
            ("pse_tier1_count","Tier 1",THEME["red"]),
            ("pse_tier2_count","Tier 2",THEME["amber"]),
            ("pse_tier3_count","Tier 3",THEME["orange"]),
            ("pse_tier4_count","Tier 4",THEME["green"]),
        ]:
            fig_pse.add_trace(go.Bar(
                x=kpis["year_month"], y=kpis[tier],
                name=col, marker_color=color, opacity=0.85,
            ))
        apply_layout(fig_pse, height=300)
        fig_pse.update_layout(barmode="stack", yaxis_title="Event Count",
                              legend=dict(orientation="h", y=1.1, x=0, font=dict(size=10)),
                              margin=dict(l=50,r=20,t=35,b=60))
        st.plotly_chart(fig_pse, use_container_width=True, key="p2_to_p8_chart_6")

    section_header("PSE Event Register")
    if not pse_all.empty:
        pse_display = pse_all[["incident_number","incident_date","api_rp754_tier",
                                "incident_type","work_area","description",
                                "regulatory_reportable","estimated_cost_usd"]].copy()
        pse_display.columns = ["Number","Date","API Tier","Type","Area",
                                "Description","Regulatory","Cost $"]
        pse_display["Cost $"] = pse_display["Cost $"].apply(lambda x: f"${x:,.0f}")
        pse_display["Regulatory"] = pse_display["Regulatory"].map({1:"🔴 YES",0:"Internal"})
        pse_display["Description"] = pse_display["Description"].str[:80]
        st.dataframe(pse_display, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — CORRECTIVE ACTIONS TRACKER
# ═══════════════════════════════════════════════════════════════
def render_corrective_actions():
    inject_css()
    page_header("Corrective Actions Tracker",
                "Action close-out performance · Overdue tracking · Priority management", "✅")

    actions  = get_corrective_actions()
    open_ca  = get_open_actions()

    if actions.empty:
        st.warning("No corrective actions found.")
        return

    # Overdue alerts
    overdue = actions[actions["status"] == "Overdue"]
    if not overdue.empty:
        alert_banner(f"{len(overdue)} actions are OVERDUE. Immediate management attention required.", "critical")

    section_header("Action Status Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Actions", len(actions))
    with c2: st.metric("Open", len(actions[actions["status"]=="Open"]))
    with c3: st.metric("In Progress", len(actions[actions["status"]=="In Progress"]))
    with c4: st.metric("Overdue", len(overdue))
    with c5:
        closed = len(actions[actions["status"]=="Closed"])
        closeout_rate = round(closed / len(actions) * 100, 1)
        st.metric("Close-out Rate", f"{closeout_rate}%",
                  "Target: 85%" if closeout_rate < 85 else "✓ Above target")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        section_header("Status Distribution")
        status_counts = actions["status"].value_counts()
        status_colors = {"Closed":THEME["green"],"In Progress":THEME["blue"],
                         "Open":THEME["amber"],"Overdue":THEME["red"],"Cancelled":THEME["text_muted"]}
        fig_status = go.Figure(go.Pie(
            labels=status_counts.index.tolist(),
            values=status_counts.values.tolist(),
            marker_colors=[status_colors.get(s, THEME["blue"]) for s in status_counts.index],
            hole=0.5, textinfo="label+percent",
        ))
        apply_layout(fig_status, height=280)
        fig_status.update_layout(showlegend=False, margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig_status, use_container_width=True, key="p2_to_p8_chart_7")

    with col_r:
        section_header("Actions by Type")
        type_counts = actions["action_type"].value_counts()
        fig_type = go.Figure(go.Bar(
            x=type_counts.values, y=type_counts.index,
            orientation="h", marker_color=THEME["blue"], opacity=0.8,
            text=type_counts.values, textposition="outside",
        ))
        apply_layout(fig_type, height=280)
        fig_type.update_layout(margin=dict(l=200,r=40,t=20,b=40), showlegend=False)
        st.plotly_chart(fig_type, use_container_width=True, key="p2_to_p8_chart_8")

    section_header("Open & Overdue Actions — Priority Register")
    tabs = st.tabs(["All Open Actions", "Overdue Only", "Closed Actions"])

    def _render_actions(df):
        if df.empty:
            st.info("No actions in this category.")
            return
        cols = ["action_number","incident_id","action_type","description",
                "assigned_to","due_date","priority","status"]
        d = df[cols].copy()
        d.columns = ["Action #","Inc ID","Type","Description","Assigned To","Due Date","Priority","Status"]
        d["Description"] = d["Description"].str[:80]
        st.dataframe(d, use_container_width=True, hide_index=True, height=300)

    with tabs[0]: _render_actions(actions[actions["status"].isin(["Open","In Progress","Overdue"])])
    with tabs[1]: _render_actions(overdue.sort_values("due_date"))
    with tabs[2]: _render_actions(actions[actions["status"]=="Closed"].head(50))


# ═══════════════════════════════════════════════════════════════
# PAGE 5 — LEADING INDICATORS (Observations & Near Miss)
# ═══════════════════════════════════════════════════════════════
def render_leading_indicators():
    inject_css()
    page_header("Leading Indicators Dashboard",
                "Near Miss Reporting · Safety Observations · Stop Work Authority · Reporting Culture", "📡")

    obs      = get_safety_observations()
    kpis     = get_monthly_kpis()
    summary  = get_facility_hse_summary()

    section_header("Leading Indicator KPI Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Observations", len(obs))
    with c2:
        nm = len(obs[obs["observation_type"]=="Near Miss"])
        st.metric("Near Miss Reports", nm)
    with c3:
        swa = len(obs[obs["observation_type"]=="Stop Work Authority"])
        st.metric("Stop Work Authority Used", swa, help="High = healthy safety culture")
    with c4:
        anon = len(obs[obs["is_anonymous"]==1])
        anon_pct = round(anon/max(len(obs),1)*100,1)
        st.metric("Anonymous Reports", f"{anon_pct}%",
                  help="Some anonymity expected. >50% may indicate fear of reporting.")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        section_header("Observation Type Distribution")
        obs_counts = obs["observation_type"].value_counts()
        obs_colors = {
            "Near Miss": THEME["red"],
            "Unsafe Act": THEME["amber"],
            "Unsafe Condition": THEME["orange"],
            "Good Practice": THEME["green"],
            "Safety Walk": THEME["blue"],
            "Stop Work Authority": THEME["purple"],
            "Dropped Object Potential": THEME["red"],
            "Environmental Concern": THEME["cyan"] if hasattr(THEME,"cyan") else THEME["blue"],
        }
        fig_obs = go.Figure(go.Pie(
            labels=obs_counts.index.tolist(),
            values=obs_counts.values.tolist(),
            marker_colors=[obs_colors.get(t, THEME["blue"]) for t in obs_counts.index],
            hole=0.45, textinfo="label+percent", textfont=dict(size=10),
        ))
        apply_layout(fig_obs, height=300)
        fig_obs.update_layout(showlegend=False, margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig_obs, use_container_width=True, key="p2_to_p8_chart_9")

    with col_r:
        section_header("Near Miss Ratio — Monthly (Target >5:1)")
        fig_nm = go.Figure()
        fig_nm.add_trace(go.Bar(
            x=kpis["year_month"], y=kpis["near_miss_ratio"],
            marker_color=[THEME["green"] if v >= KPI_THRESHOLDS["nmrr_green"]
                          else (THEME["amber"] if v >= KPI_THRESHOLDS["nmrr_amber"]
                          else THEME["red"]) for v in kpis["near_miss_ratio"]],
            text=[f"{v:.1f}" for v in kpis["near_miss_ratio"]],
            textposition="outside", textfont=dict(size=9),
        ))
        fig_nm.add_hline(y=KPI_THRESHOLDS["nmrr_green"], line_dash="dash",
                         line_color=THEME["green"], line_width=1.5,
                         annotation_text="Target ≥5.0",
                         annotation_font=dict(size=9))
        apply_layout(fig_nm, height=300)
        fig_nm.update_layout(yaxis_title="Near Miss : Recordable Ratio",
                             showlegend=False, margin=dict(l=55,r=60,t=20,b=60))
        st.plotly_chart(fig_nm, use_container_width=True, key="p2_to_p8_chart_10")

    section_header("Potential Severity of Near Miss Events")
    nm_obs = obs[obs["observation_type"]=="Near Miss"]
    if not nm_obs.empty:
        pot_sev = nm_obs["potential_severity"].value_counts()
        st.info(f"💡 **Interpretation:** {len(nm_obs[nm_obs['potential_severity'].isin(['Critical','High'])])} near misses had Critical or High potential severity. Each represents a potential fatality or serious injury that was avoided. These require full investigation equivalent to an actual LTI.")
        fig_pot = go.Figure(go.Bar(
            x=pot_sev.index, y=pot_sev.values,
            marker_color=[SEVERITY_COLORS.get(s, THEME["blue"]) for s in pot_sev.index],
            text=pot_sev.values, textposition="outside",
        ))
        apply_layout(fig_pot, height=250)
        fig_pot.update_layout(yaxis_title="Near Miss Count", showlegend=False,
                              margin=dict(l=50,r=20,t=20,b=50))
        st.plotly_chart(fig_pot, use_container_width=True, key="p2_to_p8_chart_11")

    section_header("Observation Register")
    obs_display = obs[["observation_number","observation_date","observation_type",
                        "work_area","potential_severity","description",
                        "followup_required","followup_complete"]].head(100).copy()
    obs_display.columns = ["Number","Date","Type","Area","Potential Severity",
                           "Description","Followup?","Complete?"]
    obs_display["Description"] = obs_display["Description"].str[:80]
    obs_display["Followup?"] = obs_display["Followup?"].map({1:"Yes",0:"No"})
    obs_display["Complete?"] = obs_display["Complete?"].map({1:"✅",0:"⏳"})
    st.dataframe(obs_display, use_container_width=True, hide_index=True, height=300)


# ═══════════════════════════════════════════════════════════════
# PAGE 6 — HSE INSPECTIONS & AUDIT
# ═══════════════════════════════════════════════════════════════
def render_inspections():
    inject_css()
    page_header("HSE Inspections & Audit Performance",
                "Inspection score trends · Finding analysis · Compliance monitoring", "🔍")

    inspections = get_hse_inspections()
    kpis        = get_monthly_kpis()

    if inspections.empty:
        st.warning("No inspection records.")
        return

    section_header("Inspection Performance Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Inspections", len(inspections))
    with c2: st.metric("Avg Score", f"{inspections['inspection_score'].mean():.1f}/100")
    with c3: st.metric("Total Findings", int(inspections["findings_count"].sum()))
    with c4: st.metric("Critical Findings", int(inspections["critical_findings"].sum()))
    with c5:
        excellent = len(inspections[inspections["overall_rating"].isin(["Excellent","Good"])])
        st.metric("Good/Excellent", f"{excellent/len(inspections)*100:.0f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    section_header("Inspection Score Trend — All Types")
    inspections["inspection_date"] = pd.to_datetime(inspections["inspection_date"])
    fig_scores = go.Figure()

    for insp_type in inspections["inspection_type"].unique():
        subset = inspections[inspections["inspection_type"]==insp_type].sort_values("inspection_date")
        if len(subset) < 2:
            continue
        fig_scores.add_trace(go.Scatter(
            x=subset["inspection_date"], y=subset["inspection_score"],
            mode="lines+markers", name=insp_type,
            line=dict(width=1.8), marker=dict(size=5),
        ))

    fig_scores.add_hline(y=80, line_dash="dash", line_color=THEME["amber"],
                         line_width=1.2, annotation_text="Min Acceptable 80",
                         annotation_font=dict(size=9))
    apply_layout(fig_scores, height=320)
    fig_scores.update_layout(yaxis=dict(range=[50,105], title="Score /100"),
                             legend=dict(orientation="h", y=1.1, x=0, font=dict(size=9)),
                             margin=dict(l=55,r=20,t=40,b=50))
    st.plotly_chart(fig_scores, use_container_width=True, key="p2_to_p8_chart_12")

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Overall Rating Distribution")
        rating_counts = inspections["overall_rating"].value_counts()
        rating_colors = {"Excellent":THEME["green"],"Good":"#27ae60","Satisfactory":THEME["blue"],
                         "Unsatisfactory":THEME["amber"],"Critical":THEME["red"]}
        fig_rat = go.Figure(go.Pie(
            labels=rating_counts.index.tolist(), values=rating_counts.values.tolist(),
            marker_colors=[rating_colors.get(r, THEME["blue"]) for r in rating_counts.index],
            hole=0.5, textinfo="label+percent",
        ))
        apply_layout(fig_rat, height=270)
        fig_rat.update_layout(showlegend=False, margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig_rat, use_container_width=True, key="p2_to_p8_chart_13")

    with col_r:
        section_header("Monthly Avg Inspection Score vs Target")
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=kpis["year_month"], y=kpis["inspection_score_avg"],
            marker_color=[THEME["green"] if v >= 85 else (THEME["amber"] if v >= 70 else THEME["red"])
                          for v in kpis["inspection_score_avg"]],
            text=[f"{v:.1f}" for v in kpis["inspection_score_avg"]],
            textposition="outside", textfont=dict(size=9),
        ))
        fig_monthly.add_hline(y=85, line_dash="dash", line_color=THEME["green"], line_width=1.5,
                              annotation_text="Target 85",
                              annotation_font=dict(size=9, color=THEME["green"]))
        apply_layout(fig_monthly, height=270)
        fig_monthly.update_layout(yaxis=dict(range=[55,105], title="Score"),
                                  showlegend=False, margin=dict(l=50,r=50,t=20,b=60))
        st.plotly_chart(fig_monthly, use_container_width=True, key="p2_to_p8_chart_14")

    section_header("Inspection Register")
    display_cols = ["inspection_number","inspection_date","inspection_type","work_area",
                    "inspector","inspection_score","findings_count","critical_findings","overall_rating"]
    disp = inspections[display_cols].copy()
    disp.columns = ["Number","Date","Type","Area","Inspector","Score","Findings","Critical","Rating"]
    disp["Date"] = disp["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(disp, use_container_width=True, hide_index=True, height=280)


# ═══════════════════════════════════════════════════════════════
# PAGE 7 — PERMIT TO WORK ANALYTICS
# ═══════════════════════════════════════════════════════════════
def render_ptw_analytics():
    inject_css()
    page_header("Permit to Work Analytics",
                "PTW compliance · Violation tracking · Hot work & confined space monitoring", "📄")

    ptw = get_ptw_records()
    if ptw.empty:
        st.warning("No PTW records.")
        return

    violations = ptw[ptw["violations_noted"] == 1]
    if not violations.empty:
        alert_banner(f"{len(violations)} PTW violation(s) recorded in 2024. Each violation represents a potential process safety event.", "warning")

    section_header("PTW Performance Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Permits", len(ptw))
    with c2:
        hot_work = len(ptw[ptw["permit_type"]=="Hot Work"])
        st.metric("Hot Work Permits", hot_work)
    with c3:
        confined = len(ptw[ptw["permit_type"]=="Confined Space Entry"])
        st.metric("Confined Space Permits", confined)
    with c4: st.metric("PTW Violations", len(violations))
    with c5:
        violation_rate = round(len(violations)/len(ptw)*100, 2)
        st.metric("Violation Rate", f"{violation_rate}%",
                  "Target: <2%", delta_color="inverse")

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Permit Type Distribution")
        type_counts = ptw["permit_type"].value_counts()
        fig_ptw = go.Figure(go.Bar(
            x=type_counts.values, y=type_counts.index,
            orientation="h", marker_color=THEME["blue"], opacity=0.8,
            text=type_counts.values, textposition="outside",
        ))
        apply_layout(fig_ptw, height=300)
        fig_ptw.update_layout(margin=dict(l=190,r=40,t=20,b=40), showlegend=False)
        st.plotly_chart(fig_ptw, use_container_width=True, key="p2_to_p8_chart_15")

    with col_r:
        section_header("PTW Violations by Type")
        if not violations.empty:
            viol_by_type = violations["permit_type"].value_counts()
            fig_viol = go.Figure(go.Bar(
                x=viol_by_type.values, y=viol_by_type.index,
                orientation="h", marker_color=THEME["red"], opacity=0.8,
                text=viol_by_type.values, textposition="outside",
            ))
            apply_layout(fig_viol, height=300)
            fig_viol.update_layout(margin=dict(l=190,r=40,t=20,b=40), showlegend=False)
            st.plotly_chart(fig_viol, use_container_width=True, key="p2_to_p8_chart_16")
        else:
            st.success("No PTW violations recorded.")

    section_header("PTW Violation Register")
    if not violations.empty:
        viol_display = violations[["permit_number","permit_date","permit_type","work_area",
                                   "issued_by","workers_on_permit","violation_description"]].copy()
        viol_display.columns = ["Permit #","Date","Type","Area","Issued By","Workers","Violation"]
        viol_display["Violation"] = viol_display["Violation"].str[:100]
        st.dataframe(viol_display, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No PTW violations in 2024 — excellent permit compliance.")


# ═══════════════════════════════════════════════════════════════
# PAGE 8 — TRAINING & COMPETENCY
# ═══════════════════════════════════════════════════════════════
def render_training_competency():
    inject_css()
    page_header("Training & Competency Management",
                "HSE training compliance · Expiry tracking · Competency gap analysis", "🎓")

    training = get_training_records()
    kpis     = get_monthly_kpis()

    if training.empty:
        st.warning("No training records.")
        return

    expired = training[training["is_expired"]==1]
    expiring_soon = training[
        (training["is_expired"]==0) &
        (pd.to_datetime(training["expiry_date"]) <=
         pd.Timestamp("2024-12-31") + pd.Timedelta(days=90))
    ]

    if len(expired) > 0:
        alert_banner(f"{len(expired)} training certificate(s) expired. Regulatory compliance risk. Review immediately.", "critical")
    if len(expiring_soon) > 0:
        alert_banner(f"{len(expiring_soon)} certificate(s) expiring within 90 days. Schedule renewals.", "warning")

    section_header("Training Compliance Summary")
    total = len(training)
    valid = len(training[training["is_expired"]==0])
    compliance = round(valid/total*100, 1)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Training Records", f"{total:,}")
    with c2: st.metric("Valid Certificates", f"{valid:,}")
    with c3: st.metric("Expired", len(expired))
    with c4: st.metric("Expiring <90 days", len(expiring_soon))
    with c5:
        color = "normal" if compliance >= KPI_THRESHOLDS["training_green"] else "inverse"
        st.metric("Compliance Rate", f"{compliance}%",
                  f"Target: {KPI_THRESHOLDS['training_green']}%", delta_color=color)

    col_l, col_r = st.columns(2)

    with col_l:
        section_header("Compliance by Course")
        course_stats = training.groupby("training_course").agg(
            total=("employee_id","count"),
            expired=("is_expired","sum"),
        ).reset_index()
        course_stats["compliance_pct"] = round(
            (1 - course_stats["expired"]/course_stats["total"]) * 100, 1
        )
        course_stats = course_stats.sort_values("compliance_pct", ascending=True).head(12)
        colors_c = [THEME["green"] if v >= 95 else (THEME["amber"] if v >= 85 else THEME["red"])
                    for v in course_stats["compliance_pct"]]
        fig_course = go.Figure(go.Bar(
            x=course_stats["compliance_pct"], y=course_stats["training_course"],
            orientation="h", marker_color=colors_c,
            text=[f"{v:.0f}%" for v in course_stats["compliance_pct"]],
            textposition="outside",
        ))
        fig_course.add_vline(x=95, line_dash="dash", line_color=THEME["green"], line_width=1.2)
        apply_layout(fig_course, height=340)
        fig_course.update_layout(xaxis=dict(range=[0,110], title="Compliance %"),
                                 margin=dict(l=210,r=50,t=20,b=40), showlegend=False)
        st.plotly_chart(fig_course, use_container_width=True, key="p2_to_p8_chart_17")

    with col_r:
        section_header("Compliance by Department")
        dept_stats = training.groupby("department").agg(
            total=("employee_id","count"),
            expired=("is_expired","sum"),
        ).reset_index()
        dept_stats["compliance_pct"] = round(
            (1 - dept_stats["expired"]/dept_stats["total"]) * 100, 1
        )
        dept_stats = dept_stats.sort_values("compliance_pct", ascending=True)
        colors_d = [THEME["green"] if v >= 95 else (THEME["amber"] if v >= 85 else THEME["red"])
                    for v in dept_stats["compliance_pct"]]
        fig_dept = go.Figure(go.Bar(
            x=dept_stats["compliance_pct"], y=dept_stats["department"],
            orientation="h", marker_color=colors_d,
            text=[f"{v:.0f}%" for v in dept_stats["compliance_pct"]],
            textposition="outside",
        ))
        fig_dept.add_vline(x=95, line_dash="dash", line_color=THEME["green"], line_width=1.2)
        apply_layout(fig_dept, height=340)
        fig_dept.update_layout(xaxis=dict(range=[0,110], title="Compliance %"),
                               margin=dict(l=190,r=50,t=20,b=40), showlegend=False)
        st.plotly_chart(fig_dept, use_container_width=True, key="p2_to_p8_chart_18")

    section_header("Expired & At-Risk Certificates")
    tabs = st.tabs(["Expired", "Expiring <90 days"])
    def _render_training(df):
        if df.empty:
            st.success("No records in this category.")
            return
        d = df[["employee_id","employee_name","department","training_course",
                 "training_date","expiry_date","is_expired"]].copy()
        d.columns = ["Emp ID","Name","Dept","Course","Trained","Expires","Expired?"]
        d["Expired?"] = d["Expired?"].map({1:"🔴 YES",0:"🟢 Valid"})
        st.dataframe(d, use_container_width=True, hide_index=True, height=300)
    with tabs[0]: _render_training(expired)
    with tabs[1]: _render_training(expiring_soon)
