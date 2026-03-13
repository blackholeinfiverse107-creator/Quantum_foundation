"""
Cycle 4 — Quantum Error Models and Constraints
==============================================

This module formalizes error, noise, and decoherence as first-class 
architectural constraints. In this system, errors are not exceptions to be 
caught and ignored; they are irreversible physical processes that destroy 
quantum information.

Core Principles:
1. Measurement Disturbance: Extracting information strictly bounds what remains.
2. Decoherence: Interactions with the environment cause non-unitary evolution.
3. Unitary Noise: Imperfect control applies valid operations but with incorrect parameters.

Information destroyed by measurement or decoherence CANNOT be restored by 
rule-based "undo". It can only be mitigated through ancilla-based 
fault-tolerance, which costs additional qubits.
"""

from dataclasses import dataclass
from typing import Optional

from cycle1.state_evolution_engine import StateVector
from cycle2.measurement_policy import MeasurementResult

class ArchitecturalErrorViolation(Exception):
    """Raised when an operation attempts to violate quantum error bounds, e.g., silent restoration of wiped data."""
    pass


@dataclass(frozen=True)
class ErrorProfile:
    """
    Describes the error bounds of a specific quantum operation or state.
    """
    information_loss_bits: float
    decoherence_rate: float
    unitary_fidelity: float  # [0.0, 1.0] where 1.0 is perfect

    def __post_init__(self):
        if self.information_loss_bits < 0:
            raise ValueError("Information loss cannot be negative.")
        if not (0.0 <= self.unitary_fidelity <= 1.0):
            raise ValueError("Unitary fidelity must be between 0.0 and 1.0.")
        if self.decoherence_rate < 0:
            raise ValueError("Decoherence rate cannot be negative.")


class QuantumError:
    """Base class for physical quantum errors."""
    def __init__(self, description: str, severity: str):
        self.description = description
        self.severity = severity  # "TOLERABLE", "FATAL", "UNRECOVERABLE"

    @property
    def is_recoverable(self) -> bool:
        return self.severity == "TOLERABLE"


class DecoherenceError(QuantumError):
    """
    Error caused by uncontrolled interaction with the environment.
    Transforms pure states into mixed states (loss of superposition/phase).
    Architecturally: Cannot be reversed without an ancilla system.
    """
    def __init__(self, rate: float):
        super().__init__(f"Decoherence at rate {rate}", "UNRECOVERABLE")
        self.rate = rate


class MeasurementDisturbance(QuantumError):
    """
    Error caused by acquiring classical information.
    Architecturally: The information extracted dictates exactly how much the state was disturbed.
    """
    def __init__(self, result: MeasurementResult):
        super().__init__(
            f"Measurement collapsed state, losing {result.information_loss_declared} bits",
            "UNRECOVERABLE"
        )
        self.result = result


class UnitaryNoise(QuantumError):
    """
    Error caused by imperfect gates (e.g., rotating by π/2 + ε).
    Architecturally: This is a coherent error. It IS reversible (TOLERABLE) IF 
    the exact inverse unitary is known, but practically unknown.
    """
    def __init__(self, fidelity: float):
        # Even if coherent, without knowing the exact error, it's practically fatal over time unless corrected.
        # But we classify it as TOLERABLE under active quantum error correction.
        super().__init__(f"Unitary noise with fidelity {fidelity}", "TOLERABLE")
        self.fidelity = fidelity


def calculate_fidelity(state_a: StateVector, state_b: StateVector) -> float:
    """
    Calculates the fidelity |<a|b>|^2 between two pure states.
    Fidelity = 1.0 means identical states. Fidelity = 0.0 means orthogonal states.
    """
    dict_a = state_a.as_dict()
    dict_b = state_b.as_dict()
    keys = set(dict_a.keys()) | set(dict_b.keys())
    inner_product = complex(0)
    for k in keys:
        amp_a = dict_a.get(k, complex(0))
        amp_b = dict_b.get(k, complex(0))
        # <a|b> = sum(a* b)
        inner_product += amp_a.conjugate() * amp_b
    
    fidelity = abs(inner_product) ** 2
    
    # Handle floating point inaccuracies
    if fidelity > 1.0:
        fidelity = 1.0
    elif fidelity < 0.0:
        fidelity = 0.0
        
    return fidelity


class ErrorModel:
    """
    Applies strict physical error bounds to state evolution.
    """
    def __init__(self, base_decoherence: float = 0.0, base_fidelity: float = 1.0):
        self._total_info_loss = 0.0
        self._decoherence_rate = base_decoherence
        self._base_fidelity = base_fidelity

    def register_measurement_disturbance(self, loss_bits: float) -> None:
        """Permanently adds to the unrecoverable information loss."""
        if loss_bits < 0:
            raise ValueError("Cannot recover information by negative loss.")
        self._total_info_loss += loss_bits

    @property
    def total_unrecoverable_loss(self) -> float:
        return self._total_info_loss
