import hashlib

class MockAdapter:
    """A trivial adapter to prove the engine is completely decoupled from domain logic."""
    def __init__(self):
        self.val = 0

    def apply_event_payload(self, payload: dict):
        if "add" in payload:
            self.val += payload["add"]

    def get_state_hash(self) -> str:
        h = hashlib.sha256()
        h.update(str(self.val).encode('utf-8'))
        return h.hexdigest()
        
    def to_dict(self) -> dict:
        return {"val": self.val}
