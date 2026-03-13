"""
Cycle 2 — Deterministic Measurement & Collapse Framework
=========================================================

Design mandate:
  • Takes multi-path internal state (StateVector)
  • Applies explicit measurement policies
  • Produces: observed_value, confidence, declared_information_loss
  • Collapse is IRREVERSIBLE — recorded as an append-only event
  • No randomness unless explicitly seeded (deterministic by default)
  • Repeat measurement of a collapsed state converges (idempotent)

Quantum alignment:
  • Measurement COSTS information — the post-measurement state has LESS
    superposition than the pre-measurement state
  • Collapse is the standard (von Neumann / projective) model
  • Information loss is DECLARED, not hidden
  • Born rule determines outcome probabilities; seed controls the draw

This module contains:
  - MeasurementPolicy (abstract base)
  - ProjectiveMeasurementPolicy — full collapse onto a basis eigenstate
  - WeakMeasurementPolicy — partial information, partial collapse
  - MeasurementResult — the observable output of a measurement
"""

from __future__ import annotations

import hashlib
import math
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cycle1.state_evolution_engine import Amplitude, StateVector


# ---------------------------------------------------------------------------
# Measurement Costs — Entropy helpers
# ---------------------------------------------------------------------------

def von_neumann_entropy(state: StateVector) -> float:
    """
    Compute the classical Shannon entropy of the probability distribution
    defined by a StateVector.

    H = -∑ p_i log₂(p_i)  where p_i = |α_i|²

    This is a lower bound on the quantum von Neumann entropy for pure states
    (which is always 0 for pure states, but the classical projection entropy
    measures how much information is lost when we measure in the standard basis).

    For a pure state, this is the measurement entropy — how much classical
    information is extractable.
    """
    entropy = 0.0
    for amp in state.amplitudes:
        p = amp.probability()
        if p > 1e-15:
            entropy -= p * math.log2(p)
    return entropy


def information_loss_after_collapse(
    pre_state: StateVector,
    post_state: StateVector,
) -> float:
    """
    Declared information loss = H(pre) - H(post).

    After projective collapse, the post-state is a pure basis state with
    H=0. The full pre-measurement entropy is lost.

    For partial (weak) measurement, only some entropy is lost.
    """
    return von_neumann_entropy(pre_state) - von_neumann_entropy(post_state)


# ---------------------------------------------------------------------------
# Measurement Result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MeasurementResult:
    """
    The observable output of a measurement operation.

    All three fields are ALWAYS present — hiding information loss is forbidden.

    Fields:
      outcome        — the observed basis label (classical bit/string)
      confidence     — probability of this outcome under the Born rule
      information_loss_declared — entropy removed from the system by this measurement
      post_state     — the collapsed StateVector after measurement
      seed_used      — the seed that produced this deterministic outcome
      policy_name    — name of the policy that was applied
    """
    outcome: str
    confidence: float
    information_loss_declared: float
    post_state: StateVector
    seed_used: int
    policy_name: str

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0 + 1e-10):
            raise ValueError(
                f"confidence must be in [0, 1], got {self.confidence:.8f}"
            )
        if self.information_loss_declared < -1e-10:
            raise ValueError(
                f"information_loss_declared must be ≥ 0, got {self.information_loss_declared:.8f}"
            )


# ---------------------------------------------------------------------------
# Abstract Measurement Policy
# ---------------------------------------------------------------------------

class MeasurementPolicy(ABC):
    """
    Abstract base for all measurement strategies.

    A MeasurementPolicy defines HOW a StateVector is measured.
    It is a pure, stateless object. The same policy applied to the same
    state with the same seed must ALWAYS produce the same result.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this policy."""

    @abstractmethod
    def measure(self, state: StateVector, seed: int) -> MeasurementResult:
        """
        Apply this measurement policy to a state.

        Args:
            state: The pre-measurement StateVector
            seed: Deterministic seed controlling outcome selection

        Returns:
            MeasurementResult with outcome, confidence, and declared loss
        """


# ---------------------------------------------------------------------------
# Deterministic Seed → Outcome Selection
# ---------------------------------------------------------------------------

def _seeded_sample(probabilities: List[float], seed: int) -> int:
    """
    Deterministically select an index from a probability distribution
    using a seeded hash function.

    This is NOT random — given the same seed and distribution, always returns
    the same index. The seed must be explicitly provided by the caller.

    Algorithm:
    1. Hash (seed || probabilities) using SHA-256 to get a deterministic float
    2. Use that float as a "random" number for cumulative distribution sampling

    This is deterministic, auditable, and seedless-call-resistant.
    """
    # Build a canonical, deterministic byte string from seed + probabilities
    payload = struct.pack("q", seed)  # 8-byte seed
    for p in probabilities:
        payload += struct.pack("d", p)  # 8-byte double per probability

    digest = hashlib.sha256(payload).hexdigest()
    # Map the first 16 hex chars to a float in [0, 1)
    raw = int(digest[:16], 16)
    r = raw / (16 ** 16)  # normalize to [0, 1)

    # Cumulative distribution function sampling
    cumulative = 0.0
    for i, p in enumerate(probabilities):
        cumulative += p
        if r < cumulative:
            return i

    return len(probabilities) - 1  # fallback for floating-point edge cases


