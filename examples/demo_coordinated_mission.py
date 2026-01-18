"""
demo_coordinated_mission.py
Demonstrates CGCS + Fleet Manager + Mission Planner integration.
Updated to use the real CGCS adapter (v2.0).
"""

import sys
import time
sys.path.insert(0, '/workspaces/cgcs-ai-robotics')

from stack.interfaces import (
    MissionSpec,
    BoundedRole,
    WorldCue,
    ActionRequest,
)
from stack.fleet_manager import FleetManager
from stack.cgcs_adapter import CGCSAgentAdapter


if __name__ == "__main__":
    print("=" * 60)
    print("CGCS-INTEGRATED ROBOTICS STACK DEMO v2.0")
    print("Using Real CGCS Adapter")
    print("=" * 60)
    
    # 1. Initialize REAL CGCS-powered agents
    print("\n1. 🤖 Initializing CGCS-Powered Agents...")
    robot_scout = CGCSAgentAdapter(
        agent_id="scout_1",
        robot_capabilities=["navigate", "scan", "report"]
    )
    
    robot_transport = CGCSAgentAdapter(
        agent_id="transport_1",
        robot_capabilities=["navigate", "carry", "deliver"]
    )
    
    # 2. Create Fleet Manager
    print("\n2. 🎯 Creating Fleet Manager...")
    fleet = FleetManager(cgcs_api=robot_scout, agents=["scout_1", "transport_1"])
    
    # 3. Submit mission
    print("\n3. 📋 Submitting Search Mission...")
    mission = MissionSpec(
        mission_id="M-001",
        objective="Grid scan",
        parameters={"max_duration_s": 120, "max_range_m": 100.0},
        required_roles=["scout", "observer"],
    )
    
    ok = fleet.submit_mission(mission)
    print(f"   Mission accepted: {ok}")
    
    # 4. Check agent status
    print("\n4. 📊 Agent Status After Role Assignment...")
    scout_status = robot_scout.get_status()
    print(f"   Scout: {scout_status}")
    
    # 5. Simulate scout action
    if scout_status.get("current_role") == "scout":
        print("\n5. 🔍 Scout Detects Anomaly...")
        
        action = ActionRequest(
            source_agent_id="scout_1",
            source_role="scout",
            action_type="scan",
            parameters={"target": [45, 67], "intensity": "high"},
            priority=7
        )
        
        success = robot_scout.request_action(action)
        print(f"   Action request processed: {success}")
        
        # CGCS creates memory cue
        cue = WorldCue(
            cue_id="anomaly_001",
            tag="thermal_anomaly",
            data={"location": [45, 67], "temperature": 42.5, "confidence": 0.92}
        )
        
        robot_scout.share_cue_with_fleet(cue, ["transport_1"])
    
    # 6. Simulate World Model update
    print("\n6. 🗺️  World Model Updates Scout...")
    weather_cue = WorldCue(
        cue_id="weather_001",
        tag="storm_approaching",
        data={"direction": "northwest", "eta_minutes": 15, "severity": "medium"},
        ttl=int(time.time()) + 300
    )
    robot_scout.inject_world_cue("scout_1", weather_cue)
    
    # 7. Simulate time passage and stress accumulation
    print("\n7. ⏱️  Simulating 30s of operation (stress accumulation)...")
    for _ in range(30):
        robot_scout.step(dt=1.0)
    
    # 8. Final status
    print("\n8. 📊 Final System Status...")
    print(f"   Scout: {robot_scout.get_status()}")
    print(f"   Transport: {robot_transport.get_status()}")
    
    print("\n" + "=" * 60)
    print("✅ Demo complete. Real CGCS adapter integrated.")
    print("   Stack spans L1-L7 with CGCS as ethical core.")
    print("=" * 60)
