import sys
import os
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))
from computation_protocol import ComputationProtocolHub, ProposalMessage, ProtocolNode

# We import the marine adapter to act as our execution layer for demonstration/staging.
# In a true domain-agnostic setup, this adapter injection would be configuration-driven.
from adapters.marine.marine_adapter import MarineStateEngine, ZoneState, create_marine_update_event

app = FastAPI(title="BHIV Deterministic Execution Interface")
hub = ComputationProtocolHub(halt_on_rejection=True, halt_on_divergence=True)

# 1. Initialize Distributed Nodes (Bootstrapped with Marine Adapter)
_initial_zones = {
    "BOW_PORT": ZoneState(0.12, 1.05, 35.0, 0.05, 0.02),
    "MID_KEEL": ZoneState(0.24, 0.90, 42.5, 0.15, 0.10)
}

nodes = []
for name in ["Sector_A", "Sector_B", "Sector_C"]:
    engine_adapter = MarineStateEngine(_initial_zones)
    # The ProtocolNode now takes ANY generic adapter
    n = ProtocolNode(name, adapter=engine_adapter)
    hub.register_node(n)
    nodes.append(n)

# 2. Pydantic Schemas for Generic Execution API
class ExecuteRequest(BaseModel):
    event_type: str
    origin: str = "ExternalSimulationNode"
    payload: Dict[str, Any]

# 3. Routes
@app.post("/execute")
def execute_event(req: ExecuteRequest):
    """
    Accepts arbitrary structured events and applies them strictly across the distributed sequence.
    """
    if hub.is_halted:
        raise HTTPException(status_code=500, detail=f"Hub is halted: {hub.halt_reason}")

    # Generate the proposal to insert into the sequenced protocol
    # In a real environment, the adapter might pre-process `req.payload` depending on event_type.
    prop = ProposalMessage.create(req.origin, req.event_type, req.payload)
    
    # 4. Engine executes and enforces causality
    receipt = hub.submit(prop)
    
    if receipt.any_rejected:
        # Halt or feedback immediately
        raise HTTPException(status_code=400, detail="Update rejected by one or more covariant nodes. Divergence prevented.")
        
    return {
        "status": "applied",
        "causal_id": receipt.sequenced_event.causal_id,
        "state_hash": nodes[0].get_state_hash(),
        "consensus": True if hub.check_full_consensus()["consensus"] else False
    }

@app.get("/metrics")
def get_hub_metrics():
    """
    Diagnostic metrics reflecting the state of deterministic replay.
    """
    sync_check = hub.check_full_consensus()
    return {
        "engine_causal_id": hub.next_causal_id - 1,
        "nodes_registered": len(nodes),
        "is_halted": hub.is_halted,
        "halt_reason": hub.halt_reason,
        "consensus_verified": sync_check["consensus"],
        "divergent_hashes": sync_check["unique_hashes"] if not sync_check["consensus"] else None,
        "global_state_hash": nodes[0].get_state_hash()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
