"""
fleet_manager.py
Coordinates missions across CGCS-powered agents.
"""

from typing import Dict, List
from .interfaces import (
    FleetManagementAPI,
    MissionSpec,
    UpwardAPI,
)
from .mission_planner import MissionPlanner


class FleetManager(FleetManagementAPI):
    """
    Layer-5 conductor.
    No control authority — coordination only.
    """

    def __init__(self, cgcs_api: UpwardAPI, agents: List[str]):
        self.cgcs_api = cgcs_api
        self.agents = agents
        self.planner = MissionPlanner()
        self.active_missions: Dict[str, MissionSpec] = {}

    def submit_mission(self, mission: MissionSpec) -> bool:
        if mission.mission_id in self.active_missions:
            return False

        roles = self.planner.expand_mission(mission)

        if len(roles) > len(self.agents):
            return False

        for agent_id, role in zip(self.agents, roles):
            ok = self.cgcs_api.assign_role_to_agent(agent_id, role)
            if not ok:
                return False

        self.active_missions[mission.mission_id] = mission
        return True

    def cancel_mission(self, mission_id: str) -> bool:
        if mission_id not in self.active_missions:
            return False

        del self.active_missions[mission_id]
        return True
