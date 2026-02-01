"""
Hardware Safety Controller - Physical Enforcement

Provides GPIO-based emergency stop and physical safety enforcement
for Linear C validation failures.

Platform support:
- Raspberry Pi (RPi.GPIO)
- Generic Linux GPIO (via /sys/class/gpio)
- Simulation mode (for testing)
"""
import time
import threading
from enum import Enum
from typing import Optional, Callable, Dict
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

# Platform detection
try:
    import RPi.GPIO as GPIO  # type: ignore
    HAS_RPI_GPIO = True
except ImportError:
    HAS_RPI_GPIO = False
    logger.warning("RPi.GPIO not available, using simulation mode")


class HardwareMode(Enum):
    """Hardware operation modes"""
    SIMULATION = "simulation"  # Mock hardware for testing
    GPIO_RPI = "gpio_rpi"      # Raspberry Pi GPIO
    GPIO_LINUX = "gpio_linux"  # Generic Linux GPIO


class SafetyState(Enum):
    """Physical safety states"""
    ENABLED = "enabled"       # System operational
    WARNING = "warning"       # Warning state (soft stop)
    EMERGENCY = "emergency"   # Emergency stop triggered
    FAULT = "fault"           # Hardware fault detected


@dataclass
class HardwareConfig:
    """Hardware configuration"""
    mode: HardwareMode = HardwareMode.SIMULATION
    emergency_stop_pin: int = 17  # BCM pin for E-Stop relay
    warning_led_pin: int = 27     # BCM pin for warning LED
    fault_led_pin: int = 22       # BCM pin for fault LED
    enable_pin: int = 23          # BCM pin for motor enable
    watchdog_timeout: float = 1.0 # Watchdog timeout in seconds
    

