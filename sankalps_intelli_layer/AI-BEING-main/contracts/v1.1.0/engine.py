import uuid
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import List

from .schemas import IntelligenceInput, BeingResponseBlock, ToneBand
from .emotion import EmotionMapper
from .narration import NarrationComposer
from .karma_tone_mapper import KarmaToneMapper
from .context_continuity import ContextContinuityEngine
from . import templates

# Setup basic logging to simulate "Bucket logs"
logging.basicConfig(filename='sankalp_logs.jsonl', level=logging.INFO, format='%(message)s')

class ResponseComposerEngine:
    ENGINE_VERSION = "1.1.0"

    def __init__(self):
        self.emotion_mapper = EmotionMapper()
        self.narration_composer = NarrationComposer()
        self.karma_mapper = KarmaToneMapper()
        self.context_engine = ContextContinuityEngine()

    def process(self, input_data: IntelligenceInput) -> BeingResponseBlock:
        """
        Main pipeline: Input -> Emotion Mapping -> Narration Composition -> Output
        Wraps logic in a safety net to ensure a valid response is always returned.
        """
        try:
            return self._process_unsafe(input_data)
        except Exception as e:
            logging.error(f"CRITICAL ENGINE FAILURE: {e}")
            return self._create_fallback_response(input_data)

    def _process_unsafe(self, input_data: IntelligenceInput) -> BeingResponseBlock:
        # 1. Determine Emotional State (delegated to KarmaToneMapper for Tone/Warmth override)
        voice_profile = self.karma_mapper.map_warmth(input_data)
        expression_level = self.emotion_mapper.map_expression_level(input_data)
        delivery_style = self.emotion_mapper.map_delivery_style(input_data)
        tone_profile = self.karma_mapper.map_tone(input_data)

        # 2. Narration Composition (Deterministic Text Structuring)
        # "You own: voice of the Being, trust tone, structured response format, deterministic narration blocks"
        
        boundaries_enforced = []
        if input_data.constraints:
            boundaries_enforced.extend(input_data.constraints)

        # Phase 2: Handle Enforcement Signals (BLOCK, SOFT REDIRECT, REWRITE)
        # Check if constraints dictate a specific refusal type
        final_message = ""
        
        if "blocked" in boundaries_enforced or "harmful_content" in boundaries_enforced:
             final_message = self.context_engine.get_context_aware_refusal(boundaries_enforced, input_data.context_summary)
             # Override Tone to PROTECTIVE for safety
             tone_profile = ToneBand.PROTECTIVE
        elif "soft_redirect" in boundaries_enforced or "intimacy_limit" in boundaries_enforced:
             final_message = templates.get_dependency_refusal() 
             tone_profile = ToneBand.NEUTRAL_COMPANION
        elif "possessiveness" in boundaries_enforced:
             final_message = templates.get_possessiveness_refusal()
             tone_profile = ToneBand.NEUTRAL_COMPANION
        elif "sensitive_topic" in boundaries_enforced or "allow_warning" in boundaries_enforced:
             # ALLOW WITH WARNING
             tone_profile = ToneBand.NEUTRAL_COMPANION
             # We rely on NarrationComposer to append the warning based on constraints
             final_message = self.narration_composer.compose(
                raw_content=input_data.message_content,
                tone=tone_profile,
                confidence=input_data.confidence,
                constraints=boundaries_enforced, # Pass all constraints including sensitive_topic
                context_summary=input_data.context_summary
            )
        else:
             # Check for Hedging (Context Continuity)
             has_context = bool(input_data.context_summary)
             should_hedge = self.context_engine.should_hedge(input_data.confidence, has_context)
             
             final_message = self.narration_composer.compose(
                raw_content=input_data.message_content,
                tone=tone_profile,
                confidence=input_data.confidence,
                constraints=input_data.constraints,
                context_summary=input_data.context_summary
            )
             
             # If hedging is required and not handled by composer, we might inject it here,
             # but NarrationComposer usually handles confidence.
             # We verify that Tone is stable.
             # tone_profile = self.context_engine.stabilize_tone(tone_profile.value) 
             # (Skipping stateful stabilization for now as per design, trusting inputs)

        # 3. Construct the Response Block
        # Deterministic Trace ID: hash(IntelligenceInput + version)
        input_signature = json.dumps(input_data.to_dict(), sort_keys=True)
        raw_trace = f"{input_signature}{self.ENGINE_VERSION}"
        trace_id = hashlib.sha256(raw_trace.encode('utf-8')).hexdigest()
        
        # Determine allowed modes based on speech_mode
        # If speech_mode is "chat", we allow text and speech.
        # If "monologue", maybe just speech? For now, we allow both defaults.
        allowed_modes = ["text", "speech"] 
        if input_data.speech_mode == "silent":
             allowed_modes = ["text"]

        # Map DeliveryStyle to Pacing Hint
        pacing_map = {
            "concise": "fast",
            "supportive": "slow",
            "conversational": "normal"
        }
        pacing_hint = pacing_map.get(delivery_style.value, "normal")

        # Aggregate Safety Flags
        # Combine upstream constraints + any local detections
        content_safety_flags = []
        if input_data.upstream_safe_mode == "on":
            content_safety_flags.append("safe_mode_active")
        if input_data.age_gate_status == "minor":
            content_safety_flags.append("minor_interaction")
        content_safety_flags.extend(boundaries_enforced)

        response = BeingResponseBlock(
            message_primary=final_message,
            tone_profile=tone_profile.value,
            emotional_depth=expression_level.value,
            boundaries_enforced=boundaries_enforced,
            allowed_modes=allowed_modes,
            voice_profile=voice_profile.value,
            trace_id=trace_id,
            content_safety_flags=content_safety_flags,
            pacing_hint=pacing_hint,
            delivery_style=delivery_style.value
        )

        # 4. Log to Bucket (Write Only)
        self._log_response(input_data, response)

        return response

    def _create_fallback_response(self, input_data: IntelligenceInput) -> BeingResponseBlock:
        """
        Returns a safe, minimal response when the engine crashes.
        """
        return BeingResponseBlock(
            message_primary=templates.get_safety_refusal(),
            tone_profile="protective",
            emotional_depth="low",
            boundaries_enforced=["system_error"],
            allowed_modes=["text"],
            voice_profile="neutral_companion",
            trace_id=str(uuid.uuid4()),
            content_safety_flags=["system_failure"],
            pacing_hint="normal",
            delivery_style="concise"
        )

    def _log_response(self, input_data: IntelligenceInput, response: BeingResponseBlock):
        """
        Logs the interaction for analysis (Write Only).
        No private memory. No emotional blackmail tools.
        """
        
        # Derive Logic Fields
        # 1. Narration Intent
        if "minor_interaction" in response.content_safety_flags:
            intent = "safety_protection"
        elif "safe_mode_active" in response.content_safety_flags:
            intent = "safety_protection"
        elif response.tone_profile == "empathetic":
            intent = "emotional_support"
        else:
            intent = "information_delivery"

        # 2. Trust Posture
        # Derived from karma and confidence
        if input_data.karma_hint == "negative":
            trust_posture = "defensive"
        elif input_data.confidence < 0.5:
            trust_posture = "cautious"
        else:
            trust_posture = "open"

        # 3. Refusal Explanation
        refusal_explanation = None
        if response.boundaries_enforced:
            refusal_explanation = f"Blocked due to: {', '.join(response.boundaries_enforced)}"
        elif "minor_interaction" in response.content_safety_flags:
            refusal_explanation = "Age Gating Active"

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": response.trace_id,
            "narration_intent": intent,
            "emotional_outcome": response.tone_profile,
            "trust_posture": trust_posture,
            "refusal_explanation": refusal_explanation,
            # Core Metadata
            "input_behavior": input_data.behavioral_state,
            "output_voice": response.voice_profile,
            "boundaries": response.boundaries_enforced,
            "context_summary_used": bool(input_data.context_summary)
        }
        
        # Stateless Log - Fire and Forget
        logging.info(json.dumps(log_entry))

if __name__ == "__main__":
    # Quick self-test
    engine = ResponseComposerEngine()
    test_input = IntelligenceInput(
        behavioral_state="curious",
        speech_mode="chat",
        constraints=[],
        confidence=0.9,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="positive",
        context_summary="User asked about weather",
        message_content="The weather is quite sunny today."
    )
    result = engine.process(test_input)
    print(json.dumps(result.to_dict(), indent=2))
