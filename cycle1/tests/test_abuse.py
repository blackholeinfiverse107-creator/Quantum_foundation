"""
Cycle 1 Tests — Abuse & Adversarial Testing
=============================================

Demonstrates that the Sovereign State Evolution Engine RESISTS:
  1. Retroactive mutation of the delta log
  2. State injection bypassing the observe() interface
  3. Implicit execution via unregistered observation types
  4. Non-StateVector returns from TransitionRules
  5. Dimension-changing transitions
  6. Zero-vector injection
  7. Duplicate rule registration (silent override attack)

Every test MUST demonstrate rejection — these are negative tests.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import unittest

from cycle1.state_evolution_engine import (
    Observation,
    StateVector,
    SovereignStateEngine,
    StateDelta,
    identity_rule,
    phase_rotation_rule,
)


def _uniform_2d() -> StateVector:
    amp = 1.0 / math.sqrt(2)
    return StateVector({"0": complex(amp), "1": complex(amp)})


def _basis_0() -> StateVector:
    return StateVector({"0": complex(1.0), "1": complex(0.0)})


class TestRetroactiveMutationRejection(unittest.TestCase):
    """History must remain immutable at all times."""

    def test_cannot_modify_delta_sequence_number(self):
        """StateDelta is frozen — mutating seq_number must raise."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        delta = engine.observe(Observation("identity", ()))
        with self.assertRaises((AttributeError, TypeError)):
            delta.sequence_number = 999  # type: ignore

    def test_cannot_modify_delta_prior_state(self):
        """StateDelta.prior_state is frozen — reassignment must raise."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        delta = engine.observe(Observation("identity", ()))
        with self.assertRaises((AttributeError, TypeError)):
            delta.prior_state = _basis_0()  # type: ignore

    def test_cannot_modify_delta_next_state(self):
        """StateDelta.next_state is frozen — reassignment must raise."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        delta = engine.observe(Observation("identity", ()))
        with self.assertRaises((AttributeError, TypeError)):
            delta.next_state = _basis_0()  # type: ignore

    def test_delta_log_is_immutable_tuple(self):
        """engine.delta_log returns a tuple — it cannot be mutated."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        engine.observe(Observation("identity", ()))
        log = engine.delta_log
        self.assertIsInstance(log, tuple)
        with self.assertRaises((TypeError, AttributeError)):
            log[0] = None  # type: ignore

    def test_appending_to_log_copy_does_not_affect_engine(self):
        """Appending to a copy of the delta log must not affect engine state."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        engine.observe(Observation("identity", ()))
        log_copy = list(engine.delta_log)
        # Forge a delta and add to the copy
        log_copy.append(None)  # type: ignore
        # Engine log is unchanged
        self.assertEqual(len(engine.delta_log), 1)


class TestStateInjectionRejection(unittest.TestCase):
    """Engine state must only be reachable via observe()."""

    def test_no_state_setter_exists(self):
        """SovereignStateEngine must have no public state setter."""
        engine = SovereignStateEngine(_uniform_2d())
        with self.assertRaises(AttributeError):
            engine.current_state = _basis_0()  # type: ignore

    def test_cannot_inject_via_raw_dict(self):
        """Passing a raw dict instead of Observation must be rejected."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        with self.assertRaises((TypeError, AttributeError)):
            engine.observe({"type": "identity", "payload": ()})  # type: ignore

    def test_cannot_inject_via_string(self):
        """Passing a string instead of Observation must be rejected."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        with self.assertRaises(TypeError):
            engine.observe("identity")  # type: ignore

    def test_invalid_observation_type_rejected(self):
        """Observation with unregistered type must be rejected."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        with self.assertRaises(ValueError):
            engine.observe(Observation("UNKNOWN_UNREGISTERED_OP", ()))

    def test_observation_with_mutable_payload_rejected(self):
        """Observation payload must be a tuple — list is rejected."""
        with self.assertRaises(TypeError):
            Observation("identity", [1, 2, 3])  # type: ignore


class TestImplicitExecutionRejection(unittest.TestCase):
    """TransitionRules must be pure evolution functions, not executors."""

    def test_rule_returning_none_rejected(self):
        """A TransitionRule that returns None must be caught and rejected."""
        def bad_rule(state, obs):
            return None  # implicit execution of nothing — not a StateVector

        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("bad", bad_rule)
        with self.assertRaises(TypeError):
            engine.observe(Observation("bad", ()))

    def test_rule_returning_string_rejected(self):
        """A TransitionRule that returns a string must be caught and rejected."""
        def exec_rule(state, obs):
            return "execute_command_xyz"  # black-box logic — rejected

        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("exec", exec_rule)
        with self.assertRaises(TypeError):
            engine.observe(Observation("exec", ()))


class TestDimensionChangeRejection(unittest.TestCase):
    """Hilbert space dimension must not change mid-evolution."""

    def test_rule_expanding_dimension_rejected(self):
        """A rule that adds a new basis state must be rejected."""
        def expand_rule(state, obs):
            amps = {a.basis_label: a.value for a in state.amplitudes}
            amps["EXTRA"] = complex(0.0)
            # Will fail norm check — but even if it didn't, dimension changes
            # We make it unit by construction:
            import math
            n = len(amps)
            return StateVector({k: complex(1.0 / math.sqrt(n)) for k in amps})

        initial = _uniform_2d()
        engine = SovereignStateEngine(initial)
        engine.register_rule("expand", expand_rule)
        with self.assertRaises(ValueError):
            engine.observe(Observation("expand", ()))

    def test_rule_collapsing_dimension_rejected(self):
        """A rule that removes a basis state must be rejected."""
        def collapse_rule(state, obs):
            # Returns only 1 basis state from a 2-dimensional space
            return StateVector({"0": complex(1.0)})

        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("collapse_dim", collapse_rule)
        with self.assertRaises(ValueError):
            engine.observe(Observation("collapse_dim", ()))


class TestZeroVectorInjection(unittest.TestCase):
    """Zero vector must be a forbidden state."""

    def test_zero_vector_directly_rejected(self):
        """Constructing a StateVector from all-zero amplitudes must raise."""
        with self.assertRaises(ValueError):
            StateVector({"0": complex(0.0), "1": complex(0.0)})

    def test_rule_producing_zero_vector_rejected(self):
        """A damping that drives norm to zero must be caught."""
        engine = SovereignStateEngine(_uniform_2d())

        def annihilate(state, obs):
            # Try to return a zero vector — should raise inside StateVector
            return StateVector({"0": complex(0.0), "1": complex(0.0)})

        engine.register_rule("annihilate", annihilate)
        with self.assertRaises(ValueError):
            engine.observe(Observation("annihilate", ()))


class TestDuplicateRuleRejection(unittest.TestCase):
    """Silent rule override (a security attack vector) must be blocked."""

    def test_re_registering_same_observation_type_raises(self):
        """Registering a second rule for the same observation type must raise."""
        engine = SovereignStateEngine(_uniform_2d())
        engine.register_rule("identity", identity_rule)
        with self.assertRaises(ValueError):
            engine.register_rule("identity", phase_rotation_rule)


class TestObservationImmutability(unittest.TestCase):
    """Observations themselves must be immutable tokens."""

    def test_observation_is_frozen(self):
        """Observation must not be mutable after creation."""
        obs = Observation("identity", ())
        with self.assertRaises((AttributeError, TypeError)):
            obs.observation_type = "HACKED"  # type: ignore

    def test_empty_observation_type_rejected(self):
        """An empty string observation type must be rejected."""
        with self.assertRaises(ValueError):
            Observation("", ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
