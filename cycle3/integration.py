"""
Cycle 3 — Integration: All Three Layers Wired Together
=======================================================

This module proves the three cycles interlock without contradiction:

  1. Cycle 1: SovereignStateEngine produces StateDelta events
  2. Cycle 2: CollapseEngine produces IrreversibleCollapseEvent records
  3. Cycle 3: CausalTimeline records BOTH as ordered CausalEvents

Every state evolution and every measurement collapse becomes a point in the
unified causal history. The timeline provides global causal ordering.

This is not an orchestrator — it is a wiring adapter. Each engine retains
its own guarantees and invariants. The integration only adds causal ordering.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import Optional, Tuple

from cycle1.state_evolution_engine import (
    Observation,
    StateVector,
    SovereignStateEngine,
    StateDelta,
)
from cycle2.collapse_engine import (
    CollapseEngine,
    CollapseToken,
    IrreversibleCollapseEvent,
)
from cycle2.measurement_policy import MeasurementPolicy
from cycle3.causality_primitives import CausalEvent
from cycle3.timeline import CausalTimeline


class QuantumFoundationSystem:
    """
    The top-level integration object.

    Wires Cycle1 (state evolution) + Cycle2 (measurement collapse) +
    Cycle3 (causal timeline) into a coherent system.

    Every action produces a CausalEvent in the shared timeline.

    Prohibitions (inherited and reinforced):
      - No execution authority here
      - No hidden state — all state is in the three engines
      - No rollback — only compensation via timeline.compensate()
      - No measurement without a token
    """

    def __init__(
        self,
        initial_state: StateVector,
        name: str = "QuantumFoundationSystem",
    ) -> None:
        self.name = name
        self._state_engine = SovereignStateEngine(initial_state)
        self._collapse_engine = CollapseEngine()
        self._timeline = CausalTimeline()

        # Record genesis event
        self._timeline.record(
            event_type="GENESIS",
            payload={"system_name": name, "initial_state": repr(initial_state)},
        )

    # --- Cycle 1 Integration ---

    def register_transition_rule(self, obs_type: str, rule, description: str = "") -> None:
        """Register a TransitionRule in the state evolution engine."""
        self._state_engine.register_rule(obs_type, rule, description)

    def evolve(self, observation: Observation) -> Tuple[StateDelta, CausalEvent]:
        """
        Submit an observation to the state engine and record the resulting
        StateDelta in the causal timeline.

        Returns:
            (StateDelta, CausalEvent) — the evolution and its causal record
        """
        delta = self._state_engine.observe(observation)
        causal_event = self._timeline.record(
            event_type="STATE_DELTA",
            payload=delta,
        )
        return delta, causal_event

    # --- Cycle 2 Integration ---

    def register_measurement_policy(self, policy: MeasurementPolicy) -> None:
        """Register a MeasurementPolicy in the collapse engine."""
        self._collapse_engine.register_policy(policy)

    def issue_collapse_token(self, policy_name: str, token_id: str) -> CollapseToken:
        """Issue a single-use CollapseToken."""
        return self._collapse_engine.issue_token(policy_name, token_id)

    def measure(
        self,
        token: CollapseToken,
        seed: int,
    ) -> Tuple[IrreversibleCollapseEvent, CausalEvent]:
        """
        Perform a measurement collapse on the CURRENT state of the evolution engine.
        Records the collapse as a CausalEvent in the timeline.

        The post-collapse state is NOT automatically fed back into the state engine.
        That decision belongs to the caller (separation of authority).

        Returns:
            (IrreversibleCollapseEvent, CausalEvent)
        """
        current_state = self._state_engine.current_state
        collapse_event = self._collapse_engine.collapse(current_state, token, seed)
        causal_event = self._timeline.record(
            event_type="COLLAPSE",
            payload=collapse_event,
        )
        return collapse_event, causal_event

    # --- Cycle 3 Integration ---

    def seal_timeline(self, reason: str) -> None:
        """
        Place a PointOfNoReturn at the current timeline head.
        All prior events become permanently sealed.
        """
        if self._timeline.length == 0:
            raise ValueError("Cannot seal an empty timeline.")
        last_id = self._timeline.events[-1].causal_id
        self._timeline.seal(last_id, reason)

    def compensate(
        self,
        target_causal_id: int,
        compensation_payload: object,
        reason: str = "",
    ) -> CausalEvent:
        """
        Add a compensation event for a prior action.
        Compensation NEVER deletes or modifies prior events.
        """
        return self._timeline.compensate(target_causal_id, compensation_payload, reason)

    # --- Query Interface ---

    @property
    def current_state(self) -> StateVector:
        return self._state_engine.current_state

    @property
    def timeline(self) -> CausalTimeline:
        return self._timeline

    @property
    def state_engine(self) -> SovereignStateEngine:
        return self._state_engine

    @property
    def collapse_engine(self) -> CollapseEngine:
        return self._collapse_engine

    def verify_all_invariants(self) -> dict:
        """
        Run invariant checks across all three cycles.
        Returns a dict with keys 'cycle1', 'cycle2', 'cycle3', each with pass/fail info.
        """
        from cycle1.invariants import run_all_invariants as c1_check
        from cycle2.invariants import run_all_measurement_invariants
        from cycle2.measurement_policy import ProjectiveMeasurementPolicy

        c1_report = c1_check(self._state_engine)
        c2_report = run_all_measurement_invariants(
            self._collapse_engine, ProjectiveMeasurementPolicy()
        )

        # Cycle 3: verify timeline ordering
        c3_passed = []
        c3_failed = []
        try:
            self._timeline.verify_ordering()
            c3_passed.append("C3_ORDERING")
        except Exception as e:
            c3_failed.append(f"C3_ORDERING: {e}")

        return {
            "cycle1": {"passed": c1_report.passed, "failed": c1_report.failed},
            "cycle2": {"passed": c2_report.passed, "failed": c2_report.failed},
            "cycle3": {"passed": c3_passed, "failed": c3_failed},
        }

    def __repr__(self) -> str:
        return (
            f"QuantumFoundationSystem('{self.name}', "
            f"timeline={self._timeline.length} events, "
            f"state={self._state_engine.current_state!r})"
        )
