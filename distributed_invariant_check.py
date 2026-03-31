"""
distributed_invariant_check.py
================================
Phase 6 — Distributed Invariant Enforcement

Extends invariant checking across the entire node network:
  - Each node runs its local invariants (Cycles 1–8 via FullStackHarness)
  - Hub checks global consensus (all nodes must agree on state hash)
  - If any local invariant fails OR nodes disagree → SYSTEM HALT

Authority: This module enforces. It does not compute. It cannot bypass sealed invariants.

No Cycle 1–8 core logic is modified.
"""

import sys
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(__file__))
from computation_protocol import ComputationProtocolHub, ProtocolNode


# ---------------------------------------------------------------------------
# Report types
# ---------------------------------------------------------------------------

@dataclass
class NodeInvariantResult:
    """Full invariant check result for one node."""
    node_id: str
    committed_causal_id: int
    state_hash: str
    local_passed: List[str]
    local_failed: List[str]
    is_partial: bool

    @property
    def ok(self) -> bool:
        return len(self.local_failed) == 0 and not self.is_partial


@dataclass
class GlobalInvariantReport:
    """Full distributed invariant check result."""
    node_results: List[NodeInvariantResult]
    global_consensus: bool           # All nodes agree on state hash
    all_local_passed: bool           # All nodes passed all local invariants
    diverged_nodes: List[str]        # Nodes with different hashes
    partial_nodes: List[str]         # Nodes with pending events
    failed_invariant_nodes: List[str]# Nodes with invariant failures
    reference_hash: str              # Hash of the most advanced node
    system_should_halt: bool
    halt_reasons: List[str]

    @property
    def clean(self) -> bool:
        return self.global_consensus and self.all_local_passed and not self.system_should_halt

    def summary(self) -> str:
        status = "PASS [OK]" if self.clean else "HALT [X]"
        parts = []
        if not self.global_consensus:
            parts.append(f"consensus_fail={self.diverged_nodes}")
        if not self.all_local_passed:
            parts.append(f"invariant_fail={self.failed_invariant_nodes}")
        if self.partial_nodes:
            parts.append(f"partial={self.partial_nodes}")
        detail = " | ".join(parts) if parts else "all checks passed"
        return f"[{status}] {detail}"


# ---------------------------------------------------------------------------
# DistributedInvariantChecker
# ---------------------------------------------------------------------------

