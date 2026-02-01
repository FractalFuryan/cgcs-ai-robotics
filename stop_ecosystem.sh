#!/bin/bash
# Stop Linear C Complete Safety Ecosystem
# Version 3.0.0

echo "🛑 Stopping Linear C Complete Safety Ecosystem"
echo "================================================================"

# Function to stop service
stop_service() {
    local name=$1
    local pid_file="logs/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "  Stopping $name (PID: $pid)..."
            kill "$pid"
            sleep 1
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "    Force stopping $name..."
                kill -9 "$pid"
            fi
            
            rm "$pid_file"
            echo "    ✅ $name stopped"
        else
            echo "  ⚠️  $name not running (stale PID file)"
            rm "$pid_file"
        fi
    else
        echo "  ⚠️  $name PID file not found"
    fi
}

# Stop all services
stop_service "Marketplace"
stop_service "Certification"
stop_service "Control-Plane"

echo ""
echo "================================================================"
echo "✅ All ecosystem services stopped"
echo "================================================================"
