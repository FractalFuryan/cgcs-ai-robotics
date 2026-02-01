"""
Tests for hardware safety controller
"""
import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.hardware.safety_controller import (
    HardwareSafetyController,
    HardwareConfig,
    HardwareMode,
    SafetyState
)


class TestHardwareConfig:
    """Test hardware configuration"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = HardwareConfig()
        
        assert config.mode == HardwareMode.SIMULATION
        assert config.emergency_stop_pin == 17
        assert config.warning_led_pin == 27
        assert config.fault_led_pin == 22
        assert config.enable_pin == 23
        assert config.watchdog_timeout == 1.0
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = HardwareConfig(
            mode=HardwareMode.GPIO_RPI,
            emergency_stop_pin=24,
            watchdog_timeout=2.0
        )
        
        assert config.mode == HardwareMode.GPIO_RPI
        assert config.emergency_stop_pin == 24
        assert config.watchdog_timeout == 2.0


class TestSimulationMode:
    """Test hardware controller in simulation mode"""
    
    @pytest.fixture
    def controller(self):
        """Create controller in simulation mode"""
        config = HardwareConfig(mode=HardwareMode.SIMULATION)
        controller = HardwareSafetyController(config)
        yield controller
        controller.shutdown()
    
    def test_initialization(self, controller):
        """Test controller initializes in simulation mode"""
        assert controller.config.mode == HardwareMode.SIMULATION
        assert controller.state == SafetyState.ENABLED
        assert controller._watchdog_active is True
    
    def test_trigger_emergency_stop(self, controller):
        """Test emergency stop in simulation mode"""
        controller.trigger_emergency_stop("Test emergency")
        
        assert controller.state == SafetyState.EMERGENCY
    
    def test_trigger_warning(self, controller):
        """Test warning trigger in simulation mode"""
        controller.trigger_warning("Test warning")
        
        assert controller.state == SafetyState.WARNING
    
    def test_reset_from_warning(self, controller):
        """Test reset from warning state"""
        controller.trigger_warning("Test warning")
        assert controller.state == SafetyState.WARNING
        
        result = controller.reset()
        
        assert result is True
        assert controller.state == SafetyState.ENABLED
    
    def test_cannot_reset_from_emergency(self, controller):
        """Test cannot reset from emergency (requires manual intervention)"""
        controller.trigger_emergency_stop("Test emergency")
        assert controller.state == SafetyState.EMERGENCY
        
        result = controller.reset()
        
        assert result is False
        assert controller.state == SafetyState.EMERGENCY
    
    def test_heartbeat(self, controller):
        """Test heartbeat updates"""
        time_before = controller._last_heartbeat
        time.sleep(0.1)
        
        controller.heartbeat()
        
        time_after = controller._last_heartbeat
        assert time_after > time_before
    
    def test_get_status(self, controller):
        """Test status reporting"""
        status = controller.get_status()
        
        assert status['state'] == SafetyState.ENABLED.value
        assert status['mode'] == HardwareMode.SIMULATION.value
        assert status['watchdog_active'] is True
        assert 'last_heartbeat' in status
        assert 'time_since_heartbeat' in status
    
    def test_callbacks(self, controller):
        """Test state transition callbacks"""
        emergency_callback = Mock()
        warning_callback = Mock()
        
        controller.register_callback(SafetyState.EMERGENCY, emergency_callback)
        controller.register_callback(SafetyState.WARNING, warning_callback)
        
        # Trigger warning
        controller.trigger_warning("Test warning")
        warning_callback.assert_called_once_with("Test warning")
        
        # Trigger emergency
        controller.trigger_emergency_stop("Test emergency")
        emergency_callback.assert_called_once_with("Test emergency")
    
    @pytest.mark.slow
    def test_watchdog_timeout(self):
        """Test watchdog triggers emergency stop on timeout"""
        config = HardwareConfig(
            mode=HardwareMode.SIMULATION,
            watchdog_timeout=0.5  # Short timeout for testing
        )
        controller = HardwareSafetyController(config)
        
        # Don't send heartbeat, wait for watchdog
        time.sleep(0.7)
        
        # Watchdog should have triggered emergency stop
        assert controller.state == SafetyState.EMERGENCY
        
        controller.shutdown()
    
    @pytest.mark.slow
    def test_watchdog_with_heartbeat(self):
        """Test watchdog stays active with regular heartbeats"""
        config = HardwareConfig(
            mode=HardwareMode.SIMULATION,
            watchdog_timeout=0.5
        )
        controller = HardwareSafetyController(config)
        
        # Send heartbeats regularly
        for _ in range(5):
            time.sleep(0.2)
            controller.heartbeat()
        
        # Should still be enabled
        assert controller.state == SafetyState.ENABLED
        assert controller._watchdog_active is True
        
        controller.shutdown()


@pytest.mark.skip(reason="GPIO tests require RPi.GPIO module")
@patch('src.hardware.safety_controller.HAS_RPI_GPIO', True)
@patch('RPi.GPIO')
class TestGPIOMode:
    """Test hardware controller with GPIO (mocked)"""
    
    def test_gpio_setup(self, mock_gpio):
        """Test GPIO pin setup"""
        config = HardwareConfig(mode=HardwareMode.GPIO_RPI)
        controller = HardwareSafetyController(config)
        
        # Verify GPIO setup calls
        mock_gpio.setmode.assert_called_once_with(mock_gpio.BCM)
        mock_gpio.setwarnings.assert_called_once_with(False)
        
        # Verify pin setup
        assert mock_gpio.setup.call_count == 4  # 4 output pins
        
        # Verify initial states
        assert mock_gpio.output.call_count >= 4
        
        controller.shutdown()
    
    def test_emergency_stop_gpio(self, mock_gpio):
        """Test emergency stop activates GPIO pins"""
        config = HardwareConfig(mode=HardwareMode.GPIO_RPI)
        controller = HardwareSafetyController(config)
        
        # Reset mock call count
        mock_gpio.output.reset_mock()
        
        controller.trigger_emergency_stop("Test")
        
        # Should have set emergency stop pin HIGH and enable pin LOW
        calls = mock_gpio.output.call_args_list
        
        # Verify emergency stop activated
        emergency_call = any(
            call[0][0] == config.emergency_stop_pin and call[0][1] == mock_gpio.HIGH
            for call in calls
        )
        assert emergency_call
        
        controller.shutdown()
    
    def test_warning_gpio(self, mock_gpio):
        """Test warning activates warning LED"""
        config = HardwareConfig(mode=HardwareMode.GPIO_RPI)
        controller = HardwareSafetyController(config)
        
        mock_gpio.output.reset_mock()
        
        controller.trigger_warning("Test")
        
        # Should have set warning LED HIGH
        calls = mock_gpio.output.call_args_list
        warning_call = any(
            call[0][0] == config.warning_led_pin and call[0][1] == mock_gpio.HIGH
            for call in calls
        )
        assert warning_call
        
        controller.shutdown()
    
    def test_reset_gpio(self, mock_gpio):
        """Test reset clears GPIO pins"""
        config = HardwareConfig(mode=HardwareMode.GPIO_RPI)
        controller = HardwareSafetyController(config)
        
        # Trigger warning then reset
        controller.trigger_warning("Test")
        mock_gpio.output.reset_mock()
        
        controller.reset()
        
        # Should have cleared all pins
        calls = mock_gpio.output.call_args_list
        assert len(calls) >= 4
        
        controller.shutdown()
    
    def test_shutdown_cleanup(self, mock_gpio):
        """Test shutdown cleans up GPIO"""
        config = HardwareConfig(mode=HardwareMode.GPIO_RPI)
        controller = HardwareSafetyController(config)
        
        controller.shutdown()
        
        # Should call GPIO.cleanup()
        mock_gpio.cleanup.assert_called_once()


class TestHardwareModes:
    """Test different hardware modes"""
    
    def test_simulation_fallback(self):
        """Test fallback to simulation if GPIO unavailable"""
        # GPIO not available, should fall back to simulation
        config = HardwareConfig(mode=HardwareMode.GPIO_RPI)
        controller = HardwareSafetyController(config)
        
        # Should have fallen back to simulation
        assert controller.config.mode == HardwareMode.SIMULATION
        
        controller.shutdown()


class TestSafetyStates:
    """Test safety state transitions"""
    
    @pytest.fixture
    def controller(self):
        """Create controller"""
        config = HardwareConfig(mode=HardwareMode.SIMULATION)
        controller = HardwareSafetyController(config)
        yield controller
        controller.shutdown()
    
    def test_state_transition_enabled_to_warning(self, controller):
        """Test ENABLED -> WARNING transition"""
        assert controller.state == SafetyState.ENABLED
        
        controller.trigger_warning("Test")
        assert controller.state == SafetyState.WARNING
    
    def test_state_transition_enabled_to_emergency(self, controller):
        """Test ENABLED -> EMERGENCY transition"""
        assert controller.state == SafetyState.ENABLED
        
        controller.trigger_emergency_stop("Test")
        assert controller.state == SafetyState.EMERGENCY
    
    def test_state_transition_warning_to_emergency(self, controller):
        """Test WARNING -> EMERGENCY transition"""
        controller.trigger_warning("Test")
        assert controller.state == SafetyState.WARNING
        
        controller.trigger_emergency_stop("Test")
        assert controller.state == SafetyState.EMERGENCY
    
    def test_state_transition_warning_to_enabled(self, controller):
        """Test WARNING -> ENABLED transition (reset)"""
        controller.trigger_warning("Test")
        assert controller.state == SafetyState.WARNING
        
        controller.reset()
        assert controller.state == SafetyState.ENABLED
