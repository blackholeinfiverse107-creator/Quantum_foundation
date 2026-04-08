# Marine Adapter Specification

This outlines the Marine Adapter's role acting as the translation layer between external simulations (e.g. Dhiraj's physical simulators) and the Domain-Agnostic Execution Engine.

## Purpose

The Marine Adapter encapsulates all ocean-domain variables, preventing them from leaking into the sequencing and determinism modules.

1. **Translation (`create_marine_update_event`)**: Converts Dhiraj's nested `{"zone_1": {"corrosion_rate": x}}` JSON formats directly into an agnostic Payload Dictionary destined for `ExecutionEvent` (specifically generating the `STATE_UPDATE` event_type).
2. **Transition Execution (`apply_event_payload`)**: Accepts untyped payload structures back from the execution hub upon sequencer approval, routing changes cleanly down to individual cached `ZoneState` models.
3. **Determinism Encoding (`get_state_hash`)**: Flattens marine structure parameters heavily formatted to 6th-float-precision independent of ordering to export a deterministic `.sha256()` integrity hash back to the generic validation cluster.

## Rules
👉 Adapter translates inputs into raw event format.  
👉 Engine accepts payload blindly and stamps causality.  
👉 Engine must NOT import `adapters.marine`.  
👉 Adapter implements `apply_event_payload(dict)` and `get_state_hash() -> str`.
