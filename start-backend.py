"""Punto de entrada para arrancar el backend con la raíz del repo en PYTHONPATH.

Uso recomendado: `python start-backend.py` desde la raíz del repositorio.

Esto asegura que el paquete `backend` sea importable aunque el working
directory no esté en `PYTHONPATH` (evita `ModuleNotFoundError`).
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import uvicorn


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
