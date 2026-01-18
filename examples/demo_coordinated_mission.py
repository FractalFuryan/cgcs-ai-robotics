"""
demo_coordinated_mission.py
Demonstrates CGCS + Fleet Manager + Mission Planner integration.
"""

import sys
sys.path.insert(0, '/workspaces/cgcs-ai-robotics')

from stack.interfaces import (
    MissionSpec,
    BoundedRole,
    WorldCue,
    UpwardAPI,
)
from stack.fleet_manager import FleetManager
from typing import Dict


class MockCGCS(UpwardAPI):
    """Minimal CGCS adapter for demo/testing."""

    def __init__(self):
        self.roles: Dict[str, BoundedRole] = {}

    def assign_role_to_agent(self, agent_id: str, role: BoundedRole) -> bool:
        self.roles[agent_id] = role
        print(f"[CGCS] Assigned {role.role_name} to {agent_id}")
        return True

    def inject_world_cue(self, agent_id: str, cue: WorldCue) -> bool:
        print(f"[CGCS] Cue injected for {agent_id}: {cue.tag}")
        return True


if __name__ == "__main__":
    cgcs = MockCGCS()
    fleet = FleetManager(cgcs_api=cgcs, agents=["A1", "A2"])

    mission = MissionSpec(
        mission_id="M-001",
        objective="Grid scan",
        parameters={"max_duration_s": 120},
        required_roles=["scout", "observer"],
    )

    ok = fleet.submit_mission(mission)
    print("Mission accepted:", ok)
