import pytest
from types import SimpleNamespace

from enforcement_gateway import live_enforce, EnforcementRequest
import enforcement_gateway as gw


def make_request(**overrides):
    base = {
        "text": "hello",
        "meta": {"emotional_output": {"tone": "neutral", "dependency_score": 0.0}, "risk_flags": []},
        "age_state": "ALLOWED",
        "region_state": "IN",
        "platform_policy_state": "YOUTUBE",
        "karma_signal": 0.0,
    }
    base.update(overrides)
    return EnforcementRequest(**base)


def test_gateway_minimal_evaluator_trace_on_allow():
    req = make_request()
    res = live_enforce(req)
    assert res.decision in {"ALLOW", "REWRITE", "BLOCK"}
    if res.decision != "BLOCK":
        assert isinstance(res.evaluator_trace, list) and len(res.evaluator_trace) == 1
        entry = res.evaluator_trace[0]
        assert set(entry.keys()) == {"decision", "rewrite_class"}
    else:
        assert res.evaluator_trace == []


def test_enforcement_decision_id_unique_per_call():
    req = make_request()
    r1 = live_enforce(req)
    r2 = live_enforce(req)
    assert r1.enforcement_decision_id != r2.enforcement_decision_id


def test_decision_mapping_applied_execute_to_allow():
    req = make_request(meta={"emotional_output": {"tone": "neutral", "dependency_score": 0.0}, "risk_flags": []})
    res = live_enforce(req)
    assert res.decision == "ALLOW"


def test_decision_mapping_applied_rewrite():
    req = make_request(meta={"emotional_output": {"tone": "attached", "dependency_score": 0.9}, "risk_flags": []})
    res = live_enforce(req)
    assert res.decision == "REWRITE"
    assert isinstance(res.evaluator_trace, list) and len(res.evaluator_trace) == 1
    assert res.evaluator_trace[0]["rewrite_class"] is not None


def test_decision_mapping_applied_block():
    req = make_request(meta={"emotional_output": {"tone": "neutral", "dependency_score": 0.0}, "risk_flags": ["HIGH_RISK"]})
    res = live_enforce(req)
    assert res.decision == "BLOCK"
    assert isinstance(res.evaluator_trace, list) and len(res.evaluator_trace) == 1
    entry = res.evaluator_trace[0]
    assert set(entry.keys()) == {"decision", "rewrite_class"}


def test_block_never_calls_akanksha(monkeypatch):
    called = {"value": False}

    def guard(**kwargs):
        called["value"] = True
        raise AssertionError("send_to_akanksha must not be called on BLOCK")

    monkeypatch.setattr(gw, "send_to_akanksha", guard)

    req = make_request(meta={"emotional_output": {"tone": "neutral", "dependency_score": 0.0}, "risk_flags": ["HIGH_RISK"]})
    res = live_enforce(req)
    assert res.decision == "BLOCK"
    assert called["value"] is False


def test_reason_constants_stable_success_and_fail_closed(monkeypatch):
    # Success path reason
    req_ok = make_request()
    res_ok = live_enforce(req_ok)
    assert res_ok.reason == "DETERMINISTIC_ENFORCEMENT_APPLIED"

    # Fail-closed path reason by breaking enforce
    real_enforce = gw.enforce

    def boom(_):
        raise RuntimeError("broken")

    try:
        monkeypatch.setattr(gw, "enforce", boom)
        res_fail = live_enforce(make_request())
        assert res_fail.decision == "BLOCK"
        assert res_fail.reason == "ENFORCEMENT_FAILURE_FAIL_CLOSED"
    finally:
        monkeypatch.setattr(gw, "enforce", real_enforce)
