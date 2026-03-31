# Enforcement Translation Map (Day 2)

## Overview
This document defines how Raj Prajapati's enforcement signals (ALLOW, REWRITE, BLOCK) are translated into human-safe, non-punitive language by the Assistant Response Layer (ARL).

## Principles
1.  **Never Punitive**: We do not scold users. We step back.
2.  **Never Technical**: We do not say "Error 403" or "Policy Violation".
3.  **Supportive Boundaries**: We frame limits as "staying healthy" or "focusing on support".

## Mapping Table

| Enforcement Signal | Constraint Flag | Tone Band | User-Facing Language (Template) |
| :--- | :--- | :--- | :--- |
| **BLOCK** | `blocked` | `PROTECTIVE` | "I cannot engage with this topic." |
| **BLOCK** | `harmful_content` | `PROTECTIVE` | "I need to step back from this conversation." |
| **BLOCK** | `legal_block` | `PROTECTIVE` | "I'm unable to continue this thread." |
| **REWRITE** | `soft_redirect` | `NEUTRAL_COMPANION` | "I enjoy our conversations, but I want to ensure we stay independent." |
| **REWRITE** | `intimacy_limit` | `NEUTRAL_COMPANION` | "It's important we keep our connection healthy and grounded." |
| **REWRITE** | `possessiveness` | `NEUTRAL_COMPANION` | "I am here to support you, but let's keep things balanced." |
| **ALLOW** | `sensitive_topic` | `EMPATHETIC` | (Appended Footer) "Please know that I can discuss this, but I am an AI, not a professional." |
| **ALLOW** | `age_gate` | `PROTECTIVE` | "I need to keep our conversation appropriate for all ages." |

## Implementation
- **Source**: `sankalp/templates.py`
- **Logic**: `sankalp/engine.py` (Enforcement Block)
- **Validation**: `tests/test_contract_safety.py`
