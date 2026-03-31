# Response Layer (formerly Sankalp)

## Overview
The Response Layer acts as the bridge between the **Intelligence Core** and the **Embodiment**. It is responsible for:
1.  **Tone Synthesis**: Converting behavioral states into specific voice/tone profiles.
2.  **Safety & Trust**: Enforcing boundaries and maintaining a non-manipulative, dignified presence.
3.  **Deterministic Narration**: Ensuring the Being's response is stable and consistent.

## Integration Points

### Input: From Intelligence Core
The system uses an **Adapter** to consume the raw `EmbodimentOutput` from the `intelligence_core` package.
See `response_layer/adapter.py`.

The internal `IntelligenceInput` object contains:
-   `behavioral_state`: (e.g., "curious", "defensive")
-   `constraints`: List of safety policy strings.
-   `age_gate_status`: "adult" | "minor" | "unknown"
-   `karma_hint`: "positive" | "negative" | "neutral"
-   `confidence`: float (0.0 - 1.0)

### Output: To Embodiment
The system produces a `BeingResponseBlock`:
-   `message_primary`: The text to be spoken.
-   `tone_profile`: "empathetic" | "professional" | "casual" | "protective"
-   `voice_profile`: "warm_soft" | "natural_friend" | "neutral_companion"
-   `emotional_depth`: "low" | "medium" | "high"
-   `delivery_style`: "conversational" | "supportive" | "concise"

## Hard Rules & Philosophy
1.  **Do NOT Emotionally Trap**: We do not build dependence.
2.  **Do NOT Overshare**: The Being maintains dignity.
3.  **Do NOT Fake Safety**: If Intelligence Core flags a constraint, the Response Layer enforces it.
4.  **Age Gating**: If `age_gate_status` is "minor" or "unknown", the system defaults to `VoiceProfile.NEUTRAL_COMPANION` and `ToneBand.PROTECTIVE`.

## Directory Structure
-   `engine.py`: Main entry point (`ResponseComposerEngine`).
-   `adapter.py`: Adapter for Intelligence Core outputs.
-   `emotion.py`: Logic for mapping input state to emotional parameters (`EmotionMapper`).
-   `schemas.py`: Data contracts (Input/Output/Enums).
-   `templates.py`: Deterministic fallback phrases for safety/refusal.
-   `demo.py`: Executable script to verify standalone scenarios.
-   `integration_test.py`: Full verification script using the Intelligence Core.

## How to Run
See the root `README.md` for full system instructions.

### Standalone Demo
```bash
python -m response_layer.demo
```
