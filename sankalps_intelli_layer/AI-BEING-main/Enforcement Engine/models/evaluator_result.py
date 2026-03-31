from dataclasses import dataclass
from typing import Literal

ActionType = Literal["EXECUTE", "REWRITE", "BLOCK"]

@dataclass
class EvaluatorResult:
    name: str
    triggered: bool
    action: ActionType
    code: str
