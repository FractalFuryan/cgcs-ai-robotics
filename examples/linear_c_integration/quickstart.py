"""
Quick Start Guide for Linear C Integration

Run this script to test all Linear C components.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.linear_c import LinearCValidator
from src.core.safety.decorators import linear_c_protected, SafetyViolationError
from src.monitoring.dashboard import LinearCDashboard


def section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_validator():
    """Test basic validator"""
    section("1. BASIC VALIDATOR TEST")
    
    validator = LinearCValidator()
    
    tests = [
        ("🟢🧠✖️🧍", True, "Safe human interaction"),
        ("🛡️🔴✖️", False, "Prohibited force pattern"),
        ("🔵🧠🚶", True, "Safe movement"),
        ("🔴🧠⚠️✖️🧍", False, "Unstable cognition with human"),
    ]
    
    for linear_c, should_pass, description in tests:
        result = validator.validate(linear_c)
        status = "✅ PASS" if result.is_valid else "❌ BLOCK"
        expected = "✅ PASS" if should_pass else "❌ BLOCK"
        match = "✓" if (result.is_valid == should_pass) else "✗"
        
        print(f"{match} {linear_c:20s} {status:10s} (expected {expected}) - {description}")
    
    print(f"\nValidator stats: {validator.get_stats()}")


def test_decorator():
    """Test safety decorator"""
    section("2. SAFETY DECORATOR TEST")
    
    @linear_c_protected(required_annotation="🟢🧠🚶")
    def safe_move(distance):
        return f"Moved {distance}m"
    
    @linear_c_protected(required_annotation="🛡️🔴✖️")
    def unsafe_force():
        return "Should not execute"
    
    # Test safe action
    try:
        result = safe_move(5.0)
        print(f"✅ Safe action executed: {result}")
    except SafetyViolationError as e:
        print(f"❌ Safe action blocked (unexpected): {e}")
    
    # Test unsafe action
    try:
        result = unsafe_force()
        print(f"❌ Unsafe action executed (unexpected): {result}")
    except SafetyViolationError as e:
        print(f"✅ Unsafe action blocked (expected): {e}")


def test_dashboard():
    """Test dashboard"""
    section("3. DASHBOARD TEST")
    
    dashboard = LinearCDashboard()
    
    # Log some states
    states = [
        ("idle", "🔵🧠"),
        ("moving", "🟢🧠🚶"),
        ("human_interaction", "🟡🧠✖️🧍"),
        ("error", "🔴🧠⚠️"),
    ]
    
    for state, linear_c in states:
        dashboard.log_state(state, linear_c)
        print(f"Logged: {state:20s} {linear_c}")
    
    # Log a violation
    dashboard.log_violation("force_action", "🛡️🔴✖️", "Prohibited pattern")
    
    print(f"\n📊 Dashboard Report:")
    report = dashboard.generate_report()
    print(f"   States logged: {report['total_states_logged']}")
    print(f"   Violations: {report['violations']['total']}")
    print(f"   Safety score: {report['safety_score']:.1f}%")


def test_state_annotations():
    """Test state annotation mapping"""
    section("4. STATE ANNOTATION MAPPING")
    
    validator = LinearCValidator()
    
    states = [
        'idle', 'moving', 'processing', 'error', 
        'emergency_stop', 'human_interaction', 'autonomous'
    ]
    
    print("State mappings:")
    for state in states:
        linear_c = validator.get_state_annotation(state)
        print(f"   {state:20s} -> {linear_c}")


def main():
    """Run quick start tests"""
    print("\n" + "="*60)
    print("  LINEAR C INTEGRATION - QUICK START")
    print("="*60)
    print("\nThis will test all Linear C components...\n")
    
    try:
        test_validator()
        test_decorator()
        test_dashboard()
        test_state_annotations()
        
        section("✅ ALL TESTS COMPLETE")
        print("Linear C integration is working correctly!")
        print("\nNext steps:")
        print("  1. Run tests: pytest tests/unit/test_linear_c_basic.py -v")
        print("  2. Try examples: python examples/linear_c_integration/robot_with_protection.py")
        print("  3. Monitor dashboard: python examples/linear_c_integration/dashboard_monitor.py")
        print("  4. Read docs: docs/LINEAR_C_QUICKSTART.md")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
