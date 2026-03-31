from fastapi.testclient import TestClient
from app.main import app
from app.core.karma_tone_mapper import karma_band, apply_karma_to_band
import app.core.assistant_orchestrator as ao


client = TestClient(app)
client.headers.update({"X-API-Key": "localtest"})


def _ensure_simple_response(monkeypatch):
    if not hasattr(ao.decision_hub, "simple_response"):
        def simple_response(text: str) -> str:
            return f"Echo: {text}"
        monkeypatch.setattr(ao.decision_hub, "simple_response", simple_response, raising=False)


def make_payload(message: str, karma_hint, session_id: str) -> dict:
    return {
        "version": "3.0.0",
        "input": {
            "message": message,
            "summarized_payload": {"summary": message, "karma_hint": karma_hint},
        },
        "context": {
            "platform": "web",
            "device": "desktop",
            "voice_input": False,
            "session_id": session_id,
        },
    }


def test_karma_band_mapping():
    assert karma_band(None) == "neutral"
    assert karma_band(0.0) == "neutral"
    assert karma_band(0.5) == "positive"
    assert karma_band(-0.5) == "negative"


def test_apply_karma_to_band():
    assert apply_karma_to_band("neutral", "positive") == "steady_supportive"
    assert apply_karma_to_band("neutral", "negative") == "calm_supportive"
    assert apply_karma_to_band("calm_supportive", "positive") == "calm_supportive"
    assert apply_karma_to_band("steady_supportive", "negative") == "calm_supportive"


def test_positive_karma_hint_nudges_tone_without_leak(monkeypatch):
    _ensure_simple_response(monkeypatch)

    def gw(**kwargs):
        return {"decision": "EXECUTE", "rewrite_class": None}

    monkeypatch.setattr(ao, "raj_execution_gateway", gw, raising=False)

    payload = make_payload("This is great!!!", karma_hint=0.8, session_id="sess-karma-pos")
    resp = client.post("/api/assistant", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "karma" not in text.lower()


def test_negative_karma_hint_nudges_tone_without_leak(monkeypatch):
    _ensure_simple_response(monkeypatch)

    def gw(**kwargs):
        return {"decision": "EXECUTE", "rewrite_class": None}

    monkeypatch.setattr(ao, "raj_execution_gateway", gw, raising=False)

    payload = make_payload("Handle this carefully!!!", karma_hint=-0.9, session_id="sess-karma-neg")
    resp = client.post("/api/assistant", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "karma" not in text.lower()


def test_neutral_karma_hint_keeps_tone_neutral_without_leak(monkeypatch):
    _ensure_simple_response(monkeypatch)

    def gw(**kwargs):
        return {"decision": "EXECUTE", "rewrite_class": None}

    monkeypatch.setattr(ao, "raj_execution_gateway", gw, raising=False)

    payload = make_payload("Regular request!!!", karma_hint=0.0, session_id="sess-karma-neu")
    resp = client.post("/api/assistant", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    text = data["result"]["response"]
    assert "karma" not in text.lower()

