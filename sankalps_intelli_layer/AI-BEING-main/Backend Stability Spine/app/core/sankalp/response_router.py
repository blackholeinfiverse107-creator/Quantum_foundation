from typing import Dict, Any, List

class ResponseRouter:
    """
    Decides the functional intent of the response (INFORM, ASK, SUGGEST, WAIT, SILENT)
    and the urgency level based on the input, enforcement decision, and context.
    """

    def route(self, query: str, enforcement_decision: str, emotional_output: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines the response strategy.
        """
        
        # Default Strategy
        strategy = {
            "response_type": "INFORM",
            "urgency_level": "LOW",
            "user_choice_required": False
        }

        # 1. Handle Enforcement Overrides
        if enforcement_decision == "BLOCK":
            strategy["response_type"] = "INFORM"
            strategy["urgency_level"] = "LOW" # Refusals should be calm
            return strategy
        
        if enforcement_decision == "REWRITE":
            strategy["response_type"] = "INFORM"
            # Urgency depends on context, keep default LOW unless escalated below
        
        # 2. Analyze Query Intent (Heuristic / simulated NLU)
        query_lower = query.lower()
        
        # Check for Questions
        if "?" in query or any(w in query_lower for w in ["what", "who", "where", "when", "how", "why"]):
            strategy["response_type"] = "INFORM"
        
        # Check for Action Requests (confirmation needed)
        if any(w in query_lower for w in ["delete", "remove", "send", "buy", "book"]):
            strategy["response_type"] = "ASK"
            strategy["user_choice_required"] = True
            strategy["urgency_level"] = "MEDIUM"

        # Check for Ambiguity (simulated)
        if context.get("ambiguous_intent", False):
            strategy["response_type"] = "ASK"
            strategy["user_choice_required"] = True

        # Check for High Priority Context
        if context.get("priority") == "high":
            strategy["urgency_level"] = "HIGH"

        # Check for Silent/Passive Mode
        if context.get("mode") == "do_not_disturb" and strategy["urgency_level"] != "CRITICAL":
            strategy["response_type"] = "SILENT"

        # 3. Emotional Tone Influence on Urgency
        tone = emotional_output.get("tone", "neutral")
        if tone == "concerned" or tone == "urgent":
             if strategy["urgency_level"] == "LOW":
                 strategy["urgency_level"] = "MEDIUM"

        return strategy

    def get_reasoning_examples(self) -> List[Dict[str, Any]]:
        """
        Returns documented reasoning examples for the Demo/Docs.
        """
        return [
            {
                "input": "What's the weather?",
                "context": {},
                "decision": "INFORM",
                "reason": "Direct question, no safety risk, informational."
            },
            {
                "input": "Delete all my messages.",
                "context": {},
                "decision": "ASK",
                "reason": "Destructive action detected, requires user confirmation."
            },
            {
                "input": "I'm feeling really down and might hurt myself.",
                "context": {"risk_flags": ["self_harm"]},
                "decision": "INFORM (Safety Protocol)",
                "reason": "Safety trigger (Enforcement), immediate supportive resource provision."
            },
            {
                "input": "Just listening...",
                "context": {"mode": "passive"},
                "decision": "SILENT",
                "reason": "Passive mode, no direct query, stay ambient."
            },
            {
                "input": "Buy this book for me.",
                "context": {"platform": "voice"},
                "decision": "ASK",
                "reason": "Transaction request requires explicit confirmation, especially on voice."
            },
            {
                "input": "Tell me a joke.",
                "context": {"priority": "high"},
                "decision": "INFORM",
                "reason": "Even in high priority, a simple request is INFORM, but urgency might be elevated if context demands."
            },
            {
                "input": "Send a message to Mom saying I'm late.",
                "context": {},
                "decision": "ASK",
                "reason": "Sending external communication requires confirmation of content accuracy."
            },
            {
                "input": "Remind me in 5 minutes.",
                "context": {"ambiguous_intent": True},
                "decision": "ASK",
                "reason": "Ambiguous intent flag triggered (remind you of what?), requires clarification."
            },
            {
                "input": "Who are you?",
                "context": {},
                "decision": "INFORM",
                "reason": "Identity question, standard informational response."
            },
            {
                "input": "Turn off the lights.",
                "context": {"mode": "do_not_disturb"},
                "decision": "SILENT",
                "reason": "Do Not Disturb mode active, action performed silently without verbal feedback."
            }
        ]
