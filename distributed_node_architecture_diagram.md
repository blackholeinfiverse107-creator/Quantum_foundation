# Distributed Node Architecture Diagram

```mermaid
graph TD
    subgraph "Network Hub"
        Hub[Sequencing Engine]
        Log[Global Event Log]
    end

    subgraph "Node A (Originator)"
        HarnessA[FullStackHarness]
        ClockA[Logical Clock]
        BufferA[Event Buffer]
        NodeA[DistributedStateNode]
        NodeA --> HarnessA
        NodeA --> ClockA
        NodeA --> BufferA
    end

    subgraph "Node B (Peer)"
        HarnessB[FullStackHarness]
        ClockB[Logical Clock]
        BufferB[Event Buffer]
        NodeB[DistributedStateNode]
        NodeB --> HarnessB
        NodeB --> ClockB
        NodeB --> BufferB
    end

    subgraph "Node C (Peer)"
        HarnessC[FullStackHarness]
        ClockC[Logical Clock]
        BufferC[Event Buffer]
        NodeC[DistributedStateNode]
        NodeC --> HarnessC
        NodeC --> ClockC
        NodeC --> BufferC
    end

    NodeA -- "Propose EVOLVE/MEASURE" --> Hub
    Hub -- "Broadcast NetworkEvent(causal_id)" --> NodeA
    Hub -- "Broadcast NetworkEvent(causal_id)" --> NodeB
    Hub -- "Broadcast NetworkEvent(causal_id)" --> NodeC

    classDef node fill:#f9f,stroke:#333,stroke-width:2px;
    classDef hub fill:#00d,color:#fff,stroke:#333,stroke-width:4px;
    class Hub hub;
    class NodeA,NodeB,NodeC node;
```

### Key Components
- **FullStackHarness**: The local quantum state and evolution engine (Cycles 1-8).
- **Sequencing Engine**: Assigns deterministic `causal_id` to proposed events.
- **Event Buffer**: Handles out-of-order network arrival to ensure sequential application.
- **Logical Clock**: Tracks the node's progress through the global causal timeline.
