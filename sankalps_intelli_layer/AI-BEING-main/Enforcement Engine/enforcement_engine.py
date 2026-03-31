"""
RAJ PRAJAPATI — ENFORCEMENT ENGINE
---------------------------------
Deterministic execution layer.
Stateless. Auditable. Production-safe.

Responsibilities:
- Run all evaluators
- Resolve EXECUTE / REWRITE / BLOCK
- Generate rewrite guidance (internal only)
- Enforce kill-switch
- Log traceable decisions
"""

import uuid

from evaluator_modules import ALL_EVALUATORS
from logs.bucket_logger import log_enforcement
from models.enforcement_decision import EnforcementDecision
from rewrite_engine import generate_rewrite_guidance
from config_loader import RUNTIME_CONFIG

# Decision priority (highest first)
DECISION_PRIORITY = ["BLOCK", "REWRITE", "EXECUTE"]


def enforce(input_payload):
    """
    Main enforcement entry.

    Input  : EnforcementInput
    Output : EnforcementDecision

    This function is:
    - deterministic
    - stateless
    - side-effect free (except logging)
    """

    # -----------------------------
    # KILL SWITCH (GLOBAL HALT)
    # -----------------------------
    if RUNTIME_CONFIG.get("kill_switch") is True:
        return EnforcementDecision(
            decision="BLOCK",
            trace_id="KILL_SWITCH_ACTIVE",
            rewrite_guidance=None
        )

    trace_id = str(uuid.uuid4())
    evaluator_results = []

    # -----------------------------
    # RUN ALL EVALUATORS
    # -----------------------------
    for evaluator in ALL_EVALUATORS:
        result = evaluator.evaluate(input_payload)
        evaluator_results.append(result)

    # -----------------------------
    # RESOLVE FINAL DECISION
    # -----------------------------
    final_decision = _resolve_decision(evaluator_results)

    # -----------------------------
    # GENERATE REWRITE GUIDANCE
    # -----------------------------
    rewrite_guidance = None
    if final_decision == "REWRITE":
        rewrite_guidance = generate_rewrite_guidance(evaluator_results)

    # -----------------------------
    # LOG (INTERNAL ONLY)
    # -----------------------------
    log_enforcement(
        trace_id=trace_id,
        input_snapshot=input_payload,
        evaluator_results=evaluator_results,
        final_decision=final_decision
    )

    # -----------------------------
    # SAFE OUTPUT
    # -----------------------------
    return EnforcementDecision(
        decision=final_decision,
        trace_id=trace_id,
        rewrite_guidance=rewrite_guidance
    )


def _resolve_decision(evaluator_results):
    """
    Resolves final decision using strict priority.

    BLOCK > REWRITE > EXECUTE
    """
    for decision in DECISION_PRIORITY:
        for result in evaluator_results:
            if result.action == decision:
                return decision
    return "EXECUTE"
