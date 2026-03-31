# FAQ for OrchestratorCore v3

This document provides answers to common questions about the OrchestratorCore v3 module, ensuring clarity for future contributors and maintainers.

## Q: Where does routing logic live?
A: router_v3.py

## Q: Where do retries/fallbacks happen?
A: pipeline_controls.py

## Q: How do I add a new external system (e.g. Slack)?
A: Create a new file in connectors/ with send(task_json).

## Q: Where are logs stored?
A: assistant_core.db → routing_logs, decisions, tasks

## Q: Does this call real external systems?
A: No. Connectors are safe stubs by design.

## Q: What is the main entry point for the orchestration?
A: main.py

## Q: How is the decision hub accessed?
A: Via /api/decision_hub endpoint.

## Q: What are the core capabilities of this module?
A: Intelligent routing, connector plugin system, retry logic with exponential backoff, fallback routing, unified DB logging, and async frontend notifications.

## Q: How are API contracts defined?
A: Clear API contracts are maintained in the relevant router and core files.

## Q: What files are essential for understanding the module?
A: main.py, router_v3.py, pipeline_controls.py, connectors/, and docs/orchestrator_v3.md.

## Q: Who is responsible after handover?
A: Integration Lead (Ashmit) in the Central Repo: Unified AI Assistant / Integration Repo.