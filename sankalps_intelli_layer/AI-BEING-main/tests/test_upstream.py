import json
import sys
import os

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sankalp.schemas import IntelligenceInput, BeingResponseBlock, ToneBand, ExpressionLevel
from sankalp.engine import ResponseComposerEngine
from sankalp.adapter import IntelligenceAdapter

def test_upstream_integration():
    print("--- Testing Upstream Integration Compliance ---")
    
    # Mock Upstream Output (EmbodimentOutput)
    # Scenario 1: Strict Safety Override
    upstream_output_safe = {
        "behavioral_state": "excited", # Usually implies HIGH expression
        "expression_profile": "medium",
        "safe_mode": "on", # SHOULD force PROTECTIVE tone
        "speech_mode": "soft_voice",
        "confidence": "high",
        "constraints": {"gating_flags": ["safety_lock"]},
        "timestamp": "2024-01-01T00:00:00Z",
        "trace_id": "123"
    }
    
    adapter = IntelligenceAdapter()
    engine = ResponseComposerEngine()
    
    # Adapt
    input_data = adapter.adapt(
        embodiment_output=upstream_output_safe,
        original_context={"user_age": 25, "region": "US"},
        original_karma={"risk_signal": "low", "karma_score": 50},
        message_content="I am so excited!"
    )
    
    # Process
    response = engine.process(input_data)
    
    print(f"\nScenario 1 (Safe Mode ON):")
    print(f"Upstream Behavioral: {upstream_output_safe['behavioral_state']}")
    print(f"Upstream Safe Mode: {upstream_output_safe['safe_mode']}")
    print(f"Result Tone: {response.tone_profile}")
    
    if response.tone_profile == ToneBand.PROTECTIVE:
        print("PASS: Safe Mode ON forced PROTECTIVE tone.")
    else:
        print(f"FAIL: Expected PROTECTIVE, got {response.tone_profile}")

    # Scenario 2: Expression Ceiling
    upstream_output_constrained = {
        "behavioral_state": "excited", # Wants HIGH
        "expression_profile": "low",   # Ceiling is LOW
        "safe_mode": "off",
        "speech_mode": "expressive_voice",
        "confidence": "high",
        "constraints": {"gating_flags": []},
        "timestamp": "2024-01-01T00:00:00Z",
        "trace_id": "456"
    }

    input_data_2 = adapter.adapt(
        embodiment_output=upstream_output_constrained,
        original_context={"user_age": 25, "region": "US"},
        original_karma={"risk_signal": "low", "karma_score": 50},
        message_content="I am so happy!"
    )
    
    response_2 = engine.process(input_data_2)
    
    print(f"\nScenario 2 (Expression Ceiling):")
    print(f"Upstream Behavioral: {upstream_output_constrained['behavioral_state']} (Wants HIGH)")
    print(f"Upstream Expression: {upstream_output_constrained['expression_profile']} (Limit LOW)")
    print(f"Result Depth: {response_2.emotional_depth}")
    
    if response_2.emotional_depth == ExpressionLevel.LOW:
        print("PASS: Expression ceiling honored.")
    else:
        print(f"FAIL: Expected LOW, got {response_2.emotional_depth}")


def test_adapter_validation_and_defaults():
    adapter = IntelligenceAdapter()

    upstream_output = {
        "behavioral_state": "neutral",
        "expression_profile": "medium",
        "safe_mode": "adaptive",
        "speech_mode": "chat",
        "confidence": 2.5,
        "constraints": {"gating_flags": ["age_gate", 123]},
        "trace_id": "abc",
    }

    input_data = adapter.adapt(
        embodiment_output=upstream_output,
        original_context={"user_age": 15, "region": "US"},
        original_karma={"risk_signal": "low", "karma_score": "75"},
        message_content="Hello",
    )

    assert isinstance(input_data.constraints, list)
    assert input_data.constraints == ["age_gate", "123"]
    assert input_data.age_gate_status == "minor"
    assert input_data.region_gate_status == "US"
    assert 0.0 <= input_data.confidence <= 1.0
    assert input_data.confidence == 1.0
    assert input_data.karma_hint == "positive"
if __name__ == "__main__":
    test_upstream_integration()
