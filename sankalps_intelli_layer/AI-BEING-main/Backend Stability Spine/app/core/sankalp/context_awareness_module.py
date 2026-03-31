from typing import Dict, Any, List, Optional
try:
    from ..context_continuity import continuity
except ImportError:
    # Fallback for testing/standalone
    continuity = None

class ContextAwarenessModule:
    """
    Manages multi-turn context to prevent repetition and maintain conversation stability.
    Wraps the core ContextContinuity engine for session persistence.
    """

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        # Local short-term memory for immediate repetition check
        self.local_history = [] 
        # Track deferred items and unresolved context
        self.deferred_intents = []
        self.unresolved_topics = []

    def update_context(self, user_input: str, assistant_response: str, tone: str, deferred_intent: Optional[str] = None):
        """
        Updates the context after a turn.
        """
        # 1. Update Core Continuity Engine
        if continuity:
            continuity.ingest(
                session_id=self.session_id,
                summary=user_input[:50], # approximating summary
                sentiment=tone,
                decision="RESPOND",
                rewrite_class=None
            )

        # 2. Update Local History (FIFO)
        self.local_history.append({
            "user": user_input,
            "assistant": assistant_response,
            "timestamp": "now" # In real system use datetime
        })
        if len(self.local_history) > 5:
            self.local_history.pop(0)

        # 3. Track Deferred Items
        if deferred_intent:
            self.deferred_intents.append(deferred_intent)

    def is_repetitive(self, proposed_response: str) -> bool:
        """
        Checks if the proposed response is too similar to recent responses.
        """
        for turn in self.local_history:
            # Simple string matching for now, could be semantic similarity
            if turn["assistant"] == proposed_response:
                return True
        return False

    def get_stable_tone(self) -> str:
        """
        Returns the stabilized tone from the continuity engine.
        """
        if continuity:
            return continuity.tone_band(self.session_id)
        return "neutral"

    def apply_continuity_polish(self, text: str, tone: str) -> str:
        """
        Applies low-level text continuity rules (e.g. punctuation smoothing).
        """
        if continuity:
            return continuity.apply_continuity(text, tone)
        return text

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Returns a summary of the current context for the Engine.
        """
        return {
            "history_depth": len(self.local_history),
            "stable_tone": self.get_stable_tone(),
            "session_id": self.session_id,
            "deferred_count": len(self.deferred_intents),
            "last_user_input": self.local_history[-1]["user"] if self.local_history else None
        }
