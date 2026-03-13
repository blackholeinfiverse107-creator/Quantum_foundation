"""
Cycle 1 — Sovereign State Evolution Engine
===========================================

Design mandate:
  • Accepts inputs strictly as Observations (typed, immutable)
  • Evolves internal state via explicit TransitionRules (pure functions)
  • Emits StateDelta objects only — never mutates history
  • Never executes actions or side-effects
  • Zero hidden global state

Quantum alignment:
  • StateVector = superposition of named basis amplitudes (complex numbers)
  • Norm conservation enforced at every transition (unit vector invariant)
  • No cloning — StateVectors are value objects, not references
  • Observation is irreversible — state cannot un-observe
"""

from __future__ import annotations

import cmath
import math
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Primitive Types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Observation:
    """
    An external input presented to the engine.

    Observations are IMMUTABLE and TYPED. The engine rejects anything that
    does not conform to a registered observation type. Observations carry
    no execution semantics — they are pure information tokens.
    """
    observation_type: str          # must match a registered rule key
    payload: Tuple                 # arbitrary typed data, frozen

    def __post_init__(self) -> None:
        if not self.observation_type or not isinstance(self.observation_type, str):
            raise ValueError("observation_type must be a non-empty string")
        if not isinstance(self.payload, tuple):
            raise TypeError("payload must be a tuple (immutable sequence)")


@dataclass(frozen=True)
class Amplitude:
    """
    A complex probability amplitude for a single basis state.
    Carries both the value and the basis label.
    """
    basis_label: str
    value: complex

    def probability(self) -> float:
        """Born rule: P = |amplitude|²"""
        return (self.value * self.value.conjugate()).real


class StateVector:
    """
    Immutable superposition of named basis amplitudes.

    Invariants:
      1. Sum of probabilities == 1.0  (unit norm)
      2. No basis label is empty
      3. Dimension >= 1
      4. Instance is effectively frozen (no public setters)
    """

    _TOLERANCE: float = 1e-10

    def __init__(self, amplitudes: Dict[str, complex]) -> None:
        if not amplitudes:
            raise ValueError("[FORBIDDEN STATE] StateVector must have at least one basis state")

        for label, val in amplitudes.items():
            if not label:
                raise ValueError("[FORBIDDEN STATE] Basis label must be non-empty")
            if not isinstance(val, complex):
                # Accept int/float by coercing
                amplitudes = {k: complex(v) for k, v in amplitudes.items()}
                break

        # Store as frozen tuple of Amplitude objects
        self._amplitudes: Tuple[Amplitude, ...] = tuple(
            Amplitude(label, complex(val)) for label, val in amplitudes.items()
        )
        self._norm: float = self._compute_norm()
        self._validate_norm()

    def _compute_norm(self) -> float:
        return math.sqrt(sum(a.probability() for a in self._amplitudes))

    def _validate_norm(self) -> None:
        if abs(self._norm - 1.0) > self._TOLERANCE:
            raise ValueError(
                f"[FORBIDDEN STATE] StateVector norm = {self._norm:.8f}, must be 1.0. "
                "A quantum state must lie on the unit sphere."
            )

    @property
    def amplitudes(self) -> Tuple[Amplitude, ...]:
        return self._amplitudes

    @property
    def dimension(self) -> int:
        return len(self._amplitudes)

    def get(self, basis_label: str) -> Optional[complex]:
        for a in self._amplitudes:
            if a.basis_label == basis_label:
                return a.value
        return None

    def as_dict(self) -> Dict[str, complex]:
        return {a.basis_label: a.value for a in self._amplitudes}

    def norm(self) -> float:
        return self._norm

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StateVector):
            return False
        return self._amplitudes == other._amplitudes

    def __repr__(self) -> str:
        terms = " + ".join(
            f"({a.value:.4f})|{a.basis_label}⟩" for a in self._amplitudes
        )
        return f"StateVector[{terms}]"

    def __hash__(self) -> int:
        return hash(self._amplitudes)


# ---------------------------------------------------------------------------
# Transition Rules
# ---------------------------------------------------------------------------

# A TransitionRule is a pure function: (StateVector, Observation) -> StateVector
# It must NOT mutate inputs, must NOT access global state, must NOT execute.
TransitionRule = Callable[[StateVector, Observation], StateVector]


@dataclass(frozen=True)
class RegisteredRule:
    """Associates an observation type with a pure TransitionRule."""
    observation_type: str
    rule: TransitionRule
    description: str


