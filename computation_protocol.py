"""
computation_protocol.py
========================
Phase 3 — Computation Execution Protocol

Defines the full proposal → sequencing → execution pipeline with:
  - ProposalMessage and SequencedEvent dataclasses
  - ComputationProtocolHub: strict ordering, execution tracking, SYNC support
  - ProtocolNode: wraps PropagatingStateNode with proposal API
  - AckMessage and per-node execution receipts
  - Identical execution guarantee enforced by Hub

No Cycle 1–8 core logic is modified.
"""

import time
import uuid
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from distributed_state_propagation import (
    PropagatingStateNode,
    PropagatingHub,
    StateSnapshot,
    MergeResult
)
from distributed_state_node import ExecutionEvent


# ---------------------------------------------------------------------------
# Protocol Message Types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProposalMessage:
    """
    Sent from a ProtocolNode to the Hub before sequencing.
    Has no causal authority — it is a *request*, not a command.
    """
    proposal_id: str         # Unique UUID per proposal
    origin_node: str         # Proposing node ID
    step_type: str           # "EVOLVE" | "MEASURE" | "SYNC"
    payload: dict            # Operation parameters
    proposed_at: float       # Monotonic timestamp (advisory only)

    @staticmethod
    def create(origin: str, step_type: str, payload: dict) -> "ProposalMessage":
        return ProposalMessage(
            proposal_id=str(uuid.uuid4()),
            origin_node=origin,
            step_type=step_type,
            payload=payload,
            proposed_at=time.monotonic()
        )

    @staticmethod
    def sync(origin: str) -> "ProposalMessage":
        return ProposalMessage(
            proposal_id=str(uuid.uuid4()),
            origin_node=origin,
            step_type="SYNC",
            payload={},
            proposed_at=time.monotonic()
        )


@dataclass(frozen=True)
class SequencedEvent:
    """
    Hub-stamped event with a global causal_id. Delivered to all nodes.
    This is the authoritative computation instruction.
    """
    causal_id: int
    proposal_id: str
    origin_node: str
    step_type: str
    payload: dict
    sequenced_at: float


@dataclass(frozen=True)
class AckMessage:
    """
    Acknowledgement from a node after applying a SequencedEvent.
    Contains the state hash after execution for integrity checking.
    """
    causal_id: int
    proposal_id: str
    node_id: str
    state_hash: str
    ack_type: str          # "APPLIED" | "BUFFERED" | "REJECTED"
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.ack_type in ("APPLIED", "BUFFERED")


@dataclass
class SyncReport:
    """
    Result of a SYNC step: global state consensus check.
    """
    causal_id: int
    node_hashes: Dict[str, str]
    consensus: bool
    diverged_nodes: List[str]
    committed_causal_ids: Dict[str, int]  # per-node

    def summary(self) -> str:
        if self.consensus:
            return f"SYNC causal_id={self.causal_id}: CONSENSUS [OK] (all {len(self.node_hashes)} nodes agree)"
        else:
            return (f"SYNC causal_id={self.causal_id}: DIVERGENCE [X] "
                    f"— diverged={self.diverged_nodes}")


@dataclass
class ExecutionReceipt:
    """
    Complete record of one computation step's lifecycle.
    """
    sequenced_event: SequencedEvent
    acks: List[AckMessage]
    sync_report: Optional[SyncReport]
    execution_complete: bool

    @property
    def all_applied(self) -> bool:
        return all(a.ack_type == "APPLIED" for a in self.acks)

    @property
    def any_rejected(self) -> bool:
        return any(a.ack_type == "REJECTED" for a in self.acks)


# ---------------------------------------------------------------------------
# ProtocolNode
# ---------------------------------------------------------------------------

