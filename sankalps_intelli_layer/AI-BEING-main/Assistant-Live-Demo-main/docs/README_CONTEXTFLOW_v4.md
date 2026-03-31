# ContextFlow V4 Documentation

This document outlines the usage, integration, and logic of the `contextflow_v4` module and its associated API endpoint.

## API Usage

### Endpoint: `POST /api/contextflow_task`

This endpoint accepts a summary object (typically from Seeya's summarizer), normalizes it into a task, persists it to Nilesh's unified database, and returns the created task object wrapped in a standard response envelope.

#### Request Body (JSON)

The input payload must match the `DecisionHubSummary` schema:

```json
{
  "summary_id": "s_700",
  "user_id": "abc123",
  "platform": "whatsapp",
  "message_id": "m700",
  "summary": "Remind client about payment tomorrow at 5 pm",
  "intent": "reminder",
  "urgency": "medium",
  "entities": { 
    "person": ["ACME"], 
    "datetime": null 
  },
  "context_flags": ["has_person"],
  "device_context": "ios",
  "generated_at": "2025-12-17T10:00:00Z"
}
```

#### Response Body (JSON)

The response follows the Nilesh API envelope standard:

```json
{
    "status": "ok",
    "timestamp": "2025-12-17T10:06:38.854167Z",
    "trace_id": "6623315d-d58e-44c5-b277-cb46e64680ba",
    "data": {
        "task_id": "t_c10be9b2",
        "user_id": "abc123",
        "summary_id": "s_700",
        "task_summary": "Reminder related to ACME.",
        "task_type": "reminder",
        "external_target": "crm",
        "priority": "medium",
        "scheduled_for": "2025-12-18T17:00:00Z",
        "status": "pending",
        "platform": "whatsapp",
        "device_context": "ios",
        "created_at": "2025-12-17T10:06:38.810482Z"
    }
}

### Endpoint: `GET /api/tasks`

Retrieves tasks for a specific user. This is primarily for the Frontend to display the task list.

#### Query Parameters
- `user_id` (required): The ID of the user.
- `pending_only` (optional, default=False): If true, returns only tasks with status `pending`.

#### Response Body (JSON)
A list of Task objects.

### Authentication
- Production deployments should protect endpoints with an API key header.
- Set `CONTEXTFLOW_API_KEY` in the environment; clients must send header `X-API-Key: <value>`.
- Health and read endpoints can retain the same guard depending on your threat model.

## Architecture & Integration

This module serves as the bridge between Seeya's raw context understanding and the broader system's action execution.

### 1. Seeya (Context Understanding)
-   **Role:** Ingests raw messages, summarizes them, and extracts intents/entities.
-   **Handoff:** Passes a `DecisionHubSummary` to ContextFlow.

### 2. ContextFlow V4 (Normalization & Task Creation)
-   **Role:** 
    -   Interprets the summary and intent.
    -   Maps fuzzy intents to concrete external targets (e.g., "meeting" -> Calendar API).
    -   Parses relative time expressions (e.g., "tomorrow at 5pm") into ISO8601 timestamps.
    -   Standardizes the data into a `TaskObject`.
-   **Persistence:** Writes the standardized task to Nilesh's `assistant_core.db` in the `tasks` table.

### 3. Nilesh's Decision Hub (Routing & Learning)
-   **Integration:** The `tasks` table acts as a source of truth for the Decision Hub.
-   **Flow:** The Decision Hub can query `pending` tasks, apply RL/scoring logic, and decide *when* or *how* to act on them.

### 4. Parth's Orchestrator (Execution)
-   **Integration:** Calls `/api/contextflow_task` as the "task creation step" to formalize a decision into a persistent task.
-   **Code Reference:** `OrchestrationCore-v3-main/main.py` uses `create_task_via_contextflow` to call this API.
-   **Execution:** After creating the task, the Orchestrator uses the returned `TaskObject` to route and execute actions via connectors (`calendar`, `crm`, `email`).
-   **Logging:** Execution logs are stored in the `task_execution_logs` table in Nilesh's unified DB (`nilesh/data/assistant_core.db`).

### 5. Yash's Frontend (Task Dashboard)
-   **Role:** Displays the "clean" tasks to the user.
-   **Code:** `yash_frontend_v4.py` (Streamlit).
-   **Usage:**
    ```bash
    streamlit run yash_frontend_v4.py
    ```
-   **Integration:** Fetches data from `GET /api/tasks`.

## Mapping Rules & Assumptions

The logic in `contextflow_v4.py` applies the following heuristic rules to determine `task_type` and `external_target`:

### 1. External Target Mapping
The system scans both the `intent` and `summary` fields for keywords. Priority is determined by the order of checks:

*   **CRM (`crm`)**:
    *   **Keywords:** "invoice", "payment", "client"
    *   **Assumption:** Any mention of financial/client terms implies a CRM operation.
*   **Todo (`todo`)**:
    *   **Keywords:** "remind", "remember", "follow up", "followup"
    *   **Condition:** Only applies if **no date/time** is detected/parsed.
    *   **Assumption:** A reminder without a specific time is a general todo list item.
*   **Calendar (`calendar`)**:
    *   **Keywords:** "meeting", "call", "zoom"
    *   **Assumption:** These terms imply a scheduled event.
*   **None (`none`)**:
    *   Default if no keywords match.

### 2. Scheduling Logic
*   **Source:** Uses `entities.datetime` if present; otherwise, attempts to parse the `summary` text using `dateparser`.
*   **Anchor:** Relative dates (e.g., "tomorrow") are calculated relative to the `generated_at` timestamp of the summary, or `now` if missing.
*   **Output:** Always normalized to UTC ISO8601 strings (e.g., `2025-12-18T17:00:00Z`).

### 3. Task Type Determination
*   **Meeting:** Intent contains "meeting" or "schedule".
*   **Reminder:** Intent contains "reminder".
*   **Follow-up:** Intent contains "follow_up" or "followup".
*   **Note:** Default fallback.
