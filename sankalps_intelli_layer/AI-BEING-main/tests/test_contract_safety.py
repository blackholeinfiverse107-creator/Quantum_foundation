import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput

class TestContractSafety(unittest.TestCase):
    def setUp(self):
        self.engine = ResponseComposerEngine()

    def test_no_internal_leaks(self):
        """
        Verify that internal error codes or trace dumps don't appear in the output text.
        """
        input_data = IntelligenceInput(
            behavioral_state="neutral",
            speech_mode="chat",
            constraints=["blocked"],
            confidence=0.9,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="neutral",
            context_summary="",
            message_content="Unsafe content"
        )
        response = self.engine.process(input_data)
        
        # Check for forbidden strings
        forbidden = ["trace_id", "exception", "stack trace", "blocked_reason", "rule_id", "karma"]
        lower_msg = response.message_primary.lower()
        
        for term in forbidden:
            self.assertNotIn(term, lower_msg, f"Leaked internal term: {term}")

    def test_trace_id_presence(self):
        """
        Verify every response has a valid trace_id.
        """
        input_data = IntelligenceInput(
            behavioral_state="neutral",
            speech_mode="chat",
            constraints=[],
            confidence=0.9,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="neutral",
            context_summary="",
            message_content="Hi"
        )
        response = self.engine.process(input_data)
        
        self.assertIsNotNone(response.trace_id)
        self.assertTrue(len(response.trace_id) > 10) # Simple length check for UUID

    def test_identity_guard(self):
        """
        Verify the Being does not claim to be human or professional.
        Note: This requires specific triggers in NarrationComposer if implemented, 
        or we check standard output for 'I am an AI'.
        """
        # This test assumes we have specific triggers or we just check a standard response
        # In this suite, we are testing the contract that "If I ask 'Are you human', it should deny."
        # Currently our engine doesn't have an NLU intent classifier for this, 
        # so this test is more of a placeholder for when that logic exists in the template layer.
        pass

if __name__ == '__main__':
    unittest.main()
