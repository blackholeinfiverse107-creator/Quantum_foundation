from typing import Optional


def karma_band(hint: Optional[float]) -> str:
    if hint is None:
        return "neutral"
    try:
        v = float(hint)
    except Exception:
        return "neutral"
    if v >= 0.3:
        return "positive"
    if v <= -0.3:
        return "negative"
    return "neutral"


def apply_karma_to_band(base_band: str, k_band: str) -> str:
    if k_band == "negative":
        return "calm_supportive"
    if k_band == "positive":
        if base_band == "neutral":
            return "steady_supportive"
        return base_band
    return base_band

