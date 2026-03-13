"""
Cycle 2 — Measurement Invariants
==================================

Formally defines and enforces the invariants of the measurement and collapse
framework. Machine-checkable at runtime and in tests.

Invariant classification (follows Cycle 1 pattern):
  M1  Probability normalization — Born-rule probabilities sum to 1
  M2  Declared information loss is non-negative
  M3  Collapse event log is append-only (event IDs strictly increasing)
  M4  Repeat measurement convergence (idempotent post-collapse)
  M5  Deterministic replay — same state + seed → same outcome
  M6  Confidence ∈ [0, 1] for every MeasurementResult
  M7  Post-collapse norm conservation (collapsed state is unit vector)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cycle1.state_evolution_engine import StateVector
from cycle2.collapse_engine import CollapseEngine, IrreversibleCollapseEvent
from cycle2.measurement_policy import MeasurementPolicy, MeasurementResult


class MeasurementInvariantError(Exception):
    pass


# ---------------------------------------------------------------------------
# M1: Probability Normalization
# ---------------------------------------------------------------------------

def check_probability_normalization(state: StateVector, tolerance: float = 1e-10) -> None:
    """Born rule: sum of |amplitude|² must equal 1."""
    total = sum(a.probability() for a in state.amplitudes)
    if abs(total - 1.0) > tolerance:
        raise MeasurementInvariantError(
            f"M1 VIOLATED: Probability sum = {total:.12f}, expected 1.0"
        )


# ---------------------------------------------------------------------------
# M2: Non-Negative Information Loss
# ---------------------------------------------------------------------------

def check_information_loss_nonnegative(result: MeasurementResult) -> None:
    """Information loss must be ≥ 0. Negative loss would mean measurement created information."""
    if result.information_loss_declared < -1e-10:
        raise MeasurementInvariantError(
            f"M2 VIOLATED: information_loss_declared = {result.information_loss_declared:.8f}. "
            "Measurement cannot create information."
        )


# ---------------------------------------------------------------------------
# M3: Collapse Log Monotonicity
# ---------------------------------------------------------------------------

def check_collapse_log_monotonicity(
    events: Tuple[IrreversibleCollapseEvent, ...]
) -> None:
    """Event IDs in the collapse log must be strictly increasing."""
    for i in range(1, len(events)):
        prev = events[i - 1].event_id
        curr = events[i].event_id
        if curr <= prev:
            raise MeasurementInvariantError(
                f"M3 VIOLATED: event_id must be strictly increasing. "
                f"events[{i-1}].id={prev}, events[{i}].id={curr}"
            )


# ---------------------------------------------------------------------------
# M4: Repeat Measurement Convergence
# ---------------------------------------------------------------------------

def check_repeat_measurement_idempotent(
    policy: MeasurementPolicy,
    post_collapse_state: StateVector,
    seed: int,
    rounds: int = 5,
) -> None:
    """
    Measuring a post-collapse (pure eigenstate) state must always return
    the same outcome, regardless of the seed.

    This models the quantum property: once collapsed, a state stays collapsed.
    """
    first_result = policy.measure(post_collapse_state, seed)
    first_outcome = first_result.outcome

    for i in range(1, rounds):
        result = policy.measure(post_collapse_state, seed + i * 100)
        if result.outcome != first_outcome:
            raise MeasurementInvariantError(
                f"M4 VIOLATED: Repeat measurement returned different outcome. "
                f"First='{first_outcome}', round {i}='{result.outcome}'. "
                "Post-collapse state must be stable under repeated measurement."
            )


# ---------------------------------------------------------------------------
# M5: Deterministic Replay
# ---------------------------------------------------------------------------

def check_collapse_replay_determinism(engine: CollapseEngine) -> None:
    """Replaying all collapse events must reproduce the same outcomes."""
    try:
        engine.verify_collapse_integrity()
    except AssertionError as e:
        raise MeasurementInvariantError(f"M5 VIOLATED: {e}") from e


# ---------------------------------------------------------------------------
# M6: Confidence Bounds
# ---------------------------------------------------------------------------

def check_confidence_bounds(result: MeasurementResult) -> None:
    """Confidence (probability of outcome) must lie in [0, 1]."""
    if not (-1e-10 <= result.confidence <= 1.0 + 1e-10):
        raise MeasurementInvariantError(
            f"M6 VIOLATED: confidence = {result.confidence:.8f}, must be in [0, 1]"
        )


# ---------------------------------------------------------------------------
# M7: Post-Collapse Norm Conservation
# ---------------------------------------------------------------------------

def check_post_collapse_norm(result: MeasurementResult, tolerance: float = 1e-10) -> None:
    """Post-collapse state must still be a unit vector."""
    check_probability_normalization(result.post_state, tolerance)


# ---------------------------------------------------------------------------
# Composite Invariant Run
# ---------------------------------------------------------------------------

@dataclass
class MeasurementInvariantReport:
    passed: List[str]
    failed: List[str]


def run_all_measurement_invariants(
    engine: CollapseEngine,
    policy: MeasurementPolicy,
) -> MeasurementInvariantReport:
    """Run the full Cycle 2 invariant suite."""
    report = MeasurementInvariantReport(passed=[], failed=[])
    events = engine.collapse_log

    checks = [
        ("M3_COLLAPSE_LOG_MONOTONICITY",
         lambda: check_collapse_log_monotonicity(events)),
        ("M5_COLLAPSE_REPLAY_DETERMINISM",
         lambda: check_collapse_replay_determinism(engine)),
    ]

    # Per-event checks
    for i, event in enumerate(events):
        result = event.result
        checks.extend([
            (f"M2_INFO_LOSS_NONNEG[event={i}]",
             lambda r=result: check_information_loss_nonnegative(r)),
            (f"M6_CONFIDENCE_BOUNDS[event={i}]",
             lambda r=result: check_confidence_bounds(r)),
            (f"M7_POST_COLLAPSE_NORM[event={i}]",
             lambda r=result: check_post_collapse_norm(r)),
            (f"M1_PRE_COLLAPSE_NORM[event={i}]",
             lambda s=event.pre_collapse_state: check_probability_normalization(s)),
        ])

    for name, check in checks:
        try:
            check()
            report.passed.append(name)
        except MeasurementInvariantError as e:
            report.failed.append(f"{name}: {e}")

    return report
