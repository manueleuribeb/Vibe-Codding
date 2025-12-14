import sys
import pathlib

# ensure project root is on sys.path so `backend` package can be imported
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import os
from fastapi.testclient import TestClient
from backend.main import app


def test_eia_status_present(monkeypatch):
    monkeypatch.setenv('EIA_API_KEY', 'TESTKEY')
    client = TestClient(app)
    r = client.get('/api/eia_status')
    assert r.status_code == 200
    assert r.json().get('eia_key_present') is True


def test_eia_status_missing(monkeypatch):
    monkeypatch.delenv('EIA_API_KEY', raising=False)
    monkeypatch.delenv('EIA_TOKEN', raising=False)
    client = TestClient(app)
    r = client.get('/api/eia_status')
    assert r.status_code == 200
    assert r.json().get('eia_key_present') is False
