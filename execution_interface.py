import sys
import os
import time
import uuid
import asyncioclick  # just to avoid missing dependency if they don't have it initialized, but let's assume fastapi is available
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))
from computation_protocol import ComputationProtocolHub, ProposalMessage
from marine_state_schema import ZoneState
from state_transition_mapper import MarineProtocolNode, create_marine_update_proposal

# 1. Global deterministic state initialization
app = FastAPI(title="Marine Intelligence System Execution API")
hub = ComputationProtocolHub(halt_on_rejection=True, halt_on_divergence=True)

# Register nodes across 3 logical geographical sectors
_initial_amps = {"0": complex(1.0, 0.0), "1": complex(0.0, 0.0)}
_initial_zones = {
    "zone_1": ZoneState(0.1, 5.0, 0.0, 1.0, 0.05),
    "zone_2": ZoneState(0.2, 4.8, 1.2, 0.9, 0.08)
}

nodes = []
for name in ["Sector_A", "Sector_B", "Sector_C"]:
    n = MarineProtocolNode(name, _initial_amps, _initial_zones)
    hub.register_node(n)
    nodes.append(n)

# 2. Pydantic Schemas for the API
class ZoneUpdatePayload(BaseModel):
    corrosion_rate: float = 0.0
    coating_thickness: float = 0.0
    barnacle_density: float = 0.0
    oxygen_level: float = 0.0
    surface_roughness: float = 0.0

class MultiZoneUpdate(BaseModel):
    origin: str = "ExternalSimulationNode"
    zones: Dict[str, ZoneUpdatePayload]

# 3. Routes
@app.post("/simulate")
def submit_simulation_update(payload: MultiZoneUpdate):
    """
    Accepts simulation output (e.g. from Dhiraj's Layer) and pushes it into 
    the deterministic timeline of the Quantum protocol hub.
    """
    if hub.is_halted:
        raise HTTPException(status_code=500, detail=f"Hub is halted: {hub.halt_reason}")

    # Convert to formal dict for the engine payload
    zone_dict = {
        z_id: z_data.dict(exclude_unset=True) 
        for z_id, z_data in payload.zones.items()
    }

    # Transform to Proposal
    prop = create_marine_update_proposal(payload.origin, zone_dict)
    
    # Sequence and Commit Event
    receipt = hub.submit(prop)
    
    if receipt.any_rejected:
        raise HTTPException(status_code=400, detail="Update rejected by one or more deterministic nodes.")
        
    return {
        "status": "applied",
        "causal_id": receipt.sequenced_event.causal_id,
        "nodes_agreed": len(receipt.acks),
        "execution_complete": receipt.execution_complete
    }

@app.get("/state/{zone_id}")
def get_zone_state(zone_id: str):
    """
    Returns the physical deterministic state of the zone according to Node 0 (Sector_A).
    In a fully synchronized system, any node holds the valid state.
    """
    marine_engine = nodes[0].marine_engine
    zone = marine_engine.get_zone(zone_id)
    if not zone:
         raise HTTPException(status_code=404, detail="Zone not found.")
    return zone.to_dict()

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
    # Optional execution entry
    uvicorn.run(app, host="0.0.0.0", port=8000)
