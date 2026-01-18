"""
robot_agent.py
Complete robot agent integrating CGCS, hardware, and bridge.
Main class to instantiate for each physical robot.
"""
import threading
import time
from typing import Optional
from .cgcs_adapter import CGCSAgentAdapter
from .hardware_interface import SimulatedHardwareInterface, HardwareBridge
from .interfaces import ActionRequest, WorldCue

class CompleteRobotAgent:
    """
    Complete robot agent with:
    - CGCS brain (Layer 4)
    - Hardware bridge (Layer 0)
    - Autonomous behavior loop
    """
    
    def __init__(self, agent_id: str, capabilities: list, initial_position: list = [0, 0, 0]):
        self.agent_id = agent_id
        self.running = False
        self.control_thread = None
        
        print(f"🤖 Creating complete robot agent: {agent_id}")
        
        # Layer 0: Hardware
        self.hardware = SimulatedHardwareInterface(agent_id, initial_position)
        self.bridge = HardwareBridge(agent_id, self.hardware)
        
        # Layer 4: CGCS Brain
        self.brain = CGCSAgentAdapter(agent_id, capabilities)
        
        # Connect brain to bridge
        self._connect_brain_to_bridge()
        
        print(f"   ✅ {agent_id} initialized with capabilities: {capabilities}")
    
    def _connect_brain_to_bridge(self):
        """Override brain's action execution to use hardware bridge."""
        original_request_action = self.brain.request_action
        
        def hardware_aware_request_action(request: ActionRequest) -> bool:
            print(f"⚙️  [{self.agent_id}] Brain → Hardware request")
            
            cgcs_valid = original_request_action(request)
            if not cgcs_valid:
                return False
            
            return self.bridge.process_action_request(request)
        
        self.brain.request_action = hardware_aware_request_action
    
    def start_autonomous_loop(self, interval: float = 0.5):
        """Start robot's autonomous behavior loop."""
        if self.running:
            print("⚠️  Robot already running")
            return
        
        self.running = True
        self.control_thread = threading.Thread(
            target=self._autonomous_loop,
            args=(interval,),
            daemon=True
        )
        self.control_thread.start()
        print(f"🚀 [{self.agent_id}] Autonomous loop started")
    
    def _autonomous_loop(self, interval: float):
        """Main autonomous behavior loop."""
        while self.running:
            try:
                # Read sensors and inject cues
                cue = self.bridge.read_and_convert_sensors()
                if cue:
                    self.brain.inject_world_cue(self.agent_id, cue)
                
                # Check active role
                status = self.brain.get_status()
                if status.get("current_role"):
                    self._make_autonomous_decision(status["current_role"])
                
                # Update CGCS state
                self.brain.step(dt=interval)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"⚠️  [{self.agent_id}] Loop error: {e}")
                time.sleep(interval * 2)
    
    def _make_autonomous_decision(self, current_role: str):
        """Simple autonomous behavior based on role."""
        role_behaviors = {
            "scout": self._scout_behavior,
            "transport": self._transport_behavior,
            "observer": self._observer_behavior
        }
        
        behavior = role_behaviors.get(current_role)
        if behavior:
            behavior()
    
    def _scout_behavior(self):
        """Autonomous scout behavior: explore and scan."""
        import random
        
        if random.random() > 0.8:
            target = [
                self.hardware.position[0] + random.uniform(-5, 5),
                self.hardware.position[1] + random.uniform(-5, 5)
            ]
            
            request = ActionRequest(
                source_agent_id=self.agent_id,
                source_role="scout",
                action_type="scan",
                parameters={"target": target, "intensity": "medium"},
                priority=5
            )
            
            self.brain.request_action(request)
    
    def _transport_behavior(self):
        """Autonomous transport behavior: check battery."""
        status = self.hardware.get_status()
        
        if status.battery_level < 0.3:
            print(f"   🔋 [{self.agent_id}] Battery low ({status.battery_level:.2f})")
    
    def _observer_behavior(self):
        """Autonomous observer behavior: monitor."""
        pass
    
    def stop(self):
        """Stop autonomous loop."""
        self.running = False
        if self.control_thread:
            self.control_thread.join(timeout=2.0)
        print(f"🛑 [{self.agent_id}] Stopped")
    
    def get_full_status(self) -> dict:
        """Get complete status of all layers."""
        brain_status = self.brain.get_status()
        hardware_status = self.hardware.get_status()
        
        return {
            "agent_id": self.agent_id,
            "running": self.running,
            "brain": brain_status,
            "hardware": {
                "battery": hardware_status.battery_level,
                "position": hardware_status.position,
                "motors": hardware_status.motor_status
            }
        }
