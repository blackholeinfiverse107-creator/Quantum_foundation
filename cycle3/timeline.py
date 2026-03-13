"""
Cycle 3 — Causal Timeline
==========================

The CausalTimeline is the master append-only sequence of all CausalEvents
in the system. It enforces:
  • Strict monotonic ordering (no event before its predecessor)
  • No retroactive correction or deletion
  • Compensation-over-rollback: errors are corrected by ADDING new events
  • PointOfNoReturn enforcement: sealed regions cannot be compensated

Key architectural roles:
  - Records every state delta (Cycle 1) and every collapse event (Cycle 2)
    as CausalEvents, giving them a causal timestamp
  - Provides the causal ordering proof required for Cycle 3 coherence
  - Is the single source of truth for "what happened and in what order"
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Set, Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cycle3.causality_primitives import (
    CausalEvent,
    CausalLink,
    LogicalClock,
    PointOfNoReturn,
)


class CausalityViolationError(Exception):
    """Raised when an operation would violate causal ordering."""
    pass


class PointOfNoReturnViolationError(Exception):
    """Raised when an operation tries to modify a sealed causal region."""
    pass


class CausalTimeline:
    """
    The centralized, append-only causal history of the entire system.

    Usage:
      1. `record(event_type, payload)` — add a new event, returns CausalEvent
      2. `compensate(target_id, payload)` — add a compensation event for a prior event
      3. `seal(causal_id, reason)` — place a PointOfNoReturn
      4. `get_chain(causal_id)` — retrieve the full causal chain to an event
      5. `verify_ordering()` — validate the entire timeline for consistency

    Prohibitions:
      • No deletion of any event
      • No modification of recorded events
      • No compensation of sealed events
      • No event with causal_id ≤ previous event's causal_id
    """

    def __init__(self) -> None:
        self._clock: LogicalClock = LogicalClock(start=0)
        self._events: List[CausalEvent] = []
        self._links: List[CausalLink] = []
        self._ponr_markers: List[PointOfNoReturn] = []
        # Index for fast lookup
        self._event_index: Dict[int, CausalEvent] = {}
        self._sealed_up_to: int = -1   # all causal_ids <= this are sealed

    # --- Recording New Events ---

    def record(
        self,
        event_type: str,
        payload: object,
        is_compensation: bool = False,
    ) -> CausalEvent:
        """
        Append a new event to the timeline.

        Args:
            event_type: string tag identifying the type of event
            payload: the event data (should be immutable/frozen)
            is_compensation: True if this event compensates a prior one

        Returns:
            The newly created CausalEvent
        """
        causal_id = self._clock.tick()
        predecessor_id = causal_id - 1 if causal_id > 1 else None

        event = CausalEvent(
            causal_id=causal_id,
            event_type=event_type,
            payload=payload,
            predecessor_id=predecessor_id,
            wall_time_ns=time.time_ns(),
            is_compensation=is_compensation,
        )

        self._events.append(event)
        self._event_index[causal_id] = event

        # Auto-link to predecessor
        if predecessor_id is not None:
            link = CausalLink(
                cause_id=predecessor_id,
                effect_id=causal_id,
                mechanism=event_type,
            )
            self._links.append(link)

        return event

    # --- Compensation ---

    def compensate(
        self,
        target_causal_id: int,
        compensation_payload: object,
        reason: str = "",
    ) -> CausalEvent:
        """
        Add a compensation event for a prior event.

        Compensation is the ONLY sanctioned way to respond to an erroneous
        prior event. It does NOT undo the prior event — it appends a new
        event that corrects the downstream effects.

        Raises:
            PointOfNoReturnViolationError if target_causal_id is sealed
            CausalityViolationError if target does not exist
        """
        if target_causal_id not in self._event_index:
            raise CausalityViolationError(
                f"Cannot compensate: event with causal_id={target_causal_id} does not exist."
            )
        if target_causal_id <= self._sealed_up_to:
            raise PointOfNoReturnViolationError(
                f"Cannot compensate event {target_causal_id}: "
                f"it is sealed by a PointOfNoReturn (sealed_up_to={self._sealed_up_to}). "
                "No compensation is permitted past a PointOfNoReturn."
            )

        comp_event = self.record(
            event_type="COMPENSATION",
            payload=compensation_payload,
            is_compensation=True,
        )

        # Link the compensation to its target explicitly
        explicit_link = CausalLink(
            cause_id=target_causal_id,
            effect_id=comp_event.causal_id,
            mechanism=f"COMPENSATES:{reason or 'unspecified'}",
        )
        self._links.append(explicit_link)

        return comp_event

    # --- Point of No Return ---

    def seal(self, up_to_causal_id: int, reason: str) -> PointOfNoReturn:
        """
        Place a PointOfNoReturn sealing all events with causal_id ≤ up_to_causal_id.

        Once sealed:
        - No compensation for sealed events is allowed
        - The marker is permanently recorded

        Raises:
            ValueError if up_to_causal_id is less than current sealed boundary
        """
        if up_to_causal_id <= self._sealed_up_to:
            raise ValueError(
                f"Cannot seal up to {up_to_causal_id}: "
                f"already sealed up to {self._sealed_up_to}. "
                "PointOfNoReturn can only advance forwards."
            )
        if up_to_causal_id not in self._event_index:
            raise CausalityViolationError(
                f"Cannot seal: event {up_to_causal_id} does not exist in timeline."
            )

        ponr = PointOfNoReturn(
            sealed_at_causal_id=up_to_causal_id,
            reason=reason,
            wall_time_ns=time.time_ns(),
        )
        self._ponr_markers.append(ponr)
        self._sealed_up_to = up_to_causal_id
        return ponr

    # --- Chain Retrieval ---

    def get_chain(self, causal_id: int) -> Tuple[CausalEvent, ...]:
        """
        Return the full causal ancestor chain from genesis to causal_id.

        The chain follows predecessor_id links backwards and returns events
        in chronological order (genesis first, causal_id last).
        """
        if causal_id not in self._event_index:
            raise CausalityViolationError(
                f"Event {causal_id} does not exist in the timeline."
            )
        chain = []
        current = self._event_index[causal_id]
        while current is not None:
            chain.append(current)
            if current.predecessor_id is not None:
                current = self._event_index.get(current.predecessor_id)
            else:
                break
        chain.reverse()
        return tuple(chain)

    # --- Ordering Verification ---

    def verify_ordering(self) -> bool:
        """
        Verify the entire timeline for causal consistency:
        - Strictly increasing causal_ids
        - Each event's predecessor_id points to the immediately preceding event
        - Each epoch starts at 1 (after tick())

        Returns True if consistent. Raises CausalityViolationError on failure.
        """
        expected_id = 1
        for event in self._events:
            if event.causal_id != expected_id:
                raise CausalityViolationError(
                    f"ORDERING VIOLATION: expected causal_id={expected_id}, "
                    f"got {event.causal_id}. Gap or duplication detected."
                )
            if expected_id > 1 and event.predecessor_id != expected_id - 1:
                raise CausalityViolationError(
                    f"PREDECESSOR VIOLATION at causal_id={event.causal_id}: "
                    f"expected predecessor_id={expected_id - 1}, "
                    f"got {event.predecessor_id}."
                )
            expected_id += 1
        return True

    # --- Read-Only Properties ---

    @property
    def events(self) -> Tuple[CausalEvent, ...]:
        return tuple(self._events)

    @property
    def links(self) -> Tuple[CausalLink, ...]:
        return tuple(self._links)

    @property
    def ponr_markers(self) -> Tuple[PointOfNoReturn, ...]:
        return tuple(self._ponr_markers)

    @property
    def sealed_up_to(self) -> int:
        return self._sealed_up_to

    @property
    def length(self) -> int:
        return len(self._events)

    def __repr__(self) -> str:
        return (
            f"CausalTimeline("
            f"events={self.length}, "
            f"sealed_up_to={self._sealed_up_to}, "
            f"ponr_count={len(self._ponr_markers)})"
        )
