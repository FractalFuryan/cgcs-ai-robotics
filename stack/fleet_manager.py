"""
fleet_manager.py
Multi-agent fleet coordinator with routing table and cue propagation.
"""

from typing import Dict, List, Optional
from .interfaces import (
    FleetManagementAPI,
    MissionSpec,
    UpwardAPI,
    WorldCue,
)
from .mission_planner import MissionPlanner


class FleetManager(FleetManagementAPI):
    """
    Layer-5 conductor with multi-agent routing.
    No control authority — coordination only.
    Enables role distribution, cue propagation, cooperative missions.
    """

    def __init__(self, agent_routing: Dict[str, UpwardAPI]):
        """
        Args:
            agent_routing: Map of agent_id → CGCSAgentAdapter
        """
        self.routing = agent_routing
        self.planner = MissionPlanner()
        self.active_missions: Dict[str, MissionSpec] = {}
        self.mission_assignments: Dict[str, Dict[str, str]] = {}
    
    def add_agent(self, agent_id: str, agent_api: UpwardAPI):
        """Dynamically add an agent to the fleet."""
        self.routing[agent_id] = agent_api
        print(f"🔗 [{agent_id}] Added to fleet (total: {len(self.routing)} agents)")
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from the fleet."""
        if agent_id in self.routing:
            del self.routing[agent_id]
            print(f"🔌 [{agent_id}] Removed from fleet")
    
    def submit_mission(self, mission: MissionSpec) -> bool:
        """Distribute mission roles across available agents."""
        if mission.mission_id in self.active_missions:
            print(f"⚠️  Mission {mission.mission_id} already active")
            return False

        roles = self.planner.expand_mission(mission)
        available_agents = list(self.routing.keys())
        
        if len(roles) > len(available_agents):
            print(f"⚠️  Insufficient agents: need {len(roles)}, have {len(available_agents)}")
            return False
        
        assignments = {}
        failed_assignments = []
        
        for agent_id, role in zip(available_agents, roles):
            agent_api = self.routing[agent_id]
            ok = agent_api.assign_role_to_agent(agent_id, role)
            
            if ok:
                assignments[agent_id] = role.role_name
                print(f"   ✅ {agent_id} ← {role.role_name}")
            else:
                failed_assignments.append((agent_id, role.role_name))
                print(f"   ⚠️  {agent_id} refused {role.role_name}")
        
        if len(failed_assignments) > 0:
            print(f"⚠️  Mission deployment failed: {len(failed_assignments)} refusals")
            return False
        
        self.active_missions[mission.mission_id] = mission
        self.mission_assignments[mission.mission_id] = assignments
        print(f"✅ Mission {mission.mission_id} deployed to {len(assignments)} agents")
        return True

    def cancel_mission(self, mission_id: str) -> bool:
        """Cancel an active mission."""
        if mission_id not in self.active_missions:
            return False

        if mission_id in self.mission_assignments:
            for agent_id in self.mission_assignments[mission_id]:
                print(f"   📢 Notifying {agent_id} of mission cancellation")
        
        del self.active_missions[mission_id]
        if mission_id in self.mission_assignments:
            del self.mission_assignments[mission_id]
        
        return True
    
    def broadcast_cue(self, cue: WorldCue, exclude: Optional[List[str]] = None) -> int:
        """Broadcast a world cue to all agents (consent-based)."""
        exclude = exclude or []
        count = 0
        
        for agent_id, agent_api in self.routing.items():
            if agent_id not in exclude:
                ok = agent_api.inject_world_cue(agent_id, cue)
                if ok:
                    count += 1
        
        print(f"📡 Broadcast cue '{cue.tag}' to {count}/{len(self.routing)} agents")
        return count
    
    def get_fleet_status(self) -> Dict[str, any]:
        """Get status of entire fleet."""
        return {
            "total_agents": len(self.routing),
            "active_missions": len(self.active_missions),
            "missions": {
                mid: {
                    "objective": mission.objective,
                    "agents": self.mission_assignments.get(mid, {})
                }
                for mid, mission in self.active_missions.items()
            }
        }
