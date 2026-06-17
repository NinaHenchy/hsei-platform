"""
HSEI Platform — Test Suite
Run: pytest tests/test_hsei.py -v
"""

import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(scope="session")
def engine():
    from database.db_connection import get_engine
    return get_engine()


@pytest.fixture(scope="session")
def incidents(engine):
    return pd.read_sql("SELECT * FROM incidents", engine)


@pytest.fixture(scope="session")
def kpis(engine):
    return pd.read_sql("SELECT * FROM kpi_monthly_summary", engine)


@pytest.fixture(scope="session")
def actions(engine):
    return pd.read_sql("SELECT * FROM corrective_actions", engine)


@pytest.fixture(scope="session")
def training(engine):
    return pd.read_sql("SELECT * FROM training_records", engine)


class TestDatabase:
    def test_connection(self, engine):
        from sqlalchemy import text
        with engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1

    def test_all_tables_populated(self, engine):
        from sqlalchemy import text
        tables = ["incidents","corrective_actions","safety_observations",
                  "hse_inspections","permit_to_work","training_records","kpi_monthly_summary"]
        with engine.connect() as conn:
            for t in tables:
                r = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                assert r > 0, f"{t} is empty"

    def test_incident_count_realistic(self, incidents):
        assert 100 <= len(incidents) <= 500, f"Incident count {len(incidents)} outside realistic range"

    def test_kpi_covers_12_months(self, kpis):
        assert len(kpis) == 12, f"Expected 12 monthly KPI records, got {len(kpis)}"


class TestIncidents:
    VALID_SEVERITIES = {"Critical","High","Medium","Low","Negligible"}
    VALID_EMP_TYPES  = {"Direct","Contractor","Visitor","Unknown"}

    def test_severity_values_valid(self, incidents):
        actual = set(incidents["severity"].unique())
        assert actual.issubset(self.VALID_SEVERITIES)

    def test_incident_numbers_unique(self, incidents):
        assert incidents["incident_number"].nunique() == len(incidents)

    def test_days_lost_non_negative(self, incidents):
        assert (incidents["days_lost"] >= 0).all()

    def test_cost_non_negative(self, incidents):
        assert (incidents["estimated_cost_usd"] >= 0).all()

    def test_lti_has_days_lost(self, incidents):
        ltis = incidents[incidents["incident_type"] == "Lost Time Injury"]
        if len(ltis) > 0:
            assert (ltis["days_lost"] > 0).all(), "LTIs must have days lost > 0"

    def test_api_tier_values_valid(self, incidents):
        valid_tiers = {"Tier 1","Tier 2","Tier 3","Tier 4", None}
        pse = incidents[incidents["api_rp754_tier"].notna()]
        actual = set(pse["api_rp754_tier"].unique())
        assert actual.issubset({"Tier 1","Tier 2","Tier 3","Tier 4"})

    def test_heinrich_triangle_ratio(self, incidents):
        recordables = len(incidents[incidents["incident_type"].isin(
            ["Lost Time Injury","Restricted Work Case","Medical Treatment Case"])])
        near_misses = len(incidents[incidents["incident_type"] == "Near Miss"])
        if recordables > 0:
            ratio = near_misses / recordables
            assert ratio >= 1.0, f"Near miss ratio {ratio:.1f} too low — reporting culture concern"


class TestKPIs:
    def test_trir_non_negative(self, kpis):
        assert (kpis["trir"] >= 0).all()

    def test_ltir_non_negative(self, kpis):
        assert (kpis["ltir"] >= 0).all()

    def test_ltir_lte_trir(self, kpis):
        assert (kpis["ltir"] <= kpis["trir"] + 0.001).all(), \
            "LTIR cannot exceed TRIR"

    def test_manhours_positive(self, kpis):
        assert (kpis["total_manhours"] > 0).all()

    def test_near_miss_ratio_computed(self, kpis):
        assert "near_miss_ratio" in kpis.columns
        assert kpis["near_miss_ratio"].notna().all()

    def test_trir_realistic_for_oilgas(self, kpis):
        avg_trir = kpis["trir"].mean()
        assert avg_trir < 3.0, f"Average TRIR {avg_trir:.3f} unrealistically high for O&G"


class TestCorrectiveActions:
    VALID_STATUSES = {"Open","In Progress","Overdue","Closed","Cancelled"}

    def test_status_values_valid(self, actions):
        actual = set(actions["status"].unique())
        assert actual.issubset(self.VALID_STATUSES)

    def test_action_numbers_unique(self, actions):
        assert actions["action_number"].nunique() == len(actions)

    def test_closeout_rate_acceptable(self, actions):
        closed = len(actions[actions["status"] == "Closed"])
        rate = closed / len(actions) * 100
        assert rate >= 50, f"Close-out rate {rate:.1f}% critically low"


class TestTraining:
    def test_all_employees_have_training(self, training):
        assert len(training) > 0

    def test_passed_column_binary(self, training):
        assert set(training["passed"].unique()).issubset({0, 1})

    def test_expired_column_binary(self, training):
        assert set(training["is_expired"].unique()).issubset({0, 1})

    def test_some_expired_realistic(self, training):
        expired_pct = training["is_expired"].mean() * 100
        assert expired_pct < 85, f"Expired training {expired_pct:.1f}% unrealistically high"


class TestDataAccess:
    def test_get_incidents(self):
        from dashboards.data_access import get_incidents
        df = get_incidents()
        assert len(df) > 0

    def test_get_monthly_kpis(self):
        from dashboards.data_access import get_monthly_kpis
        df = get_monthly_kpis()
        assert len(df) == 12

    def test_get_facility_summary(self):
        from dashboards.data_access import get_facility_hse_summary
        s = get_facility_hse_summary()
        required = ["ytd_trir","ytd_ltir","total_incidents","lti_count",
                    "near_miss_count","total_cost_usd","lti_free_days"]
        for k in required:
            assert k in s, f"Missing key: {k}"

    def test_get_open_actions(self):
        from dashboards.data_access import get_open_actions
        df = get_open_actions()
        assert "action_number" in df.columns

    def test_get_incident_pareto(self):
        from dashboards.data_access import get_incident_pareto
        df = get_incident_pareto()
        assert len(df) > 0
        assert "incident_category" in df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
