"""
Unit Tests for Linear C Validator

Tests basic pattern matching and validation logic.
"""
import pytest
from src.core.linear_c.validator import LinearCValidator, ValidationResult, ValidationLevel
from src.core.linear_c.patterns import PatternLibrary


class TestLinearCValidator:
    """Test the Linear C validator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return LinearCValidator()
    
    @pytest.fixture
    def patterns(self):
        """Create pattern library instance"""
        return PatternLibrary()
    
    def test_validator_creation(self, validator):
        """Test validator can be created"""
        assert validator is not None
        assert isinstance(validator, LinearCValidator)
    
    def test_prohibited_pattern_force(self, validator):
        """Test that force prohibition pattern is blocked"""
        # Shield + Red + Cross = Force (prohibited)
        result = validator.validate("🛡️🔴✖️🧍")
        
        assert not result.is_valid
        assert result.level == ValidationLevel.BLOCK
        assert "prohibited" in result.message.lower() or "force" in result.message.lower()
    
    def test_prohibited_pattern_unstable_force(self, validator):
        """Test that unstable cognition with force is blocked"""
        result = validator.validate("🔴🧠⚠️✖️")
        
        assert not result.is_valid
        assert result.level == ValidationLevel.BLOCK
    
    def test_prohibited_pattern_collective_force(self, validator):
        """Test that collective forcing individual is blocked"""
        result = validator.validate("🛡️🔴👥✖️🧍")
        
        assert not result.is_valid
        assert result.level == ValidationLevel.BLOCK
    
    def test_safe_pattern_allowed(self, validator):
        """Test that safe patterns are allowed"""
        # Green cognition with human interaction (safe)
        result = validator.validate("🟢🧠✖️🧍")
        
        assert result.is_valid
        assert result.level == ValidationLevel.INFO
    
    def test_safe_autonomous_movement(self, validator):
        """Test that safe autonomous movement is allowed"""
        # Blue cognition with movement
        result = validator.validate("🔵🧠🚶")
        
        assert result.is_valid
    
    def test_required_patterns_human_interaction(self, validator):
        """Test that human interaction requires specific patterns"""
        # Blue cognition alone is not enough for human_interaction context
        result = validator.validate("🔵🧠", context="human_interaction")
        
        assert not result.is_valid
        assert result.level == ValidationLevel.WARNING
        assert "required" in result.message.lower()
    
    def test_required_patterns_satisfied(self, validator):
        """Test that satisfying required patterns passes"""
        # Green with human for human_interaction context
        result = validator.validate("🟢🧠✖️🧍", context="human_interaction")
        
        assert result.is_valid
    
    def test_state_annotation_mapping(self, validator):
        """Test that state names map to Linear C correctly"""
        idle_lc = validator.get_state_annotation("idle")
        assert "🔵" in idle_lc  # Blue for idle
        assert "🧠" in idle_lc  # Brain emoji
        
        moving_lc = validator.get_state_annotation("moving")
        assert "🟢" in moving_lc  # Green for moving
        assert "🚶" in moving_lc  # Walking emoji
        
        error_lc = validator.get_state_annotation("error")
        assert "🔴" in error_lc  # Red for error
        assert "⚠️" in error_lc   # Warning
    
    def test_validation_history(self, validator):
        """Test that validation history is recorded"""
        validator.validate("🟢🧠✖️🧍")
        validator.validate("🛡️🔴✖️")
        
        history = validator.get_recent_validations(count=2)
        assert len(history) == 2
    
    def test_statistics(self, validator):
        """Test that statistics are calculated correctly"""
        # Run some validations
        validator.validate("🟢🧠✖️🧍")  # Pass
        validator.validate("🛡️🔴✖️")    # Block
        validator.validate("🔵🧠")       # Pass
        
        stats = validator.get_stats()
        assert stats['total_validations'] == 3
        assert stats['passed'] == 2
        assert stats['blocked'] == 1
        assert 'success_rate' in stats


class TestPatternLibrary:
    """Test the pattern library"""
    
    @pytest.fixture
    def patterns(self):
        return PatternLibrary()
    
    def test_prohibited_patterns_exist(self, patterns):
        """Test that prohibited patterns are defined"""
        prohibited = patterns.prohibited_patterns
        assert len(prohibited) > 0
        assert all('pattern' in p for p in prohibited)
    
    def test_required_patterns_exist(self, patterns):
        """Test that required patterns are defined"""
        required = patterns.required_patterns
        assert 'human_interaction' in required
        assert 'autonomous_movement' in required
    
    def test_state_mappings_exist(self, patterns):
        """Test that state mappings are defined"""
        states = patterns.state_patterns
        assert 'idle' in states
        assert 'moving' in states
        assert 'error' in states
    
    def test_check_prohibited(self, patterns):
        """Test prohibited pattern checking"""
        violations = patterns.check_prohibited("🛡️🔴✖️")
        assert len(violations) > 0
        
        no_violations = patterns.check_prohibited("🟢🧠✖️🧍")
        assert len(no_violations) == 0
    
    def test_check_required(self, patterns):
        """Test required pattern checking"""
        missing = patterns.check_required("🔵🧠", "human_interaction")
        assert len(missing) > 0
        
        satisfied = patterns.check_required("🟢🧠✖️🧍", "human_interaction")
        assert len(satisfied) == 0


class TestValidationResult:
    """Test validation result data structure"""
    
    def test_validation_result_creation(self):
        """Test creating a validation result"""
        result = ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            rule_id="OK",
            message="Test passed"
        )
        
        assert result.is_valid
        assert result.level == ValidationLevel.INFO
        assert result.timestamp  # Has timestamp
        assert isinstance(result.timestamp, str)  # Is string
    
    def test_validation_result_repr(self):
        """Test string representation"""
        result = ValidationResult(
            is_valid=False,
            level=ValidationLevel.BLOCK,
            rule_id="P1",
            message="Test blocked"
        )
        
        repr_str = repr(result)
        assert "INVALID" in repr_str or "BLOCK" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
