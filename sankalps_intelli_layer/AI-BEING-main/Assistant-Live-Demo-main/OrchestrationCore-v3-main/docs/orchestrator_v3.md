# OrchestratorCore v3 Documentation

## Overview
OrchestratorCore v3 is a scalable, connector-ready pipeline that routes incoming tasks to appropriate external systems, handles retries, fallbacks, and integrates with the Decision Hub and Unified DB.

## Pipeline Flow Diagram

```
Task JSON Input
       |
       v
  route_task() in router_v3.py
       |
       +--> Fetch decision from /decision_hub
       |
       +--> If decision == "defer" --> Status: queued --> DB log
       |
       +--> If decision == "proceed" --> Route to connector --> Status: sent --> DB log
       |
       v
  execute_pipeline() in pipeline_controls.py
       |
       +--> Send to primary connector
       |     |
       |     +--> Success --> Final status: success --> DB update
       |     |
       |     +--> Fail --> Retry (up to 3 times, exponential backoff)
       |           |
       |           +--> Success --> Final status: success --> DB update
       |           |
       |           +--> Fail --> Try fallback connector
       |                 |
       |                 +--> Success --> Final status: success, fallback_used: true --> DB update
       |                 |
       |                 +--> Fail --> Final status: failed, fallback_used: true --> DB update
```

## Connector Design
Connectors are lightweight modules in the `connectors/` directory. Each exposes a `send(task_json)` function that:
- Validates input (must be dict)
- Logs the attempt
- Simulates success/failure (for stubs)
- Returns `{"status": "success"|"failed", "info": "..."}`

### Available Connectors
- `calendar_connector.py`: Handles calendar events
- `email_connector.py`: Sends emails
- `crm_connector.py`: Updates CRM records

## Routing Rules
Routing is handled by `route_task(task_json)` in `router_v3.py`:
- Extracts `task_type` and `external_target` from `task_json`
- Calls Nilesh's `/decision_hub` with input_text, platform, device_context for intelligent decision making
- If decision == "proceed": routes to `external_target` if in ["calendar", "email", "crm"], else "fallback"; status = "sent"
- If decision == "defer": routed_to = "queue", status = "queued"
- Logs routing and decision to DB tables `routing_logs` and `decisions`

## Fallback Strategy
- Primary connector fails after 3 retries (1s, 2s, 4s backoff)
- Fallback mapping:
  - calendar → email
  - email → crm
  - crm → no fallback (fail)
- If fallback succeeds, `fallback_used = true`

## API Contracts

### Orchestration API
**Endpoint:** POST /orchestrate
**Input:** `{"task_id": str}`
**Output:** `{"routing": routing_result, "pipeline": pipeline_result or None}` or `{"error": str}`
Where routing_result: `{"routed_to": str, "status": "queued"|"sent", "trace_id": str, "timestamp": str}`
pipeline_result: `{"final_status": "success"|"failed", "attempts": int, "fallback_used": bool}`

### Internal Functions

#### route_task(task_json: dict) → dict
**Input:** Task data dict
**Output:** Routing result as above

#### execute_pipeline(task_json: dict, routed_to: str, trace_id: str) → dict
**Input:** Task data, routed connector, trace ID
**Output:** Pipeline result as above

#### Connector send(task_json: dict) → dict
**Input:** Task data dict
**Output:** `{"status": "success"|"failed", "info": str}`

## Integration with ContextFlow
The orchestrator calls Sankalp's ContextFlow API at `/api/contextflow_task` for task creation. The `/orchestrate` endpoint takes a `task_id`, fetches the full task from ContextFlow, enriches it, routes it, and executes the pipeline, returning results for evaluation.

## Integration with Nilesh's Decision Hub
The router integrates with Nilesh's Decision Hub API at `/decision_hub` (expected on localhost:8000). It sends task data with input_text, platform, device_context for platform-aware decision making. Receives decision outcomes to enable intelligent routing. Compatible logs are written to the shared `assistant_core.db` for unified tracing.

## Integration with Seeya's SummaryFlow
The orchestrator enriches incoming tasks with structured summaries using Seeya's SummaryFlow v3 API. Before routing, tasks are processed to extract `summary`, `type`, `intent`, `urgency`, and `entities` (persons, datetime). This provides cleaner, structured context for routing and execution. Summaries are persisted to the shared `assistant_core.db` summaries table.

## Integration with Chandresh's EmbedCore
The orchestrator generates deterministic embeddings for task content using Chandresh's EmbedCore v3. Embeddings are created for future use in routing decisions and similarity matching. This prepares the system for advanced embedding-based intelligence in task processing.

## Integration with Yash's Frontend
After routing and pipeline execution, the orchestrator sends routing and pipeline results to Yash's frontend API at `/api/routing_result` (expected on localhost:4000). This allows the frontend to display real-time success/fail/fallback status for user visibility. The call is asynchronous and non-blocking to avoid impacting orchestration performance.

## Database Schema
- **routing_logs**: task_id, routed_to, status, trace_id, timestamp
- **decisions**: task_id, score, top_agent, decision, timestamp
- **tasks**: task_id, routed_to, retries, final_status, timestamp, trace_id

## Error Handling
- Invalid inputs: Return failed status with info
- API failures: Fallback to proceed
- DB errors: Logged but not fatal
- Connector failures: Retried with backoff, then fallback