class ProtocolNode(PropagatingStateNode):
    """
    A PropagatingStateNode extended with the formal proposal API.
    Communicates with ComputationProtocolHub via ProposalMessage and AckMessage.
    """

    def __init__(self, node_id: str, adapter: 'Any' = None):
        super().__init__(node_id, adapter)
        self._ack_log: List[AckMessage] = []

    def propose_event(self, step_type: str, payload: dict) -> ProposalMessage:
        """Propose a generic transition event."""
        return ProposalMessage.create(self.node_id, step_type, payload)

    def propose_sync(self) -> ProposalMessage:
        """Propose a SYNC (consensus check) step."""
        return ProposalMessage.sync(self.node_id)

    def execute_sequenced_event(self, event: SequencedEvent) -> AckMessage:
        """
        Execute a SequencedEvent delivered by the Hub.
        Returns an AckMessage with execution result.
        """
        prev_expected = self.next_expected_causal_id

        # Convert SequencedEvent to ExecutionEvent for existing pipeline
        net_event = ExecutionEvent(
            causal_id=event.causal_id,
            origin_node_id=event.origin_node,
            event_type=event.step_type,
            payload=event.payload
        )

        if event.step_type == "SYNC":
            # SYNC is a no-op on state — just report current hash
            self.next_expected_causal_id = event.causal_id + 1
            ack = AckMessage(
                causal_id=event.causal_id,
                proposal_id=event.proposal_id,
                node_id=self.node_id,
                state_hash=self.get_state_hash(),
                ack_type="APPLIED"
            )
        else:
            try:
                self.receive_event(net_event)
                if self.next_expected_causal_id > prev_expected:
                    ack_type = "APPLIED"
                else:
                    ack_type = "BUFFERED"
                ack = AckMessage(
                    causal_id=event.causal_id,
                    proposal_id=event.proposal_id,
                    node_id=self.node_id,
                    state_hash=self.get_state_hash(),
                    ack_type=ack_type
                )
            except Exception as exc:
                ack = AckMessage(
                    causal_id=event.causal_id,
                    proposal_id=event.proposal_id,
                    node_id=self.node_id,
                    state_hash="",
                    ack_type="REJECTED",
                    error=str(exc)
                )

        self._ack_log.append(ack)
        return ack

    @property
    def execution_log(self) -> List[AckMessage]:
        """Full history of acknowledgements for this node."""
        return list(self._ack_log)


# ---------------------------------------------------------------------------
# ComputationProtocolHub
# ---------------------------------------------------------------------------

