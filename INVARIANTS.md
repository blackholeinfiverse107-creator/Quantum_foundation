# Master Invariant Index
# All invariants across all three cycles — Sovereign Quantum Architecture Primitives
# Date: 2026-03-02  |  Maintained by: Kanishk Singh

---

## Cycle 1 — State Evolution Invariants

| ID | Name | Type | Description | Module |
|---|---|---|---|---|
| I1 | Norm Conservation | GUARANTEE | ‖ψ‖² = 1.0 at all times | `cycle1/invariants.py` |
| I2 | No Zero Vector | FORBIDDEN STATE | Zero amplitude vector is rejected | `cycle1/state_evolution_engine.py` |
| I3 | History Immutability | GUARANTEE | Delta log is append-only, frozen | `cycle1/invariants.py` |
| I4 | Sequence Monotonicity | GUARANTEE | Seq numbers strictly increase by 1 | `cycle1/invariants.py` |
| I5 | Delta Continuity | GUARANTEE | next_state[i] == prior_state[i+1] | `cycle1/invariants.py` |
| I6 | Dimension Preservation | IMPOSSIBLE TRANSITION | Hilbert space dim never changes mid-evolution | `cycle1/state_evolution_engine.py` |
| I7 | Replay Determinism | GUARANTEE | Same observations → same final state | `cycle1/invariants.py` |

---

## Cycle 2 — Measurement Invariants

| ID | Name | Type | Description | Module |
|---|---|---|---|---|
| M1 | Probability Normalization | GUARANTEE | Born-rule probs sum to 1 | `cycle2/invariants.py` |
| M2 | Non-Negative Info Loss | GUARANTEE | Declared information_loss ≥ 0 | `cycle2/invariants.py` |
| M3 | Collapse Log Monotonicity | GUARANTEE | Event IDs strictly increasing | `cycle2/invariants.py` |
| M4 | Repeat Measurement Idempotent | GUARANTEE | Repeated measurement of post-collapse state = same outcome | `cycle2/invariants.py` |
| M5 | Collapse Replay Determinism | GUARANTEE | Same seed → same collapse outcome | `cycle2/invariants.py` |
| M6 | Confidence Bounds | GUARANTEE | confidence ∈ [0, 1] | `cycle2/invariants.py` |
| M7 | Post-Collapse Norm | GUARANTEE | Post-collapse state is unit vector | `cycle2/invariants.py` |

---

## Cycle 3 — Causality Invariants

| ID | Name | Type | Description | Module |
|---|---|---|---|---|
| C1 | Causal ID Monotonicity | GUARANTEE | causal_ids strictly increasing | `cycle3/timeline.py` |
| C2 | Predecessor Validity | GUARANTEE | predecessor_id = causal_id - 1 | `cycle3/causality_primitives.py` |
| C3 | CausalEvent Immutability | GUARANTEE | Frozen dataclass — no field mutation | `cycle3/causality_primitives.py` |
| C4 | No Deletion | GUARANTEE | No delete/rollback/revert methods exist | `cycle3/timeline.py` |
| C5 | Compensation Adds Only | GUARANTEE | Compensation creates new event, original unchanged | `cycle3/timeline.py` |
| C6 | PONR Monotonic Advance | GUARANTEE | sealed_up_to only increases | `cycle3/timeline.py` |
| C7 | PONR Blocks Compensation | GUARANTEE | Compensating sealed events raises error | `cycle3/timeline.py` |

---

## Cycle 4 — Quantum Error Invariants

| ID | Name | Type | Description | Module |
|---|---|---|---|---|
| E1 | Unrecoverable Bounds | GUARANTEE | Loss tracked ≥ Declared info loss | `cycle4/invariants.py` |
| E2 | No Free Restoration | GUARANTEE | Negative info loss forbidden | `cycle4/invariants.py` |
| E3 | Propagation Monotonicity | GUARANTEE | Unrecoverable loss never decreases | `cycle4/invariants.py` |
| E4 | Compensation Traceability | GUARANTEE | Correction acts as explicit compensation | `cycle4/invariants.py` |

## Cycle 5 — Quantum No-Go Boundaries

| ID | Name | Type | Description | Module |
|---|---|---|---|---|
| NG1 | No-Cloning Bound | PROHIBITION | Linear un-branching timeline required | `cycle5/invariants.py` |
| NG2 | No-Deleting Bound | PROHIBITION | History deletion/truncation forbidden | `cycle5/invariants.py` |
| NG3 | Confidence Collapse | PROHIBITION | Confidence > 0 requires info loss > 0 | `cycle5/invariants.py` |

---

## Cross-Cycle Compatibility

| Invariant Pair | Compatibility |
|---|---|
| I3 + C4 | Both enforce append-only logs. Cycle 3 wraps Cycle 1 events without touching C1 log. |
| I1 + M7 | Both enforce norm = 1. Post-collapse state satisfies C1's state validity requirement. |
| I7 + M5 | Both enforce deterministic replay. Orthogonal mechanisms; no conflict. |
| I4 + C1 | Both enforce strict monotonicity. Separate counters in separate systems; no conflict. |
| M3 + C4 | Both forbid deletion. Mutually reinforcing. |
| M2 + C5 | Information loss is declared (M2); compensation never erases the record (C5). |

---

## Composite Check

```bash
# Cycle 1 invariants
python -c "
from cycle1.state_evolution_engine import *
from cycle1.invariants import run_all_invariants
import math
amp = 1/math.sqrt(2)
e = SovereignStateEngine(StateVector({'0':complex(amp),'1':complex(amp)}))
e.register_rule('id', identity_rule)
e.observe(Observation('id', ()))
r = run_all_invariants(e)
print('C1 passed:', r.passed)
print('C1 failed:', r.failed)
"
```
