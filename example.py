"""
Example usage of the CGCS framework.

This demonstrates the core features:
- Consent-first behavior
- Fatigue-aware role coordination
- Opt-in, cue-based memory
- Loop prevention and de-escalation
"""

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


def main():
    print("=== CGCS Framework Example ===\n")
    
    # Initialize core components
    consent_manager = ConsentManager()
    fatigue_tracker = FatigueTracker()
    memory_store = MemoryStore(consent_manager=consent_manager)
    coordinator = Coordinator(
        consent_manager=consent_manager,
        fatigue_tracker=fatigue_tracker,
        memory_store=memory_store
    )
    
    print("1. Creating agents with refusal-first approach...")
    # Create agents
    agent1 = Agent(
        agent_id="agent_1",
        name="Task Executor",
        consent_manager=consent_manager,
        fatigue_tracker=fatigue_tracker
    )
    
    # Register with coordinator
    coordinator.register_agent(agent1)
    print(f"   - Created agent: {agent1.name}")
    
    # Try to perform action without role (will fail - refusal-first)
    print("\n2. Attempting action without role (refusal-first)...")
    result = agent1.perform_action("execute_task")
    print(f"   - Action allowed: {result} (Expected: False)")
    
    # Request consent for role assignment
    print("\n3. Requesting consent for role assignment...")
    consent_req = consent_manager.request_consent(
        request_id="role_assign_1",
        consent_type=ConsentType.ROLE_ASSIGNMENT,
        requester=agent1.agent_id,
        description="Assign executor role to agent_1"
    )
    print(f"   - Consent request created: {consent_req.request_id}")
    print(f"   - Status: {consent_req.status.value}")
    
    # Grant consent
    consent_manager.grant_consent("role_assign_1")
    print("   - Consent granted!")
    
    # Create and assign role with consent
    print("\n4. Assigning bounded role with consent...")
    executor_role = Role(
        role_id="executor_1",
        role_type=RoleType.EXECUTOR,
        name="Task Executor",
        description="Can execute tasks and report status",
        permitted_actions={"execute_task", "report_status"}
    )
    
    result = agent1.assign_role(executor_role, consent_id="role_assign_1")
    print(f"   - Role assigned: {result}")
    print(f"   - Current role: {agent1.get_current_role().name}")
    
    # Now action should work
    print("\n5. Performing actions with fatigue tracking...")
    for i in range(5):
        result = coordinator.coordinate_action(
            agent1.agent_id,
            "execute_task",
            context=f"Task {i+1}"
        )
        fatigue_state = fatigue_tracker.get_state(agent1.agent_id)
        print(f"   - Action {i+1}: {result}, Energy: {fatigue_state.energy:.1f}, Level: {fatigue_state.level.value}")
    
    # Demonstrate loop prevention
    print("\n6. Demonstrating loop prevention...")
    print("   - Attempting same action repeatedly...")
    for i in range(5):
        result = coordinator.coordinate_action(
            agent1.agent_id,
            "execute_task",
            context="Same task"
        )
        escalation = coordinator.get_escalation_level(agent1.agent_id)
        print(f"   - Attempt {i+1}: {result}, Escalation level: {escalation}")
        
        if not result:
            print("   - Loop detected! Action prevented.")
            break
    
    # Demonstrate memory with consent
    print("\n7. Demonstrating opt-in memory (forget by default)...")
    
    # Register a memory cue
    cue = memory_store.register_cue(
        cue_id="task_complete",
        pattern="task_completed",
        description="Triggered when a task completes"
    )
    print(f"   - Registered memory cue: {cue.cue_id}")
    
    # Try to store memory without consent (will fail)
    print("   - Attempting to store memory without consent...")
    result = memory_store.store_memory(
        memory_id="mem_1",
        agent_id=agent1.agent_id,
        content="Task was completed successfully",
        cues={"task_complete"}
    )
    print(f"   - Memory stored: {result is not None} (Expected: False - no consent)")
    
    # Request and grant memory consent
    print("   - Requesting consent to store memory...")
    mem_consent = consent_manager.request_consent(
        request_id="mem_store_1",
        consent_type=ConsentType.MEMORY_STORE,
        requester=agent1.agent_id,
        description="Store task completion memory"
    )
    consent_manager.grant_consent("mem_store_1")
    print("   - Consent granted!")
    
    # Now store memory
    result = memory_store.store_memory(
        memory_id="mem_1",
        agent_id=agent1.agent_id,
        content="Task was completed successfully",
        cues={"task_complete"},
        consent_id="mem_store_1"
    )
    print(f"   - Memory stored: {result is not None}")
    print(f"   - Total memories: {memory_store.get_memory_count()}")
    
    # Demonstrate forgetting (default behavior)
    print("\n8. Demonstrating forget-by-default...")
    print(f"   - Current memory count: {memory_store.get_memory_count()}")
    count = memory_store.forget_all()
    print(f"   - Forgot {count} memories")
    print(f"   - Final memory count: {memory_store.get_memory_count()}")
    
    print("\n=== CGCS Framework Example Complete ===")


if __name__ == "__main__":
    main()
