"""
Linear C Validator Core

Deterministic safety validation using emoji-based patterns.
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .patterns import PatternLibrary


class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    BLOCK = "block"
    EMERGENCY = "emergency"


@dataclass
class ValidationResult:
    """Result of a Linear C validation check"""
    is_valid: bool
    level: ValidationLevel
    rule_id: str
    message: str
    details: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    linear_c: str = ""
    
    def __repr__(self) -> str:
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        return f"{status} [{self.level.value.upper()}] {self.rule_id}: {self.message}"


class LinearCValidator:
    """
    Linear C Safety Validator
    
    Validates robot actions using deterministic emoji pattern matching.
    No ML, no black boxes - just pure string validation.
    """
    
    def __init__(self, pattern_library: PatternLibrary = None):
        """
        Initialize validator with pattern library
        
        Args:
            pattern_library: Custom pattern library (uses default if None)
        """
        self.patterns = pattern_library or PatternLibrary()
        self.validation_history: List[ValidationResult] = []
        self._stats = {
            'total_validations': 0,
            'blocked': 0,
            'warnings': 0,
            'passed': 0
        }
    
    def validate(self, 
                linear_c: str, 
                context: Optional[str] = None,
                action_name: Optional[str] = None) -> ValidationResult:
        """
        Validate a Linear C annotation
        
        Args:
            linear_c: Linear C emoji string to validate
            context: Optional context (e.g., 'human_interaction', 'movement')
            action_name: Optional name of action being validated
        
        Returns:
            ValidationResult with validation outcome
        """
        self._stats['total_validations'] += 1
        
        # Check for prohibited patterns first (highest priority)
        prohibited = self.patterns.check_prohibited(linear_c)
        if prohibited:
            result = self._create_blocked_result(
                linear_c=linear_c,
                violations=prohibited,
                action_name=action_name
            )
            self._stats['blocked'] += 1
            self.validation_history.append(result)
            return result
        
        # Check for required patterns if context provided
        if context:
            missing_required = self.patterns.check_required(linear_c, context)
            if missing_required:
                result = self._create_warning_result(
                    linear_c=linear_c,
                    context=context,
                    missing=missing_required,
                    action_name=action_name
                )
                self._stats['warnings'] += 1
                self.validation_history.append(result)
                return result
        
        # All checks passed
        result = ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            rule_id="OK",
            message=f"Linear C validation passed{f' for {action_name}' if action_name else ''}",
            details={
                'linear_c': linear_c,
                'context': context,
                'action': action_name
            },
            linear_c=linear_c
        )
        self._stats['passed'] += 1
        self.validation_history.append(result)
        return result
    
    def validate_action(self,
                       action: str,
                       context: Dict,
                       linear_c_annotation: str) -> ValidationResult:
        """
        Validate an action with full context
        
        Args:
            action: Name of the action to validate
            context: Full context dictionary
            linear_c_annotation: Linear C annotation for the action
        
        Returns:
            ValidationResult
        """
        # Extract context type if available
        context_type = context.get('interaction_type') or context.get('context_type')
        
        return self.validate(
            linear_c=linear_c_annotation,
            context=context_type,
            action_name=action
        )
    
    def _create_blocked_result(self,
                              linear_c: str,
                              violations: List[Dict],
                              action_name: Optional[str] = None) -> ValidationResult:
        """Create a BLOCKED validation result"""
        violation_ids = [v['id'] for v in violations]
        violation_msgs = [v['description'] for v in violations]
        
        return ValidationResult(
            is_valid=False,
            level=ValidationLevel.BLOCK,
            rule_id=", ".join(violation_ids),
            message=f"Prohibited pattern detected{f' in {action_name}' if action_name else ''}: {', '.join(violation_msgs)}",
            details={
                'linear_c': linear_c,
                'violations': violations,
                'action': action_name
            },
            linear_c=linear_c
        )
    
    def _create_warning_result(self,
                              linear_c: str,
                              context: str,
                              missing: List[Dict],
                              action_name: Optional[str] = None) -> ValidationResult:
        """Create a WARNING validation result"""
        missing_ids = [m['id'] for m in missing]
        missing_msgs = [m['description'] for m in missing]
        
        return ValidationResult(
            is_valid=False,
            level=ValidationLevel.WARNING,
            rule_id=", ".join(missing_ids),
            message=f"Required patterns missing for {context}{f' in {action_name}' if action_name else ''}: {', '.join(missing_msgs)}",
            details={
                'linear_c': linear_c,
                'context': context,
                'missing_patterns': missing,
                'action': action_name
            },
            linear_c=linear_c
        )
    
    def get_state_annotation(self, robot_state: str) -> str:
        """
        Get Linear C annotation for a robot state
        
        Args:
            robot_state: Robot state name (e.g., 'idle', 'moving')
        
        Returns:
            Linear C emoji string
        """
        return self.patterns.get_state_annotation(robot_state)
    
    def get_stats(self) -> Dict:
        """Get validation statistics"""
        total = self._stats['total_validations']
        if total == 0:
            return {**self._stats, 'success_rate': 100.0}
        
        return {
            **self._stats,
            'success_rate': (self._stats['passed'] / total) * 100.0
        }
    
    def get_recent_validations(self, count: int = 10) -> List[ValidationResult]:
        """Get recent validation results"""
        return self.validation_history[-count:]
    
    def clear_history(self):
        """Clear validation history"""
        self.validation_history.clear()
