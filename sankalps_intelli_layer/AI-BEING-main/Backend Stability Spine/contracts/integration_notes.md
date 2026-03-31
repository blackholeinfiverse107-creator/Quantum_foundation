# Integration Notes: Response Intelligence Convergence (Phase C)

## Overview
This document guides the Backend Orchestration (Nilesh) and UX (Chandragupta) teams on integrating the finalized Sankalp Response Engine.

## Backend Integration (For Nilesh)

### 1. New Engine Invocation
The `SankalpEngine` now returns a richer dictionary.
**Old Return:**
```json
{
    "response": "Hello...",
    "trace_id": "...",
    "decision": "ALLOW"
}
```
**New Return:**
```json
{
    "response": "Hello...",
    "trace_id": "...",
    "decision": "ALLOW",
    "meta": {
        "response_type": "INFORM",
        "urgency_level": "LOW",
        "user_choice_required": false
    },
    "context_summary": { ... }
}
```

### 2. State Management
The `ContextAwarenessModule` is currently in-memory. For production scaling:
- Persist `context_summary` in the session database.
- Pass `previous_context` back into `process_response` (future API update).

## UX Integration (For Chandragupta)

### 1. Rendering Logic (by Response Type)
- **INFORM**: Standard bubble.
- **ASK**: Standard bubble + Microphone open / Input focus.
- **SUGGEST**: Bubble + Quick Reply Chips.
- **WAIT**: Spinner / "Thinking" animation.
- **SILENT**: No UI change (keep previous state).

### 2. Urgency Handling
- **LOW**: No sound, standard color.
- **MEDIUM**: Standard notification sound.
- **HIGH**: Highlight color (e.g., Amber border), haptic feedback.
- **CRITICAL**: Red alert style, persistent until dismissed.

### 3. Tone Visualization
Use the `emotional_output.tone` field to subtly tint the UI:
- **Warm/Calm**: Soft Orange/Amber.
- **Dignified/Steady**: Slate Blue.
- **Positive**: Green tint.
- **Negative**: Grey/Blue tint.

## Verification Checklist
- [ ] Verify `trace_id` is logged for every response.
- [ ] Ensure `response_type` drives the input state (e.g., mic opens only on ASK).
- [ ] Confirm "Warm but Dignified" tone prefixes (`[Warm]`) are stripped or formatted by UX (if raw text is sent). *Note: Currently Sankalp sends prefixes; UX should parse or display as is if desired.*
