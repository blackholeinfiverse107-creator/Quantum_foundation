"""
Cycle 8 — Integration Harness
=============================

Full deterministic chain validating State -> Operator -> Measurement.
This harness proves that the mathematical core operates correctly 
end-to-end without invariant violations or abstraction leakage.
"""

from typing import Tuple, Mapping
import math

from cycle8.core_state import QuantumState, InvariantViolation
from cycle8.core_operators import UnitaryOperator
from cycle8.core_measurement import MeasurementHarness, ProjectionOperator


class IntegrationChainHarness:
    """Automated integration chain proving the mathematical base works."""

    @staticmethod
    def run_deterministic_chain(
        initial_amplitudes: Mapping[str, complex],
        evolution_matrix: Mapping[Tuple[str, str], complex],
        projectors: Mapping[str, Mapping[Tuple[str, str], complex]],
        seed: int
    ) -> Tuple[QuantumState, QuantumState, str, QuantumState]:
        """
        Runs the full Hilbert space core chain.
        Returns: (InitialState, EvolvedState, MeasurementOutcome, FinalState)
        Raises: InvariantViolation if any rule is broken.
        """
        
        # 1. State Invariant Construction
        try:
            initial_state = QuantumState.from_dict(initial_amplitudes)
        except Exception as e:
            raise InvariantViolation(f"Initial state construction failed: {e}")

        # 2. Operator Unitarity Seal
        try:
            unitary = UnitaryOperator(evolution_matrix)
        except Exception as e:
            raise InvariantViolation(f"Evolution operator rejected: {e}")

        # 3. Deterministic Evolution (Norm is preserved)
        try:
            evolved_state = unitary.evolve(initial_state)
        except Exception as e:
            raise InvariantViolation(f"Evolution failure: {e}")

        # 4. Measurement Harness (Hermitian projectors, Sum=1, deterministic seed)
        built_projectors = {}
        try:
            for outcome, mat in projectors.items():
                built_projectors[outcome] = ProjectionOperator(mat)
        except Exception as e:
             raise InvariantViolation(f"Projector construction rejected: {e}")

        try:
            outcome, final_state = MeasurementHarness.collapse(evolved_state, built_projectors, seed)
        except Exception as e:
            raise InvariantViolation(f"Measurement collapse rejected: {e}")

        return initial_state, evolved_state, outcome, final_state


if __name__ == "__main__":
    # Example End-to-End run proving the mathematical harness
    
    # |0> State
    state_amps = {"0": complex(1.0)}
    
    # Hadamard Unitary
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {
        ("0", "0"): inv_sq2, ("0", "1"): inv_sq2,
        ("1", "0"): inv_sq2, ("1", "1"): -inv_sq2
    }
    
    # Proper Z-basis Projectors
    proj_matrices = {
        "out_0": {("0", "0"): 1.0},
        "out_1": {("1", "1"): 1.0}
    }
    
    try:
        init, ev, out, final = IntegrationChainHarness.run_deterministic_chain(
            state_amps, h_matrix, proj_matrices, seed=42
        )
        print("Integration Chain: SUCCESS")
        print(f"Init:     {init}")
        print(f"Evolved:  {ev}")
        print(f"Outcome:  {out}")
        print(f"Final:    {final}")
    except InvariantViolation as e:
        print(f"Integration Chain: FAILED -> {e}")
