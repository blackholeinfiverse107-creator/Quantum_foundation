import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(__file__))

from cycle8.integration_harness import IntegrationChainHarness
from cycle8.core_state import InvariantViolation
from cycle7.complex_vector import ComplexVector

def log_attack(name, func):
    print(f"=== {name} ===")
    try:
        func()
        print("[!] VULNERABILITY FOUND: System silently accepted malformed payload.\\n")
    except Exception as e:
        print(f"[+] SYSTEM SECURE: Caught exception -> {type(e).__name__}: {e}")
        # print(traceback.format_exc())
        print()

def attack_malformed_payload():
    print("Payload: initial_amplitudes='NOT_A_DICT'")
    IntegrationChainHarness.run_deterministic_chain(
        initial_amplitudes="NOT_A_DICT",
        evolution_matrix={},
        projectors={},
        seed=42
    )

def attack_missing_field():
    print("Payload: Missing projector field in arguments (passing None)")
    IntegrationChainHarness.run_deterministic_chain(
        initial_amplitudes={"0": 1.0},
        evolution_matrix={("0","0"): 1.0},
        projectors=None,
        seed=42
    )

def attack_type_mutation():
    print("Payload: initial_amplitudes has nested list instead of complex number")
    IntegrationChainHarness.run_deterministic_chain(
        initial_amplitudes={"0": [1.0, 0.0]},
        evolution_matrix={("0","0"): 1.0},
        projectors={},
        seed=42
    )

def attack_unknown_field():
    print("Payload: passing dictionary with unexpected internal types or keys")
    # Actually, python kwargs don't allow unknown fields if not defined, but we can pass unknown structural keys
    IntegrationChainHarness.run_deterministic_chain(
        initial_amplitudes={"0": 1.0, "UNKNOWN_META": "should_fail"},
        evolution_matrix={("0","0"): 1.0},
        projectors={},
        seed=42
    )

def attack_schema_downgrade():
    print("Payload: Replaying older schema version by passing lists instead of dicts (Cycle 1 vs Cycle 8)")
    IntegrationChainHarness.run_deterministic_chain(
        initial_amplitudes=[1.0, 0.0],
        evolution_matrix=[[1.0, 0.0], [0.0, 1.0]],
        projectors={},
        seed=42
    )

def attack_remove_required_fields():
    print("Payload: Dict missing required ('0','0') tuple structure in matrix")
    IntegrationChainHarness.run_deterministic_chain(
        initial_amplitudes={"0": 1.0},
        evolution_matrix={"0": 1.0}, # Missing tuple structure
        projectors={},
        seed=42
    )

if __name__ == "__main__":
    print("--- CONTRACT MISMATCH INJECTION ---")
    log_attack("Malformed Payload Injection", attack_malformed_payload)
    log_attack("Missing-Field Injection", attack_missing_field)
    log_attack("Type Mutation Injection", attack_type_mutation)
    log_attack("Unknown-Field Injection", attack_unknown_field)
    
    print("--- SCHEMA DOWNGRADE & VERSION ATTACK ---")
    log_attack("Replay Older Schema Versions", attack_schema_downgrade)
    log_attack("Remove Required Fields (tuple indices)", attack_remove_required_fields)
