# ⚠️🧡 CAUTION + 🧭💛 INDEX-ONLY — Loop Guard & Coordinator
# 🧾💙 HASHED — Provenance available
# 🔐💜 DAVNA COVENANT — Deterministic · Autonomous · Verifiable · Non-hoarding · Anti-loops
# ⛔🖤 REFUSAL-FIRST — De-escalation without diagnosis
# 🚫❤️‍🔥 PROHIBITED — No diagnosis, no content retention

"""
Coordinator System

Implements loop prevention, de-escalation, and agent coordination.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import deque


@dataclass
class ActionRecord:
    """Record of an action in the system."""
    agent_id: str
    action: str
    timestamp: datetime
    context: str = ""


@dataclass
class LoopDetection:
    """Configuration for loop detection."""
    window_size: int = 10  # Number of recent actions to check
    similarity_threshold: float = 0.8  # Similarity threshold for loop detection
    max_repetitions: int = 3  # Maximum allowed repetitions


class Coordinator:
    """
    Coordinates multiple agents with loop prevention and de-escalation.
    
    Prevents infinite loops and manages escalation of agent behaviors.
    """
    
    def __init__(
        self,
        consent_manager=None,
        fatigue_tracker=None,
        memory_store=None,
        loop_detection: Optional[LoopDetection] = None
    ):
        """
        Initialize coordinator.
        
        Args:
            consent_manager: ConsentManager instance
            fatigue_tracker: FatigueTracker instance
            memory_store: MemoryStore instance
            loop_detection: Loop detection configuration
        """
        self._consent_manager = consent_manager
        self._fatigue_tracker = fatigue_tracker
        self._memory_store = memory_store
        self._loop_config = loop_detection or LoopDetection()
        
        self._agents: Dict[str, 'Agent'] = {}
        self._action_history: deque = deque(maxlen=self._loop_config.window_size)
        self._escalation_levels: Dict[str, int] = {}
        self._circuit_breakers: Set[str] = set()  # Agents in circuit breaker state
    
    def register_agent(self, agent: 'Agent') -> bool:
        """
        Register an agent with the coordinator.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if registered successfully
        """
        self._agents[agent.agent_id] = agent
        self._escalation_levels[agent.agent_id] = 0
        
        # Also register with fatigue tracker if available
        if self._fatigue_tracker:
            self._fatigue_tracker.register_agent(agent.agent_id)
        
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the coordinator.
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if agent_id not in self._agents:
            return False
        
        del self._agents[agent_id]
        self._escalation_levels.pop(agent_id, None)
        self._circuit_breakers.discard(agent_id)
        return True
    
    def coordinate_action(
        self,
        agent_id: str,
        action: str,
        context: str = ""
    ) -> bool:
        """
        Coordinate an action by an agent with loop prevention.
        
        Args:
            agent_id: ID of the agent performing action
            action: Action identifier
            context: Optional context for the action
            
        Returns:
            True if action is allowed, False if prevented (loop/escalation)
        """
        # Check if agent is in circuit breaker state
        if agent_id in self._circuit_breakers:
            return False
        
        # Check if agent exists
        if agent_id not in self._agents:
            return False
        
        agent = self._agents[agent_id]
        
        # Check if agent can perform action
        if not agent.can_perform_action(action):
            return False
        
        # Check for loops
        if self._detect_loop(agent_id, action):
            self._trigger_de_escalation(agent_id)
            return False
        
        # Check escalation level
        if self._escalation_levels[agent_id] >= 5:
            self._trigger_circuit_breaker(agent_id)
            return False
        
        # Record action
        record = ActionRecord(
            agent_id=agent_id,
            action=action,
            timestamp=datetime.now(),
            context=context
        )
        self._action_history.append(record)
        
        # Record in fatigue tracker if available
        if self._fatigue_tracker:
            if not self._fatigue_tracker.record_action(agent_id):
                # Agent is too fatigued, trigger de-escalation
                self._trigger_de_escalation(agent_id)
                return False
        
        # Reset escalation on successful diverse action
        if not self._is_repetitive_action(agent_id, action):
            self._escalation_levels[agent_id] = max(0, self._escalation_levels[agent_id] - 1)
        
        return True
    
    def _detect_loop(self, agent_id: str, action: str) -> bool:
        """
        Detect if an action would create a loop.
        
        Args:
            agent_id: ID of the agent
            action: Action being attempted
            
        Returns:
            True if loop detected, False otherwise
        """
        # Count recent identical actions by this agent
        recent_actions = [
            record for record in self._action_history
            if record.agent_id == agent_id and record.action == action
        ]
        
        # Check if too many repetitions in window
        if len(recent_actions) >= self._loop_config.max_repetitions:
            # Check if they're recent (within last few actions)
            recent_count = sum(
                1 for record in list(self._action_history)[-5:]
                if record.agent_id == agent_id and record.action == action
            )
            if recent_count >= self._loop_config.max_repetitions:
                return True
        
        return False
    
    def _is_repetitive_action(self, agent_id: str, action: str) -> bool:
        """Check if action is repetitive for the agent."""
        recent = list(self._action_history)[-3:]
        return all(
            record.agent_id == agent_id and record.action == action
            for record in recent
        )
    
    def _trigger_de_escalation(self, agent_id: str) -> None:
        """
        Trigger de-escalation for an agent.
        
        Args:
            agent_id: ID of the agent to de-escalate
        """
        self._escalation_levels[agent_id] = min(10, self._escalation_levels[agent_id] + 2)
        
        # Force rest if fatigue tracker available
        if self._fatigue_tracker:
            self._fatigue_tracker.start_rest(agent_id)
    
    def _trigger_circuit_breaker(self, agent_id: str) -> None:
        """
        Trigger circuit breaker for an agent (temporary suspension).
        
        Args:
            agent_id: ID of the agent to suspend
        """
        self._circuit_breakers.add(agent_id)
        
        # Deactivate agent
        if agent_id in self._agents:
            self._agents[agent_id].deactivate()
    
    def reset_circuit_breaker(self, agent_id: str) -> bool:
        """
        Reset circuit breaker for an agent.
        
        Args:
            agent_id: ID of the agent to reset
            
        Returns:
            True if reset, False if agent not found or not in breaker state
        """
        if agent_id not in self._circuit_breakers:
            return False
        
        self._circuit_breakers.remove(agent_id)
        self._escalation_levels[agent_id] = 0
        
        # Reactivate agent
        if agent_id in self._agents:
            self._agents[agent_id].activate()
        
        return True
    
    def get_escalation_level(self, agent_id: str) -> int:
        """Get current escalation level for an agent."""
        return self._escalation_levels.get(agent_id, 0)
    
    def is_circuit_broken(self, agent_id: str) -> bool:
        """Check if agent is in circuit breaker state."""
        return agent_id in self._circuit_breakers
    
    def get_recent_actions(self, limit: int = 10) -> List[ActionRecord]:
        """
        Get recent action history.
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of recent action records
        """
        return list(self._action_history)[-limit:]
    
    def clear_history(self, agent_id: Optional[str] = None) -> int:
        """
        Clear action history, optionally for a specific agent.
        
        Args:
            agent_id: If provided, only clear actions from this agent
            
        Returns:
            Number of records cleared
        """
        if agent_id:
            original_len = len(self._action_history)
            self._action_history = deque(
                [record for record in self._action_history if record.agent_id != agent_id],
                maxlen=self._loop_config.window_size
            )
            return original_len - len(self._action_history)
        else:
            count = len(self._action_history)
            self._action_history.clear()
            return count
