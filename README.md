# Vibe-Coding

Energia Forecast — monorepo with a FastAPI backend and Vite + React + TypeScript frontend.

Quick start

- Backend: `cd backend` && `pip install -r requirements.txt` && `uvicorn backend.main:app --reload`
- Frontend: `cd frontend` && `npm install` && `npm run dev`

From the project root you can run the backend with `npm run start-backend` or start the frontend with `npm run dev-frontend`.

Installation

- Backend (Python):

	```bash
	cd backend
	python -m pip install -r requirements.txt
	# run server
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
	```

- Frontend (Node):

	```bash
	cd frontend
	npm install
	npm run dev
	```

EIA API token

- To use `source=eia` with `/api/online`, get a free API key from the U.S. Energy Information Administration (EIA): https://www.eia.gov/opendata/register.php
- Set the key in your environment before running the backend (quick):

  ```bash
  EIA_API_KEY="your_api_key_here" uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
  ```

- Or create a `.env` file in the project root with your key (development):

  ```bash
  # .env
  EIA_API_KEY=your_api_key_here
  ```

  The backend will automatically load `.env` when starting in development.

Running tests

```bash
python -m pip install -r backend/requirements.txt
pytest -q backend/tests
```

UI improvements and usage

- The frontend now includes:
	- A clean layout and CSS styles in `frontend/src/index.css`.
	- Preset quick-buttons for WTI (CL=F), Brent (BZ=F) and Henry Hub (NG=F).
	- A method selector (Auto/Naive/Moving average/EWMA) and a slider to choose horizon.
	- Forecast chart using Recharts (prepared data hook in `frontend/src/hooks/useForecastData` and chart component `ForecastChart`).

Evidence (quick checks)

- Start backend and frontend then visit `http://localhost:5173/`.
- Try online forecast for Brent from the UI (press "Online source" → Preset "Brent" → "Fetch & Forecast").
- Or curl directly to the API:

```bash
curl 'http://127.0.0.1:8000/api/online?source=yahoo&symbol=BZ=F&period=1mo'
```

Example output snippet:

```json
{
	"best_method": "moving_average",
	"mape": 1.72,
	"rmse": 1.13,
	"series": [{"date":"2025-12-13","forecast":58.62}, ...]
}
```

Notes on EIA

- If using `source=eia`, ensure `EIA_API_KEY` is set; you can get one at https://www.eia.gov/opendata/register.php.
- Example EIA call (replace `PET.RWTC.D` with another series id if needed):

```bash
curl "http://127.0.0.1:8000/api/online?source=eia&symbol=PET.RWTC.D"
```

API endpoints (backend)

- `POST /api/upload` — multipart form upload `file` (CSV or XLSX) with columns `date` and `price`. Optional query `horizon` (days forecast, default 7). Returns JSON with `best_method`, `mape`, `rmse`, and `series` (future dates and forecasts).
- `GET /api/online` — fetch online series and forecast. Query params: `source` (one of `yahoo|eia|xm`, default `yahoo`), `symbol` (optional), `period` (yahoo period, default `1y`), `horizon` (forecast days, default 7).

Notes:
- EIA access requires an API key set as environment variable `EIA_API_KEY` for `source=eia` (series default `PET.RWTC.D`).
# Vibe-Codding