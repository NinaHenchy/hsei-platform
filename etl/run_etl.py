"""
HSEI Platform — ETL Orchestrator
"""

import sys
from pathlib import Path
from datetime import datetime

from loguru import logger

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logger.add(LOG_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
           rotation="10 MB", level="DEBUG")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_connection import initialize_database, get_engine, test_connection
from etl.extractors.synthetic_data_generator import run_full_generation
from etl.loaders.db_loader import load_all_tables, verify_load


def run_etl():
    logger.info("HSEI ETL Pipeline — START")
    initialize_database()
    test_connection()
    data = run_full_generation()

    # Export CSVs
    processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    for name, df in data.items():
        df.to_csv(processed_dir / f"{name}.csv", index=False)

    engine = get_engine()
    load_all_tables(data, engine, mode="replace")
    verify_load(engine)
    logger.success("HSEI ETL Pipeline — COMPLETE")
    return data


if __name__ == "__main__":
    run_etl()
