"""
Safety Decorators for Linear C Validation

Decorators to add automatic Linear C validation to any function.
"""
from functools import wraps
from typing import Optional, Callable, Any
import inspect

from ..linear_c.validator import LinearCValidator, ValidationLevel


class SafetyViolationError(Exception):
    """Raised when a Linear C safety violation is detected"""
    pass


def linear_c_protected(required_annotation: Optional[str] = None,
                      context: Optional[str] = None,
                      allow_warnings: bool = False):
    """
    Decorator that validates Linear C before executing function
    
    Args:
        required_annotation: Required Linear C annotation (if None, reads from kwargs)
        context: Context type for validation (e.g., 'human_interaction')
        allow_warnings: If True, allows execution with warnings (default: False)
    
    Example:
        @linear_c_protected(required_annotation="🟢🧠🚶", context="movement")
        def move_forward(distance: float):
            # Your movement code
            pass
    
    Raises:
        SafetyViolationError: If validation fails
    """
    def decorator(func: Callable) -> Callable:
        validator = LinearCValidator()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Get Linear C from annotation or kwargs
            linear_c = required_annotation or kwargs.get('linear_c', '🔵🧠')
            
            # Remove linear_c from kwargs if present (don't pass to original function)
            kwargs_copy = {k: v for k, v in kwargs.items() if k != 'linear_c'}
            
            # Validate
            result = validator.validate(
                linear_c=linear_c,
                context=context,
                action_name=func.__name__
            )
            
            # Check result
            if not result.is_valid:
                if result.level == ValidationLevel.BLOCK:
                    raise SafetyViolationError(
                        f"Action '{func.__name__}' blocked by Linear C: {result.message}"
                    )
                elif result.level == ValidationLevel.WARNING and not allow_warnings:
                    raise SafetyViolationError(
                        f"Action '{func.__name__}' has safety warnings: {result.message}"
                    )
            
            # Log the validated action
            print(f"[LINEAR-C] ✅ {func.__name__}: {linear_c}")
            
            # Execute original function
            return func(*args, **kwargs_copy)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Get Linear C from annotation or kwargs
            linear_c = required_annotation or kwargs.get('linear_c', '🔵🧠')
            
            # Remove linear_c from kwargs if present
            kwargs_copy = {k: v for k, v in kwargs.items() if k != 'linear_c'}
            
            # Validate
            result = validator.validate(
                linear_c=linear_c,
                context=context,
                action_name=func.__name__
            )
            
            # Check result
            if not result.is_valid:
                if result.level == ValidationLevel.BLOCK:
                    raise SafetyViolationError(
                        f"Action '{func.__name__}' blocked by Linear C: {result.message}"
                    )
                elif result.level == ValidationLevel.WARNING and not allow_warnings:
                    raise SafetyViolationError(
                        f"Action '{func.__name__}' has safety warnings: {result.message}"
                    )
            
            # Log the validated action
            print(f"[LINEAR-C] ✅ {func.__name__}: {linear_c}")
            
            # Execute original async function
            return await func(*args, **kwargs_copy)
        
        # Return appropriate wrapper based on whether function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def with_state_annotation(state_name: str):
    """
    Decorator that automatically adds Linear C state annotation
    
    Args:
        state_name: Robot state name (e.g., 'moving', 'idle')
    
    Example:
        @with_state_annotation('moving')
        def start_navigation():
            # Automatically annotated with moving state Linear C
            pass
    """
    def decorator(func: Callable) -> Callable:
        validator = LinearCValidator()
        linear_c = validator.get_state_annotation(state_name)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add linear_c to kwargs
            kwargs['linear_c'] = linear_c
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
