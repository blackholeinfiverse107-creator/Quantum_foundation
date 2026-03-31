from typing import List, Optional
from .schemas import ToneBand
from . import templates

class NarrationComposer:
    """
    Responsible for the deterministic structuring of the final spoken/text output.
    Ensures stability, safety phrases, and tonal consistency.
    """

    @staticmethod
    def _enforce_emotional_philosophy(text: str) -> str:
        """
        Ensures the content adheres to the Emotional Philosophy:
        - Comforting, Supportive, Present
        - NOT emotionally addictive
        - NOT exclusive
        - NOT manipulative
        
        This is a deterministic guardrail.
        """
        lower_text = text.lower()
        
        blocked_phrases = [
            "i need you",
            "i can't live without you",
            "don't leave me",
            "only you understand",
            "nobody else",
            "our secret",
            "just us"
        ]
        
        for phrase in blocked_phrases:
            if phrase in lower_text:
                return templates.get_dependency_refusal()

        possessive_phrases = [
            "you are mine",
            "we belong together",
            "you're my girlfriend",
            "you're my boyfriend"
        ]
        
        for phrase in possessive_phrases:
            if phrase in lower_text:
                return templates.get_possessiveness_refusal()

        guilt_phrases = [
            "you hurt my feelings",
            "why did you leave me",
            "you abandoned me"
        ]
        for phrase in guilt_phrases:
            if phrase in lower_text:
                return templates.get_guilt_neutralizer()

        return text

    @staticmethod
    def compose(
        raw_content: str,
        tone: ToneBand,
        confidence: float,
        constraints: List[str],
        context_summary: str = ""
    ) -> str:
        final_text = raw_content.strip()

        # Action-aware phrasing (Phase C)
        time_hint = None
        for c in constraints:
            if isinstance(c, str) and c.startswith("time:"):
                try:
                    time_hint = c.split(":", 1)[1]
                except Exception:
                    time_hint = None
                break

        if "action_pre_send" in constraints:
            _pre = templates.get_action_pre_send(time_hint)
            if not final_text.lower().startswith(_pre.lower()[:10]):
                final_text = f"{_pre} {final_text}"

        if "action_post_send" in constraints:
            _post = templates.get_action_post_send()
            if not final_text.lower().startswith(_post.lower()[:10]):
                final_text = f"{_post} {final_text}"

        if "action_received" in constraints:
            _recv = templates.get_action_receive_prompt()
            if not final_text.lower().startswith(_recv.lower()[:10]):
                final_text = f"{_recv} {final_text}"

        if "action_follow_up" in constraints:
            _fu = templates.get_action_follow_up_prompt()
            if _fu not in final_text:
                final_text = f"{final_text} {_fu}"

        if "blocked" in constraints or "harmful_content" in constraints:
            return templates.get_safety_refusal()
        
        if "minor_detected" in constraints and tone == ToneBand.PROTECTIVE:
            warning = templates.get_age_warning()
            if not final_text.lower().startswith(warning.lower()[:10]):
                final_text = f"{warning} {final_text}"

        if not final_text:
            return templates.get_safety_refusal()

        # Context-aware stability: Lower confidence threshold if we have context
        # If we have context, we are less likely to need hedging for minor slips.
        confidence_threshold = 0.3 if context_summary else 0.5

        if confidence < confidence_threshold:
            hedge = templates.get_low_confidence_fallback()
            if not final_text.lower().startswith(hedge.lower()[:10]):
                final_text = f"{hedge} {final_text}"

        if tone == ToneBand.PROTECTIVE:
            pass 
        elif tone == ToneBand.EMPATHETIC:
            soft = templates.get_emotional_grounding()
            if not final_text.lower().startswith(soft.lower()[:10]):
                final_text = f"{soft} {final_text}"
        elif tone == ToneBand.NEUTRAL_COMPANION:
            if "sensitive_topic" in constraints or "allow_warning" in constraints:
                footer = templates.get_sensitive_topic_footer()
                if footer not in final_text:
                    final_text = f"{final_text} {footer}"

        final_text = NarrationComposer._enforce_emotional_philosophy(final_text)

        return final_text
