"""
Cycle 4 Invariants — Quantum Error Bounds
=========================================

E1: Unrecoverable Information Bounds
E2: No Free Restoration
E3: Error Propagation Monotonicity
E4: Compensation Traceability
"""

from dataclasses import dataclass
from typing import List

from cycle2.collapse_engine import CollapseEngine
from cycle3.timeline import CausalTimeline, CausalEvent
from cycle4.error_model import ErrorModel


@dataclass
class InvariantResult:
    passed: List[str]
    failed: List[str]


class InvariantViolationError(Exception):
    """Raised when a formal architectural error invariant is violated."""
    pass


def check_unrecoverable_bounds(error_model: ErrorModel, collapse_engine: CollapseEngine) -> None:
    """
    E1: Unrecoverable Information Bounds
    The error model's unrecoverable loss must be >= the total information 
    declared lost by the collapse engine. We cannot "forget" about lost info.
    """
    actual_lost = collapse_engine.total_information_lost
    tracked_loss = error_model.total_unrecoverable_loss

    if tracked_loss < actual_lost:
        raise InvariantViolationError(
            f"E1 Violation: Tracked loss ({tracked_loss}) is less than actual declared loss ({actual_lost}). "
            "Information destruction cannot be reversed."
        )


def check_no_free_restoration(events: List[CausalEvent]) -> None:
    """
    E2: No Free Restoration
    If an event attempts to decrease the total entropy/decoherence of the system,
    it MUST be an explicit 'SYNDROME_MEASUREMENT' or 'CORRECTION' event using an ancilla.
    Free restoration (magic cooling) is physically impossible.
    
    In our architecture, this means no event can declare a negative information loss.
    """
    for ev in events:
        if ev.event_type == "COLLAPSE":
            res = ev.payload.result
            if getattr(res, "information_loss_declared", 0) < 0:
                raise InvariantViolationError(
                    f"E2 Violation: Event ID {ev.causal_id} declared negative information loss. "
                    "Information cannot be freely created out of a collapse."
                )


def check_error_propagation_monotonicity(error_model: ErrorModel, post_loss: float) -> None:
    """
    E3: Error Propagation Monotonicity
    Without active error correction, the total unrecoverable loss must monotonically increase.
    """
    if post_loss < error_model.total_unrecoverable_loss:
        raise InvariantViolationError(
            f"E3 Violation: New loss ({post_loss}) is strictly less than previous loss "
            f"({error_model.total_unrecoverable_loss}) without an explicit correction event."
        )


def check_compensation_traceability(timeline: CausalTimeline) -> None:
    """
    E4: Compensation Traceability
    Every correction/compensation must leave an audit trail back to the event it compensates.
    This was largely proven in Cycle 3 (CausalTimeline), but E4 requires that 
    ANY operation tagging itself as 'CORRECTION' must have is_compensation=True in the timeline.
    """
    for ev in timeline.events:
        if ev.event_type == "CORRECTION":
            if not ev.is_compensation:
                raise InvariantViolationError(
                    f"E4 Violation: Event ID {ev.causal_id} is marked as 'CORRECTION' "
                    "but is not a formal timeline compensation. Silent correction is forbidden."
                )


def run_all_error_invariants(
    error_model: ErrorModel, 
    collapse_engine: CollapseEngine, 
    timeline: CausalTimeline
) -> InvariantResult:
    """Runs E1-E4 and returns the result."""
    passed = []
    failed = []

    # E1
    try:
        check_unrecoverable_bounds(error_model, collapse_engine)
        passed.append("E1_UNRECOVERABLE_BOUNDS")
    except Exception as e:
        failed.append(f"E1_UNRECOVERABLE_BOUNDS: {e}")

    # E2
    try:
        check_no_free_restoration(timeline.events)
        passed.append("E2_NO_FREE_RESTORATION")
    except Exception as e:
        failed.append(f"E2_NO_FREE_RESTORATION: {e}")

    # E3 (Not run explicitly in batch, it's a runtime check on state transition)

    # E4
    try:
        check_compensation_traceability(timeline)
        passed.append("E4_COMPENSATION_TRACEABILITY")
    except Exception as e:
        failed.append(f"E4_COMPENSATION_TRACEABILITY: {e}")

    return InvariantResult(passed=passed, failed=failed)
