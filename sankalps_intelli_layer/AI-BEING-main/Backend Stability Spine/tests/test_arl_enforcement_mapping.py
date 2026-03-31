from fastapi.testclient import TestClient
from app.main import app
import app.core.assistant_orchestrator as ao


client = TestClient(app)
client.headers.update({"X-API-Key": "localtest"})


LIVE_TRACE_MAP = {
    "EXECUTE": "ALLOW",
    "REWRITE": "SOFT_REDIRECT",
    "BLOCK": "BLOCK",
    "UNKNOWN": "BLOCK_FALLBACK",
}


def make_request(message: str, platform: str = "web", device: str = "desktop", session_id: str = "sess-map-1"):
    return {
        "version": "3.0.0",
        "input": {"message": message},
        "context": {
            "platform": platform,
            "device": device,
            "voice_input": False,
            "session_id": session_id,
        },
    }


def stub_gateway(decision: str | None, rewrite_class: str | None = None):
    def _gw(**kwargs):
        if decision is None:
            return {}
        return {
            "decision": decision,
            "rewrite_class": rewrite_class,
        }

    return _gw


def _ensure_simple_response(monkeypatch):
    if not hasattr(ao.decision_hub, "simple_response"):
        def simple_response(text: str) -> str:
            return f"Echo: {text}"
        monkeypatch.setattr(ao.decision_hub, "simple_response", simple_response, raising=False)


def test_execute_maps_to_allow_messaging(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway("EXECUTE"), raising=False)
    resp = client.post("/api/assistant", json=make_request("Hello world"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I can’t go down that path" not in text
    assert "I’ve adjusted the phrasing" not in text


def test_execute_vr_maps_to_allow_with_optional_warning(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway("EXECUTE"), raising=False)
    resp = client.post("/api/assistant", json=make_request("Hello in VR", platform="vr", device="vr-headset"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I can’t go down that path" not in text
    assert "I’ve adjusted the phrasing" not in text


def test_rewrite_maps_to_soft_redirect(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway("REWRITE", "REDUCE_EMOTIONAL_DEPENDENCY"), raising=False)
    resp = client.post("/api/assistant", json=make_request("Please help me, I can't live without this!!!"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I’ve adjusted the phrasing to keep things supportive and appropriate." in text


def test_rewrite_platform_safe_monkeypatch(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway("REWRITE", "PLATFORM_SAFE_REWRITE"), raising=False)
    resp = client.post("/api/assistant", json=make_request("subscribe now!!! click immediately"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I’ve adjusted the phrasing to keep things supportive and appropriate." in text


def test_block_maps_to_calm_refusal(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway("BLOCK"), raising=False)
    resp = client.post("/api/assistant", json=make_request("Do something unsafe"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I can’t go down that path" in text


def test_block_vr_maps_to_calm_refusal(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway("BLOCK"), raising=False)
    resp = client.post("/api/assistant", json=make_request("Do something unsafe in VR", platform="vr", device="vr-headset"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I can’t go down that path" in text


def test_unknown_decision_falls_back_to_block(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway("UNKNOWN"), raising=False)
    resp = client.post("/api/assistant", json=make_request("Unknown enforcement state"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I can’t go down that path" in text


def test_missing_decision_falls_back_to_block(monkeypatch):
    _ensure_simple_response(monkeypatch)
    monkeypatch.setattr(ao, "raj_execution_gateway", stub_gateway(None), raising=False)
    resp = client.post("/api/assistant", json=make_request("Missing decision"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I can’t go down that path" in text


def test_gateway_exception_falls_back_to_block(monkeypatch):
    _ensure_simple_response(monkeypatch)
    def boom(**kwargs):
        raise RuntimeError("upstream enforcement failure")

    monkeypatch.setattr(ao, "raj_execution_gateway", boom, raising=False)
    resp = client.post("/api/assistant", json=make_request("Exception from Raj"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "I can’t go down that path" in text
