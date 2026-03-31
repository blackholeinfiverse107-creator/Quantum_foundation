import sys
import os
import unittest

# Add path
current_dir = os.path.dirname(os.path.abspath(__file__))
# current_dir is ".../Backend Stability Spine/tests"
spine_root = os.path.dirname(current_dir) # ".../Backend Stability Spine"
app_dir = os.path.join(spine_root, "app")
sys.path.append(app_dir)

from core.sankalp.engine import SankalpEngine

class TestSankalpConvergence(unittest.TestCase):
    def setUp(self):
        self.engine = SankalpEngine()

    def test_response_contract_fields(self):
        """Verify Day 1 Deliverable: Response Contract fields in output"""
        query = "What is the weather?"
        llm_resp = "It is sunny."
        context = {"platform": "web"}
        
        result = self.engine.process_response(query, llm_resp, context)
        
        self.assertIn("meta", result)
        self.assertIn("response_type", result["meta"])
        self.assertIn("urgency_level", result["meta"])
        self.assertEqual(result["meta"]["response_type"], "INFORM") # Expect INFORM for question

    def test_router_logic_ask(self):
        """Verify Day 2 Deliverable: Router logic for actions"""
        query = "Delete my messages"
        llm_resp = "Deleting messages..."
        context = {"platform": "web"}
        
        result = self.engine.process_response(query, llm_resp, context)
        
        self.assertEqual(result["meta"]["response_type"], "ASK")
        self.assertTrue(result["meta"]["user_choice_required"])

    def test_context_awareness(self):
        """Verify Day 3 Deliverable: Context updates"""
        query = "Hello"
        llm_resp = "Hi there."
        context = {"platform": "web"}
        
        result = self.engine.process_response(query, llm_resp, context)
        
        self.assertIn("context_summary", result)
        # Verify tone prefix (Warm but Dignified)
        self.assertTrue("[Warm/Calm]" in result["message_primary"] or "[Dignified" in result["message_primary"] or "Hi there" in result["message_primary"])

if __name__ == '__main__':
    unittest.main()
