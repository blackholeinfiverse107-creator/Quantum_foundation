import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
client.headers.update({"X-API-Key": "localtest"})

def test_tone_stability_across_turns():
    session_id = "sess-continuity-1"
    messages = [
        "create task urgent!!! angry tone task",
        "create task immediately please!!! frustrated task",
        "task now ASAP!!! problem task",
        "task priority high!!! angry",
        "schedule meeting critical!!! frustrated",
        "send email urgent!!! problem",
        "create note important!!! angry",
        "manage calendar now!!! frustrated",
        "task reminder ASAP!!! problem",
        "task follow-up urgent!!! angry",
        "task again!!! frustrated",
        "finalize task urgent!!! problem",
    ]
    for msg in messages:
        payload = {
            "version": "3.0.0",
            "input": {"message": msg},
            "context": {"platform": "web", "device": "desktop", "voice_input": False, "session_id": session_id}
        }
        resp = client.post("/api/assistant", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ["success", "error"]
        if data["status"] == "success":
            text = data["result"]["response"]
            assert "!" not in text
