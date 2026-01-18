"""
demo_multi_agent_swarm.py
Demonstrates consent-based multi-agent swarm coordination.
Shows role distribution, cue propagation, and cooperative missions.
"""
import time
import sys
sys.path.insert(0, '/workspaces/cgcs-ai-robotics')

from stack.robot_agent import CompleteRobotAgent
from stack.fleet_manager import FleetManager
from stack.interfaces import MissionSpec, WorldCue

print("=" * 70)
print("MULTI-AGENT SWARM COORDINATION DEMO")
print("Consent-Based Fleet with Cue Propagation")
print("=" * 70)

# 1. Create a swarm of robot agents
print("\n1. 🏗️  Creating Robot Swarm (4 agents)...")

agents = {
    "scout_alpha": CompleteRobotAgent(
        agent_id="scout_alpha",
        capabilities=["navigate", "scan", "inspect"],
        initial_position=[0, 0, 0]
    ),
    "scout_beta": CompleteRobotAgent(
        agent_id="scout_beta",
        capabilities=["navigate", "scan", "report"],
        initial_position=[10, 0, 0]
    ),
    "transport_gamma": CompleteRobotAgent(
        agent_id="transport_gamma",
        capabilities=["navigate", "carry", "deliver"],
        initial_position=[0, 10, 0]
    ),
    "observer_delta": CompleteRobotAgent(
        agent_id="observer_delta",
        capabilities=["monitor", "signal"],
        initial_position=[10, 10, 0]
    )
}

# 2. Create fleet manager with routing table
print("\n2. 🎯 Creating Fleet Manager with Routing Table...")

routing_table = {
    agent_id: agent.brain 
    for agent_id, agent in agents.items()
}

fleet = FleetManager(agent_routing=routing_table)

print(f"   ✅ Fleet initialized with {len(routing_table)} agents")

# 3. Start autonomous loops
print("\n3. 🚀 Starting Autonomous Behavior Loops...")
for agent in agents.values():
    agent.start_autonomous_loop(interval=1.0)

# 4. Deploy cooperative mission
print("\n4. 📋 Deploying Cooperative Search & Rescue Mission...")

mission = MissionSpec(
    mission_id="COOP-SR-001",
    objective="Coordinated search and rescue",
    parameters={
        "max_duration_s": 300,
        "search_grid": [[0, 0], [20, 0], [20, 20], [0, 20]],
        "max_range_m": 50.0
    },
    required_roles=["scout", "scout", "transport", "observer"]
)

deployment_ok = fleet.submit_mission(mission)
print(f"\n   Mission deployment: {'✅ SUCCESS' if deployment_ok else '⚠️  FAILED'}")

# 5. Broadcast global cue to fleet
print("\n5. 📡 Broadcasting Global Alert to Fleet...")

global_alert = WorldCue(
    cue_id="alert_001",
    tag="hazard_detected",
    data={
        "type": "chemical_spill",
        "location": [15, 15],
        "severity": "high",
        "radius": 5.0
    },
    ttl=int(time.time()) + 600
)

recipients = fleet.broadcast_cue(global_alert)
print(f"   Cue received by {recipients} agents (consent-based)")

# 6. Monitor fleet for 8 seconds
print("\n6. 📊 Monitoring Fleet Operations (8 seconds)...")

for i in range(8):
    time.sleep(1.0)
    
    if i % 2 == 0:
        print(f"\n   --- Fleet Status @ {i}s ---")
        fleet_status = fleet.get_fleet_status()
        
        print(f"   Active Agents: {fleet_status['total_agents']}")
        print(f"   Active Missions: {fleet_status['active_missions']}")
        
        # Show individual agent status
        for agent_id, agent in list(agents.items())[:2]:  # Show first 2
            status = agent.get_full_status()
            role = status['brain'].get('current_role', 'none')
            battery = status['hardware']['battery']
            fatigue = status['brain'].get('fatigue', 0.0)
            print(f"   {agent_id}: {role} | Battery: {battery:.2f} | Fatigue: {fatigue:.2f}")

# 7. Test dynamic agent addition
print("\n7. 🔧 Testing Dynamic Fleet Reconfiguration...")

# Add a new agent mid-mission
new_agent = CompleteRobotAgent(
    agent_id="rescue_epsilon",
    capabilities=["navigate", "medical", "extract"],
    initial_position=[5, 5, 0]
)
new_agent.start_autonomous_loop(interval=1.0)

fleet.add_agent("rescue_epsilon", new_agent.brain)

# Broadcast cue to new agent
fleet.broadcast_cue(WorldCue(
    cue_id="welcome_001",
    tag="fleet_join",
    data={"message": "Welcome to fleet", "mission": mission.mission_id}
))

time.sleep(2)

# Remove an agent
print("\n8. 🔌 Testing Agent Removal...")
fleet.remove_agent("observer_delta")
agents["observer_delta"].stop()

# 9. Cancel mission and shutdown
print("\n9. 🛑 Mission Cancellation & Fleet Shutdown...")

fleet.cancel_mission(mission.mission_id)

for agent in agents.values():
    agent.stop()
new_agent.stop()

# 10. Final fleet statistics
print("\n10. 📈 Final Fleet Statistics...")
final_status = fleet.get_fleet_status()
print(f"   Final agent count: {final_status['total_agents']}")
print(f"   Active missions: {final_status['active_missions']}")

print("\n" + "=" * 70)
print("✅ MULTI-AGENT SWARM DEMO COMPLETE")
print("\n   Demonstrated:")
print("   • Multi-agent role distribution (4 agents, 4 roles)")
print("   • Consent-based cue propagation")
print("   • Dynamic fleet reconfiguration (add/remove agents)")
print("   • Cooperative mission coordination")
print("   • FleetManager as swarm conductor (no control authority)")
print("\n   Ready for:")
print("   • Scale to larger fleets (10s-100s of agents)")
print("   • Real inter-robot communication (MQTT/ROS 2)")
print("   • Complex multi-agent behaviors")
print("=" * 70)
