
#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

mkdir -p logs

source "$PROJECT_DIR/venv/bin/activate"

# Prevent overlapping ETL runs
exec 9>"$PROJECT_DIR/.etl.lock"

if ! flock -n 9; then
    echo "Another ETL process is running"
    exit 1
fi

PIPELINE="${1:-}"

case "$PIPELINE" in
    incremental)
        python -m incremental_pipeline
        ;;
    stats)
        python -m stats_refresh_pipeline --limit 0
        ;;
    *)
        echo "Usage: $0 {incremental|stats}"
        exit 2
        ;;
esac
