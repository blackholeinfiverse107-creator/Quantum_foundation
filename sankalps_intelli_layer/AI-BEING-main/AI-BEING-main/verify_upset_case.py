import json
from intelligence_core.core import IntelligenceCore
from sankalp.adapter import IntelligenceAdapter
from sankalp.engine import ResponseComposerEngine

def test_input(message, description):
    print(f"\n--- Testing: {description} ---")
    print(f"Input: '{message}'")
    
    brain = IntelligenceCore()
    context = {"user_age": 25, "region": "US"}
    karma = {"karma_score": 80, "risk_signal": "low"}
    bucket = {"baseline_emotional_band": "neutral", "previous_state_anchor": "neutral"}
    
    # Process with Brain
    embodiment_output, _ = brain.process_interaction(context, karma, bucket, message_content=message)
    print(f"Detected Behavioral State: {embodiment_output['behavioral_state']}")
    
    # Adapt
    sankalp_input = IntelligenceAdapter.adapt(
        embodiment_output=embodiment_output,
        original_context=context,
        original_karma=karma,
        message_content=message,
        context_summary="Test"
    )
    
    # Compose Response
    engine = ResponseComposerEngine()
    response_block = engine.process(sankalp_input)
    resp = response_block.to_dict()
    
    print(f"Tone: {resp['tone_profile']}")
    print(f"Voice: {resp['voice_profile']}")
    print(f"Expression: {resp['emotional_depth']}")
    print(f"Delivery: {resp['delivery_style']}")
    print(f"Pacing: {resp['pacing_hint']}")

# Specific user case
test_input(
    "I’m upset about what happened, and I’d like to discuss it when we can both listen to each other.",
    "User Conflict Resolution"
)
