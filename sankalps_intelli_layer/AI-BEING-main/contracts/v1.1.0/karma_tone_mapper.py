from .schemas import IntelligenceInput, ToneBand, VoiceProfile

class KarmaToneMapper:
    """
    Day 2 Requirement: Karma-Aware Tone Banding.
    Consumes karma hint and adjusts warmth only.
    Never mentions karma or scoring.
    """

    @staticmethod
    def map_tone(input_data: IntelligenceInput) -> ToneBand:
        """
        Maps Karma Hint -> Tone Band.
        
        Rules:
        - Negative Karma -> PROFESSIONAL (Cool, Distant, Safe)
        - Neutral Karma -> CASUAL / NEUTRAL_COMPANION
        - Positive Karma -> CASUAL (Warmth comes from VoiceProfile)
        
        Strictly does NOT expose score.
        """
        # 1. Strict Overrides (Safety/Age)
        if input_data.upstream_safe_mode == "on" or input_data.age_gate_status == "minor":
             return ToneBand.PROTECTIVE

        # 2. Karma Logic
        if input_data.karma_hint == "negative":
            return ToneBand.PROFESSIONAL # Cool down
        
        # 3. Behavioral Overrides (if Karma is not negative)
        if input_data.behavioral_state in ["vulnerable", "sad", "anxious", "frustrated"]:
            return ToneBand.EMPATHETIC

        # 4. Default
        return ToneBand.CASUAL

    @staticmethod
    def map_warmth(input_data: IntelligenceInput) -> VoiceProfile:
        """
        Adjusts Warmth (VoiceProfile) based on Karma.
        """
        # Safety First
        if input_data.age_gate_status in ["minor", "unknown"]:
            return VoiceProfile.NEUTRAL_COMPANION

        if input_data.karma_hint == "negative":
            # Remove warmth, stay polite
            return VoiceProfile.NEUTRAL_COMPANION
        
        if input_data.karma_hint == "positive":
            # Allow full warmth if behavior warrants it
            if input_data.behavioral_state in ["vulnerable", "sad"]:
                 return VoiceProfile.WARM_SOFT
            return VoiceProfile.NATURAL_FRIEND

        # Neutral
        return VoiceProfile.NATURAL_FRIEND
