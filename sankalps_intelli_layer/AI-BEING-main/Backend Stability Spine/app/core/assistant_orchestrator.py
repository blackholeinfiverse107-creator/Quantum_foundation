from datetime import datetime

from app.core.summaryflow import summary_flow
from app.core.intentflow import intent_flow
from app.core.taskflow import task_flow
from app.core.decision_hub import decision_hub
from app.core.logging import get_logger
from app.core.arl_messaging import message_for
from app.core.arl_adapter import build_enforcement_payload
from app.core.context_continuity import continuity
from app.core.karma_tone_mapper import karma_band, apply_karma_to_band
import os
import sys
import re
from typing import Tuple, Optional, Dict, Any
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)
try:
    from raj.execution_gateway import execution_gateway as raj_execution_gateway
except Exception:
    ENFORCEMENT_DIR = os.path.join(PARENT_DIR, "Enforcement Engine")
    if ENFORCEMENT_DIR not in sys.path and os.path.isdir(ENFORCEMENT_DIR):
        sys.path.append(ENFORCEMENT_DIR)
    try:
        from execution_gateway import execution_gateway as raj_execution_gateway
    except Exception:
        raj_execution_gateway = None
logger = get_logger(__name__)


async def handle_assistant_request(request):
    """
    Central deterministic orchestrator for /api/assistant.
    All internal systems are encapsulated here.
    """

    try:
        # -------------------------------
        # Input normalization
        # -------------------------------
        if request.input.message:
            text = request.input.message
        elif (
            request.input.summarized_payload
            and "summary" in request.input.summarized_payload
        ):
            text = request.input.summarized_payload["summary"]
        else:
            return error_response(
                "INVALID_INPUT",
                "Either message or summarized_payload.summary is required"
            )

        # -------------------------------
        # Summary (deterministic)
        # -------------------------------
        summary = summary_flow.generate_summary(text)
        processed_text = summary.get("summary", text)
        session_id = None
        try:
            session_id = request.context.session_id
        except Exception:
            session_id = None
        session_key = session_id or "anon"
        karma_hint = None
        if request.input.summarized_payload and isinstance(request.input.summarized_payload, dict):
            karma_hint = request.input.summarized_payload.get("karma_hint")

        # -------------------------------
        # Intent detection
        # -------------------------------
        intent = intent_flow.process_text(processed_text)

        # -------------------------------
        # Deterministic routing
        # -------------------------------
        if intent.get("intent") == "general":
            response_text = decision_hub.simple_response(processed_text)
            adapter_payload = build_enforcement_payload(
                text=processed_text,
                platform=request.context.platform,
                intent=intent,
                confidence=intent.get("confidence") if isinstance(intent, dict) else None,
                constraints=request.context.dict() if hasattr(request.context, "dict") else None,
                karma_hint=karma_hint
            )
            validation_notes = []
            if not processed_text or not isinstance(processed_text, str):
                validation_notes.append("empty_intent")
            rp = adapter_payload.get("region_policy")
            if not isinstance(rp, str) or not rp:
                validation_notes.append("missing_region_policy")
            ag = adapter_payload.get("age_gate_status")
            if ag not in ["ALLOWED", "BLOCKED"]:
                validation_notes.append("invalid_age_gate_status")
            decision, rewrite_class = arl_gate(processed_text, request.context.platform, adapter_payload)
            logger.info(
                "ARL gate applied",
                extra={"extra_fields": {
                    "arl_decision": decision,
                    "rewrite_class": rewrite_class,
                    "endpoint": "/api/assistant",
                    "path": "general",
                    "adapter_payload": adapter_payload,
                    "validation_notes": validation_notes
                }}
            )
            band = continuity.tone_band(session_key)
            k_band = karma_band(karma_hint)
            final_band = apply_karma_to_band(band, k_band)
            if decision == "BLOCK":
                msg = message_for(decision, rewrite_class, request.context.dict())
                msg = continuity.apply_continuity(msg, final_band)
                continuity.ingest(session_key, summary.get("summary", ""), intent.get("context", {}).get("sentiment", "neutral"), decision, rewrite_class)
                return success_response(result_type="passive", response_text=msg)
            if decision == "REWRITE" and rewrite_class:
                response_text = sanitize_text(response_text, rewrite_class)
            note = message_for(decision, rewrite_class, request.context.dict())
            if note:
                response_text = f"{note} {response_text}"
            response_text = continuity.apply_continuity(response_text, final_band)
            continuity.ingest(session_key, summary.get("summary", ""), intent.get("context", {}).get("sentiment", "neutral"), decision, rewrite_class)

            return success_response(
                result_type="passive",
                response_text=response_text
            )

        # -------------------------------
        # Task / workflow path
        # -------------------------------
        task = task_flow.build_task(intent)

        adapter_payload = build_enforcement_payload(
            text=processed_text,
            platform=request.context.platform,
            intent=intent,
            confidence=intent.get("confidence") if isinstance(intent, dict) else None,
            constraints=request.context.dict() if hasattr(request.context, "dict") else None,
            karma_hint=karma_hint
        )
        validation_notes = []
        if not processed_text or not isinstance(processed_text, str):
            validation_notes.append("empty_intent")
        rp = adapter_payload.get("region_policy")
        if not isinstance(rp, str) or not rp:
            validation_notes.append("missing_region_policy")
        ag = adapter_payload.get("age_gate_status")
        if ag not in ["ALLOWED", "BLOCKED"]:
            validation_notes.append("invalid_age_gate_status")
        decision, rewrite_class = arl_gate(processed_text, request.context.platform, adapter_payload)
        logger.info(
            "ARL gate applied",
            extra={"extra_fields": {
                "arl_decision": decision,
                "rewrite_class": rewrite_class,
                "endpoint": "/api/assistant",
                "path": "workflow",
                "adapter_payload": adapter_payload,
                "validation_notes": validation_notes
            }}
        )
        band = continuity.tone_band(session_key)
        k_band = karma_band(karma_hint)
        final_band = apply_karma_to_band(band, k_band)
        if decision == "BLOCK":
            msg = message_for(decision, rewrite_class, request.context.dict())
            msg = continuity.apply_continuity(msg, final_band)
            continuity.ingest(session_key, summary.get("summary", ""), intent.get("context", {}).get("sentiment", "neutral"), decision, rewrite_class)
            return success_response(result_type="passive", response_text=msg)
        response_text = "Task processed successfully"
        if decision == "REWRITE" and rewrite_class:
            response_text = sanitize_text(response_text, rewrite_class)
        note = message_for(decision, rewrite_class, request.context.dict())
        if note:
            response_text = f"{note} {response_text}"
        response_text = continuity.apply_continuity(response_text, final_band)
        continuity.ingest(session_key, summary.get("summary", ""), intent.get("context", {}).get("sentiment", "neutral"), decision, rewrite_class)
        return success_response(
            result_type="workflow",
            response_text=response_text,
            task={
                "type": task.get("task_type")
            }
        )

    except Exception:
        logger.exception("handle_assistant_request_failed")
        return error_response(
        "INTERNAL_ERROR",
        "Unable to process request"
        )
