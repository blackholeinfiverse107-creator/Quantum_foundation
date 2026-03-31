import pytest
from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput

def test_trace_id_determinism():
    engine = ResponseComposerEngine()
    
    input_data_1 = IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.9,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="neutral",
        context_summary="User asked a question.",
        message_content="Hello world",
        upstream_safe_mode="adaptive",
        upstream_expression_profile="medium"
    )
    
    # Run 1
    response_1 = engine.process(input_data_1)
    
    # Run 2 (Same Input)
    response_2 = engine.process(input_data_1)
    
    # Assert Determinism
    assert response_1.trace_id == response_2.trace_id, "Trace ID should be identical for identical inputs"
    assert len(response_1.trace_id) > 0
    
    # Run 3 (Different Input)
    input_data_2 = input_data_1.to_dict()
    input_data_2["message_content"] = "Hello universe"
    # Reconstruct object
    input_data_2_obj = IntelligenceInput(**input_data_2)
    
    response_3 = engine.process(input_data_2_obj)
    
    assert response_1.trace_id != response_3.trace_id, "Trace ID should differ for different inputs"

def test_trace_id_version_impact():
    engine = ResponseComposerEngine()
    
    input_data = IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.9,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="neutral",
        context_summary="User asked a question.",
        message_content="Hello world",
        upstream_safe_mode="adaptive",
        upstream_expression_profile="medium"
    )
    
    response_1 = engine.process(input_data)
    
    # Simulate Version Change
    original_version = engine.ENGINE_VERSION
    engine.ENGINE_VERSION = "1.0.1"
    
    response_2 = engine.process(input_data)
    
    # Restore Version
    engine.ENGINE_VERSION = original_version
    
    assert response_1.trace_id != response_2.trace_id, "Trace ID should differ when engine version changes"
