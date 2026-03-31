from typing import List, Optional
from .schemas import IntelligenceInput
from . import templates

class ContextContinuityEngine:
    """
    Day 1 Requirement: Multi-Turn Continuity Engine.
    - Implements rolling context summary logic (consumption side).
    - Maintains tone stability across turns.
    - Ensures no emotional escalation.
    """

    HEDGING_THRESHOLD_WITH_CONTEXT = 0.3
    HEDGING_THRESHOLD_NO_CONTEXT = 0.5

    @staticmethod
    def should_hedge(confidence: float, has_context: bool) -> bool:
        """
        Determines if the response should include hedging phrases based on confidence
        and presence of context.
        """
        threshold = (
            ContextContinuityEngine.HEDGING_THRESHOLD_WITH_CONTEXT
            if has_context
            else ContextContinuityEngine.HEDGING_THRESHOLD_NO_CONTEXT
        )
        return confidence < threshold

    @staticmethod
    def stabilize_tone(current_tone: str, previous_history: List[str] = None) -> str:
        """
        Prevents rapid tone switching (e.g., oscillating between Protective and Casual).
        For now, this is a placeholder for where stateful logic would sit if ARL held state.
        Since ARL is stateless, we rely on the Backend to pass `context_summary` which
        implicitly stabilizes the input `behavioral_state`.
        
        However, we can enforce 'De-Escalation' here.
        """
        # ARL is stateless, so we trust the input, but we can clamp extremes.
        # This method is exposed for future stateful integration.
        return current_tone

    @staticmethod
    def get_context_aware_refusal(constraints: List[str], context_summary: str) -> str:
        """
        Uses context to choose a slightly more specific refusal if safe,
        otherwise defaults to generic.
        """
        # Day 2: Enforcement Translation
        if "blocked" in constraints or "harmful_content" in constraints:
            return templates.get_safety_refusal()
        
        if "soft_redirect" in constraints:
            return templates.get_dependency_refusal()
            
        return templates.get_safety_refusal()
