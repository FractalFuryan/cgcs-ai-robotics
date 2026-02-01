"""
Linear C Safety Middleware

Middleware for action pipeline with Linear C validation.
"""
from typing import Dict, Any, Callable, List
from datetime import datetime
import asyncio

from ..linear_c.validator import LinearCValidator, ValidationResult, ValidationLevel


class LinearCSafetyMiddleware:
    """
    Safety middleware that validates all actions through Linear C
    """
    
    def __init__(self, validator: LinearCValidator = None):
        """
        Initialize middleware
        
        Args:
            validator: LinearCValidator instance (creates default if None)
        """
        self.validator = validator or LinearCValidator()
        self.blocked_actions: List[Dict] = []
        self.executed_actions: List[Dict] = []
    
    async def process_action(self,
                            action_callable: Callable,
                            action_context: Dict,
                            linear_c: str,
                            action_name: str = None) -> Dict[str, Any]:
        """
        Process action through safety layer
        
        Args:
            action_callable: Function to execute if validation passes
            action_context: Context for the action
            linear_c: Linear C annotation
            action_name: Optional action name (uses callable name if None)
        
        Returns:
            Dict with status and result/reason
        """
        if action_name is None:
            action_name = action_callable.__name__
        
        # Validate
        validation = self.validator.validate_action(
            action=action_name,
            context=action_context,
            linear_c_annotation=linear_c
        )
        
        # Handle based on validation level
        if validation.level == ValidationLevel.BLOCK:
            # Block the action
            self.blocked_actions.append({
                'action': action_name,
                'linear_c': linear_c,
                'reason': validation.message,
                'timestamp': datetime.utcnow().isoformat(),
                'context': action_context
            })
            
            print(f"[SAFETY] 🛑 Blocked: {action_name} - {validation.message}")
            
            return {
                'status': 'blocked',
                'reason': validation.message,
                'validation': validation,
                'linear_c': linear_c
            }
        
        elif validation.level == ValidationLevel.WARNING:
            # Log warning but potentially allow execution
            print(f"[SAFETY] ⚠️  Warning: {action_name} - {validation.message}")
        
        # Execute the action (valid or warning)
        try:
            if asyncio.iscoroutinefunction(action_callable):
                result = await action_callable(**action_context)
            else:
                result = action_callable(**action_context)
            
            # Log successful execution
            self.executed_actions.append({
                'action': action_name,
                'linear_c': linear_c,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'success',
                'validation_level': validation.level.value
            })
            
            print(f"[SAFETY] ✅ Executed: {action_name} with {linear_c}")
            
            return {
                'status': 'executed',
                'result': result,
                'validation': validation,
                'linear_c': linear_c
            }
        
        except Exception as e:
            # Log execution failure
            print(f"[SAFETY] ❌ Failed: {action_name} - {str(e)}")
            
            return {
                'status': 'failed',
                'reason': str(e),
                'validation': validation,
                'linear_c': linear_c
            }
    
    def get_blocked_actions(self, recent: int = None) -> List[Dict]:
        """Get list of blocked actions"""
        if recent:
            return self.blocked_actions[-recent:]
        return self.blocked_actions
    
    def get_executed_actions(self, recent: int = None) -> List[Dict]:
        """Get list of executed actions"""
        if recent:
            return self.executed_actions[-recent:]
        return self.executed_actions
    
    def get_safety_summary(self) -> Dict:
        """Get summary of safety middleware activity"""
        total = len(self.blocked_actions) + len(self.executed_actions)
        
        return {
            'total_actions': total,
            'blocked': len(self.blocked_actions),
            'executed': len(self.executed_actions),
            'block_rate': (len(self.blocked_actions) / total * 100) if total > 0 else 0.0,
            'validator_stats': self.validator.get_stats()
        }
