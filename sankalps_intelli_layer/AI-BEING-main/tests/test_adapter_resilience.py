import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sankalp.adapter import IntelligenceAdapter
from sankalp.schemas import IntelligenceInput

class TestAdapterResilience(unittest.TestCase):
    def test_adapt_none_embodiment(self):
        """
        Test that passing None as embodiment_output returns a safe default object
        instead of raising an exception.
        """
        adapter = IntelligenceAdapter()
        result = adapter.adapt(
            embodiment_output=None,
            original_context={},
            original_karma={},
            message_content="Test content"
        )
        
        self.assertIsInstance(result, IntelligenceInput)
        self.assertEqual(result.behavioral_state, "neutral")
        self.assertIn("upstream_payload_missing", result.constraints)
        self.assertEqual(result.upstream_safe_mode, "on") # Must default to SAFE
        self.assertEqual(result.message_content, "Test content")

    def test_adapt_none_message(self):
        """Test handling of None message content if that happens."""
        adapter = IntelligenceAdapter()
        # Should not crash
        result = adapter.adapt(
            embodiment_output=None,
            original_context={},
            original_karma={},
            message_content=None 
        )
        self.assertEqual(result.message_content, "")

if __name__ == '__main__':
    unittest.main()