# ---------------------------------------------------------------------------
# State Deltas (Append-Only Log Entries)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StateDelta:
    """
    Immutable record of a state transition event.

    A StateDelta is a SNAPSHOT, not a command. It records what happened —
    not what to do. The log of StateDelta objects constitutes the full,
    replay-able history of the engine.

    Invariants:
      • sequence_number is strictly monotonically increasing
      • prior_state and next_state are both valid StateVectors
      • timestamp_ns is the wall-clock time of the transition (nanoseconds)
      • Delta objects are frozen — they cannot be mutated after creation
    """
    sequence_number: int
    observation: Observation
    prior_state: StateVector
    next_state: StateVector
    applied_rule: str              # name/key of the rule that was applied
    timestamp_ns: int              # time.time_ns() at transition

    def __post_init__(self) -> None:
        if self.sequence_number < 0:
            raise ValueError("sequence_number must be non-negative")
        if self.prior_state == self.next_state:
            # A delta with no change is technically valid but worth noting
            pass


class _ImmutableDeltaLog:
    """
    Append-only log of StateDelta objects.

    Enforces:
      • No deletion
      • No in-place update
      • Strictly increasing sequence numbers
    """

    def __init__(self) -> None:
        self._entries: List[StateDelta] = []
        self._sealed: bool = False

    def append(self, delta: StateDelta) -> None:
        if self._sealed:
            raise RuntimeError(
                "[IMMUTABILITY VIOLATION] Delta log has been sealed. No further appends allowed."
            )
        if self._entries:
            last = self._entries[-1]
            if delta.sequence_number <= last.sequence_number:
                raise ValueError(
                    f"[IMPOSSIBLE TRANSITION] sequence_number must be strictly increasing. "
                    f"Got {delta.sequence_number}, last was {last.sequence_number}."
                )
        self._entries.append(delta)

    def seal(self) -> None:
        """Permanently close the log. No further appends permitted."""
        self._sealed = True

    @property
    def entries(self) -> Tuple[StateDelta, ...]:
        """Returns an immutable snapshot of the log."""
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(tuple(self._entries))


# ---------------------------------------------------------------------------
# The Sovereign State Evolution Engine
# ---------------------------------------------------------------------------

