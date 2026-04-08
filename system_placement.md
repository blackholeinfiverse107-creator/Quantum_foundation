# System Placement Analysis

This document evaluates the architectural placement options for integrating the Domain-Agnostic Deterministic Execution Engine. We are analyzing where the sequence synchronization loop best solves pipeline challenges without dictating domain behavior. 

**DO NOT FINALIZE - FOR ANALYSIS ONLY**

## 1. KESHAV (Validation Layer)

**Pros:**
- Matches Keshav's primary objective: observing mutations and applying drift/constraint analysis algorithms without interfering in primary simulation data.
- Can ingest `ExecutionEvent` outputs and construct real-time dashboards mapping convergence.
- The Engine’s Strict Output (`REJECTED`) explicitly supports strict invariant auditing and blocking.

**Cons:**
- The Deterministic Engine is highly stateful (it buffers missing Causal IDs and resolves hashes). The Validation Layer traditionally scopes lightly to reduce IO footprint. Turning Keshav into a heavy synchronization node could bottleneck verification.

## 2. BHIV Core (Execution Validation Layer)

**Pros:**
- Direct alignment with the central authority logic. BHIV orchestrates distributed simulators.
- The Hub naturally fits here: the Core takes simulation deltas natively (e.g. from Dhiraj's pipeline) and imposes `causal_id` BEFORE farming out to sub-nodes or validation hooks.
- Forces all subsequent layers down the pipeline (UI, Keshav, Sinks) to rely exactly on one timeline without worrying about out-of-order race conditions. 

**Cons:**
- Tying the state buffer back into BHIV Core execution tightly couples the Hub component as a single point of failure. If the Engine is blocked (e.g. by a rejected event), all pipelines attached directly to BHIV might halt until reconciled.

## 3. Other (Middleware / Sidecar Architecture)

**Pros:**
- Deploys the Execution Interface as an API sidecar attached to any node that requests it. The Hub sits separate as an isolated orchestration microservice.
- Adapters (like `marine_adapter.py`) stay extremely local to where they are needed (i.e. Dhiraj's boundary nodes) while only raw `ExecutionEvent` dictionaries pass over the wire.

**Cons:**
- Multiplies the moving components and network dependencies, adding jitter before sequence resolution. 

## Conclusion
Each deployment model respects the newly crafted domain-agnostic interface boundaries. For strict replayability, **BHIV Core** offers the tightest sequencer guarantee, while **KESHAV** provides an audit-first abstraction. No final placement architecture is mandated at this phase.
