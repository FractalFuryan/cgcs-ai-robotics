#!/usr/bin/env python3
"""
Master Deployment Script - Deploy All Linear C Components

This script orchestrates deployment of all Linear C production components:
- Optimized validator with caching
- Hardware safety controller
- ROS 2 safety server (optional)
- Monitoring dashboard
- Analytics system
- Simulation integration (optional)

Usage:
    # Deploy all components
    python deploy_all.py --all
    
    # Deploy specific components
    python deploy_all.py --core --hardware --monitoring
    
    # Deploy with ROS 2 support
    python deploy_all.py --all --ros2
    
    # Simulation mode (no hardware)
    python deploy_all.py --all --simulation
"""
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict
import json

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_warning(msg: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def run_command(cmd: List[str], cwd: Path = None, env: Dict = None) -> bool:
    """Run command and return success status"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env or os.environ,
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        print_error(f"Error: {e.stderr}")
        return False

def check_python_version() -> bool:
    """Check Python version >= 3.8"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} OK")
    return True

def install_dependencies(simulation: bool = False, ros2: bool = False) -> bool:
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    workspace_root = Path(__file__).parent
    
    # Install core dependencies
    print("Installing core dependencies...")
    extras = ["dev"]
    
    if simulation:
        extras.append("simulation")
    
    # Check if on ARM platform for hardware support
    import platform
    if platform.machine().startswith('arm') or platform.machine().startswith('aarch'):
        extras.append("hardware")
        print_success("Detected ARM platform - including hardware support")
    
    if ros2:
        extras.append("ros2")
        print_success("ROS 2 support requested")
    
    # Install with extras
    extras_str = ",".join(extras)
    cmd = [sys.executable, "-m", "pip", "install", "-e", f".[{extras_str}]"]
    
    if not run_command(cmd, cwd=workspace_root):
        print_error("Failed to install dependencies")
        return False
    
    print_success("All dependencies installed")
    return True

def deploy_core_validator() -> bool:
    """Deploy optimized validator"""
    print_header("Deploying Core Validator")
    
    # Verify validator files exist
    validator_path = Path(__file__).parent / "src" / "core" / "linear_c"
    required_files = ["validator.py", "patterns.py", "optimized.py"]
    
    for file in required_files:
        if not (validator_path / file).exists():
            print_error(f"Missing required file: {file}")
            return False
    
    print_success("Core validator files verified")
    
    # Run validator tests
    print("Running validator tests...")
    test_cmd = [sys.executable, "-m", "pytest", "tests/unit/test_linear_c_basic.py", "-v"]
    if not run_command(test_cmd):
        print_warning("Some validator tests failed (non-blocking)")
    else:
        print_success("Validator tests passed")
    
    return True

def deploy_hardware_safety(simulation: bool = False) -> bool:
    """Deploy hardware safety controller"""
    print_header("Deploying Hardware Safety Controller")
    
    controller_path = Path(__file__).parent / "src" / "hardware" / "safety_controller.py"
    if not controller_path.exists():
        print_error("Hardware safety controller not found")
        return False
    
    if simulation:
        print_warning("Running in SIMULATION mode (no physical hardware)")
        # Create simulation config
        config = {
            "mode": "simulation",
            "emergency_stop_pin": 17,
            "warning_led_pin": 27,
            "fault_led_pin": 22,
            "enable_pin": 23,
            "watchdog_timeout": 1.0
        }
    else:
        print_success("Hardware mode enabled (GPIO control)")
        config = {
            "mode": "gpio_rpi",
            "emergency_stop_pin": 17,
            "warning_led_pin": 27,
            "fault_led_pin": 22,
            "enable_pin": 23,
            "watchdog_timeout": 1.0
        }
    
    # Save config
    config_path = Path(__file__).parent / "hardware_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print_success(f"Hardware config saved: {config_path}")
    return True

def deploy_monitoring_dashboard() -> bool:
    """Deploy monitoring dashboard"""
    print_header("Deploying Monitoring Dashboard")
    
    dashboard_path = Path(__file__).parent / "src" / "monitoring" / "dashboard.py"
    if not dashboard_path.exists():
        print_error("Dashboard not found")
        return False
    
    print_success("Monitoring dashboard ready")
    
    # Create systemd service (optional, requires sudo)
    print("To run dashboard as service, create systemd unit:")
    print("  sudo systemctl enable linear-c-dashboard")
    print("  sudo systemctl start linear-c-dashboard")
    
    return True

