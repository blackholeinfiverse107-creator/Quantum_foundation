"""
Cycle 9 - Node Network Simulation
====================================

Instantiates a 3-node deterministic quantum network (Node A, B, C).
Demonstrates:
  1. Shared initial state across all nodes
  2. Evolution event propagation (one node evolves, all nodes receive)
  3. Measurement collapse broadcast (one node measures, all nodes collapse)
  4. Causal timeline synchronisation
  5. Deterministic state convergence verification

Architecture:
  NodeNetwork acts as the message bus. It holds references to all nodes
  and routes NetworkEvents from the originating node to all peers.
  The bus is synchronous and ordered -- no concurrency, no reordering.

  NodeA --evolve--> bus --> NodeB.receive_event()
                        --> NodeC.receive_event()

  NodeA --measure-> bus --> NodeB.receive_event()
                        --> NodeC.receive_event()
"""

from __future__ import annotations

import sys
import os
import math
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cycle9.distributed_state_node import DistributedStateNode, NetworkEvent


# ---------------------------------------------------------------------------
# Node Network -- synchronous message bus
# ---------------------------------------------------------------------------

class NodeNetwork:
    """
    A synchronous, ordered message bus connecting DistributedStateNodes.

    Responsibilities:
      - Register nodes
      - Route NetworkEvents from origin to all peers (not back to origin)
      - Maintain a global ordered event log for replay validation
      - Enforce no duplicate delivery

    This is NOT a real network -- it is a deterministic simulation harness.
    All delivery is synchronous and in-order.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, DistributedStateNode] = {}
        self._global_event_log: List[NetworkEvent] = []

    def register_node(self, node: DistributedStateNode) -> None:
        """Register a node and wire its broadcast callback to this bus."""
        if node.node_id in self._nodes:
            raise ValueError(f"Node '{node.node_id}' already registered.")
        self._nodes[node.node_id] = node
        node._broadcast = self._route

    def _route(self, net_event: NetworkEvent) -> None:
        """Deliver a NetworkEvent to all nodes except the origin."""
        self._global_event_log.append(net_event)
        for node_id, node in self._nodes.items():
            if node_id != net_event.origin_node:
                node.receive_event(net_event)

    @property
    def global_event_log(self) -> tuple:
        return tuple(self._global_event_log)

    def verify_state_convergence(self) -> bool:
        """
        Assert all nodes have identical state hashes.
        Raises AssertionError on divergence.
        """
        hashes = {nid: node.state_hash() for nid, node in self._nodes.items()}
        unique = set(hashes.values())
        if len(unique) != 1:
            raise AssertionError(
                "STATE DIVERGENCE DETECTED across nodes:\n"
                + "\n".join(f"  {nid}: {h}" for nid, h in hashes.items())
            )
        return True

    def verify_causal_ordering(self) -> bool:
        """Assert all nodes' local timelines pass causal ordering verification."""
        for node_id, node in self._nodes.items():
            node._harness.system.timeline.verify_ordering()
        return True


# ---------------------------------------------------------------------------
# Standard network setup helper
# ---------------------------------------------------------------------------

def build_standard_network(initial_amplitudes: dict) -> tuple:
    """
    Instantiate Node A, B, C with identical initial state.
    Register the Hadamard and Pauli-X gates on all nodes.
    Wire all nodes into a NodeNetwork.

    Returns (network, node_a, node_b, node_c).
    """
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {
        ("0", "0"): inv_sq2,  ("0", "1"): inv_sq2,
        ("1", "0"): inv_sq2,  ("1", "1"): -inv_sq2,
    }
    x_matrix = {
        ("0", "0"): 0.0, ("0", "1"): 1.0,
        ("1", "0"): 1.0, ("1", "1"): 0.0,
    }

    nodes = []
    for name in ("A", "B", "C"):
        n = DistributedStateNode(f"Node{name}", initial_amplitudes)
        n.observe("H", h_matrix, "Hadamard Gate")
        n.observe("X", x_matrix, "Pauli-X Gate")
        n.activate()
        nodes.append(n)

    node_a, node_b, node_c = nodes
    network = NodeNetwork()
    for n in nodes:
        network.register_node(n)

    return network, node_a, node_b, node_c


# ---------------------------------------------------------------------------
# Simulation scenarios
# ---------------------------------------------------------------------------

def run_evolution_propagation_scenario(network, node_a, node_b, node_c) -> None:
    """
    Scenario 1: Node A evolves; B and C receive and apply the same evolution.
    Validates state convergence after propagation.
    """
    print("\n[Scenario 1] Evolution Propagation")
    node_a.evolve("H")
    network.verify_state_convergence()
    print("  NodeA evolved H -> B and C converged. PASS")

    node_a.evolve("X")
    network.verify_state_convergence()
    print("  NodeA evolved X -> B and C converged. PASS")


def run_measurement_broadcast_scenario(network, node_a, node_b, node_c) -> None:
    """
    Scenario 2: Node B triggers measurement; all nodes collapse consistently.
    Validates post-collapse state equality and causal ordering.
    """
    print("\n[Scenario 2] Measurement Broadcast")
    net_event, collapse_event = node_b.measure("m_net_1", seed=42)
    network.verify_state_convergence()
    network.verify_causal_ordering()
    outcome = collapse_event.result.outcome
    print(f"  NodeB measured -> outcome='{outcome}' -> all nodes collapsed consistently. PASS")


def run_causal_ordering_scenario(network, node_a, node_b, node_c) -> None:
    """
    Scenario 3: Multiple sequential evolutions from different nodes.
    Validates that causal ordering is maintained across all timelines.
    """
    print("\n[Scenario 3] Causal Ordering - Multi-node Sequential Evolution")
    node_c.evolve("H")
    node_a.evolve("H")
    node_b.evolve("X")
    network.verify_causal_ordering()
    network.verify_state_convergence()
    print("  Multi-node sequential evolution -> causal ordering preserved. PASS")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Distributed Quantum Node Network Simulation")
    print("Nodes: A, B, C | Initial state: |0>")
    print("=" * 60)

    initial = {"0": complex(1.0), "1": complex(0.0)}
    network, node_a, node_b, node_c = build_standard_network(initial)

    run_evolution_propagation_scenario(network, node_a, node_b, node_c)
    run_measurement_broadcast_scenario(network, node_a, node_b, node_c)

    # Re-build for scenario 3 (post-collapse state is already collapsed)
    network2, na2, nb2, nc2 = build_standard_network(initial)
    run_causal_ordering_scenario(network2, na2, nb2, nc2)

    print("\n" + "=" * 60)
    print("ALL NETWORK SIMULATION SCENARIOS PASSED.")
    print(f"Global event log length: {len(network.global_event_log)} events")
    print("=" * 60)
