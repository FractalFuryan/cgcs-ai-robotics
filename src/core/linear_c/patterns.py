"""
Linear C Pattern Library

Defines prohibited and required patterns for safety validation.
Based on SPEC_LINEAR_C_v1.0.1.md
"""
import re
from typing import Dict, List


class PatternLibrary:
    """Library of Linear C safety patterns"""
    
    def __init__(self):
        self._prohibited_patterns = self._init_prohibited()
        self._required_patterns = self._init_required()
        self._state_patterns = self._init_states()
    
    def _init_prohibited(self) -> List[Dict[str, str]]:
        """Initialize prohibited patterns that must never occur"""
        return [
            {
                'id': 'P1-FORCE',
                'pattern': r'🛡️.*🔴.*✖️',
                'description': 'Shield + Red + Cross = Force prohibition',
                'severity': 'BLOCK'
            },
            {
                'id': 'P2-UNSTABLE-FORCE',
                'pattern': r'🔴.*🧠.*⚠️.*✖️',
                'description': 'Unstable cognition with force',
                'severity': 'BLOCK'
            },
            {
                'id': 'P3-COLLECTIVE-FORCE',
                'pattern': r'🛡️.*🔴.*👥.*✖️.*🧍',
                'description': 'Collective forcing individual',
                'severity': 'BLOCK'
            },
            {
                'id': 'P4-UNSTABLE-HUMAN',
                'pattern': r'🔴.*🧠.*⚠️.*🧍',
                'description': 'Unstable cognition with human interaction',
                'severity': 'BLOCK'
            },
            {
                'id': 'P5-RED-MOVEMENT',
                'pattern': r'🔴.*🧠.*🚶',
                'description': 'Critical state with movement',
                'severity': 'WARNING'
            },
            {
                'id': 'P6-FORCED-MOVEMENT',
                'pattern': r'🛡️.*🔴.*✖️.*🚶',
                'description': 'Forced movement during critical state',
                'severity': 'BLOCK'
            }
        ]
    
    def _init_required(self) -> Dict[str, List[Dict[str, str]]]:
        """Initialize required patterns for specific contexts"""
        return {
            'human_interaction': [
                {
                    'id': 'R1-SAFE-HUMAN',
                    'pattern': r'(🟢|🟡).*🧍',
                    'description': 'Green/Yellow required for human interaction'
                },
                {
                    'id': 'R2-ATTENTION',
                    'pattern': r'✖️',
                    'description': 'Attention cross required for interaction'
                }
            ],
            'autonomous_movement': [
                {
                    'id': 'R3-STABLE-COG',
                    'pattern': r'(🔵|🟢).*🧠',
                    'description': 'Stable cognition required for movement'
                }
            ],
            'environment_interaction': [
                {
                    'id': 'R4-ENVIRONMENT',
                    'pattern': r'🌍',
                    'description': 'Environment marker required'
                }
            ],
            'collective_action': [
                {
                    'id': 'R5-COLLECTIVE',
                    'pattern': r'👥',
                    'description': 'Collective marker required'
                }
            ]
        }
    
    def _init_states(self) -> Dict[str, str]:
        """Map robot states to Linear C emoji patterns"""
        return {
            'idle': '🔵🧠',
            'processing': '🟡🧠',
            'moving': '🟢🧠🚶',
            'error': '🔴🧠⚠️',
            'emergency_stop': '🛡️🔴⛔',
            'human_interaction': '🟡🧠✖️🧍',
            'autonomous': '🔵🧠🧭',
            'low_battery': '🟡🧠🔋⚠️',
            'safe_movement': '🟢🧠🚶',
            'environment_interaction': '🟢🧠✖️🌍',
            'collective_mode': '🔵🧠👥',
            'attention_mode': '🟡✖️'
        }
    
    @property
    def prohibited_patterns(self) -> List[Dict[str, str]]:
        """Get all prohibited patterns"""
        return self._prohibited_patterns
    
    @property
    def required_patterns(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all required patterns by context"""
        return self._required_patterns
    
    @property
    def state_patterns(self) -> Dict[str, str]:
        """Get state to Linear C mappings"""
        return self._state_patterns
    
    def get_state_annotation(self, state: str) -> str:
        """Get Linear C annotation for a robot state"""
        return self._state_patterns.get(state, '⚪❓')
    
    def check_prohibited(self, linear_c: str) -> List[Dict[str, str]]:
        """Check if string contains any prohibited patterns"""
        violations = []
        for pattern_def in self._prohibited_patterns:
            if re.search(pattern_def['pattern'], linear_c):
                violations.append(pattern_def)
        return violations
    
    def check_required(self, linear_c: str, context: str) -> List[Dict[str, str]]:
        """Check if string has all required patterns for context"""
        missing = []
        if context in self._required_patterns:
            for pattern_def in self._required_patterns[context]:
                if not re.search(pattern_def['pattern'], linear_c):
                    missing.append(pattern_def)
        return missing
