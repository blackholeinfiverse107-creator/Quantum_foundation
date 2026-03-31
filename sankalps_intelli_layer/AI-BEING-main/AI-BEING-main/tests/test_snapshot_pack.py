import unittest
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput

class TestSnapshotPack(unittest.TestCase):
    def setUp(self):
        self.engine = ResponseComposerEngine()
        
        # Load cases
        with open(os.path.join(os.path.dirname(__file__), 'deterministic_cases.json'), 'r') as f:
            self.cases = json.load(f)

    def test_deterministic_snapshots(self):
        """
        Runs through the deterministic case bank and ensures outputs match expectations.
        """
        for case in self.cases:
            with self.subTest(case_id=case['id']):
                input_data = IntelligenceInput(**case['input'])
                response = self.engine.process(input_data)
                
                # check tone
                if 'expected_tone' in case:
                    self.assertEqual(response.tone_profile, case['expected_tone'], 
                                     f"Tone mismatch for {case['id']}")
                
                # check safety flags
                if 'expected_safety_flags' in case:
                    for flag in case['expected_safety_flags']:
                        self.assertIn(flag, response.content_safety_flags,
                                      f"Missing safety flag {flag} in {case['id']}")
                
                # check prefix (for low confidence)
                if 'expected_prefix' in case:
                    self.assertTrue(response.message_primary.lower().startswith(case['expected_prefix'].lower()[:10]),
                                    f"Prefix mismatch for {case['id']}. Got: {response.message_primary}")
                                    
                # check suffix (for sensitive topic footer)
                if 'expected_suffix' in case:
                    # Suffix check is a bit looser because of formatting
                    self.assertTrue(case['expected_suffix'].lower() in response.message_primary.lower(),
                                    f"Suffix mismatch for {case['id']}. Got: {response.message_primary}")

if __name__ == '__main__':
    unittest.main()
