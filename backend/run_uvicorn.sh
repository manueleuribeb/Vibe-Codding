#!/usr/bin/env bash
# Run this script from the `backend/` directory to start uvicorn with the
# repository root added to PYTHONPATH so `backend` can be imported reliably.

set -euo pipefail

ROOT_DIR="$(pwd)/.."
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

exec python ../start-backend.py
