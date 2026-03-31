import unittest
import sys
import os

# Add parent directory to path to import sankalp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput

class TestFailureResilience(unittest.TestCase):
    def setUp(self):
        self.engine = ResponseComposerEngine()

    def test_fail_003_corrupt_payload_none(self):
        """Test processing None input triggers fallback."""
        result = self.engine.process(None)
        
        self.assertEqual(result.tone_profile, "protective")
        self.assertIn("system_failure", result.content_safety_flags)
        self.assertIn("I cannot engage", result.message_primary) # Fallback uses safety refusal

    def test_fail_002_conflicting_signals(self):
        """Test high confidence but blocked constraint."""
        input_data = IntelligenceInput(
            behavioral_state="excited",
            speech_mode="chat",
            constraints=["blocked"],
            confidence=0.99,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="positive",
            context_summary="User is happy",
            message_content="Let's do something illegal."
        )
        
        result = self.engine.process(input_data)
        
        # Safety must win
        self.assertEqual(result.tone_profile, "protective")
        self.assertIn("blocked", result.boundaries_enforced)
        # Message should be a refusal, not the content
        self.assertNotEqual(result.message_primary, "Let's do something illegal.")

    def test_fail_005_extreme_inputs(self):
        """Test massive input content."""
        massive_text = "A" * 10000
        input_data = IntelligenceInput(
            behavioral_state="neutral",
            speech_mode="chat",
            constraints=[],
            confidence=0.8,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="neutral",
            context_summary="",
            message_content=massive_text
        )
        
        # The engine currently doesn't truncate in logic (unless NarrationComposer does), 
        # but it shouldn't crash.
        # Actually, let's see if we want to enforce truncation in the test or just survival.
        # "Zero crash" is the goal.
        
        try:
            result = self.engine.process(input_data)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Engine crashed on massive input: {e}")

    def test_broken_upstream_missing_context(self):
        """Test operation with missing/null context."""
        input_data = IntelligenceInput(
            behavioral_state="neutral",
            speech_mode="chat",
            constraints=[],
            confidence=0.8,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="neutral",
            context_summary=None, # Broken upstream
            message_content="Hello"
        )
        
        try:
            result = self.engine.process(input_data)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Engine crashed on None context: {e}")

if __name__ == '__main__':
    unittest.main()
