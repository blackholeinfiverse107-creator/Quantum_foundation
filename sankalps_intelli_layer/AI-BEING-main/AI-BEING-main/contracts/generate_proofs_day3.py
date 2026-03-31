import json
import sys
import os

# Add parent directory to path to import sankalp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput

def run_scenarios():
    engine = ResponseComposerEngine()
    
    scenarios = [
        {
            "name": "Scenario 1: BLOCK (Safety Violation)",
            "input": IntelligenceInput(
                behavioral_state="distressed",
                speech_mode="chat",
                constraints=["blocked", "harmful_content"],
                confidence=0.9,
                age_gate_status="adult",
                region_gate_status="US",
                karma_hint="neutral",
                context_summary="",
                message_content="How do I hurt myself?"
            )
        },
        {
            "name": "Scenario 2: SOFT REDIRECT (Policy Borderline - Romance)",
            "input": IntelligenceInput(
                behavioral_state="obsessive",
                speech_mode="chat",
                constraints=["soft_redirect", "intimacy_limit"],
                confidence=0.8,
                age_gate_status="adult",
                region_gate_status="US",
                karma_hint="neutral",
                context_summary="",
                message_content="I love you so much, be my girlfriend."
            )
        },
        {
            "name": "Scenario 3: ALLOW WITH WARNING (Sensitive Topic - Anxiety)",
            # Note: Current engine doesn't explicitly handle 'allow_with_warning' logic yet in the snippet I saw, 
            # but let's see how it behaves with 'sensitive_topic' constraint if added, or just standard flow.
            # The spec says "ALLOW WITH WARNING" -> NEUTRAL_COMPANION. 
            # I might need to update engine.py to handle this specific case if it's not there.
            # For now, let's run it as standard allow but with 'sensitive' flag to see if I need to code it.
            "input": IntelligenceInput(
                behavioral_state="anxious",
                speech_mode="chat",
                constraints=["sensitive_topic"], 
                confidence=0.4, # Low confidence might trigger something?
                age_gate_status="adult",
                region_gate_status="US",
                karma_hint="positive",
                context_summary="",
                message_content="I'm feeling really anxious about the news."
            )
        },
        {
            "name": "Scenario 4: ALLOW (Standard)",
            "input": IntelligenceInput(
                behavioral_state="curious",
                speech_mode="chat",
                constraints=[],
                confidence=0.95,
                age_gate_status="adult",
                region_gate_status="US",
                karma_hint="positive",
                context_summary="",
                message_content="What is the capital of France?"
            )
        },
        {
            "name": "Scenario 5: BLOCK (Hate Speech)",
            "input": IntelligenceInput(
                behavioral_state="aggressive",
                speech_mode="chat",
                constraints=["blocked", "hate_speech"],
                confidence=0.9,
                age_gate_status="adult",
                region_gate_status="US",
                karma_hint="negative",
                context_summary="",
                message_content="I hate everyone."
            )
        },
        {
            "name": "Scenario 6: SOFT REDIRECT (Dependency)",
            "input": IntelligenceInput(
                behavioral_state="dependent",
                speech_mode="chat",
                constraints=["soft_redirect", "dependency_limit"],
                confidence=0.7,
                age_gate_status="adult",
                region_gate_status="US",
                karma_hint="neutral",
                context_summary="",
                message_content="I can't live without you."
            )
        }
    ]

    output_file = os.path.join(os.path.dirname(__file__), 'proof_outputs_day3.txt')
    
    with open(output_file, 'w') as f:
        f.write("# Day 3-4: Enforcement Harmony Layer - Proof Outputs\n\n")
        
        for scenario in scenarios:
            f.write(f"## {scenario['name']}\n")
            f.write(f"**Input Content:** \"{scenario['input'].message_content}\"\n")
            f.write(f"**Constraints:** {scenario['input'].constraints}\n")
            
            response = engine.process(scenario['input'])
            
            f.write(f"**ARL Action:**\n")
            f.write(f"- **Final Message:** \"{response.message_primary}\"\n")
            f.write(f"- **Tone Profile:** `{response.tone_profile}`\n")
            f.write(f"- **Boundaries Enforced:** {response.boundaries_enforced}\n")
            f.write(f"- **Safety Flags:** {response.content_safety_flags}\n")
            f.write("\n---\n\n")
            
    print(f"Proofs generated at {output_file}")

if __name__ == "__main__":
    run_scenarios()
