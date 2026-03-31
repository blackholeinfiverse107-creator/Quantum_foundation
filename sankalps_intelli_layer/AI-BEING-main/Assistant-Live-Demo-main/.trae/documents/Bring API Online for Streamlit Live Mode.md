## Goal
Get the API running locally and reconnect the Streamlit dashboard so the sidebar shows “API Connected” instead of “API Offline — Simulated Mode”.

## Diagnose
- Confirm which API the dashboard expects: `Assistant-Live-Bridge/demo_streamlit_app.py` defaults `API_BASE_URL = http://127.0.0.1:8000`
- Verify that this port is reachable (`/health`) and not blocked by firewall

## Start API (Assistant-Live-Bridge)
- Activate venv and install missing deps (`fastapi`, `uvicorn`, `pydantic`)
- Launch: `uvicorn main:app --host 127.0.0.1 --port 8000`
- If binding issues occur, use `--host 0.0.0.0` and keep client at `http://127.0.0.1:8000`
- Health check: open `http://127.0.0.1:8000/health`

## Connect Streamlit
- Open `http://127.0.0.1:8506/`
- Sidebar → toggle “Use Live API” on; it probes `/health` and switches to live mode
- Use “Load Demo Messages” → run “Summarize” or “Full Pipeline” and verify tasks populate

## Verify End-to-End
- Confirm summaries/tasks appear in the dashboard tabs
- Optionally hit API endpoints directly:
  - `POST /summarize` with a sample message
  - `POST /process_summary` with the returned summary
  - `GET /users/{id}/tasks` to read persisted tasks

## Alternative (assistant-live-demo API)
- If you prefer the demo API stack, start: `uvicorn assistant-live-demo.api.main:app --host 127.0.0.1 --port 8000`
- Point Streamlit to the same base URL (it already defaults to `127.0.0.1:8000`)

## Contingencies
- If `/health` fails: check venv activation, missing packages, or port conflicts
- If port is blocked: temporarily disable local firewall for the port or change to `8001` and set `API_BASE_URL` accordingly

## Acceptance Criteria
- Sidebar shows “API Connected”
- Full pipeline creates tasks and they show up under “✅ Tasks” and “🗃 DB Tasks”
- API health responds with JSON, and endpoints succeed for sample payloads