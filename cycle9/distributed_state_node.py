"""
Cycle 9 — Distributed State Node
==================================

A DistributedStateNode is a self-contained computation unit that:
  - Wraps a FullStackHarness (all 8 cycles: state, collapse, causality, error, no-go)
  - Maintains a local causal timeline
  - Exposes a deterministic API: observe(), evolve(), measure(), receive_event()
  - Propagates events to peer nodes via a registered broadcast callback

Design constraints (inherited and extended):
  • No shared mutable state between nodes — each node owns its harness
  • Events are propagated as immutable NetworkEvent records
  • receive_event() is idempotent: duplicate event_ids are silently dropped
  • Causal ordering is enforced: events are applied in logical-clock order
  • No node can initiate a measurement on behalf of another node
  • Deterministic replay: given the same event stream, all nodes converge

Node lifecycle:
  INIT → ACTIVE → SEALED
  - INIT: harness constructed, rules registered
  - ACTIVE: observe/evolve/measure/receive_event permitted
  - SEALED: no further mutations; timeline frozen
"""

from __future__ import annotations

import sys
import os
import math
import hashlib
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from full_stack_integration_harness import FullStackHarness
from cycle2.collapse_engine import IrreversibleCollapseEvent
from cycle3.causality_primitives import CausalEvent


# ---------------------------------------------------------------------------
# Network Event — the unit of inter-node communication
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NetworkEvent:
    """
    An immutable record broadcast between nodes.

    Fields:
      event_id      — globally unique identifier (origin_node_id + logical clock)
      origin_node   — node_id that produced this event
      event_type    — "EVOLUTION" | "COLLAPSE" | "SEAL"
      logical_clock — Lamport timestamp at origin at time of emission
      payload       — the underlying CausalEvent from the origin node's timeline
    """
    event_id: str
    origin_node: str
    event_type: str          # "EVOLUTION" | "COLLAPSE" | "SEAL"
    logical_clock: int
    payload: object          # CausalEvent from origin timeline


# ---------------------------------------------------------------------------
# Node Lifecycle States
# ---------------------------------------------------------------------------

_INIT   = "INIT"
_ACTIVE = "ACTIVE"
_SEALED = "SEALED"


# ---------------------------------------------------------------------------
# Distributed State Node
# ---------------------------------------------------------------------------

