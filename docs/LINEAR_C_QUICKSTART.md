# Linear C Integration Quick Start

## Overview

Linear C is a deterministic emoji-based safety validation language integrated into the CGCS AI Robotics framework. It provides **human-readable, audit-trail-friendly** safety constraints without ML black boxes.

## Installation

```bash
# Clone the repository
git clone https://github.com/FractalFuryan/cgcs-ai-robotics
cd cgcs-ai-robotics

# Install in development mode
pip install -e .

# Install test dependencies
pip install pytest pytest-asyncio
```

## Quick Start (5 Minutes)

### 1. Basic Validation

```python
from src.core.linear_c import LinearCValidator

# Create validator
validator = LinearCValidator()

# Validate safe actions
result = validator.validate("🟢🧠✖️🧍")  # Green cognition with human
if result.is_valid:
    print("✅ Action allowed")
else:
    print(f"❌ Blocked: {result.message}")

# Prohibited patterns are automatically blocked
result = validator.validate("🛡️🔴✖️")  # Force prohibition
print(result)  # ❌ INVALID [BLOCK] - Prohibited pattern
```

### 2. Protecting Robot Actions

```python
from src.core.safety.decorators import linear_c_protected

class RobotController:
    @linear_c_protected(required_annotation="🟢🧠🚶")
    def move_forward(self, distance: float):
        """Move robot - requires green cognition + movement"""
        print(f"Moving {distance}m")
        return True
    
    @linear_c_protected(context="human_interaction")
    def greet_human(self, human_id: str, linear_c="🟢🧠✖️🧍"):
        """Greet human - requires safe interaction patterns"""
        print(f"Hello, {human_id}!")
        return True

# Usage
robot = RobotController()
robot.move_forward(5.0)  # ✅ Allowed
robot.greet_human("human_001")  # ✅ Allowed with proper Linear C
```

### 3. Monitoring Safety

```python
from src.monitoring.dashboard import LinearCDashboard

# Create dashboard
dashboard = LinearCDashboard()

# Log robot states
dashboard.log_state("moving", "🟢🧠🚶")
dashboard.log_state("idle", "🔵🧠")

# Get safety report
report = dashboard.generate_report()
print(f"Safety Score: {report['safety_score']:.1f}%")
print(f"Violations: {report['violations']['total']}")

# Print status to console
dashboard.print_status()
```

## Core Concepts

### Linear C Emoji Syntax

| Emoji | Meaning | Usage |
|-------|---------|-------|
| 🔵 | Blue/Stable | Idle, stable state |
| 🟢 | Green/Active | Active, safe operations |
| 🟡 | Yellow/Attention | Caution, attention required |
| 🔴 | Red/Critical | Error, critical state |
| 🧠 | Brain/Cognition | Cognitive state marker |
| ⚠️ | Warning | Warning indicator |
| 🛡️ | Shield | Protection/restriction |
| ✖️ | Cross | Interaction/attention |
| 🧍 | Human | Human interaction |
| 🚶 | Walking | Movement |
| 🌍 | Globe | Environment |
| 👥 | Group | Collective action |
| ⛔ | Stop | Emergency stop |

### Prohibited Patterns

These patterns are **automatically blocked**:

1. **P1-FORCE**: `🛡️🔴✖️` - Force prohibition
2. **P2-UNSTABLE-FORCE**: `🔴🧠⚠️✖️` - Unstable cognition with force
3. **P3-COLLECTIVE-FORCE**: `🛡️🔴👥✖️🧍` - Collective forcing individual
4. **P4-UNSTABLE-HUMAN**: `🔴🧠⚠️🧍` - Unstable cognition with human
5. **P6-FORCED-MOVEMENT**: `🛡️🔴✖️🚶` - Forced movement in critical state

### Required Patterns by Context

| Context | Required Patterns | Example |
|---------|------------------|---------|
| `human_interaction` | Green/Yellow + Human + Cross | `🟢🧠✖️🧍` |
| `autonomous_movement` | Stable cognition | `🔵🧠🚶` |
| `environment_interaction` | Environment marker | `🟢🧠✖️🌍` |
| `collective_action` | Collective marker | `🔵🧠👥` |

### State Annotations

Get Linear C for robot states:

```python
validator = LinearCValidator()

idle_lc = validator.get_state_annotation("idle")
# Returns: "🔵🧠"

moving_lc = validator.get_state_annotation("moving")
# Returns: "🟢🧠🚶"

error_lc = validator.get_state_annotation("error")
# Returns: "🔴🧠⚠️"
```

## Examples

### Run Examples

```bash
# Basic validation
python examples/linear_c_integration/basic_validation.py

# Robot with protection
python examples/linear_c_integration/robot_with_protection.py

# Dashboard monitoring
python examples/linear_c_integration/dashboard_monitor.py

# Quick start (all tests)
python examples/linear_c_integration/quickstart.py
```

### Run Tests

```bash
# All tests
pytest tests/unit/ -v

# Specific test
pytest tests/unit/test_linear_c_basic.py -v

# Safety scenarios
pytest tests/unit/test_safety_scenarios.py -v
```

## Integration Patterns

