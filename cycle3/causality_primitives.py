"""
Cycle 3 — Causality Primitives
================================

Defines the atomic types for the time and causality layer:
  - LogicalClock: strictly monotonically increasing counter
  - CausalEvent: a single point in causal history with predecessor linkage
  - CausalLink: the directed causal edge between two events
  - PointOfNoReturn: a sealed marker that blocks future compensations

Design principles:
  • Events have strict causal order (no simultaneous writes)
  • No event can claim a timestamp before a prior committed event
  • Causality chains are immutable (frozen dataclasses)
  • The PointOfNoReturn is a permanent architectural seal

Quantum alignment:
  • Causality in quantum systems is absolute: measurement outcomes cannot
    propagate backwards in time (quantum no-signaling theorem)
  • Time ordering of events is the classical shadow of unitary evolution order
  • Rollback violates causality because it would require 'un-causing' an event
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Logical Clock
# ---------------------------------------------------------------------------

class LogicalClock:
    """
    A strictly monotonically increasing logical clock.

    This is a Lamport-style logical clock. It does NOT represent wall time.
    It represents causal ordering within a single CausalTimeline.

    Properties:
      - tick() increments by exactly 1
      - peek() reads the current value without advancing
      - The clock value NEVER decreases
      - No external actor can set the clock backwards
    """

    def __init__(self, start: int = 0) -> None:
        if start < 0:
            raise ValueError("LogicalClock start must be >= 0")
        self._value: int = start

    def tick(self) -> int:
        """Advance the clock and return the NEW value."""
        self._value += 1
        return self._value

    def peek(self) -> int:
        """Return the current clock value without advancing."""
        return self._value

    def __repr__(self) -> str:
        return f"LogicalClock(t={self._value})"


# ---------------------------------------------------------------------------
# Causal Event
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CausalEvent:
    """
    A single, immutable point in causal history.

    Every event in the system — whether a state delta (Cycle 1) or a collapse
    event (Cycle 2) — is wrapped in a CausalEvent to anchor it in the timeline.

    Fields:
      causal_id        — unique identifier (logical clock value)
      event_type       — string tag: "STATE_DELTA", "COLLAPSE", "COMPENSATION", etc.
      payload          — arbitrary frozen data (the actual event record)
      predecessor_id   — causal_id of the immediately preceding event (None for genesis)
      wall_time_ns     — physical wall-clock time at creation
      is_compensation  — True if this event compensates a prior one (never undoes it)
    """
    causal_id: int
    event_type: str
    payload: object           # any frozen/hashable object
    predecessor_id: Optional[int]
    wall_time_ns: int
    is_compensation: bool = False

    def __post_init__(self) -> None:
        if self.causal_id < 0:
            raise ValueError("causal_id must be >= 0")
        if not self.event_type:
            raise ValueError("event_type must be non-empty")
        if self.predecessor_id is not None and self.predecessor_id >= self.causal_id:
            raise ValueError(
                f"predecessor_id ({self.predecessor_id}) must be < causal_id ({self.causal_id}). "
                "Causality violation: an event cannot precede itself or its successors."
            )


# ---------------------------------------------------------------------------
# Causal Link
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CausalLink:
    """
    A directed causal edge: cause → effect.

    A CausalLink asserts that event `cause_id` is the direct cause of
    event `effect_id`. The link is immutable and cannot be deleted.

    Optional metadata describes WHAT mechanism caused the effect.
    """
    cause_id: int
    effect_id: int
    mechanism: str = ""       # e.g. "OBSERVATION", "COLLAPSE", "COMPENSATION"

    def __post_init__(self) -> None:
        if self.cause_id >= self.effect_id:
            raise ValueError(
                f"CausalLink: cause_id ({self.cause_id}) must be < effect_id ({self.effect_id}). "
                "Cause must precede effect."
            )


# ---------------------------------------------------------------------------
# Point of No Return
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PointOfNoReturn:
    """
    A permanent architectural seal placed at a specific causal_id.

    Once a PointOfNoReturn is registered:
    - No further events can be added BEFORE this causal_id
    - No compensation for events AT or BEFORE this id is allowed
    - The event at this id and all prior events are permanently sealed

    This models the physical irreversibility of certain quantum events —
    once a photon has been absorbed, there is no 'undo'.
    """
    sealed_at_causal_id: int
    reason: str               # Human-readable justification
    wall_time_ns: int

    def __post_init__(self) -> None:
        if self.sealed_at_causal_id < 0:
            raise ValueError("sealed_at_causal_id must be >= 0")
        if not self.reason:
            raise ValueError("PointOfNoReturn.reason must be non-empty")
