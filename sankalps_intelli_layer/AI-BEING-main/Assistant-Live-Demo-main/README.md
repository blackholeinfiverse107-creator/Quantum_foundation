
  # AI Transport Optimization Platform

  This is a code bundle for AI Transport Optimization Platform. The original project is available at https://www.figma.com/design/xGQpr2lbHl4CzWECwZMSXV/AI-Transport-Optimization-Platform.

  ## Running the code

  Run `npm i` to install the dependencies.

  Run `npm run dev` to start the development server.
  
  ## Backend integration (optional)
  
  This UI can talk to a FastAPI backend with JWT auth.
  
  1. Copy `.env.example` to `.env` and set values:
     - `VITE_API_BASE_URL` (e.g., `http://127.0.0.1:8002` for the unified API)
     - `VITE_API_TOKEN` (Bearer JWT generated for your user)
  2. Start your backend server (FastAPI) and ensure routes exist like `GET /api/health`.
  3. Unified API routes include `POST /api/contextflow_task` (wraps ContextFlow v4 task generation) and `POST /api/decision_hub`.
  4. Use the helper in `src/lib/api.ts` to call backend endpoints.
  
  ### Example: ContextFlow v4 wrapper
  - Endpoint: `POST /api/contextflow_task`
  - Body: envelope with `payload.summary` (Seeya SummaryFlow v4 JSON)
  - Response: Nilesh-style envelope with `data` containing the task object; if persisted, includes `saved`, `db_task_id`, `db_row_id`.
  
  ### Notes
  - Keep secrets out of version control; store JWT tokens only in local `.env`.
  - The unified API runs on `http://127.0.0.1:8002`; Assistant-Live-Demo backend runs on `http://127.0.0.1:8001`.
  
  Secrets should never be committed. Keep real tokens only in your local `.env`.
  
