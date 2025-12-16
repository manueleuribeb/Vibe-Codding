#!/usr/bin/env bash
# Simple, robust start script for the FastApi backend.
# Usage: ./start.sh
set -euo pipefail

#Detect root (this script lives at repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensuere backend exists
if [ ! -d "backend" ]; then
  echo "[ERROR] No se encuentra la carpeta 'backend' en el directorio actual: $SCRIPT_DIR" >&2
  exit 1
fi

# Install dependencies from backend/requirements.txt
if [ -f "backend/requirements.txt" ]; then
  echo "[INFO] Instalando dependencias desde backend/requirements.txt..."
  pip install -r backend/requirements.txt
else
  echo "[WARNING] No se encontró backend/requirements.txt. Omitiendo instalación de dependencias."
fi

#Run uvicorn using import path from repo root
echo "[INFO] Iniciando el servidor en http://127.0.0.1:8000 (reload activo)"
exec uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000