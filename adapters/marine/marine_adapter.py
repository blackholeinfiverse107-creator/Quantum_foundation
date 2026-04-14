import hashlib
import uuid
import time
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class ZoneState:
    corrosion_depth_mm: float
    coating_thickness_mm: float
    roughness_Ra_um: float
    fouling_coverage_frac: float
    fouling_thickness_mm: float

    def apply_delta(self, delta: dict) -> "ZoneState":
        new_fouling = min(1.0, max(0.0, self.fouling_coverage_frac + delta.get("delta_fouling_coverage", 0.0)))
        
        return ZoneState(
            corrosion_depth_mm=self.corrosion_depth_mm + delta.get("delta_corrosion_mm", 0.0),
            coating_thickness_mm=self.coating_thickness_mm + delta.get("delta_coating_mm", 0.0), # delta_coating is usually negative
            roughness_Ra_um=self.roughness_Ra_um + delta.get("delta_roughness_um", 0.0),
            fouling_coverage_frac=new_fouling,
            fouling_thickness_mm=self.fouling_thickness_mm + delta.get("delta_fouling_thick_mm", 0.0),
        )

    def to_dict(self) -> dict:
        return {
            "corrosion_depth_mm": self.corrosion_depth_mm,
            "coating_thickness_mm": self.coating_thickness_mm,
            "roughness_Ra_um": self.roughness_Ra_um,
            "fouling_coverage_frac": self.fouling_coverage_frac,
            "fouling_thickness_mm": self.fouling_thickness_mm
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
        Expected shape matches Dhiraj's Contract: {"zones": [{"zone_id": "BOW_PORT", "state_transitions": {...}}, ...]}
        """
        zones_data = payload.get("zones", [])
        for zone in zones_data:
            z_id = zone.get("zone_id")
            if not z_id: continue
            
            transitions = zone.get("state_transitions", {})
            delta = {
                "delta_corrosion_mm": transitions.get("delta_corrosion_mm", {}).get("value", 0.0),
                "delta_coating_mm": transitions.get("delta_coating_mm", {}).get("value", 0.0),
                "delta_roughness_um": transitions.get("delta_roughness_um", {}).get("value", 0.0),
                "delta_fouling_coverage": transitions.get("delta_fouling_coverage", {}).get("value", 0.0),
                "delta_fouling_thick_mm": transitions.get("delta_fouling_thick_mm", {}).get("value", 0.0),
            }
            try:
                self.apply_transition(z_id, delta)
            except ValueError:
                pass # Unregistered zones from simulation are ignored

    def get_state_hash(self) -> str:
        """
        Construct a strict, ordering-independent deterministic hash of all zones.
        """
        h = hashlib.sha256()
        for z_id in sorted(self._zones.keys()):
            z = self._zones[z_id]
            h.update(z_id.encode('utf-8'))
            z_str = f"{z.corrosion_depth_mm:.6f}_{z.coating_thickness_mm:.6f}_{z.roughness_Ra_um:.6f}_{z.fouling_coverage_frac:.6f}_{z.fouling_thickness_mm:.6f}"
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
