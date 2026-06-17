"""
HSEI Platform — Database Connection Manager
"""

import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, event, text
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import SQLITE_DB_PATH, DB_TYPE


def get_engine():
    engine = create_engine(
        f"sqlite:///{SQLITE_DB_PATH}",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_pragmas(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA cache_size=-32000")
        cursor.close()

    return engine


def initialize_database():
    schema_path = Path(__file__).parent / "schemas" / "hsei_schema.sql"
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        sql = schema_path.read_text()
        lines = [l for l in sql.splitlines() if not l.strip().startswith("--")]
        statements = [s.strip() for s in "\n".join(lines).split(";") if s.strip()]
        for stmt in statements:
            try:
                conn.execute(stmt)
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"Schema: {e}")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.commit()
        logger.success("HSEI database schema initialised.")
    finally:
        conn.close()
    return get_engine()


def test_connection():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.success("Database connection OK.")
    return True
