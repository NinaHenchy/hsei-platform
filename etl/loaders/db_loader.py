"""
HSEI Platform — Database Loader
"""

import sys
import sqlite3
from pathlib import Path

import pandas as pd
from loguru import logger
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from database.db_connection import get_engine
from config.settings import SQLITE_DB_PATH

TABLE_LOAD_ORDER = [
    "incidents",
    "corrective_actions",
    "safety_observations",
    "hse_inspections",
    "permit_to_work",
    "training_records",
    "kpi_monthly_summary",
]


def _truncate_all():
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        for t in reversed(TABLE_LOAD_ORDER):
            conn.execute(f"DELETE FROM {t}")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        logger.info("  All tables truncated.")
    finally:
        conn.close()


def load_all_tables(datasets: dict, engine=None, mode: str = "replace") -> dict:
    if engine is None:
        engine = get_engine()
    if mode == "replace":
        _truncate_all()
        mode = "append"
    summary = {}
    for table in TABLE_LOAD_ORDER:
        if table in datasets and not datasets[table].empty:
            rows = len(datasets[table])
            datasets[table].to_sql(table, con=engine, if_exists=mode,
                                   index=False, chunksize=500, method="multi")
            logger.success(f"  Loaded {table}: {rows:,} rows")
            summary[table] = rows
    return summary


def verify_load(engine=None) -> pd.DataFrame:
    if engine is None:
        engine = get_engine()
    rows = []
    with engine.connect() as conn:
        for t in TABLE_LOAD_ORDER:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            rows.append({"table": t, "row_count": count})
            logger.success(f"  {t}: {count:,} rows")
    return pd.DataFrame(rows)
