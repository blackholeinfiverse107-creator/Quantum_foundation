from typing import Dict, Any

class NarrationEngine:
    PERSONA = "Warm but Dignified"

    # Rule-based polish map to ensure no system language leaks
    # In production, this would be an LLM-based rewriter
    POLISH_PATTERNS = {
        "Error: Command": "I'm not sure how to do that yet. Is there something else I can help with?",
        "BLOCK: HARMFUL": "I can't engage with that topic. Let's talk about something else.",
        "Ambiguous input": "Could you clarify what you mean?",
        "Processing...": "I'm looking into that for you, just a moment.",
        "Null result": "I couldn't find any information on that.",
        "System Online": "Hello. It's good to see you.",
        "Alert: Task": "Just a reminder: it's time for",
        "Initiating sequence": "I can help with that. First, let's start with",
        "Listening active": "" # Silence
    }

    def compose_response(self, content: str, emotional_output: Dict[str, Any]) -> str:
        """
        Composes the final response based on content and emotional state.
        Enforces the 'Warm but Dignified' persona.
        """
        tone = emotional_output.get("tone", "neutral")
        
        # 1. Apply Text Polish (Remove system language)
        polished_content = self._polish_text(content)
        
        # 2. Enforce 'Warm but Dignified' persona through tone markers
        prefix = ""
        if tone == "calm_supportive":
            prefix = "[Warm/Calm] "
        elif tone == "steady_supportive":
            prefix = "[Dignified/Steady] "
        elif tone == "positive":
            prefix = "[Warm] "
        elif tone == "negative":
            prefix = "[Dignified] "
            
        return f"{prefix}{polished_content}"

    def _polish_text(self, text: str) -> str:
        """
        Replaces raw system outputs with persona-aligned text.
        """
        for pattern, replacement in self.POLISH_PATTERNS.items():
            if pattern in text:
                # specific handling for partial matches if needed
                if pattern == "Alert: Task":
                    return text.replace("Alert: Task", "Just a reminder: it's time for").replace("due now", "")
                return replacement
        return text
