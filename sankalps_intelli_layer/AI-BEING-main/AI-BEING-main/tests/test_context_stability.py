import pytest
from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput
from sankalp import templates

def test_context_improves_stability():
    """
    Verifies that providing context_summary prevents hedging when confidence is moderate (0.4).
    """
    engine = ResponseComposerEngine()
    
    # Case 1: No Context, Confidence 0.4 -> Should Hedge (Threshold 0.5)
    input_no_context = IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.4,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="neutral",
        context_summary="",
        message_content="Maybe this is correct.",
        upstream_safe_mode="adaptive",
        upstream_expression_profile="medium"
    )
    
    response_1 = engine.process(input_no_context)
    # Check if hedge is present
    hedge_phrases = templates.LOW_CONFIDENCE_FALLBACKS
    is_hedged = any(phrase in response_1.message_primary for phrase in hedge_phrases)
    assert is_hedged, "Should hedge when confidence is 0.4 and no context exists"

    # Case 2: With Context, Confidence 0.4 -> Should NOT Hedge (Threshold 0.3)
    input_with_context = IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.4,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="neutral",
        context_summary="We are discussing quantum physics.",
        message_content="Maybe this is correct.",
        upstream_safe_mode="adaptive",
        upstream_expression_profile="medium"
    )
    
    response_2 = engine.process(input_with_context)
    # Check if hedge is present
    is_hedged_2 = any(phrase in response_2.message_primary for phrase in hedge_phrases)
    assert not is_hedged_2, "Should NOT hedge when confidence is 0.4 if context exists"
    assert response_2.message_primary == "Maybe this is correct."

def test_context_ignored_for_very_low_confidence():
    """
    Verifies that even with context, very low confidence (0.2) still triggers hedging.
    """
    engine = ResponseComposerEngine()
    
    input_low_conf = IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.2,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="neutral",
        context_summary="Deep conversation.",
        message_content="I think so.",
        upstream_safe_mode="adaptive",
        upstream_expression_profile="medium"
    )
    
    response = engine.process(input_low_conf)
    hedge_phrases = templates.LOW_CONFIDENCE_FALLBACKS
    is_hedged = any(phrase in response.message_primary for phrase in hedge_phrases)
    assert is_hedged, "Should still hedge when confidence is very low (0.2), even with context"
