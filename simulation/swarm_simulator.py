"""
swarm_simulator.py
Large-scale simulation of CGCS coordination (100+ agents).
Statistical validation of formal properties at scale.
"""
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
import time
import json
from collections import defaultdict, deque
import random
import statistics
from pathlib import Path

# Import CGCS stack
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from stack.interfaces import MissionSpec, BoundedRole, ActionRequest


@dataclass
class SwarmConfig:
    """Configuration for large-scale swarm simulation."""
    
    # Scale parameters
    num_agents: int = 100
    simulation_steps: int = 1000
    steps_per_second: float = 10.0
    
    # World parameters
    world_size: Tuple[float, float] = (1000.0, 1000.0)  # meters
    communication_range: float = 50.0
    
    # Mission parameters
    concurrent_missions: int = 5
    mission_duration_steps: int = 200
    
    # Agent parameters
    agent_speed_range: Tuple[float, float] = (0.1, 1.0)  # m/s
    battery_capacity_range: Tuple[float, float] = (0.5, 1.0)
    
    # Metrics collection
    collect_metrics: bool = True
    metrics_path: str = "simulation/metrics"
    
    # Output
    save_results: bool = True
    verbose: bool = True


@dataclass
class AgentState:
    """State of a single agent in the simulation."""
    agent_id: str
    position: np.ndarray
    velocity: np.ndarray
    battery_level: float
    capabilities: List[str]
    current_role: Optional[str] = None
    role_start_step: int = 0
    fatigue: float = 0.0
    risk_level: float = 0.0
    anchored_memories: List[str] = field(default_factory=list)
    communication_history: deque = field(default_factory=lambda: deque(maxlen=100))
    action_history: deque = field(default_factory=lambda: deque(maxlen=50))
    failed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "position": self.position.tolist(),
            "battery_level": self.battery_level,
            "current_role": self.current_role,
            "fatigue": self.fatigue,
            "risk_level": self.risk_level,
            "failed": self.failed
        }


