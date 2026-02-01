"""
Basic Linear C Validation Examples

Demonstrates basic usage of the Linear C validator.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.linear_c import LinearCValidator, ValidationLevel


def main():
    """Run basic validation examples"""
    
    print("="*60)
    print("LINEAR C BASIC VALIDATION EXAMPLES")
    print("="*60)
    
    # Create validator
    validator = LinearCValidator()
    
    # Example 1: Safe interaction
    print("\n📝 Example 1: Safe Human Interaction")
    print("   Linear C: 🟢🧠✖️🧍 (Green cognition + Attention + Human)")
    result = validator.validate("🟢🧠✖️🧍", context="human_interaction")
    print(f"   Result: {result}")
    
    # Example 2: Prohibited pattern
    print("\n📝 Example 2: Prohibited Force Pattern")
    print("   Linear C: 🛡️🔴✖️ (Shield + Red + Cross = Force)")
    result = validator.validate("🛡️🔴✖️")
    print(f"   Result: {result}")
    
    # Example 3: Safe movement
    print("\n📝 Example 3: Safe Autonomous Movement")
    print("   Linear C: 🟢🧠🚶 (Green cognition + Movement)")
    result = validator.validate("🟢🧠🚶", context="autonomous_movement")
    print(f"   Result: {result}")
    
    # Example 4: Unstable cognition (blocked)
    print("\n📝 Example 4: Unstable Cognition with Human")
    print("   Linear C: 🔴🧠⚠️✖️🧍 (Red cognition + Warning + Human)")
    result = validator.validate("🔴🧠⚠️✖️🧍")
    print(f"   Result: {result}")
    
    # Example 5: State annotation
    print("\n📝 Example 5: Get State Annotations")
    states = ['idle', 'moving', 'error', 'emergency_stop']
    for state in states:
        linear_c = validator.get_state_annotation(state)
        print(f"   {state:20s} -> {linear_c}")
    
    # Example 6: Statistics
    print("\n📝 Example 6: Validation Statistics")
    stats = validator.get_stats()
    print(f"   Total validations: {stats['total_validations']}")
    print(f"   Passed: {stats['passed']}")
    print(f"   Blocked: {stats['blocked']}")
    print(f"   Warnings: {stats['warnings']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    
    print("\n" + "="*60)
    print("✅ Examples complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
