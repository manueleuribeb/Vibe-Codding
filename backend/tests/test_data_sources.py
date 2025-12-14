import pytest
import requests
import sys
import pathlib

# ensure project root is on sys.path so `backend` package can be imported when running pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from backend.data_sources import load_from_eia


class DummyResp:
    def __init__(self, js=None, status_ok=True, text=''):
        self._js = js or {}
        self.status_ok = status_ok
        self.text = text

    def raise_for_status(self):
        if not self.status_ok:
            raise requests.HTTPError('HTTP error')

    def json(self):
        return self._js


def test_load_from_eia_success(monkeypatch):
    js = {'response': {'data': [{'period': '2025-12-01', 'value': '50'}]}}
    monkeypatch.setattr('requests.get', lambda *a, **k: DummyResp(js=js))
    df = load_from_eia('PET.RWTC.D', token='KEY')
    assert not df.empty
    assert 'date' in df.columns and 'price' in df.columns
    assert float(df['price'].iloc[0]) == 50.0


def test_load_from_eia_no_data(monkeypatch):
    js = {}
    monkeypatch.setattr('requests.get', lambda *a, **k: DummyResp(js=js))
    with pytest.raises(ValueError) as e:
        load_from_eia('PET.RWTC.D', token='KEY')
    assert 'No data returned' in str(e.value)


def test_load_from_eia_http_error(monkeypatch):
    js = {'error': 'invalid key'}
    monkeypatch.setattr('requests.get', lambda *a, **k: DummyResp(js=js, status_ok=False, text='invalid'))
    with pytest.raises(requests.HTTPError):
        load_from_eia('PET.RWTC.D', token='KEY')
