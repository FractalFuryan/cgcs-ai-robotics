"""
Dashboard Monitoring Example

Demonstrates real-time monitoring of Linear C safety status.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import time
import random
from src.monitoring.dashboard import LinearCDashboard
from src.core.linear_c import LinearCValidator


class SimulatedRobot:
    """Simulated robot for dashboard demonstration"""
    
    def __init__(self, dashboard: LinearCDashboard):
        self.dashboard = dashboard
        self.validator = LinearCValidator()
        self.states = ['idle', 'moving', 'processing', 'human_interaction', 'scanning']
        self.current_state = 'idle'
    
    def tick(self):
        """Simulate one robot tick"""
        # Randomly change state
        if random.random() < 0.3:  # 30% chance to change state
            self.current_state = random.choice(self.states)
        
        # Get Linear C for current state
        linear_c = self.validator.get_state_annotation(self.current_state)
        
        # Occasionally inject an unsafe pattern for testing
        if random.random() < 0.05:  # 5% chance of unsafe pattern
            linear_c = "🛡️🔴✖️"  # Prohibited pattern
            self.current_state = "unsafe_attempt"
        
        # Log to dashboard
        self.dashboard.log_state(
            robot_state=self.current_state,
            linear_c=linear_c,
            context={
                'tick': time.time(),
                'position': {'x': random.uniform(0, 10), 'y': random.uniform(0, 10)}
            }
        )


def main():
    """Run dashboard monitoring example"""
    
    print("="*60)
    print("LINEAR C DASHBOARD MONITORING")
    print("="*60)
    print("\nSimulating robot activity with safety monitoring...")
    print("Press Ctrl+C to stop\n")
    
    # Create dashboard
    dashboard = LinearCDashboard()
    
    # Create simulated robot
    robot = SimulatedRobot(dashboard)
    
    try:
        # Run simulation
        for i in range(50):
            robot.tick()
            
            # Print status every 10 ticks
            if (i + 1) % 10 == 0:
                print(f"\n--- After {i + 1} ticks ---")
                dashboard.print_status()
                time.sleep(0.5)
            else:
                time.sleep(0.1)
        
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60)
        
        # Generate final report
        report = dashboard.generate_report()
        
        print(f"\n📊 Summary:")
        print(f"   Total states logged: {report['total_states_logged']}")
        print(f"   Total violations: {report['violations']['total']}")
        print(f"   Safety score: {report['safety_score']:.1f}%")
        
        if report['violations']['recent']:
            print(f"\n⚠️  Recent violations:")
            for v in report['violations']['recent'][:3]:
                print(f"   - {v['action']}: {v['linear_c']}")
                print(f"     Reason: {v['reason']}")
        
        # Save to file
        dashboard.save_to_file("examples/linear_c_integration/dashboard_log.json")
        print(f"\n💾 Dashboard log saved to: dashboard_log.json")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
        dashboard.print_status()
    
    print("\n" + "="*60)
    print("✅ Dashboard monitoring example complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
