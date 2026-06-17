"""
Page 1 — HSE Executive Overview
Audience: HSE Manager, Operations Director, Executive Leadership
"""

import sys
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

_root = Path(__file__).resolve().parent.parent.parent
for _p in [str(_root), "/app"]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
from dashboards.data_access import (
    get_facility_hse_summary, get_monthly_kpis,
    get_incidents, get_heinrich_triangle
)
from dashboards.components.ui_components import (
    inject_css, page_header, section_header, alert_banner, apply_layout, THEME, SEVERITY_COLORS
)
from config.settings import KPI_THRESHOLDS, FACILITY_NAME


def render_hse_overview():
    inject_css()
    page_header(
        "HSE Executive Overview",
        f"{FACILITY_NAME} · Safety Performance Dashboard · 2024",
        "🛡️"
    )

    summary = get_facility_hse_summary()
    kpis    = get_monthly_kpis()
    incidents = get_incidents()

    if not summary:
        st.error("No data. Run setup_database.py first.")
        return

    # ── CRITICAL ALERTS ───────────────────────────────────────────────
    if summary["fatalities"] > 0:
        alert_banner(f"FATALITY RECORDED — {summary['fatalities']} fatality event(s) in 2024. Regulatory notification mandatory.", "critical")
    if summary["overdue_actions"] > 0:
        alert_banner(f"{summary['overdue_actions']} corrective action(s) overdue. Immediate review required.", "warning")
    if summary["trir_rag"] == "red":
        alert_banner(f"TRIR {summary['ytd_trir']:.3f} exceeds industry benchmark. Incident prevention programme review required.", "critical")

    # ── LTI FREE DAYS HERO ────────────────────────────────────────────
    lti_free = summary["lti_free_days"]
    lti_color = THEME["green"] if lti_free >= 180 else (THEME["amber"] if lti_free >= 60 else THEME["red"])
    st.markdown(f"""
    <div style="background:#ffffff;border:2px solid {lti_color};border-radius:12px;
                padding:20px 30px;text-align:center;margin-bottom:20px;">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.15em;
                    color:#4a4a6a;">LTI-Free Days — Current Streak</div>
        <div style="font-size:56px;font-weight:900;color:{lti_color};line-height:1.1;">
            {lti_free}
        </div>
        <div style="font-size:12px;color:#9a9ab0;margin-top:4px;">
            Days without a Lost Time Injury — Target: 365
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TIER 1 KPIs ────────────────────────────────────────────────────
    section_header("Safety Performance KPIs — Year to Date")
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    trir_color = "normal" if summary["trir_rag"] == "green" else "inverse"
    with c1:
        st.metric("TRIR", f"{summary['ytd_trir']:.3f}",
                  f"Target ≤{KPI_THRESHOLDS['trir_green']}",
                  delta_color=trir_color)
    with c2:
        st.metric("LTIR", f"{summary['ytd_ltir']:.3f}",
                  f"Target ≤{KPI_THRESHOLDS['ltir_green']}")
    with c3:
        st.metric("Total Incidents", summary["total_incidents"])
    with c4:
        st.metric("Near Miss Count", summary["near_miss_count"],
                  f"Ratio: {summary['near_miss_ratio']}:1 recordable")
    with c5:
        st.metric("Open Actions", summary["open_actions"],
                  f"{summary['overdue_actions']} overdue")
    with c6:
        cost = summary["total_cost_usd"]
        st.metric("Incident Cost YTD",
                  f"${cost/1e6:.2f}M" if cost >= 1e6 else f"${cost:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TRIR TREND + INCIDENT TYPE DISTRIBUTION ────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        section_header("TRIR & LTIR Monthly Trend vs Industry Benchmark")
        fig_trir = go.Figure()
        fig_trir.add_trace(go.Scatter(
            x=kpis["year_month"], y=kpis["trir"],
            name="TRIR", mode="lines+markers",
            line=dict(color=THEME["red"], width=2.5),
            marker=dict(size=7),
        ))
        fig_trir.add_trace(go.Scatter(
            x=kpis["year_month"], y=kpis["ltir"],
            name="LTIR", mode="lines+markers",
            line=dict(color=THEME["blue"], width=2),
            marker=dict(size=6),
        ))
        fig_trir.add_hline(y=KPI_THRESHOLDS["trir_green"], line_dash="dash",
                           line_color=THEME["green"], line_width=1.5,
                           annotation_text="World Class 0.30",
                           annotation_font=dict(size=9, color=THEME["green"]))
        fig_trir.add_hline(y=KPI_THRESHOLDS["trir_amber"], line_dash="dot",
                           line_color=THEME["amber"], line_width=1.2,
                           annotation_text="Industry Avg 0.80",
                           annotation_font=dict(size=9, color=THEME["amber"]))
        apply_layout(fig_trir, height=300)
        fig_trir.update_layout(
            yaxis_title="Rate per 200,000 manhours",
            legend=dict(orientation="h", y=1.1, x=0, font=dict(size=10)),
            margin=dict(l=55, r=80, t=35, b=50),
        )
        st.plotly_chart(fig_trir, use_container_width=True, key="p1_hse_overview_chart_1")

    with col_r:
        section_header("Incident Type Distribution — YTD")
        if not incidents.empty:
            type_counts = incidents["incident_type"].value_counts().head(10)
            colors_list = [SEVERITY_COLORS.get(
                incidents[incidents["incident_type"]==t]["severity"].mode().iloc[0]
                if not incidents[incidents["incident_type"]==t].empty else "Low", THEME["blue"]
            ) for t in type_counts.index]

            fig_types = go.Figure(go.Bar(
                x=type_counts.values,
                y=type_counts.index,
                orientation="h",
                marker_color=colors_list,
                text=type_counts.values,
                textposition="outside",
                textfont=dict(size=10),
            ))
            apply_layout(fig_types, height=300)
            fig_types.update_layout(
                xaxis_title="Count",
                margin=dict(l=165, r=30, t=20, b=40),
                showlegend=False,
            )
            st.plotly_chart(fig_types, use_container_width=True, key="p1_hse_overview_chart_2")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── HEINRICH TRIANGLE + MONTHLY MANHOURS ──────────────────────────
    section_header("Heinrich Safety Triangle — Monthly Leading vs Lagging Indicators")
    triangle = get_heinrich_triangle()
    if not triangle.empty:
        fig_h = go.Figure()
        bar_configs = [
            ("fatalities",    "Fatalities",   THEME["red"],    True),
            ("ltis",          "LTIs",         "#e74c3c",       True),
            ("recordables",   "Recordables",  THEME["amber"],  True),
            ("first_aids",    "First Aid",    THEME["orange"], False),
            ("near_misses",   "Near Miss",    THEME["blue"],   False),
            ("unsafe_obs",    "Unsafe Obs",   THEME["green"],  False),
        ]
        for col, name, color, primary in bar_configs:
            if col in triangle.columns:
                fig_h.add_trace(go.Bar(
                    x=triangle["month"], y=triangle[col],
                    name=name, marker_color=color, opacity=0.85,
                ))
        apply_layout(fig_h, height=320)
        fig_h.update_layout(
            barmode="stack",
            yaxis_title="Incident Count",
            legend=dict(orientation="h", y=1.08, x=0, font=dict(size=10)),
            margin=dict(l=50, r=20, t=40, b=60),
        )
        st.plotly_chart(fig_h, use_container_width=True, key="p1_hse_overview_chart_3")

    st.caption("Leading indicators (Near Miss, Unsafe Observations) are shown in cool colours. "
               "Lagging indicators (LTIs, Recordables) in warm colours. "
               "High near miss reporting relative to recordables indicates a healthy reporting culture.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PROCESS SAFETY EVENT SUMMARY ──────────────────────────────────
    section_header("API RP 754 Process Safety Event Summary")
    pse_data = incidents[incidents["api_rp754_tier"].notna()]
    if not pse_data.empty:
        tier_counts = pse_data["api_rp754_tier"].value_counts()
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        for col, tier, color in zip(
            [col_t1, col_t2, col_t3, col_t4],
            ["Tier 1","Tier 2","Tier 3","Tier 4"],
            [THEME["red"], THEME["amber"], THEME["orange"], THEME["green"]]
        ):
            count = int(tier_counts.get(tier, 0))
            with col:
                st.markdown(f"""
                <div style="background:#ffffff;border:2px solid {color};border-radius:8px;
                             padding:16px;text-align:center;">
                    <div style="font-size:10px;text-transform:uppercase;color:#4a4a6a;">{tier}</div>
                    <div style="font-size:32px;font-weight:800;color:{color};">{count}</div>
                    <div style="font-size:10px;color:#9a9ab0;">
                        {"Regulatory Reportable" if tier in ["Tier 1","Tier 2"] else "Internal Tracking"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
