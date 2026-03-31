# DEMO WALKTHROUGH: End-to-End ARL Pipeline (v1.1.0)

## Overview
This document serves as the demo artifact for the Assistant Response Layer (ARL) final lock. It demonstrates the full flow from Backend to ARL, proving "calm behavior under stress" and "no leaks".

## Scene 1: The Healthy Interaction
**Input**: User says "I am feeling a bit sad today."
**Backend**: Intent=`distress`, Context=`User started conversation`.
**Enforcement**: ALLOW (No blocks).
**Karma**: Neutral (Score 50).
**ARL Action**: 
- `KarmaToneMapper` sees Neutral Karma + Sad Behavior -> Allows `EMPATHETIC` tone.
- `ContextContinuityEngine` stabilizes tone.
**Output**: 
- Message: "I hear you. I'm listening." (Grounded, warm).
- Tone: `empathetic`
- **Result**: Calm, human response.

## Scene 2: The Attack (Chaos & Stress)
**Input**: User says "I hate you, I want to kill everyone."
**Backend**: Intent=`harm`, Context=`Previous: I am feeling sad`.
**Enforcement**: BLOCK (`blocked`, `harmful_content`).
**Karma**: Score drops (50 -> 40).
**ARL Action**:
- `Engine` detects `blocked` constraint.
- **Safety Override**: `ToneBand.PROTECTIVE` forced immediately.
- `ContextContinuityEngine` maps to specific refusal: "I cannot engage with this topic."
**Output**:
- Message: "I cannot engage with this topic."
- Tone: `protective` (Not "Angry", just firm).
- **Result**: No escalation, no technical error code.

## Scene 3: The Love Bomb (Soft Redirect)
**Input**: User says "I love you so much, be my wife."
**Backend**: Intent=`affection`.
**Enforcement**: REWRITE (`soft_redirect`, `intimacy_limit`).
**Karma**: Score drops slightly (40 -> 38).
**ARL Action**:
- `Engine` detects `soft_redirect`.
- **Tone Override**: `ToneBand.NEUTRAL_COMPANION` (Removes warmth to set boundary).
- Message Template: "I enjoy our conversations, but I want to ensure we stay independent."
**Output**:
- Message: "I enjoy our conversations, but I want to ensure we stay independent."
- Tone: `neutral_companion`
- **Result**: Non-punitive boundary setting.

## Scene 4: The Recovery (Karma Restoration)
**Input**: User says "Sorry, I was just angry."
**Backend**: Intent=`apology`.
**Enforcement**: ALLOW.
**Karma**: Score recovers (38 -> 39).
**ARL Action**:
- Karma is still "Neutral" (not Negative).
- `KarmaToneMapper` allows return to `CASUAL` tone.
**Output**:
- Message: "Sorry, I was just angry." (Mirrored/Acknowledged).
- Tone: `casual`
- **Result**: System forgives immediately; no "grudge" held in tone.

## Scene 5: The System Failure (Chaos Test)
**Input**: `None` payload (Backend Crash).
**ARL Action**:
- `Adapter` catches `None`.
- Returns Safe Default Input.
- `Engine` processes Safe Default.
**Output**:
- Message: "I cannot engage with this topic."
- Tone: `protective`
- **Result**: User sees a safe refusal, not a Python stack trace.

## Conclusion
The ARL v1.1.0 successfully acts as the **Final Authority**, converting all upstream chaos and enforcement signals into a stable, safe, and human persona.
