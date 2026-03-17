import sys
import os
import math
import io
from typing import List, Dict
from distributed_state_node import DistributedStateNode, NetworkEvent

# Global capture buffer
output_buffer = io.StringIO()

def log(msg):
    print(msg)
    output_buffer.write(str(msg) + "\n")

class NetworkHub:
    """
    Simulates a central network that sequences events and broadcasts them 
    to all connected nodes.
    """
    def __init__(self):
        self.nodes: List[DistributedStateNode] = []
        self.global_causal_id = 1
        self.event_log: List[NetworkEvent] = []

    def register_node(self, node: DistributedStateNode):
        self.nodes.append(node)

    def broadcast(self, raw_event: NetworkEvent):
        """Sequences and broadcasts an event to all nodes."""
        # Assign global causal id
        sequenced_event = NetworkEvent(
            causal_id=self.global_causal_id,
            origin_node_id=raw_event.origin_node_id,
            event_type=raw_event.event_type,
            payload=raw_event.payload
        )
        self.global_causal_id += 1
        self.event_log.append(sequenced_event)

        # In a real network, this would be asynchronous and might involve delays.
        # Here we deliver to all nodes immediately.
        for node in self.nodes:
            node.receive_event(sequenced_event)

def run_simulation():
    log("Starting Multi-Node Quantum Foundation Simulation...")
    
    # Initial state: |0>
    initial_amps = {"0": 1.0, "1": 0.0}
    
    hub = NetworkHub()
    
    # Phase 3.2: Instantiate Nodes A, B, C
    node_a = DistributedStateNode("Node_A", initial_amps)
    node_b = DistributedStateNode("Node_B", initial_amps)
    node_c = DistributedStateNode("Node_C", initial_amps)
    
    hub.register_node(node_a)
    hub.register_node(node_b)
    hub.register_node(node_c)

    # Define operations on all nodes (local setup)
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {
        ("0", "0"): inv_sq2, ("0", "1"): inv_sq2,
        ("1", "0"): inv_sq2, ("1", "1"): -inv_sq2
    }
    x_matrix = {
        ("0", "0"): 0.0, ("0", "1"): 1.0,
        ("1", "0"): 1.0, ("1", "1"): 0.0
    }

    for node in [node_a, node_b, node_c]:
        node.harness.define_unitary_operation("H", h_matrix, "Hadamard")
        node.harness.define_unitary_operation("X", x_matrix, "Pauli-X")

    # Phase 3.3: Propagate evolution events
    log("Broadcasting events from multiple nodes...")
    
    # Node A proposes H
    e1 = node_a.propose_evolution("H")
    hub.broadcast(e1)
    
    # Node B proposes X
    e2 = node_b.propose_evolution("X")
    hub.broadcast(e2)
    
    # Node C proposes H
    e3 = node_c.propose_evolution("H")
    hub.broadcast(e3)

    # Phase 4.1: Trigger measurement on Node A
    seed = 42
    log(f"Triggering measurement on Node A (Seed={seed})...")
    m1 = node_a.propose_measurement("m1", seed)
    hub.broadcast(m1)

    # Phase 3.5 / 4.4: Validate consistency
    log("\nVerifying Node Consistency:")
    hashes = {
        "Node_A": node_a.get_state_hash(),
        "Node_B": node_b.get_state_hash(),
        "Node_C": node_c.get_state_hash()
    }
    
    for name, h in hashes.items():
        log(f"{name} State Hash: {h[:16]}...")

    if len(set(hashes.values())) == 1:
        log("\nSUCCESS: All nodes arrived at the exact same state hash.")
    else:
        log("\nFAILURE: State divergence detected among nodes!")
        # Write failures to file before exit
        with open("sim_results.txt", "w") as f:
            f.write(output_buffer.getvalue())
        sys.exit(1)

    # Final Invariant Check
    log("Verifying structural invariants on all nodes...")
    for node in [node_a, node_b, node_c]:
        report = node.verify_node_integrity()
        for cycle, res in report.items():
            if res["failed"]:
                log(f"Invariant Failure on {node.node_id} in {cycle}: {res['failed']}")
                with open("sim_results.txt", "w") as f:
                    f.write(output_buffer.getvalue())
                sys.exit(1)
    
    log("ALL INVARIANTS PASSED ON ALL NODES.")
    log("Simulation Complete.")

    # Write the buffer to a file
    with open("sim_results.txt", "w") as f:
        f.write(output_buffer.getvalue())

if __name__ == "__main__":
    run_simulation()
