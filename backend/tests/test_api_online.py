import sys
import pathlib

# ensure project root is on sys.path so `backend` package can be imported
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from backend.main import app


def test_online_eia_rejects_ticker():
    client = TestClient(app)
    r = client.get('/api/online?source=eia&symbol=CL=F')
    assert r.status_code == 400
    assert 'ticker' in r.json().get('detail', '').lower()
