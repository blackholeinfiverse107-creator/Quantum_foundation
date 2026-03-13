"""
Cycle 5 Invariants — Quantum No-Go Bounds
=========================================

NG1: No-Cloning Bound
NG2: No-Deleting Bound
NG3: Confidence Collapse Bound
"""

from typing import List
from dataclasses import dataclass

from cycle2.collapse_engine import CollapseEngine
from cycle3.timeline import CausalTimeline, CausalEvent
from cycle4.invariants import InvariantResult, InvariantViolationError
from cycle5.nogo_primitives import (
    NoCloningViolation,
    NoDeletingViolation,
    ConfidenceCollapseViolation
)

@dataclass
class NoGoInvariantResult:
    passed: List[str]
    failed: List[str]


def check_linear_timeline(timeline: CausalTimeline) -> None:
    """
    NG1: No-Cloning Bound
    The timeline must be a strictly linear sequence with no branched event IDs.
    Parallel states derived from the same root would cause ID collisions or 
    non-monotonic jumps.
    """
    expected_id = 1
    for ev in timeline.events:
        if ev.causal_id != expected_id:
            raise NoCloningViolation(
                f"NG1 Violation: Causal history branching detected! "
                f"Expected event {expected_id} but found {ev.causal_id}. "
                "State cloning or parallel evaluation of unentangled references occurred."
            )
        expected_id += 1


def check_no_unlogged_deletions(timeline: CausalTimeline) -> None:
    """
    NG2: No-Deleting Bound
    States cannot be silently removed. A timeline is an append-only log. 
    Removing an event implies destroying its physical consequences.
    This was enforced in Cycle 3 mechanically, but NG2 elevates it to a 
    verifiable No-Go bound.
    """
    if len(timeline.events) < timeline.length:
        raise NoDeletingViolation("NG2 Violation: The timeline length metadata is greater than the actual event list. History was deleted.")
        
    for i, ev in enumerate(timeline.events):
        if ev is None:
            raise NoDeletingViolation(f"NG2 Violation: Event index {i} is null. History was erased.")


def check_confidence_disturbance_tradeoff(events: List[CausalEvent]) -> None:
    """
    NG3: Confidence Collapse Bound
    If a collapse event grants confidence > 0.0, it MUST declare information_loss > 0.0.
    A state cannot be "read" perfectly without disturbing its purity.
    """
    for ev in events:
        if ev.event_type == "STRICT_COLLAPSE":
            res = ev.payload.result
            conf = res.confidence
            loss = getattr(res, "information_loss_declared", 0.0)
            
            if conf > 0.0 and loss == 0.0:
                raise ConfidenceCollapseViolation(
                    f"NG3 Violation: Event {ev.causal_id} acquired {conf*100}% confidence "
                    "with zero information loss. Hidden measurement bypass detected."
                )


def run_all_nogo_invariants(timeline: CausalTimeline) -> NoGoInvariantResult:
    """Runs NG1-NG3 and returns the result."""
    passed = []
    failed = []

    # NG1
    try:
        check_linear_timeline(timeline)
        passed.append("NG1_NO_CLONING_BOUND")
    except Exception as e:
        failed.append(f"NG1_NO_CLONING_BOUND: {e}")

    # NG2
    try:
        check_no_unlogged_deletions(timeline)
        passed.append("NG2_NO_DELETING_BOUND")
    except Exception as e:
        failed.append(f"NG2_NO_DELETING_BOUND: {e}")

    # NG3
    try:
        check_confidence_disturbance_tradeoff(timeline.events)
        passed.append("NG3_CONFIDENCE_COLLAPSE_BOUND")
    except Exception as e:
        failed.append(f"NG3_CONFIDENCE_COLLAPSE_BOUND: {e}")

    return NoGoInvariantResult(passed=passed, failed=failed)
