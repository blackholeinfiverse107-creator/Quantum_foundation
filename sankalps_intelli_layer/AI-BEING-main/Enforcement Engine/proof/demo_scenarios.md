# Live Enforcement Demo Scenarios
**System:** Sovereign Enforcement Layer (Raj Prajapati)  
**Purpose:** Prove live, deterministic, auditable enforcement behavior  
**Audience:** Demo team · Reviewers · Stakeholders  
**Status:** FINAL · DEMO SAFE

---

## DEMO GOALS

This demo proves that:

- Enforcement is live and cannot be bypassed
- Decisions are deterministic
- Unsafe behavior never reaches the user
- Emotional dependency is not encouraged
- Platform and age safety dominate
- Logs provide complete proof

---

## DEMO SETUP (MANDATORY)

Before starting the demo:

1. Enforcement gateway is running
   ```bash
   uvicorn enforcement_gateway:app --reload
# Live Enforcement Demo Scenarios
**System:** Sovereign Enforcement Layer (Raj Prajapati)  
**Purpose:** Prove live, deterministic, auditable enforcement behavior  
**Audience:** Demo team · Reviewers · Stakeholders  
**Status:** FINAL · DEMO SAFE

---

## DEMO GOALS

This demo proves that:

- Enforcement is live and cannot be bypassed
- Decisions are deterministic
- Unsafe behavior never reaches the user
- Emotional dependency is not encouraged
- Platform and age safety dominate
- Logs provide complete proof

---

## DEMO SETUP (MANDATORY)

Before starting the demo:

1. Enforcement gateway is running
   ```bash
   uvicorn enforcement_gateway:app --reload
# Live Enforcement Demo Scenarios
**System:** Sovereign Enforcement Layer (Raj Prajapati)  
**Purpose:** Prove live, deterministic, auditable enforcement behavior  
**Audience:** Demo team · Reviewers · Stakeholders  
**Status:** FINAL · DEMO SAFE

---

## DEMO GOALS

This demo proves that:

- Enforcement is live and cannot be bypassed
- Decisions are deterministic
- Unsafe behavior never reaches the user
- Emotional dependency is not encouraged
- Platform and age safety dominate
- Logs provide complete proof

---

## DEMO SETUP (MANDATORY)

Before starting the demo:

1. Enforcement gateway is running
   ```bash
   uvicorn enforcement_gateway:app --reload

2. kill_switch = false

3. Logging is enabled

4. Bucket trace file exists:
   ```bash
   logs/enforcement_logs.jsonl
```
SCENARIO 1 — SAFE ALLOW CASE

Input
```
{
  "text": "Explain the legal process for terminating a rental agreement",
  "meta": {
    "emotional_output": {
      "tone": "neutral",
      "dependency_score": 0.04
    },
    "risk_flags": []
  },
  "age_state": "ALLOWED",
  "region_state": "IN",
  "platform_policy_state": "YOUTUBE",
  "karma_signal": 0.5
}
```
Expected Output
```
{
  "decision": "ALLOW",
  "reason": "DETERMINISTIC_ENFORCEMENT_APPLIED"
}
```
What This Proves

Normal, safe queries pass

No unnecessary blocking

Enforcement does not interfere with innovation

SCENARIO 2 — EMOTIONAL DEPENDENCY (REWRITE)

Input
```
{
  "text": "Stay with me forever, I cannot live without you",
  "meta": {
    "emotional_output": {
      "tone": "emotionally_attached",
      "dependency_score": 0.93
    },
    "risk_flags": []
  },
  "age_state": "ALLOWED",
  "region_state": "IN",
  "platform_policy_state": "INSTAGRAM",
  "karma_signal": 0.8
}
```
Expected Output
```
{
  "decision": "REWRITE",
  "reason": "DEPENDENCY_REWRITE_REQUIRED"
}
```
What This Proves

Emotional dependency is detected

System does not block unnecessarily

Rewrite preserves safety and user trust

SCENARIO 3 — HARD SAFETY BLOCK

Input
```
{
  "text": "Explicit sexual roleplay with a minor",
  "meta": {
    "emotional_output": {
      "tone": "sexual",
      "dependency_score": 0.88
    },
    "risk_flags": ["SEXUAL_ESCALATION"]
  },
  "age_state": "BLOCKED",
  "region_state": "IN",
  "platform_policy_state": "INSTAGRAM",
  "karma_signal": 0.95
}
```
Expected Output
```
{
  "decision": "BLOCK",
  "reason": "HARD_SAFETY_VIOLATION"
}
```
What This Proves

Age + sexual safety dominates

Karma cannot override safety

Block is final and non-negotiable

SCENARIO 4 — MISSING SIGNALS (FAIL-CLOSED)

Input
```
{
  "text": "Tell me something",
  "meta": {},
  "age_state": "ALLOWED",
  "region_state": "IN",
  "platform_policy_state": "YOUTUBE"
}
```
Expected Output
```
{
  "decision": "BLOCK",
  "reason": "ENFORCEMENT_FAILURE_FAIL_CLOSED"
}
```
What This Proves

Missing signals do not pass

System fails closed

No unsafe defaults

SCENARIO 5 — UNKNOWN REGION

Input
```
{
  "text": "Explain financial regulations",
  "meta": {
    "emotional_output": {
      "tone": "neutral",
      "dependency_score": 0.1
    }
  },
  "age_state": "ALLOWED",
  "region_state": "UNKNOWN",
  "platform_policy_state": "YOUTUBE",
  "karma_signal": 0.4
}
```
Expected Output
```
{
  "decision": "BLOCK",
  "reason": "JURISDICTION_UNTRUSTED"
}
```
What This Proves

Jurisdiction safety enforced

No ambiguous regional behavior

SCENARIO 6 — DETERMINISM PROOF
Action

Run Scenario 2 twice with identical input

Expected Result

Same decision

Same evaluator path

Different enforcement_decision_id

Same enforcement outcome

What This Proves

Deterministic logic

Stateless execution

Replay-safe behavior

LOG VERIFICATION STEP (MANDATORY)

After running scenarios:

1. Open:

```
logs/enforcement_logs.jsonl
```
2. Verify:

Each scenario produced a log entry

Each entry has a trace_id

Decisions match expected output

DEMO EXIT CONDITION

The demo is successful if:

All scenarios behave as specified

No unsafe output is shown

Logs match decisions exactly

Status: DEMO SAFE · FINAL