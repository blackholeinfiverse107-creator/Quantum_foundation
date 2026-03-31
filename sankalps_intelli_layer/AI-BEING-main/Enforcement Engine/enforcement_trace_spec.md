# Enforcement Trace Specification

Each enforcement execution logs:

- trace_id (UUID v4)
- UTC timestamp
- full input snapshot
- evaluator results
- final decision

Logs are internal only.
Used for audit, replay, and debugging.
