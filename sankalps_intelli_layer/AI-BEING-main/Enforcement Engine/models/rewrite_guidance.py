from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RewriteGuidance:
    rewrite_class: str
    rewrite_hints: Optional[List[str]] = None
