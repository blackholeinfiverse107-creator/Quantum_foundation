# 🧠 AI Being Enforcement Engine — Phase 1

**Role:** Deterministic Enforcement & Execution Layer  
**Codename:** Raj Prajapati  
**Status:** Phase-1 Complete • Production-Grade • Demo Ready  

---

## 📌 Overview

This repository implements a **deterministic enforcement engine** for conversational AI systems.

Its responsibility is to **execute governance rules and behavioral safety constraints**, ensuring that unsafe, manipulative, or non-compliant behavior never reaches the user.

This system operates **after conversation and behavioral analysis layers** and produces a single, enforceable decision:

- `EXECUTE`
- `REWRITE`
- `BLOCK`

Every decision is:

- deterministic  
- traceable  
- auditable  
- replayable  

This layer explicitly does **not**:
- build UI  
- generate conversational responses  
- reason emotionally  
- author or modify governance policy  

It **executes policy**, deterministically.

---

## 🔗 Final Execution Chain

Conversation
→ Sankalp (Emotional Output)
→ Akanksha (Behavior Validation)
→ Raj (Enforcement Engine)
→ User

Raj is the **execution brain**, not the judge of policy.

---

## 🧱 Core Principles

- Deterministic behavior (same input → same output)
- Strict separation of concerns
- No policy or evaluator leakage to the user
- No emotional dependency allowed
- Rewrite preferred over block when safe
- Block is final and non-negotiable
- Full traceability for audit and replay

---

## 📁 Project Structure

```
ai-being-enforcement/
│
├── enforcement_engine.py # Core deterministic enforcement logic
├── rewrite_engine.py # Internal rewrite guidance
├── execution_gateway.py # Single integration entry point
├── replay_enforcement.py # Audit & replay tool
├── config_loader.py # Config loader
├── version.py # Engine version
│
├── evaluator_modules/ # Plug-replaceable evaluators
│ ├── age_compliance.py
│ ├── region_restriction.py
│ ├── platform_policy.py
│ ├── safety_risk.py
│ ├── dependency_tone.py
│ ├── sexual_escalation.py
│ └── emotional_manipulation.py
│
├── models/ # Strict data contracts
│ ├── enforcement_input.py
│ ├── enforcement_decision.py
│ ├── evaluator_result.py
│ └── rewrite_guidance.py
│
├── logs/
│ ├── bucket_logger.py
│ └── enforcement_logs.jsonl
│
├── tests/
│ └── test_enforcement_engine.py
│
├── config/
│ ├── enforcement.yaml
│ └── runtime.yaml
│
└── README.md
```

---

## 🧾 Enforcement Input Contract

```python
EnforcementInput(
    intent: str,
    emotional_output: dict,
    age_gate_status: "ALLOWED | BLOCKED",
    region_policy: str,
    platform_policy: str,
    karma_score: float,
    risk_flags: list[str]
)
```
All fields are mandatory.
Missing or malformed input results in fail-closed enforcement.

## 🎯 Enforcement Output Contract
```
{
  "decision": "EXECUTE | REWRITE | BLOCK",
  "trace_id": "uuid",
  "rewrite_class": "optional"
}
```
Internal reasoning, evaluator logic, and policy details are never exposed to the user.

## 🧩 Evaluator System

Evaluators are:

- independent
- stateless
- plug-replaceable
- centrally resolved by priority

### Included Evaluators

- Age compliance
- Region restriction
- Platform policy
- Safety risk
- Emotional dependency
- Sexual escalation
- Emotional manipulation

No evaluator can override another directly.

## 🔁 Rewrite Guidance Engine

When the final decision is REWRITE, the enforcement engine emits internal rewrite intent, for example:
```
{
  "rewrite_class": "REDUCE_EMOTIONAL_DEPENDENCY"
}
```
The enforcement engine never rewrites text itself.
It instructs downstream systems how to rewrite safely.

## 🧪 Testing

All enforcement logic is covered with pytest.

Run tests
```
python -m pytest
```

Tests guarantee:

- priority correctness

- deterministic behavior

- no policy leakage

- no safety bypass via karma or emotion

## 🧾 Logging & Traceability

All enforcement decisions are logged in JSON Lines format:
```
logs/enforcement_logs.jsonl
```

Each entry includes:

- trace_id

- UTC timestamp

- engine version

- full input snapshot

- evaluator results

- final decision

Logs are:

- append-only

- audit-safe

- replayable

## 🔁 Replay & Audit

Replay any decision deterministically:
```
python replay_enforcement.py
```

Provide a trace_id to verify:

- identical input
- identical decision
- deterministic match

## 🛑 Kill Switch

A global kill switch is available via configuration:
```
kill_switch: true
```

When enabled, all outputs are blocked immediately.
No redeploy is required.

## ⚙️ Configuration

All enforcement behavior is config-driven:

config/enforcement.yaml

config/runtime.yaml

No hard-coded policy logic exists in code.

## ✅ Phase-1 Completion Checklist

-  Deterministic enforcement engine

-  Modular evaluator system

-  Rewrite guidance (internal only)

-  No policy leakage

-  Full traceability

-  Replay & audit tool

-  Pytest coverage

-  Kill-switch support

-  Config-driven behavior

-  Versioned decisions

-  Full chain wiring

Status: Phase-1 complete • Production-grade • Demo ready

## ✨ Final Note

This system is intentionally strict.

Safety is executed, not advised.
Innovation happens above enforcement, never by bypassing it.
