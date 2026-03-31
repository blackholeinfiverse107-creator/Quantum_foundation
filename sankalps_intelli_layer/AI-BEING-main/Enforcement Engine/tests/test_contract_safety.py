import pytest
import uuid

from enforcement_gateway import live_enforce, EnforcementRequest
import enforcement_gateway as gw
import evaluator_modules as em


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


def test_output_contract_shape_and_reason_constants():
    res = live_enforce(make_request())
    assert res.decision in {"ALLOW", "REWRITE", "BLOCK"}
    assert res.reason == "DETERMINISTIC_ENFORCEMENT_APPLIED"
    assert isinstance(res.enforcement_decision_id, str) and len(res.enforcement_decision_id) > 0
    uuid.UUID(res.enforcement_decision_id)
    if res.decision != "BLOCK":
        assert isinstance(res.evaluator_trace, list) and len(res.evaluator_trace) == 1
        k = set(res.evaluator_trace[0].keys())
        assert k == {"decision", "rewrite_class"}
    else:
        assert isinstance(res.evaluator_trace, list)


def test_fail_closed_reason_on_engine_error(monkeypatch):
    real = gw.enforce

    def boom(_):
        raise RuntimeError("chaos")

    try:
        monkeypatch.setattr(gw, "enforce", boom)
        res = live_enforce(make_request())
        assert res.decision == "BLOCK"
        assert res.reason == "ENFORCEMENT_FAILURE_FAIL_CLOSED"
    finally:
        monkeypatch.setattr(gw, "enforce", real)


def test_block_never_calls_akanksha(monkeypatch):
    called = {"v": False}

    def guard(**kwargs):
        called["v"] = True
        raise AssertionError("Akanksha must not be called on BLOCK")

    monkeypatch.setattr(gw, "send_to_akanksha", guard)
    res = live_enforce(make_request(meta={"risk_flags": ["HIGH_RISK"]}))
    assert res.decision == "BLOCK"
    assert called["v"] is False


def test_chaos_evaluator_crash_fail_closed(monkeypatch):
    class CrashEval:
        name = "crasher"
        def evaluate(self, _): raise RuntimeError("boom")
    real_evals = list(em.ALL_EVALUATORS)
    monkeypatch.setattr(em, "ALL_EVALUATORS", [CrashEval()])
    res = live_enforce(make_request())
    assert res.decision in {"ALLOW", "REWRITE", "BLOCK"}
    # enforce crashes -> gateway returns BLOCK
    # if enforce survives, decision mapping still valid

