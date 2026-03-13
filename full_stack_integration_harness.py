import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from cycle1.state_evolution_engine import StateVector, Observation
from cycle2.measurement_policy import ProjectiveMeasurementPolicy, MeasurementPolicy
from cycle3.integration import QuantumFoundationSystem
from cycle4.error_enforcement_engine import ErrorEnforcementEngine
from cycle4.correction_primitives import SyndromeToken
from cycle5.nogo_enforcement import NoGoEnforcementEngine
from cycle5.nogo_primitives import StateReference
from cycle7.complex_vector import ComplexVector
from cycle8.core_state import QuantumState
from cycle8.core_operators import UnitaryOperator


class FullStackHarness:
    """
    The definitive integrated system combining Cycles 1 through 8.
    Ensures mathematical fidelity at initialization and evolution, causality 
    timeline tracking, and adherence to physical (Error) and structural (No-Go) constraints.
    """
    def __init__(self, initial_amplitudes: dict):
        # 1. Math Verification Layer (C6/C7/C8)
        # Guarantees L2-Norm = 1.0, blocks malformed state constructs.
        q_state = QuantumState.from_dict(initial_amplitudes)
        
        # 2. Rehydrate into Logic Cycle 1 state. 
        # C1 strictly enforces dimensionality. C7's ComplexVector drops zero amplitudes.
        # We must restore structural zeros to satisfy C1 dimension invariants.
        c1_amps = {k: q_state.vector.amplitudes.get(k, complex(0)) for k in initial_amplitudes.keys()}
        self.c1_state = StateVector(c1_amps)
        
        # 3. Causality Timeline Wiring (C1-C3)
        self.system = QuantumFoundationSystem(self.c1_state, "FullStackDeterministicHarness")
        self.system.register_measurement_policy(ProjectiveMeasurementPolicy())
        
        # 4. Strict Physical Corridors (C4, C5)
        self.error_layer = ErrorEnforcementEngine(
            self.c1_state, 
            self.system.state_engine, 
            self.system.collapse_engine, 
            self.system.timeline
        )
        self.nogo_layer = NoGoEnforcementEngine(
            self.system.state_engine, 
            self.system.collapse_engine, 
            self.system.timeline, 
            self.error_layer.error_model
        )
        
        # Obtain linear causality reference to guard against parallel forks
        self.state_reference = self.nogo_layer.root_reference

    def define_unitary_operation(self, rule_name: str, matrix: dict, description: str = ""):
        """
        Validates mathematical integrity (U^dagger * U = I) via Cycle 6/8 and registers 
        it as an architectural transition rule.
        """
        # Math Seal Verification
        UnitaryOperator(matrix) 
        
        def verified_rule_fn(state: StateVector, obs: Observation) -> StateVector:
            # Rehydrate to formal Hilbert space
            q = QuantumState.from_dict(state.as_dict())
            u = UnitaryOperator(matrix)
            new_q = u.evolve(q)
            
            # Maintain strict Cycle 1 dimensionality
            new_c1_amps = {k: new_q.vector.amplitudes.get(k, complex(0)) for k in state.as_dict().keys()}
            return StateVector(new_c1_amps)
            
        self.system.register_transition_rule(rule_name, verified_rule_fn, description)

    def evolve_deterministic(self, rule_name: str):
        """
        Applies a validated evolution algorithmically while guarding against cloning
        and unphysical timeline modifications.
        """
        obs = Observation(rule_name, ())
        ref, causal_event = self.nogo_layer.evolve_strictly(self.state_reference, obs, noise_fidelity=1.0)
        self.state_reference = ref
        
        # Keep C4 ideal state tracked synchronously for physical auditing symmetry
        self.error_layer._ideal_state = self.system.state_engine.current_state
        return ref

    def measure_deterministic(self, token_id: str, seed: int):
        """
        Performs irreversible collapse utilizing exact entropy and causality tracking.
        """
        token = self.system.issue_collapse_token("ProjectiveMeasurement", token_id)
        ref, collapse_event, causal_event = self.nogo_layer.measure_strictly(self.state_reference, token, seed)
        self.state_reference = ref
        
        # Sync C4 logic explicitly
        self.error_layer._ideal_state = collapse_event.result.post_state
        self.error_layer._physical_state = collapse_event.result.post_state
        return collapse_event

    def seal_timeline(self, reason: str):
        """Places a terminal point of no return."""
        self.system.seal_timeline(reason)
        
    def verify_all_invariants(self) -> dict:
        """Runs the complete suite of invariants across all sub-engines."""
        report = self.system.verify_all_invariants()
        
        # C4 error boundaries
        c4 = self.error_layer.run_error_invariants()
        report['cycle4'] = {"passed": c4.passed, "failed": c4.failed}
        
        # C5 absolute constraints
        from cycle5.invariants import run_all_nogo_invariants
        c5 = run_all_nogo_invariants(self.nogo_layer.timeline)
        report['cycle5'] = {"passed": c5.passed, "failed": c5.failed}
        
        return report

if __name__ == "__main__":
    # Test initialization
    import math
    harness = FullStackHarness({"0": 1.0, "1": 0.0})
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {
        ("0", "0"): inv_sq2, ("0", "1"): inv_sq2,
        ("1", "0"): inv_sq2, ("1", "1"): -inv_sq2
    }
    harness.define_unitary_operation("H", h_matrix, "Hadamard")
    print("Executing complete integration mapping... ")
    harness.evolve_deterministic("H")
    harness.measure_deterministic("m1", 42)
    harness.seal_timeline("Test EOF")
    r = harness.verify_all_invariants()
    failed = False
    for layer, results in r.items():
        if results['failed']:
            print(f"FAILED INVARIANTS in {layer}: {results['failed']}")
            failed = True
    if not failed:
        print("ALL TESTS PASSED. SYSTEM SEALED.")
