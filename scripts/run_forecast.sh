#!/usr/bin/env bash
# Run GFS Wave forecast plot and regenerate frontend config.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

pick_cycle() {
    python3 -c "
import sys
sys.path.insert(0, '${ROOT}')
from plotter.core.grib_loader import pick_latest_gfswave_cycle
print(pick_latest_gfswave_cycle())
"
}

CYCLE="${CYCLE:-$(pick_cycle)}"
MAX_HOURS="${MAX_HOURS:-4}"
REGION="${REGION:-all}"

echo "[INFO] Using cycle: $CYCLE, forecast hours: $MAX_HOURS"
python3 src/plot.py --dataset gfswave --cycle "$CYCLE" --region "$REGION" --max-hours "$MAX_HOURS"
python3 scripts/generate_config.py --dataset gfswave --cycle "$CYCLE" --max-hours "$MAX_HOURS"
