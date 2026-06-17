#!/bin/bash
set -e
echo "HSEI Platform starting..."
cd /app
export PYTHONPATH=/app

if [ ! -f "database/hsei_dev.db" ]; then
    echo "Initialising database..."
    python scripts/setup_database.py
fi

echo "Launching Streamlit..."
exec streamlit run dashboards/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
