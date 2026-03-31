# SANKALP Interface Contracts

This document defines the strict contracts for the SANKALP Response & Emotion Engine.
These contracts must be honored by upstream (Intelligence Core/Ishan) and downstream (Embodiment/Yaseen) systems.

## 1. Upstream Contract (Input from Ishan)

The `IntelligenceInput` schema represents the decision state from the Intelligence Core.

```json
{
  "behavioral_state": "string (e.g., 'neutral', 'curious', 'defensive')",
  "speech_mode": "string (e.g., 'chat', 'monologue')",
  "constraints": ["string (e.g., 'minor_detected')"],
  "confidence": "float (0.0 - 1.0)",
  "age_gate_status": "string ('adult' | 'minor' | 'unknown')",
  "region_gate_status": "string ('US' | 'EU' | 'unknown')",
  "karma_hint": "string ('positive' | 'negative' | 'neutral')",
  "context_summary": "string",
  "message_content": "string (Raw thought/content)",
  "upstream_safe_mode": "string ('on' | 'adaptive' | 'off')",
  "upstream_expression_profile": "string ('low' | 'medium' | 'high')"
}
```

## 2. Downstream Contract (Output to Yaseen)

The `BeingResponseBlock` schema is the finalized instruction set for the Embodiment Layer.

```json
{
  "message_primary": "string (Final spoken/text content)",
  "tone_profile": "ToneBand Enum",
  "emotional_depth": "ExpressionLevel Enum",
  "boundaries_enforced": ["string"],
  "allowed_modes": ["string (e.g., 'text', 'speech')"],
  "voice_profile": "VoiceProfile Enum",
  "trace_id": "string (UUID)",
  "content_safety_flags": ["string"],
  "pacing_hint": "string ('fast' | 'slow' | 'normal')",
  "delivery_style": "DeliveryStyle Enum"
}
```

## 3. Enums & States

### VoiceProfile
- `warm_soft`: Empathetic, comforting.
- `natural_friend`: Casual, relatable.
- `neutral_companion`: Objective, calm (used in safe mode).

### ExpressionLevel (Emotional Spectrum)
- `low`: Minimal emotional variance (protective/professional).
- `medium`: Balanced engagement.
- `high`: Full emotional range (requires high confidence).

### DeliveryStyle
- `conversational`: Standard flow.
- `supportive`: Slower, more pauses.
- `concise`: Quick, direct information.

### ToneBand (Response States)
- `empathetic`: Focus on user feelings.
- `professional`: Focus on accuracy/facts.
- `casual`: Relaxed interaction.
- `protective`: Guarded, safety-first.

## 4. Emotional Philosophy Guardrails
- **Non-Addictive**: Phrases implying dependency ("I need you") are blocked.
- **Non-Exclusive**: Phrases implying unique connection ("Only you understand") are blocked.
- **Supportive**: Tone always leans towards constructive/calm.
