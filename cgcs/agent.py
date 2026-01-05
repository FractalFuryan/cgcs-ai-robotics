# 🧭💛 INDEX-ONLY + 📖💚 PUBLIC — Agent & Role System
# 🧾💙 HASHED — Provenance available
# 🔐💜 DAVNA COVENANT — Deterministic · Autonomous · Verifiable · Non-hoarding · Anti-loops
# ⛔🖤 REFUSAL-FIRST — Role assignment requires consent
# 🚫❤️‍🔥 PROHIBITED — No secrets, no identifiers, no raw logs

"""
Agent and Role System

Implements bounded roles for agent coordination.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class RoleType(Enum):
    """Predefined role types for agents."""
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    OBSERVER = "observer"
    VALIDATOR = "validator"
    CUSTOM = "custom"


@dataclass
class Role:
    """
    Represents a bounded role that an agent can assume.
    
    Roles define what actions an agent is permitted to perform.
    """
    role_id: str
    role_type: RoleType
    name: str
    description: str
    permitted_actions: Set[str] = field(default_factory=set)
    max_duration: Optional[int] = None  # Maximum duration in seconds
    requires_consent: bool = True
    
    def can_perform(self, action: str) -> bool:
        """Check if this role permits a specific action."""
        return action in self.permitted_actions or "*" in self.permitted_actions


@dataclass
class AgentState:
    """Represents the current state of an agent."""
    agent_id: str
    current_role: Optional[Role] = None
    role_assigned_at: Optional[datetime] = None
    is_active: bool = True
    action_history: List[str] = field(default_factory=list)


class Agent:
    """
    Represents an agent in the CGCS system.
    
    Agents operate through bounded roles and must have appropriate
    consent to perform actions.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        consent_manager=None,
        fatigue_tracker=None
    ):
        """
        Initialize an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            consent_manager: ConsentManager instance
            fatigue_tracker: FatigueTracker instance
        """
        self.agent_id = agent_id
        self.name = name
        self._consent_manager = consent_manager
        self._fatigue_tracker = fatigue_tracker
        self._state = AgentState(agent_id=agent_id)
    
    def assign_role(
        self,
        role: Role,
        consent_id: Optional[str] = None
    ) -> bool:
        """
        Assign a role to this agent.
        
        Args:
            role: Role to assign
            consent_id: Consent approval ID (required if role requires consent)
            
        Returns:
            True if role was assigned, False if consent not granted
        """
        # Check consent if required
        if role.requires_consent and self._consent_manager:
            from .consent import ConsentType
            if not self._consent_manager.check_consent(
                self.agent_id,
                ConsentType.ROLE_ASSIGNMENT,
                consent_id
            ):
                return False
        
        self._state.current_role = role
        self._state.role_assigned_at = datetime.now()
        return True
    
    def release_role(self) -> bool:
        """
        Release the current role.
        
        Returns:
            True if role was released, False if no role assigned
        """
        if not self._state.current_role:
            return False
        
        self._state.current_role = None
        self._state.role_assigned_at = None
        return True
    
    def can_perform_action(self, action: str) -> bool:
        """
        Check if agent can perform a specific action.
        
        Args:
            action: Action identifier to check
            
        Returns:
            True if action is permitted, False otherwise
        """
        # Check if agent is active
        if not self._state.is_active:
            return False
        
        # Check fatigue
        if self._fatigue_tracker and not self._fatigue_tracker.can_act(self.agent_id):
            return False
        
        # Check role permissions
        if not self._state.current_role:
            return False
        
        return self._state.current_role.can_perform(action)
    
    def perform_action(
        self,
        action: str,
        consent_id: Optional[str] = None
    ) -> bool:
        """
        Perform an action with consent and fatigue checking.
        
        Args:
            action: Action identifier to perform
            consent_id: Consent approval ID for this specific action
            
        Returns:
            True if action was performed, False otherwise
        """
        # Check if action is permitted
        if not self.can_perform_action(action):
            return False
        
        # Check specific action consent if consent manager exists
        if self._consent_manager and consent_id:
            from .consent import ConsentType
            if not self._consent_manager.check_consent(
                self.agent_id,
                ConsentType.ACTION,
                consent_id
            ):
                return False
        
        # Record action in fatigue tracker
        if self._fatigue_tracker:
            if not self._fatigue_tracker.record_action(self.agent_id):
                return False  # Too fatigued
        
        # Record action in history
        self._state.action_history.append(action)
        
        return True
    
    def deactivate(self) -> None:
        """Deactivate the agent."""
        self._state.is_active = False
        self.release_role()
    
    def activate(self) -> None:
        """Activate the agent."""
        self._state.is_active = True
    
    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self._state
    
    def get_current_role(self) -> Optional[Role]:
        """Get currently assigned role."""
        return self._state.current_role
