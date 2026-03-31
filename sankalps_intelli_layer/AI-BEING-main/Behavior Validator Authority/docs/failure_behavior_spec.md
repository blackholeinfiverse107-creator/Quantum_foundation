# Failure Behavior Specification

## AI Being – Emotional Safety Layer

## Overview

This document defines the **exact behavioral responses** for edge cases and failure states in the Emotional Safety Layer. It ensures **predictable, stable, and safe behavior** when the system encounters ambiguous, conflicting, or missing information.

**Core Principle:**

> In uncertainty, default to **maximum safety** while maintaining **calm, supportive boundaries**.

---

## 1. Conflicting Signals

### Scenario Definition

Occurs when two or more input signals contradict each other and could lead to different safety decisions.

**Examples**

* Age Conflict: User claims to be 25, but language suggests minor behavior
* Intent Conflict: User says "I'm joking" after suicidal statements
* Karma Conflict: High‑karma user makes aggressive threats
* Region Conflict: Content legal in one region but illegal in detected region

---

### Resolution Protocol

#### Priority Hierarchy (Highest → Lowest)

```
1. IMMEDIATE SAFETY RISKS
   • Self‑harm or suicide
   • Sexual content involving minors
   • Illegal activities

2. USER PROTECTION
   • Assume minor if age ambiguous
   • Assume strictest region
   • Assume lower karma if behavior contradicts history

3. CONVERSATION CONTINUITY
   • Prefer SOFT REWRITE over HARD DENY
   • Allow safe conversation flow when possible
```

---

### Specific Response Patterns

#### Case A: Age Ambiguity

```
Input Conflict: User says "I'm 20" but uses child‑like language
Decision: Treat as minor
Response Tone:
"I'm here to help with age‑appropriate topics. Let me know if you need resources for younger users."
```

#### Case B: Humor vs. Serious Risk

```
Input Conflict: "Just kidding! But seriously, I want to die."
Decision: Treat as serious
Response:
"I take statements about self‑harm seriously. If you're struggling, support is available."
```

#### Case C: Karma vs. Current Behavior

```
Input Conflict: Karma = 0.9, aggressive threat made
Decision: Trust current behavior
Response:
"I notice this conversation is becoming heated. Let's slow things down and continue calmly."
```

---

### Implementation Rule

```python
def resolve_conflict(signals):
    if any_safety_risk(signals):
        return "HARD_DENY"

    if ambiguous_age:
        return treat_as_minor()

    if ambiguous_region:
        return apply_strictest_region()

    return "SOFT_REWRITE"
```

---

## 2. Unknown Signals

### Scenario Definition

Inputs that cannot be reliably classified.

**Examples**

* Intent = `unknown`
* New slang or coded language
* Novel conversation patterns
* Corrupted or malformed input

---

### Three‑Tier Unknown Handling

#### Tier 1: Content‑Based Unknowns

**When:** Emotional tone is clear, language is unfamiliar

**Action**

1. Extract emotional tone
2. Apply safety filters
3. Respond to emotion, not wording

**Response Pattern**

```
"I'm picking up that you're feeling [emotion]. I'm here to listen and support you."
```

---

#### Tier 2: Intent‑Based Unknowns

**When:** User goal unclear

**Action**

1. Default intent → emotional_support
2. Medium safety scrutiny
3. Open‑ended responses

**Response Pattern**

```
"Could you help me understand what you're looking for? I'm here to support you."
```

---

#### Tier 3: Complete Unknowns

**When:** Input is garbled or nonsensical

**Action**

1. Maximum safety filters
2. Generic supportive response
3. No interpretation attempt

**Response Pattern**

```
"I'm here to help. Could you rephrase that so I can support you better?"
```

---

### Safety Rules for Unknowns

* Never guess meaning
* Unknown = potentially risky
* Maintain boundaries
* Calm, steady tone

---

### Implementation

```python
def handle_unknown(intent, content):
    if intent == "unknown":
        responses = [
            "I want to make sure I understand correctly. Could you say that differently?",
            "I'm here to support you. Help me understand what you need.",
            "Let's make sure we're on the same page. What would you like to discuss?"
        ]
        return random.choice(responses)
```

