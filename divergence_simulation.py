"""
divergence_simulation.py
=========================
Phase 4 — Controlled Divergence Simulation

Simulates three failure scenarios without breaking system guarantees:
  Scenario A: Node A is delayed (receives events late)
  Scenario B: Node B is missing an event entirely
  Scenario C: Node C receives events out-of-order

For each scenario:
  - The divergence is detected (not silently swallowed)
  - The system does not crash or corrupt state
  - Recovery path is documented (reconciliation handled in Phase 5)

No Cycle 1–8 core logic is modified.
"""

import math
import sys
import os
import time
from dataclasses import dataclass
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(__file__))
from computation_protocol import (
    ComputationProtocolHub,
    ProtocolNode,
    ProposalMessage,
    SequencedEvent,
    SyncReport,
    ExecutionReceipt
)
from distributed_state_node import NetworkEvent


# ---------------------------------------------------------------------------
# DivergenceReport data structure
# ---------------------------------------------------------------------------

@dataclass
class ScenarioDivergenceResult:
    scenario_name: str
    description: str
    diverged: bool
    diverged_nodes: List[str]
    partial_nodes: List[str]
    node_hashes: Dict[str, str]       # {node_id: hash}
    node_committed_ids: Dict[str, int] # {node_id: last_applied_causal_id}
    system_halted: bool
    halt_reason: Optional[str]
    notes: str


# ---------------------------------------------------------------------------
# Shared setup helper
# ---------------------------------------------------------------------------

def _build_nodes_and_hub(halt_on_divergence=False):
    """Create 3 fresh ProtocolNodes with H and X operators, registered to a Hub."""
    initial_amps = {"0": complex(1.0, 0.0), "1": complex(0.0, 0.0)}
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {
        ("0", "0"): inv_sq2, ("0", "1"): inv_sq2,
        ("1", "0"): inv_sq2, ("1", "1"): -inv_sq2
    }
    x_matrix = {
        ("0", "0"): 0.0, ("0", "1"): 1.0,
        ("1", "0"): 1.0, ("1", "1"): 0.0
    }

    hub = ComputationProtocolHub(
        halt_on_rejection=True,
        halt_on_divergence=halt_on_divergence
    )
    nodes = {}
    for name in ["Node_A", "Node_B", "Node_C"]:
        n = ProtocolNode(name, initial_amps)
        n.harness.define_unitary_operation("H", h_matrix, "Hadamard")
        n.harness.define_unitary_operation("X", x_matrix, "Pauli-X")
        hub.register_node(n)
        nodes[name] = n

    return hub, nodes


# ---------------------------------------------------------------------------
# Scenario A: Node A Delayed
# ---------------------------------------------------------------------------

def simulate_scenario_a_delayed_node() -> ScenarioDivergenceResult:
    """
    Scenario A: Node A is delayed.
    Events 1 and 2 are held from Node A; B and C receive them normally.
    At SYNC point, Node A is behind — divergence detected.
    System does not crash; Node A's state is still coherent at its own level.
    """
    hub, nodes = _build_nodes_and_hub(halt_on_divergence=False)
    node_a = nodes["Node_A"]

    # Event 1: H — delivered to B and C immediately, held from A
    p1 = nodes["Node_B"].propose_evolve("H")
    hub.submit(p1, delay_nodes=["Node_A"])

    # Event 2: X — same
    p2 = nodes["Node_C"].propose_evolve("X")
    hub.submit(p2, delay_nodes=["Node_A"])

    # Event 3: SYNC — only B and C participate
    p_sync = nodes["Node_B"].propose_sync()
    r_sync = hub.submit(p_sync, exclude_nodes=["Node_A"])

    sync_report = r_sync.sync_report
    diverged = not sync_report.consensus

    # Node status at divergence point
    node_hashes = {n.node_id: n.get_state_hash() for n in nodes.values()}
    committed_ids = {n.node_id: n.committed_causal_id for n in nodes.values()}
    partial_nodes = [n.node_id for n in nodes.values() if n.is_partial or n.committed_causal_id < 2]

    return ScenarioDivergenceResult(
        scenario_name="A — Delayed Node",
        description="Node A does not receive events 1 and 2. B and C advance. "
                    "SYNC detects Node A is behind (hash mismatch at same causal slot).",
        diverged=node_a.get_state_hash() != nodes["Node_B"].get_state_hash(),
        diverged_nodes=["Node_A"],
        partial_nodes=partial_nodes,
        node_hashes=node_hashes,
        node_committed_ids=committed_ids,
        system_halted=hub.is_halted,
        halt_reason=hub.halt_reason,
        notes="Node A state is intact at causal_id=0 (initial). "
              "Recovery: release held events → Node A catches up."
    )


# ---------------------------------------------------------------------------
# Scenario B: Node B Missing Event
# ---------------------------------------------------------------------------

