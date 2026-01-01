# Consent-Gated Coherence System (CGCS)

A refusal-first coordination framework where agents act through bounded roles, recover through rest, and remember only by explicit human consent.

## Overview

CGCS is a reference implementation and design framework focused on safe, consent-based agent coordination. This project is **designed to forget by default** and implements several key safety mechanisms:

- **Consent-first behavior**: All actions require explicit approval
- **Fatigue-aware role coordination**: Agents work in bounded roles with mandatory rest periods
- **Opt-in, cue-based memory**: Memories are stored and retrieved only with explicit consent
- **Loop prevention and de-escalation**: Automatic detection and prevention of infinite loops

## Core Principles

### 1. Refusal-First Approach
By default, all actions are denied until explicit consent is granted. This ensures that agents cannot perform unauthorized actions.

### 2. Bounded Roles
Agents operate within well-defined roles that limit their permitted actions. Roles must be explicitly assigned with consent.

### 3. Fatigue Awareness
Agents track energy expenditure and must rest periodically to recover. This prevents overuse and ensures sustainable operation.

### 4. Forget by Default
The system does not persist memories unless explicitly authorized. When sessions end, memories are cleared unless consent to store them was granted.

### 5. Loop Prevention
The coordinator monitors action patterns and prevents agents from entering infinite loops through escalation and circuit-breaker mechanisms.

## Installation

```bash
# Clone the repository
git clone https://github.com/FractalFuryan/cgcs-ai-robotics.git
cd cgcs-ai-robotics

# The framework is pure Python with no external dependencies
```

## Quick Start

```python
from cgcs import (
    ConsentManager,
    Agent,
    Role,
    RoleType,
    FatigueTracker,
    MemoryStore,
    Coordinator,
)
from cgcs.consent import ConsentType

# Initialize core components
consent_manager = ConsentManager()
fatigue_tracker = FatigueTracker()
memory_store = MemoryStore(consent_manager=consent_manager)
coordinator = Coordinator(
    consent_manager=consent_manager,
    fatigue_tracker=fatigue_tracker,
    memory_store=memory_store
)

# Create an agent
agent = Agent(
    agent_id="agent_1",
    name="Task Executor",
    consent_manager=consent_manager,
    fatigue_tracker=fatigue_tracker
)

# Request consent for role assignment
consent_req = consent_manager.request_consent(
    request_id="role_assign_1",
    consent_type=ConsentType.ROLE_ASSIGNMENT,
    requester=agent.agent_id,
    description="Assign executor role"
)

# Grant consent (in real use, this would be done by a human)
consent_manager.grant_consent("role_assign_1")

# Create and assign a bounded role
executor_role = Role(
    role_id="executor_1",
    role_type=RoleType.EXECUTOR,
    name="Task Executor",
    description="Can execute tasks",
    permitted_actions={"execute_task", "report_status"}
)
agent.assign_role(executor_role, consent_id="role_assign_1")

# Coordinate action with loop prevention
coordinator.register_agent(agent)
result = coordinator.coordinate_action(
    agent.agent_id,
    "execute_task",
    context="Sample task"
)
```

See `example.py` for a complete demonstration.

## Architecture

### Core Components

#### ConsentManager (`cgcs/consent.py`)
- Manages all consent requests and approvals
- Implements refusal-first policy
- Tracks consent status and expiration
- Supports different consent types (action, memory, role assignment)

#### Agent (`cgcs/agent.py`)
- Represents an autonomous agent in the system
- Operates through assigned roles
- Checks consent before actions
- Integrates with fatigue tracking

#### Role (`cgcs/agent.py`)
- Defines bounded permissions for agents
- Specifies permitted actions
- Can require consent for assignment
- Supports time-limited assignments

#### FatigueTracker (`cgcs/fatigue.py`)
- Monitors agent energy levels
- Enforces mandatory rest periods
- Tracks action counts
- Implements recovery mechanisms

#### MemoryStore (`cgcs/memory.py`)
- Manages opt-in memory storage
- Implements cue-based retrieval
- Requires consent for store and retrieve operations
- Forgets by default (no persistence)

#### Coordinator (`cgcs/coordinator.py`)
- Coordinates multiple agents
- Detects and prevents loops
- Implements de-escalation strategies
- Manages circuit breakers for problematic agents

## Configuration

See `config.yaml` for configuration options. Key settings include:

- Consent behavior (refusal-first)
- Fatigue parameters (energy cost, rest duration, recovery rate)
- Memory settings (forget by default, consent requirements)
- Loop prevention (window size, repetition limits)
- De-escalation (escalation levels, circuit breakers)

## Design Notes

### Why Refusal-First?
Traditional systems often operate on an allowlist or blocklist basis. CGCS inverts this: everything is blocked by default, and only explicitly consented actions are permitted. This provides stronger safety guarantees.

### Why Fatigue Tracking?
Unbounded agent operation can lead to resource exhaustion and unstable behavior. Fatigue tracking ensures agents operate sustainably with mandatory rest periods.

### Why Forget by Default?
Memory persistence creates long-term dependencies and potential privacy issues. By forgetting by default, CGCS ensures that data is only retained when explicitly necessary and authorized.

### Why Loop Prevention?
Autonomous agents can enter infinite loops or repetitive behavior patterns. The coordinator detects these patterns and implements de-escalation strategies, including temporary suspension via circuit breakers.

## Use Cases

CGCS is designed for scenarios requiring:

- **Safe agent coordination**: Multiple agents working together with consent-based permissions
- **Bounded autonomy**: Agents that operate independently but within strict limits
- **Privacy-conscious operation**: Systems that should forget unless told to remember
- **Reliable operation**: Fatigue-aware scheduling prevents burnout and ensures sustainability
- **Loop-safe execution**: Prevention of infinite loops and runaway behaviors

## Testing

Run the example to see the framework in action:

```bash
python example.py
```

This demonstrates:
- Refusal-first consent behavior
- Role-based action permissions
- Fatigue tracking and energy management
- Loop detection and prevention
- Opt-in memory with forget-by-default

## Contributing

This is a reference implementation demonstrating consent-gated coordination patterns. Contributions that enhance the core principles are welcome.

## License

See LICENSE file for details.

## Design Philosophy

CGCS is built on the principle that **safe defaults are better than convenient defaults**. By requiring explicit consent, enforcing rest periods, and forgetting by default, the system prioritizes safety and sustainability over convenience.

The framework is intentionally simple and transparent, with clear boundaries and explicit state management. This makes it easier to understand, audit, and trust.

## Further Reading

See `DESIGN_NOTES.md` for detailed design rationale and implementation notes.
