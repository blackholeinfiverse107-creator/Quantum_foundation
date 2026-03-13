"""
Cycle 1 — Formal Invariants
============================

This module defines and enforces the invariants of the Sovereign State
Evolution Engine. Each invariant is expressed as a callable check function
that raises InvariantViolationError on failure.

Invariant classification:
  FORBIDDEN STATES   — configurations that must never exist
  IMPOSSIBLE TRANSITIONS — edges in the state graph that must never fire
  GUARANTEES         — properties that must always hold
  NON-GUARANTEES     — properties that are explicitly NOT promised

These invariants are LOGICAL proofs, not mathematical. They are expressed
in code so they can be automatically checked during testing and at runtime.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

from cycle1.state_evolution_engine import (
    StateDelta,
    StateVector,
    SovereignStateEngine,
)


class InvariantViolationError(Exception):
    """Raised when a formal invariant is found to be violated."""
    pass


# ---------------------------------------------------------------------------
# INVARIANT 1: Norm Conservation
# ---------------------------------------------------------------------------

def check_norm_conservation(state: StateVector, tolerance: float = 1e-10) -> None:
    """
    GUARANTEE: Every StateVector must lie on the unit sphere.
    Sum of |amplitude|² must equal 1.0.

    Quantum alignment: This is the Born rule pre-condition. A non-unit state
    yields probabilities that do not sum to 1, making measurement undefined.
    """
    norm_sq = sum(a.probability() for a in state.amplitudes)
    if abs(norm_sq - 1.0) > tolerance:
        raise InvariantViolationError(
            f"NORM CONSERVATION VIOLATED: ‖ψ‖² = {norm_sq:.12f}, expected 1.0. "
            f"Deviation: {abs(norm_sq - 1.0):.2e}"
        )


# ---------------------------------------------------------------------------
# INVARIANT 2: No Zero-Vector State
# ---------------------------------------------------------------------------

def check_no_zero_state(state: StateVector) -> None:
    """
    FORBIDDEN STATE: The zero vector must never appear as a quantum state.

    The zero vector has no physical interpretation as a quantum state —
    it represents the absence of probability amplitude everywhere.
    """
    all_zero = all(abs(a.value) < 1e-15 for a in state.amplitudes)
    if all_zero:
        raise InvariantViolationError(
            "FORBIDDEN STATE: Zero vector detected. "
            "The zero vector cannot represent a physical quantum state."
        )


# ---------------------------------------------------------------------------
# INVARIANT 3: History Immutability
# ---------------------------------------------------------------------------

def check_history_immutability(
    log: Tuple[StateDelta, ...],
    known_checksums: List[int],
) -> None:
    """
    GUARANTEE: The delta log must never be retroactively modified.

    We verify this by re-computing hash checksums of each delta entry
    and comparing against stored checksums.

    known_checksums must have been computed at the time of original logging.
    """
    if len(log) != len(known_checksums):
        raise InvariantViolationError(
            f"HISTORY IMMUTABILITY VIOLATED: Log length changed from "
            f"{len(known_checksums)} to {len(log)}."
        )
    for i, (delta, expected_checksum) in enumerate(zip(log, known_checksums)):
        actual = hash(delta)
        if actual != expected_checksum:
            raise InvariantViolationError(
                f"HISTORY IMMUTABILITY VIOLATED at delta #{i} "
                f"(seq={delta.sequence_number}). "
                f"Expected checksum {expected_checksum}, got {actual}. "
                "This indicates retroactive mutation."
            )


# ---------------------------------------------------------------------------
# INVARIANT 4: Strictly Increasing Sequence Numbers
# ---------------------------------------------------------------------------

def check_sequence_monotonicity(log: Tuple[StateDelta, ...]) -> None:
    """
    IMPOSSIBLE TRANSITION: Sequence numbers must be strictly monotonically
    increasing across the delta log.

    Violation would indicate either:
      - A deleted entry (gap)
      - A replayed or duplicated entry
      - A forged entry injected out of order
    """
    for i in range(1, len(log)):
        prev = log[i - 1].sequence_number
        curr = log[i].sequence_number
        if curr != prev + 1:
            raise InvariantViolationError(
                f"SEQUENCE MONOTONICITY VIOLATED: "
                f"delta[{i-1}].seq={prev}, delta[{i}].seq={curr}. "
                "Expected strictly increasing by 1."
            )


# ---------------------------------------------------------------------------
# INVARIANT 5: Delta Continuity (prior → next chaining)
# ---------------------------------------------------------------------------

def check_delta_continuity(log: Tuple[StateDelta, ...]) -> None:
    """
    GUARANTEE: The next_state of delta[i] must equal the prior_state of delta[i+1].

    This ensures the log describes a single, continuous trajectory through
    state space. Any gap indicates a hidden state mutation.
    """
    for i in range(1, len(log)):
        prev_next = log[i - 1].next_state
        curr_prior = log[i].prior_state
        if prev_next != curr_prior:
            raise InvariantViolationError(
                f"DELTA CONTINUITY VIOLATED between delta[{i-1}] and delta[{i}]. "
                f"next_state of delta[{i-1}] does not match prior_state of delta[{i}]. "
                "Hidden state mutation suspected."
            )


# ---------------------------------------------------------------------------
# INVARIANT 6: Dimension Preservation
# ---------------------------------------------------------------------------

def check_dimension_preservation(log: Tuple[StateDelta, ...]) -> None:
    """
    IMPOSSIBLE TRANSITION: The Hilbert space dimension (number of basis states)
    must not change mid-evolution.

    Quantum alignment: The Hilbert space is fixed at system definition time.
    Spontaneous dimension change would imply an undefined interaction.
    """
    if not log:
        return
    initial_dim = log[0].prior_state.dimension
    for i, delta in enumerate(log):
        for label, state in [("prior", delta.prior_state), ("next", delta.next_state)]:
            if state.dimension != initial_dim:
                raise InvariantViolationError(
                    f"DIMENSION PRESERVATION VIOLATED at delta[{i}].{label}_state: "
                    f"got dimension {state.dimension}, expected {initial_dim}."
                )


# ---------------------------------------------------------------------------
# INVARIANT 7: Replay Determinism
# ---------------------------------------------------------------------------

def check_replay_determinism(engine: SovereignStateEngine) -> None:
    """
    GUARANTEE: Replaying the full delta log from the initial state must
    produce the current state exactly.

    This is the core determinism guarantee of the engine.
    """
    try:
        engine.verify_replay_integrity()
    except AssertionError as e:
        raise InvariantViolationError(f"REPLAY DETERMINISM VIOLATED: {e}") from e


# ---------------------------------------------------------------------------
# NON-GUARANTEES (documented explicitly)
# ---------------------------------------------------------------------------

NON_GUARANTEES = """
NON-GUARANTEES (explicitly declared):
======================================

