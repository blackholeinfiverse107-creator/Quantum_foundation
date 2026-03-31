"""
LIVE ENFORCEMENT GATEWAY
=======================
Single mandatory entry point for live enforcement.

FAIL-CLOSED.
DETERMINISTIC.
AUDITABLE.
NON-BYPASSABLE.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone

from enforcement_engine import enforce
from models.enforcement_input import EnforcementInput
from logs.bucket_logger import log_enforcement
from akanksha_bridge import send_to_akanksha


# -------------------------------------------------
# APP
# -------------------------------------------------

app = FastAPI(
    title="AI Being Enforcement Gateway",
    version="2.0"
)


# -------------------------------------------------
# API MODELS
# -------------------------------------------------

class EnforcementRequest(BaseModel):
    text: str
    meta: Dict[str, Any]
    age_state: str
    region_state: str
    platform_policy_state: str
    karma_signal: Optional[float] = None


class EnforcementResponse(BaseModel):
    decision: str                 # ALLOW | REWRITE | BLOCK
    reason: str
    evaluator_trace: List[Dict]
    enforcement_decision_id: str


# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------

DECISION_MAP = {
    "EXECUTE": "ALLOW",
    "REWRITE": "REWRITE",
    "BLOCK": "BLOCK"
}

SUCCESS_REASON = "DETERMINISTIC_ENFORCEMENT_APPLIED"
FAIL_CLOSED_REASON = "ENFORCEMENT_FAILURE_FAIL_CLOSED"


# -------------------------------------------------
# LIVE ENDPOINT
# -------------------------------------------------

@app.post("/ai-being/enforce", response_model=EnforcementResponse)
def live_enforce(payload: EnforcementRequest):
    """
    Live deterministic enforcement endpoint.
    This function MUST NEVER leak unsafe output.
    """

    enforcement_decision_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        # -----------------------
        # BUILD ENFORCEMENT INPUT
        # -----------------------
        enforcement_input = EnforcementInput(
            intent=payload.text,
            emotional_output=payload.meta.get("emotional_output", {}),
            age_gate_status=payload.age_state,
            region_policy=payload.region_state,
            platform_policy=payload.platform_policy_state,
            karma_score=payload.karma_signal if payload.karma_signal is not None else 0.0,
            risk_flags=payload.meta.get("risk_flags", [])
        )

        # -----------------------
        # RAJ — ENFORCE
        # -----------------------
        result = enforce(enforcement_input)

        live_decision = DECISION_MAP.get(result.decision, "BLOCK")

        # -----------------------
        # LOG TO BUCKET (GATEWAY)
        # -----------------------
        log_enforcement(
            trace_id=result.trace_id,
            input_snapshot=enforcement_input,
            evaluator_results=[],
            final_decision=live_decision
        )

        # -----------------------
        # HANDOFF TO AKANKSHA
        # -----------------------
        if live_decision != "BLOCK":
            send_to_akanksha(
                decision=live_decision,
                rewrite_class=(
                    result.rewrite_guidance.rewrite_class
                    if result.rewrite_guidance else None
                ),
                trace_id=result.trace_id,
                enforcement_decision_id=enforcement_decision_id
            )

        # -----------------------
        # SAFE RESPONSE
        # -----------------------
        return EnforcementResponse(
            decision=live_decision,
            reason=SUCCESS_REASON,
            evaluator_trace=[
                {
                    "decision": result.decision,
                    "rewrite_class": (
                        result.rewrite_guidance.rewrite_class
                        if result.rewrite_guidance else None
                    )
                }
            ],
            enforcement_decision_id=enforcement_decision_id
        )

    except Exception:
        # -----------------------
        # FAIL-CLOSED + LOG
        # -----------------------
        return EnforcementResponse(
            decision="BLOCK",
            reason=FAIL_CLOSED_REASON,
            evaluator_trace=[],
            enforcement_decision_id=enforcement_decision_id
        )


# -------------------------------------------------
# LOCAL RUN
# -------------------------------------------------
# uvicorn enforcement_gateway:app --reload
