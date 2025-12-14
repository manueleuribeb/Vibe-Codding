"""Helper entrypoint to run the backend with the project root on PYTHONPATH.

Usage:
  python start-backend.py

This imports `backend` reliably even if your current working directory doesn't
automatically put the repository root on `sys.path`.
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import uvicorn


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
