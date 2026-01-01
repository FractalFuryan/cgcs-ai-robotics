"""
Fatigue Tracking System

Implements fatigue-aware role coordination with recovery through rest.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional


class FatigueLevel(Enum):
    """Levels of fatigue for an agent."""
    FRESH = "fresh"
    ACTIVE = "active"
    TIRED = "tired"
    EXHAUSTED = "exhausted"
    RECOVERING = "recovering"


@dataclass
class FatigueState:
    """Represents the fatigue state of an agent."""
    agent_id: str
    level: FatigueLevel = FatigueLevel.FRESH
    energy: float = 100.0  # 0-100 scale
    actions_count: int = 0
    last_action: Optional[datetime] = None
    rest_started: Optional[datetime] = None
    recovery_rate: float = 10.0  # Energy points per minute of rest
    
    def update_energy(self) -> None:
        """Update energy based on recovery if resting."""
        if self.rest_started and self.level == FatigueLevel.RECOVERING:
            elapsed = (datetime.now() - self.rest_started).total_seconds() / 60.0
            recovered = elapsed * self.recovery_rate
            self.energy = min(100.0, self.energy + recovered)
            
            # Update fatigue level based on energy
            if self.energy >= 80:
                self.level = FatigueLevel.FRESH
                self.rest_started = None
            elif self.energy >= 60:
                self.level = FatigueLevel.ACTIVE


class FatigueTracker:
    """
    Tracks agent fatigue and enforces rest periods.
    
    Implements fatigue-aware coordination where agents must rest to recover.
    """
    
    def __init__(
        self,
        energy_cost_per_action: float = 5.0,
        max_actions_before_rest: int = 20,
        min_rest_duration: timedelta = timedelta(minutes=5)
    ):
        """
        Initialize fatigue tracker.
        
        Args:
            energy_cost_per_action: Energy cost for each action
            max_actions_before_rest: Maximum actions before mandatory rest
            min_rest_duration: Minimum rest duration before resuming
        """
        self._states: Dict[str, FatigueState] = {}
        self._energy_cost = energy_cost_per_action
        self._max_actions = max_actions_before_rest
        self._min_rest = min_rest_duration
    
    def register_agent(self, agent_id: str) -> FatigueState:
        """
        Register a new agent for fatigue tracking.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Initial FatigueState for the agent
        """
        state = FatigueState(agent_id=agent_id)
        self._states[agent_id] = state
        return state
    
    def record_action(self, agent_id: str) -> bool:
        """
        Record an action performed by an agent.
        
        Args:
            agent_id: Identifier of the agent performing action
            
        Returns:
            True if action is allowed, False if agent is too fatigued
        """
        if agent_id not in self._states:
            self.register_agent(agent_id)
        
        state = self._states[agent_id]
        
        # Update energy from recovery if applicable
        state.update_energy()
        
        # Check if agent is recovering
        if state.level == FatigueLevel.RECOVERING:
            if not self._can_resume(state):
                return False
        
        # Check if agent is too exhausted
        if state.level == FatigueLevel.EXHAUSTED:
            return False
        
        # Deduct energy and record action
        state.energy -= self._energy_cost
        state.actions_count += 1
        state.last_action = datetime.now()
        
        # Update fatigue level
        self._update_fatigue_level(state)
        
        # Force rest if too many actions
        if state.actions_count >= self._max_actions:
            self.start_rest(agent_id)
            return False
        
        return True
    
    def _update_fatigue_level(self, state: FatigueState) -> None:
        """Update fatigue level based on current energy."""
        if state.energy <= 0:
            state.level = FatigueLevel.EXHAUSTED
            state.energy = 0
        elif state.energy <= 25:
            state.level = FatigueLevel.TIRED
        elif state.energy <= 60:
            state.level = FatigueLevel.ACTIVE
        else:
            state.level = FatigueLevel.FRESH
    
    def start_rest(self, agent_id: str) -> bool:
        """
        Start rest period for an agent.
        
        Args:
            agent_id: Identifier of the agent to rest
            
        Returns:
            True if rest was started, False if agent not registered
        """
        if agent_id not in self._states:
            return False
        
        state = self._states[agent_id]
        state.level = FatigueLevel.RECOVERING
        state.rest_started = datetime.now()
        state.actions_count = 0  # Reset action counter
        return True
    
    def _can_resume(self, state: FatigueState) -> bool:
        """Check if agent has rested long enough to resume."""
        if not state.rest_started:
            return True
        
        elapsed = datetime.now() - state.rest_started
        return elapsed >= self._min_rest and state.energy >= 50
    
    def can_act(self, agent_id: str) -> bool:
        """
        Check if an agent can perform an action.
        
        Args:
            agent_id: Identifier of the agent to check
            
        Returns:
            True if agent can act, False if too fatigued
        """
        if agent_id not in self._states:
            return True  # New agents can act
        
        state = self._states[agent_id]
        state.update_energy()
        
        if state.level == FatigueLevel.EXHAUSTED:
            return False
        
        if state.level == FatigueLevel.RECOVERING:
            return self._can_resume(state)
        
        return True
    
    def get_state(self, agent_id: str) -> Optional[FatigueState]:
        """Get current fatigue state for an agent."""
        state = self._states.get(agent_id)
        if state:
            state.update_energy()
        return state
    
    def reset_agent(self, agent_id: str) -> bool:
        """
        Reset fatigue state for an agent.
        
        Args:
            agent_id: Identifier of the agent to reset
            
        Returns:
            True if reset successful, False if agent not found
        """
        if agent_id not in self._states:
            return False
        
        self._states[agent_id] = FatigueState(agent_id=agent_id)
        return True