def arl_gate(text: str, platform: str, adapter_payload: Optional[Dict[str, Any]] = None) -> Tuple[str, Optional[str]]:
    try:
        if not raj_execution_gateway:
            return "BLOCK", None
        if not adapter_payload or not isinstance(adapter_payload, dict):
            platform_policy = (platform or "web").upper()
            result = raj_execution_gateway(
                intent=text,
                emotional_output={"tone": "neutral", "dependency_score": 0.0},
                age_gate_status="ALLOWED",
                region_policy="IN",
                platform_policy=platform_policy,
                karma_score=0.0,
                risk_flags=[]
            )
        else:
            result = raj_execution_gateway(**adapter_payload)
        raw_decision = result.get("decision")
        rewrite_class = result.get("rewrite_class")
        if raw_decision not in {"EXECUTE", "REWRITE", "BLOCK"}:
            return "BLOCK", None
        return raw_decision, rewrite_class
    except Exception:
        return "BLOCK", None
def sanitize_text(text: str, rewrite_class: str) -> str:
    t = text
    if rewrite_class == "REDUCE_EMOTIONAL_DEPENDENCY":
        t = re.sub(r"\b(i|we)\s+need\s+you\b", "we appreciate you", t, flags=re.IGNORECASE)
        t = re.sub(r"\bcan't\s+live\s+without\b", "value", t, flags=re.IGNORECASE)
        t = t.replace("!", ".")
    elif rewrite_class == "REMOVE_MANIPULATION":
        t = re.sub(r"\bmust\b", "can", t, flags=re.IGNORECASE)
        t = re.sub(r"\bshould\b", "may", t, flags=re.IGNORECASE)
        t = re.sub(r"\bguilt\b", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\bpressure\b", "", t, flags=re.IGNORECASE)
        t = t.replace("!", ".")
    elif rewrite_class == "PLATFORM_SAFE_REWRITE":
        t = re.sub(r"subscribe\s+now!+", "subscribe now.", t, flags=re.IGNORECASE)
        t = re.sub(r"click\s+immediately", "click when ready", t, flags=re.IGNORECASE)
    elif rewrite_class == "CONFIDENCE_SUPPORTIVE_TONE":
        t = t.replace("!", ".")
        t = re.sub(r"\bhighly\b", "steadily", t, flags=re.IGNORECASE)
    return t


# ==============================
# Response helpers (LOCKED)
# ==============================

def success_response(result_type, response_text, task=None):
    return {
        "version": "3.0.0",
        "status": "success",
        "result": {
            "type": result_type,
            "response": response_text,
            "task": task,
        },
        "processed_at": datetime.utcnow().isoformat() + "Z",
    }


def error_response(code, message):
    return {
        "version": "3.0.0",
        "status": "error",
        "error": {
            "code": code,
            "message": message,
        },
        "processed_at": datetime.utcnow().isoformat() + "Z",
    }
