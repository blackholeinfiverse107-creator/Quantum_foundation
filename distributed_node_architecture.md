# Distributed Quantum Node Architecture

## Overview
The Distributed Quantum Node system extends the sovereign quantum foundation into a multi-node environment. Each node maintains a local copy of the global Hilbert space state and synchronizes evolution through a deterministic event propagation model.

## Core Component: DistributedStateNode
A `DistributedStateNode` is a computation unit that encapsulates a `FullStackHarness`. It is responsible for local state observation, initiating global transitions, and maintaining causal consistency with peer nodes.

### Responsibilities
- **Observe**: Provide a read-only interface to the current state amplitudes.
- **Evolve**: Propose a unitary evolution. This is broadcast as a `NetworkEvent`.
- **Measure**: Propose a state collapse. This is broadcast as a `NetworkEvent` containing the seed.
- **Propagate**: Emit local events to the network simulation.
- **Consensus/Ordering**: Ensure that events from all nodes are applied in a deterministic causal order.

## Communication Model
Nodes communicate via **Network Events**. A network event contains:
- `origin_node_id`: Identity of the node that initiated the event.
- `event_type`: "EVOLVE" or "MEASURE".
- `payload`: Rule name for evolution or (token_id, seed) for measurement.
- `causal_id`: The global sequence index for this event.

### Logical Clock & Ordering
Deterministic replay requires that all nodes arrive at the same state given the same event stream.
- Each node maintains a local `LogicalClock`.
- Events are applied to the local `FullStackHarness` only when they match the next expected `causal_id`.
- Out-of-order events are buffered until their predecessors arrive.
- Conflicting events at the same `causal_id` are rejected or resolved via a tie-breaking rule (e.g., node_id priority).

## Node Lifecycle
1. **Bootstrap**: Initialize with a shared genesis state and a list of peer nodes.
2. **Active Evolution**: 
    - Locally triggered operations are broadcast.
    - Remotely triggered operations are received and applied.
3. **Measurement Sync**: 
    - When a node measures, it broadcasts the results/seed.
    - Peers apply the same measurement with the same seed to collapse their local state identically.
4. **Validation**: Continuous invariant checks ensure local state never diverges from the global consensus.

## Determinism Guarantees
- **Local Determinism**: `FullStackHarness` ensures local operations are deterministic.
- **Network Determinism**: Causal ordering of the event stream ensures all nodes process the same transitions.
- **Replay Stability**: The entire network event stream can be hashed and replayed to verify system-wide consistency.