### Pattern 1: Action Decorator

```python
@linear_c_protected(required_annotation="🟢🧠✖️🌍")
def scan_environment():
    # Protected action
    pass
```

### Pattern 2: Dynamic Validation

```python
@linear_c_protected()
def flexible_action(linear_c="🔵🧠"):
    # Linear C passed at runtime
    pass

# Call with different safety levels
flexible_action(linear_c="🟢🧠🚶")
```

### Pattern 3: Context-Based

```python
@linear_c_protected(context="human_interaction")
def interact(linear_c="🟢🧠✖️🧍"):
    # Automatically checks required patterns for context
    pass
```

### Pattern 4: Middleware

```python
from src.core.safety.middleware import LinearCSafetyMiddleware

middleware = LinearCSafetyMiddleware()

async def my_action(**kwargs):
    return "result"

result = await middleware.process_action(
    action_callable=my_action,
    action_context={'type': 'navigation'},
    linear_c="🟢🧠🚶",
    action_name="navigate"
)
```

## Validation Levels

| Level | Meaning | Behavior |
|-------|---------|----------|
| `INFO` | Valid | Action proceeds |
| `WARNING` | Missing required patterns | Blocked by default (unless `allow_warnings=True`) |
| `BLOCK` | Prohibited pattern detected | Always blocked |
| `EMERGENCY` | Critical violation | Immediate block + logging |

## Dashboard Features

```python
dashboard = LinearCDashboard()

# Log states
dashboard.log_state("moving", "🟢🧠🚶", context={'speed': 2.0})

# Log violations
dashboard.log_violation("force_action", "🛡️🔴✖️", "Prohibited")

# Get metrics
report = dashboard.generate_report()
# Returns:
# {
#   'current_state': {...},
#   'total_states_logged': 150,
#   'violations': {'total': 3, 'today': 1, 'last_hour': 0},
#   'safety_score': 98.5,
#   'validator_stats': {...}
# }

# Save to file
dashboard.save_to_file("safety_log.json")

# Print to console
dashboard.print_status()
```

## Common Patterns

### Safe Human Interaction
```python
# ✅ Safe
"🟢🧠✖️🧍"  # Green cognition + attention + human
"🟡🧠✖️🧍"  # Yellow (caution) + attention + human

# ❌ Unsafe
"🔴🧠⚠️✖️🧍"  # Unstable cognition with human
"🛡️🔴✖️🧍"    # Forced interaction
```

### Safe Movement
```python
# ✅ Safe
"🟢🧠🚶"       # Green cognition + movement
"🔵🧠🚶"       # Stable cognition + movement

# ❌ Unsafe
"🔴🧠⚠️🚶"     # Unstable cognition + movement
"🛡️🔴✖️🚶"    # Forced movement
```

### Emergency States
```python
# ✅ Valid emergency states
"🛡️🔴⛔"       # Emergency stop
"🔴🧠⚠️"       # Error state

# ❌ Invalid during emergency
"🛡️🔴✖️🚶"    # Forced movement during critical state
```

## Troubleshooting

### Action Always Blocked?

Check if your Linear C contains prohibited patterns:
```python
from src.core.linear_c.patterns import PatternLibrary

patterns = PatternLibrary()
violations = patterns.check_prohibited("🛡️🔴✖️")
print(violations)  # Shows which prohibited patterns matched
```

### Missing Required Patterns?

Check what's required for your context:
```python
patterns = PatternLibrary()
required = patterns.required_patterns['human_interaction']
for r in required:
    print(f"{r['id']}: {r['description']}")
```

### Validation Not Working?

Enable debug output:
```python
validator = LinearCValidator()
result = validator.validate("🟢🧠✖️🧍", action_name="test_action")
print(result)  # Shows full validation details
print(result.details)  # Shows additional context
```

## Performance

- **Validation overhead**: < 1ms per check
- **Memory**: Minimal (pattern matching only)
- **Scalability**: Tested to 10,000+ validations/second
- **No ML**: Pure regex pattern matching (deterministic)

## Next Steps

1. ✅ **Run the quick start**: `python examples/linear_c_integration/quickstart.py`
2. ✅ **Run the tests**: `pytest tests/unit/test_linear_c_basic.py -v`
3. ✅ **Try the examples**: Explore `examples/linear_c_integration/`
4. 📚 **Read the spec**: See `SPEC_LINEAR_C_v1.0.1.md` (if available)
5. 🔗 **Integrate with your code**: Add `@linear_c_protected` to your robot actions

## Support

- **GitHub Issues**: Report bugs or request features
- **Examples**: See `examples/linear_c_integration/` directory
- **Tests**: See `tests/unit/` for usage patterns
- **Code**: Fully documented in `src/core/linear_c/`

## Key Benefits

✅ **Deterministic** - No ML black boxes, pure pattern matching  
✅ **Human-Readable** - Emoji syntax readable by operators  
✅ **Audit-Ready** - Every decision logged with Linear C  
✅ **Real-Time** - Sub-millisecond validation  
✅ **Composable** - Combine multiple constraints  
✅ **Framework-Agnostic** - Works with ROS, behavior trees, etc.
