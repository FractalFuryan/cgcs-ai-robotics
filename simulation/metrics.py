"""
metrics.py
Metrics collection and visualization for CGCS swarm simulation.
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np


class SwarmMetricsVisualizer:
    """Visualize swarm simulation metrics."""
    
    def __init__(self, metrics_data: Dict[str, Any]):
        self.metrics = metrics_data
        self.fig_dir = Path("simulation/plots")
        self.fig_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_plots(self):
        """Generate all visualization plots."""
        print("📊 Generating visualization plots...")
        
        self.plot_agent_activity()
        self.plot_fatigue_risk()
        self.plot_communication()
        self.plot_consent_rates()
        
        print(f"   Plots saved to: {self.fig_dir}")
    
    def plot_agent_activity(self):
        """Plot agent activity over time."""
        step_data = self.metrics.get("step_data", [])
        if not step_data:
            return
        
        steps = [d["step"] for d in step_data]
        active_agents = [d["active_agents"] for d in step_data]
        agents_with_roles = [d["agents_with_roles"] for d in step_data]
        
        plt.figure(figsize=(10, 6))
        plt.plot(steps, active_agents, label="Active Agents", linewidth=2)
        plt.plot(steps, agents_with_roles, label="Agents with Roles", linewidth=2)
        plt.xlabel("Simulation Step")
        plt.ylabel("Number of Agents")
        plt.title("Agent Activity Over Time")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.fig_dir / "agent_activity.png", dpi=150)
        plt.close()
    
    def plot_fatigue_risk(self):
        """Plot fatigue and risk levels."""
        step_data = self.metrics.get("step_data", [])
        if not step_data:
            return
        
        steps = [d["step"] for d in step_data]
        fatigue = [d["average_fatigue"] for d in step_data]
        risk = [d["average_risk"] for d in step_data]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        ax1.plot(steps, fatigue, color='orange', linewidth=2)
        ax1.set_ylabel("Average Fatigue")
        ax1.set_title("INV-03: Fatigue Bounds [0,1]")
        ax1.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label="Upper Bound")
        ax1.axhline(y=0.0, color='r', linestyle='--', alpha=0.5, label="Lower Bound")
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        ax2.plot(steps, risk, color='red', linewidth=2)
        ax2.set_xlabel("Simulation Step")
        ax2.set_ylabel("Average Risk Level")
        ax2.set_title("INV-04: Risk De-escalation (>0.8 triggers)")
        ax2.axhline(y=0.8, color='darkred', linestyle='--', alpha=0.7, label="De-escalation Threshold")
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(self.fig_dir / "fatigue_risk.png", dpi=150)
        plt.close()
    
    def plot_communication(self):
        """Plot communication patterns."""
        comm_events = self.metrics.get("communication_events", [])
        if not comm_events:
            return
        
        # Group by step
        from collections import defaultdict
        events_by_step = defaultdict(int)
        successful_by_step = defaultdict(int)
        
        for event in comm_events:
            step = event["step"]
            events_by_step[step] += 1
            if event.get("consent_granted", False):
                successful_by_step[step] += 1
        
        steps = sorted(events_by_step.keys())
        total_events = [events_by_step[s] for s in steps]
        successful_events = [successful_by_step[s] for s in steps]
        
        plt.figure(figsize=(10, 6))
        plt.plot(steps, total_events, label="Total Communication Attempts", linewidth=2, alpha=0.7)
        plt.plot(steps, successful_events, label="Successful (Consent Granted)", linewidth=2)
        plt.xlabel("Simulation Step")
        plt.ylabel("Communication Events")
        plt.title("Communication Patterns (INV-01: Consent-Based)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.fig_dir / "communication.png", dpi=150)
        plt.close()
    
    def plot_consent_rates(self):
        """Plot consent acceptance rates."""
        consent_events = self.metrics.get("consent_events", [])
        if not consent_events:
            return
        
        # Calculate rolling consent rate
        window_size = 50
        consent_granted = [1 if e.get("consent_granted", False) else 0 for e in consent_events]
        
        rolling_rate = []
        for i in range(len(consent_granted)):
            start = max(0, i - window_size)
            window = consent_granted[start:i+1]
            rolling_rate.append(sum(window) / len(window) if window else 0)
        
        plt.figure(figsize=(10, 6))
        plt.plot(rolling_rate, linewidth=2, color='green')
        plt.xlabel("Consent Event Index")
        plt.ylabel("Consent Rate (Rolling Average)")
        plt.title(f"INV-01: Consent Acceptance Rate (Window={window_size})")
        plt.ylim(0, 1.05)
        plt.axhline(y=0.8, color='blue', linestyle='--', alpha=0.5, label="Target Rate")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.fig_dir / "consent_rates.png", dpi=150)
        plt.close()


def load_and_visualize_metrics(metrics_file: Path):
    """Load metrics from file and generate visualizations."""
    with open(metrics_file, 'r') as f:
        data = json.load(f)
    
    visualizer = SwarmMetricsVisualizer(data)
    visualizer.generate_all_plots()
    
    return data
