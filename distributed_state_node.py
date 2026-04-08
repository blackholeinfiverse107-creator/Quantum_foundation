import sys
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import hashlib

@dataclass(frozen=True)
class ExecutionEvent:
    """represents a deterministic event propagate across the node network."""
    causal_id: int
    origin_node_id: str
    event_type: str
    payload: dict

class DistributedStateNode:
    """
    A domain-agnostic computation node that maintains state via an adapter
    and synchronizes with peers via deterministic ExecutionEvents.
    """
    def __init__(self, node_id: str, adapter: Any):
        self.node_id = node_id
        self.adapter = adapter
        self.next_expected_causal_id = 1
        self.event_buffer: Dict[int, ExecutionEvent] = {}
        self.local_log: List[ExecutionEvent] = []

    def receive_event(self, event: ExecutionEvent):
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

    def _apply_event(self, event: ExecutionEvent):
        """Executes the event by delegating strictly to the adapter."""
        self.adapter.apply_event_payload(event.payload)

    def verify_node_integrity(self) -> dict:
        """Runs local adapter invariants."""
        if hasattr(self.adapter, "verify_all_invariants"):
            return self.adapter.verify_all_invariants()
        return {"Adapter_Invariants": {"passed": [], "failed": []}}

    def get_state_hash(self) -> str:
        """Returns a deterministic hash of the adapter's current state."""
        return self.adapter.get_state_hash()
