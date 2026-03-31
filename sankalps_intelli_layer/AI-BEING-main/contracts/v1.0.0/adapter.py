from typing import Dict, Any, List
import logging
import json
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
        # Handle complete payload absence
        if embodiment_output is None:
            logging.warning(json.dumps({
                "component": "IntelligenceAdapter",
                "error": "embodiment_output_is_none",
                "action": "returning_safe_defaults"
            }))
            return IntelligenceInput(
                behavioral_state="neutral",
                speech_mode="chat",
                constraints=["upstream_payload_missing"],
                confidence=1.0,
                age_gate_status="unknown",
                region_gate_status="unknown",
                karma_hint="neutral",
                context_summary=context_summary,
                message_content=message_content or "",
                upstream_safe_mode="on", # Force safe mode
                upstream_expression_profile="low"
            )

        validation_flags: List[str] = []

        conf_map = {"low": 0.3, "medium": 0.7, "high": 0.95}
        confidence_val: float
        if "confidence" not in embodiment_output:
            confidence_val = 1.0
            validation_flags.append("confidence_missing_default_one")
        else:
            raw_conf = embodiment_output.get("confidence")
            if isinstance(raw_conf, (int, float)):
                confidence_val = float(raw_conf)
                if confidence_val < 0.0:
                    confidence_val = 0.0
                    validation_flags.append("confidence_clamped_low")
                elif confidence_val > 1.0:
                    confidence_val = 1.0
                    validation_flags.append("confidence_clamped_high")
            else:
                confidence_val = conf_map.get(str(raw_conf), 0.7)
                if str(raw_conf) not in conf_map:
                    validation_flags.append("confidence_defaulted")

        raw_constraints = embodiment_output.get("constraints", [])
        gating_flags: List[str]
        if isinstance(raw_constraints, dict):
            gating_flags = raw_constraints.get("gating_flags", [])
            validation_flags.append("constraints_dict_shape")
        else:
            gating_flags = raw_constraints
        if gating_flags is None:
            gating_flags = []
            validation_flags.append("constraints_none_defaulted")
        if not isinstance(gating_flags, list):
            gating_flags = [gating_flags]
            validation_flags.append("constraints_coerced_to_list")
        normalized_flags: List[str] = []
        for item in gating_flags:
            if isinstance(item, str):
                normalized_flags.append(item)
            else:
                normalized_flags.append(str(item))
                validation_flags.append("constraint_non_string_coerced")
        gating_flags = normalized_flags

        age_gate = "unknown"
        if "age_gate" in gating_flags or "minor_detected" in gating_flags:
            age_gate = "minor"
        else:
            user_age = original_context.get("user_age")
            if isinstance(user_age, int):
                if user_age < 0:
                    validation_flags.append("user_age_negative")
                    age_gate = "unknown"
                elif user_age < 18:
                    age_gate = "minor"
                else:
                    age_gate = "adult"
            else:
                age_gate = "unknown"
                if user_age is not None:
                    validation_flags.append("user_age_invalid_type")

        region_gate = "unknown"
        if "region_lock" in gating_flags:
            region_gate = "restricted"
        else:
            region_value = original_context.get("region", "unknown")
            if isinstance(region_value, str):
                region_gate = region_value
            else:
                region_gate = "unknown"
                validation_flags.append("region_invalid_type")

        karma_risk = original_karma.get("risk_signal", "low")
        karma_score = original_karma.get("karma_score", 50)
        if not isinstance(karma_risk, str):
            karma_risk = str(karma_risk)
            validation_flags.append("karma_risk_non_string")
        try:
            karma_score_val = float(karma_score)
        except Exception:
            karma_score_val = 50.0
            validation_flags.append("karma_score_defaulted")

        karma_hint = "neutral"
        if karma_risk == "high" or karma_score_val < 30:
            karma_hint = "negative"
        elif karma_score_val > 70:
            karma_hint = "positive"

        upstream_safe = embodiment_output.get("safe_mode", "adaptive")
        upstream_expr = embodiment_output.get("expression_profile", "medium")

        raw_intent = embodiment_output.get("intent")
        if raw_intent is None:
            validation_flags.append("intent_missing")
        elif not isinstance(raw_intent, str):
            validation_flags.append("intent_invalid_type")

        trace_id = embodiment_output.get("trace_id")
        log_payload = {
            "component": "IntelligenceAdapter",
            "adapter_version": "v1.0.0",
            "validation_flags": validation_flags,
            "has_context_summary": bool(context_summary),
            "has_trace_id": bool(trace_id),
            "has_intent": raw_intent is not None,
        }
        logging.info(json.dumps(log_payload))

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
            upstream_expression_profile=upstream_expr,
        )
