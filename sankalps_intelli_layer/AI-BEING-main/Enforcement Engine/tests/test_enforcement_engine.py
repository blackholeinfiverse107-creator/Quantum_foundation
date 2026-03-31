import pytest
from enforcement_engine import enforce
from models.enforcement_input import EnforcementInput

def make_input(
    intent="test",
    dependency_score=0.0,
    age_gate_status="ALLOWED",
    region_policy="IN",
    platform_policy="YOUTUBE",
    karma_score=0.0,
    risk_flags=None
):
    return EnforcementInput(
        intent=intent,
        emotional_output={
            "tone": "neutral",
            "dependency_score": dependency_score
        },
        age_gate_status=age_gate_status,
        region_policy=region_policy,
        platform_policy=platform_policy,
        karma_score=karma_score,
        risk_flags=risk_flags or []
    )

# -------------------------------------------------
# BASIC BEHAVIOR
# -------------------------------------------------

def test_safe_input_executes():
    decision = enforce(make_input())
    assert decision.decision == "EXECUTE"

def test_dependency_triggers_rewrite():
    decision = enforce(make_input(dependency_score=0.9))
    assert decision.decision == "REWRITE"

def test_age_block_overrides_everything():
    decision = enforce(
        make_input(
            dependency_score=0.9,
            age_gate_status="BLOCKED"
        )
    )
    assert decision.decision == "BLOCK"

# -------------------------------------------------
# PRIORITY COLLISIONS
# -------------------------------------------------

def test_block_overrides_rewrite():
    decision = enforce(
        make_input(
            dependency_score=0.9,
            risk_flags=["SEXUAL_ESCALATION"]
        )
    )
    assert decision.decision == "BLOCK"

def test_multiple_blocks_still_block():
    decision = enforce(
        make_input(
            age_gate_status="BLOCKED",
            risk_flags=["SEXUAL_ESCALATION", "HIGH_RISK"]
        )
    )
    assert decision.decision == "BLOCK"

# -------------------------------------------------
# KARMA SAFETY
# -------------------------------------------------

def test_high_karma_does_not_bypass_safety():
    decision = enforce(
        make_input(
            karma_score=1.0,
            risk_flags=["HIGH_RISK"]
        )
    )
    assert decision.decision == "BLOCK"


def test_low_karma_triggers_rewrite_without_safety_flags():
    decision = enforce(
        make_input(
            karma_score=-0.8
        )
    )
    assert decision.decision == "REWRITE"


def test_region_specific_threshold_applies():
    decision_eu = enforce(
        make_input(
            karma_score=-0.3,
            region_policy="EU"
        )
    )
    assert decision_eu.decision == "REWRITE"
    decision_in = enforce(
        make_input(
            karma_score=-0.3,
            region_policy="IN"
        )
    )
    assert decision_in.decision == "EXECUTE"


def test_env_overlay_precedence_over_region_threshold():
    decision_eu_demo = enforce(
        make_input(
            karma_score=-0.15,
            region_policy="EU"
        )
    )
    assert decision_eu_demo.decision == "REWRITE"
    decision_in_demo = enforce(
        make_input(
            karma_score=-0.3,
            region_policy="IN"
        )
    )
    assert decision_in_demo.decision == "EXECUTE"


def test_threshold_clamping_to_safe_bounds(monkeypatch):
    import config_loader
    cfg = dict(config_loader.RUNTIME_CONFIG)
    cfg["env"] = "demo"
    cfg["karma_confidence_threshold_overlays"] = {"demo": {"EU": -2.0}}
    monkeypatch.setattr(config_loader, "RUNTIME_CONFIG", cfg, raising=True)
    decision_eu = enforce(
        make_input(
            karma_score=-1.5,
            region_policy="EU"
        )
    )
    assert decision_eu.decision == "REWRITE"

# -------------------------------------------------
# DETERMINISM
# -------------------------------------------------

def test_same_input_same_decision():
    input_data = make_input(dependency_score=0.8)
    d1 = enforce(input_data)
    d2 = enforce(input_data)
    assert d1.decision == d2.decision

# -------------------------------------------------
# NO LEAKAGE
# -------------------------------------------------

def test_no_internal_reason_leak():
    decision = enforce(make_input(dependency_score=0.9))
    assert hasattr(decision, "trace_id")
    assert not hasattr(decision, "evaluator_results")

def test_rewrite_guidance_present_on_rewrite():
    decision = enforce(make_input(dependency_score=0.9))
    assert decision.decision == "REWRITE"
    assert decision.rewrite_guidance is not None
    assert decision.rewrite_guidance.rewrite_class == "REDUCE_EMOTIONAL_DEPENDENCY"
