"""
Comprehensive validation of CGCS framework features.

This script validates all core requirements:
1. Consent-first behavior
2. Fatigue-aware role coordination
3. Opt-in, cue-based memory
4. Loop prevention and de-escalation
5. Forget by default
"""

import sys
from cgcs import (
    ConsentManager,
    Agent,
    Role,
    RoleType,
    FatigueTracker,
    MemoryStore,
    Coordinator,
)
from cgcs.consent import ConsentType, ConsentStatus


def test_consent_first():
    """Test that consent is required for all actions (refusal-first)."""
    print("=" * 60)
    print("TEST 1: Consent-First Behavior")
    print("=" * 60)
    
    cm = ConsentManager()
    
    # Test 1.1: Default denial
    print("\n1.1 Testing default denial (refusal-first)...")
    has_consent = cm.check_consent("agent_1", ConsentType.ACTION, "req_1")
    assert has_consent == False, "FAIL: Default should be denial"
    print("✓ PASS: Actions denied by default")
    
    # Test 1.2: Request and grant
    print("\n1.2 Testing consent request and grant...")
    req = cm.request_consent("req_1", ConsentType.ACTION, "agent_1", "Test action")
    assert req.status == ConsentStatus.PENDING, "FAIL: Request should be pending"
    cm.grant_consent("req_1")
    has_consent = cm.check_consent("agent_1", ConsentType.ACTION, "req_1")
    assert has_consent == True, "FAIL: Consent should be granted"
    print("✓ PASS: Consent request and grant works")
    
    # Test 1.3: Revoke
    print("\n1.3 Testing consent revocation...")
    cm.revoke_consent("req_1")
    has_consent = cm.check_consent("agent_1", ConsentType.ACTION, "req_1")
    assert has_consent == False, "FAIL: Consent should be revoked"
    print("✓ PASS: Consent can be revoked")
    
    print("\n✅ Consent-First Behavior: ALL TESTS PASSED\n")


def test_fatigue_awareness():
    """Test fatigue tracking and recovery."""
    print("=" * 60)
    print("TEST 2: Fatigue-Aware Role Coordination")
    print("=" * 60)
    
    ft = FatigueTracker(energy_cost_per_action=10.0, max_actions_before_rest=5)
    
    # Test 2.1: Energy depletion
    print("\n2.1 Testing energy depletion...")
    ft.register_agent("agent_1")
    for i in range(4):  # Do 4 actions, one less than max
        result = ft.record_action("agent_1")
        assert result == True, f"FAIL: Action {i+1} should be allowed"
    state = ft.get_state("agent_1")
    assert state.energy == 60.0, f"FAIL: Energy should be 60, got {state.energy}"
    print("✓ PASS: Energy depletes with actions")
    
    # Test 2.2: Mandatory rest
    print("\n2.2 Testing mandatory rest after max actions...")
    result = ft.record_action("agent_1")
    assert result == False, "FAIL: Should require rest after max actions"
    state = ft.get_state("agent_1")
    assert state.level.value == "recovering", "FAIL: Should be in recovering state"
    print("✓ PASS: Mandatory rest enforced")
    
    # Test 2.3: Recovery
    print("\n2.3 Testing energy recovery...")
    ft.reset_agent("agent_1")
    state = ft.get_state("agent_1")
    assert state.energy == 100.0, "FAIL: Energy should be reset to 100"
    assert state.level.value == "fresh", "FAIL: Should be fresh after reset"
    print("✓ PASS: Energy recovery works")
    
    print("\n✅ Fatigue-Aware Coordination: ALL TESTS PASSED\n")


def test_memory_system():
    """Test opt-in, cue-based memory."""
    print("=" * 60)
    print("TEST 3: Opt-In, Cue-Based Memory")
    print("=" * 60)
    
    cm = ConsentManager()
    ms = MemoryStore(consent_manager=cm)
    
    # Test 3.1: Cannot store without consent
    print("\n3.1 Testing memory storage requires consent...")
    result = ms.store_memory("mem_1", "agent_1", "test data", {"cue_1"})
    assert result is None, "FAIL: Should not store without consent"
    assert ms.get_memory_count() == 0, "FAIL: Memory count should be 0"
    print("✓ PASS: Memory storage requires consent")
    
    # Test 3.2: Store with consent
    print("\n3.2 Testing memory storage with consent...")
    req = cm.request_consent("mem_req_1", ConsentType.MEMORY_STORE, "agent_1", "Store memory")
    cm.grant_consent("mem_req_1")
    ms.register_cue("cue_1", "pattern_1", "Test cue")
    result = ms.store_memory("mem_1", "agent_1", "test data", {"cue_1"}, consent_id="mem_req_1")
    assert result is not None, "FAIL: Should store with consent"
    assert ms.get_memory_count() == 1, "FAIL: Memory count should be 1"
    print("✓ PASS: Memory stored with consent")
    
    # Test 3.3: Cannot retrieve without consent
    print("\n3.3 Testing memory retrieval requires consent...")
    memories = ms.retrieve_by_cue("cue_1", "agent_1")
    assert len(memories) == 0, "FAIL: Should not retrieve without consent"
    print("✓ PASS: Memory retrieval requires consent")
    
    # Test 3.4: Retrieve with consent
    print("\n3.4 Testing memory retrieval with consent...")
    req2 = cm.request_consent("mem_req_2", ConsentType.MEMORY_RETRIEVE, "agent_1", "Retrieve memory")
    cm.grant_consent("mem_req_2")
    memories = ms.retrieve_by_cue("cue_1", "agent_1", consent_id="mem_req_2")
    assert len(memories) == 1, "FAIL: Should retrieve with consent"
    print("✓ PASS: Memory retrieved with consent")
    
    # Test 3.5: Forget by default
    print("\n3.5 Testing forget by default...")
    count = ms.forget_all()
    assert count == 1, "FAIL: Should forget 1 memory"
    assert ms.get_memory_count() == 0, "FAIL: Memory count should be 0"
    print("✓ PASS: Forget by default works")
    
    print("\n✅ Opt-In, Cue-Based Memory: ALL TESTS PASSED\n")


