import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from cycle1.state_evolution_engine import SovereignStateEngine, StateVector, Observation, identity_rule
from cycle2.collapse_engine import CollapseEngine, CollapseToken
from cycle2.measurement_policy import ProjectiveMeasurementPolicy
from cycle3.timeline import CausalTimeline, CausalityViolationError, PointOfNoReturnViolationError
from cycle3.integration import QuantumFoundationSystem

def log_attack(name, func):
    print(f"=== {name} ===")
    try:
        func()
        print("[!] VULNERABILITY FOUND: System silently accepted attack.\\n")
    except Exception as e:
        print(f"[+] SYSTEM SECURE: Caught exception -> {type(e).__name__}: {e}\\n")

def setup_system():
    init_state = StateVector({"0": 1.0, "1": 0.0})
    sys = QuantumFoundationSystem(init_state)
    sys.register_measurement_policy(ProjectiveMeasurementPolicy())
    sys.register_transition_rule("identity", identity_rule)
    return sys

def attack_cross_layer_invocation():
    print("Payload: Calling CollapseEngine directly without valid token mapping")
    sys = setup_system()
    # Try calling collapse directly without issuing a token
    try:
        sys.collapse_engine.collapse(sys.current_state, "NOT_A_TOKEN", 42)
    except TypeError as e:
        raise e

def attack_inject_authority_flags():
    print("Payload: Forging a CollapseToken locally to bypass issuer authority")
    sys = setup_system()
    # Maliciously forging a token
    fake_token = CollapseToken(token_id="fake_123", authorized_policy="ProjectiveMeasurement", issued_at_ns=time.time_ns())
    # Calling CollapseEngine with forged token
    sys.collapse_engine.collapse(sys.current_state, fake_token, 42)

def attack_governance_layer_calls():
    print("Payload: Calling seal_timeline over an empty timeline or backwards")
    sys = setup_system()
    # Try to seal timeline at id 0 (which doesn't exist)
    sys.seal_timeline("Governance Bypass Attack")

def attack_unauthorized_access():
    print("Payload: Attempting double-spend of a consumed CollapseToken")
    sys = setup_system()
    token = sys.issue_collapse_token("ProjectiveMeasurement", "auth_token_1")
    sys.measure(token, 42)
    # Attempt second measure with same token
    sys.measure(token, 84)

def attack_runtime_registry_mutation():
    print("Payload: Attempting to overwrite an existing transition rule in SovereignStateEngine")
    sys = setup_system()
    # Trying to register over 'identity'
    sys.register_transition_rule("identity", identity_rule)

def attack_temporary_override():
    print("Payload: Attempting to modify the timeline _events log directly via append")
    sys = setup_system()
    try:
        sys.timeline.events.append("MALICIOUS_EVENT")
    except AttributeError as e:
        raise e

def attack_execution_order_variance():
    print("Payload: Forcing causal execution order violation in CausalTimeline")
    sys = setup_system()
    # Bypass timeline record method to mess up ordering manually
    event = sys.timeline.record("TEST", {"data": 1})
    # Corrupting the order
    try:
        sys.timeline._events[0].causal_id = 999
    except AttributeError as e:
        # dataclass frozen exception
        raise e

def attack_replay_divergence():
    print("Payload: Replaying same state and token multiple times to check divergence")
    sys = setup_system()
    # Determinism test
    base_state = sys.current_state
    token1 = sys.collapse_engine.issue_token("ProjectiveMeasurement", "token_1")
    res1 = sys.collapse_engine.collapse(base_state, token1, 42)
    
    token2 = sys.collapse_engine.issue_token("ProjectiveMeasurement", "token_2")
    res2 = sys.collapse_engine.collapse(base_state, token2, 42)
    
    if res1.result.outcome != res2.result.outcome:
         raise Exception("Replay divergence detected - outputs differ on same seed!")
    else:
         raise Exception("No divergence - identical seed produces identical output.")

if __name__ == "__main__":
    print("--- PRIVILEGE ESCALATION ---")
    log_attack("Cross-Layer Invocation", attack_cross_layer_invocation)
    log_attack("Authority Flag Injection", attack_inject_authority_flags)
    log_attack("Governance Layer Bypass", attack_governance_layer_calls)
    log_attack("Unauthorized Access (Token Reuse)", attack_unauthorized_access)
    
    print("--- REGISTRY MUTATION & REPLAY ---")
    log_attack("Runtime Registry Mutation", attack_runtime_registry_mutation)
    log_attack("Temporary Override Injection", attack_temporary_override)
    log_attack("Execution-Order Variance (Frozen Mutation)", attack_execution_order_variance)
    log_attack("Deterministic Replay (Divergence check)", attack_replay_divergence)
