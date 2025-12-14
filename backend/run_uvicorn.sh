#!/usr/bin/env bash
# Ejecuta este script desde el directorio `backend/` para arrancar uvicorn.
# El script delega en `start-backend.py` que se asegura de que la raíz del
# repositorio esté en `PYTHONPATH`, evitando `ModuleNotFoundError`.

set -euo pipefail

ROOT_DIR="$(pwd)/.."
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

exec python ../start-backend.py
