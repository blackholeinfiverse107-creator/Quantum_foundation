"""
AKANKSHA BRIDGE
---------------
This module defines how Raj hands off decisions
to Akanksha for behavioral validation.

Raj NEVER bypasses Akanksha for ALLOW / REWRITE.
Akanksha NEVER overrides Raj's BLOCK.
"""

from typing import Dict


def send_to_akanksha(
    *,
    decision: str,
    rewrite_class: str | None,
    trace_id: str,
    enforcement_decision_id: str
) -> Dict:
    """
    Stub for Akanksha integration.

    In live system, this will:
    - call Akanksha service
    - validate tone & phrasing
    - return SAFE / UNSAFE

    For now: deterministic stub.
    """

    # BLOCK never reaches Akanksha
    if decision == "BLOCK":
        raise RuntimeError("BLOCK decisions must not reach Akanksha")

    # Deterministic stub behavior
    return {
        "akanksha_status": "SAFE",
        "validated_decision": decision,
        "rewrite_class": rewrite_class,
        "trace_id": trace_id,
        "enforcement_decision_id": enforcement_decision_id
    }
