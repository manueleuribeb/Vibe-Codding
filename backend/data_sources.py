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
    url = f"https://api.eia.gov/series/?api_key={token}&series_id={series_id}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    js = resp.json()
    data = js["series"][0]["data"]  # [[YYYYMMDD, value], ...]
    df = pd.DataFrame(data, columns=["date","price"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return df.dropna().sort_values("date").reset_index(drop=True)