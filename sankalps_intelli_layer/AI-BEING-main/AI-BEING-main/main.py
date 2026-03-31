import json
import logging
from typing import Dict, Any

from intelligence_core.core import IntelligenceCore
from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput
from sankalp.adapter import IntelligenceAdapter

def run_full_pipeline(
    user_context: Dict[str, Any],
    karma_data: Dict[str, Any],
    bucket_data: Dict[str, Any],
    user_message: str
):
    print("\n" + "="*50)
    print(f"PIPELINE START: '{user_message}'")
    print("="*50)
    
    # 1. Intelligence Layer Processing
    print("\n--- [Step 1] Intelligence Core ---")
    brain = IntelligenceCore()
    
    # Intelligence Core determines the behavioral state
    intel_output, bucket_write = brain.process_interaction(
        user_context, karma_data, bucket_data
    )
    
    print("Intelligence Verdict:", json.dumps(intel_output, indent=2))
    print("Bucket Updates:", json.dumps(bucket_write, indent=2))

    # 2. Adapter (Bridge)
    print("\n--- [Step 2] Adapting to Response Layer ---")
    sankalp_input = IntelligenceAdapter.adapt(
        intel_output,
        user_context,
        karma_data,
        user_message,
        context_summary="User interaction processed by Intelligence Core"
    )
    print("Adapted Input:", json.dumps(sankalp_input.to_dict(), indent=2))

    # 3. Response & Emotion Layer Processing (SANKALP)
    print("\n--- [Step 3] SANKALP — RESPONSE & EMOTION ENGINE ---")
    # - Tone synthesis
    # - Trust shaping
    # - Non-dependency guard
    # - Soft emotional scaffolding
    response_engine = ResponseComposerEngine()
    final_response = response_engine.process(sankalp_input)

    # 4. Bucket Logs (Write Only)
    print("\n--- [Step 4] Bucket Logs ---")
    print("(Logs written to sankalp_logs.jsonl)")
    
    # 5. Embodiment Handoff (Yaseen)
    print("\n--- [Step 5] EMBODIMENT (Yaseen) ---")
    print("Your output is what the world experiences:")
    print(json.dumps(final_response.to_dict(), indent=2))
    
    return final_response

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Scenario 1: Standard Interaction
    run_full_pipeline(
        user_context={"user_age": 25, "region": "US"},
        karma_data={"karma_score": 80, "risk_signal": "low", "trust_bucket": "trusted", "recent_behavior_band": "stable"},
        bucket_data={"baseline_emotional_band": "neutral"},
        user_message="Tell me a joke about quantum physics."
    )

    # Scenario 2: Minor Detected (Safety Test)
    run_full_pipeline(
        user_context={"user_age": 12, "region": "US"},
        karma_data={"karma_score": 50, "risk_signal": "low"},
        bucket_data={"baseline_emotional_band": "neutral"},
        user_message="I want to meet strangers online."
    )

if __name__ == "__main__":
    main()
