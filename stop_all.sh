#!/bin/bash
#
# Stop All Linear C Production Components
#
# Usage:
#   ./stop_all.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$WORKSPACE_ROOT/logs"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Stopping Linear C Production System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to stop component
stop_component() {
  local name=$1
  local pid_file="$LOG_DIR/${name}.pid"
  
  if [ ! -f "$pid_file" ]; then
    echo -e "${YELLOW}⚠ No PID file for $name${NC}"
    return
  fi
  
  local pid=$(cat "$pid_file")
  
  if ps -p $pid > /dev/null 2>&1; then
    echo -e "${GREEN}Stopping $name (PID: $pid)...${NC}"
    kill $pid
    sleep 1
    
    # Force kill if still running
    if ps -p $pid > /dev/null 2>&1; then
      echo -e "${YELLOW}Force stopping $name...${NC}"
      kill -9 $pid
    fi
    
    echo -e "${GREEN}✓ $name stopped${NC}"
  else
    echo -e "${YELLOW}⚠ $name (PID: $pid) not running${NC}"
  fi
  
  # Remove PID file
  rm -f "$pid_file"
}

# Stop all components
if [ -d "$LOG_DIR" ]; then
  for pid_file in "$LOG_DIR"/*.pid; do
    if [ -f "$pid_file" ]; then
      name=$(basename "$pid_file" .pid)
      stop_component "$name"
    fi
  done
else
  echo -e "${YELLOW}No running components found${NC}"
fi

echo ""
echo -e "${GREEN}All components stopped${NC}"
echo ""
