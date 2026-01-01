"""
Memory Store System

Implements opt-in, cue-based memory that forgets by default.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set


@dataclass
class MemoryCue:
    """A cue that triggers memory storage or retrieval."""
    cue_id: str
    pattern: str
    description: str
    enabled: bool = True


@dataclass
class Memory:
    """Represents a stored memory."""
    memory_id: str
    agent_id: str
    content: str
    cues: Set[str] = field(default_factory=set)
    timestamp: datetime = field(default_factory=datetime.now)
    consent_id: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


class MemoryStore:
    """
    Manages opt-in, cue-based memory storage.
    
    Designed to forget by default - memories are only stored with explicit
    consent and are retrieved only when specific cues are present.
    """
    
    def __init__(self, consent_manager=None):
        """
        Initialize memory store.
        
        Args:
            consent_manager: ConsentManager instance for checking permissions
        """
        self._memories: Dict[str, Memory] = {}
        self._cues: Dict[str, MemoryCue] = {}
        self._consent_manager = consent_manager
        self._cue_index: Dict[str, Set[str]] = {}  # cue_id -> memory_ids
    
    def register_cue(
        self,
        cue_id: str,
        pattern: str,
        description: str
    ) -> MemoryCue:
        """
        Register a memory cue.
        
        Args:
            cue_id: Unique identifier for the cue
            pattern: Pattern that triggers this cue
            description: Human-readable description
            
        Returns:
            MemoryCue object
        """
        cue = MemoryCue(
            cue_id=cue_id,
            pattern=pattern,
            description=description
        )
        self._cues[cue_id] = cue
        self._cue_index[cue_id] = set()
        return cue
    
    def store_memory(
        self,
        memory_id: str,
        agent_id: str,
        content: str,
        cues: Set[str],
        consent_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Memory]:
        """
        Store a memory with explicit consent.
        
        Args:
            memory_id: Unique identifier for the memory
            agent_id: ID of the agent storing the memory
            content: Content to store
            cues: Set of cue IDs that trigger this memory
            consent_id: ID of consent approval (required if consent manager set)
            metadata: Optional metadata
            
        Returns:
            Memory object if stored, None if consent not granted
        """
        # Check consent if manager is set
        if self._consent_manager:
            from .consent import ConsentType
            if not self._consent_manager.check_consent(
                agent_id,
                ConsentType.MEMORY_STORE,
                consent_id
            ):
                return None
        
        # Create and store memory
        memory = Memory(
            memory_id=memory_id,
            agent_id=agent_id,
            content=content,
            cues=cues,
            consent_id=consent_id,
            metadata=metadata or {}
        )
        
        self._memories[memory_id] = memory
        
        # Index by cues
        for cue_id in cues:
            if cue_id in self._cue_index:
                self._cue_index[cue_id].add(memory_id)
        
        return memory
    
    def retrieve_by_cue(
        self,
        cue_id: str,
        agent_id: str,
        consent_id: Optional[str] = None
    ) -> List[Memory]:
        """
        Retrieve memories triggered by a specific cue.
        
        Args:
            cue_id: ID of the cue triggering retrieval
            agent_id: ID of the agent requesting retrieval
            consent_id: ID of consent approval (required if consent manager set)
            
        Returns:
            List of memories associated with the cue (empty if no consent)
        """
        # Check consent if manager is set
        if self._consent_manager:
            from .consent import ConsentType
            if not self._consent_manager.check_consent(
                agent_id,
                ConsentType.MEMORY_RETRIEVE,
                consent_id
            ):
                return []
        
        # Check if cue exists and is enabled
        if cue_id not in self._cues or not self._cues[cue_id].enabled:
            return []
        
        # Retrieve memories
        memory_ids = self._cue_index.get(cue_id, set())
        return [self._memories[mid] for mid in memory_ids if mid in self._memories]
    
    def forget(self, memory_id: str) -> bool:
        """
        Forget (delete) a specific memory.
        
        Args:
            memory_id: ID of the memory to forget
            
        Returns:
            True if memory was forgotten, False if not found
        """
        if memory_id not in self._memories:
            return False
        
        memory = self._memories[memory_id]
        
        # Remove from cue index
        for cue_id in memory.cues:
            if cue_id in self._cue_index:
                self._cue_index[cue_id].discard(memory_id)
        
        # Delete memory
        del self._memories[memory_id]
        return True
    
    def forget_all(self, agent_id: Optional[str] = None) -> int:
        """
        Forget all memories, optionally filtered by agent.
        
        Args:
            agent_id: If provided, only forget memories from this agent
            
        Returns:
            Number of memories forgotten
        """
        if agent_id:
            to_forget = [
                mid for mid, mem in self._memories.items()
                if mem.agent_id == agent_id
            ]
        else:
            to_forget = list(self._memories.keys())
        
        count = 0
        for memory_id in to_forget:
            if self.forget(memory_id):
                count += 1
        
        return count
    
    def disable_cue(self, cue_id: str) -> bool:
        """
        Disable a memory cue.
        
        Args:
            cue_id: ID of the cue to disable
            
        Returns:
            True if disabled, False if cue not found
        """
        if cue_id not in self._cues:
            return False
        
        self._cues[cue_id].enabled = False
        return True
    
    def enable_cue(self, cue_id: str) -> bool:
        """
        Enable a memory cue.
        
        Args:
            cue_id: ID of the cue to enable
            
        Returns:
            True if enabled, False if cue not found
        """
        if cue_id not in self._cues:
            return False
        
        self._cues[cue_id].enabled = True
        return True
    
    def get_memory_count(self, agent_id: Optional[str] = None) -> int:
        """
        Get count of stored memories.
        
        Args:
            agent_id: If provided, count only memories from this agent
            
        Returns:
            Number of memories
        """
        if agent_id:
            return sum(1 for mem in self._memories.values() if mem.agent_id == agent_id)
        return len(self._memories)
