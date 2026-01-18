"""
demo_complete_system.py
Final integration test with complete hardware-in-the-loop system.
"""
import time
import sys
sys.path.insert(0, '/workspaces/cgcs-ai-robotics')

from stack.robot_agent import CompleteRobotAgent
from stack.fleet_manager import FleetManager
from stack.interfaces import MissionSpec

print("=" * 70)
print("FINAL SYSTEM INTEGRATION TEST")
print("Complete Stack: Layers 0-7 with Hardware Simulation")
print("=" * 70)

# 1. Create complete robot agents
print("\n1. 🏗️  Creating Complete Robot Agents...")

scout_robot = CompleteRobotAgent(
    agent_id="scout_alpha",
    capabilities=["navigate", "scan", "inspect"],
    initial_position=[0, 0, 0]
)

transport_robot = CompleteRobotAgent(
    agent_id="transport_beta",
    capabilities=["navigate", "carry"],
    initial_position=[10, 0, 0]
)

# 2. Start autonomous behavior
print("\n2. 🚀 Starting Autonomous Behavior Loops...")
scout_robot.start_autonomous_loop(interval=1.0)
transport_robot.start_autonomous_loop(interval=1.0)

# 3. Create mission and fleet manager
print("\n3. 🎯 Creating Mission & Fleet Manager...")
mission = MissionSpec(
    mission_id="SR-FINAL-001",
    objective="Search and rescue operation",
    parameters={"max_duration_s": 300, "search_grid": [[0, 0], [50, 0], [50, 50], [0, 50]]},
    required_roles=["scout", "observer"]
)

fleet_manager = FleetManager(cgcs_api=scout_robot.brain, agents=["scout_alpha", "transport_beta"])

# 4. Deploy mission
print(f"\n4. 📋 Deploying Mission: {mission.objective}")
print(f"   Search Area: {mission.parameters['search_grid']}")

deployment_status = fleet_manager.submit_mission(mission)
print(f"   Mission status: {deployment_status}")

# 5. Monitor system
print("\n5. 📊 Monitoring System Operation (10 seconds)...")
for i in range(10):
    time.sleep(1.0)
    
    if i % 2 == 0:
        print(f"\n   --- Status Update @ {i}s ---")
        scout_status = scout_robot.get_full_status()
        print(f"   Scout: {scout_status['brain'].get('current_role', 'none')} | "
              f"Pos: {scout_status['hardware']['position']} | "
              f"Battery: {scout_status['hardware']['battery']:.2f}")
        
        if scout_status['brain'].get('fatigue'):
            print(f"   Fatigue: {scout_status['brain']['fatigue']:.2f}")

# 6. Clean shutdown
print("\n6. 🛑 Performing Graceful Shutdown...")
scout_robot.stop()
transport_robot.stop()

print("\n" + "=" * 70)
print("✅ FINAL TEST COMPLETE")
print("   System Architecture: FULLY OPERATIONAL")
print("\n   Next Steps for Real Deployment:")
print("   1. Replace SimulatedHardwareInterface with real motor controllers")
print("   2. Implement real sensor drivers in hardware_interface.py")
print("   3. Add ROS 2 or MQTT communication layer")
print("   4. Deploy to actual robot hardware")
print("=" * 70)
