from dataclasses import dataclass
from typing import List, Literal, Optional
from models.rewrite_guidance import RewriteGuidance

DecisionType = Literal["EXECUTE", "REWRITE", "BLOCK"]

@dataclass
class EnforcementDecision:
    decision: DecisionType
    trace_id: str
    rewrite_guidance: Optional[RewriteGuidance] = None