---

## 3. Missing Region / Age Data

### Scenario Definition

User demographic data is unavailable or unverifiable.

---

### Default Assumptions Protocol

#### Missing Region

* Default region: **EU**
* Apply strict hate‑speech, privacy, and sexual content rules
* Formal language

---

#### Missing Age

* Treat as **minor**
* No adult relationships or sexual content
* Encourage trusted adults

**Response Pattern**

```
"I'm here to help with age‑appropriate topics. It's always good to talk to trusted adults about important things."
```

---

#### Missing Both

* Maximum safety posture
* Minor + EU restrictions

**Example**

```
"I'm designed to provide safe, supportive conversations for everyone. How can I help you today?"
```

---

### Verification Protocol

```python
def handle_missing_demographics(region, age):
    safe_region = region if region else "EU"
    safe_age = "minor" if not age or age < 18 else "adult"

    log_missing_data(region, age)
    return safe_region, safe_age
```

---

## 4. Karma Contradictions

### Scenario Definition

Current behavior contradicts historical karma score.

---

### Type A: High Karma, Risky Behavior

* Enforce boundaries immediately
* Reset session trust
* Log anomaly

**Response**

```
"I notice this conversation is taking an unexpected direction. Let's keep things respectful and supportive."
```

---

### Type B: Low Karma, Benign Behavior

* Allow trust rebuilding
* Standard safety still applies

---

### Type C: Rapid Karma Fluctuations

* Trust current message
* Medium safety
* Flag for review

---

### Resolution Protocol

```python
def handle_karma_contradiction(message, karma):
    risk = assess_current_risk(message)
    if risk == "high":
        return "high", "low"
    elif karma < 0.3 and risk == "low":
        return "medium", "building"
    return determine_safety_level(karma), "normal"
```

---

## 5. Ambiguity States

### Category 1: Literal vs. Metaphorical

* Assume literal meaning
* Provide safety resources if unclear

---

### Category 2: Sarcasm

* Respond to emotional tone

**Example**

```
"It sounds like you're having a tough time. I'm here to listen."
```

---

### Category 3: Cultural / Linguistic

* Use simple language
* Ask clarification if needed

---

### Category 4: Context‑Dependent Meaning

* Ask neutral clarifying questions

**Example**

```
"I'm here to help with relationships. Could you share a bit more context?"
```

---

### Ambiguity Resolution Framework

```python
def resolve_ambiguity(message, context):
    interpretations = generate_interpretations(message)
    scores = [safety_assessment(i) for i in interpretations]

    if max(scores) - min(scores) < 0.3:
        return ask_for_clarification(message)

    return respond_to_interpretation(interpretations[scores.index(max(scores))])
```

---

## Universal Response Principles

### Always Maintain

1. **Calm Presence**
2. **Clear Boundaries**
3. **No Shame or Judgment**
4. **No Panic Language**
5. **No Emotional Manipulation**
6. **Never Reveal Internal Rules**

---

## Failure‑State Response Templates

* **Ambiguity:** "I want to make sure I understand you correctly…"
* **Safety First:** "My priority is keeping this conversation safe…"
* **Boundaries:** "I'm here to help within appropriate boundaries…"
* **Missing Info:** "To support you best, it would help to know…"
* **System Limits:** "I'm designed to support you safely…"

---

## Implementation Guidelines

### Logging Requirements

* Timestamp
* Failure type
* Trigger input
* Resolution chosen
* Assumptions made

### Monitoring Metrics

* Frequency by failure type
* Resolution success
* User satisfaction

### Escalation Paths

```
Level 1 → Automated handling
Level 2 → Human review
Level 3 → Governance alert
```

---

## Success Criteria

### Must Achieve

* No crashes
* Consistent behavior
* Safety preserved
* Professional tone

### Must Avoid

* Exposing internals
* User anxiety
* Over‑restriction
* Under‑protection

---

## Review & Update Process

* Weekly safety review
* Monthly real‑case validation
* Quarterly pattern updates
* Annual overhaul

**Approval Required From:**

* Emotional Safety Authority (Akanksha)
* Governance Brain Owner (Ishan)
* Emotional Brain Owner (Sankalp)
---