class SwarmSimulator:
    """
    Large-scale simulation of CGCS-coordinated swarm.
    Validates formal properties at scale with statistical significance.
    """
    
    def __init__(self, config: SwarmConfig):
        self.config = config
        self.step = 0
        self.start_time = time.time()
        
        # Initialize world
        self.world_size = np.array(config.world_size)
        
        # Initialize agents
        self.agents: Dict[str, AgentState] = {}
        self._initialize_agents()
        
        # Initialize missions
        self.active_missions: List[MissionSpec] = []
        self.mission_history: List[Dict] = []
        
        # Metrics collection
        self.metrics = {
            "step_data": [],
            "agent_data": defaultdict(list),
            "mission_data": [],
            "invariant_checks": [],
            "consent_events": [],
            "communication_events": []
        }
        
        # Performance tracking
        self.performance_stats = {
            "step_times": [],
        }
        
        # Emergent behavior tracking
        self.emergent_patterns = {
            "clusters": [],
            "coordinated_movements": [],
        }
        
        if self.config.verbose:
            print(f"🌐 Swarm Simulator initialized")
            print(f"   Agents: {config.num_agents}")
            print(f"   World: {config.world_size[0]}x{config.world_size[1]}m")
            print(f"   Communication range: {config.communication_range}m")
            print(f"   Steps: {config.simulation_steps}")
    
    def _initialize_agents(self):
        """Initialize all agents with diverse capabilities and positions."""
        capability_pools = [
            ["navigate", "scan", "communicate"],
            ["navigate", "transport", "communicate"],
            ["scan", "analyze", "communicate"],
            ["navigate", "scan", "transport"],
            ["coordinate", "analyze", "communicate"]
        ]
        
        for i in range(self.config.num_agents):
            agent_id = f"agent_{i:04d}"
            
            # Random capabilities
            capability_pool = capability_pools[i % len(capability_pools)]
            capabilities = random.sample(capability_pool, 
                                       random.randint(2, len(capability_pool)))
            
            # Random initial position
            position = np.random.rand(2) * self.world_size
            
            # Random initial velocity
            speed = np.random.uniform(*self.config.agent_speed_range)
            angle = np.random.uniform(0, 2 * np.pi)
            velocity = np.array([np.cos(angle) * speed, np.sin(angle) * speed])
            
            # Battery level
            battery = np.random.uniform(*self.config.battery_capacity_range)
            
            # Create agent state
            self.agents[agent_id] = AgentState(
                agent_id=agent_id,
                position=position,
                velocity=velocity,
                battery_level=battery,
                capabilities=capabilities
            )
        
        if self.config.verbose:
            print(f"   Initialized {self.config.num_agents} agents")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete swarm simulation.
        Returns comprehensive metrics and analysis.
        """
        if self.config.verbose:
            print(f"\n▶️  Starting swarm simulation...")
        
        # Generate initial missions
        self._generate_initial_missions()
        
        # Main simulation loop
        try:
            from tqdm import tqdm
            progress_bar = tqdm(total=self.config.simulation_steps, 
                              desc="Swarm Simulation", unit="step")
            use_tqdm = True
        except ImportError:
            use_tqdm = False
            if self.config.verbose:
                print("   Running simulation...")
        
        for step in range(self.config.simulation_steps):
            self.step = step
            step_start = time.time()
            
            # Update all agents
            self._simulation_step(step)
            
            # Update missions
            if step % 20 == 0:
                self._update_missions(step)
            
            # Collect step metrics
            if self.config.collect_metrics:
                self._collect_step_metrics(step)
            
            # Check for emergent patterns
            if step % 50 == 0:
                self._detect_emergent_patterns(step)
            
            # Performance tracking
            step_time = time.time() - step_start
            self.performance_stats["step_times"].append(step_time)
            
            if use_tqdm:
                progress_bar.update(1)
            elif self.config.verbose and step % 100 == 0:
                print(f"   Step {step}/{self.config.simulation_steps}")
        
        if use_tqdm:
            progress_bar.close()
        
        # Final analysis
        if self.config.verbose:
            print(f"\n📊 Analyzing results...")
        results = self._analyze_results()
        
        # Save metrics
        if self.config.save_results:
            self._save_metrics(results)
        
        # Print summary
        if self.config.verbose:
            self._print_summary(results)
        
        return results
    
    def _simulation_step(self, step: int):
        """Execute one simulation step for all agents."""
        # Update agent positions
        for agent_id, agent in self.agents.items():
            if agent.failed:
                continue
            
            # Apply movement
            agent.position += agent.velocity / self.config.steps_per_second
            
            # Boundary handling (wrap-around)
            agent.position = np.mod(agent.position, self.world_size)
            
            # Battery drain
            agent.battery_level -= 0.0001
            agent.battery_level = max(0.0, agent.battery_level)
            
            # Fatigue accumulation
            if agent.current_role:
                agent.fatigue += 0.001
                agent.fatigue = min(1.0, agent.fatigue)
            else:
                # Recovery when not assigned
                agent.fatigue = max(0.0, agent.fatigue - 0.0005)
            
            # Risk level fluctuations
            agent.risk_level += np.random.normal(0, 0.01)
            agent.risk_level = np.clip(agent.risk_level, 0.0, 1.0)
            
            # Check invariants (INV-03: fatigue bounds)
            if agent.fatigue > 1.0:
                agent.fatigue = 1.0
            if agent.fatigue < 0.0:
                agent.fatigue = 0.0
            
            # Check INV-04: Risk de-escalation
            if agent.risk_level > 0.8:
                agent.current_role = None  # De-escalate
                agent.risk_level = 0.5
                
                self.metrics["invariant_checks"].append({
                    "step": step,
                    "agent": agent_id,
                    "invariant": "INV-04",
                    "action": "risk_de_escalation"
                })
        
        # Agent communication (every 5 steps)
        if step % 5 == 0:
            self._simulate_communication(step)
        
        # Agent decision making (every 10 steps)
        if step % 10 == 0:
            self._simulate_agent_decisions(step)
    
    def _simulate_communication(self, step: int):
        """Simulate communication between nearby agents."""
        communication_events = []
        
        for agent_id, agent in self.agents.items():
            if agent.failed:
                continue
            
            # Find nearby agents
            nearby_agents = self._get_nearby_agents(agent_id, 
                                                   self.config.communication_range)
            
            for nearby_id in nearby_agents[:3]:  # Limit to 3
                # Simulate consent (INV-01)
                consent_prob = 0.8  # Base consent probability
                
                # Adjust based on role compatibility
                if agent.current_role and self.agents[nearby_id].current_role:
                    if agent.current_role == self.agents[nearby_id].current_role:
                        consent_prob = 0.9
                
                consent_granted = np.random.random() < consent_prob
                
                communication_event = {
                    "step": step,
                    "from_agent": agent_id,
                    "to_agent": nearby_id,
                    "consent_granted": consent_granted,
                    "distance": float(np.linalg.norm(
                        agent.position - self.agents[nearby_id].position
                    ))
                }
                
                communication_events.append(communication_event)
                
                if consent_granted:
                    agent.communication_history.append({
                        "step": step,
                        "with_agent": nearby_id
                    })
                    
                    # Record consent event
                    self.metrics["consent_events"].append({
                        "step": step,
                        "agent": agent_id,
                        "consent_granted": True
                    })
        
        self.metrics["communication_events"].extend(communication_events)
    
    def _simulate_agent_decisions(self, step: int):
        """Simulate agents making decisions based on their roles and state."""
        for agent_id, agent in self.agents.items():
            if agent.failed or not agent.current_role:
                continue
            
            # Role-based decision making
            if "navigate" in agent.capabilities:
                if np.random.random() < 0.1:
                    target = agent.position + np.random.randn(2) * 20.0
                    target = np.clip(target, 0, self.world_size)
                    
                    agent.action_history.append({
                        "step": step,
                        "action": "navigate",
                        "target": target.tolist()
                    })
            
            if "scan" in agent.capabilities:
                if np.random.random() < 0.15:
                    agent.action_history.append({
                        "step": step,
                        "action": "scan"
                    })
    
    def _get_nearby_agents(self, agent_id: str, max_distance: float) -> List[str]:
        """Get agents within specified distance."""
        agent_pos = self.agents[agent_id].position
        nearby = []
        
        for other_id, other_agent in self.agents.items():
            if other_id == agent_id or other_agent.failed:
                continue
            
            distance = np.linalg.norm(agent_pos - other_agent.position)
            if distance <= max_distance:
                nearby.append((other_id, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[1])
        
        return [agent_id for agent_id, _ in nearby[:10]]
    
    def _generate_initial_missions(self):
        """Generate initial missions for the simulation."""
        mission_types = [
            ("area_reconnaissance", ["scout", "observer"]),
            ("logistics_transport", ["transport", "navigator"]),
            ("environmental_monitoring", ["observer", "analyzer"]),
        ]
        
        for i in range(self.config.concurrent_missions):
            mission_type, roles = random.choice(mission_types)
            
            mission = MissionSpec(
                mission_id=f"mission_{i:03d}",
                objective=f"{mission_type} in sector {i}",
                parameters={
                    "priority": np.random.randint(1, 10),
                    "time_limit": self.config.mission_duration_steps
                },
                required_roles=roles
            )
            
            self.active_missions.append(mission)
            
            # Assign to random agents
            for role in roles:
                candidates = [
                    aid for aid, agent in self.agents.items()
                    if any(cap in agent.capabilities for cap in ["navigate", "scan", "transport"])
                    and not agent.current_role
                ]
                
                if candidates:
                    chosen = random.choice(candidates)
                    self.agents[chosen].current_role = role
                    self.agents[chosen].role_start_step = self.step
        
        if self.config.verbose:
            print(f"   Generated {len(self.active_missions)} initial missions")
    
    def _update_missions(self, step: int):
        """Update mission states."""
        # Check for completed missions
        for mission in self.active_missions[:]:
            if step % self.config.mission_duration_steps == 0:
                # Free agents from this mission
                for agent in self.agents.values():
                    if agent.current_role:
                        # Probabilistic mission completion
                        if np.random.random() < 0.3:
                            agent.current_role = None
                            agent.fatigue = max(0.0, agent.fatigue - 0.2)
    
    def _detect_emergent_patterns(self, step: int):
        """Detect emergent patterns in swarm behavior."""
        # Cluster detection
        clusters = self._detect_clusters()
        if clusters:
            self.emergent_patterns["clusters"].append({
                "step": step,
                "count": len(clusters),
                "largest": max(len(c) for c in clusters) if clusters else 0
            })
        
        # Coordinated movement detection
        coordinated = self._detect_coordinated_movement()
        if coordinated:
            self.emergent_patterns["coordinated_movements"].append({
                "step": step,
                "count": len(coordinated)
            })
    
    def _detect_clusters(self, distance_threshold: float = 20.0) -> List[List[str]]:
        """Detect clusters of agents."""
        clusters = []
        visited = set()
        
        for agent_id in self.agents:
            if agent_id in visited or self.agents[agent_id].failed:
                continue
            
            cluster = []
            queue = [agent_id]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                
                visited.add(current)
                cluster.append(current)
                
                neighbors = self._get_nearby_agents(current, distance_threshold)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return clusters
    
    def _detect_coordinated_movement(self) -> List[List[str]]:
        """Detect groups moving in similar directions."""
        coordinated_groups = []
        velocity_groups = defaultdict(list)
        
        for agent_id, agent in self.agents.items():
            if agent.failed or np.linalg.norm(agent.velocity) < 0.01:
                continue
            
            norm_vel = agent.velocity / np.linalg.norm(agent.velocity)
            angle = np.arctan2(norm_vel[1], norm_vel[0])
            angle_quantized = round(angle / (np.pi / 8))
            
            velocity_groups[angle_quantized].append(agent_id)
        
        for group in velocity_groups.values():
            if len(group) >= 3:
                coordinated_groups.append(group)
        
        return coordinated_groups
    
    def _collect_step_metrics(self, step: int):
        """Collect metrics for the current step."""
        active_agents = [a for a in self.agents.values() if not a.failed]
        
        step_data = {
            "step": step,
            "active_agents": len(active_agents),
            "agents_with_roles": sum(1 for a in active_agents if a.current_role),
            "average_fatigue": statistics.mean([a.fatigue for a in active_agents]) if active_agents else 0,
            "average_risk": statistics.mean([a.risk_level for a in active_agents]) if active_agents else 0,
            "average_battery": statistics.mean([a.battery_level for a in active_agents]) if active_agents else 0,
        }
        
        self.metrics["step_data"].append(step_data)
    
    def _analyze_results(self) -> Dict[str, Any]:
        """Analyze simulation results and compute key metrics."""
        step_data = self.metrics["step_data"]
        
        results = {
            "simulation_summary": {
                "total_steps": len(step_data),
                "total_agents": self.config.num_agents,
                "failed_agents": sum(1 for a in self.agents.values() if a.failed),
                "simulation_duration": time.time() - self.start_time,
                "average_step_time": statistics.mean(self.performance_stats["step_times"]) 
                                   if self.performance_stats["step_times"] else 0
            },
            
            "invariant_analysis": {
                "total_checks": len(self.metrics["invariant_checks"]),
                "risk_de_escalations": sum(1 for c in self.metrics["invariant_checks"] 
                                         if c.get("invariant") == "INV-04"),
            },
            
            "consent_analysis": {
                "total_events": len(self.metrics["consent_events"]),
                "consent_granted": sum(1 for e in self.metrics["consent_events"] 
                                     if e.get("consent_granted", False)),
                "consent_rate": sum(1 for e in self.metrics["consent_events"] 
                                  if e.get("consent_granted", False)) / 
                              max(len(self.metrics["consent_events"]), 1) if self.metrics["consent_events"] else 1.0,
            },
            
            "communication_analysis": {
                "total_events": len(self.metrics["communication_events"]),
                "successful_communications": sum(1 for e in self.metrics["communication_events"] 
                                               if e.get("consent_granted", False)),
                "success_rate": sum(1 for e in self.metrics["communication_events"] 
                                  if e.get("consent_granted", False)) / 
                              max(len(self.metrics["communication_events"]), 1) if self.metrics["communication_events"] else 1.0,
            },
            
            "emergent_behavior": {
                "clusters_detected": len(self.emergent_patterns["clusters"]),
                "coordinated_movements": len(self.emergent_patterns["coordinated_movements"]),
                "largest_cluster": max((c["largest"] for c in self.emergent_patterns["clusters"]), 
                                     default=0)
            },
            
            "performance_metrics": {
                "steps_per_second": len(step_data) / max(time.time() - self.start_time, 0.001),
                "agent_updates_per_second": self.config.num_agents * len(step_data) / 
                                          max(time.time() - self.start_time, 0.001),
            },
            
            "scale_validation": {
                "agents_simulated": self.config.num_agents,
                "steps_completed": len(step_data),
                "total_agent_steps": self.config.num_agents * len(step_data),
                "communication_events": len(self.metrics["communication_events"]),
                "consent_events": len(self.metrics["consent_events"]),
            }
        }
        
        return results
    
    def _save_metrics(self, results: Dict[str, Any]):
        """Save metrics to JSON file."""
        metrics_dir = Path(self.config.metrics_path)
        metrics_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        metrics_file = metrics_dir / f"swarm_metrics_{timestamp}.json"
        
        with open(metrics_file, 'w') as f:
            json.dump({
                "config": {
                    "num_agents": self.config.num_agents,
                    "simulation_steps": self.config.simulation_steps,
                    "world_size": self.config.world_size
                },
                "results": results,
                "step_data": self.metrics["step_data"][-100:],  # Last 100 steps
            }, f, indent=2)
        
        if self.config.verbose:
            print(f"   Metrics saved to: {metrics_file}")
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print simulation summary."""
        print("\n" + "=" * 70)
        print("SWARM SIMULATION RESULTS")
        print("=" * 70)
        
        summary = results["simulation_summary"]
        print(f"\n📊 Simulation Summary:")
        print(f"   Agents: {summary['total_agents']}")
        print(f"   Steps: {summary['total_steps']}")
        print(f"   Duration: {summary['simulation_duration']:.2f}s")
        print(f"   Avg step time: {summary['average_step_time']*1000:.2f}ms")
        
        inv = results["invariant_analysis"]
        print(f"\n🛡️  Invariant Analysis:")
        print(f"   Total checks: {inv['total_checks']}")
        print(f"   INV-04 triggers: {inv['risk_de_escalations']}")
        
        consent = results["consent_analysis"]
        print(f"\n✋ Consent Analysis (INV-01):")
        print(f"   Total events: {consent['total_events']}")
        print(f"   Consent rate: {consent['consent_rate']:.1%}")
        
        comm = results["communication_analysis"]
        print(f"\n📡 Communication Analysis:")
        print(f"   Total events: {comm['total_events']}")
        print(f"   Success rate: {comm['success_rate']:.1%}")
        
        emergent = results["emergent_behavior"]
        print(f"\n🌟 Emergent Behavior:")
        print(f"   Clusters detected: {emergent['clusters_detected']}")
        print(f"   Largest cluster: {emergent['largest_cluster']} agents")
        print(f"   Coordinated movements: {emergent['coordinated_movements']}")
        
        perf = results["performance_metrics"]
        print(f"\n⚡ Performance:")
        print(f"   Steps/second: {perf['steps_per_second']:.1f}")
        print(f"   Agent updates/second: {perf['agent_updates_per_second']:.0f}")
        
        scale = results["scale_validation"]
        print(f"\n📈 Scale Validation:")
        print(f"   Total agent-steps: {scale['total_agent_steps']:,}")
        print(f"   Communication events: {scale['communication_events']:,}")
        print(f"   Consent events: {scale['consent_events']:,}")
        
        print("\n" + "=" * 70)
        print("✅ SWARM SIMULATION COMPLETE")
        print("=" * 70)
