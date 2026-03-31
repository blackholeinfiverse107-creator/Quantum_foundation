from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class EnforcementInput:
    intent: str
    emotional_output: Dict
    age_gate_status: str          # ALLOWED | BLOCKED
    region_policy: str            # IN | EU | US | etc
    platform_policy: str          # YOUTUBE | INSTAGRAM | etc
    karma_score: float            # -1.0 to +1.0
    risk_flags: List[str]
