from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class ZoneState:
    corrosion_rate: float
    coating_thickness: float
    barnacle_density: float
    oxygen_level: float
    surface_roughness: float

    def apply_delta(self, delta: dict) -> "ZoneState":
        """
        Derives a new deterministic ZoneState by accumulating physical deltas.
        We cap parameters to physical realism if necessary, or just blindly sum for math.
        """
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
