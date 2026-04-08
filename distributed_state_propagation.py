"""
distributed_state_propagation.py
=================================
Phase 2 — Partial State Propagation

Extends DistributedStateNode with:
  - Partial state holding (snapshots with causal stamps)
  - Receiving and merging updates from other nodes
  - Deterministic state merge (no direct overwrite, only valid transitions)

This module does NOT modify any Cycle 1–8 core logic.
It wraps the existing DistributedStateNode additively.
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from distributed_state_node import DistributedStateNode, ExecutionEvent


# ---------------------------------------------------------------------------
# Partial State Snapshot
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StateSnapshot:
    """
    A read-only, causally-stamped export of a node's state at a given point.
    Shared between nodes for catch-up and reconciliation — never used to write.
    """
    node_id: str
    last_applied_causal_id: int
    state_hash: str
    domain_state_dict: dict       # Frozen copy of adapter state
    captured_at: float            # Monotonic timestamp (non-authoritative)

    def __eq__(self, other):
        if not isinstance(other, StateSnapshot):
            return False
        return (self.state_hash == other.state_hash and
                self.last_applied_causal_id == other.last_applied_causal_id)


# ---------------------------------------------------------------------------
# Merge Result
# ---------------------------------------------------------------------------

@dataclass
class MergeResult:
    """
    Result of applying a batch of events during a catch-up merge.
    Describes what was applied, what was skipped, and the final hash.
    """
    events_applied: List[int]       # causal_ids that were applied
    events_skipped: List[int]       # causal_ids already committed (duplicates)
    events_buffered: List[int]      # causal_ids buffered (waiting for predecessors)
    final_state_hash: str
    success: bool
    error_message: Optional[str] = None


# ---------------------------------------------------------------------------
# PropagatingStateNode
# ---------------------------------------------------------------------------

class PropagatingStateNode(DistributedStateNode):
    """
    Extended DistributedStateNode that supports:
      1. Generating StateSnapshots for export
      2. Receiving event batches from Hub (batch catch-up)
      3. Deterministic merge with no overwrite
      4. Tracking partial knowledge status
    """

    def __init__(self, node_id: str, adapter: 'Any' = None):
        super().__init__(node_id, adapter)
        # Snapshot history keyed by causal_id
        self._snapshot_history: Dict[int, StateSnapshot] = {}
        # Track events that were rejected by invariants
        self._rejected_events: List[Tuple[ExecutionEvent, str]] = []
        # Partial knowledge flag — True if node is known to be missing events
        self._is_partial: bool = False

    # -----------------------------------------------------------------------
    # Snapshot Export
    # -----------------------------------------------------------------------

    def export_snapshot(self) -> StateSnapshot:
        """
        Export a read-only, causally-stamped snapshot of the current state.
        Safe to share with other nodes or the reconciliation engine.
        """
        domain_dict = getattr(self.adapter, "to_dict", lambda: {})()
        snap = StateSnapshot(
            node_id=self.node_id,
            last_applied_causal_id=self.next_expected_causal_id - 1,
            state_hash=self.get_state_hash(),
            domain_state_dict=domain_dict,
            captured_at=time.monotonic()
        )
        # Cache for diagnostic use
        self._snapshot_history[snap.last_applied_causal_id] = snap
        return snap

    def get_snapshot_at(self, causal_id: int) -> Optional[StateSnapshot]:
        """Retrieve a previously taken snapshot at a given causal ID."""
        return self._snapshot_history.get(causal_id)

    # -----------------------------------------------------------------------
    # Batch Merge (Catch-Up Protocol)
    # -----------------------------------------------------------------------

    def merge_event_batch(self, events: List[ExecutionEvent]) -> MergeResult:
        """
        Deterministically apply a batch of events in causal order.

        Rules:
          - Events already committed (causal_id < next_expected) are skipped
          - Events not yet reachable are buffered (existing receive_event logic)
          - No direct state overwrite: only FullStackHarness transitions are valid
          - Invariant violations are caught and recorded; merge halts on first failure

        Returns a MergeResult describing what happened.
        """
        applied = []
        skipped = []
        buffered = []
        error_msg = None
        success = True

        # Sort events by causal_id to ensure deterministic processing order
        ordered = sorted(events, key=lambda e: e.causal_id)

        for event in ordered:
            cid = event.causal_id

            # Skip already-committed events (no duplicate application)
            if cid < self.next_expected_causal_id:
                skipped.append(cid)
                continue

            # Attempt to receive (will buffer or apply via existing logic)
            prev_expected = self.next_expected_causal_id
            try:
                self.receive_event(event)
            except Exception as exc:
                # FullStackHarness or invariant rejected this event
                self._rejected_events.append((event, str(exc)))
                error_msg = f"Event causal_id={cid} rejected: {exc}"
                success = False
                break

            # Determine outcome
            if self.next_expected_causal_id > prev_expected:
                # Event was applied (and possibly buffered predecessors too)
                for applied_id in range(prev_expected, self.next_expected_causal_id):
                    applied.append(applied_id)
            else:
                # Event was buffered, not yet applied
                buffered.append(cid)

        self._is_partial = len(buffered) > 0

        return MergeResult(
            events_applied=applied,
            events_skipped=skipped,
            events_buffered=buffered,
            final_state_hash=self.get_state_hash(),
            success=success,
            error_message=error_msg
        )

    # -----------------------------------------------------------------------
    # Partial Knowledge Status
    # -----------------------------------------------------------------------

    @property
    def is_partial(self) -> bool:
        """
        True if this node is known to hold partial (incomplete) state —
        i.e., it has buffered events waiting for predecessors.
        """
        return len(self.event_buffer) > 0

    @property
    def pending_causal_ids(self) -> List[int]:
        """Return list of causal IDs buffered but not yet applied."""
        return sorted(self.event_buffer.keys())

    @property
    def committed_causal_id(self) -> int:
        """The highest causal_id fully committed on this node."""
        return self.next_expected_causal_id - 1

    # -----------------------------------------------------------------------
    # Determinism Verification
    # -----------------------------------------------------------------------

    def verify_matches_snapshot(self, snapshot: StateSnapshot) -> bool:
        """
        Verify that this node's current state matches a given snapshot.
        Used during reconciliation to confirm catch-up success.
        """
        return (self.get_state_hash() == snapshot.state_hash and
                self.committed_causal_id == snapshot.last_applied_causal_id)

    def rejected_event_summary(self) -> List[dict]:
        """Return summary of any events rejected by invariant enforcement."""
        return [
            {
                "causal_id": ev.causal_id,
                "origin": ev.origin_node_id,
                "type": ev.event_type,
                "reason": reason
            }
            for ev, reason in self._rejected_events
        ]

    # -----------------------------------------------------------------------
    # Enhanced State Hash (with causal stamp)
    # -----------------------------------------------------------------------

    def get_stamped_hash(self) -> dict:
        """
        Returns the state hash along with the causal context it was taken in.
        Allows distinguishing 'same hash at different causal positions'.
        """
        return {
            "node_id": self.node_id,
            "causal_id": self.committed_causal_id,
            "state_hash": self.get_state_hash(),
            "pending_events": self.pending_causal_ids
        }


# ---------------------------------------------------------------------------
# PropagatingHub (extended NetworkHub)
# ---------------------------------------------------------------------------

class PropagatingHub:
    """
    Extended hub that supports:
      - Tracking per-node acknowledgement state
      - Detecting which nodes are lagging
      - Providing event log slices for catch-up
    """

    def __init__(self):
        self.nodes: List[PropagatingStateNode] = []
        self.global_causal_id: int = 1
        self.event_log: List[ExecutionEvent] = []
        self._delivery_mode: str = "IMMEDIATE"  # can switch to "SELECTIVE"
        self._held_events: Dict[str, List[ExecutionEvent]] = {}  # for simulated delays

    def register_node(self, node: PropagatingStateNode):
        self.nodes.append(node)
        self._held_events[node.node_id] = []

    def broadcast(self, raw_event: ExecutionEvent,
                  exclude_nodes: Optional[List[str]] = None,
                  delay_nodes: Optional[List[str]] = None) -> ExecutionEvent:
        """
        Sequence and broadcast an event.

        Args:
            raw_event: Unsequenced proposal from a node
            exclude_nodes: Node IDs to skip entirely (simulate missing event)
            delay_nodes: Node IDs to hold the event for (simulate delay)

        Returns:
            The sequenced event (with assigned causal_id).
        """
        sequenced = ExecutionEvent(
            causal_id=self.global_causal_id,
            origin_node_id=raw_event.origin_node_id,
            event_type=raw_event.event_type,
            payload=raw_event.payload
        )
        self.global_causal_id += 1
        self.event_log.append(sequenced)

        exclude_nodes = exclude_nodes or []
        delay_nodes = delay_nodes or []

        for node in self.nodes:
            if node.node_id in exclude_nodes:
                continue  # Event never delivered (simulate missing event)
            elif node.node_id in delay_nodes:
                self._held_events[node.node_id].append(sequenced)  # Hold for later
            else:
                node.receive_event(sequenced)

        return sequenced

    def release_held_events(self, node_id: str) -> List[ExecutionEvent]:
        """
        Release all held (delayed) events to a specific node.
        Simulates a delayed node finally receiving its events.
        """
        held = self._held_events.get(node_id, [])
        node = self._find_node(node_id)
        if node:
            for event in held:
                node.receive_event(event)
        self._held_events[node_id] = []
        return held

    def get_event_slice(self, from_causal_id: int,
                        to_causal_id: Optional[int] = None) -> List[ExecutionEvent]:
        """
        Return event log slice from from_causal_id (inclusive) to to_causal_id.
        Used by reconciliation engine to replay missed events.
        """
        if to_causal_id is None:
            to_causal_id = self.event_log[-1].causal_id if self.event_log else 0
        return [e for e in self.event_log if from_causal_id <= e.causal_id <= to_causal_id]

    def get_node_status(self) -> List[dict]:
        """Return current status of all registered nodes."""
        return [
            {
                "node_id": n.node_id,
                "committed_causal_id": n.committed_causal_id,
                "is_partial": n.is_partial,
                "pending_events": n.pending_causal_ids,
                "state_hash": n.get_state_hash()
            }
            for n in self.nodes
        ]

    def check_consensus(self) -> dict:
        """
        Check whether all nodes agree on the same state hash.
        Only considers nodes with no pending events (fully committed).
        """
        fully_committed = [n for n in self.nodes if not n.is_partial]
        partial_nodes = [n.node_id for n in self.nodes if n.is_partial]

        hashes = {n.node_id: n.get_state_hash() for n in fully_committed}
        unique_hashes = set(hashes.values())

        return {
            "consensus": len(unique_hashes) <= 1,
            "unique_hashes": list(unique_hashes),
            "node_hashes": hashes,
            "partial_nodes": partial_nodes,
            "total_nodes": len(self.nodes),
            "committed_nodes": len(fully_committed)
        }

    def _find_node(self, node_id: str) -> Optional[PropagatingStateNode]:
        for n in self.nodes:
            if n.node_id == node_id:
                return n
        return None


# ---------------------------------------------------------------------------
# Self-Test Extracted out for domain-agnosticism.
# ---------------------------------------------------------------------------
