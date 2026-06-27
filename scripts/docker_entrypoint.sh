#!/bin/bash
set -e
cd /app
export PYTHONPATH=/app

echo "============================================================"
echo "HSEI Platform Starting..."
echo "============================================================"

if [ ! -f "database/hsei_dev.db" ]; then
    echo "Step 1/2: Initialising database..."
    python scripts/setup_database.py
    echo "Database ready."
fi

echo "Launching Streamlit on port 8501..."
exec streamlit run dashboards/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false