class ComputationProtocolHub:
    """
    The authoritative hub for the distributed computation protocol.

    Responsibilities:
      1. Accept ProposalMessages from ProtocolNodes or external coordinators
      2. Assign monotonically increasing causal_id (strict ordering)
      3. Deliver SequencedEvents to all registered nodes
      4. Collect AckMessages and build ExecutionReceipts
      5. Run SYNC steps and generate SyncReports
      6. Halt if any node reports a REJECTED event or consensus fails

    Authority Model:
      - Hub is the ONLY source of causal_id assignment
      - No node may propose an event that bypasses the Hub
      - SYNC reports are read-only observation — they do not alter state
    """

    def __init__(self, halt_on_rejection: bool = True,
                       halt_on_divergence: bool = True):
        self.nodes: List[ProtocolNode] = []
        self._global_causal_id: int = 1
        self._event_log: List[SequencedEvent] = []
        self._receipts: List[ExecutionReceipt] = []
        self._sync_reports: List[SyncReport] = []
        self.halt_on_rejection = halt_on_rejection
        self.halt_on_divergence = halt_on_divergence
        self._halted: bool = False
        self._halt_reason: Optional[str] = None

        # Selective delivery support (for divergence simulation)
        self._exclude_map: Dict[int, List[str]] = {}   # causal_id → excluded nodes
        self._pending_held: Dict[str, List[SequencedEvent]] = {}

    # -----------------------------------------------------------------------
    # Node Registration
    # -----------------------------------------------------------------------

    def register_node(self, node: ProtocolNode):
        self.nodes.append(node)
        self._pending_held[node.node_id] = []

    # -----------------------------------------------------------------------
    # Core Protocol: Submit → Sequence → Execute
    # -----------------------------------------------------------------------

    def submit(self, proposal: ProposalMessage,
               exclude_nodes: Optional[List[str]] = None,
               delay_nodes: Optional[List[str]] = None) -> ExecutionReceipt:
        """
        Main protocol entry point. Accepts a proposal, sequences it,
        delivers to all nodes, and returns an ExecutionReceipt.

        Args:
            proposal: Proposal from any node or external coordinator
            exclude_nodes: Nodes to skip entirely (simulate missing event)
            delay_nodes: Nodes to hold event for (simulate delay)

        Returns:
            ExecutionReceipt with full execution trace.

        Raises:
            RuntimeError if hub is halted.
        """
        if self._halted:
            raise RuntimeError(f"Hub is HALTED: {self._halt_reason}. "
                                "No further operations permitted.")

        # Step 1: Sequence the proposal
        sequenced = SequencedEvent(
            causal_id=self._global_causal_id,
            proposal_id=proposal.proposal_id,
            origin_node=proposal.origin_node,
            step_type=proposal.step_type,
            payload=proposal.payload,
            sequenced_at=time.monotonic()
        )
        self._global_causal_id += 1
        self._event_log.append(sequenced)

        exclude_nodes = exclude_nodes or []
        delay_nodes = delay_nodes or []

        # Step 2: Deliver to nodes and collect acks
        acks = []
        sync_report = None

        for node in self.nodes:
            if node.node_id in exclude_nodes:
                continue  # Completely skip (simulate dropped packet)

            if node.node_id in delay_nodes:
                self._pending_held[node.node_id].append(sequenced)
                # No ack yet — node hasn't received it
                continue

            ack = node.execute_sequenced_event(sequenced)
            acks.append(ack)

            # Check for rejection
            if ack.ack_type == "REJECTED" and self.halt_on_rejection:
                self._halt(f"Node {node.node_id} REJECTED causal_id={sequenced.causal_id}: {ack.error}")

        # Step 3: For SYNC steps, build consensus report
        if proposal.step_type == "SYNC":
            sync_report = self._build_sync_report(sequenced, acks)
            self._sync_reports.append(sync_report)

            if not sync_report.consensus and self.halt_on_divergence:
                self._halt(f"SYNC causal_id={sequenced.causal_id} "
                           f"revealed divergence: {sync_report.diverged_nodes}")

        receipt = ExecutionReceipt(
            sequenced_event=sequenced,
            acks=acks,
            sync_report=sync_report,
            execution_complete=not self._halted
        )
        self._receipts.append(receipt)
        return receipt

    def release_held_events(self, node_id: str) -> List[AckMessage]:
        """
        Deliver all held events to a previously-delayed node.
        Returns acks for each delivered event.
        """
        if self._halted:
            raise RuntimeError(f"Hub is HALTED: {self._halt_reason}")

        node = self._find_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not registered")

        held = self._pending_held.get(node_id, [])
        acks = []
        for event in held:
            ack = node.execute_sequenced_event(event)
            acks.append(ack)
            if ack.ack_type == "REJECTED" and self.halt_on_rejection:
                self._halt(f"Node {node_id} REJECTED held event causal_id={event.causal_id}")
                break
        self._pending_held[node_id] = []
        return acks

    # -----------------------------------------------------------------------
    # Event Log Access
    # -----------------------------------------------------------------------

    def get_event_log(self) -> List[SequencedEvent]:
        """Return the complete ordered event log."""
        return list(self._event_log)

    def get_event_slice(self, from_id: int, to_id: Optional[int] = None) -> List[SequencedEvent]:
        """Return a slice of the event log by causal_id range."""
        to_id = to_id or (self._global_causal_id - 1)
        return [e for e in self._event_log if from_id <= e.causal_id <= to_id]

    def get_receipts(self) -> List[ExecutionReceipt]:
        return list(self._receipts)

    def get_sync_reports(self) -> List[SyncReport]:
        return list(self._sync_reports)

    # -----------------------------------------------------------------------
    # State
    # -----------------------------------------------------------------------

    @property
    def is_halted(self) -> bool:
        return self._halted

    @property
    def halt_reason(self) -> Optional[str]:
        return self._halt_reason

    @property
    def next_causal_id(self) -> int:
        return self._global_causal_id

    def get_node_status(self) -> List[dict]:
        return [
            {
                "node_id": n.node_id,
                "committed_causal_id": n.committed_causal_id,
                "is_partial": n.is_partial,
                "pending": n.pending_causal_ids,
                "state_hash": n.get_state_hash()[:16] + "..."
            }
            for n in self.nodes
        ]

    def check_full_consensus(self) -> dict:
        """Consensus check across all nodes (including partially-committed)."""
        hashes = {n.node_id: n.get_state_hash() for n in self.nodes}
        unique = set(hashes.values())
        partial = [n.node_id for n in self.nodes if n.is_partial]
        return {
            "consensus": len(unique) <= 1 and len(partial) == 0,
            "unique_hashes": list(unique),
            "node_hashes": hashes,
            "partial_nodes": partial
        }

    # -----------------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------------

    def _build_sync_report(self, event: SequencedEvent,
                           acks: List[AckMessage]) -> SyncReport:
        node_hashes = {a.node_id: a.state_hash for a in acks}
        committed_ids = {n.node_id: n.committed_causal_id for n in self.nodes
                         if n.node_id in node_hashes}
        unique_hashes = set(node_hashes.values())
        consensus = len(unique_hashes) == 1
        majority_hash = max(unique_hashes, key=list(node_hashes.values()).count) if node_hashes else ""
        diverged = [nid for nid, h in node_hashes.items() if h != majority_hash]
        return SyncReport(
            causal_id=event.causal_id,
            node_hashes=node_hashes,
            consensus=consensus,
            diverged_nodes=diverged,
            committed_causal_ids=committed_ids
        )

    def _halt(self, reason: str):
        self._halted = True
        self._halt_reason = reason

    def _find_node(self, node_id: str) -> Optional[ProtocolNode]:
        for n in self.nodes:
            if n.node_id == node_id:
                return n
        return None


# ---------------------------------------------------------------------------
# Self-Test extracted out for Domain Agnosticism
# ---------------------------------------------------------------------------
