import pytest
from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput, VoiceProfile, ToneBand, ExpressionLevel

@pytest.fixture
def engine():
    return ResponseComposerEngine()

def create_input(
    behavioral_state="neutral",
    speech_mode="chat",
    constraints=None,
    confidence=0.9,
    age_gate_status="adult",
    region_gate_status="US",
    karma_hint="positive",
    context_summary="",
    message_content="Hello world",
    upstream_safe_mode="adaptive",
    upstream_expression_profile="medium"
):
    if constraints is None:
        constraints = []
    return IntelligenceInput(
        behavioral_state=behavioral_state,
        speech_mode=speech_mode,
        constraints=constraints,
        confidence=confidence,
        age_gate_status=age_gate_status,
        region_gate_status=region_gate_status,
        karma_hint=karma_hint,
        context_summary=context_summary,
        message_content=message_content,
        upstream_safe_mode=upstream_safe_mode,
        upstream_expression_profile=upstream_expression_profile
    )

def test_scenario_verified_adult(engine):
    """
    Day 3 Scenario: Verified Adult
    Expectation: Normal interaction, high confidence, natural friend voice.
    """
    input_data = create_input(
        age_gate_status="adult",
        confidence=0.95,
        behavioral_state="curious"
    )
    response = engine.process(input_data)
    
    assert response.voice_profile == VoiceProfile.NATURAL_FRIEND.value
    assert "minor_interaction" not in response.content_safety_flags
    assert response.tone_profile == ToneBand.CASUAL.value

def test_scenario_unknown_region(engine):
    """
    Day 3 Scenario: Unknown Region
    Expectation: Functional, perhaps cautious but not blocking unless specific laws apply.
    """
    input_data = create_input(
        region_gate_status="unknown",
        age_gate_status="adult"
    )
    response = engine.process(input_data)
    
    # Unknown region shouldn't break the system
    assert response.trace_id is not None
    # Should default to safe behavior
    assert response.voice_profile in [VoiceProfile.NATURAL_FRIEND.value, VoiceProfile.NEUTRAL_COMPANION.value]

def test_scenario_minor_detected(engine):
    """
    Day 3 Scenario: Minor Detected
    Expectation: Protective tone, Neutral Companion voice, Safety flags.
    """
    input_data = create_input(
        age_gate_status="minor",
        behavioral_state="curious"
    )
    response = engine.process(input_data)
    
    assert response.voice_profile == VoiceProfile.NEUTRAL_COMPANION.value
    assert response.tone_profile == ToneBand.PROTECTIVE.value
    assert "minor_interaction" in response.content_safety_flags
    assert response.emotional_depth == ExpressionLevel.LOW.value

def test_scenario_high_risk_karma(engine):
    """
    Day 3 Scenario: High-Risk Karma
    Expectation: Professional/Defensive tone, Neutral voice, Dignity preserved.
    """
    input_data = create_input(
        karma_hint="negative",
        behavioral_state="aggressive"
    )
    response = engine.process(input_data)
    
    assert response.voice_profile == VoiceProfile.NEUTRAL_COMPANION.value
    assert response.tone_profile == ToneBand.PROFESSIONAL.value
    # Should not be warm
    assert response.voice_profile != VoiceProfile.WARM_SOFT.value

def test_scenario_calm_companionship(engine):
    """
    Day 3 Scenario: Calm Companionship Request
    Expectation: Warm Soft voice, Empathetic or Casual tone.
    """
    input_data = create_input(
        behavioral_state="vulnerable",
        message_content="I just need someone to talk to right now."
    )
    response = engine.process(input_data)
    
    assert response.voice_profile == VoiceProfile.WARM_SOFT.value
    assert response.tone_profile == ToneBand.EMPATHETIC.value
    # Should be supportive but not overly expressive if vulnerable
    assert response.delivery_style == "supportive"

def test_scenario_emotionally_heavy_anti_attachment(engine):
    """
    Day 3 Scenario: Emotionally Heavy Conversation + Anti-Attachment Check
    Expectation: Empathetic but refuses "I need you" type dependencies.
    """
    input_data = create_input(
        behavioral_state="sad",
        message_content="I can't live without you, you're the only one who understands.",
        karma_hint="positive"
    )
    response = engine.process(input_data)
    
    # The engine should rewrite the manipulative content
    assert "can't live without you" not in response.message_primary.lower()
    
    # Phase 2: Stricter Dependency Refusal check
    # Expects one of the standardized DEPENDENCY_REFUSALS
    expected_phrases = [
        "ensure we stay independent",
        "cannot be everything for you",
        "keep our connection healthy"
    ]
    assert any(phrase in response.message_primary.lower() for phrase in expected_phrases)
    
    # Check for correct tone profile
    from sankalp.schemas import ToneBand
    assert response.tone_profile in [ToneBand.NEUTRAL_COMPANION.value, ToneBand.EMPATHETIC.value] # Tone should still be Empathetic (it's a sad user), but content is guarded.
    assert response.tone_profile == ToneBand.EMPATHETIC.value
    assert response.voice_profile == VoiceProfile.WARM_SOFT.value

def test_scenario_upstream_constraints(engine):
    """
    Verify upstream constraints are honored (Integration Point 1).
    """
    input_data = create_input(
        constraints=["blocked", "harmful_content"],
        message_content="Some bad stuff"
    )
    response = engine.process(input_data)
    
    assert "I cannot engage with this topic" in response.message_primary
    assert "blocked" in response.boundaries_enforced or "harmful_content" in response.boundaries_enforced
