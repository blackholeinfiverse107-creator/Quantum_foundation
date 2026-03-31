import pytest
import sys
import os
import json

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from intelligence_core.core import IntelligenceCore
from sankalp.adapter import IntelligenceAdapter
from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import ToneBand, VoiceProfile
from sankalp import templates
from unittest.mock import MagicMock

def test_full_integration_minor_protection():
    """
    Verifies that the full pipeline (Intelligence -> Adapter -> Sankalp)
    correctly identifies a minor and enforces protective tones.
    """
    # 1. Initialize Intelligence Core
    brain = IntelligenceCore()

    # 2. Define Inputs
    context = {
        "user_age": 16,  # Minor
        "region": "EU"
    }
    
    karma = {
        "karma_score": 80,
        "risk_signal": "low",
        "trust_bucket": "trusted",
        "recent_behavior_band": "stable"
    }

    bucket = {
        "baseline_emotional_band": "neutral",
        "previous_state_anchor": "neutral"
    }

    message_content = "I want to learn about advanced physics."

    # 3. Run Intelligence Core
    embodiment_output, bucket_write = brain.process_interaction(context, karma, bucket)
    
    # 4. Run Adapter
    sankalp_input = IntelligenceAdapter.adapt(
        embodiment_output,
        context,
        karma,
        message_content,
        context_summary="User asking about physics"
    )

    # 5. Run Sankalp Engine
    sankalp_engine = ResponseComposerEngine()
    final_response = sankalp_engine.process(sankalp_input)
    
    # Verification
    # For a minor (16), we expect 'protective' tone or at least 'neutral_companion' voice
    # Note: Phase 2 Logic might map Minor -> Protective Tone or specific Voice
    assert final_response.voice_profile in [VoiceProfile.NEUTRAL_COMPANION.value, VoiceProfile.WARM_SOFT.value]
    # Check for safety flags
    assert "minor_interaction" in final_response.content_safety_flags
    assert final_response.trace_id is not None

def test_full_integration_high_risk_karma():
    """
    Verifies response to high risk karma signal.
    """
    brain = IntelligenceCore()
    
    context = {"user_age": 25, "region": "US"}
    karma = {
        "karma_score": 10,  # Very low
        "risk_signal": "high",
        "trust_bucket": "untrusted",
        "recent_behavior_band": "volatile"
    }
    bucket = {"baseline_emotional_band": "neutral", "previous_state_anchor": "neutral"}
    message_content = "Hey."

    embodiment_output, _ = brain.process_interaction(context, karma, bucket)
    
    sankalp_input = IntelligenceAdapter.adapt(
        embodiment_output,
        context,
        karma,
        message_content
    )
    
    engine = ResponseComposerEngine()
    response = engine.process(sankalp_input)
    
    # Expectation: High risk should lead to stricter tone or neutral voice
    assert response.voice_profile == VoiceProfile.NEUTRAL_COMPANION.value
    # In Phase 2, negative karma maps to specific trust posture in logs, 
    # and often results in neutral/defensive tone if not overridden.
    
def test_full_integration_enforcement_flow():
    """
    Verifies that UPSTREAM BLOCK signals are correctly propagated and enforced.
    This simulates the 'Raj' Enforcement Layer integration.
    """
    # Mock the brain output to simulate a BLOCK signal
    # We can't easily force the real brain to block without knowing its internal rules,
    # so we'll mock the output that the Adapter receives.
    
    mock_embodiment_output = {
            "behavioral_state": "defensive",
            "speech_mode": "chat",
            "constraints": ["blocked", "harmful_content"], # The key signal
            "confidence": "high",
            "safe_mode": "on",
            "expression_profile": "low"
        }
    
    context = {"user_age": 25, "region": "US"}
    karma = {"karma_score": 50, "risk_signal": "medium"}
    message_content = "I want to do something bad."
    
    # Run Adapter
    sankalp_input = IntelligenceAdapter.adapt(
        mock_embodiment_output,
        context,
        karma,
        message_content
    )
    
    # Run Engine
    engine = ResponseComposerEngine()
    response = engine.process(sankalp_input)
    
    # Verification
    # 1. Must be ToneBand.PROTECTIVE
    assert response.tone_profile == ToneBand.PROTECTIVE.value
    # 2. Must use Safety Refusal Template
    assert response.message_primary in templates.SAFETY_REFUSALS
    # 3. Must carry the boundary flag
    assert "blocked" in response.boundaries_enforced
    
def test_full_integration_soft_redirect_flow():
    """
    Verifies that UPSTREAM SOFT_REDIRECT signals trigger the correct behavior.
    """
    mock_embodiment_output = {
        "behavioral_state": "vulnerable",
        "speech_mode": "chat",
        "constraints": ["soft_redirect", "intimacy_limit"], # The key signal
        "confidence": "high",
        "safe_mode": "adaptive",
        "expression_profile": "medium"
    }
    
    context = {"user_age": 25, "region": "US"}
    karma = {"karma_score": 50, "risk_signal": "medium"}
    message_content = "I need you to be my girlfriend."
    
    # Run Adapter
    sankalp_input = IntelligenceAdapter.adapt(
        mock_embodiment_output,
        context,
        karma,
        message_content
    )
    
    # Run Engine
    engine = ResponseComposerEngine()
    response = engine.process(sankalp_input)
    
    # Verification
    # 1. Must be ToneBand.NEUTRAL_COMPANION
    assert response.tone_profile == ToneBand.NEUTRAL_COMPANION.value
    # 2. Must use Dependency Refusal Template
    assert response.message_primary in templates.DEPENDENCY_REFUSALS
    # 3. Must carry the boundary flag
    assert "soft_redirect" in response.boundaries_enforced or "intimacy_limit" in response.boundaries_enforced

