# CGCS Quick Start Guide

## What is CGCS?

CGCS (Consent-Gated Coherence System) is a **refusal-first coordination framework** for AI agents that prioritizes safety and consent. It's designed to forget by default and requires explicit human approval for all operations.

## Key Features

✅ **Consent-First**: All actions denied by default  
✅ **Bounded Roles**: Agents work within strict permission boundaries  
✅ **Fatigue Tracking**: Mandatory rest periods prevent burnout  
✅ **Opt-In Memory**: Memories only stored with consent  
✅ **Loop Prevention**: Automatic detection and de-escalation  

## Installation

```bash
# Clone the repository
git clone https://github.com/FractalFuryan/cgcs-ai-robotics.git
cd cgcs-ai-robotics

# No dependencies needed - pure Python!
```

## 5-Minute Tutorial

### Step 1: Initialize Components

```python
from cgcs import ConsentManager, Agent, Role, RoleType, FatigueTracker, Coordinator
from cgcs.consent import ConsentType

# Create the core system components
consent_manager = ConsentManager()
fatigue_tracker = FatigueTracker()
coordinator = Coordinator(
    consent_manager=consent_manager,
    fatigue_tracker=fatigue_tracker
)
```

### Step 2: Create an Agent

```python
# Create an agent (it can't do anything yet - refusal-first!)
agent = Agent(
    agent_id="my_agent",
    name="My First Agent",
    consent_manager=consent_manager,
    fatigue_tracker=fatigue_tracker
)

coordinator.register_agent(agent)
```

### Step 3: Request and Grant Consent

```python
# Request consent to assign a role
consent_req = consent_manager.request_consent(
    request_id="assign_role_1",
    consent_type=ConsentType.ROLE_ASSIGNMENT,
    requester=agent.agent_id,
    description="Allow agent to become a task executor"
)

# Human grants consent (in real use, this would be interactive)
consent_manager.grant_consent("assign_role_1")
```

### Step 4: Assign a Bounded Role

```python
# Define what the agent is allowed to do
executor_role = Role(
    role_id="executor_1",
    role_type=RoleType.EXECUTOR,
    name="Task Executor",
    description="Can execute and report on tasks",
    permitted_actions={"execute_task", "report_status", "request_help"}
)

# Assign the role with consent
agent.assign_role(executor_role, consent_id="assign_role_1")
```

### Step 5: Coordinate Actions

```python
# Now the agent can perform actions (with loop prevention!)
result = coordinator.coordinate_action(
    agent.agent_id,
    "execute_task",
    context="Process user data"
)

if result:
    print("✓ Action completed successfully")
    
    # Check fatigue
    state = fatigue_tracker.get_state(agent.agent_id)
    print(f"Agent energy: {state.energy}%")
else:
    print("✗ Action prevented (loop detection, fatigue, or no permission)")
```

## Common Patterns

### Working with Memory

```python
from cgcs import MemoryStore

# Create memory store with consent integration
memory = MemoryStore(consent_manager=consent_manager)

# Register a cue (trigger for memory retrieval)
memory.register_cue(
    cue_id="task_complete",
    pattern="task_completed",
    description="Triggered when tasks finish"
)

# Request consent to store memory
mem_consent = consent_manager.request_consent(
    request_id="store_mem_1",
    consent_type=ConsentType.MEMORY_STORE,
    requester=agent.agent_id,
    description="Remember successful task completion"
)
consent_manager.grant_consent("store_mem_1")

# Store memory (with consent)
memory.store_memory(
    memory_id="mem_1",
    agent_id=agent.agent_id,
    content="Successfully completed data processing task",
    cues={"task_complete"},
    consent_id="store_mem_1"
)

# Later: forget everything (default behavior)
memory.forget_all()
```

### Handling Fatigue

```python
# Check if agent needs rest
if not fatigue_tracker.can_act(agent.agent_id):
    print("Agent needs rest!")
    fatigue_tracker.start_rest(agent.agent_id)
    
# Check state
state = fatigue_tracker.get_state(agent.agent_id)
print(f"Energy: {state.energy}%")
print(f"Status: {state.level.value}")
```

### Loop Prevention

```python
# The coordinator automatically detects loops
for i in range(10):
    result = coordinator.coordinate_action(
        agent.agent_id,
        "same_action",  # Repetitive!
        context="same context"
    )
    
    if not result:
        escalation = coordinator.get_escalation_level(agent.agent_id)
        print(f"Loop detected! Escalation level: {escalation}")
        
        # Reset if needed
        if coordinator.is_circuit_broken(agent.agent_id):
            print("Circuit breaker activated - agent suspended")
            coordinator.reset_circuit_breaker(agent.agent_id)
        break
```

## Examples

Run the included examples:

```bash
# Basic example showing all features
python example.py

# Comprehensive validation
python validate.py
```

## Configuration

Edit `config.yaml` to customize:

- Consent defaults
- Fatigue parameters (energy cost, recovery rate)
- Memory behavior
- Loop detection thresholds
- Circuit breaker settings

## Next Steps

1. Read `README.md` for full documentation
2. Check `DESIGN_NOTES.md` for design rationale
3. Explore the example scripts
4. Build your own consent-gated agents!

## Why Use CGCS?

Use CGCS when you need:

- **Safe multi-agent coordination** with clear boundaries
- **Audit trails** of all agent actions and consents
- **Sustainable operation** with fatigue management
- **Privacy-first memory** that forgets by default
- **Protection from loops** and runaway behaviors

## Philosophy

> "Safe defaults are better than convenient defaults."

CGCS prioritizes safety, transparency, and sustainability. Every action requires consent, every agent has limits, and nothing is remembered unless explicitly authorized.

## License

MIT License - See LICENSE file for details.
