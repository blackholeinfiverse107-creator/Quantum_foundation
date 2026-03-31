import itertools
import json
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.core.assistant_orchestrator as ao


client = TestClient(app)
client.headers.update({"X-API-Key": "localtest"})


def make_base_payload() -> Dict[str, Any]:
    return {
        "version": "3.0.0",
        "input": {
            "message": "Base message",
            "summarized_payload": {
                "summary": "Base message summary",
                "karma_hint": 0.0,
            },
        },
        "context": {
            "platform": "web",
            "device": "desktop",
            "session_id": "sess-chaos",
            "voice_input": False,
        },
    }


def _ensure_simple_response(monkeypatch):
    if not hasattr(ao.decision_hub, "simple_response"):
        def simple_response(text: str) -> str:
            return f"Echo: {text}"
        monkeypatch.setattr(ao.decision_hub, "simple_response", simple_response, raising=False)


def _ensure_raj_gateway(monkeypatch):
    def gw(**kwargs):
        return {"decision": "EXECUTE", "rewrite_class": None}
    monkeypatch.setattr(ao, "raj_execution_gateway", gw, raising=False)


def _assert_graceful(response):
    assert response.status_code in {200, 400, 422}
    data = response.json()
    assert isinstance(data, dict)
    if response.status_code == 200:
        assert data["version"] == "3.0.0"
        assert data["status"] in ["success", "error"]
        if data["status"] == "success":
            assert "result" in data
            assert "response" in data["result"]
        else:
            assert "error" in data
    elif response.status_code == 400:
        assert "detail" in data
    elif response.status_code == 422:
        assert "detail" in data


@pytest.mark.parametrize(
    "mutator",
    [
        lambda p: p.pop("version", None),
        lambda p: p.pop("input", None),
        lambda p: p.pop("context", None),
        lambda p: p["input"].pop("message", None),
        lambda p: p["input"].pop("summarized_payload", None),
        lambda p: p["context"].pop("platform", None),
        lambda p: p["context"].pop("device", None),
        lambda p: p["context"].pop("voice_input", None),
        lambda p: p["context"].__setitem__("session_id", None),
    ],
)
def test_missing_fields_graceful(monkeypatch, mutator):
    _ensure_simple_response(monkeypatch)
    _ensure_raj_gateway(monkeypatch)
    payload = make_base_payload()
    mutator(payload)
    response = client.post("/api/assistant", json=payload)
    _assert_graceful(response)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda p: p.__setitem__("version", 3),
        lambda p: p["input"].__setitem__("message", 123),
        lambda p: p["input"].__setitem__("summarized_payload", "not-a-dict"),
        lambda p: p["input"]["summarized_payload"].__setitem__("summary", 999),
        lambda p: p["input"]["summarized_payload"].__setitem__("karma_hint", "high"),
        lambda p: p["context"].__setitem__("platform", 123),
        lambda p: p["context"].__setitem__("device", 999),
        lambda p: p["context"].__setitem__("voice_input", "false"),
    ],
)
def test_corrupt_types_graceful(monkeypatch, mutator):
    _ensure_simple_response(monkeypatch)
    _ensure_raj_gateway(monkeypatch)
    payload = make_base_payload()
    mutator(payload)
    response = client.post("/api/assistant", json=payload)
    _assert_graceful(response)


def test_empty_body_graceful():
    response = client.post("/api/assistant", data="")
    assert response.status_code in {400, 422}
    data = response.json()
    assert "detail" in data


def test_non_json_body_graceful():
    response = client.post("/api/assistant", data="not-json", headers={"Content-Type": "text/plain"})
    assert response.status_code in {400, 422}
    data = response.json()
    assert "detail" in data


def test_internal_timeout_like_signal_graceful(monkeypatch):
    _ensure_simple_response(monkeypatch)
    _ensure_raj_gateway(monkeypatch)

    def slow_summary(text: str):
        raise TimeoutError("simulated slow summary flow")

    monkeypatch.setattr(ao.summary_flow, "generate_summary", slow_summary, raising=False)
    payload = make_base_payload()
    response = client.post("/api/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "3.0.0"
    assert data["status"] == "error"
    assert data["error"]["code"] == "INTERNAL_ERROR"


def test_internal_adapter_payload_failure_graceful(monkeypatch):
    _ensure_simple_response(monkeypatch)
    _ensure_raj_gateway(monkeypatch)

    def bad_enforcement_payload(**kwargs):
        raise RuntimeError("adapter payload failure")

    monkeypatch.setattr(ao, "build_enforcement_payload", bad_enforcement_payload, raising=False)
    payload = make_base_payload()
    response = client.post("/api/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "3.0.0"
    assert data["status"] == "error"
    assert data["error"]["code"] == "INTERNAL_ERROR"


def test_multiple_randomized_mutations_graceful(monkeypatch):
    _ensure_simple_response(monkeypatch)
    _ensure_raj_gateway(monkeypatch)
    base = make_base_payload()
    keys_to_corrupt = [
        ("input", "message"),
        ("input", "summarized_payload"),
        ("context", "platform"),
        ("context", "device"),
        ("context", "voice_input"),
    ]
    for combo_len in range(1, len(keys_to_corrupt) + 1):
        for combo in itertools.combinations(keys_to_corrupt, combo_len):
            payload = json.loads(json.dumps(base))
            for path in combo:
                scope, key = path
                if scope == "input":
                    payload["input"][key] = None
                elif scope == "context":
                    payload["context"][key] = None
            response = client.post("/api/assistant", json=payload)
            _assert_graceful(response)

