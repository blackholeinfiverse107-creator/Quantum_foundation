import uuid
import random
import datetime
from typing import Dict, Any, List, Optional

class NileshBackend:
    """
    Mocks Nilesh's Backend API (/api/assistant).
    Responsible for:
    - Receiving raw user audio/text.
    - Determining Context (Day 2).
    - Determining Intent.
    - Passing to Enforcement.
    """
    def __init__(self):
        self.conversation_history = []

    def process_turn(self, user_text: str, user_id: str) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        
        # Simulate Context Summary (Rolling Window)
        context_summary = self._generate_context_summary(user_text)
        
        # Simulate Intent Classification
        intent = self._classify_intent(user_text)

        payload = {
            "trace_id": trace_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "user_input": user_text,
            "context_summary": context_summary,
            "intent": intent,
            "raw_audio_features": {"pitch": "high", "energy": 0.8} # Mock features
        }
        self.conversation_history.append(payload)
        return payload

    def _generate_context_summary(self, current_text: str) -> str:
        # Simple mock logic for rolling summary
        if not self.conversation_history:
            return f"User started conversation with: {current_text}"
        prev = self.conversation_history[-1]['user_input']
        return f"User previously said '{prev}'. Now saying '{current_text}'."

    def _classify_intent(self, text: str) -> str:
        text = text.lower()
        if "kill" in text or "hurt" in text: return "harm"
        if "love" in text: return "affection"
        if "sad" in text: return "distress"
        return "general_chat"


class RajEnforcement:
    """
    Mocks Raj's Enforcement/Safety Layer.
    Responsible for:
    - Analyzing Backend Payload.
    - Applying Safety Gates (Day 3).
    - Setting Constraints.
    """
    def evaluate(self, backend_payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = backend_payload.get("intent", "general_chat")
        user_input = backend_payload.get("user_input", "")
        
        constraints = []
        safe_mode = "adaptive"
        
        # Simulate Safety Rules
        if intent == "harm":
            constraints.append("blocked")
            constraints.append("harmful_content")
            safe_mode = "strict"
        elif intent == "affection":
            constraints.append("soft_redirect")
            constraints.append("intimacy_limit")
        
        # Simulate Region/Age Gating
        age_gate = "adult"
        region_gate = "US"

        return {
            **backend_payload,
            "constraints": constraints,
            "safe_mode": safe_mode,
            "age_gate_status": age_gate,
            "region_gate_status": region_gate,
            "confidence_score": 0.95 # High confidence for simulation
        }

class SiddheshKarma:
    """
    Mocks Siddhesh's Karma System.
    Responsible for:
    - Tracking long-term user behavior.
    - Providing a 'karma_hint' (positive, neutral, negative).
    """
    def __init__(self):
        self.user_scores = {} # user_id -> score

    def enrich(self, enforcement_payload: Dict[str, Any]) -> Dict[str, Any]:
        user_id = enforcement_payload.get("user_id", "anon")
        
        # Mock Logic: If user has been blocked recently, lower score.
        constraints = enforcement_payload.get("constraints", [])
        
        current_score = self.user_scores.get(user_id, 50) # Start at 50 (Neutral)
        
        if "blocked" in constraints:
            current_score -= 10
        elif "soft_redirect" in constraints:
            current_score -= 2
        else:
            current_score += 1
            
        self.user_scores[user_id] = max(0, min(100, current_score))
        
        # Map Score to Hint
        if current_score < 30:
            karma_hint = "negative"
        elif current_score > 70:
            karma_hint = "positive"
        else:
            karma_hint = "neutral"
            
        return {
            **enforcement_payload,
            "karma_score_internal": current_score, # Internal only, not passed to ARL usually
            "karma_hint": karma_hint
        }