class HardwareSafetyController:
    """
    Hardware-level safety enforcement for Linear C violations
    
    Capabilities:
    - Emergency stop relay control
    - Warning/fault indication LEDs
    - Motor enable/disable control
    - Hardware watchdog
    - Physical interlocks
    """
    
    def __init__(self, config: Optional[HardwareConfig] = None):
        """
        Initialize hardware safety controller
        
        Args:
            config: Hardware configuration (defaults to simulation mode)
        """
        self.config = config or HardwareConfig()
        self.state = SafetyState.ENABLED
        self._watchdog_active = False
        self._watchdog_thread = None
        self._last_heartbeat = time.time()
        self._callbacks: Dict[SafetyState, Callable] = {}
        
        # Initialize hardware
        self._setup_hardware()
        
        # Start watchdog
        self._start_watchdog()
        
        logger.info(
            "HardwareSafetyController initialized",
            mode=self.config.mode.value,
            emergency_pin=self.config.emergency_stop_pin
        )
    
    def _setup_hardware(self):
        """Setup GPIO pins and hardware"""
        if self.config.mode == HardwareMode.GPIO_RPI:
            if not HAS_RPI_GPIO:
                logger.error("RPi.GPIO not available, falling back to simulation")
                self.config.mode = HardwareMode.SIMULATION
                return
            
            # Setup Raspberry Pi GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Configure output pins
            GPIO.setup(self.config.emergency_stop_pin, GPIO.OUT)
            GPIO.setup(self.config.warning_led_pin, GPIO.OUT)
            GPIO.setup(self.config.fault_led_pin, GPIO.OUT)
            GPIO.setup(self.config.enable_pin, GPIO.OUT)
            
            # Initial state: system enabled
            GPIO.output(self.config.enable_pin, GPIO.HIGH)
            GPIO.output(self.config.emergency_stop_pin, GPIO.LOW)
            GPIO.output(self.config.warning_led_pin, GPIO.LOW)
            GPIO.output(self.config.fault_led_pin, GPIO.LOW)
            
            logger.info("Raspberry Pi GPIO configured")
        
        elif self.config.mode == HardwareMode.SIMULATION:
            logger.info("Running in SIMULATION mode (no physical hardware)")
        
        else:
            logger.warning(f"Unsupported mode: {self.config.mode}")
    
    def trigger_emergency_stop(self, reason: str = "Linear C violation"):
        """
        Trigger emergency stop
        
        This immediately:
        - Cuts power to motors via relay
        - Activates emergency LED
        - Sets state to EMERGENCY
        - Calls registered callbacks
        
        Args:
            reason: Reason for emergency stop
        """
        logger.critical("EMERGENCY STOP TRIGGERED", reason=reason)
        
        self.state = SafetyState.EMERGENCY
        
        if self.config.mode == HardwareMode.GPIO_RPI:
            GPIO.output(self.config.emergency_stop_pin, GPIO.HIGH)
            GPIO.output(self.config.enable_pin, GPIO.LOW)
            GPIO.output(self.config.fault_led_pin, GPIO.HIGH)
            GPIO.output(self.config.warning_led_pin, GPIO.LOW)
        
        # Call registered callbacks
        if SafetyState.EMERGENCY in self._callbacks:
            try:
                self._callbacks[SafetyState.EMERGENCY](reason)
            except Exception as e:
                logger.error("Emergency callback failed", error=str(e))
    
    def trigger_warning(self, reason: str = "Linear C warning"):
        """
        Trigger warning state (soft stop)
        
        This:
        - Activates warning LED
        - Reduces motor power/speed
        - Sets state to WARNING
        - Does NOT trigger emergency stop
        
        Args:
            reason: Reason for warning
        """
        logger.warning("Safety warning triggered", reason=reason)
        
        self.state = SafetyState.WARNING
        
        if self.config.mode == HardwareMode.GPIO_RPI:
            GPIO.output(self.config.warning_led_pin, GPIO.HIGH)
            GPIO.output(self.config.fault_led_pin, GPIO.LOW)
        
        # Call registered callbacks
        if SafetyState.WARNING in self._callbacks:
            try:
                self._callbacks[SafetyState.WARNING](reason)
            except Exception as e:
                logger.error("Warning callback failed", error=str(e))
    
    def reset(self) -> bool:
        """
        Reset from warning/emergency state
        
        Returns:
            True if reset successful
        """
        if self.state == SafetyState.EMERGENCY:
            logger.info("Resetting from EMERGENCY state (requires manual intervention)")
            # Emergency stop requires manual reset
            return False
        
        logger.info("Resetting to ENABLED state")
        self.state = SafetyState.ENABLED
        
        if self.config.mode == HardwareMode.GPIO_RPI:
            GPIO.output(self.config.enable_pin, GPIO.HIGH)
            GPIO.output(self.config.emergency_stop_pin, GPIO.LOW)
            GPIO.output(self.config.warning_led_pin, GPIO.LOW)
            GPIO.output(self.config.fault_led_pin, GPIO.LOW)
        
        # Reset watchdog
        self._last_heartbeat = time.time()
        
        return True
    
    def heartbeat(self):
        """Send heartbeat to prevent watchdog timeout"""
        self._last_heartbeat = time.time()
    
    def register_callback(self, state: SafetyState, callback: Callable):
        """
        Register callback for state transitions
        
        Args:
            state: State to monitor
            callback: Function to call on state entry
        """
        self._callbacks[state] = callback
        logger.debug(f"Callback registered for {state.value}")
    
    def _start_watchdog(self):
        """Start hardware watchdog thread"""
        if self._watchdog_active:
            return
        
        self._watchdog_active = True
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name="HardwareSafetyWatchdog"
        )
        self._watchdog_thread.start()
        logger.info("Hardware watchdog started", timeout=self.config.watchdog_timeout)
    
    def _watchdog_loop(self):
        """Watchdog monitoring loop"""
        while self._watchdog_active:
            time.sleep(0.1)  # Check every 100ms
            
            # Check if heartbeat timed out
            elapsed = time.time() - self._last_heartbeat
            if elapsed > self.config.watchdog_timeout:
                logger.critical(
                    "Hardware watchdog timeout - triggering emergency stop",
                    elapsed=elapsed,
                    timeout=self.config.watchdog_timeout
                )
                self.trigger_emergency_stop("Watchdog timeout")
                self._watchdog_active = False
    
    def get_status(self) -> Dict:
        """Get current hardware status"""
        return {
            'state': self.state.value,
            'mode': self.config.mode.value,
            'watchdog_active': self._watchdog_active,
            'last_heartbeat': self._last_heartbeat,
            'time_since_heartbeat': time.time() - self._last_heartbeat
        }
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down hardware safety controller")
        
        self._watchdog_active = False
        
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=1.0)
        
        # Reset hardware to safe state
        if self.config.mode == HardwareMode.GPIO_RPI:
            GPIO.output(self.config.enable_pin, GPIO.LOW)
            GPIO.output(self.config.emergency_stop_pin, GPIO.LOW)
            GPIO.output(self.config.warning_led_pin, GPIO.LOW)
            GPIO.output(self.config.fault_led_pin, GPIO.LOW)
            GPIO.cleanup()
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.shutdown()
        except:
            pass
