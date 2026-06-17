"""
HSEI Platform — Setup Script
"""

import sys
from pathlib import Path

for _p in [str(Path(__file__).resolve().parent.parent), "/app"]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    print("=" * 60)
    print("HSEI Platform — Initial Setup")
    print("=" * 60)

    for d in ["data/raw","data/processed","data/exports",
              "database","logs","models/artifacts"]:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {d}")

    print("\nInitialising database...")
    from database.db_connection import initialize_database, test_connection
    initialize_database()
    test_connection()
    print("  ✓ Schema created")

    print("\nRunning ETL pipeline...")
    from etl.run_etl import run_etl
    run_etl()

    print("\n" + "=" * 60)
    print("✅ HSEI Platform ready.")
    print("   Run: streamlit run dashboards/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