1. The engine does NOT guarantee that two different observation sequences
   produce different final states. Convergence of distinct paths is allowed.

2. The engine does NOT guarantee real-time ordering between concurrent
   engine instances. Distributed ordering requires Cycle 3 (CausalTimeline).

3. The engine does NOT guarantee that the payload of an Observation is
   semantically valid — only that it is structurally a tuple. Semantic
   validation is the caller's responsibility via TransitionRule.

4. The engine does NOT guarantee loss-less measurement. That guarantee
   belongs to Cycle 2 (CollapseEngine).

5. The engine does NOT prevent valid (norm-preserving) transitions that
   may have physical uninterpretability. Physical constraint enforcement
   is a higher-level concern.
"""


# ---------------------------------------------------------------------------
# Composite Invariant Check (run all)
# ---------------------------------------------------------------------------

@dataclass
class InvariantReport:
    passed: List[str]
    failed: List[str]


def run_all_invariants(engine: SovereignStateEngine) -> InvariantReport:
    """
    Run the full invariant suite against an engine instance.
    Returns an InvariantReport with passed and failed invariant names.
    """
    log = engine.delta_log
    report = InvariantReport(passed=[], failed=[])

    checks = [
        ("NORM_CONSERVATION",
         lambda: check_norm_conservation(engine.current_state)),
        ("NO_ZERO_STATE",
         lambda: check_no_zero_state(engine.current_state)),
        ("SEQUENCE_MONOTONICITY",
         lambda: check_sequence_monotonicity(log)),
        ("DELTA_CONTINUITY",
         lambda: check_delta_continuity(log)),
        ("DIMENSION_PRESERVATION",
         lambda: check_dimension_preservation(log)),
        ("REPLAY_DETERMINISM",
         lambda: check_replay_determinism(engine)),
    ]

    for name, check in checks:
        try:
            check()
            report.passed.append(name)
        except InvariantViolationError as e:
            report.failed.append(f"{name}: {e}")

    return report
