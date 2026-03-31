import sys
import os
import json
import logging

sys.path.insert(0, os.path.dirname(__file__))

# Import Distributed Foundations
from computation_protocol import (
    ComputationProtocolHub, 
    ProtocolNode, 
    ProposalMessage,
    SequencedEvent,
    AckMessage
)

# Import Sankalp Intelligence Layer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sankalps_intelli_layer", "AI-BEING-main", "AI-BEING-main"))
from sankalp.engine import ResponseComposerEngine
from sankalp.schemas import IntelligenceInput

# Suppress Sankalp's default file logging during our state checks, or reroute it.
# Actually, let's leave default behavior to see if it causes I/O collision or just messy logs.
# logging.getLogger().setLevel(logging.CRITICAL)

class SankalpEnabledNode(ProtocolNode):
    """
    Overriding ProtocolNode to also run an Intelligence/Response layer on incoming events.
    """
    def __init__(self, node_id: str, initial_amplitudes: dict):
        super().__init__(node_id, initial_amplitudes)
        self.sankalp_engine = ResponseComposerEngine()
        self.last_sankalp_response = None

    def execute_sequenced_event(self, event: SequencedEvent) -> AckMessage:
        if event.step_type == "SANKALP_QUERY":
            # 1. Skip quantum evolution since this is just an intelligence query
            # However, we must increment causality track to stay aligned with the Hub
            self.next_expected_causal_id = event.causal_id + 1
            payload = event.payload
            
            sankalp_input = IntelligenceInput(
                behavioral_state=payload.get("behavioral_state", "curious"),
                speech_mode="chat",
                constraints=payload.get("constraints", []),
                confidence=payload.get("confidence", 0.9),
                age_gate_status=payload.get("age_gate_status", "adult"),
                region_gate_status="US",
                karma_hint=payload.get("karma_hint", "positive"),
                context_summary="Distributed event evaluation",
                message_content=payload.get("message_content", "Hello")
            )
            
            # Execute Sankalp Intelligence
            response = self.sankalp_engine.process(sankalp_input)
            self.last_sankalp_response = response.to_dict()
            
            # Re-hash state with Sankalp output
            return AckMessage(
                causal_id=event.causal_id,
                proposal_id=event.proposal_id,
                node_id=self.node_id,
                state_hash=self.get_state_hash(), # Includes sankalp state now
                ack_type="APPLIED"
            )
            
        return super().execute_sequenced_event(event)

    def get_state_hash(self) -> str:
        """
        We must include Sankalp's state output in the consensus hash to verify deterministic safety!
        """
        base_hash = super().get_state_hash()
        
        import hashlib
        h = hashlib.sha256(base_hash.encode('utf-8'))
        
        if self.last_sankalp_response:
            # Hash the raw payload to see if nodes diverge on non-deterministic fields
            resp_str = json.dumps(self.last_sankalp_response, sort_keys=True)
            h.update(resp_str.encode('utf-8'))
            
        return h.hexdigest()


def test_sankalp_distributed_safety():
    print("=== Testing Sankalp Integration in Distributed Environment ===\\n")
    
    hub = ComputationProtocolHub(halt_on_rejection=True, halt_on_divergence=True)
    
    # 1. Register Nodes
    nodes = []
    initial_amps = {"0": complex(1.0, 0.0), "1": complex(0.0, 0.0)}
    for name in ["Node_A", "Node_B", "Node_C"]:
        n = SankalpEnabledNode(name, initial_amps)
        hub.register_node(n)
        nodes.append(n)
        
    print(f"Registered {len(nodes)} Sankalp-Enabled Nodes.")
    
    # 2. Emit a Sankalp Query via Hub
    # Create an arbitrary proposal, hijacking step_type
    proposal = ProposalMessage(
        proposal_id="test_query_001",
        origin_node="Node_A",
        step_type="SANKALP_QUERY",
        payload={
            "behavioral_state": "sad",
            "message_content": "I am feeling lonely",
            "confidence": 0.85
        },
        proposed_at=0.0
    )
    
    print("Submitting SANKALP_QUERY to the protocol hub...")
    hub.submit(proposal)
    
    # 3. Check Consensus
    # The hub checks if `get_state_hash()` is identical across Node A, B, and C.
    print("Testing consensus across distributed intelligence queries...")
    sync_prop = ProposalMessage.sync("Node_A")
    hub.submit(sync_prop)
    
    consensus_res = hub.check_full_consensus()
    if consensus_res["consensus"]:
         print("[OK] SUCCESS: Sankalp layer executes safely deterministically across nodes!")
         print(f"Consensus Hash: {consensus_res['unique_hashes'][0]}")
    else:
         print("[!] VULNERABILITY FOUND: Sankalp layer broke deterministic consensus!")
         for n in nodes:
             print(f"  {n.node_id} Hash: {n.get_state_hash()}")
             
    if hub.is_halted:
         print(f"HUB HALTED: {hub.halt_reason}")

if __name__ == "__main__":
    test_sankalp_distributed_safety()