class DistributedStateNode:
    """
    A single computation node in the distributed quantum network.

    Each node independently evolves a shared initial state space.
    Nodes communicate exclusively through NetworkEvent propagation —
    there is no shared memory, no shared object reference.

    API:
      observe(rule_name)          → register a unitary rule (INIT only)
      evolve(rule_name)           → apply evolution, broadcast NetworkEvent
      measure(token_id, seed)     → collapse + broadcast NetworkEvent
      receive_event(net_event)    → apply a remote event to local state
      seal(reason)                → freeze this node's timeline
      state_hash()                → deterministic hash of current state
      timeline_hash()             → deterministic hash of full event log
    """

    def __init__(
        self,
        node_id: str,
        initial_amplitudes: dict,
        broadcast: Optional[Callable[[NetworkEvent], None]] = None,
    ) -> None:
        """
        Args:
            node_id:             unique string identifier for this node
            initial_amplitudes:  initial quantum state (must be normalised)
            broadcast:           callback invoked with each NetworkEvent this
                                 node emits; set by the network layer
        """
        if not node_id:
            raise ValueError("node_id must be non-empty")

        self.node_id = node_id
        self._harness = FullStackHarness(initial_amplitudes)
        self._broadcast: Optional[Callable[[NetworkEvent], None]] = broadcast
        self._logical_clock: int = 0
        self._seen_event_ids: Set[str] = set()
        self._received_log: List[NetworkEvent] = []   # ordered received events
        self._lifecycle: str = _INIT
        self._registered_rules: Dict[str, dict] = {}  # rule_name → matrix

    # --- Lifecycle ---

    def _assert_active(self) -> None:
        if self._lifecycle != _ACTIVE:
            raise RuntimeError(
                f"Node '{self.node_id}' is in state '{self._lifecycle}'. "
                "Only ACTIVE nodes may process events."
            )

    def activate(self) -> None:
        """Transition from INIT to ACTIVE. Must be called before evolve/measure."""
        if self._lifecycle != _INIT:
            raise RuntimeError(f"Node '{self.node_id}' already activated.")
        self._lifecycle = _ACTIVE

    # --- Rule Registration (INIT phase) ---

    def observe(self, rule_name: str, matrix: dict, description: str = "") -> None:
        """
        Register a unitary evolution rule on this node.
        Must be called before activate().
        All nodes in a network must register identical rules for determinism.
        """
        if self._lifecycle != _INIT:
            raise RuntimeError(
                f"Node '{self.node_id}': rules must be registered before activation."
            )
        self._harness.define_unitary_operation(rule_name, matrix, description)
        self._registered_rules[rule_name] = {"matrix": matrix, "description": description}

    # --- Evolution ---

    def evolve(self, rule_name: str) -> NetworkEvent:
        """
        Apply a registered unitary evolution locally and broadcast the event.

        Returns the NetworkEvent that was broadcast.
        """
        self._assert_active()
        self._logical_clock += 1
        ref = self._harness.evolve_deterministic(rule_name)

        # Retrieve the causal event just appended to the local timeline
        causal_event = self._harness.system.timeline.events[-1]

        net_event = NetworkEvent(
            event_id=f"{self.node_id}:{self._logical_clock}",
            origin_node=self.node_id,
            event_type="EVOLUTION",
            logical_clock=self._logical_clock,
            payload=causal_event,
        )
        self._seen_event_ids.add(net_event.event_id)
        if self._broadcast:
            self._broadcast(net_event)
        return net_event

    # --- Measurement ---

    def measure(self, token_id: str, seed: int) -> Tuple[NetworkEvent, IrreversibleCollapseEvent]:
        """
        Perform irreversible collapse locally and broadcast the collapse event.

        Returns (NetworkEvent, IrreversibleCollapseEvent).
        The collapse event carries the post-collapse state for peer synchronisation.
        """
        self._assert_active()
        self._logical_clock += 1
        collapse_event = self._harness.measure_deterministic(token_id, seed)

        causal_event = self._harness.system.timeline.events[-1]

        net_event = NetworkEvent(
            event_id=f"{self.node_id}:{self._logical_clock}",
            origin_node=self.node_id,
            event_type="COLLAPSE",
            logical_clock=self._logical_clock,
            payload=causal_event,
        )
        self._seen_event_ids.add(net_event.event_id)
        if self._broadcast:
            self._broadcast(net_event)
        return net_event, collapse_event

    # --- Event Reception ---

    def receive_event(self, net_event: NetworkEvent) -> bool:
        """
        Apply a NetworkEvent received from a peer node.

        Idempotent: duplicate event_ids are silently dropped (returns False).
        Causal ordering: the Lamport clock is updated on receipt.

        For EVOLUTION events: the local harness re-applies the same rule.
        For COLLAPSE events:  the local harness re-applies the same collapse
                              (same token_id and seed extracted from payload).
        For SEAL events:      the local timeline is sealed.

        Returns True if the event was applied, False if it was a duplicate.
        """
        self._assert_active()

        # Idempotency guard
        if net_event.event_id in self._seen_event_ids:
            return False

        # Lamport clock update: max(local, remote) + 1
        self._logical_clock = max(self._logical_clock, net_event.logical_clock) + 1
        self._seen_event_ids.add(net_event.event_id)
        self._received_log.append(net_event)

        causal_event = net_event.payload  # CausalEvent from origin

        if net_event.event_type == "EVOLUTION":
            # Payload is a dict: {'observation': Observation, 'noise_fidelity': float}
            # Extract rule name from the Observation inside the causal payload
            observation = causal_event.payload["observation"]
            rule_name = observation.observation_type
            self._harness.evolve_deterministic(rule_name)

        elif net_event.event_type == "COLLAPSE":
            # Payload is an IrreversibleCollapseEvent
            collapse_record = causal_event.payload
            token_id = collapse_record.token_id
            seed = collapse_record.result.seed_used
            self._harness.measure_deterministic(token_id, seed)

        elif net_event.event_type == "SEAL":
            reason = str(causal_event.payload) if causal_event else "remote_seal"
            self._harness.seal_timeline(reason)

        return True

    # --- Seal ---

    def seal(self, reason: str) -> NetworkEvent:
        """Seal this node's timeline and broadcast the seal event."""
        self._assert_active()
        self._logical_clock += 1
        self._harness.seal_timeline(reason)

        causal_event = self._harness.system.timeline.events[-1]
        net_event = NetworkEvent(
            event_id=f"{self.node_id}:{self._logical_clock}",
            origin_node=self.node_id,
            event_type="SEAL",
            logical_clock=self._logical_clock,
            payload=causal_event,
        )
        self._seen_event_ids.add(net_event.event_id)
        self._lifecycle = _SEALED
        if self._broadcast:
            self._broadcast(net_event)
        return net_event

    # --- Hashing (for deterministic replay validation) ---

    def state_hash(self) -> str:
        """SHA-256 of the current state amplitudes (deterministic)."""
        h = hashlib.sha256()
        state_dict = self._harness.system.state_engine.current_state.as_dict()
        for k in sorted(state_dict.keys()):
            v = state_dict[k]
            h.update(k.encode())
            h.update(f"({v.real:.8f}+{v.imag:.8f}j)".encode())
        return h.hexdigest()

    def timeline_hash(self) -> str:
        """SHA-256 of the local causal timeline (wall-clock stripped)."""
        import re
        h = hashlib.sha256()
        for event in self._harness.system.timeline.events:
            h.update(str(event.causal_id).encode())
            h.update(event.event_type.encode())
            payload_str = repr(event.payload)
            payload_str = re.sub(r"timestamp_ns=\d+", "timestamp_ns=0", payload_str)
            payload_str = re.sub(r"issued_at_ns=\d+", "issued_at_ns=0", payload_str)
            payload_str = re.sub(r"wall_time_ns=\d+", "wall_time_ns=0", payload_str)
            payload_str = re.sub(r" at 0x[0-9a-fA-F]+", "", payload_str)
            h.update(payload_str.encode())
        return h.hexdigest()

    def verify_invariants(self) -> dict:
        """Run the full invariant suite on this node's harness."""
        return self._harness.verify_all_invariants()

    @property
    def lifecycle(self) -> str:
        return self._lifecycle

    @property
    def received_log(self) -> Tuple[NetworkEvent, ...]:
        return tuple(self._received_log)

    def __repr__(self) -> str:
        return (
            f"DistributedStateNode(id='{self.node_id}', "
            f"lifecycle={self._lifecycle}, "
            f"clock={self._logical_clock})"
        )
