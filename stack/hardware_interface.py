"""
hardware_interface.py
Layer 0: Hardware Abstraction Layer (HAL)
Translates between CGCS actions and real robot hardware.
"""
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .interfaces import ActionRequest, WorldCue

@dataclass
class HardwareStatus:
    """Current status of robot hardware."""
    battery_level: float  # 0.0 to 1.0
    motor_status: Dict[str, Any]  # Left/right motor status
    sensor_status: Dict[str, bool]  # Which sensors are active
    position: Optional[list] = None  # [x, y, z] if available
    orientation: Optional[list] = None  # [roll, pitch, yaw]

class BaseHardwareInterface(ABC):
    """Abstract base class for all hardware interfaces."""
    
    @abstractmethod
    def execute_action(self, request: ActionRequest) -> bool:
        """Execute a CGCS action request on physical hardware."""
        pass
    
    @abstractmethod
    def read_sensors(self) -> Dict[str, Any]:
        """Read all sensors and return as dictionary."""
        pass
    
    @abstractmethod
    def get_status(self) -> HardwareStatus:
        """Get current hardware status."""
        pass

class SimulatedHardwareInterface(BaseHardwareInterface):
    """
    Simulated hardware for testing.
    Can be replaced with real interfaces for:
    - ROS 2 / motor controllers
    - Arduino / Raspberry Pi
    - Custom robotics platforms
    """
    
    def __init__(self, robot_id: str, initial_position: list = [0, 0, 0]):
        self.robot_id = robot_id
        self.position = initial_position
        self.battery = 1.0
        self.motors = {"left": "idle", "right": "idle"}
        self.sensors = {
            "lidar": True,
            "camera": True,
            "imu": True,
            "bumper": False
        }
    
    def execute_action(self, request: ActionRequest) -> bool:
        """Execute simulated actions."""
        print(f"🛠️  [{self.robot_id}] HAL executing: {request.action_type}")
        
        action_handlers = {
            "navigate": self._execute_navigation,
            "scan": self._execute_scan,
            "carry": self._execute_carry,
            "inspect": self._execute_inspect,
            "report": self._execute_report
        }
        
        handler = action_handlers.get(request.action_type)
        if handler:
            return handler(request.parameters)
        
        print(f"⚠️  Unknown action type: {request.action_type}")
        return False
    
    def _execute_navigation(self, params: Dict[str, Any]) -> bool:
        """Simulate movement to target location."""
        target = params.get("target", [0, 0])
        speed = params.get("speed", 1.0)
        
        print(f"   → Moving to {target} at speed {speed}")
        self.position = [target[0], target[1], self.position[2]]
        self.motors = {"left": f"moving_{speed}", "right": f"moving_{speed}"}
        self.battery -= 0.01
        time.sleep(0.1)
        return True
    
    def _execute_scan(self, params: Dict[str, Any]) -> bool:
        """Simulate scanning action."""
        target = params.get("target", [0, 0])
        intensity = params.get("intensity", "medium")
        
        print(f"   → Scanning {target} at {intensity} intensity")
        time.sleep(0.1)
        
        import random
        if random.random() > 0.5:
            print("   → Object detected!")
        
        return True
    
    def _execute_carry(self, params: Dict[str, Any]) -> bool:
        """Simulate carrying a load."""
        load_weight = params.get("weight", 1.0)
        print(f"   → Carrying {load_weight}kg load")
        self.battery -= 0.02 * load_weight
        return True
    
    def _execute_inspect(self, params: Dict[str, Any]) -> bool:
        """Simulate inspection action."""
        target = params.get("object", "unknown")
        print(f"   → Inspecting {target}")
        time.sleep(0.1)
        return True
    
    def _execute_report(self, params: Dict[str, Any]) -> bool:
        """Simulate reporting action."""
        print(f"   → Reporting status")
        return True
    
    def read_sensors(self) -> Dict[str, Any]:
        """Simulate sensor readings."""
        import random
        
        return {
            "lidar_distance": random.uniform(0.1, 5.0),
            "camera_detection": ["wall", "floor"] if random.random() > 0.7 else [],
            "imu_acceleration": [
                random.uniform(-0.1, 0.1),
                random.uniform(-0.1, 0.1),
                random.uniform(9.7, 9.9)
            ],
            "bumper_pressed": False,
            "temperature": random.uniform(20.0, 40.0)
        }
    
    def get_status(self) -> HardwareStatus:
        """Return current hardware status."""
        return HardwareStatus(
            battery_level=self.battery,
            motor_status=self.motors,
            sensor_status=self.sensors,
            position=self.position,
            orientation=[0, 0, 0]
        )

class HardwareBridge:
    """
    Bridges CGCSAdapter with HardwareInterface.
    Converts sensor data to WorldCue and routes actions to hardware.
    """
    
    def __init__(self, agent_id: str, hardware: BaseHardwareInterface):
        self.agent_id = agent_id
        self.hardware = hardware
        self.last_sensor_read = time.time()
        self.sensor_interval = 1.0
    
    def process_action_request(self, request: ActionRequest) -> bool:
        """Route CGCS action request to hardware."""
        print(f"🌉 [{self.agent_id}] Bridge routing action: {request.action_type}")
        
        hw_status = self.hardware.get_status()
        
        if hw_status.battery_level < 0.1:
            print("   ⚠️  Battery too low for action")
            return False
        
        return self.hardware.execute_action(request)
    
    def read_and_convert_sensors(self) -> Optional[WorldCue]:
        """Read sensors and convert to WorldCue if something interesting detected."""
        current_time = time.time()
        if current_time - self.last_sensor_read < self.sensor_interval:
            return None
        
        self.last_sensor_read = current_time
        sensor_data = self.hardware.read_sensors()
        
        cues = []
        
        if sensor_data.get("lidar_distance", 5.0) < 0.5:
            cues.append(WorldCue(
                cue_id=f"obstacle_{int(time.time())}",
                tag="obstacle_near",
                data={
                    "distance": sensor_data["lidar_distance"],
                    "position": self.hardware.get_status().position
                }
            ))
        
        if sensor_data.get("temperature", 25.0) > 35.0:
            cues.append(WorldCue(
                cue_id=f"temp_{int(time.time())}",
                tag="high_temperature",
                data={"temperature": sensor_data["temperature"]}
            ))
        
        return cues[0] if cues else None
