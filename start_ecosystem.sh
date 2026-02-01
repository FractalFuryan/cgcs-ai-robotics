#!/bin/bash
# Start Linear C Complete Safety Ecosystem
# Version 3.0.0

echo "🚀 Starting Linear C Complete Safety Ecosystem"
echo "=" "============================================================"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "❌ uvicorn not found. Install with: pip install uvicorn"
    exit 1
fi

# Function to start service in background
start_service() {
    local name=$1
    local module=$2
    local port=$3
    
    echo "📡 Starting $name on port $port..."
    uvicorn "$module" --host 0.0.0.0 --port "$port" --log-level info > "logs/${name}.log" 2>&1 &
    echo $! > "logs/${name}.pid"
    sleep 2
    
    if ps -p $(cat "logs/${name}.pid") > /dev/null; then
        echo "   ✅ $name started (PID: $(cat logs/${name}.pid))"
    else
        echo "   ❌ $name failed to start"
        return 1
    fi
}

# Create logs directory
mkdir -p logs

# Start services
echo ""
echo "🔧 Starting API Services..."
echo "-----------------------------------------------------------"

start_service "Marketplace" "marketplace.pattern_marketplace:app" 8001
start_service "Certification" "certification.certification_authority:cert_app" 8002
start_service "Control-Plane" "platform.control_plane.api.main:app" 8000

echo ""
echo "=" "============================================================"
echo "🎉 Linear C Ecosystem Started Successfully!"
echo "=" "============================================================"
echo ""
echo "🌐 Access Points:"
echo "  • Marketplace:      http://localhost:8001/docs"
echo "  • Certification:    http://localhost:8002/docs"
echo "  • Control Plane:    http://localhost:8000/docs"
echo ""
echo "📚 Knowledge Resources:"
echo "  • Research:         ./research/"
echo "  • Education:        ./education/"
echo "  • Standards:        ./standards/"
echo "  • Community:        ./community/"
echo ""
echo "📋 Logs:"
echo "  • Marketplace:      ./logs/Marketplace.log"
echo "  • Certification:    ./logs/Certification.log"
echo "  • Control-Plane:    ./logs/Control-Plane.log"
echo ""
echo "🛑 To stop all services: ./stop_ecosystem.sh"
echo "=" "============================================================"
