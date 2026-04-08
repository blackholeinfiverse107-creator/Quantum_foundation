# Interface Contract

This contract defines the strict boundaries for interaction with the generic Domain-Agnostic Deterministic Execution Engine. 

The core engine **DOES NOT** understand the contents of the `payload`. It ONLY enforces deterministic causality, node replication, and synchronization of events in a distributed manner.

## `ExecutionEvent` (Input)

Events proposed to the engine MUST adhere to the following schema.

```python
class ExecutionEvent:
    event_id: str        # Unique identifier for the event (e.g., UUID string)
    event_type: str      # String defining the type of the event (e.g., "STATE_UPDATE", "SYNC")
    payload: dict        # The domain-specific arbitrary payload dict
    timestamp: float     # Monotonic local timestamp of the proposal (for observability only, non-causal)
```

**Rule:** `payload` must contain serializable and deterministic types. The engine treats it as extremely opaque. All validations regarding the data schema must be handled by the Domain Adapter before or during transition extraction.

## `ExecutionResult` (Output)

Upon attempting to sequence and validate an event across the cluster, the hub returns an `ExecutionResult` reflecting the convergence success.

```python
class ExecutionResult:
    status: str          # "APPLIED" | "REJECTED" | "BUFFERED"
    causal_id: int       # The monotonically increasing sequenced causal ID
    state_hash: str      # Deterministic hash defining the global state at this causal_id
    consensus: bool      # True if all validating nodes agreed on the resulting state_hash
```

**Rule:** A `status` of `REJECTED` implies invariant violation or processing failure on the Adapter level, which will immediately abort engine progression if strict mode is toggled. `BUFFERED` occurs out of deterministic sequencing. `APPLIED` shows successful state injection.
