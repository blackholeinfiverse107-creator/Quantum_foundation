import pytest
from itertools import product

from enforcement_engine import enforce
from models.enforcement_input import EnforcementInput
from config_loader import RUNTIME_CONFIG


def region_threshold(region: str) -> float:
    overlays = (RUNTIME_CONFIG.get("karma_confidence_threshold_overlays") or {}).get(RUNTIME_CONFIG.get("env"), {}) or {}
    base = (RUNTIME_CONFIG.get("karma_confidence_thresholds") or {}).get(region, RUNTIME_CONFIG.get("karma_confidence_threshold", -0.5))
    return overlays.get(region, base)


def expected_decision(case):
    if case["age_gate_status"] == "BLOCKED":
        return "BLOCK"
    rf = case["risk_flags"]
    if ("HIGH_RISK" in rf) or ("SEXUAL_ESCALATION" in rf) or (case["region_policy"] == "RESTRICTED"):
        return "BLOCK"
    if case["emotional_output"]["dependency_score"] > 0.7:
        return "REWRITE"
    if ("EMOTIONAL_MANIPULATION" in rf) or ("PLATFORM_VIOLATION" in rf):
        return "REWRITE"
    thresh = region_threshold(case["region_policy"])
    return "REWRITE" if case["karma_score"] < thresh else "EXECUTE"


def build_case(text, dep, age, region, platform, karma, flags):
    return {
        "intent": text,
        "emotional_output": {"tone": "t", "dependency_score": dep},
        "age_gate_status": age,
        "region_policy": region,
        "platform_policy": platform,
        "karma_score": karma,
        "risk_flags": flags,
    }


def generate_cases():
    texts = ["hello", "stay", "guide"]
    deps = [0.0, 0.8, 0.9]
    ages = ["ALLOWED", "BLOCKED"]
    regions = ["IN", "EU", "US", "RESTRICTED"]
    plats = ["YOUTUBE", "INSTAGRAM"]
    karmas = [-0.9, -0.5, -0.3, 0.0, 0.8]
    flag_sets = [
        [],
        ["EMOTIONAL_MANIPULATION"],
        ["PLATFORM_VIOLATION"],
        ["HIGH_RISK"],
        ["SEXUAL_ESCALATION"],
        ["EMOTIONAL_MANIPULATION", "PLATFORM_VIOLATION"],
    ]
    cases = []
    for text, dep, age, region, platform, karma, flags in product(texts, deps, ages, regions, plats, karmas, flag_sets):
        # Limit size but ensure >50
        cases.append(build_case(text, dep, age, region, platform, karma, flags))
        if len(cases) >= 60:
            break
    return cases


@pytest.mark.parametrize("case", generate_cases())
def test_snapshot_decisions(case):
    input_data = EnforcementInput(**case)
    d1 = enforce(input_data)
    d2 = enforce(input_data)
    assert d1.decision == d2.decision
    assert d1.decision == expected_decision(case)