class DistributedInvariantChecker:
    """
    Runs a full distributed invariant check across all nodes registered to a Hub.

    Enforcement policy:
      1. Run local harness invariants on each node (C1–C8)
      2. Check global state-hash consensus
      3. Check all nodes are fully committed (no partial state)
      4. If anything fails → system_should_halt = True
         Caller is responsible for taking action (halt hub, raise, log)

    Raj Prajapati — Enforcement Gateway:
      This class is the enforcement boundary. No authority leaks.
      It observes only — it does not mutate any node state.
    """

    def __init__(self, hub: ComputationProtocolHub):
        self.hub = hub
        self._check_history: List[GlobalInvariantReport] = []

    def run_full_check(self) -> GlobalInvariantReport:
        """
        Run full distributed invariant check. Returns a GlobalInvariantReport.
        Does NOT halt the hub automatically — caller decides on action.
        """
        nodes = self.hub.nodes
        halt_reasons = []
        node_results = []

        # Step 1: Per-node local invariant check
        for node in nodes:
            result = self._check_node(node)
            node_results.append(result)
            if not result.ok:
                if result.local_failed:
                    halt_reasons.append(
                        f"Node {node.node_id} invariant failures: {result.local_failed}"
                    )
                if result.is_partial:
                    halt_reasons.append(
                        f"Node {node.node_id} is partial (pending causal_ids: {node.pending_causal_ids})"
                    )

        # Step 2: Global hash consensus
        fully_committed = [r for r in node_results if not r.is_partial]
        partial_nodes = [r.node_id for r in node_results if r.is_partial]
        failed_invariant_nodes = [r.node_id for r in node_results if r.local_failed]

        all_hashes = {r.node_id: r.state_hash for r in fully_committed}
        unique_hashes = set(all_hashes.values())
        global_consensus = (len(unique_hashes) <= 1) and (len(partial_nodes) == 0)

        if not global_consensus:
            majority_hash = max(unique_hashes, key=lambda h: list(all_hashes.values()).count(h)) \
                            if unique_hashes else ""
            diverged = [nid for nid, h in all_hashes.items() if h != majority_hash]
            halt_reasons.append(f"Global hash divergence: nodes {diverged} disagree.")
        else:
            diverged = []

        reference_hash = (
            max(fully_committed, key=lambda r: r.committed_causal_id).state_hash
            if fully_committed else ""
        )

        all_local_passed = all(r.ok for r in node_results if not r.is_partial)
        system_should_halt = bool(halt_reasons)

        report = GlobalInvariantReport(
            node_results=node_results,
            global_consensus=global_consensus,
            all_local_passed=all_local_passed,
            diverged_nodes=diverged,
            partial_nodes=partial_nodes,
            failed_invariant_nodes=failed_invariant_nodes,
            reference_hash=reference_hash,
            system_should_halt=system_should_halt,
            halt_reasons=halt_reasons
        )
        self._check_history.append(report)
        return report

    def run_and_halt_if_failed(self) -> GlobalInvariantReport:
        """
        Run the full check. If the system should halt, also halt the hub.
        This is the 'enforcement mode' used in production simulation.
        """
        report = self.run_full_check()
        if report.system_should_halt:
            self.hub._halt(
                "DistributedInvariantChecker: " + " | ".join(report.halt_reasons)
            )
        return report

    def _check_node(self, node: ProtocolNode) -> NodeInvariantResult:
        """Run local harness invariants on a single node."""
        passed = []
        failed = []

        try:
            inv_report = node.verify_node_integrity()
            for cycle, res in inv_report.items():
                for p in res.get("passed", []):
                    passed.append(f"{cycle}::{p}")
                for f_item in res.get("failed", []):
                    failed.append(f"{cycle}::{f_item}")
        except Exception as exc:
            failed.append(f"EXCEPTION during invariant check: {exc}")

        return NodeInvariantResult(
            node_id=node.node_id,
            committed_causal_id=node.committed_causal_id,
            state_hash=node.get_state_hash(),
            local_passed=passed,
            local_failed=failed,
            is_partial=node.is_partial
        )

    @property
    def check_history(self) -> List[GlobalInvariantReport]:
        return list(self._check_history)


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def assert_global_invariants(hub: ComputationProtocolHub, label: str = "") -> GlobalInvariantReport:
    """
    Run full distributed invariant check and raise RuntimeError if it fails.
    Use this as a gate in simulation loops.
    """
    checker = DistributedInvariantChecker(hub)
    report = checker.run_full_check()
    tag = f"[{label}] " if label else ""
    if report.system_should_halt:
        raise RuntimeError(
            f"{tag}DISTRIBUTED INVARIANT CHECK FAILED:\n" +
            "\n".join(f"  - {r}" for r in report.halt_reasons)
        )
    return report


# ---------------------------------------------------------------------------
# Self-Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import math
    from computation_protocol import ProposalMessage

    print("=== distributed_invariant_check.py — Self Test ===\n")

    initial_amps = {"0": complex(1.0, 0.0), "1": complex(0.0, 0.0)}
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {
        ("0", "0"): inv_sq2, ("0", "1"): inv_sq2,
        ("1", "0"): inv_sq2, ("1", "1"): -inv_sq2
    }

    hub = ComputationProtocolHub(halt_on_rejection=True, halt_on_divergence=False)
    for name in ["Node_A", "Node_B", "Node_C"]:
        n = ProtocolNode(name, initial_amps)
        n.harness.define_unitary_operation("H", h_matrix, "Hadamard")
        hub.register_node(n)

    nodes = {n.node_id: n for n in hub.nodes}

    # Normal operations — all nodes in sync
    p1 = nodes["Node_A"].propose_evolve("H")
    hub.submit(p1)

    p2 = nodes["Node_B"].propose_measure("m1", 42)
    hub.submit(p2)

    # Test 1: Clean check (should pass)
    checker = DistributedInvariantChecker(hub)
    report = checker.run_full_check()
    print(f"Test 1 (clean): {report.summary()}")
    assert report.clean, f"Expected clean report, got: {report.halt_reasons}"

    # Test 2: Introduce divergence — delay one node
    hub2 = ComputationProtocolHub(halt_on_rejection=True, halt_on_divergence=False)
    for name in ["Node_X", "Node_Y"]:
        n = ProtocolNode(name, initial_amps)
        n.harness.define_unitary_operation("H", h_matrix, "Hadamard")
        hub2.register_node(n)

    nodes2 = {n.node_id: n for n in hub2.nodes}
    p3 = nodes2["Node_X"].propose_evolve("H")
    hub2.submit(p3, delay_nodes=["Node_Y"])  # Node_Y doesn't get it

    checker2 = DistributedInvariantChecker(hub2)
    report2 = checker2.run_full_check()
    print(f"Test 2 (diverged): {report2.summary()}")
    # Node_Y is still at initial state — hashes will differ
    assert report2.system_should_halt, "Should have detected divergence/partial"

    print("\n✓ distributed_invariant_check.py — All self-tests passed.")
