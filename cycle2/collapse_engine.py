"""
Cycle 2 — Collapse Engine
==========================

The CollapseEngine applies a MeasurementPolicy to a StateVector and records
the event as an IrreversibleCollapseEvent in an append-only log.

Key properties:
  • Deterministic: same state + same seed + same policy → same result
  • Irreversible: collapse events are frozen and append-only
  • Replay-safe: the full collapse log can be replayed to verify integrity
  • Token-gated: each collapse consumes a CollapseToken (one-use permission)

Quantum alignment:
  • Measurement without a CollapseToken is rejected — measurement is not free
  • Each collapse event permanently records what information was destroyed
  • Repeat measurement of a post-collapse state is idempotent
  • The engine does NOT decide when to measure — that is the caller's authority
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cycle1.state_evolution_engine import StateVector
from cycle2.measurement_policy import MeasurementPolicy, MeasurementResult


# ---------------------------------------------------------------------------
# CollapseToken — Gating Measurement Authority
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CollapseToken:
    """
    A single-use permission token granting authority to perform one collapse.

    Tokens are issued by external authority (the caller). The CollapseEngine
    will only perform a measurement if a valid, unused token is presented.

    This models the quantum principle that measurement is not free — it requires
    a deliberate act with explicit permission. The engine does not spontaneously
    measure; it waits for an explicit decision.

    Tokens are NOT recyclable. After use, the CollapseEngine marks them consumed.
    """
    token_id: str              # unique identifier
    authorized_policy: str     # the policy name this token authorizes
    issued_at_ns: int          # timestamp when token was issued

    def __post_init__(self) -> None:
        if not self.token_id:
            raise ValueError("CollapseToken.token_id must be non-empty")
        if not self.authorized_policy:
            raise ValueError("CollapseToken.authorized_policy must be non-empty")


# ---------------------------------------------------------------------------
# IrreversibleCollapseEvent — The Permanent Record
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IrreversibleCollapseEvent:
    """
    A frozen record of one measurement collapse.

    This is the fundamental unit of the collapse log. Once created, it cannot
    be modified. Every field is preserved for audit and replay.

    Fields:
      event_id            — unique sequential identifier
      pre_collapse_state  — the StateVector BEFORE measurement
      result              — the full MeasurementResult (outcome, confidence, loss)
      token_id            — the CollapseToken that authorized this measurement
      timestamp_ns        — wall-clock time of the collapse event
    """
    event_id: int
    pre_collapse_state: StateVector
    result: MeasurementResult
    token_id: str
    timestamp_ns: int

    def __post_init__(self) -> None:
        if self.event_id < 0:
            raise ValueError("event_id must be non-negative")


class _CollapseEventLog:
    """
    Append-only log of IrreversibleCollapseEvent objects.
    Structurally identical in design to Cycle 1's _ImmutableDeltaLog.
    """

    def __init__(self) -> None:
        self._events: List[IrreversibleCollapseEvent] = []

    def append(self, event: IrreversibleCollapseEvent) -> None:
        if self._events:
            last_id = self._events[-1].event_id
            if event.event_id <= last_id:
                raise ValueError(
                    f"[COLLAPSE LOG] event_id must be strictly increasing. "
                    f"Got {event.event_id}, last was {last_id}."
                )
        self._events.append(event)

    @property
    def events(self) -> Tuple[IrreversibleCollapseEvent, ...]:
        return tuple(self._events)

    def __len__(self) -> int:
        return len(self._events)


# ---------------------------------------------------------------------------
# The Collapse Engine
# ---------------------------------------------------------------------------

class CollapseEngine:
    """
    Applies MeasurementPolicies to StateVectors and records irreversible
    collapse events.

    Usage pattern:
        1. Register a policy
        2. Issue a CollapseToken for that policy
        3. Call engine.collapse(state, token, seed)
        4. Retrieve the MeasurementResult and the post-collapse StateVector

    The engine does NOT hold a StateVector internally — it is stateless
    between collapses. It is the caller's responsibility to manage state
    and bridge Cycle 1's engine output into Cycle 2's collapse input.
    """

    def __init__(self) -> None:
        self._policies: dict[str, MeasurementPolicy] = {}
        self._log: _CollapseEventLog = _CollapseEventLog()
        self._consumed_tokens: set[str] = set()
        self._event_counter: int = 0

    # --- Policy Registration ---

    def register_policy(self, policy: MeasurementPolicy) -> None:
        """Register a MeasurementPolicy. Re-registration is forbidden."""
        name = policy.name
        if name in self._policies:
            raise ValueError(
                f"Policy '{name}' is already registered. "
                "Re-registration is forbidden."
            )
        self._policies[name] = policy

    # --- Token Management ---

    def issue_token(self, policy_name: str, token_id: str) -> CollapseToken:
        """
        Issue a new CollapseToken for a registered policy.

        Raises if policy_name is not registered or token_id is already consumed.
        """
        if policy_name not in self._policies:
            raise ValueError(
                f"Cannot issue token: policy '{policy_name}' is not registered."
            )
        if token_id in self._consumed_tokens:
            raise ValueError(
                f"Token '{token_id}' has already been consumed. "
                "Tokens are single-use."
            )
        return CollapseToken(
            token_id=token_id,
            authorized_policy=policy_name,
            issued_at_ns=time.time_ns(),
        )

    # --- Core Collapse Operation ---

    def collapse(
        self,
        state: StateVector,
        token: CollapseToken,
        seed: int,
    ) -> IrreversibleCollapseEvent:
        """
        Perform one measurement collapse.

        Args:
            state: The pre-measurement StateVector
            token: A valid, unused CollapseToken
            seed:  Deterministic seed for outcome selection

        Returns:
            An IrreversibleCollapseEvent (also appended to the internal log)

        Raises:
            ValueError if token is consumed, invalid, or policy mismatch
        """
        # Token validation
        if not isinstance(token, CollapseToken):
            raise TypeError(
                "collapse() requires a CollapseToken. "
                "Direct measurement without a token is forbidden."
            )
        if token.token_id in self._consumed_tokens:
            raise ValueError(
                f"[TOKEN CONSUMED] Token '{token.token_id}' has already been used. "
                "A collapsed state cannot be un-collapsed and re-collapsed with the same token."
            )
        if token.authorized_policy not in self._policies:
            raise ValueError(
                f"[POLICY MISMATCH] Token authorizes policy '{token.authorized_policy}', "
                "which is not registered."
            )

        # Apply the measurement policy
        policy = self._policies[token.authorized_policy]
        result = policy.measure(state, seed)

        # Record the collapse as an irreversible event
        event = IrreversibleCollapseEvent(
            event_id=self._event_counter,
            pre_collapse_state=state,
            result=result,
            token_id=token.token_id,
            timestamp_ns=time.time_ns(),
        )

        self._log.append(event)
        self._consumed_tokens.add(token.token_id)
        self._event_counter += 1

        return event

    # --- Replay Verification ---

    def replay_collapse(
        self,
        event: IrreversibleCollapseEvent,
    ) -> MeasurementResult:
        """
        Replay a collapse event to verify determinism.

        Given the same pre-collapse state, seed, and policy, always produces
        the same MeasurementResult. This is a read-only operation.
        """
        policy_name = event.result.policy_name
        if policy_name not in self._policies:
            raise ValueError(
                f"Cannot replay: policy '{policy_name}' is not registered."
            )
        policy = self._policies[policy_name]
        return policy.measure(event.pre_collapse_state, event.result.seed_used)

    def verify_collapse_integrity(self) -> bool:
        """
        Verify all recorded collapse events replay to the same result.
        Returns True if all replays match. Raises on any mismatch.
        """
        for event in self._log.events:
            replayed = self.replay_collapse(event)
            if replayed.outcome != event.result.outcome:
                raise AssertionError(
                    f"[COLLAPSE INTEGRITY FAILURE] "
                    f"Event {event.event_id}: original outcome='{event.result.outcome}', "
                    f"replayed outcome='{replayed.outcome}'."
                )
        return True

    # --- Read-Only Access ---

    @property
    def collapse_log(self) -> Tuple[IrreversibleCollapseEvent, ...]:
        return self._log.events

    @property
    def total_information_lost(self) -> float:
        """Sum of all declared information losses across all collapses."""
        return sum(e.result.information_loss_declared for e in self._log.events)

    def __repr__(self) -> str:
        return (
            f"CollapseEngine("
            f"events={len(self._log)}, "
            f"policies={list(self._policies.keys())}, "
            f"total_info_lost={self.total_information_lost:.4f} bits)"
        )
