# Sovereign Enforcement Integration Spec

## 1. Sankalp (Conversation / Emotion)

Sankalp MUST:
- produce emotional_output
- NOT self-censor for policy
- accept rewrite_class blindly

Consumes:
- decision
- rewrite_class (if present)

---

## 2. Akanksha (Behavior Validator)

Akanksha MUST:
- validate behavioral safety
- emit risk_flags
- NOT block directly

Consumes:
- enforcement decision only for observability

---

## 3. Ishan (Governance)

Ishan MUST:
- map laws → evaluator rules
- never modify enforcement logic directly

Consumes:
- evaluator reason codes
- trace logs (offline)

---

## 4. Raj (This System)

Raj:
- executes deterministically
- never negotiates
- never leaks rules
- always fails closed
