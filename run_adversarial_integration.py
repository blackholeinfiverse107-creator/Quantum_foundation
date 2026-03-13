import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from full_stack_integration_harness import FullStackHarness
from cycle8.core_state import NormalizationInvariantError, InvalidStateStructureError, QuantumState
from cycle8.core_operators import NonUnitaryInvariantError
from cycle8.core_measurement import IncompletePOVMError, ProjectionOperator
from cycle5.nogo_primitives import NoCloningViolation, StateReference
from cycle5.nogo_enforcement import NoGoEnforcementEngine
from cycle1.state_evolution_engine import Observation

class AdversarialTester:
    def __init__(self):
        self.passes = 0
        self.failures = 0
        self.logs = []

    def log(self, text):
        print(text)
        self.logs.append(text)

    def assert_raises(self, func, *args, expected_exception, test_name):
        try:
            func(*args)
            self.log(f"[FAIL] {test_name}: Expected {expected_exception.__name__} but execution succeeded!")
            self.failures += 1
        except expected_exception as e:
            self.log(f"[PASS] {test_name}: Caught expected -> {e}")
            self.passes += 1
        except Exception as e:
            if isinstance(e, expected_exception):
                self.log(f"[PASS] {test_name}: Caught expected -> {e}")
                self.passes += 1
            else:
                self.log(f"[FAIL] {test_name}: Threw unexpected error {type(e).__name__}: {e}")
                self.failures += 1

    def run_tests(self):
        self.log("=== ADVERSARIAL INTEGRATION HARNESS ===")
        
        # 1. Invalid State Vectors (Norm != 1)
        self.assert_raises(
            FullStackHarness, {"0": 1.0, "1": 1.0},
            expected_exception=NormalizationInvariantError,
            test_name="Inject Un-normalized State Vector (Norm=1.414)"
        )
        
        # Zero Vector
        self.assert_raises(
            FullStackHarness, {"0": 0.0, "1": 0.0},
            expected_exception=InvalidStateStructureError,
            test_name="Inject Zero Amplitude Vector"
        )
        
        # Setup valid harness
        harness = FullStackHarness({"0": 1.0, "1": 0.0})
        
        # 2. Non-Unitary Operators
        non_unitary_matrix = {
            ("0", "0"): 0.9, ("0", "1"): 0.1,
            ("1", "0"): 0.1, ("1", "1"): 0.9
        }
        self.assert_raises(
            harness.define_unitary_operation, "BadGate", non_unitary_matrix, "Should fail",
            expected_exception=NonUnitaryInvariantError,
            test_name="Inject Non-Unitary Mathematical Operator"
        )
        
        # 3. Illegal Measurement Projections (Probabilities don't sum to 1)
        # Note: Projectors in harness are defined via policies. But we can test the raw math layer:
        def test_raw_incomplete_povm():
            state = QuantumState.from_dict({"0": 1.0})
            proj_bad = {"out1": ProjectionOperator({("0", "0"): 0.5})}
            from cycle8.core_measurement import MeasurementHarness
            MeasurementHarness.collapse(state, proj_bad, 42)
            
        self.assert_raises(
            test_raw_incomplete_povm,
            expected_exception=IncompletePOVMError,
            test_name="Attempt Measurement with Incomplete Mathematical Policy"
        )
        
        # 4. Cross-layer Mutation (Trying to mutate state dictionary after instantiation)
        def test_mutation():
            harness.c1_state.amplitudes[0] = 5.0 # Tuples are frozen, mutation raises TypeError
        
        self.assert_raises(
            test_mutation,
            expected_exception=TypeError,
            test_name="Attempt Cross-layer Private Property Mutation"
        )
        
        # 5. Cloning Operation (Trying to branch causal timeline logic)
        def test_cloning():
            # Get valid reference
            h_matrix = {("0", "0"): 1.0, ("1", "1"): 1.0}
            harness.define_unitary_operation("Id", h_matrix)
            
            # Evolve correctly once
            harness.evolve_deterministic("Id")
            
            old_ref = harness.state_reference
            
            # Since C5 uses `expected_next_event_id` to block out-of-band events from state copies, 
            # we need to simulate the cloning by creating a parallel enforcement engine 
            # OR by copying the reference and running it simultaneously.
            # But wait, C5's explicit check for cloning is `check_independent_copy()`
            ref_b = StateReference(harness.state_reference.reference_id)
            harness.nogo_layer.check_independent_copy(harness.state_reference, ref_b)
            
        self.assert_raises(
            test_cloning,
            expected_exception=NoCloningViolation,
            test_name="Attempt Causal History Branching / State Reference Cloning"
        )

        self.log(f"\n--- RESULTS: {self.passes} PASSED | {self.failures} FAILED ---")
        
        # Generate the report output
        with open(os.path.join(os.path.dirname(__file__), "integration_adversarial_report.md"), "w", encoding="utf-8") as f:
            f.write("# Adversarial Integration Stress Test\n\n")
            f.write("Systematic attempt to compromise the quantum foundations by violating core bounds at mathematical, logical, and structural layers.\n\n")
            f.write("## Test Log\n")
            f.write("```\n")
            f.write("\n".join(self.logs))
            f.write("\n```\n")

if __name__ == "__main__":
    tester = AdversarialTester()
    tester.run_tests()
