import os, pandas as pd, numpy as np, requests, yfinance as yf
from typing import Optional

EIA_DEFAULT_TOKEN = os.getenv("EIA_TOKEN", "")

EIA_SERIES = {
    "wti_daily": "PET.RWTC.D",      # WTI spot diario (EIA)
    "brent_daily": "PET.RBRTE.D",   # Brent spot diario (EIA)
    "henryhub_monthly": "NG.RNGWHHD.M"  # Henry Hub spot mensual (EIA)
}

def load_from_yahoo(symbol: str, start: Optional[str], end: Optional[str], interval: str="1d") -> pd.DataFrame:
    df = yf.download(symbol, start=start, end=end, interval=interval)
    df = df.rename(columns={"Close":"price"}).reset_index()[["Date","price"]]
    df.columns = ["date","price"]
    return df

def load_from_eia(series_id: str, token: Optional[str] = None) -> pd.DataFrame:
    token = token or EIA_DEFAULT_TOKEN
    if not (series_id and token):
        raise ValueError("series_id y token EIA son requeridos (o EIA_TOKEN en entorno).")
    # API v1 series endpoint
    # Use EIA API v2 seriesid endpoint (backwards-compatible)
    url = f"https://api.eia.gov/v2/seriesid/{series_id}"
    resp = requests.get(url, params={'api_key': token}, timeout=30)
    resp.raise_for_status()
    js = resp.json()
    rows = js.get('response', {}).get('data', [])
    if not rows:
        raise ValueError("No data returned from EIA for series_id")
    df = pd.DataFrame(rows)
    # v2 rows typically have 'period' and 'value' keys
    if 'period' in df.columns and 'value' in df.columns:
        df = df.rename(columns={'period': 'date', 'value': 'price'})
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    return df.dropna().sort_values('date').reset_index(drop=True)