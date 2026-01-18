"""
interfaces.py
Defines the core APIs for the CGCS-Integrated Robotics Stack.
Formal, deterministic interfaces only.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ===================== DATA MODELS =====================

@dataclass(frozen=True)
class MissionSpec:
    mission_id: str
    objective: str
    parameters: Dict[str, Any]
    required_roles: List[str]


@dataclass(frozen=True)
class BoundedRole:
    role_name: str
    capabilities: List[str]
    constraints: Dict[str, Any]
    mission_id: str


@dataclass(frozen=True)
class ActionRequest:
    source_agent_id: str
    source_role: str
    action_type: str
    parameters: Dict[str, Any]
    priority: int = 5


@dataclass(frozen=True)
class WorldCue:
    cue_id: str
    tag: str
    data: Dict[str, Any]
    ttl: Optional[int] = None


# ===================== APIS =====================

class UpwardAPI(ABC):
    """Lower layers → CGCS"""

    @abstractmethod
    def assign_role_to_agent(self, agent_id: str, role: BoundedRole) -> bool:
        pass

    @abstractmethod
    def inject_world_cue(self, agent_id: str, cue: WorldCue) -> bool:
        pass


class DownwardAPI(ABC):
    """CGCS → Lower layers"""

    @abstractmethod
    def request_action(self, request: ActionRequest) -> bool:
        pass

    @abstractmethod
    def share_cue_with_fleet(
        self, cue: WorldCue, target_agent_ids: List[str]
    ) -> bool:
        pass


class FleetManagementAPI(ABC):
    """Top-level orchestration"""

    @abstractmethod
    def submit_mission(self, mission: MissionSpec) -> bool:
        pass

    @abstractmethod
    def cancel_mission(self, mission_id: str) -> bool:
        pass
