import hashlib
from typing import Dict, Optional
from marine_state_schema import ZoneState

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

    def hash(self) -> str:
        """
        Construct a strict, ordering-independent deterministic hash of all zones
        to ensure multi-node replay convergence.
        """
        h = hashlib.sha256()
        for z_id in sorted(self._zones.keys()):
            z = self._zones[z_id]
            h.update(z_id.encode('utf-8'))
            # Format to strict precision to avoid floating point cross-platform drift
            z_str = f"{z.corrosion_rate:.6f}_{z.coating_thickness:.6f}_{z.barnacle_density:.6f}_{z.oxygen_level:.6f}_{z.surface_roughness:.6f}"
            h.update(z_str.encode('utf-8'))
        return h.hexdigest()
