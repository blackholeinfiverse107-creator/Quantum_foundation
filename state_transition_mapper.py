import uuid
import time
from typing import Dict
from computation_protocol import ProtocolNode, ProposalMessage, SequencedEvent, AckMessage
from marine_state_engine import MarineStateEngine
from marine_state_schema import ZoneState

class MarineProtocolNode(ProtocolNode):
    """
    A ProtocolNode augmented with a MarineStateEngine.
    It extends the sealed quantum architecture by intercepting MARINE_UPDATE events
    while enforcing the same sequential causality and hash consensus checks.
    """
    def __init__(self, node_id: str, initial_amplitudes: dict, initial_marine_state: Dict[str, ZoneState]):
        super().__init__(node_id, initial_amplitudes)
        self.marine_engine = MarineStateEngine(initial_marine_state)

    def execute_sequenced_event(self, event: SequencedEvent) -> AckMessage:
        if event.step_type == "MARINE_UPDATE":
            # Deterministic timeline enforcement
            if event.causal_id < self.next_expected_causal_id:
                # Old or dup event
                return AckMessage(
                    causal_id=event.causal_id,
                    proposal_id=event.proposal_id,
                    node_id=self.node_id,
                    state_hash=self.get_state_hash(),
                    ack_type="BUFFERED" # Actually APPLIED before but this is late arrival handling
                )
                
            self.next_expected_causal_id = event.causal_id + 1
            payload = event.payload
            
            try:
                # payload shape: {"zone_1": {"corrosion_rate": 0.01}, "zone_2": {...}}
                for zone_id, delta in payload.items():
                    self.marine_engine.apply_transition(zone_id, delta)

                ack = AckMessage(
                    causal_id=event.causal_id,
                    proposal_id=event.proposal_id,
                    node_id=self.node_id,
                    state_hash=self.get_state_hash(),
                    ack_type="APPLIED"
                )
            except Exception as e:
                ack = AckMessage(
                    causal_id=event.causal_id,
                    proposal_id=event.proposal_id,
                    node_id=self.node_id,
                    state_hash="",
                    ack_type="REJECTED",
                    error=str(e)
                )
            
            self._ack_log.append(ack)
            return ack
            
        # Fallback to pure deterministic quantum states for other events
        return super().execute_sequenced_event(event)

    def get_state_hash(self) -> str:
        """
        Combine core foundation hash with marine physical hash ensuring that ANY 
        divergence in EITHER layer flags a protocol halt.
        """
        base_hash = super().get_state_hash()
        marine_hash = self.marine_engine.hash()
        
        import hashlib
        h = hashlib.sha256(base_hash.encode('utf-8'))
        h.update(marine_hash.encode('utf-8'))
        return h.hexdigest()

def create_marine_update_proposal(origin_node: str, updates: Dict[str, dict]) -> ProposalMessage:
    """
    Transforms Dhiraj's format into an event-sourcing Proposal.
    """
    return ProposalMessage(
        proposal_id=str(uuid.uuid4()),
        origin_node=origin_node,
        step_type="MARINE_UPDATE",
        payload=updates,
        proposed_at=time.monotonic()
    )
