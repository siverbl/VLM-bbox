#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${VENV_DIR:-.venv}"
CORES="${BBOX_CPU_CORES:-2-5}"

source "${VENV_DIR}/bin/activate"
exec taskset -c "${CORES}" uvicorn app.server:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop --http httptools
