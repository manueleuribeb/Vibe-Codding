# Vibe-Coding

Energia Forecast — monorepo with a FastAPI backend and Vite + React + TypeScript frontend.

Quick start

- Backend: `cd backend` && `pip install -r requirements.txt` && `uvicorn backend.main:app --reload`
- Frontend: `cd frontend` && `npm install` && `npm run dev`

From the project root you can run the backend with `npm run start-backend` or start the frontend with `npm run dev-frontend`.

API endpoints (backend)

- `POST /api/upload` — multipart form upload `file` (CSV or XLSX) with columns `date` and `price`. Optional query `horizon` (days forecast, default 7). Returns JSON with `best_method`, `mape`, `rmse`, and `series` (future dates and forecasts).
- `GET /api/online` — fetch online series and forecast. Query params: `source` (one of `yahoo|eia|xm`, default `yahoo`), `symbol` (optional), `period` (yahoo period, default `1y`), `horizon` (forecast days, default 7).

Notes:
- EIA access requires an API key set as environment variable `EIA_API_KEY` for `source=eia` (series default `PET.RWTC.D`).
# Vibe-Codding