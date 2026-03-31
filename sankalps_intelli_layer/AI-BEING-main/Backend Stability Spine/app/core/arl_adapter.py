from typing import Any, Dict, List, Optional

def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v

def build_enforcement_payload(
    *,
    text: str,
    platform: str,
    intent: Optional[Dict[str, Any]] = None,
    confidence: Optional[float] = None,
    constraints: Optional[Dict[str, Any]] = None,
    karma_hint: Optional[float] = None
) -> Dict[str, Any]:
    safe_text = text if isinstance(text, str) and text.strip() else ""
    platform_policy = (platform or "web").upper() if isinstance(platform, str) else "WEB"
    age_gate_status = "ALLOWED"
    region_policy = "IN"
    risk_flags: List[str] = []
    if isinstance(constraints, dict):
        age_gate_status = str(constraints.get("age_gate_status", age_gate_status)).upper()
        region_policy = str(constraints.get("region_policy", region_policy)).upper()
        rf = constraints.get("risk_flags", [])
        if isinstance(rf, list):
            risk_flags = [str(x) for x in rf]
    dep_score = 0.0
    if confidence is not None:
        try:
            dep_score = 1.0 - clamp(float(confidence), 0.0, 1.0)
        except Exception:
            dep_score = 0.0
    tone = "neutral"
    if isinstance(intent, dict):
        t = intent.get("tone")
        if isinstance(t, str) and t:
            tone = t.lower()
    emotional_output = {"tone": tone, "dependency_score": dep_score}
    karma_score = 0.0 if karma_hint is None else float(karma_hint)
    return {
        "intent": safe_text,
        "emotional_output": emotional_output,
        "age_gate_status": age_gate_status,
        "region_policy": region_policy,
        "platform_policy": platform_policy,
        "karma_score": karma_score,
        "risk_flags": risk_flags,
    }
