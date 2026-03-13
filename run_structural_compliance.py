import sys
import os
import hashlib

sys.path.insert(0, os.path.dirname(__file__))

from cycle1.state_evolution_engine import StateVector, Observation, phase_rotation_rule
from cycle2.measurement_policy import ProjectiveMeasurementPolicy
from cycle3.integration import QuantumFoundationSystem

def run_chain(seed: int) -> str:
    # Initialize Core System
    init_state = StateVector({"0": 1.0, "1": 0.0})
    sys_instance = QuantumFoundationSystem(init_state)
    
    # Register Rules
    sys_instance.register_transition_rule("phase", phase_rotation_rule)
    sys_instance.register_measurement_policy(ProjectiveMeasurementPolicy())
    
    # 1. Evolution Event
    sys_instance.evolve(Observation("phase", (0.5,)))
    
    # 2. Measurement Event
    token = sys_instance.issue_collapse_token("ProjectiveMeasurement", "token_1")
    sys_instance.measure(token, seed)
    
    # 3. Governance Event
    sys_instance.seal_timeline("Compliance Verification Seal")
    
    # Hash the full causal timeline to ensure bit-level determinism
    timeline_hash = hashlib.sha256()
    for event in sys_instance.timeline.events:
        timeline_hash.update(str(event.causal_id).encode())
        timeline_hash.update(str(event.event_type).encode())
        timeline_hash.update(str(repr(event.payload)).encode())
    
    return timeline_hash.hexdigest()

def run_verification_harness(num_runs=100, target_seed=42):
    print(f"--- DETERMINISTIC REPLAY VERIFICATION HARNESS ---")
    print(f"Executing {num_runs} synchronous system chains with seed={target_seed}")
    
    hashes = []
    divergence_detected = False
    
    for i in range(num_runs):
        computed_hash = run_chain(target_seed)
        hashes.append(computed_hash)
        
        # Immediate comparison
        if i > 0 and hashes[i] != hashes[i-1]:
            print(f"[!] DIVERGENCE DETECTED at Iteration {i}. Determinism broken.")
            divergence_detected = True
            break

    if not divergence_detected:
        print("[+] VERIFICATION PASSED. All runs generated identical timeline hashes.")
        print(f"[+] Final structural hash signature: {hashes[0]}")
    else:
        print("[-] VERIFICATION FAILED.")

if __name__ == "__main__":
    run_verification_harness()
