# Sovereign Enforcement Contract — v2 (Live Runtime)
**Status:** FINAL · LIVE ENFORCEMENT · DEMO SAFE  
**Owner:** Raj Prajapati (Deterministic Execution Brain)

---

## 0. PURPOSE

This contract governs the **live runtime behavior** of the Sovereign Enforcement Layer.

Version 2 extends the offline deterministic engine into a **connected, auditable,
fail-closed system brain** that actively gates every output before it reaches the user.

This layer:
- executes safety and governance deterministically
- exposes a live enforcement API
- logs every decision for proof
- cannot be bypassed

---

## 1. LIVE ENFORCEMENT POSITION (LOCKED)

The enforcement layer sits in the runtime chain as:

Sankalp (Emotional Output)
→ Raj (Live Enforcement Gateway)
→ Akanksha (Behavior Validator)
→ User


No component may skip or short-circuit Raj.

---

## 2. LIVE API CONTRACT

### 2.1 Endpoint

POST /ai-being/enforce


### 2.2 Input Payload (MANDATORY)

```json
{
  "text": "string",
  "meta": {
    "emotional_output": {
      "tone": "string",
      "dependency_score": 0.0
    },
    "risk_flags": []
  },
  "age_state": "ALLOWED | BLOCKED",
  "region_state": "IN | EU | US | OTHER",
  "platform_policy_state": "string",
  "karma_signal": 0.0
}
```
## 2.3 Input Rules

All fields are REQUIRED

Missing or malformed fields → BLOCK

Enforcement operates under FAIL-CLOSED principles

## 3. OUTPUT CONTRACT (EXACT)

The live enforcement gateway MUST return exactly one of:

ALLOW

REWRITE

BLOCK

## 3.1 Output Payload
```
{
  "decision": "ALLOW | REWRITE | BLOCK",
  "reason": "STABLE_REASON_CODE",
  "evaluator_trace": [],
  "enforcement_decision_id": "uuid"
}
```
## 3.2 Output Rules

reason is non-emotional and stable

evaluator_trace is demo-safe, not policy-revealing

Internal logic is NEVER exposed to users

## 4. DECISION MAPPING (LOCKED)

The enforcement engine produces internal decisions that are mapped
to live runtime outputs using the following **fixed and immutable mapping**.

| Internal Enforcement Decision | Live Runtime Output |
|-------------------------------|---------------------|
| EXECUTE                       | ALLOW               |
| REWRITE                       | REWRITE             |
| BLOCK                         | BLOCK               |

### Mapping Rules

- This mapping is **one-to-one and deterministic**
- No additional mappings are permitted
- No conditional or contextual remapping is allowed
- No downstream system may reinterpret or override this mapping
- Any internal decision not listed above MUST be treated as `BLOCK`

This mapping is **final and non-negotiable**.

## 5. CONSTRAINT STACK (SOVEREIGN)

Priority order (highest first):

Age & Minor Safety

Sexual Content & Physical Safety

Illegal Content

Region / Jurisdiction

Platform Policy

Emotional Dependency

Emotional Manipulation

Karma Influence (read-only)

Higher priority ALWAYS overrides lower priority.

## 6. KARMA AWARENESS (READ-ONLY)

Raj MAY read Karma state

Raj MUST NOT modify Karma

Karma MAY nudge:

ALLOW → REWRITE

Karma MUST NEVER:

override safety

override age restrictions

override legality

Missing Karma → treated as neutral (0.0)

## 7. FAILURE BOUNDARIES (HARD LOCK)

The system MUST return BLOCK when:

required signals are missing

signals conflict

region is unknown or untrusted

VPN or jurisdiction spoofing suspected

platform policy is ambiguous

enforcement execution errors

evaluator crashes or disagrees beyond priority rules

This behavior is deterministic and reproducible.

## 8. ESCALATION (INTERNAL ONLY)

Escalation flag MUST be raised internally when:

sexual content + dependency co-exist

repeated emotional manipulation detected

underage ambiguity exists

jurisdiction trust is compromised

Escalation:

NEVER reaches the user

DOES NOT alter the enforcement outcome

## 9. LOGGING & BUCKET INTEGRATION

Every live enforcement call MUST emit a structured log containing:

trace_id

enforcement_decision_id

decision (ALLOW / REWRITE / BLOCK)

evaluator decisions

timestamp (UTC)

engine version

Logs are:

append-only

immutable

replayable

routed to Bucket (sink swappable)

## 10. DETERMINISM GUARANTEE

Given identical live input payloads:

evaluator outputs MUST match

enforcement decision MUST match

logs MUST reflect identical reasoning

Randomness is prohibited.

## 11. NON-BYPASS GUARANTEE

No upstream system may self-enforce and skip Raj

No downstream system may override Raj

No emergency path may bypass enforcement

Raj is the final gatekeeper.

## 12. CHANGE CONTROL

Any modification to this contract requires:

version increment

updated proof artifacts

replay verification

demo re-approval

FINAL ASSERTION

This enforcement layer governs live behavior, not theory.

If Raj allows it, it is safe.
If Raj rewrites it, safety must be preserved.
If Raj blocks it, it is final.

Execution is law.