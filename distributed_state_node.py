import sys
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import hashlib

sys.path.insert(0, os.path.dirname(__file__))
from full_stack_integration_harness import FullStackHarness

@dataclass(frozen=True)
class NetworkEvent:
    """represents a deterministic event propagate across the node network."""
    causal_id: int
    origin_node_id: str
    event_type: str  # "EVOLVE" or "MEASURE"
    payload: dict    # {"rule_name": str} or {"token_id": str, "seed": int}

class DistributedStateNode:
    """
    A computation node that maintains a local FullStackHarness and synchronizes
    with peers via deterministic network events.
    """
    def __init__(self, node_id: str, initial_amplitudes: Dict[str, complex]):
        self.node_id = node_id
        self.harness = FullStackHarness(initial_amplitudes)
        self.next_expected_causal_id = 1
        self.event_buffer: Dict[int, NetworkEvent] = {}
        self.local_log: List[NetworkEvent] = []

    def observe(self) -> Dict[str, complex]:
        """Provides a read-only view of the current local state amplitudes."""
        # Accessing the state from the system's state engine
        return self.harness.system.state_engine.current_state.as_dict()

    def propose_evolution(self, rule_name: str) -> NetworkEvent:
        """Proposes a unitary evolution to be broadcast to the network."""
        # Note: In a real network, the causal_id would be assigned by a sequencer
        # or consensus mechanism. For this prototype, we'll assume the caller
        # or simulation harness provides it.
        return NetworkEvent(
            causal_id=-1, # Placeholder
            origin_node_id=self.node_id,
            event_type="EVOLVE",
            payload={"rule_name": rule_name}
        )

    def propose_measurement(self, token_id: str, seed: int) -> NetworkEvent:
        """Proposes a measurement collapse to be broadcast."""
        return NetworkEvent(
            causal_id=-1, # Placeholder
            origin_node_id=self.node_id,
            event_type="MEASURE",
            payload={"token_id": token_id, "seed": seed}
        )

    def receive_event(self, event: NetworkEvent):
        """
        Receives an event from the network. Buffers if out of order, 
        or applies if it matches the next expected causal_id.
        """
        if event.causal_id < self.next_expected_causal_id:
            # Duplicate or old event, ignore but log
            return

        self.event_buffer[event.causal_id] = event
        self._process_buffer()

    def _process_buffer(self):
        """Applies buffered events in strict causal order."""
        while self.next_expected_causal_id in self.event_buffer:
            event = self.event_buffer.pop(self.next_expected_causal_id)
            self._apply_event(event)
            self.local_log.append(event)
            self.next_expected_causal_id += 1

    def _apply_event(self, event: NetworkEvent):
        """Executes the event on the local harness."""
        if event.event_type == "EVOLVE":
            rule_name = event.payload["rule_name"]
            self.harness.evolve_deterministic(rule_name)
        elif event.event_type == "MEASURE":
            token_id = event.payload["token_id"]
            seed = event.payload["seed"]
            self.harness.measure_deterministic(token_id, seed)
        else:
            raise ValueError(f"Unknown event type: {event.event_type}")

    def verify_node_integrity(self) -> dict:
        """Runs local harness invariants."""
        return self.harness.verify_all_invariants()

    def get_state_hash(self) -> str:
        """Returns a deterministic hash of the current local state."""
        state = self.observe()
        h = hashlib.sha256()
        for k in sorted(state.keys()):
            val = state[k]
            val_str = f"({val.real:.8f}+{val.imag:.8f}j)"
            h.update(k.encode('utf-8'))
            h.update(val_str.encode('utf-8'))
        return h.hexdigest()