# ---------------------------------------------------------------------------
# Projective Measurement Policy (Full Collapse)
# ---------------------------------------------------------------------------

class ProjectiveMeasurementPolicy(MeasurementPolicy):
    """
    Standard von Neumann projective measurement.

    Process:
    1. Compute Born-rule probabilities for each basis state
    2. Select an outcome deterministically using the seed
    3. Collapse the state to the selected basis eigenstate
    4. Declare the full pre-measurement entropy as information loss

    Post-measurement guarantee:
    - The post-state is a pure eigenstate (one amplitude = 1, rest = 0)
    - Measuring the post-state again always returns the same outcome (idempotent)
    """

    @property
    def name(self) -> str:
        return "ProjectiveMeasurement"

    def measure(self, state: StateVector, seed: int) -> MeasurementResult:
        amps = state.amplitudes
        labels = [a.basis_label for a in amps]
        probs = [a.probability() for a in amps]

        # Select outcome
        idx = _seeded_sample(probs, seed)
        selected_label = labels[idx]
        confidence = probs[idx]

        # Collapse: post-measurement state = |selected_label⟩
        post_amps: Dict[str, complex] = {
            label: complex(1.0) if label == selected_label else complex(0.0)
            for label in labels
        }
        post_state = StateVector(post_amps)

        # Declared information loss = full pre-measurement entropy
        info_loss = information_loss_after_collapse(state, post_state)

        return MeasurementResult(
            outcome=selected_label,
            confidence=confidence,
            information_loss_declared=max(0.0, info_loss),
            post_state=post_state,
            seed_used=seed,
            policy_name=self.name,
        )


# ---------------------------------------------------------------------------
# Weak Measurement Policy (Partial Collapse)
# ---------------------------------------------------------------------------

class WeakMeasurementPolicy(MeasurementPolicy):
    """
    Weak / partial measurement.

    Instead of fully collapsing to a basis eigenstate, the state is
    'nudged' toward the selected outcome by a coupling strength α ∈ (0, 1].

    α = 0.0 → no collapse (identity measurement, maximum privacy)
    α = 1.0 → full projective collapse (same as ProjectiveMeasurementPolicy)

    The declared information loss is α * full_entropy_loss.

    This models partial-measurement scenarios, POVM elements, and
    non-demolition measurements.
    """

    def __init__(self, coupling_strength: float = 0.5) -> None:
        if not (0.0 < coupling_strength <= 1.0):
            raise ValueError(
                f"coupling_strength must be in (0, 1], got {coupling_strength}"
            )
        self._alpha = coupling_strength

    @property
    def name(self) -> str:
        return f"WeakMeasurement(α={self._alpha:.2f})"

    def measure(self, state: StateVector, seed: int) -> MeasurementResult:
        amps = state.amplitudes
        labels = [a.basis_label for a in amps]
        probs = [a.probability() for a in amps]

        # Select the 'peeked-at' outcome
        idx = _seeded_sample(probs, seed)
        selected_label = labels[idx]
        confidence = probs[idx]

        # Partial collapse: boost the selected amplitude by α, suppress others
        pre_amps = {a.basis_label: a.value for a in amps}
        post_amps_raw: Dict[str, complex] = {}
        for label, val in pre_amps.items():
            if label == selected_label:
                # Increase toward 1 by α
                mag = abs(val)
                boosted_mag = mag + self._alpha * (1.0 - mag)
                # Preserve phase
                phase = val / mag if mag > 1e-15 else complex(1.0)
                post_amps_raw[label] = boosted_mag * phase
            else:
                # Decrease toward 0 by α
                post_amps_raw[label] = val * (1.0 - self._alpha)

        # Renormalize
        raw_norm = math.sqrt(sum(abs(v) ** 2 for v in post_amps_raw.values()))
        if raw_norm < 1e-15:
            raise ValueError(
                "[FORBIDDEN STATE] Weak measurement drove norm to zero."
            )
        post_amps_normalized = {k: v / raw_norm for k, v in post_amps_raw.items()}
        post_state = StateVector(post_amps_normalized)

        # Partial information loss
        full_loss = information_loss_after_collapse(state, post_state)
        declared_loss = max(0.0, self._alpha * full_loss)

        return MeasurementResult(
            outcome=selected_label,
            confidence=confidence,
            information_loss_declared=declared_loss,
            post_state=post_state,
            seed_used=seed,
            policy_name=self.name,
        )
