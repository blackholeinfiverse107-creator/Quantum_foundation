"""
Integration Demo — Sovereign Quantum Architecture Primitives
============================================================

This script demonstrates all three cycles working together:

  Cycle 1: State evolves under observations without execution
  Cycle 2: State is measured, information loss is declared
  Cycle 3: All events are recorded in the causal timeline

Run:
  python integration_demo.py

Expected: all invariants pass, timeline printed, no exceptions raised.
"""

import math
import sys
import io

# Force UTF-8 encoding for Windows console to support the |⟩ ket symbol.
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Make sure root is on path
import os
sys.path.insert(0, os.path.dirname(__file__))

from cycle1.state_evolution_engine import (
    Observation, StateVector, identity_rule, phase_rotation_rule, dampened_amplitude_rule
)
from cycle2.measurement_policy import ProjectiveMeasurementPolicy, WeakMeasurementPolicy
from cycle3.integration import QuantumFoundationSystem


DIVIDER = "=" * 64


def make_qubit(prob_zero: float = 0.5) -> StateVector:
    """Return a qubit with P(|0>) = prob_zero."""
    amp0 = math.sqrt(prob_zero)
    amp1 = math.sqrt(1.0 - prob_zero)
    return StateVector({"0": complex(amp0), "1": complex(amp1)})


def section(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def main() -> None:
    print(DIVIDER)
    print("  SOVEREIGN QUANTUM ARCHITECTURE PRIMITIVES")
    print("  Integration Demo — All Three Cycles")
    print(DIVIDER)

    # ----------------------------------------------------------
    # SETUP: Create the unified system
    # ----------------------------------------------------------
    section("SETUP: QuantumFoundationSystem")

    initial = make_qubit(prob_zero=0.5)  # |+> state: 50/50 superposition
    system = QuantumFoundationSystem(initial, name="demo-system")

    # Register Cycle 1 transition rules
    system.register_transition_rule(
        "phase_rotation", phase_rotation_rule,
        "Apply a phase rotation to all amplitudes"
    )
    system.register_transition_rule(
        "dampen", dampened_amplitude_rule,
        "Dampen a specific basis amplitude and renormalize"
    )
    system.register_transition_rule(
        "identity", identity_rule,
        "No-op — state unchanged"
    )

    # Register Cycle 2 measurement policies
    system.register_measurement_policy(ProjectiveMeasurementPolicy())
    system.register_measurement_policy(WeakMeasurementPolicy(coupling_strength=0.4))

    print(f"Initial state: {system.current_state}")
    print(f"Timeline: {system.timeline}")

    # ----------------------------------------------------------
    # CYCLE 1: State Evolution
    # ----------------------------------------------------------
    section("CYCLE 1: State Evolution Under Observations")

    obs1 = Observation("phase_rotation", (math.pi / 4,))
    delta1, ev1 = system.evolve(obs1)
    print(f"[obs: phase π/4]  → delta seq={delta1.sequence_number}, causal_id={ev1.causal_id}")
    print(f"  New state: {system.current_state}")

    obs2 = Observation("dampen", ("1", 0.7))
    delta2, ev2 = system.evolve(obs2)
    print(f"[obs: dampen |1>]  → delta seq={delta2.sequence_number}, causal_id={ev2.causal_id}")
    print(f"  New state: {system.current_state}")

    obs3 = Observation("phase_rotation", (math.pi / 2,))
    delta3, ev3 = system.evolve(obs3)
    print(f"[obs: phase π/2]  → delta seq={delta3.sequence_number}, causal_id={ev3.causal_id}")
    print(f"  New state: {system.current_state}")

    # ----------------------------------------------------------
    # CYCLE 1: Deterministic Replay
    # ----------------------------------------------------------
    section("CYCLE 1: Deterministic Replay Verification")

    integrity_ok = system.state_engine.verify_replay_integrity()
    print(f"Replay integrity: {'PASS ✓' if integrity_ok else 'FAIL ✗'}")

    # ----------------------------------------------------------
    # CYCLE 2: Measurement
    # ----------------------------------------------------------
    section("CYCLE 2: Deterministic Measurement & Collapse")

    token_a = system.issue_collapse_token("ProjectiveMeasurement", "demo-tok-projective")
    collapse_ev_a, causal_ev_a = system.measure(token_a, seed=42)
    r = collapse_ev_a.result
    print(f"[Projective, seed=42]")
    print(f"  Outcome:        |{r.outcome}⟩")
    print(f"  Confidence:     {r.confidence:.4f}  (Born rule probability)")
    print(f"  Info loss:      {r.information_loss_declared:.4f} bits")
    print(f"  Post state:     {r.post_state}")
    print(f"  Causal ID:      {causal_ev_a.causal_id}")

    # Second measurement — same seed and same state (the pre-collapse state) → same outcome
    token_b = system.issue_collapse_token("ProjectiveMeasurement", "demo-tok-replay")
    policy = ProjectiveMeasurementPolicy()
    replayed = policy.measure(collapse_ev_a.pre_collapse_state, seed=42)
    print(f"\n[Replay verification: same seed, same pre-state]")
    print(f"  Replay outcome: |{replayed.outcome}⟩  {'== original ✓' if replayed.outcome == r.outcome else '≠ original ✗'}")

    # Weak measurement
    token_c = system.issue_collapse_token(
        f"WeakMeasurement(α=0.40)", "demo-tok-weak"
    )
    collapse_ev_c, causal_ev_c = system.measure(token_c, seed=77)
    rw = collapse_ev_c.result
    print(f"\n[Weak, α=0.4, seed=77]")
    print(f"  Outcome:        |{rw.outcome}⟩")
    print(f"  Info loss:      {rw.information_loss_declared:.4f} bits  (< projective loss)")
    print(f"  Total info lost so far: {system.collapse_engine.total_information_lost:.4f} bits")

    # ----------------------------------------------------------
    # CYCLE 3: Causal Timeline
    # ----------------------------------------------------------
    section("CYCLE 3: Causal Timeline")

    print(f"Timeline length: {system.timeline.length} events")
    print(f"Events recorded:")
    for ev in system.timeline.events:
        comp_tag = " [COMPENSATION]" if ev.is_compensation else ""
        print(f"  [{ev.causal_id:3d}] {ev.event_type}{comp_tag}")

    print(f"\n[Verify causal ordering]")
    ordered = system.timeline.verify_ordering()
    print(f"  Ordering: {'PASS ✓' if ordered else 'FAIL ✗'}")

    # Seal the timeline at current head
    system.seal_timeline("Demo end-of-session seal")
    print(f"\n[PointOfNoReturn placed at id={system.timeline.sealed_up_to}]")
    print(f"  Sealed events are permanently non-compensable")

    # ----------------------------------------------------------
    # ALL INVARIANTS CHECK
    # ----------------------------------------------------------
    section("FULL INVARIANT SUITE")

    report = system.verify_all_invariants()
    all_ok = True
    for cycle_name, results in report.items():
        status = "PASS ✓" if not results["failed"] else "FAIL ✗"
        print(f"  {cycle_name.upper()}: {status}  ({len(results['passed'])} passed, {len(results['failed'])} failed)")
        if results["failed"]:
            all_ok = False
            for fail in results["failed"]:
                print(f"    ✗ {fail}")

    print()
    print(DIVIDER)
    if all_ok:
        print("  ✓ ALL INVARIANTS PASS — SYSTEM IS COHERENT")
    else:
        print("  ✗ INVARIANT FAILURES DETECTED")
    print(DIVIDER)

    return 0 if all_ok else 1


if __name__ == "__main__":
    result = main()
    sys.exit(result)
