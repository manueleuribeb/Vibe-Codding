"""Cargadores de datos para distintas fuentes.

Contiene helpers para descargar series desde Yahoo (`yfinance`) y desde la
API de la EIA (v2). Las funciones devuelven `DataFrame` con columnas `date` y
`price` ya convertidas y ordenadas.
"""

import os, pandas as pd, numpy as np, requests, yfinance as yf
from typing import Optional

# Soporta `EIA_API_KEY` como nombre de variable en entorno (o `EIA_TOKEN`)
EIA_DEFAULT_TOKEN = os.getenv("EIA_API_KEY") or os.getenv("EIA_TOKEN", "")

EIA_SERIES = {
    "wti_daily": "PET.RWTC.D",      # WTI spot diario (EIA)
    "brent_daily": "PET.RBRTE.D",   # Brent spot diario (EIA)
    "henryhub_monthly": "NG.RNGWHHD.M"  # Henry Hub spot mensual (EIA)
}

def load_from_yahoo(symbol: str, start: Optional[str], end: Optional[str], interval: str="1d") -> pd.DataFrame:
    """Descarga una serie desde Yahoo (usando `yfinance`) y devuelve
    `DataFrame(date, price)`.

    Parámetros: `symbol` (ej. `CL=F`), `start`, `end` (fechas opcionales) y `interval`.
    """
    df = yf.download(symbol, start=start, end=end, interval=interval)
    df = df.rename(columns={"Close":"price"}).reset_index()[["Date","price"]]
    df.columns = ["date","price"]
    return df

def load_from_eia(series_id: str, token: Optional[str] = None) -> pd.DataFrame:
    """Carga datos desde la API v2 de EIA para `series_id`.

    Requiere `token` (o la variable de entorno `EIA_API_KEY`). Devuelve un
    `DataFrame` con `date` (convertida a datetime) y `price` (numérico). Lanza
    `ValueError` si la respuesta no contiene datos.
    """
    token = token or EIA_DEFAULT_TOKEN
    if not (series_id and token):
        raise ValueError("series_id y token EIA son requeridos (o EIA_TOKEN en entorno).")
    # Detect common user mistakes: passing a Yahoo ticker (eg 'CL=F') to the EIA loader
    if '=' in series_id:
        raise ValueError(f"Invalid series_id: looks like a ticker '{series_id}'. EIA expects a series id like 'PET.RWTC.D'.")
    # API v1 series endpoint
    # Use EIA API v2 seriesid endpoint (backwards-compatible)
    url = f"https://api.eia.gov/v2/seriesid/{series_id}"
    resp = requests.get(url, params={'api_key': token}, timeout=30)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # include response content if available para depuración
        txt = ''
        try:
            txt = resp.json()
        except Exception:
            txt = resp.text
        raise requests.HTTPError(f"EIA HTTP error: {e} - {txt}")

    js = resp.json()
    # La API v2 suele incluir `response.data`; soportamos también otras formas
    rows = js.get('response', {}).get('data', []) or js.get('data') or js.get('series')
    if not rows:
        # intentar incluir cualquier mensaje de error que vuelva EIA
        err_msg = js.get('error') or js.get('message') or js
        raise ValueError(f"No data returned from EIA for series_id: {err_msg}")
    df = pd.DataFrame(rows)
    # v2 rows typically have 'period' and 'value' keys
    if 'period' in df.columns and 'value' in df.columns:
        df = df.rename(columns={'period': 'date', 'value': 'price'})
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    return df.dropna().sort_values('date').reset_index(drop=True)