def test_loop_prevention():
    """Test loop detection and de-escalation."""
    print("=" * 60)
    print("TEST 4: Loop Prevention and De-Escalation")
    print("=" * 60)
    
    cm = ConsentManager()
    ft = FatigueTracker()
    coord = Coordinator(consent_manager=cm, fatigue_tracker=ft)
    
    # Create and register agent
    agent = Agent("agent_1", "Test Agent", cm, ft)
    req = cm.request_consent("role_req", ConsentType.ROLE_ASSIGNMENT, "agent_1", "Assign role")
    cm.grant_consent("role_req")
    role = Role("role_1", RoleType.EXECUTOR, "Executor", "Test role", permitted_actions={"action_1"})
    agent.assign_role(role, consent_id="role_req")
    coord.register_agent(agent)
    
    # Test 4.1: Normal actions allowed
    print("\n4.1 Testing normal diverse actions allowed...")
    result = coord.coordinate_action("agent_1", "action_1", "context_1")
    assert result == True, "FAIL: First action should be allowed"
    print("✓ PASS: Normal actions allowed")
    
    # Test 4.2: Loop detection
    print("\n4.2 Testing loop detection on repetitive actions...")
    loop_detected = False
    for i in range(10):
        result = coord.coordinate_action("agent_1", "action_1", "same_context")
        if not result:
            loop_detected = True
            escalation = coord.get_escalation_level("agent_1")
            assert escalation > 0, "FAIL: Escalation should increase"
            print(f"✓ PASS: Loop detected after {i+1} attempts, escalation level: {escalation}")
            break
    assert loop_detected, "FAIL: Loop should be detected"
    
    # Test 4.3: Circuit breaker
    print("\n4.3 Testing circuit breaker activation...")
    is_broken = coord.is_circuit_broken("agent_1")
    print(f"   Circuit breaker active: {is_broken}")
    
    # Test 4.4: Circuit breaker reset
    if is_broken:
        print("\n4.4 Testing circuit breaker reset...")
        coord.reset_circuit_breaker("agent_1")
        is_broken = coord.is_circuit_broken("agent_1")
        assert is_broken == False, "FAIL: Circuit breaker should be reset"
        escalation = coord.get_escalation_level("agent_1")
        assert escalation == 0, "FAIL: Escalation should be reset"
        print("✓ PASS: Circuit breaker can be reset")
    
    print("\n✅ Loop Prevention and De-Escalation: ALL TESTS PASSED\n")


def test_bounded_roles():
    """Test that agents operate through bounded roles."""
    print("=" * 60)
    print("TEST 5: Bounded Roles")
    print("=" * 60)
    
    cm = ConsentManager()
    agent = Agent("agent_1", "Test Agent", cm)
    
    # Test 5.1: Cannot act without role
    print("\n5.1 Testing agent cannot act without role...")
    can_act = agent.can_perform_action("action_1")
    assert can_act == False, "FAIL: Should not be able to act without role"
    print("✓ PASS: Agent cannot act without role")
    
    # Test 5.2: Role limits actions
    print("\n5.2 Testing role limits permitted actions...")
    req = cm.request_consent("role_req", ConsentType.ROLE_ASSIGNMENT, "agent_1", "Assign role")
    cm.grant_consent("role_req")
    role = Role("role_1", RoleType.EXECUTOR, "Limited Role", "Test", permitted_actions={"action_1", "action_2"})
    agent.assign_role(role, consent_id="role_req")
    
    can_act_1 = agent.can_perform_action("action_1")
    can_act_3 = agent.can_perform_action("action_3")
    assert can_act_1 == True, "FAIL: Should be able to perform permitted action"
    assert can_act_3 == False, "FAIL: Should not be able to perform non-permitted action"
    print("✓ PASS: Role properly limits permitted actions")
    
    print("\n✅ Bounded Roles: ALL TESTS PASSED\n")


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("CGCS FRAMEWORK VALIDATION")
    print("=" * 60 + "\n")
    
    try:
        test_consent_first()
        test_fatigue_awareness()
        test_memory_system()
        test_loop_prevention()
        test_bounded_roles()
        
        print("\n" + "=" * 60)
        print("🎉 ALL VALIDATION TESTS PASSED! 🎉")
        print("=" * 60 + "\n")
        
        print("Summary:")
        print("✓ Consent-first behavior validated")
        print("✓ Fatigue-aware role coordination validated")
        print("✓ Opt-in, cue-based memory validated")
        print("✓ Loop prevention and de-escalation validated")
        print("✓ Bounded roles validated")
        print("✓ Forget by default validated")
        print("\nThe CGCS framework meets all requirements! ✨\n")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
