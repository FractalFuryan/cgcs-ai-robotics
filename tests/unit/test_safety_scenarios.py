"""
Safety Scenario Tests

Tests real-world robot safety scenarios with Linear C validation.
"""
import pytest
from src.core.linear_c.validator import LinearCValidator, ValidationLevel


class TestSafetyScenarios:
    """Test realistic robot safety scenarios"""
    
    @pytest.fixture
    def validator(self):
        return LinearCValidator()
    
    def test_emergency_stop_scenario(self, validator):
        """Test emergency stop states"""
        # Emergency stop is a valid state
        result = validator.validate("🛡️🔴⛔")
        assert result.is_valid
        
        # But forced movement during emergency should be blocked
        result = validator.validate("🛡️🔴✖️🚶")
        assert not result.is_valid
        assert result.level == ValidationLevel.BLOCK
    
    def test_human_interaction_scenarios(self, validator):
        """Test various human-robot interaction scenarios"""
        scenarios = [
            ("🟢🧠✖️🧍", True, "Consensual interaction - green cognition"),
            ("🛡️🔴✖️🧍", False, "Forced interaction - prohibited"),
            ("🟡🧠✖️👥", True, "Attention with group interaction"),
            ("🔴🧠⚠️✖️🧍", False, "Unstable cognition with human - prohibited"),
            ("🟡🧠✖️🧍", True, "Yellow (attention) with human - safe"),
        ]
        
        for linear_c, should_pass, description in scenarios:
            result = validator.validate(linear_c)
            assert result.is_valid == should_pass, \
                f"Failed: {description} - Expected {'PASS' if should_pass else 'FAIL'}, got {'PASS' if result.is_valid else 'FAIL'}"
    
    def test_autonomous_navigation_scenarios(self, validator):
        """Test autonomous navigation scenarios"""
        # Safe navigation - green cognition with movement
        result = validator.validate("🟢🧠🚶")
        assert result.is_valid
        
        # Navigation while cognitively unstable - should fail
        result = validator.validate("🔴🧠⚠️🚶")
        assert not result.is_valid
        
        # Navigation with attention to humans - safe
        result = validator.validate("🟡🧠🚶✖️🧍")
        assert result.is_valid
        
        # Blue (idle) cognition with movement - safe
        result = validator.validate("🔵🧠🚶")
        assert result.is_valid
    
    def test_low_battery_scenarios(self, validator):
        """Test low battery safety scenarios"""
        # Low battery with warning state
        result = validator.validate("🟡🧠🔋⚠️")
        assert result.is_valid  # Warning state is valid
        
        # Critical battery with red state
        result = validator.validate("🔴🧠🔋⚠️")
        assert result.is_valid  # Can be in critical battery state
        
        # But can't force actions in critical battery
        result = validator.validate("🛡️🔴🔋✖️")
        assert not result.is_valid
    
    def test_environment_interaction_scenarios(self, validator):
        """Test robot-environment interactions"""
        # Safe environment interaction
        result = validator.validate("🟢🧠✖️🌍")
        assert result.is_valid
        
        # Autonomous with environment
        result = validator.validate("🔵🧠🧭✖️🌍")
        assert result.is_valid
    
    def test_collective_behavior_scenarios(self, validator):
        """Test multi-robot collective scenarios"""
        # Collective mode - valid
        result = validator.validate("🔵🧠👥")
        assert result.is_valid
        
        # Collective forcing individual - invalid
        result = validator.validate("🛡️🔴👥✖️🧍")
        assert not result.is_valid
    
    def test_state_transition_scenarios(self, validator):
        """Test state transitions"""
        transitions = [
            ("🔵🧠", "idle to processing", True),
            ("🔵🧠→🟡🧠", "idle to processing transition", True),
            ("🟡🧠→🟢🧠🚶", "processing to moving", True),
            ("🟢🧠🚶→🔴🧠⚠️", "moving to error", True),
            ("🔴🧠⚠️→🛡️🔴⛔", "error to emergency stop", True),
        ]
        
        for linear_c, description, should_pass in transitions:
            result = validator.validate(linear_c)
            assert result.is_valid == should_pass, f"Failed: {description}"
    
    def test_restricted_zone_scenarios(self, validator):
        """Test restricted zone handling"""
        # Shield indicates restricted zone
        result = validator.validate("🛡️🟡🧠🚶")
        assert result.is_valid  # Can move in restricted zone with caution
        
        # But not with force
        result = validator.validate("🛡️🔴✖️🚶")
        assert not result.is_valid


class TestContextValidation:
    """Test context-specific validation"""
    
    @pytest.fixture
    def validator(self):
        return LinearCValidator()
    
    def test_human_interaction_context(self, validator):
        """Test human interaction context requires specific patterns"""
        # Missing required human interaction markers
        result = validator.validate("🔵🧠", context="human_interaction")
        assert not result.is_valid
        assert result.level == ValidationLevel.WARNING
        
        # Has required markers
        result = validator.validate("🟢🧠✖️🧍", context="human_interaction")
        assert result.is_valid
    
    def test_autonomous_movement_context(self, validator):
        """Test autonomous movement context"""
        # Needs stable cognition
        result = validator.validate("🔵🧠🚶", context="autonomous_movement")
        assert result.is_valid
        
        # Unstable cognition fails
        result = validator.validate("🔴🧠⚠️", context="autonomous_movement")
        # Should be blocked by prohibited pattern, not just context
        assert not result.is_valid
    
    def test_environment_interaction_context(self, validator):
        """Test environment interaction context"""
        result = validator.validate("🟢🧠✖️🌍", context="environment_interaction")
        assert result.is_valid
        
        # Missing environment marker
        result = validator.validate("🟢🧠", context="environment_interaction")
        assert not result.is_valid


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.fixture
    def validator(self):
        return LinearCValidator()
    
    def test_empty_linear_c(self, validator):
        """Test validation with empty string"""
        result = validator.validate("")
        # Empty string doesn't match prohibited patterns, so it's valid
        assert result.is_valid
    
    def test_unknown_emojis(self, validator):
        """Test with unknown/undefined emojis"""
        result = validator.validate("🎈🎉🎊")
        # Unknown emojis don't match prohibited patterns
        assert result.is_valid
    
    def test_multiple_states(self, validator):
        """Test with multiple state indicators"""
        # Multiple colors might indicate transition
        result = validator.validate("🔵🧠→🟢🧠")
        assert result.is_valid
    
    def test_complex_annotation(self, validator):
        """Test complex multi-component annotation"""
        # Shield + Yellow + Brain + Cross + Human + Environment
        result = validator.validate("🛡️🟡🧠✖️🧍🌍")
        assert result.is_valid  # Complex but safe


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
