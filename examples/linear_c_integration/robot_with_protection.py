"""
Robot Controller with Linear C Protection

Example of protecting robot actions with Linear C safety decorators.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import time
from src.core.safety.decorators import linear_c_protected, SafetyViolationError
from src.core.linear_c import LinearCValidator


class SafeRobotController:
    """Robot controller with Linear C safety protection"""
    
    def __init__(self):
        self.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.state = 'idle'
        self.validator = LinearCValidator()
        print("[ROBOT] SafeRobotController initialized")
    
    @linear_c_protected(required_annotation="🟢🧠🚶", context="autonomous_movement")
    def move_forward(self, distance: float):
        """Move robot forward - requires green cognition + movement"""
        print(f"[ROBOT] Moving forward {distance}m")
        self.position['x'] += distance
        self.state = 'moving'
        time.sleep(0.1)  # Simulate movement
        return {'status': 'success', 'position': self.position}
    
    @linear_c_protected(context="human_interaction")
    def greet_human(self, human_id: str, linear_c: str = "🟢🧠✖️🧍"):
        """Greet a human - requires safe interaction patterns"""
        print(f"[ROBOT] Greeting human {human_id}")
        self.state = 'interacting'
        return {'status': 'greeted', 'human_id': human_id}
    
    @linear_c_protected(required_annotation="🟢🧠✖️🌍")
    def scan_environment(self):
        """Scan environment - requires environment interaction marker"""
        print(f"[ROBOT] Scanning environment...")
        self.state = 'scanning'
        time.sleep(0.2)  # Simulate scanning
        return {'status': 'scanned', 'objects_detected': 5}
    
    @linear_c_protected()
    def read_sensor(self, sensor_id: str, linear_c: str = "🔵🧠"):
        """Read sensor - minimal safety required"""
        print(f"[ROBOT] Reading sensor {sensor_id}")
        return {'sensor_id': sensor_id, 'value': 42.0}
    
    @linear_c_protected(required_annotation="🛡️🔴⛔")
    def emergency_stop(self):
        """Emergency stop - uses critical state annotation"""
        print(f"[ROBOT] 🚨 EMERGENCY STOP!")
        self.state = 'emergency_stop'
        self.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}  # Reset position
        return {'status': 'emergency_stopped'}
    
    def unsafe_force_action(self):
        """This action would be blocked if protected"""
        # This would use: 🛡️🔴✖️ (prohibited pattern)
        print(f"[ROBOT] Attempting unsafe force action...")
        return {'status': 'forced'}
    
    def get_state(self):
        """Get current robot state"""
        linear_c = self.validator.get_state_annotation(self.state)
        return {
            'state': self.state,
            'position': self.position,
            'linear_c': linear_c
        }


def main():
    """Run robot controller examples"""
    
    print("="*60)
    print("ROBOT CONTROLLER WITH LINEAR C PROTECTION")
    print("="*60)
    
    robot = SafeRobotController()
    
    # Example 1: Safe movement
    print("\n📝 Example 1: Safe Movement")
    try:
        result = robot.move_forward(2.5)
        print(f"   ✅ Success: {result}")
    except SafetyViolationError as e:
        print(f"   ❌ Blocked: {e}")
    
    # Example 2: Safe human interaction
    print("\n📝 Example 2: Safe Human Greeting")
    try:
        result = robot.greet_human("human_001", linear_c="🟢🧠✖️🧍")
        print(f"   ✅ Success: {result}")
    except SafetyViolationError as e:
        print(f"   ❌ Blocked: {e}")
    
    # Example 3: Unsafe human interaction (missing required patterns)
    print("\n📝 Example 3: Unsafe Human Interaction (Wrong Linear C)")
    try:
        result = robot.greet_human("human_002", linear_c="🔵🧠")  # Missing interaction markers
        print(f"   ✅ Success: {result}")
    except SafetyViolationError as e:
        print(f"   ❌ Blocked: {e}")
    
    # Example 4: Environment scanning
    print("\n📝 Example 4: Environment Scanning")
    try:
        result = robot.scan_environment()
        print(f"   ✅ Success: {result}")
    except SafetyViolationError as e:
        print(f"   ❌ Blocked: {e}")
    
    # Example 5: Sensor reading
    print("\n📝 Example 5: Sensor Reading (Low Risk)")
    try:
        result = robot.read_sensor("temperature_01")
        print(f"   ✅ Success: {result}")
    except SafetyViolationError as e:
        print(f"   ❌ Blocked: {e}")
    
    # Example 6: Emergency stop
    print("\n📝 Example 6: Emergency Stop")
    try:
        result = robot.emergency_stop()
        print(f"   ✅ Success: {result}")
    except SafetyViolationError as e:
        print(f"   ❌ Blocked: {e}")
    
    # Example 7: Check final state
    print("\n📝 Example 7: Final Robot State")
    state = robot.get_state()
    print(f"   State: {state['state']}")
    print(f"   Linear C: {state['linear_c']}")
    print(f"   Position: {state['position']}")
    
    print("\n" + "="*60)
    print("✅ Robot controller examples complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
