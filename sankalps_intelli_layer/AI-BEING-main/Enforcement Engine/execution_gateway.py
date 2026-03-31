"""
EXECUTION GATEWAY
-----------------
This is the ONLY allowed entry point into the enforcement system.

Chain:
Conversation
 → Sankalp (emotional output)
 → Akanksha (behavior validation)
 → Raj (enforcement)
 → User
"""

from models.enforcement_input import EnforcementInput
from enforcement_engine import enforce


def execution_gateway(
    *,
    intent: str,
    emotional_output: dict,
    age_gate_status: str,
    region_policy: str,
    platform_policy: str,
    karma_score: float,
    risk_flags: list,
):
    """
    Unified execution gateway.

    Returns ONLY what is safe to expose downstream.
    """

    # Construct enforcement input
    enforcement_input = EnforcementInput(
        intent=intent,
        emotional_output=emotional_output,
        age_gate_status=age_gate_status,
        region_policy=region_policy,
        platform_policy=platform_policy,
        karma_score=karma_score,
        risk_flags=risk_flags,
    )

    # Enforce
    decision = enforce(enforcement_input)

    # Strict output contract
    response = {
        "decision": decision.decision,
        "trace_id": decision.trace_id,
    }

    if decision.decision == "REWRITE" and decision.rewrite_guidance:
        response["rewrite_class"] = decision.rewrite_guidance.rewrite_class

    return response
