#!/bin/bash
#
# Run All Linear C Production Components
#
# Usage:
#   ./run_all.sh                  # Start all components
#   ./run_all.sh --simulation     # Simulation mode
#   ./run_all.sh --ros2           # Include ROS 2 nodes
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIMULATION_MODE=false
ROS2_MODE=false
LOG_DIR="$WORKSPACE_ROOT/logs"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --simulation)
      SIMULATION_MODE=true
      shift
      ;;
    --ros2)
      ROS2_MODE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [--simulation] [--ros2]"
      echo "  --simulation  Run in simulation mode (no hardware)"
      echo "  --ros2        Include ROS 2 safety nodes"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Create log directory
mkdir -p "$LOG_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Linear C Production System Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Workspace: ${GREEN}$WORKSPACE_ROOT${NC}"
echo -e "Simulation: ${YELLOW}$SIMULATION_MODE${NC}"
echo -e "ROS 2: ${YELLOW}$ROS2_MODE${NC}"
echo -e "Logs: ${GREEN}$LOG_DIR${NC}"
echo ""

# Function to start component
start_component() {
  local name=$1
  local cmd=$2
  local log_file="$LOG_DIR/${name}.log"
  
  echo -e "${GREEN}Starting $name...${NC}"
  
  # Run in background, redirect output to log
  eval "$cmd" > "$log_file" 2>&1 &
  local pid=$!
  
  # Save PID for later shutdown
  echo $pid > "$LOG_DIR/${name}.pid"
  
  echo -e "${GREEN}✓ $name started (PID: $pid)${NC}"
}

# Check if Python environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
  echo -e "${YELLOW}⚠ No virtual environment detected${NC}"
  echo -e "Consider activating a virtual environment first:"
  echo -e "  python -m venv venv"
  echo -e "  source venv/bin/activate"
  echo ""
fi

# 1. Start Hardware Safety Controller
if [ "$SIMULATION_MODE" = true ]; then
  HW_MODE="--simulation"
else
  HW_MODE=""
fi

start_component "hardware_safety" \
  "python -c 'from src.hardware.safety_controller import HardwareSafetyController, HardwareConfig, HardwareMode; \
  import time; \
  mode = HardwareMode.SIMULATION if \"$SIMULATION_MODE\" == \"true\" else HardwareMode.GPIO_RPI; \
  controller = HardwareSafetyController(HardwareConfig(mode=mode)); \
  print(\"Hardware safety controller running...\"); \
  while True: controller.heartbeat(); time.sleep(0.5)'"

sleep 1

# 2. Start Monitoring Dashboard
start_component "dashboard" \
  "python -m src.monitoring.dashboard"

sleep 2

# 3. Start ROS 2 nodes (if requested)
if [ "$ROS2_MODE" = true ]; then
  # Check if ROS 2 is sourced
  if [ -z "$ROS_DISTRO" ]; then
    echo -e "${YELLOW}⚠ ROS 2 not sourced - skipping ROS 2 nodes${NC}"
    echo -e "To enable ROS 2, source it first:"
    echo -e "  source /opt/ros/humble/setup.bash"
  else
    echo -e "${GREEN}Starting ROS 2 safety nodes...${NC}"
    
    # Source ROS 2 workspace if it exists
    if [ -f "$WORKSPACE_ROOT/ros2_ws/install/setup.bash" ]; then
      source "$WORKSPACE_ROOT/ros2_ws/install/setup.bash"
      
      # Launch safety system
      start_component "ros2_safety" \
        "ros2 launch linear_c_ros2 safety_system.launch.py"
    else
      echo -e "${YELLOW}⚠ ROS 2 workspace not built - skipping${NC}"
      echo -e "Build with: cd ros2_ws && colcon build"
    fi
  fi
fi

# Wait for all components to initialize
sleep 2

# Display status
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}System Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check component PIDs
for pid_file in "$LOG_DIR"/*.pid; do
  if [ -f "$pid_file" ]; then
    name=$(basename "$pid_file" .pid)
    pid=$(cat "$pid_file")
    
    if ps -p $pid > /dev/null; then
      echo -e "${GREEN}✓ $name (PID: $pid) - RUNNING${NC}"
    else
      echo -e "${RED}✗ $name (PID: $pid) - STOPPED${NC}"
    fi
  fi
done

echo ""
echo -e "${GREEN}All components started successfully!${NC}"
echo ""
echo -e "Monitor logs:"
echo -e "  tail -f $LOG_DIR/*.log"
echo ""
echo -e "View dashboard:"
echo -e "  http://localhost:8050"
echo ""
echo -e "Stop all components:"
echo -e "  ./stop_all.sh"
echo ""