class SovereignStateEngine:
    """
    The central architectural primitive of Cycle 1.

    Responsibilities:
      • Maintain the current StateVector
      • Accept Observations and route them to registered TransitionRules
      • Emit StateDelta records into an append-only log
      • Enforce ALL invariants at every transition

    Prohibitions (machine-enforced):
      • Cannot be externally mutated (state is private)
      • Cannot replay a transition except via deterministic replay method
      • Cannot execute actions — only evolution
      • Cannot accept unregistered observation types
    """

    def __init__(self, initial_state: StateVector) -> None:
        self._state: StateVector = initial_state
        self._rules: Dict[str, RegisteredRule] = {}
        self._log: _ImmutableDeltaLog = _ImmutableDeltaLog()
        self._sequence: int = 0

    # --- Registration ---

    def register_rule(
        self,
        observation_type: str,
        rule: TransitionRule,
        description: str = "",
    ) -> None:
        """Register a pure TransitionRule for a given observation type."""
        if observation_type in self._rules:
            raise ValueError(
                f"Rule for '{observation_type}' is already registered. "
                "Re-registration is forbidden to prevent silent override attacks."
            )
        self._rules[observation_type] = RegisteredRule(
            observation_type=observation_type,
            rule=rule,
            description=description,
        )

    # --- Evolution ---

    def observe(self, observation: Observation) -> StateDelta:
        """
        Present an Observation to the engine.

        Returns a StateDelta describing the transition.
        Raises if observation type is unregistered or transition violates invariants.
        """
        if not isinstance(observation, Observation):
            raise TypeError(
                "[FORBIDDEN STATE] observe() only accepts Observation instances. "
                "Raw data injection is rejected."
            )

        obs_type = observation.observation_type
        if obs_type not in self._rules:
            raise ValueError(
                f"[IMPOSSIBLE TRANSITION] No rule registered for observation_type='{obs_type}'. "
                "Only explicit transitions are permitted."
            )

        rule = self._rules[obs_type]
        prior = self._state

        # Apply the pure transition function
        next_state = rule.rule(prior, observation)

        # Validate the result — the rule must return a valid StateVector
        if not isinstance(next_state, StateVector):
            raise TypeError(
                "[IMPOSSIBLE TRANSITION] TransitionRule must return a StateVector. "
                f"Got {type(next_state).__name__}"
            )

        # Dimension must be preserved (no spontaneous Hilbert-space change)
        if next_state.dimension != prior.dimension:
            raise ValueError(
                f"[IMPOSSIBLE TRANSITION] Dimension mismatch: "
                f"prior={prior.dimension}, next={next_state.dimension}. "
                "State space dimension is fixed at engine initialization."
            )

        # Build delta and commit
        delta = StateDelta(
            sequence_number=self._sequence,
            observation=observation,
            prior_state=prior,
            next_state=next_state,
            applied_rule=obs_type,
            timestamp_ns=time.time_ns(),
        )

        self._log.append(delta)
        self._state = next_state
        self._sequence += 1

        return delta

    # --- Inspection (read-only) ---

    @property
    def current_state(self) -> StateVector:
        """Returns current state. Read-only — no setter exists."""
        return self._state

    @property
    def delta_log(self) -> Tuple[StateDelta, ...]:
        """Returns the full immutable delta log."""
        return self._log.entries

    @property
    def step_count(self) -> int:
        return self._sequence

    # --- Deterministic Replay ---

    def replay_from_log(
        self,
        initial_state: StateVector,
        delta_log: Tuple[StateDelta, ...],
    ) -> StateVector:
        """
        Replay a sequence of deltas from an initial state.

        This proves determinism: given the same initial state and the same
        sequence of observations, the engine always reaches the same final state.

        The replay engine is stateless — it does NOT mutate self.
        """
        replay_engine = SovereignStateEngine(initial_state)

        # Re-register the same rules (replay needs them)
        for obs_type, reg in self._rules.items():
            replay_engine.register_rule(obs_type, reg.rule, reg.description)

        for delta in delta_log:
            replay_engine.observe(delta.observation)

        return replay_engine.current_state

    def verify_replay_integrity(self) -> bool:
        """
        Verify that replaying the delta log from the initial state
        produces the current state.

        Returns True if integrity holds, raises AssertionError otherwise.
        """
        if not self._log.entries:
            return True

        initial = self._log.entries[0].prior_state
        replayed = self.replay_from_log(initial, self._log.entries)

        if replayed != self._state:
            raise AssertionError(
                "[INTEGRITY FAILURE] Replay produced a different state than current. "
                "Delta log may have been tampered with."
            )
        return True

    def __repr__(self) -> str:
        return (
            f"SovereignStateEngine("
            f"step={self._sequence}, "
            f"rules={list(self._rules.keys())}, "
            f"state={self._state!r})"
        )


# ---------------------------------------------------------------------------
# Built-in Standard Transition Rules
# ---------------------------------------------------------------------------

def identity_rule(state: StateVector, obs: Observation) -> StateVector:
    """No-op rule. Returns the state unchanged. Used as a baseline."""
    return state


def phase_rotation_rule(state: StateVector, obs: Observation) -> StateVector:
    """
    Applies a phase rotation to each amplitude.
    obs.payload = (theta_radians: float,)
    where theta is the rotation angle in radians.
    Norm is preserved since |e^{iθ}| = 1.
    """
    theta = float(obs.payload[0])
    rotation = cmath.exp(1j * theta)
    new_amplitudes = {
        a.basis_label: a.value * rotation
        for a in state.amplitudes
    }
    return StateVector(new_amplitudes)


def dampened_amplitude_rule(state: StateVector, obs: Observation) -> StateVector:
    """
    Scales a specific basis amplitude by a damping factor, then renormalizes.
    obs.payload = (target_label: str, damping: float)
    Used to model amplitude redistribution under decoherence.
    """
    target_label: str = obs.payload[0]
    damping: float = float(obs.payload[1])

    if not 0.0 <= damping <= 1.0:
        raise ValueError("damping must be in [0, 1]")

    new_amps = {a.basis_label: a.value for a in state.amplitudes}
    if target_label not in new_amps:
        raise ValueError(f"Basis label '{target_label}' not found in state")

    new_amps[target_label] *= damping

    # Renormalize
    raw_norm = math.sqrt(sum(abs(v) ** 2 for v in new_amps.values()))
    if raw_norm < 1e-15:
        raise ValueError(
            "[FORBIDDEN STATE] Damping drove norm to zero — state annihilated."
        )
    normalized = {k: v / raw_norm for k, v in new_amps.items()}
    return StateVector(normalized)
