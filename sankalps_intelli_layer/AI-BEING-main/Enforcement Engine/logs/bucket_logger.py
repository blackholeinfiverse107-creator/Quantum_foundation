"""
BUCKET LOGGER
-------------
Internal-only enforcement logging sink.

Responsibilities:
- Persist enforcement traces
- Support replay & audit
- Never leak to user
- Deterministic, append-only
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Log file location (JSON Lines format)
LOG_FILE = Path("logs/enforcement_logs.jsonl")

# Ensure logs directory exists
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_enforcement(
    *,
    trace_id: str,
    input_snapshot,
    evaluator_results,
    final_decision: str
):
    """
    Writes a single enforcement trace.

    This function must NEVER throw.
    Logging failure must not block enforcement.
    """

    try:
        log_payload = {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engine_version": "1.0.0",
            "input_snapshot": input_snapshot.__dict__,
            "evaluators": [r.__dict__ for r in evaluator_results],
            "final_decision": final_decision,
        }

        # Append as JSON line (audit-friendly)
        with LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(log_payload) + "\n")

        # Console visibility (demo / dev only)
        print(json.dumps(log_payload, indent=2))

    except Exception as e:
        # Logging must NEVER break enforcement
        print(
            json.dumps(
                {
                    "logger_error": str(e),
                    "trace_id": trace_id,
                }
            )
        )
