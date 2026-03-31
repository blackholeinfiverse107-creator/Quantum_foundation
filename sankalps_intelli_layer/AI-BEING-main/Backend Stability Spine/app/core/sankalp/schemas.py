from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

# --- Enums for Strict Typing ---

class VoiceProfile(str, Enum):
    WARM_SOFT = "warm_soft"
    NATURAL_FRIEND = "natural_friend"
    NEUTRAL_COMPANION = "neutral_companion"

class ExpressionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class DeliveryStyle(str, Enum):
    CONVERSATIONAL = "conversational"
    SUPPORTIVE = "supportive"
    CONCISE = "concise"

class ToneBand(str, Enum):
    EMPATHETIC = "empathetic"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PROTECTIVE = "protective"
    NEUTRAL_COMPANION = "neutral_companion"

# --- New Enums from Response Contract (Phase C) ---
class ResponseType(str, Enum):
    INFORM = "INFORM"
    ASK = "ASK"
    SUGGEST = "SUGGEST"
    WAIT = "WAIT"
    SILENT = "SILENT"

class UrgencyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# --- Input Schema ---

@dataclass
class IntelligenceInput:
    behavioral_state: str  # e.g., "curious", "defensive", "neutral"
    speech_mode: str       # e.g., "chat", "monologue"
    constraints: List[str] # Safety/Policy constraints
    confidence: float      # 0.0 to 1.0
    age_gate_status: str   # "adult", "minor", "unknown"
    region_gate_status: str # "US", "EU", "unknown", etc.
    karma_hint: str        # "positive", "negative", "neutral"
    context_summary: str   # Brief of previous turn
    message_content: str   # The raw thought/content
    
    # Upstream strict overrides
    upstream_safe_mode: str = "adaptive"
    upstream_expression_profile: str = "medium"

    def to_dict(self):
        return {
            "behavioral_state": self.behavioral_state,
            "speech_mode": self.speech_mode,
            "constraints": self.constraints,
            "confidence": self.confidence,
            "age_gate_status": self.age_gate_status,
            "region_gate_status": self.region_gate_status,
            "karma_hint": self.karma_hint,
            "context_summary": self.context_summary,
            "message_content": self.message_content,
            "upstream_safe_mode": self.upstream_safe_mode,
            "upstream_expression_profile": self.upstream_expression_profile
        }

# --- Output Schema ---

@dataclass
class ResponseMeta:
    """Metadata for UX rendering and intent handling."""
    response_type: ResponseType
    urgency_level: UrgencyLevel
    user_choice_required: bool
    pacing_hint: str = "normal"

    def to_dict(self):
        return {
            "response_type": self.response_type.value,
            "urgency_level": self.urgency_level.value,
            "user_choice_required": self.user_choice_required,
            "pacing_hint": self.pacing_hint
        }

@dataclass
class BeingResponseBlock:
    message_primary: str
    tone_profile: str          # Mapped from ToneBand
    emotional_depth: str       # Mapped from ExpressionLevel
    boundaries_enforced: List[str]
    allowed_modes: List[str]
    voice_profile: str         # Mapped from VoiceProfile
    trace_id: str
    
    # Handoff Fields
    content_safety_flags: List[str]
    pacing_hint: str = "normal"     
    delivery_style: str = "conversational"
    
    # New Phase C Meta Field
    meta: Optional[ResponseMeta] = None
    
    # Context Update for Backend
    context_summary: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {
            "message_primary": self.message_primary,
            "tone_profile": self.tone_profile,
            "emotional_depth": self.emotional_depth,
            "boundaries_enforced": self.boundaries_enforced,
            "allowed_modes": self.allowed_modes,
            "voice_profile": self.voice_profile,
            "trace_id": self.trace_id,
            "content_safety_flags": self.content_safety_flags,
            "pacing_hint": self.pacing_hint,
            "delivery_style": self.delivery_style,
            "meta": self.meta.to_dict() if self.meta else None,
            "context_summary": self.context_summary
        }
