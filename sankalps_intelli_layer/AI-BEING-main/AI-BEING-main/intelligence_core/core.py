from typing import Dict, Tuple, Any

class IntelligenceCore:
    def __init__(self):
        pass

    def process_interaction(
        self,
        context: Dict[str, Any],
        karma_data: Dict[str, Any],
        bucket_data: Dict[str, Any],
        message_content: str = ""
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        user_age = context.get("user_age", 18)
        region = context.get("region", "unknown")
        risk_signal = karma_data.get("risk_signal", "low")
        karma_score = karma_data.get("karma_score", 50)

        gating_flags = []

        if user_age < 18:
            gating_flags.append("age_gate")
            gating_flags.append("minor_detected")

        if risk_signal == "high" or karma_score < 30:
            gating_flags.append("high_risk")

        # Basic Emotion Detection
        behavioral_state = "neutral"
        if risk_signal == "high":
            behavioral_state = "defensive"
        else:
            behavioral_state = self._detect_emotion(message_content)

        # Determine Expression Profile based on State
        expression_profile = "medium"
        if behavioral_state == "happy":
            expression_profile = "high"

        embodiment_output = {
            "behavioral_state": behavioral_state,
            "speech_mode": "chat",
            "constraints": gating_flags,
            "confidence": "medium",
            "safe_mode": "on" if risk_signal == "high" else "adaptive",
            "expression_profile": expression_profile
        }

        bucket_write = {
            "baseline_emotional_band": bucket_data.get("baseline_emotional_band", "neutral"),
            "previous_state_anchor": bucket_data.get("previous_state_anchor", "neutral"),
            "region": region,
            "updates": {
                "risk_signal": risk_signal,
                "karma_score": karma_score
            }
        }

        return embodiment_output, bucket_write

    def _detect_emotion(self, message: str) -> str:
        msg = message.lower()
        
        # Happy / Excited
        if any(w in msg for w in ["happy", "excited", "great", "awesome", "love", "amazing", "good news", "yay"]):
            return "happy"
            
        # Sad / Vulnerable
        if any(w in msg for w in ["sad", "depressed", "lonely", "hurt", "crying", "grief", "miss"]):
            return "sad"
            
        # Anxious / Fear
        if any(w in msg for w in ["scared", "anxious", "worried", "fear", "nervous", "panic"]):
            return "anxious"
            
        # Frustrated / Upset
        if any(w in msg for w in ["upset", "angry", "frustrated", "annoyed", "mad", "disappointed", "listen to each other"]):
            return "frustrated"
            
        # Confused
        if any(w in msg for w in ["confused", "don't understand", "what?", "huh", "explain"]):
            return "confused"

        # Curious
        if any(w in msg for w in ["why", "how", "what is", "tell me about"]):
            return "curious"

        return "neutral"

