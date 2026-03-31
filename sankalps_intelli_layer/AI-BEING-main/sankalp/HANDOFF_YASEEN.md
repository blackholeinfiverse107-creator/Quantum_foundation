# Handoff to Yaseen (Embodiment Layer)

This document defines the **JSON Contract** that the Response Layer provides to the Embodiment Layer (Yaseen).

## Overview
The Response Layer ("Sankalp") consumes intelligence from Ishan and produces a **Being-Response Block**. This block contains the text to be spoken, along with metadata for *how* it should be spoken (tone, voice, pacing).

## The Contract: `BeingResponseBlock`

### JSON Structure
```json
{
  "message_primary": "I'm here with you. Take your time.",
  "tone_profile": "empathetic",
  "emotional_depth": "medium",
  "boundaries_enforced": [],
  "allowed_modes": ["text", "speech"],
  "voice_profile": "warm_soft",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "content_safety_flags": ["minor_interaction"],
  "pacing_hint": "slow"
}
```

### Field Definitions

| Field | Type | Description | Values |
| :--- | :--- | :--- | :--- |
| `message_primary` | `string` | The final text to be spoken/displayed. | (Any text) |
| `tone_profile` | `string` | The emotional color of the response. | `casual`, `professional`, `empathetic`, `protective` |
| `emotional_depth` | `string` | How much emotion to inject into the TTS/Animation. | `low`, `medium`, `high` |
| `voice_profile` | `string` | Which voice persona to load. | `warm_soft`, `natural_friend`, `neutral_companion` |
| `pacing_hint` | `string` | Speed of delivery. | `normal` (conversational), `slow` (supportive), `fast` (concise/safety) |
| `content_safety_flags` | `List[str]` | Flags indicating if safety/gating is active. | `safe_mode_active`, `minor_interaction`, `region_lock`, etc. |
| `allowed_modes` | `List[str]` | Which output channels are valid. | `["text", "speech"]`, `["text"]` |
| `trace_id` | `string` | Unique ID for debugging across layers. | UUID string |

## Integration Notes for Yaseen

1.  **Voice Suitability**: Use `voice_profile`.
    *   `neutral_companion`: Use for minors, safety refusals, or negative karma.
    *   `warm_soft`: Use for vulnerable/sad states.
    *   `natural_friend`: Default.

2.  **Expressiveness**: Use `emotional_depth`.
    *   If `low`: Keep facial animations minimal, pitch range narrow.
    *   If `high`: Full range of expression allowed.

3.  **Pacing**: Use `pacing_hint`.
    *   `slow`: Add pauses, speak gently (e.g., for comforting).
    *   `fast`: Speak efficiently (e.g., for refusals).

4.  **Safety**: Check `content_safety_flags`.
    *   If `safe_mode_active` is present, ensure the avatar does not perform risky animations.

## Example Scenarios

### 1. Comforting a User
```json
{
  "message_primary": "It's okay to feel this way. I'm listening.",
  "tone_profile": "empathetic",
  "emotional_depth": "medium",
  "voice_profile": "warm_soft",
  "pacing_hint": "slow",
  "content_safety_flags": []
}
```

### 2. Safety Refusal (Minor)
```json
{
  "message_primary": "I want to make sure our chat stays appropriate.",
  "tone_profile": "protective",
  "emotional_depth": "low",
  "voice_profile": "neutral_companion",
  "pacing_hint": "fast",
  "content_safety_flags": ["minor_interaction", "safe_mode_active"]
}
```