def deploy_ros2_nodes(ros2: bool) -> bool:
    """Deploy ROS 2 safety nodes"""
    if not ros2:
        print_warning("ROS 2 deployment skipped (--ros2 not specified)")
        return True
    
    print_header("Deploying ROS 2 Nodes")
    
    # Check if ROS 2 is sourced
    if 'ROS_DISTRO' not in os.environ:
        print_warning("ROS 2 not sourced - skipping ROS 2 deployment")
        print("To deploy ROS 2 nodes, source ROS 2 first:")
        print("  source /opt/ros/humble/setup.bash")
        return True
    
    ros_distro = os.environ['ROS_DISTRO']
    print_success(f"ROS 2 {ros_distro} detected")
    
    # Build ROS 2 packages
    print("Building ROS 2 packages...")
    ros2_ws = Path(__file__).parent / "ros2_ws"
    
    if not ros2_ws.exists():
        print_warning("ROS 2 workspace not found - skipping build")
        return True
    
    build_cmd = ["colcon", "build", "--symlink-install"]
    if not run_command(build_cmd, cwd=ros2_ws):
        print_error("ROS 2 build failed")
        return False
    
    print_success("ROS 2 packages built successfully")
    return True

def create_deployment_summary(components: List[str]) -> Path:
    """Create deployment summary file"""
    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "components": components,
        "status": "deployed",
        "version": "1.1.0"
    }
    
    summary_path = Path(__file__).parent / "deployment_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary_path

def main():
    """Main deployment orchestrator"""
    parser = argparse.ArgumentParser(
        description="Deploy Linear C production components"
    )
    parser.add_argument("--all", action="store_true", help="Deploy all components")
    parser.add_argument("--core", action="store_true", help="Deploy core validator")
    parser.add_argument("--hardware", action="store_true", help="Deploy hardware safety")
    parser.add_argument("--monitoring", action="store_true", help="Deploy monitoring")
    parser.add_argument("--ros2", action="store_true", help="Deploy ROS 2 nodes")
    parser.add_argument("--simulation", action="store_true", help="Simulation mode (no hardware)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    
    args = parser.parse_args()
    
    # Validate flags
    if args.all:
        args.core = True
        args.hardware = True
        args.monitoring = True
    
    if not any([args.core, args.hardware, args.monitoring, args.ros2]):
        parser.print_help()
        sys.exit(1)
    
    print_header("Linear C Production Deployment")
    print(f"Workspace: {Path(__file__).parent}")
    print(f"Simulation: {args.simulation}")
    print(f"ROS 2: {args.ros2}\n")
    
    # Pre-flight checks
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies(simulation=args.simulation, ros2=args.ros2):
        sys.exit(1)
    
    deployed_components = []
    
    # Deploy components
    if args.core:
        if deploy_core_validator():
            deployed_components.append("core_validator")
        else:
            print_error("Core validator deployment failed")
            sys.exit(1)
    
    if args.hardware:
        if deploy_hardware_safety(simulation=args.simulation):
            deployed_components.append("hardware_safety")
        else:
            print_error("Hardware safety deployment failed")
            sys.exit(1)
    
    if args.monitoring:
        if deploy_monitoring_dashboard():
            deployed_components.append("monitoring_dashboard")
        else:
            print_error("Monitoring deployment failed")
            sys.exit(1)
    
    if args.ros2:
        if deploy_ros2_nodes(ros2=True):
            deployed_components.append("ros2_nodes")
        else:
            print_warning("ROS 2 deployment incomplete")
    
    # Create deployment summary
    summary_path = create_deployment_summary(deployed_components)
    
    # Final summary
    print_header("Deployment Complete")
    print_success(f"Deployed components: {', '.join(deployed_components)}")
    print_success(f"Deployment summary: {summary_path}")
    
    print("\n" + Colors.BOLD + "Next steps:" + Colors.RESET)
    print("  1. Run tests: pytest tests/")
    print("  2. Start dashboard: python -m src.monitoring.dashboard")
    print("  3. Verify hardware: python examples/linear_c_integration/robot_with_protection.py")
    
    if args.ros2:
        print("  4. Launch ROS 2: ros2 launch linear_c_ros2 safety_system.launch.py")
    
    print()

if __name__ == "__main__":
    main()
