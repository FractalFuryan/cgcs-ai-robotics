"""
Unit Tests for Safety Decorators

Tests the @linear_c_protected decorator and safety wrappers.
"""
import pytest
from src.core.safety.decorators import linear_c_protected, SafetyViolationError


class TestLinearCDecorator:
    """Test the linear_c_protected decorator"""
    
    def test_decorator_allows_safe_action(self):
        """Test that decorator allows safe actions"""
        
        @linear_c_protected(required_annotation="🟢🧠🚶")
        def move_forward(distance):
            return f"Moved {distance}m"
        
        result = move_forward(5.0)
        assert result == "Moved 5.0m"
    
    def test_decorator_blocks_unsafe_action(self):
        """Test that decorator blocks unsafe actions"""
        
        @linear_c_protected(required_annotation="🛡️🔴✖️")  # Prohibited pattern
        def force_action():
            return "Should not execute"
        
        with pytest.raises(SafetyViolationError) as exc_info:
            force_action()
        
        assert "blocked" in str(exc_info.value).lower()
    
    def test_decorator_with_context(self):
        """Test decorator with context validation"""
        
        @linear_c_protected(context="human_interaction")
        def handshake(human_id, linear_c="🟢🧠✖️🧍"):
            return f"Handshake with {human_id}"
        
        # Should pass with proper Linear C
        result = handshake("human_001", linear_c="🟢🧠✖️🧍")
        assert "Handshake" in result
    
    def test_decorator_with_missing_required(self):
        """Test decorator blocks when required patterns missing"""
        
        @linear_c_protected(context="human_interaction")
        def interact(linear_c="🔵🧠"):  # Missing human interaction markers
            return "Interacting"
        
        with pytest.raises(SafetyViolationError):
            interact()
    
    def test_decorator_with_warnings_allowed(self):
        """Test decorator can allow warnings"""
        
        @linear_c_protected(context="human_interaction", allow_warnings=True)
        def cautious_action(linear_c="🔵🧠"):
            return "Executed with warning"
        
        # Should execute even with warning
        result = cautious_action()
        assert result == "Executed with warning"
    
    def test_decorator_with_dynamic_linear_c(self):
        """Test decorator with Linear C passed at runtime"""
        
        @linear_c_protected()
        def flexible_action(action_type, linear_c="🔵🧠"):
            return f"Action: {action_type}"
        
        # Safe action
        result = flexible_action("navigate", linear_c="🟢🧠🚶")
        assert "navigate" in result
        
        # Unsafe action should be blocked
        with pytest.raises(SafetyViolationError):
            flexible_action("force", linear_c="🛡️🔴✖️")
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata"""
        
        @linear_c_protected(required_annotation="🟢🧠")
        def documented_function():
            """This function has documentation"""
            return "result"
        
        assert documented_function.__name__ == "documented_function"
        assert "documentation" in documented_function.__doc__


class TestAsyncDecorator:
    """Test decorator with async functions"""
    
    @pytest.mark.asyncio
    async def test_async_decorator_allows_safe(self):
        """Test decorator works with async functions"""
        
        @linear_c_protected(required_annotation="🟢🧠🚶")
        async def async_move(distance):
            return f"Async moved {distance}m"
        
        result = await async_move(10.0)
        assert "Async moved 10.0m" == result
    
    @pytest.mark.asyncio
    async def test_async_decorator_blocks_unsafe(self):
        """Test async decorator blocks unsafe actions"""
        
        @linear_c_protected(required_annotation="🛡️🔴✖️")
        async def async_force():
            return "Should not execute"
        
        with pytest.raises(SafetyViolationError):
            await async_force()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
