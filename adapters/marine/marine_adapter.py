import hashlib
import uuid
import time
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class ZoneState:
    corrosion_rate: float
    coating_thickness: float
    barnacle_density: float
    oxygen_level: float
    surface_roughness: float

    def apply_delta(self, delta: dict) -> "ZoneState":
        return ZoneState(
            corrosion_rate=self.corrosion_rate + delta.get("corrosion_rate", 0.0),
            coating_thickness=self.coating_thickness + delta.get("coating_thickness", 0.0),
            barnacle_density=self.barnacle_density + delta.get("barnacle_density", 0.0),
            oxygen_level=max(0.0, self.oxygen_level + delta.get("oxygen_level", 0.0)),
            surface_roughness=self.surface_roughness + delta.get("surface_roughness", 0.0),
        )

    def to_dict(self) -> dict:
        return {
            "corrosion_rate": self.corrosion_rate,
            "coating_thickness": self.coating_thickness,
            "barnacle_density": self.barnacle_density,
            "oxygen_level": self.oxygen_level,
            "surface_roughness": self.surface_roughness
        }

class MarineStateEngine:
    """
    Manages physical state mutations across discrete hull zones.
    Produces deterministic hashes of the complete zone state.
    """
    def __init__(self, initial_zones: Dict[str, ZoneState]):
        self._zones = initial_zones.copy()

    def get_zone(self, zone_id: str) -> Optional[ZoneState]:
        return self._zones.get(zone_id)

    def get_all_zones(self) -> Dict[str, dict]:
        return {k: v.to_dict() for k, v in self._zones.items()}

    def apply_transition(self, zone_id: str, delta: dict):
        if zone_id not in self._zones:
            raise ValueError(f"[Marine Engine] Unknown physical zone: {zone_id}")
        self._zones[zone_id] = self._zones[zone_id].apply_delta(delta)

    def apply_event_payload(self, payload: dict):
        """
        Takes the untyped payload from the ExecutionEvent and applies it across zones.
        Expected shape: {"zone_1": {"corrosion_rate": 0.01}, "zone_2": {...}}
        """
        for zone_id, delta in payload.items():
            self.apply_transition(zone_id, delta)

    def get_state_hash(self) -> str:
        """
        Construct a strict, ordering-independent deterministic hash of all zones.
        """
        h = hashlib.sha256()
        for z_id in sorted(self._zones.keys()):
            z = self._zones[z_id]
            h.update(z_id.encode('utf-8'))
            z_str = f"{z.corrosion_rate:.6f}_{z.coating_thickness:.6f}_{z.barnacle_density:.6f}_{z.oxygen_level:.6f}_{z.surface_roughness:.6f}"
            h.update(z_str.encode('utf-8'))
        return h.hexdigest()

def create_marine_update_event(origin_node: str, dhiraj_payload: dict) -> dict:
    """
    Converts Dhiraj's output schema into a raw dict that can be passed to
    the generic ExecutionEvent.
    """
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "STATE_UPDATE",
        "payload": dhiraj_payload, # E.g. {"zone_1": {"corrosion_rate": 0.02}}
        "origin_node": origin_node,
        "timestamp": time.monotonic()
    }
