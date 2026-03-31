from collections import deque
from typing import Deque, Dict, Any

class ContextContinuity:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.sessions: Dict[str, Deque[Dict[str, Any]]] = {}

    def _get_window(self, session_id: str) -> Deque[Dict[str, Any]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.window_size)
        return self.sessions[session_id]

    def ingest(self, session_id: str, summary: str, sentiment: str, decision: str, rewrite_class: str | None) -> None:
        window = self._get_window(session_id)
        window.append({
            "summary": summary or "",
            "sentiment": (sentiment or "neutral"),
            "decision": decision,
            "rewrite_class": rewrite_class
        })

    def tone_band(self, session_id: str) -> str:
        window = self._get_window(session_id)
        counts = {"positive": 0, "neutral": 0, "negative": 0}
        for item in window:
            s = str(item.get("sentiment", "neutral")).lower()
            if s in counts:
                counts[s] += 1
        if counts["negative"] >= max(counts.values()):
            return "calm_supportive"
        if counts["positive"] >= max(counts.values()):
            return "steady_supportive"
        return "neutral"

    def apply_continuity(self, text: str, band: str) -> str:
        t = text or ""
        if band in ("calm_supportive", "steady_supportive"):
            t = t.replace("!", ".")
            t = t.replace(" must ", " can ")
            t = t.replace(" should ", " may ")
        return t

continuity = ContextContinuity()
