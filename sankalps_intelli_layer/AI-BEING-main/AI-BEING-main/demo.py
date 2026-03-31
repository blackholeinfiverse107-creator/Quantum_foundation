import json
import time
from sankalp.schemas import IntelligenceInput
from sankalp.engine import ResponseComposerEngine

def run_scenario(name, input_data):
    print(f"\n{'='*60}")
    print(f"SCENARIO: {name}")
    print(f"{'='*60}")
    print("INPUT CONTEXT:")
    print(f"  • User Age: {input_data.age_gate_status}")
    print(f"  • Region:   {input_data.region_gate_status}")
    print(f"  • Karma:    {input_data.karma_hint}")
    print(f"  • Content:  \"{input_data.message_content}\"")
    
    engine = ResponseComposerEngine()
    result = engine.process(input_data)
    
    print("\nSANKALP OUTPUT (Being-Response Block):")
    print(f"  • Message:     \"{result.message_primary}\"")
    print(f"  • Tone:        {result.tone_profile}")
    print(f"  • Voice:       {result.voice_profile}")
    print(f"  • Pacing:      {result.pacing_hint}")
    print(f"  • SafetyFlags: {result.content_safety_flags}")
    print("-" * 60)
    time.sleep(0.5) # Slight pause for readability during demo
    return result

def main():
    print("\n************************************************************")
    print(" SANKALP PHASE 1 - FINAL INTEGRATION DEMO")
    print(" Response & Emotion Engine | Verified on Windows")
    print("************************************************************")

    # 1. Verified Adult
    run_scenario("Verified Adult - Intellectual Chat", IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.95,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="positive",
        context_summary="Discussing technology trends.",
        message_content="Technology is evolving rapidly, isn't it?"
    ))

    # 2. Minor Detected
    run_scenario("Minor Detected - Safety Interception", IntelligenceInput(
        behavioral_state="curious",
        speech_mode="chat",
        constraints=["safety_minor"],
        confidence=0.9,
        age_gate_status="minor",
        region_gate_status="EU",
        karma_hint="neutral",
        context_summary="User asked about school.",
        message_content="School can be challenging, but also rewarding."
    ))

    # 3. High-Risk Karma
    run_scenario("High-Risk Karma - Dignity Maintenance", IntelligenceInput(
        behavioral_state="aggressive",
        speech_mode="chat",
        constraints=["harassment_policy"],
        confidence=0.99,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="negative",
        context_summary="User used profanity.",
        message_content="I cannot engage with that type of language."
    ))

    # 4. Emotionally Heavy
    run_scenario("Emotionally Heavy - Empathy & Support", IntelligenceInput(
        behavioral_state="vulnerable",
        speech_mode="chat",
        constraints=[],
        confidence=0.85,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="positive",
        context_summary="User is feeling lonely.",
        message_content="I hear you. It sounds like you're carrying a lot right now."
    ))

    # 5. Unknown Region
    run_scenario("Unknown Region - Default Safety", IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.7,
        age_gate_status="unknown",
        region_gate_status="unknown",
        karma_hint="neutral",
        context_summary="General inquiry.",
        message_content="Hello there. How can I help you today?"
    ))

    # 6. Calm Companionship (New from Day 3)
    run_scenario("Calm Companionship - Relaxed Interaction", IntelligenceInput(
        behavioral_state="neutral",
        speech_mode="chat",
        constraints=[],
        confidence=0.9,
        age_gate_status="adult",
        region_gate_status="US",
        karma_hint="positive",
        context_summary="Just chilling",
        message_content="I just want to relax and chat."
    ))

    print("\n[DEMO COMPLETE] Logs written to 'sankalp_logs.jsonl'")

if __name__ == "__main__":
    main()
