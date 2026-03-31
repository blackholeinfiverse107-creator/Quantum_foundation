import sys
import os
import json

# Ensure we can import from local modules
sys.path.append(os.path.dirname(__file__))

from intelligence_core.core import IntelligenceCore
from sankalp.adapter import IntelligenceAdapter
from sankalp.engine import ResponseComposerEngine
from embodiment.renderer import EmbodimentRenderer

class AIBeingPipeline:
    def __init__(self):
        print("⚡ [SYSTEM] Initializing AI Being Pipeline...")
        self.brain = IntelligenceCore()
        self.heart = ResponseComposerEngine()
        self.voice = EmbodimentRenderer()
        print("✅ [SYSTEM] Pipeline Ready: Brain -> Heart -> Voice\n")

    def process_interaction(self, message: str, user_context: dict, karma_state: dict):
        print(f"📥 [INPUT] User: '{message}'")
        
        # --- STAGE 1: INTELLIGENCE LAYER (Ishan) ---
        print("🧠 [1/3] Processing in AI Being Intelligence Layer (Intelligence Core)...")
        # Mock bucket state for now
        bucket_state = {"baseline_emotional_band": "neutral", "previous_state_anchor": "neutral"}
        
        embodiment_output, _ = self.brain.process_interaction(
            context=user_context,
            karma_data=karma_state,
            bucket_data=bucket_state
        )
        # (Debug print optional)
        # print(f"   -> Raw Intent: {embodiment_output.get('behavioral_state')}")

        # --- ADAPTER: Bridge Intelligence -> Sankalp ---
        sankalp_input = IntelligenceAdapter.adapt(
            embodiment_output=embodiment_output,
            original_context=user_context,
            original_karma=karma_state,
            message_content=message,
            context_summary="Pipeline interaction"
        )

        # --- STAGE 2: RESPONSE & EMOTION LAYER (Sankalp) ---
        print("❤️  [2/3] Composing in Sankalp Layer...")
        response_block = self.heart.process(sankalp_input)
        
        # Convert to dict for transport
        response_dict = response_block.to_dict()

        # --- STAGE 3: EMBODIMENT LAYER (Yaseen) ---
        print("🗣️  [3/3] Rendering in Embodiment Layer...")
        self.voice.render(response_dict)

if __name__ == "__main__":
    pipeline = AIBeingPipeline()
    
    # Scenario 1: Normal Interaction
    context_1 = {"user_age": 25, "region": "US"}
    karma_1 = {"karma_score": 50, "risk_signal": "low"}
    pipeline.process_interaction("Hello, how are you?", context_1, karma_1)

    # Scenario 2: Minor Protection
    context_2 = {"user_age": 14, "region": "EU"}
    karma_2 = {"karma_score": 50, "risk_signal": "low"}
    pipeline.process_interaction("Can we talk about something mature?", context_2, karma_2)

    # Scenario 3: High Risk / Negative Karma
    context_3 = {"user_age": 30, "region": "US"}
    karma_3 = {"karma_score": 10, "risk_signal": "high"}
    pipeline.process_interaction("I hate everything.", context_3, karma_3)
