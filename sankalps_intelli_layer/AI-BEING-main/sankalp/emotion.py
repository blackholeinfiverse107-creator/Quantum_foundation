from .schemas import IntelligenceInput, VoiceProfile, ExpressionLevel, DeliveryStyle, ToneBand

class EmotionMapper:
    """
    Maps Intelligence Core inputs to Emotional/Embodiment parameters.
    Preserves the 'Being' philosophy: Warmth, Dignity, Stability.
    """

    @staticmethod
    def map_voice_profile(input_data: IntelligenceInput) -> VoiceProfile:
        """
        Determines the voice profile based on age, safety, and karma.
        """
        # Safety/Age Gating overrides everything
        if input_data.age_gate_status in ["minor", "unknown"]:
            return VoiceProfile.NEUTRAL_COMPANION

        # Karma/Context logic
        if input_data.karma_hint == "negative":
            # If user is abusive or negative, maintain dignity but distance
            return VoiceProfile.NEUTRAL_COMPANION
        
        if input_data.behavioral_state in ["vulnerable", "sad", "anxious", "frustrated"]:
            # "Warm Soft" here means Kind + Gentle, NOT intimate/seductive.
            # Goal: Grounding presence.
            return VoiceProfile.WARM_SOFT

        # Default state: Calm, grounded, friendly but not overly familiar.
        return VoiceProfile.NATURAL_FRIEND

    @staticmethod
    def map_expression_level(input_data: IntelligenceInput) -> ExpressionLevel:
        """
        Determines how expressive the Being should be.
        Strictly respects upstream expression limits.
        """
        # 1. Respect Upstream Contract (Ceiling Enforcement)
        # If upstream says LOW, we must be LOW.
        if input_data.upstream_expression_profile == "low":
            return ExpressionLevel.LOW
            
        # If upstream says MEDIUM, we cannot be HIGH.
        limit_to_medium = (input_data.upstream_expression_profile == "medium")

        # 2. Local Context Logic
        level = ExpressionLevel.MEDIUM

        if input_data.confidence < 0.5:
            level = ExpressionLevel.LOW
        elif input_data.age_gate_status == "minor":
            level = ExpressionLevel.LOW
        elif input_data.behavioral_state in ["excited", "happy"]:
            level = ExpressionLevel.HIGH
        elif input_data.behavioral_state in ["sad", "anxious"]:
            level = ExpressionLevel.MEDIUM
        
        # 3. Apply Ceiling
        if limit_to_medium and level == ExpressionLevel.HIGH:
            return ExpressionLevel.MEDIUM
            
        return level

    @staticmethod
    def map_delivery_style(input_data: IntelligenceInput) -> DeliveryStyle:
        """
        Determines the pacing and style of delivery.
        """
        if input_data.speech_mode == "monologue":
            return DeliveryStyle.CONVERSATIONAL

        if input_data.behavioral_state in ["anxious", "confused", "vulnerable", "sad", "frustrated"]:
            return DeliveryStyle.SUPPORTIVE

        if input_data.constraints and len(input_data.constraints) > 0:
            # If there are constraints/safety blocks, be concise
            return DeliveryStyle.CONCISE

        return DeliveryStyle.CONVERSATIONAL

    @staticmethod
    def map_tone_band(input_data: IntelligenceInput) -> ToneBand:
        """
        Determines the overall tone band.
        """
        # 0. Strict Safety Override
        if input_data.upstream_safe_mode == "on":
            return ToneBand.PROTECTIVE

        if input_data.age_gate_status == "minor":
            return ToneBand.PROTECTIVE

        if input_data.karma_hint == "negative":
            return ToneBand.PROFESSIONAL

        if input_data.behavioral_state in ["vulnerable", "sad", "anxious", "frustrated"]:
            return ToneBand.EMPATHETIC

        return ToneBand.CASUAL
