"""API backend para Energia Forecast.

Este módulo expone endpoints para obtener series de precios desde Yahoo o EIA,
aceptar uploads de CSV/XLSX con columnas `date` y `price`, evaluar métodos de
forecasting simples (naive, moving_average, ewm) y devolver métricas y una
serie de pronóstico para los siguientes `horizon` días.

Notas:
- Carga variables de entorno desde `.env` en desarrollo (usa `python-dotenv`).
- Para usar EIA, defina `EIA_API_KEY` en el entorno o en Codespaces secrets.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Form
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (conveniencia en desarrollo)
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import io
import os
import math
import requests
from typing import List, Tuple, Dict
from .data_sources import load_from_eia

app = FastAPI(title="energia-forecast backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
def _startup_checks():
    # Log whether the EIA key is present (do not log the key itself)
    key_present = bool(os.getenv('EIA_API_KEY') or os.getenv('EIA_TOKEN'))
    import logging
    logging.getLogger('uvicorn.info').info(f'EIA key present: {key_present}')


@app.get("/api/price")
def get_price(ticker: str = "AAPL", period: str = "5d"):
    """Devuelve el último precio de cierre para un `ticker` usando `yfinance`.

    Parámetros:
    - `ticker`: símbolo a consultar (ej. `AAPL`, `CL=F`).
    - `period`: periodo aceptado por yfinance (ej. `5d`, `1y`).

    Respuesta JSON: `{"ticker": <TICKER>, "close": <float>}` o HTTP 404/500 en errores.
    """
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data for ticker")
        last_close = float(df["Close"].iloc[-1])
        return {"ticker": ticker.upper(), "close": last_close}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _ensure_series(df: pd.DataFrame) -> pd.Series:
    """Normaliza un `DataFrame` entrante y devuelve una `Series` indexada por fecha.

    El `DataFrame` debe contener una columna `date` y `price` (o `close`). Se
    convierten los tipos y se ordenan por fecha. Lanza `HTTPException(400)` si
    no hay datos válidos.
    """
    # Accept 'price' or 'close' column names
    lower_cols = {c.lower(): c for c in df.columns}
    if 'date' in lower_cols:
        df = df.rename(columns={lower_cols['date']: 'date'})
    if 'price' in lower_cols:
        price_col = lower_cols['price']
    elif 'close' in lower_cols:
        price_col = lower_cols['close']
    else:
        raise HTTPException(status_code=400, detail="File must contain 'date' and 'price' (or 'close') columns")

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    s = pd.Series(df[price_col].values, index=df['date']).astype(float)
    s = s.dropna()
    if s.empty:
        raise HTTPException(status_code=400, detail="No valid price data found")
    return s


def _split_train_test(s: pd.Series, test_size: int = 14) -> Tuple[pd.Series, pd.Series]:
    """Divide la serie en train/test para evaluación.

    Usa `test_size` pero ajusta para que el tamaño mínimo sea razonable. Lanza
    `HTTPException(400)` si no hay suficientes puntos.
    """
    if len(s) < 8:
        raise HTTPException(status_code=400, detail="Not enough data points; need at least 8")
    test_size = min(test_size, max(1, len(s) // 4))
    train = s.iloc[:-test_size]
    test = s.iloc[-test_size:]
    return train, test


import numpy as np

def _mape(y_true: pd.Series, y_pred: pd.Series) -> float:
    y_true_v = np.asarray(y_true)
    y_pred_v = np.asarray(y_pred)
    if y_true_v.size != y_pred_v.size:
        # fallback: compare last n elements
        n = min(y_true_v.size, y_pred_v.size)
        y_true_v = y_true_v[-n:]
        y_pred_v = y_pred_v[-n:]
    eps = 1e-8
    denom = np.where(y_true_v == 0, eps, y_true_v)
    mape = np.mean(np.abs((y_true_v - y_pred_v) / denom)) * 100
    return float(mape)


def _rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    y_true_v = np.asarray(y_true)
    y_pred_v = np.asarray(y_pred)
    if y_true_v.size != y_pred_v.size:
        n = min(y_true_v.size, y_pred_v.size)
        y_true_v = y_true_v[-n:]
        y_pred_v = y_pred_v[-n:]
    return float(np.sqrt(np.mean((y_true_v - y_pred_v) ** 2)))


def _forecast_naive(train: pd.Series, horizon: int) -> pd.Series:
    """Pronóstico naive: repite el último valor observado para el `horizon`."""
    last = float(train.iloc[-1])
    return pd.Series([last] * horizon)


def _forecast_ma(train: pd.Series, horizon: int, window: int = 7) -> pd.Series:
    """Promedio móvil simple: calcula la media de las últimas `window` observaciones
    y la repite `horizon` veces."""
    window = min(window, len(train))
    val = float(train.iloc[-window:].mean())
    return pd.Series([val] * horizon)


def _forecast_ewm(train: pd.Series, horizon: int, alpha: float = 0.2) -> pd.Series:
    """Promedio exponencialmente ponderado (EWMA) aplicado a la serie de entrenamiento
    y repetición del último valor calculado."""
    s = train.ewm(alpha=alpha).mean()
    val = float(s.iloc[-1])
    return pd.Series([val] * horizon)


def evaluate_methods(s: pd.Series, horizon: int = 7, method: str | None = None) -> Dict:
    """Evaluate available forecasting methods and optionally force a specific method.

    If `method` is provided and valid, evaluate only that method and return its metrics and forecast.
    Otherwise select the best by MAPE (fallback RMSE) among implemented methods.
    """
    """Evalúa métodos disponibles y retorna métricas y pronóstico futuro.

    Si `method` es especificado, se evalúa solo ese método (y se devuelve su
    pronóstico). Si no, se selecciona el mejor por MAPE (con RMSE como tie-breaker).

    Retorna diccionario con `best_method`, `mape`, `rmse` y `series` (lista de
    objetos `{date, forecast}`).
    """
    train, test = _split_train_test(s, test_size=min(14, len(s) // 4))
    methods = {
        'naive': _forecast_naive,
        'moving_average': _forecast_ma,
        'ewm': _forecast_ewm,
    }

    results = {}
    for name, fn in methods.items():
        pred_test = fn(train, len(test))
        mape = _mape(test, pred_test)
        rmse = _rmse(test, pred_test)
        results[name] = {'mape': mape, 'rmse': rmse, 'pred_test': pred_test}

    chosen_name = None
    if method:
        method = method.lower()
        if method not in methods:
            raise HTTPException(status_code=400, detail=f'Unknown method {method}')
        chosen_name = method
        chosen_metrics = results[method]
    else:
        # choose best by mape, fallback to rmse
        best = min(results.items(), key=lambda kv: (kv[1]['mape'], kv[1]['rmse']))
        chosen_name = best[0]
        chosen_metrics = best[1]

    # forecast future using chosen method applied to full series (train+test)
    future = methods[chosen_name](pd.concat([train, test]), horizon)

    last_date = s.index[-1]
    dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq='D')

    series = [{'date': d.strftime('%Y-%m-%d'), 'forecast': float(v)} for d, v in zip(dates, future)]

    return {
        'best_method': chosen_name,
        'mape': round(float(chosen_metrics['mape']), 4),
        'rmse': round(float(chosen_metrics['rmse']), 4),
        'series': series,
    }


@app.post('/api/upload')
async def upload_file(file: UploadFile = File(...), horizon: int = Query(7, ge=1, le=365), method: str | None = Form(None)):
    """Upload CSV or XLSX file containing `date` and `price` columns."""
    try:
        contents = await file.read()
        if file.filename.lower().endswith('.csv') or file.content_type == 'text/csv':
            df = pd.read_csv(io.BytesIO(contents))
        else:
            # try excel
            df = pd.read_excel(io.BytesIO(contents))
        s = _ensure_series(df)
        res = evaluate_methods(s, horizon=horizon, method=method)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/online')
def online(source: str = Query('yahoo', pattern='^(yahoo|eia|xm)$'), symbol: str | None = None, period: str = '1y', horizon: int = Query(7, ge=1, le=365), method: str | None = Query(None)):
    """Fetch series online from `source` (yahoo|eia|xm) and run forecasting evaluation.

    - yahoo: uses yfinance, default symbol `CL=F` (crude oil futures)
    - eia: uses series id `PET.RWTC.D` by default; requires `EIA_API_KEY` env var
    - xm: alias to yfinance with default symbol `XM` (pass `symbol` to override)
    """
    try:
        src = source.lower()
        if src == 'yahoo':
            # support friendly symbol names
            if symbol and symbol.lower() == 'brent':
                sym = 'BZ=F'
            elif symbol and symbol.lower() == 'henry':
                sym = 'NG=F'
            else:
                sym = symbol or 'CL=F'
            t = yf.Ticker(sym)
            df = t.history(period=period)
            if df.empty:
                raise HTTPException(status_code=404, detail=f'No data for {sym} on Yahoo')
            df = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'date', 'Close': 'price'})
        elif src == 'eia':
            series_id = symbol or 'PET.RWTC.D'
            api_key = os.getenv('EIA_API_KEY') or os.getenv('EIA_TOKEN')
            try:
                df = load_from_eia(series_id, token=api_key)
            except ValueError as e:
                # data missing or unexpected format
                raise HTTPException(status_code=404, detail=str(e))
            except requests.HTTPError as e:
                raise HTTPException(status_code=502, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        elif src == 'xm':
            # xm maps to Exxon Mobil ticker XOM by default
            sym = symbol or 'XOM'
            t = yf.Ticker(sym)
            df = t.history(period=period)
            if df.empty:
                raise HTTPException(status_code=404, detail=f'No data for {sym} on Yahoo (xm)')
            df = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'date', 'Close': 'price'})
        else:
            raise HTTPException(status_code=400, detail='Unknown source')

        s = _ensure_series(df)
        res = evaluate_methods(s, horizon=horizon, method=method)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/eia_status')
def eia_status():
    """Check whether an EIA API key is available in the environment.

    Returns a JSON object with `eia_key_present: true|false` so the UI
    (or operator) can quickly detect missing tokens.
    """
    key = os.getenv('EIA_API_KEY') or os.getenv('EIA_TOKEN')
    return {'eia_key_present': bool(key)}
