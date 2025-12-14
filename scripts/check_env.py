#!/usr/bin/env python3
"""Diagnóstico simple para comprobar si Python encuentra el paquete `backend`.

Uso: `python scripts/check_env.py` desde la raíz del repositorio. El script
proporciona sugerencias en español si falta el paquete en `PYTHONPATH`.
"""
import sys
import os
from pathlib import Path
import importlib.util

print('cwd:', Path.cwd())
print('PYTHONPATH:', os.environ.get('PYTHONPATH'))

spec = importlib.util.find_spec('backend')
if spec is None:
    print('\nERROR: Python cannot find the `backend` package. Common fixes:')
    print('- Run the server from the project root and use `python start-backend.py`')
    print('- Or set `PYTHONPATH` to the project root: `export PYTHONPATH="$PWD"`')
    print('- If you are in `backend/`, run `../start-backend.py` or `./run_uvicorn.sh`')
    sys.exit(2)
else:
    print('backend package found at:', spec.origin)
    print('OK')
