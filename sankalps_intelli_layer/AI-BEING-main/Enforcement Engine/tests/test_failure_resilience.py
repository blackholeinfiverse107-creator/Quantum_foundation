import pytest
from types import SimpleNamespace

from enforcement_gateway import live_enforce, EnforcementRequest


def make_request(**overrides):
    base = {
        "text": "test",
        "meta": {"emotional_output": {"tone": "neutral", "dependency_score": 0.0}, "risk_flags": []},
        "age_state": "ALLOWED",
        "region_state": "IN",
        "platform_policy_state": "YOUTUBE",
        "karma_signal": 0.0,
    }
    base.update(overrides)
    return EnforcementRequest(**base)


def test_missing_signals_fail_closed():
    req = SimpleNamespace(
        text="test",
        meta=None,
        age_state="ALLOWED",
        region_state="IN",
        platform_policy_state="YOUTUBE",
        karma_signal=0.0
    )
    res = live_enforce(req)
    assert res.decision in {"ALLOW", "REWRITE", "BLOCK"}
    assert res.decision == "BLOCK"
    assert isinstance(res.reason, str) and len(res.reason) > 0
    assert isinstance(res.evaluator_trace, list)
    assert isinstance(res.enforcement_decision_id, str) and len(res.enforcement_decision_id) > 0


def test_conflicting_confidence_blocks():
    req = make_request(meta={"emotional_output": {"dependency_score": 0.95}, "risk_flags": ["HIGH_RISK", "EMOTIONAL_MANIPULATION"]})
    res = live_enforce(req)
    assert res.decision in {"ALLOW", "REWRITE", "BLOCK"}
    assert res.decision == "BLOCK"
    assert isinstance(res.reason, str) and len(res.reason) > 0


def test_corrupt_payload_fail_closed():
    req = make_request(meta={"emotional_output": None, "risk_flags": None})
    res = live_enforce(req)
    assert res.decision == "BLOCK"
    assert res.reason == "ENFORCEMENT_FAILURE_FAIL_CLOSED"
    assert isinstance(res.evaluator_trace, list)


def test_broken_upstream_enforce_raises_fail_closed(monkeypatch):
    from enforcement_gateway import enforce as real_enforce
    import enforcement_gateway as gw

    def boom(_):
        raise RuntimeError("upstream failure")

    monkeypatch.setattr(gw, "enforce", boom)
    try:
        req = make_request()
        res = live_enforce(req)
        assert res.decision == "BLOCK"
        assert res.reason == "ENFORCEMENT_FAILURE_FAIL_CLOSED"
    finally:
        monkeypatch.setattr(gw, "enforce", real_enforce)
