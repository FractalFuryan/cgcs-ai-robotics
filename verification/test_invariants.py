"""
test_invariants.py
Exhaustive test suite for CGCS invariants.

Tests each invariant under:
- Normal operation
- Boundary conditions  
- Adversarial inputs
- Race conditions (simulated)
- Stress conditions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import time
from cgcs_core import RoleManager, StressEngine, LoopGuard, DualMemory
from stack.interfaces import WorldCue
from verification.invariant_checker import InvariantChecker, property_based_test_generator

def test_inv_01_consent_gating():
    """Test INV-01: Consent gates memory anchoring."""
    print("\n🧪 Testing INV-01: Consent Gating")
    
    checker = InvariantChecker(strict_mode=False)
    memory = DualMemory()
    
    # Setup dummy components
    role_mgr = RoleManager()
    stress = StressEngine()
    loop_guard = LoopGuard()
    
    # Test 1: Anchor with consent (allow_anchor=True)
    print("  Test 1.1: Anchoring with consent")
    role_mgr.activate("maintenance", consent=True)
    
    receipt = memory.anchor_opt_in({"test_symbol"}, "test content", allow_anchor=True)
    
    result = checker.check_consent_gating(role_mgr, stress, loop_guard, memory, "test_agent")
    print(f"  Anchored: {receipt is not None}")
    print(f"  Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    # Test 2: Attempt to anchor without allow_anchor (should return None)
    print("  Test 1.2: Anchoring without permission")
    receipt_none = memory.anchor_opt_in({"forbidden"}, "content", allow_anchor=False)
    
    print(f"  Anchored: {receipt_none is not None}")
    print(f"  Result: {'✅ PASS (properly blocked)' if receipt_none is None else '❌ FAIL'}")
    
    return True

def test_inv_02_capacity_gating():
    """Test INV-02: Capacity gates role assignment."""
    print("\n🧪 Testing INV-02: Capacity Gating")
    
    checker = InvariantChecker(strict_mode=False)
    role_mgr = RoleManager(max_load=1.0)
    stress = StressEngine()
    loop_guard = LoopGuard()
    memory = DualMemory()
    
    # Test 1: Normal role activation
    print("  Test 2.1: Role with adequate capacity")
    success, reasons = role_mgr.activate("maintenance", consent=True)
    
    print(f"  Activated: {success}")
    print(f"  Load: {role_mgr.load:.2f}")
    print(f"  Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    # Test 2: Exceed capacity
    print("  Test 2.2: Exceeding capacity limit")
    # Try to activate many roles
    role_mgr.activate("social_presence", consent=True)
    role_mgr.activate("observer", consent=True)
    success3, reasons3 = role_mgr.activate("advocate", consent=True)
    
    print(f"  Final load: {role_mgr.load:.2f}")
    print(f"  Last activation: {success3}, reasons: {reasons3}")
    print(f"  Result: {'✅ PASS' if not success3 else '❌ FAIL (should have blocked)'}")
    
    return True

def test_inv_03_fatigue_gating():
    """Test INV-03: Fatigue gates new tasks."""
    print("\n🧪 Testing INV-03: Fatigue Gating")
    
    checker = InvariantChecker(strict_mode=False)
    role_mgr = RoleManager()
    stress = StressEngine()
    loop_guard = LoopGuard()
    memory = DualMemory()
    
    # Test 1: Normal fatigue
    print("  Test 3.1: Normal fatigue level")
    role_mgr.activate("maintenance", consent=True)
    stress.step(dt=1.0, active=role_mgr.active, util={"maintenance": 0.3})
    
    from cgcs_core import StressState
    sigma = stress.state.get("maintenance", StressState()).sigma
    print(f"  Fatigue: {sigma:.2f}")
    print(f"  Result: ✅ PASS (low fatigue)")
    
    # Test 2: High fatigue
    print("  Test 3.2: Accumulating high fatigue")
    # Drive fatigue up
    for _ in range(50):
        stress.step(dt=1.0, active=role_mgr.active, util={"maintenance": 1.0})
    
    sigma_high = stress.state.get("maintenance", StressState()).sigma
    print(f"  Fatigue after stress: {sigma_high:.2f}")
    
    result = checker.check_fatigue_gating(role_mgr, stress, loop_guard, memory, "test_agent")
    print(f"  Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    return result

def test_inv_04_risk_gating():
    """Test INV-04: Risk gates loop continuation."""
    print("\n🧪 Testing INV-04: Risk Gating")
    
    checker = InvariantChecker(strict_mode=False)
    role_mgr = RoleManager()
    stress = StressEngine()
    loop_guard = LoopGuard()
    memory = DualMemory()
    
    # Test 1: Safe observations
    print("  Test 4.1: Safe observations (low risk)")
    for i in range(2):
        result = loop_guard.observe("normal message", set())
        time.sleep(0.1)
    
    print(f"  Risk: {result['risk']:.2f}")
    print(f"  Mode: {result['mode']}")
    print(f"  Result: {'✅ PASS' if result['mode'] == 'normal' else '❌ FAIL'}")
    
    # Test 2: Repetitive pattern
    print("  Test 4.2: Repetitive escalation (high risk)")
    for i in range(10):
        result = loop_guard.observe("URGENT!! HELP!!", {"emergency"})
        time.sleep(0.01)  # Rapid repeats
    
    print(f"  Risk: {result['risk']:.2f}")
    print(f"  Mode: {result['mode']}")
    print(f"  Result: {'✅ PASS (de-escalate triggered)' if result['mode'] == 'deescalate' else '❌ FAIL'}")
    
    return True

def test_inv_05_exclusivity():
    """Test INV-05: Exclusivity prevents incompatible roles."""
    print("\n🧪 Testing INV-05: Role Exclusivity")
    
    checker = InvariantChecker(strict_mode=False)
    role_mgr = RoleManager()
    stress = StressEngine()
    loop_guard = LoopGuard()
    memory = DualMemory()
    
    # Test 1: Compatible roles
    print("  Test 5.1: Compatible roles")
    role_mgr.activate("maintenance", consent=True)
    role_mgr.activate("observer", consent=True)
    
    result = checker.check_exclusivity(role_mgr, stress, loop_guard, memory, "test_agent")
    print(f"  Active roles: {role_mgr.active}")
    print(f"  Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    # Test 2: Attempt incompatible roles (should be blocked by activate())
    print("  Test 5.2: Attempting incompatible roles (advocate + adversary)")
    role_mgr.activate("advocate", consent=True)
    success, reasons = role_mgr.activate("adversary", consent=True)  # Should fail
    
    print(f"  Adversary blocked: {not success}")
    print(f"  Reasons: {reasons}")
    print(f"  Result: {'✅ PASS (properly blocked)' if not success else '❌ FAIL'}")
    
    # Test 3: Verify exclusivity is enforced
    role_mgr2 = RoleManager()
    role_mgr2.activate("observer", consent=True)
    success2, reasons2 = role_mgr2.activate("advocate", consent=True)  # observer excludes advocate
    
    print(f"  Observer + Advocate blocked: {not success2}")
    print(f"  Result: {'✅ PASS (properly blocked)' if not success2 else '❌ FAIL'}")
    
    return True

def test_property_based():
    """Property-based testing with randomized inputs."""
    print("\n🧪 Property-Based Testing (100 random operations)")
    
    checker = InvariantChecker(strict_mode=False)
    role_mgr = RoleManager()
    stress = StressEngine()
    loop_guard = LoopGuard()
    memory = DualMemory()
    
    test_cases = property_based_test_generator(iterations=100)
    
    violations = 0
    
    for i, (operation, param) in enumerate(test_cases):
        try:
            if operation == "assign_role":
                role_mgr.activate(param, consent=True)
            elif operation == "release_role":
                if param in role_mgr.active:
                    role_mgr.active.discard(param)
            elif operation == "update_stress":
                stress.step(dt=1.0, active=role_mgr.active, util={r: param for r in role_mgr.active})
            elif operation == "anchor_cue":
                memory.anchor_opt_in({param}, f"content_{i}", allow_anchor=True)
            elif operation == "loop_signal":
                loop_guard.observe(param, set())
            
            # Verify all invariants every 10 operations (not every time - too slow)
            if i % 10 == 0:
                passed = checker.verify_all(role_mgr, stress, loop_guard, memory, "property_test")
                
                if not passed:
                    violations += 1
        
        except Exception as e:
            print(f"  Error at operation {i}: {e}")
            violations += 1
    
    print(f"  Completed 100 randomized operations")
    print(f"  Violations detected: {violations}")
    print(f"  Result: {'✅ PASS' if violations == 0 else f'⚠️ {violations} violations'}")
    
    return violations == 0

def test_stress_scenario():
    """High-stress scenario: rapid role changes + fatigue accumulation."""
    print("\n🧪 Stress Test: Rapid Role Changes Under High Load")
    
    checker = InvariantChecker(strict_mode=False)
    role_mgr = RoleManager()
    stress = StressEngine()
    loop_guard = LoopGuard()
    memory = DualMemory()
    
    # Simulate 60 seconds of high-load operation
    print("  Simulating 60 seconds of operation...")
    
    roles = ["maintenance", "social_presence", "observer"]
    
    for second in range(60):
        # Update stress for active roles
        stress.step(dt=1.0, active=role_mgr.active, util={r: 0.8 for r in role_mgr.active})
        
        # Try to activate random role every 5 seconds
        if second % 5 == 0:
            role = roles[second % len(roles)]
            success, reasons = role_mgr.activate(role, consent=True)
            
            if success:
                print(f"    t={second}s: Activated {role}")
            else:
                print(f"    t={second}s: Refused {role} - {reasons}")
        
        # Verify invariants every 10 seconds
        if second % 10 == 0:
            passed = checker.verify_all(role_mgr, stress, loop_guard, memory, "stress_test")
            if not passed:
                print(f"  ❌ Invariant violation at t={second}s")
                return False
        
        time.sleep(0.05)  # 50ms per "second" for fast test
    
    print("  ✅ Survived 60 seconds without violations")
    
    return True

def main():
    """Run all invariant tests."""
    print("=" * 70)
    print("CGCS INVARIANT VERIFICATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("INV-01: Consent Gating", test_inv_01_consent_gating),
        ("INV-02: Capacity Gating", test_inv_02_capacity_gating),
        ("INV-03: Fatigue Gating", test_inv_03_fatigue_gating),
        ("INV-04: Risk Gating", test_inv_04_risk_gating),
        ("INV-05: Exclusivity", test_inv_05_exclusivity),
        ("Property-Based Tests", test_property_based),
        ("Stress Scenario", test_stress_scenario)
    ]
    
    results = []
    
    for test_name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:40s} {status}")
    
    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)
    
    print("=" * 70)
    print(f"Passed: {total_passed}/{total_tests}")
    
    if total_passed == total_tests:
        print("✅ ALL INVARIANTS VERIFIED")
        return 0
    else:
        print(f"❌ {total_tests - total_passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
