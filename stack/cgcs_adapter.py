"""
cgcs_adapter.py
Adapter connecting the robotics stack interfaces to the actual CGCS engine.
Makes CGCS a proper Layer 4 component in the stack.
"""
import sys
import os
from typing import List, Dict, Any, Optional
import time

# Add parent directory to path for CGCS imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import actual CGCS components
try:
    # Import from parent directory
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    import cgcs_core
    # CANONICAL_ROLES is in cgcs_core, not role_spec
    from cgcs_core import CANONICAL_ROLES
    HAS_CGCS = True
except ImportError as e:
    HAS_CGCS = False
    print(f"⚠️  Warning: Could not import CGCS core modules ({e}). Using stub implementation.")

from .interfaces import UpwardAPI, DownwardAPI, BoundedRole, ActionRequest, WorldCue


class CGCSAgentAdapter(UpwardAPI, DownwardAPI):
    """
    Real adapter connecting stack interfaces to CGCS engine.
    Each physical robot has one instance.
    """
    
    def __init__(self, agent_id: str, robot_capabilities: List[str]):
        """
        Args:
            agent_id: Unique identifier for this robot/agent
            robot_capabilities: Physical capabilities this robot has
        """
        self.agent_id = agent_id
        self.capabilities = robot_capabilities
        self.current_role: Optional[BoundedRole] = None
        self.role_start_time: Optional[float] = None
        
        # Initialize CGCS components
        if HAS_CGCS:
            self.role_mgr = cgcs_core.RoleManager(max_load=1.0, min_battery=0.3)
            self.stress = cgcs_core.StressEngine()
            self.loop_guard = cgcs_core.LoopGuard(window_s=120, cooldown_s=90)
            self.memory = cgcs_core.DualMemory(thread_max_turns=50)
            print(f"✅ [{agent_id}] CGCS core engine initialized")
        else:
            self.role_mgr = None
            self.stress = None
            self.loop_guard = None
            self.memory = None
            print(f"⚠️  [{agent_id}] Using stub CGCS (real modules not found)")
    
    # ========== UpwardAPI Implementation ==========
    
    def assign_role_to_agent(self, agent_id: str, role: BoundedRole) -> bool:
        """Fleet Manager instructs this agent to adopt a bounded role."""
        if agent_id != self.agent_id:
            return False
        
        print(f"🎭 [{self.agent_id}] CGCS adopting bounded role: '{role.role_name}'")
        print(f"   └─ Capabilities: {role.capabilities}")
        print(f"   └─ Constraints: {role.constraints}")
        
        # Validate robot has required capabilities
        for required_cap in role.capabilities:
            if required_cap not in self.capabilities:
                print(f"   ⚠️  Warning: Robot lacks capability '{required_cap}'")
        
        # Store the role
        self.current_role = role
        self.role_start_time = time.time()
        
        # Activate role in CGCS RoleManager if possible
        if self.role_mgr and HAS_CGCS:
            # Map to canonical CGCS role if it exists
            cgcs_role_key = self._map_to_cgcs_role(role.role_name)
            if cgcs_role_key:
                # Require explicit consent for roles that need it
                consent = not CANONICAL_ROLES[cgcs_role_key].requires_explicit_consent
                battery = 1.0  # Assume full battery for demo
                
                ok, reasons = self.role_mgr.activate(cgcs_role_key, consent=consent, battery=battery)
                if ok:
                    print(f"   ✅ CGCS role '{cgcs_role_key}' activated")
                else:
                    print(f"   ⚠️  CGCS role activation blocked: {', '.join(reasons)}")
        
        return True
    
    def inject_world_cue(self, agent_id: str, cue: WorldCue) -> bool:
        """World Model provides new information as potential memory cue."""
        if agent_id != self.agent_id:
            return False
        
        print(f"🗺️  [{self.agent_id}] World Model cue received: '{cue.tag}'")
        print(f"   └─ Data: {cue.data}")
        
        # Process with CGCS memory system
        if self.memory and HAS_CGCS:
            # Evaluate consent for this cue
            consent_given = self._evaluate_cue_consent(cue)
            
            if consent_given:
                # Format as memory with symbol tag
                memory_text = f"[SYM:{cue.tag}] {cue.data}"
                symbols, clean_text = cgcs_core.parse_symbols(memory_text)
                
                # Add to dual memory (record turn + anchor if consented)
                self.memory.record_turn(clean_text, symbols)
                self.memory.anchor_opt_in(symbols, clean_text, allow_anchor=True)
                print(f"   ✅ Cue anchored with symbol: {cue.tag}")
            else:
                print(f"   ⏸️  Cue not anchored (no consent)")
        
        return True
    
    def _evaluate_cue_consent(self, cue: WorldCue) -> bool:
        """
        CGCS consent evaluation logic.
        Checks role relevance, fatigue, and TTL.
        """
        if not self.current_role:
            return False
        
        # Check if cue is relevant to current role
        role_keywords = self.current_role.role_name.lower()
        cue_relevance = role_keywords in cue.tag.lower()
        
        # Check TTL
        if cue.ttl and cue.ttl < time.time():
            return False
        
        # Check fatigue if available
        if self.stress and HAS_CGCS:
            cgcs_role_key = self._map_to_cgcs_role(self.current_role.role_name)
            if cgcs_role_key:
                sigma = self.stress.state.get(cgcs_role_key, cgcs_core.StressState()).sigma
                if sigma > 0.8:  # High fatigue reduces consent
                    return False
        
        return cue_relevance
    
    # ========== DownwardAPI Implementation ==========
    
    def request_action(self, request: ActionRequest) -> bool:
        """CGCS requests an action (output to planning/control layer)."""
        # Verify request comes from our current role
        if request.source_agent_id != self.agent_id:
            print(f"⚠️  [{self.agent_id}] Action request agent mismatch")
            return False
        
        if not self.current_role or request.source_role != self.current_role.role_name:
            print(f"⚠️  [{self.agent_id}] Action request role mismatch")
            return False
        
        # Verify action is allowed by role capabilities
        if request.action_type not in self.current_role.capabilities:
            print(f"⚠️  [{self.agent_id}] Action '{request.action_type}' not in role capabilities")
            return False
        
        print(f"⚡ [{self.agent_id}] CGCS requests ACTION: {request.action_type}")
        print(f"   └─ Parameters: {request.parameters}")
        print(f"   └─ Priority: {request.priority}")
        
        # Check LoopGuard and fatigue
        if self.loop_guard and HAS_CGCS:
            check = self.loop_guard.observe(str(request.parameters))
            if check["mode"] == "deescalate":
                print(f"   ⚠️  LoopGuard active: {check['reason']}")
        
        if self.stress and HAS_CGCS:
            cgcs_role_key = self._map_to_cgcs_role(self.current_role.role_name)
            if cgcs_role_key:
                sigma = self.stress.state.get(cgcs_role_key, cgcs_core.StressState()).sigma
                if sigma > 0.8:
                    print(f"   ⚠️  High fatigue ({sigma:.2f}), action may be degraded")
        
        # In real system, this interfaces with robot control layer
        return True
    
    def share_cue_with_fleet(self, cue: WorldCue, target_agent_ids: List[str]) -> bool:
        """CGCS consents to share a memory cue with other agents."""
        print(f"🔗 [{self.agent_id}] CGCS shares cue '{cue.tag}' with {len(target_agent_ids)} agents")
        print(f"   └─ Target agents: {target_agent_ids}")
        print(f"   └─ Cue data: {cue.data}")
        
        # Consent-based sharing - in full implementation would send via comms layer
        for target_id in target_agent_ids:
            print(f"   → To {target_id}: Cue '{cue.tag}' shared (consent-based)")
        
        return True
    
    # ========== Helper Methods ==========
    
    def _map_to_cgcs_role(self, role_name: str) -> Optional[str]:
        """Map stack role names to CGCS canonical roles."""
        mapping = {
            "scout": "maintenance",      # Closest match: inspect, diagnose, report
            "observer": "social_presence",  # Stand by, acknowledge
            "transport": "transport",    # Direct mapping
        }
        return mapping.get(role_name.lower())
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of this CGCS-powered agent."""
        status = {
            "agent_id": self.agent_id,
            "has_core": HAS_CGCS,
            "capabilities": self.capabilities
        }
        
        if self.current_role:
            role_duration = time.time() - self.role_start_time if self.role_start_time else 0
            status.update({
                "current_role": self.current_role.role_name,
                "role_duration_seconds": round(role_duration, 1),
                "mission_id": self.current_role.mission_id
            })
            
            if self.stress and HAS_CGCS:
                cgcs_role_key = self._map_to_cgcs_role(self.current_role.role_name)
                if cgcs_role_key:
                    sigma = self.stress.state.get(cgcs_role_key, cgcs_core.StressState()).sigma
                    status["fatigue"] = round(sigma, 2)
        
        return status
    
    def step(self, dt: float = 1.0):
        """Update CGCS state (call periodically in control loop)."""
        if self.stress and self.role_mgr and HAS_CGCS:
            # Update stress/fatigue for active roles
            util = {}
            for role_key in self.role_mgr.active:
                util[role_key] = 0.5  # Assume 50% utilization
            
            self.stress.step(dt, self.role_mgr.active, util, global_stress=0.0)