def simulate_scenario_b_missing_event() -> ScenarioDivergenceResult:
    """
    Scenario B: Node B never receives event 2 (it was dropped).
    Node B processes event 1 and event 3, but event 3 is buffered because
    causal_id=2 is missing. Divergence is structural: B is stuck.
    """
    hub, nodes = _build_nodes_and_hub(halt_on_divergence=False)
    node_b = nodes["Node_B"]

    # Event 1: H — delivered to all
    p1 = nodes["Node_A"].propose_evolve("H")
    hub.submit(p1)

    # Event 2: X — excluded from Node B (permanently missing)
    p2 = nodes["Node_A"].propose_evolve("X")
    hub.submit(p2, exclude_nodes=["Node_B"])

    # Event 3: H — delivered to all (Node B buffers it, missing causal_id=2)
    p3 = nodes["Node_C"].propose_evolve("H")
    hub.submit(p3)

    # SYNC step — Node B will report stale hash
    p_sync = nodes["Node_A"].propose_sync()
    r_sync = hub.submit(p_sync)

    node_hashes = {n.node_id: n.get_state_hash() for n in nodes.values()}
    committed_ids = {n.node_id: n.committed_causal_id for n in nodes.values()}
    partial_nodes = [n.node_id for n in nodes.values() if n.is_partial]

    diverged = len(set(node_hashes.values())) > 1

    return ScenarioDivergenceResult(
        scenario_name="B — Missing Event",
        description="Node B never receives causal_id=2 (X gate). "
                    "It processes causal_id=1 but buffers causal_id=3, waiting. "
                    "SYNC detects Node B is behind — hash mismatch.",
        diverged=diverged,
        diverged_nodes=["Node_B"] if diverged else [],
        partial_nodes=partial_nodes,
        node_hashes=node_hashes,
        node_committed_ids=committed_ids,
        system_halted=hub.is_halted,
        halt_reason=hub.halt_reason,
        notes="Node B has causal_id=3 buffered, blocked on causal_id=2. "
              "Recovery: Hub replays causal_id=2 to Node B → buffer flushes."
    )


# ---------------------------------------------------------------------------
# Scenario C: Node C Out-of-Order Delivery
# ---------------------------------------------------------------------------

def simulate_scenario_c_out_of_order() -> ScenarioDivergenceResult:
    """
    Scenario C: Node C receives causal_id=3 before causal_id=2.
    Node C buffers causal_id=3, applies causal_id=2 when it arrives.
    Eventually it catches up deterministically — no permanent divergence.
    """
    hub, nodes = _build_nodes_and_hub(halt_on_divergence=False)
    node_c = nodes["Node_C"]

    # Event 1: H — all nodes receive
    p1 = nodes["Node_A"].propose_evolve("H")
    hub.submit(p1)

    # Event 2: X — delayed to Node C (will arrive later)
    p2 = nodes["Node_B"].propose_evolve("X")
    hub.submit(p2, delay_nodes=["Node_C"])

    # Event 3: H — delivered to Node C before event 2 arrives (out-of-order)
    p3 = nodes["Node_A"].propose_evolve("H")
    hub.submit(p3)  # Node C receives this, but buffers it (causal_id=2 missing)

    # Check status: C should be partial
    c_partial_before = node_c.is_partial
    c_pending_before = list(node_c.pending_causal_ids)
    c_committed_before = node_c.committed_causal_id

    # Now release event 2 to Node C — buffer should flush
    hub.release_held_events("Node_C")

    c_partial_after = node_c.is_partial
    c_committed_after = node_c.committed_causal_id

    # SYNC
    p_sync = nodes["Node_A"].propose_sync()
    r_sync = hub.submit(p_sync)
    sync = r_sync.sync_report

    node_hashes = {n.node_id: n.get_state_hash() for n in nodes.values()}
    committed_ids = {n.node_id: n.committed_causal_id for n in nodes.values()}
    partial_nodes = [n.node_id for n in nodes.values() if n.is_partial]

    diverged = not sync.consensus

    return ScenarioDivergenceResult(
        scenario_name="C — Out-of-Order Delivery",
        description=f"Node C received causal_id=3 before causal_id=2. "
                    f"Before release: partial={c_partial_before}, "
                    f"pending={c_pending_before}, committed={c_committed_before}. "
                    f"After release: partial={c_partial_after}, committed={c_committed_after}.",
        diverged=diverged,
        diverged_nodes=sync.diverged_nodes if diverged else [],
        partial_nodes=partial_nodes,
        node_hashes=node_hashes,
        node_committed_ids=committed_ids,
        system_halted=hub.is_halted,
        halt_reason=hub.halt_reason,
        notes="Out-of-order delivery resolves automatically once the missing event arrives. "
              "No state corruption. No divergence after flush."
    )


# ---------------------------------------------------------------------------
# Run all scenarios and print report
# ---------------------------------------------------------------------------

def run_all_scenarios() -> List[ScenarioDivergenceResult]:
    results = []

    print("=" * 60)
    print("DIVERGENCE SIMULATION — Phase 4")
    print("=" * 60)

    for fn in [
        simulate_scenario_a_delayed_node,
        simulate_scenario_b_missing_event,
        simulate_scenario_c_out_of_order
    ]:
        result = fn()
        results.append(result)
        _print_result(result)

    return results


def _print_result(r: ScenarioDivergenceResult):
    print(f"\n--- Scenario {r.scenario_name} ---")
    print(f"Description : {r.description}")
    print(f"Diverged    : {r.diverged}")
    print(f"Diverged Nodes: {r.diverged_nodes}")
    print(f"Partial Nodes : {r.partial_nodes}")
    print(f"System Halted : {r.system_halted}")
    print("Node Hashes :")
    for nid, h in r.node_hashes.items():
        cid = r.node_committed_ids.get(nid, "?")
        print(f"  {nid}: hash={h[:16]}... committed_up_to={cid}")
    print(f"Notes       : {r.notes}")


if __name__ == "__main__":
    results = run_all_scenarios()
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        status = "DIVERGED (detected)" if r.diverged else "STABLE"
        halted = " | HALTED" if r.system_halted else ""
        print(f"  Scenario {r.scenario_name}: {status}{halted}")

    print("\n✓ divergence_simulation.py complete — all scenarios executed.")
