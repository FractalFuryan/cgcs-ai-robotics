"""
Linear C Dashboard for Monitoring and Telemetry

Provides real-time safety monitoring and audit trails.
"""
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..core.linear_c.validator import LinearCValidator, ValidationResult


class LinearCDashboard:
    """
    Dashboard for monitoring Linear C safety status
    """
    
    def __init__(self, validator: LinearCValidator = None):
        """
        Initialize dashboard
        
        Args:
            validator: LinearCValidator instance (creates default if None)
        """
        self.validator = validator or LinearCValidator()
        self.state_history: List[Dict] = []
        self.violations: List[Dict] = []
        self.max_history = 1000
    
    def log_state(self, 
                  robot_state: str, 
                  linear_c: str, 
                  context: Optional[Dict] = None):
        """
        Log robot state with Linear C annotation
        
        Args:
            robot_state: Robot state name (e.g., 'moving', 'idle')
            linear_c: Linear C annotation
            context: Additional context dictionary
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'state': robot_state,
            'linear_c': linear_c,
            'context': context or {}
        }
        
        # Validate the state
        validation = self.validator.validate(linear_c, action_name=f"state:{robot_state}")
        entry['validation'] = {
            'is_valid': validation.is_valid,
            'level': validation.level.value,
            'message': validation.message
        }
        
        self.state_history.append(entry)
        
        # Keep only recent history
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
        
        # Log violation if invalid
        if not validation.is_valid:
            self.log_violation(
                action=f"state:{robot_state}",
                linear_c=linear_c,
                reason=validation.message
            )
    
    def log_violation(self, action: str, linear_c: str, reason: str):
        """
        Log a safety violation
        
        Args:
            action: Action that was blocked
            linear_c: Linear C annotation
            reason: Reason for violation
        """
        self.violations.append({
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'linear_c': linear_c,
            'reason': reason
        })
    
    def get_current_state(self) -> Optional[Dict]:
        """Get most recent state entry"""
        return self.state_history[-1] if self.state_history else None
    
    def get_violations_today(self) -> List[Dict]:
        """Get violations from today"""
        today = datetime.utcnow().date()
        return [
            v for v in self.violations
            if datetime.fromisoformat(v['timestamp']).date() == today
        ]
    
    def get_violations_in_window(self, hours: int = 1) -> List[Dict]:
        """Get violations within time window"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            v for v in self.violations
            if datetime.fromisoformat(v['timestamp']) > cutoff
        ]
    
    def calculate_safety_score(self) -> float:
        """
        Calculate safety score (0-100)
        
        Score based on:
        - Validation pass rate
        - Recent violations
        - State consistency
        """
        if not self.state_history:
            return 100.0
        
        # Get validator stats
        stats = self.validator.get_stats()
        base_score = stats.get('success_rate', 100.0)
        
        # Penalty for recent violations
        recent_violations = self.get_violations_in_window(hours=1)
        violation_penalty = min(len(recent_violations) * 5, 30)  # Max 30% penalty
        
        return max(0.0, base_score - violation_penalty)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive safety report"""
        current = self.get_current_state()
        violations_today = self.get_violations_today()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'current_state': current,
            'total_states_logged': len(self.state_history),
            'violations': {
                'total': len(self.violations),
                'today': len(violations_today),
                'last_hour': len(self.get_violations_in_window(hours=1)),
                'recent': self.violations[-5:] if self.violations else []
            },
            'safety_score': self.calculate_safety_score(),
            'validator_stats': self.validator.get_stats()
        }
    
    def save_to_file(self, filepath: str = "linear_c_log.json"):
        """
        Save dashboard data to JSON file
        
        Args:
            filepath: Path to save file
        """
        data = {
            'generated_at': datetime.utcnow().isoformat(),
            'state_history': self.state_history,
            'violations': self.violations,
            'report': self.generate_report()
        }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[DASHBOARD] Saved to {filepath}")
    
    def load_from_file(self, filepath: str):
        """
        Load dashboard data from JSON file
        
        Args:
            filepath: Path to load from
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.state_history = data.get('state_history', [])
        self.violations = data.get('violations', [])
        
        print(f"[DASHBOARD] Loaded from {filepath}")
    
    def print_status(self):
        """Print current status to console"""
        report = self.generate_report()
        
        print("\n" + "="*50)
        print("LINEAR C SAFETY DASHBOARD")
        print("="*50)
        
        if report['current_state']:
            state = report['current_state']
            print(f"\n📊 Current State:")
            print(f"   State: {state['state']}")
            print(f"   Linear C: {state['linear_c']}")
            print(f"   Valid: {'✅ Yes' if state['validation']['is_valid'] else '❌ No'}")
        
        print(f"\n🔒 Safety Metrics:")
        print(f"   Safety Score: {report['safety_score']:.1f}%")
        print(f"   States Logged: {report['total_states_logged']}")
        
        print(f"\n⚠️  Violations:")
        print(f"   Total: {report['violations']['total']}")
        print(f"   Today: {report['violations']['today']}")
        print(f"   Last Hour: {report['violations']['last_hour']}")
        
        if report['violations']['recent']:
            print(f"\n   Recent Violations:")
            for v in report['violations']['recent']:
                print(f"   - {v['action']}: {v['reason']}")
        
        print("\n" + "="*50 + "\n")
