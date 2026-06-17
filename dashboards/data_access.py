"""
HSEI Platform — Dashboard Data Access Layer
"""

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.db_connection import get_engine
from config.settings import KPI_THRESHOLDS, INCIDENT_COST_ESTIMATES

_engine = None

def engine():
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def sql(query: str) -> pd.DataFrame:
    try:
        return pd.read_sql(query, engine())
    except Exception:
        return pd.DataFrame()


def get_incidents(filters: dict = None) -> pd.DataFrame:
    where = "1=1"
    if filters:
        if filters.get("type"):
            types = "','".join(filters["type"])
            where += f" AND incident_type IN ('{types}')"
        if filters.get("area"):
            where += f" AND work_area = '{filters['area']}'"
        if filters.get("dept"):
            where += f" AND department = '{filters['dept']}'"
    return sql(f"SELECT * FROM incidents WHERE {where} ORDER BY incident_date DESC")


def get_monthly_kpis() -> pd.DataFrame:
    return sql("SELECT * FROM kpi_monthly_summary ORDER BY year_month")


def get_corrective_actions() -> pd.DataFrame:
    return sql("""
        SELECT ca.*, i.incident_type, i.incident_category, i.severity
        FROM corrective_actions ca
        LEFT JOIN incidents i ON ca.incident_id = i.id
        ORDER BY ca.due_date
    """)


def get_safety_observations() -> pd.DataFrame:
    return sql("SELECT * FROM safety_observations ORDER BY observation_date DESC")


def get_hse_inspections() -> pd.DataFrame:
    return sql("SELECT * FROM hse_inspections ORDER BY inspection_date DESC")


def get_ptw_records() -> pd.DataFrame:
    return sql("SELECT * FROM permit_to_work ORDER BY permit_date DESC")


def get_training_records() -> pd.DataFrame:
    return sql("SELECT * FROM training_records ORDER BY expiry_date")


def get_incident_pareto() -> pd.DataFrame:
    return sql("""
        SELECT incident_category,
               COUNT(*) AS count,
               SUM(days_lost) AS total_days_lost,
               SUM(estimated_cost_usd) AS total_cost,
               ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),1) AS pct_of_total
        FROM incidents
        GROUP BY incident_category
        ORDER BY count DESC
    """)


def get_heinrich_triangle() -> pd.DataFrame:
    return sql("""
        SELECT
            strftime('%Y-%m', incident_date) AS month,
            COUNT(CASE WHEN incident_type='Fatality' THEN 1 END)             AS fatalities,
            COUNT(CASE WHEN incident_type='Lost Time Injury' THEN 1 END)     AS ltis,
            COUNT(CASE WHEN incident_type IN ('Restricted Work Case','Medical Treatment Case') THEN 1 END) AS recordables,
            COUNT(CASE WHEN incident_type='First Aid Case' THEN 1 END)       AS first_aids,
            COUNT(CASE WHEN incident_type='Near Miss' THEN 1 END)            AS near_misses,
            COUNT(CASE WHEN incident_type IN ('Unsafe Act','Unsafe Condition') THEN 1 END) AS unsafe_obs
        FROM incidents
        GROUP BY strftime('%Y-%m', incident_date)
        ORDER BY month
    """)


def get_open_actions() -> pd.DataFrame:
    return sql("""
        SELECT ca.*, i.incident_type, i.severity,
               CAST(julianday('now') - julianday(ca.due_date) AS INTEGER) AS days_overdue
        FROM corrective_actions ca
        LEFT JOIN incidents i ON ca.incident_id = i.id
        WHERE ca.status IN ('Open','In Progress','Overdue')
        ORDER BY ca.priority, ca.due_date
    """)


def get_facility_hse_summary() -> dict:
    incidents  = get_incidents()
    kpis       = get_monthly_kpis()
    actions    = get_corrective_actions()
    training   = get_training_records()

    if incidents.empty or kpis.empty:
        return {}

    ytd_trir  = kpis["trir"].mean()
    ytd_ltir  = kpis["ltir"].mean()
    total_inc = len(incidents)
    ltis      = len(incidents[incidents["incident_type"] == "Lost Time Injury"])
    near_miss = len(incidents[incidents["incident_type"] == "Near Miss"])
    pse       = len(incidents[incidents["incident_type"] == "Process Safety Event"])
    total_cost= incidents["estimated_cost_usd"].sum()
    open_act  = len(actions[actions["status"].isin(["Open","In Progress","Overdue"])])
    overdue   = len(actions[actions["status"] == "Overdue"])
    lti_free  = int(kpis["cumulative_lti_free_days"].iloc[-1]) if not kpis.empty else 0

    expired_training = len(training[training["is_expired"] == 1])
    total_training   = len(training)
    training_comp    = round((1 - expired_training / max(total_training, 1)) * 100, 1)

    nm_ratio  = round(near_miss / max(ltis + len(incidents[incidents["incident_type"].isin(["Restricted Work Case","Medical Treatment Case"])]), 1), 1)

    return {
        "ytd_trir":              round(ytd_trir, 3),
        "ytd_ltir":              round(ytd_ltir, 3),
        "total_incidents":       total_inc,
        "lti_count":             ltis,
        "near_miss_count":       near_miss,
        "pse_count":             pse,
        "total_cost_usd":        round(total_cost, 0),
        "open_actions":          open_act,
        "overdue_actions":       overdue,
        "lti_free_days":         lti_free,
        "training_compliance":   training_comp,
        "near_miss_ratio":       nm_ratio,
        "fatalities":            len(incidents[incidents["incident_type"] == "Fatality"]),
        "trir_rag":              "green" if ytd_trir <= KPI_THRESHOLDS["trir_green"] else
                                 "amber" if ytd_trir <= KPI_THRESHOLDS["trir_amber"] else "red",
        "ltir_rag":              "green" if ytd_ltir <= KPI_THRESHOLDS["ltir_green"] else
                                 "amber" if ytd_ltir <= KPI_THRESHOLDS["ltir_amber"] else "red",
    }
