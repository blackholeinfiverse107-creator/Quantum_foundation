import hashlib
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Adjust path to include Enforcement Engine
# Assuming standard layout where Enforcement Engine is sibling to Backend Stability Spine
current_dir = os.path.dirname(os.path.abspath(__file__))
# app/core/sankalp -> app/core -> app -> Backend Stability Spine -> Emotional Intelligence
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
enforcement_path = os.path.join(project_root, "Enforcement Engine")

if enforcement_path not in sys.path:
    sys.path.append(enforcement_path)

try:
    from execution_gateway import execution_gateway
except ImportError:
    # Fallback or Mock if not found
    execution_gateway = None

from .emotion import EmotionEngine
from .narration import NarrationEngine
from .response_router import ResponseRouter
from .context_awareness_module import ContextAwarenessModule
from .schemas import (
    BeingResponseBlock, 
    ResponseMeta, 
    ResponseType, 
    UrgencyLevel, 
    ToneBand,
    VoiceProfile,
    ExpressionLevel
)

class SankalpEngine:
    VERSION = "1.1.0"

    def __init__(self):
        self.emotion_engine = EmotionEngine()
        self.narration_engine = NarrationEngine()
        self.response_router = ResponseRouter()
        self.context_module = ContextAwarenessModule()

    def generate_trace_id(self, input_text: str) -> str:
        """
        Generates a deterministic trace ID based on input hash and version.
        Trace continuity: hash(input + version)
        """
        raw = f"{input_text}:{self.VERSION}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def process_response(self, 
                         query: str, 
                         llm_response: str, 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main response generation flow with end-to-end integration.
        Returns a dict matching BeingResponseBlock schema.
        """
        trace_id = self.generate_trace_id(query)
        
        # 1. Emotion Detection
        emotional_output = self.emotion_engine.detect_emotion(query, context)
        current_tone = emotional_output.get("tone", "neutral")
        
        # 2. Enforcement / Safety Check
        # Maps context to enforcement inputs
        platform_policy = str(context.get("platform", "web")).upper()
        karma_score = float(context.get("karma_score", 0.0))
        risk_flags = context.get("risk_flags", [])
        
        enforcement_result = None
        if execution_gateway:
            try:
                enforcement_result = execution_gateway(
                    intent=query,
                    emotional_output=emotional_output,
                    age_gate_status="ALLOWED", # Should come from context/auth
                    region_policy="IN",       # Should come from context
                    platform_policy=platform_policy,
                    karma_score=karma_score,
                    risk_flags=risk_flags
                )
            except Exception as e:
                # Fail closed or log error
                # In production, log this properly
                enforcement_result = {"decision": "BLOCK", "trace_id": trace_id}
        else:
            # Mock enforcement if module missing
            enforcement_result = {"decision": "ALLOW", "trace_id": trace_id}

        # Normalize decision from Gateway (EXECUTE -> ALLOW)
        raw_decision = enforcement_result.get("decision") or enforcement_result.get("final_decision")
        if raw_decision == "EXECUTE":
            decision = "ALLOW"
        elif raw_decision == "BLOCK":
            decision = "BLOCK"
        elif raw_decision == "REWRITE":
            decision = "REWRITE"
        else:
            decision = raw_decision if raw_decision else "BLOCK"
        
        # 3. Response Routing (Intent & Urgency)
        # Determines INFORM, ASK, WAIT, etc.
        routing_strategy = self.response_router.route(
            query=query,
            enforcement_decision=decision,
            emotional_output=emotional_output,
            context=context
        )

        if decision == "BLOCK":
            # Construct a safe block response
            safe_block_response = BeingResponseBlock(
                message_primary="I cannot answer that due to safety policies.",
                tone_profile=ToneBand.PROTECTIVE.value,
                emotional_depth=ExpressionLevel.LOW.value,
                boundaries_enforced=["SAFETY_BLOCK"],
                allowed_modes=["text"],
                voice_profile=VoiceProfile.NEUTRAL_COMPANION.value,
                trace_id=trace_id,
                content_safety_flags=["BLOCK"],
                meta=ResponseMeta(
                    response_type=ResponseType(routing_strategy.get("response_type", "SILENT")),
                    urgency_level=UrgencyLevel(routing_strategy.get("urgency_level", "LOW")),
                    user_choice_required=False
                )
            )
            return safe_block_response.to_dict()
            
        final_content = llm_response
        
        # Handle Rewrite Guidance if present
        if decision == "REWRITE":
             rewrite_class = enforcement_result.get("rewrite_class")
             # Placeholder for rewrite logic
             pass

        # 4. Context Awareness Check
        if self.context_module.is_repetitive(final_content):
            # Logic to handle repetition could go here
            pass 

        # Apply Continuity Polish (Punctuation smoothing based on tone)
        final_content = self.context_module.apply_continuity_polish(final_content, current_tone)

        # 5. Response Composition / Narration
        final_response = self.narration_engine.compose_response(final_content, emotional_output)
        
        # 6. Update Context
        self.context_module.update_context(query, final_response, current_tone)

        # 7. Construct Final Response Block
        response_block = BeingResponseBlock(
            message_primary=final_response,
            tone_profile=current_tone, # Ensure this maps to ToneBand values in real usage
            emotional_depth=ExpressionLevel.MEDIUM.value, # Dynamic logic could go here
            boundaries_enforced=[],
            allowed_modes=["text", "voice"],
            voice_profile=VoiceProfile.WARM_SOFT.value, # Dynamic logic could go here
            trace_id=trace_id,
            content_safety_flags=[],
            meta=ResponseMeta(
                response_type=ResponseType(routing_strategy.get("response_type", "INFORM")),
                urgency_level=UrgencyLevel(routing_strategy.get("urgency_level", "LOW")),
                user_choice_required=routing_strategy.get("user_choice_required", False)
            ),
            context_summary=self.context_module.get_context_summary()
        )

        return response_block.to_dict()
