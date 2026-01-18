"""
mission_planner.py
Deterministically expands missions into bounded roles.
"""

from typing import List, Dict
from .interfaces import MissionSpec, BoundedRole


class MissionPlanner:
    """
    Stateless, deterministic planner.
    No optimization, no heuristics.
    """

    def expand_mission(self, mission: MissionSpec) -> List[BoundedRole]:
        roles: List[BoundedRole] = []

        for role_name in mission.required_roles:
            roles.append(
                BoundedRole(
                    role_name=role_name,
                    capabilities=self._capabilities_for(role_name),
                    constraints=self._constraints_for(mission),
                    mission_id=mission.mission_id,
                )
            )
        return roles

    def _capabilities_for(self, role_name: str) -> List[str]:
        return {
            "scout": ["navigate", "scan", "report"],
            "transport": ["carry", "deliver"],
            "observer": ["monitor", "signal"],
        }.get(role_name, [])

    def _constraints_for(self, mission: MissionSpec) -> Dict[str, float]:
        return {
            "max_duration_s": mission.parameters.get("max_duration_s", 300),
            "max_range_m": mission.parameters.get("max_range_m", 100.0),
        }
