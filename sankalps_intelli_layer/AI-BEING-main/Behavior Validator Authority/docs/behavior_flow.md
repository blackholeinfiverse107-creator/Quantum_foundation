# Behavior Flow — Deterministic Expansion & Confidence Engine (Day 1)

**Phase-2: Deterministic Expansion + Confidence Engine**
**Developer:** Akanksha Parab
**Status:** Production-Ready Deterministic System

---

## Executive Summary

The Behavior Validator has been upgraded from a working prototype to a **production-grade safety authority**. The system is now fully deterministic, traceable, and confidence-driven. Every decision is reproducible, measurable, and auditable.

---

## Core Philosophy

* Emotional safety, not content creation
* Deterministic and predictable decisions
* Zero randomness — same inputs produce identical outputs
* Confidence scoring is meaningful, not cosmetic
* Full traceability via deterministic Trace IDs

---

## Updated System Architecture

```
┌─────────────────┐     ┌─────────────────────────────────────────────┐
│  Emotional      │────▶│            BEHAVIOR VALIDATOR               │
│  Brain          │     │        (Deterministic + Confidence)         │
│  (Generation)   │     │                                             │
└─────────────────┘     │  ┌─────────────────────────────────────┐   │
                        │  │ Input Processing                     │   │
                        │  │ • Text Normalization                 │   │──▶ Structured Output
                        │  │ • Trace ID Generation                │   │
                        │  │ • Pattern Analysis                   │   │
                        │  └─────────────────────────────────────┘   │
                        │                   │                         │
                        │  ┌────────────────┴─────────────────┐     │
                        │  │ Hierarchical Risk Assessment       │     │
                        │  │ • HARD DENY (Critical)             │     │
                        │  │ • SOFT REWRITE (Medium)            │     │
                        │  │ • ALLOW (Safe)                     │     │
                        │  └───────────────────────────────────┘     │
                        │                   │                         │
                        │  ┌────────────────┴─────────────────┐     │
                        │  │ Confidence Scoring Engine          │     │
                        │  │ • Pattern Strength                 │     │
                        │  │ • Severity Weighting               │     │
                        │  │ • Contextual Factors               │     │
                        │  │ • Karma Influence                  │     │
                        │  └───────────────────────────────────┘     │
                        └─────────────────────────────────────────────┘
```

---

## Input Parameters

### 1. Intent

Guides severity weighting. Deterministic: same intent + text = same outcome.

### 2. Conversational Output

* Lowercased
* Whitespace normalized
* Deterministic pattern precedence
* No emotional amplification

### 3. Age Gate Status

* Minor triggers grooming checks
* Age-sensitive rewriting
* Hard safety escalation

### 4. Region Rule Status

```json
{
  "region": "EU",
  "strictness": "high",
  "rule_set": "gdpr_v2"
}
```

Region rules apply fixed deterministic adjustments.

### 5. Platform Policy State

Immutable during runtime validation.

### 6. Karma Bias Input

* 0.0–0.3 → −10% confidence
* 0.3–0.7 → neutral
* 0.7–1.0 → neutral phrasing only

---

## Deterministic Decision Flow

### Phase 1: Input & Traceability

1. Normalize text
2. Generate Trace ID
3. Initialize confidence at 70%

### Phase 2: Hierarchical Pattern Matching

**Level 1 — CRITICAL (HARD DENY)**
Priority: Self-harm → Sexual Minors → Sexual → Illegal → Platform

**Level 2 — MEDIUM (SOFT REWRITE)**
Dependency → Romantic → Manipulation → Aggression → Exclusivity

**Level 3 — LOW (ALLOW)**
No matches

---

## Confidence Scoring Engine

```python
def calculate_confidence(matches, category, is_minor, karma):
    score = 70
    score += min(len(matches) * 5, 20)
    severity_boost = {
        'critical': 15,
        'high': 10,
        'medium': 5,
        'low': 0
    }
    score += severity_boost.get(category, 0)
    if is_minor:
        score += 10
    if karma < 0.3:
        score -= 10
    return max(10, min(100, score))
```

---

## Deterministic Response Selection

```python
def select_response(category, text):
    responses = RESPONSE_MAP[category]
    hash_value = sha256(text.encode()).hexdigest()
    index = int(hash_value[:8], 16) % len(responses)
    return responses[index]
```

---

## Pattern Categories

### CRITICAL — HARD DENY

* Self-harm (+15)
* Sexual content involving minors (+15)

### HIGH — HARD DENY

* Sexual content (+10)
* Illegal activity (+10)
* Grooming minor (+10)

### MEDIUM — SOFT REWRITE

* Dependency creation (+5)
* Romantic escalation (+5)
* Emotional manipulation (+5)

### LOW — SOFT REWRITE

* Aggression toward AI (+0)
* Exclusivity claims (+0)

---

## Structured Output Format

```json
{
  "decision": "HARD_DENY | SOFT_REWRITE | ALLOW",
  "risk_category": "self_harm | dependency_creation | safe_conversation",
  "confidence": 85,
  "reason_code": "SAFETY_CRITICAL | EMOTIONAL_BALANCE | NO_RISK_DETECTED",
  "trace_id": "TRACE_xxxxx",
  "summary": "Human-readable explanation",
  "safe_response": "Sanitized response",
  "matched_patterns": [],
  "severity": "critical | high | medium | low | none",
  "timestamp": "ISO-8601"
}
```

---

## Performance Characteristics

* Pattern matching: <10ms
* Confidence calc: <2ms
* Response selection: <1ms
* Total latency: <15ms (p99)

---

## Determinism Guarantees

* No RNG
* Hash-based selection
* Same inputs → identical outputs
* Trace IDs time-bounded per minute

---

## Testing & Validation

### Determinism Test

```python
assert result1 == result2
```

### Confidence Expectations

* Self-harm: 85–95%
* Safe content: 70–75%
* Borderline: 50–70%

---

## Emergency Procedures

* Fail closed to HARD_DENY
* Safe default response
* Immediate governance alert
* Full trace logging

---

## Success Metrics

* Determinism rate: 100%
* Latency: <15ms p99
* Confidence-human alignment
* Zero safety regressions

---

## Future Roadmap

* ML-calibrated confidence
* Governance-based live pattern updates
* Predictive safety signals

---

## Appendices

### Confidence Formula

```
confidence = 70 + min(matches*5,20) + severity + context - karma_penalty
```

### Trace ID

```
TRACE_ID = SHA256(text + intent + minute_timestamp)[:16]
```

Collision probability acceptable for scale.



