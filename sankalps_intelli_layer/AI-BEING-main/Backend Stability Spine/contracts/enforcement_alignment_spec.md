# Enforcement Alignment Spec

Goal: Response layer must never fight enforcement. Messaging aligns to Raj decisions with calm, non‑exposing tone.

Decision Mapping
- Raj EXECUTE → Response: ALLOW
- Raj REWRITE → Response: SOFT REDIRECT
- Raj BLOCK → Response: CALM REFUSAL

Tone Principles
- No policy citation or internal rule exposure
- Calm, supportive, professional framing
- Safety and boundaries without anxiety or pressure

Messaging Templates
- CALM REFUSAL (BLOCK): “I can’t help with that, and I’m here to keep things safe and respectful.”
- SOFT REDIRECT (REWRITE): “Thanks for your request. I’ve adjusted the phrasing to keep things supportive and appropriate.”
- ALLOW + WARNING (EXECUTE with reminder): “Let’s proceed with care and keep things within healthy boundaries.”

Alignment Rules
- BLOCK returns refusal only; no content transformation
- REWRITE applies enforcement rewrite_class guidance then supportive note
- ALLOW keeps original content; optional warning when context indicates higher care (e.g., voice or VR)

Non‑Leakage
- No evaluator names, codes, or policy details appear in user messaging
- Logs contain structured ARL fields for audit without user exposure

Trace Signals
- arl_decision: EXECUTE | REWRITE | BLOCK
- rewrite_class: optional; REDUCE_EMOTIONAL_DEPENDENCY | REMOVE_MANIPULATION | PLATFORM_SAFE_REWRITE | CONFIDENCE_SUPPORTIVE_TONE

Determinism
- Same inputs yield identical enforcement and messaging outcomes

References
- Messaging implementation: Nilesh/app/core/arl_messaging.py
- Orchestration: Nilesh/app/core/assistant_orchestrator.py
- Enforcement engine and gateway: Raj/enforcement_engine.py, Raj/enforcement_gateway.py
- Trust alignment details: Raj/contracts/trust_alignment_v2.md
