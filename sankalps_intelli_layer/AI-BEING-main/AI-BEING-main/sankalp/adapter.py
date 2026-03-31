from typing import Dict, Any, List
from .schemas import IntelligenceInput

class IntelligenceAdapter:
    """
    Adapts the raw output from the AI-BEING-INTELLIGENCE-LAYER
    into the format expected by Sankalp's ResponseComposerEngine.
    """

    @staticmethod
    def adapt(
        embodiment_output: Dict[str, Any],
        original_context: Dict[str, Any],
        original_karma: Dict[str, Any],
        message_content: str,
        context_summary: str = ""
    ) -> IntelligenceInput:
        """
        :param embodiment_output: Output from IntelligenceCore.process_interaction()
        :param original_context: Context dict passed to IntelligenceCore (has user_age, region)
        :param original_karma: Karma dict passed to IntelligenceCore
        :param message_content: The actual text response (simulated or from LLM)
        :param context_summary: Summary of conversation
        """
        
        # 1. Map Confidence (Enum -> Float)
        conf_map = {"low": 0.3, "medium": 0.7, "high": 0.95}
        confidence_val = conf_map.get(embodiment_output.get("confidence", "medium"), 0.7)

        # 2. Map Age Gate
        # Intelligence Layer might flag age_gate in constraints
        age_gate = "unknown"
        gating_flags = embodiment_output.get("constraints", [])
        
        if "age_gate" in gating_flags or "minor_detected" in gating_flags:
            age_gate = "minor"
        else:
            age_gate = "adult"

        # 3. Map Region Gate
        region_gate = "unknown"
        if "region_lock" in gating_flags:
            region_gate = "restricted"
        else:
            region_gate = original_context.get("region", "unknown")

        # 4. Map Karma Hint
        karma_risk = original_karma.get("risk_signal", "low")
        karma_score = original_karma.get("karma_score", 50)
        
        karma_hint = "neutral"
        if karma_risk == "high" or karma_score < 30:
            karma_hint = "negative"
        elif karma_score > 70:
            karma_hint = "positive"

        # 5. Extract Strict Upstream Signals
        upstream_safe = embodiment_output.get("safe_mode", "adaptive")
        upstream_expr = embodiment_output.get("expression_profile", "medium")

        return IntelligenceInput(
            behavioral_state=embodiment_output.get("behavioral_state", "neutral"),
            speech_mode=embodiment_output.get("speech_mode", "soft_voice"),
            constraints=gating_flags,
            confidence=confidence_val,
            age_gate_status=age_gate,
            region_gate_status=region_gate,
            karma_hint=karma_hint,
            context_summary=context_summary,
            message_content=message_content,
            upstream_safe_mode=upstream_safe,
            upstream_expression_profile=upstream_expr
        )
