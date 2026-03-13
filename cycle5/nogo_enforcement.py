"""
Cycle 5 — No-Go Enforcement Engine
==================================

An architectural guard layer that wraps the `QuantumFoundationSystem` 
(or its equivalent) to enforce the fundamental No-Go capabilities:
No-Cloning, No-Deleting, and No Confidence without Collapse.

Execution is not permitted here. This layer only inspects operations and 
intercepts forbidden interactions before they reach the core evolution engine.
"""

import uuid
from typing import Dict, Tuple

from cycle1.state_evolution_engine import SovereignStateEngine, StateVector, Observation
from cycle2.collapse_engine import CollapseEngine, CollapseToken, IrreversibleCollapseEvent
from cycle3.timeline import CausalTimeline, CausalEvent
from cycle4.error_model import ErrorModel, UnitaryNoise, MeasurementDisturbance
from cycle5.nogo_primitives import (
    NoCloningViolation, 
    NoDeletingViolation, 
    ConfidenceCollapseViolation, 
    StateReference
)


class NoGoEnforcementEngine:
    """
    Wraps all state interactions to guarantee fundamental physical limits.
    
    1. Single Timeline Constraint: The `StateReference` enforces linear 
       history. You cannot branch the timeline to run parallel evolutions 
       on the same unentangled state.
    2. Forced Measurement Disturbance: If you ask for the confidence of a 
       state, you MUST incur the corresponding decoherence/collapse.
    3. No State Destruction: States cannot be unconditionally deleted; 
       they must evolve unitarily or collapse into classical information.
    """
    def __init__(self, 
                 state_engine: SovereignStateEngine, 
                 collapse_engine: CollapseEngine, 
                 timeline: CausalTimeline,
                 error_model: ErrorModel):
        self.state_engine = state_engine
        self.collapse_engine = collapse_engine
        self.timeline = timeline
        self.error_model = error_model
        
        # Internal registry linking strict references to the underlying system
        self._active_references: Dict[str, StateReference] = {}
        
        # Start tracking the root state
        root_id = str(uuid.uuid4())
        self._root_ref = StateReference(root_id)
        self._active_references[root_id] = self._root_ref
        
        # We track how many times this specific state history has been evolved.
        # Forking history implies cloning, which is forbidden.
        self._expected_next_event_id: int = self.timeline.length + 1

    @property
    def root_reference(self) -> StateReference:
        return self._root_ref

    def evolve_strictly(
        self, 
        ref: StateReference, 
        observation: Observation, 
        noise_fidelity: float = 1.0
    ) -> Tuple[StateReference, CausalEvent]:
        """
        Evolve the state, returning the SAME reference (representing the 
        continuous singular physical state). 
        
        - If another piece of code tries to evolve using a cloned or old reference,
          we detect a timeline branching attempt and falsify it.
        """
        # Validate Reference
        if ref.reference_id not in self._active_references:
            raise NoDeletingViolation("Attempted to evolve an untracked or deleted physical state reference.")
            
        # Validate Linear History (No-Cloning Check)
        if self.timeline.length + 1 != self._expected_next_event_id:
            raise NoCloningViolation(
                "Timeline branching detected! The physical state history has been modified "
                "outside of the strict linear progression. Cloning an unknown state "
                "into a parallel universe is forbidden."
            )

        # 1. Ideal evolution
        delta = self.state_engine.observe(observation)
        
        # Simulate physical noise (if any)
        current_state = self.state_engine.current_state
        if noise_fidelity < 1.0:
            noise = UnitaryNoise(noise_fidelity)
            # Apply degraded fidelity representation (for the reference implementation)
            current_state = StateVector({k: v * noise_fidelity for k, v in current_state.amplitudes.items()})

        # 2. Record timeline event
        event = self.timeline.record(
            event_type="STRICT_EVOLUTION",
            payload={"observation": observation, "noise_fidelity": noise_fidelity}
        )
        
        # Advance expected history tracker
        self._expected_next_event_id = self.timeline.length + 1
        
        return ref, event

    def measure_strictly(
        self, 
        ref: StateReference, 
        token: CollapseToken, 
        seed: int
    ) -> Tuple[StateReference, IrreversibleCollapseEvent, CausalEvent]:
        """
        Measurement explicitly bounds classical confidence with state destruction.
        """
        if ref.reference_id not in self._active_references:
            raise NoDeletingViolation("Attempted to measure an untracked physical state.")
            
        # Collapse the state
        current_state = self.state_engine.current_state
        collapse_event = self.collapse_engine.collapse(current_state, token, seed)
        
        # Validate Confidence/Disturbance tradeoff
        confidence = collapse_event.result.confidence
        info_loss = collapse_event.result.information_loss_declared
        
        if confidence > 0.0 and info_loss == 0.0:
            # Re-verifying invariant physically at the boundary
            raise ConfidenceCollapseViolation()
            
        # Log unrecoverable error
        self.error_model.register_measurement_disturbance(info_loss)

        # Timeline
        causal_event = self.timeline.record(
            event_type="STRICT_COLLAPSE", 
            payload=collapse_event
        )
        self._expected_next_event_id = self.timeline.length + 1
        
        return ref, collapse_event, causal_event

    def check_independent_copy(self, ref_a: StateReference, ref_b: StateReference) -> None:
        """
        Adversarial test helper: Trying to create two independent physical 
        states from one reference without entanglement.
        """
        if ref_a.reference_id == ref_b.reference_id:
            raise NoCloningViolation(
                "You cannot pass the same physical state reference to two independent "
                "parallel evolutions. Linear types are strictly enforced."
            )
