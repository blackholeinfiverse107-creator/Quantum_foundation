"""
reconciliation_engine.py
=========================
Phase 5 — Deterministic Reconciliation

Provides the ReconciliationEngine that:
  - Detects which nodes are behind (lagging)
  - Fetches missing events from Hub event log
  - Replays them in strict causal order
  - Verifies final state hash matches the expected (advanced) nodes
  - Guarantees: same final hash, no duplicate event application

No Cycle 1–8 core logic is modified.
"""

import hashlib
import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(__file__))
from computation_protocol import (
    ComputationProtocolHub,
    ProtocolNode,
    SequencedEvent
)
from distributed_state_node import ExecutionEvent


# ---------------------------------------------------------------------------
# Reconciliation result types
# ---------------------------------------------------------------------------

@dataclass
class NodeReconciliationResult:
    """Result of reconciling one lagging node."""
    node_id: str
    was_lagging: bool
    events_replayed: List[int]        # causal_ids that were applied
    events_already_committed: List[int]  # causal_ids skipped (already had)
    events_buffered: List[int]        # causal_ids buffered (still waiting for predecessor)
    pre_hash: str                     # state hash before reconciliation
    post_hash: str                    # state hash after reconciliation
    expected_hash: str                # hash of the reference node
    converged: bool                   # True if post_hash == expected_hash
    error: Optional[str] = None


@dataclass
class ReconciliationReport:
    """Full report from one reconciliation pass."""
    reconciled_nodes: List[NodeReconciliationResult]
    reference_node: str
    reference_hash: str
    reference_causal_id: int
    full_consensus_reached: bool
    hash_matches: Dict[str, bool]     # {node_id: True/False}

    def summary(self) -> str:
        n_ok = sum(1 for v in self.hash_matches.values() if v)
        n_total = len(self.hash_matches) + 1  # +1 for reference node
        return (
            f"ReconciliationReport: {n_ok}/{len(self.hash_matches)} lagging nodes converged. "
            f"Full consensus: {self.full_consensus_reached}. "
            f"Reference: {self.reference_node} @ causal_id={self.reference_causal_id}"
        )


# ---------------------------------------------------------------------------
# ReconciliationEngine
# ---------------------------------------------------------------------------

class ReconciliationEngine:
    """
    Reconciles lagging nodes against the most-advanced node.

    Protocol:
      1. Identify the reference node (highest committed causal_id)
      2. For each lagging node: request missing events from Hub
      3. Replay in strict causal order using existing merge machinery
      4. Verify final hash matches reference
      5. Report convergence

    Guarantees:
      - No event is applied twice (skipped if already committed)
      - No state is directly overwritten (all changes via FullStackHarness transitions)
      - Same event log → same final hash (determinism guarantee from model)
    """

    def __init__(self, hub: ComputationProtocolHub):
        self.hub = hub
        self._reconciliation_log: List[ReconciliationReport] = []

    def reconcile_all(self) -> ReconciliationReport:
        """
        Identify and reconcile all lagging nodes in one pass.
        Returns a ReconciliationReport describing the outcome.
        """
        nodes = self.hub.nodes

        # Step 1: Find reference node (highest committed causal_id)
        ref_node = max(nodes, key=lambda n: n.committed_causal_id)
        ref_hash = ref_node.get_state_hash()
        ref_cid = ref_node.committed_causal_id

        # Step 2: Reconcile each lagging node
        results = []
        for node in nodes:
            if node.node_id == ref_node.node_id:
                continue  # Skip the reference node itself

            result = self._reconcile_node(node, ref_node, ref_cid, ref_hash)
            results.append(result)

        # Step 3: Check full consensus
        all_hashes = {n.node_id: n.get_state_hash() for n in nodes}
        hash_matches = {r.node_id: r.converged for r in results}
        full_consensus = (
            len(set(all_hashes.values())) == 1 and
            all(n.committed_causal_id == ref_cid for n in nodes)
        )

        report = ReconciliationReport(
            reconciled_nodes=results,
            reference_node=ref_node.node_id,
            reference_hash=ref_hash,
            reference_causal_id=ref_cid,
            full_consensus_reached=full_consensus,
            hash_matches=hash_matches
        )
        self._reconciliation_log.append(report)
        return report

    def reconcile_node(self, node_id: str) -> NodeReconciliationResult:
        """
        Reconcile a single node by ID.
        The reference is the most advanced remaining node.
        """
        nodes = self.hub.nodes
        target = next((n for n in nodes if n.node_id == node_id), None)
        if target is None:
            raise ValueError(f"Node {node_id} not registered in hub")

        others = [n for n in nodes if n.node_id != node_id]
        ref = max(others, key=lambda n: n.committed_causal_id)
        return self._reconcile_node(target, ref, ref.committed_causal_id, ref.get_state_hash())

    def _reconcile_node(self, node: ProtocolNode,
                        ref_node: ProtocolNode,
                        ref_cid: int,
                        ref_hash: str) -> NodeReconciliationResult:
        """
        Core reconciliation logic for one node.
        """
        pre_hash = node.get_state_hash()
        was_lagging = node.committed_causal_id < ref_cid or node.is_partial

        if not was_lagging and pre_hash == ref_hash:
            # Node is already in sync — nothing to do
            return NodeReconciliationResult(
                node_id=node.node_id,
                was_lagging=False,
                events_replayed=[],
                events_already_committed=[],
                events_buffered=[],
                pre_hash=pre_hash,
                post_hash=pre_hash,
                expected_hash=ref_hash,
                converged=True
            )

        # Fetch missing events from Hub
        start_from = node.committed_causal_id + 1
        missing_sequenced = self.hub.get_event_slice(start_from, ref_cid)

        # Convert SequencedEvents to ExecutionEvents for the merge pipeline
        missing_net = [
            ExecutionEvent(
                causal_id=se.causal_id,
                origin_node_id=se.origin_node,
                event_type=se.step_type,
                payload=se.payload
            )
            for se in missing_sequenced
            if se.step_type != "SYNC"  # SYNC has no state effect
        ]

        # Replay via merge (no direct overwrite, only valid transitions)
        applied = []
        skipped = []
        buffered = []
        error_msg = None

        for net_event in sorted(missing_net, key=lambda e: e.causal_id):
            cid = net_event.causal_id
            if cid < node.next_expected_causal_id:
                skipped.append(cid)
                continue

            prev_expected = node.next_expected_causal_id
            try:
                node.receive_event(net_event)
                if node.next_expected_causal_id > prev_expected:
                    for aid in range(prev_expected, node.next_expected_causal_id):
                        applied.append(aid)
                else:
                    buffered.append(cid)
            except Exception as exc:
                error_msg = f"Event causal_id={cid} rejected during reconciliation: {exc}"
                break

        post_hash = node.get_state_hash()
        converged = (post_hash == ref_hash) and (node.committed_causal_id == ref_cid)

        return NodeReconciliationResult(
            node_id=node.node_id,
            was_lagging=was_lagging,
            events_replayed=applied,
            events_already_committed=skipped,
            events_buffered=buffered,
            pre_hash=pre_hash,
            post_hash=post_hash,
            expected_hash=ref_hash,
            converged=converged,
            error=error_msg
        )

    @property
    def reconciliation_history(self) -> List[ReconciliationReport]:
        return list(self._reconciliation_log)


# ---------------------------------------------------------------------------
# Self-Test Extracted Out
# ---------------------------------------------------------------------------
