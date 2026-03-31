import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sankalp.schemas import IntelligenceInput, ToneBand, VoiceProfile
from sankalp.karma_tone_mapper import KarmaToneMapper

class TestKarmaToneMapper(unittest.TestCase):
    def test_positive_karma_warmth(self):
        """Positive Karma should unlock Warmth if behavior matches."""
        input_data = IntelligenceInput(
            behavioral_state="vulnerable",
            speech_mode="chat",
            constraints=[],
            confidence=0.9,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="positive", # User is trusted
            context_summary="",
            message_content="I feel sad."
        )
        warmth = KarmaToneMapper.map_warmth(input_data)
        self.assertEqual(warmth, VoiceProfile.WARM_SOFT)

    def test_negative_karma_cooling(self):
        """Negative Karma should force Neutral/Professional tone."""
        input_data = IntelligenceInput(
            behavioral_state="vulnerable", # Even if vulnerable
            speech_mode="chat",
            constraints=[],
            confidence=0.9,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="negative", # User is abusive/untrusted
            context_summary="",
            message_content="I feel sad."
        )
        
        warmth = KarmaToneMapper.map_warmth(input_data)
        self.assertEqual(warmth, VoiceProfile.NEUTRAL_COMPANION)
        
        tone = KarmaToneMapper.map_tone(input_data)
        self.assertEqual(tone, ToneBand.PROFESSIONAL)

    def test_neutral_karma_default(self):
        """Neutral Karma behaves normally."""
        input_data = IntelligenceInput(
            behavioral_state="happy",
            speech_mode="chat",
            constraints=[],
            confidence=0.9,
            age_gate_status="adult",
            region_gate_status="US",
            karma_hint="neutral",
            context_summary="",
            message_content="Hello."
        )
        warmth = KarmaToneMapper.map_warmth(input_data)
        self.assertEqual(warmth, VoiceProfile.NATURAL_FRIEND)
        
        tone = KarmaToneMapper.map_tone(input_data)
        self.assertEqual(tone, ToneBand.CASUAL)

if __name__ == '__main__':
    unittest.main()
