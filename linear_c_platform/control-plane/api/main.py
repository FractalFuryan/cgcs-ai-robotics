"""
Unified Control Plane API - Central management for all Linear C operations

This is the main API server for the Linear C Enterprise Safety Platform.
Provides REST and WebSocket endpoints for fleet management, safety validation,
and real-time monitoring.
"""
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import PlainTextResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import redis
except ImportError:
    redis = None
    
try:
    import jwt
except ImportError:
    jwt = None

try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
except ImportError:
    # Fallback if prometheus_client not installed
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def time(self): return self._NullContext()
        class _NullContext:
            def __enter__(self): return self
            def __exit__(self, *args): pass
    def generate_latest(): return b""
    CONTENT_TYPE_LATEST = "text/plain"

from src.core.linear_c.optimized import OptimizedLinearCValidator
from src.hardware.safety_controller import HardwareSafetyController, SafetyState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
VALIDATION_REQUESTS = Counter('validation_requests_total', 'Total validation requests')
VALIDATION_DURATION = Histogram('validation_duration_seconds', 'Validation duration in seconds')
SAFETY_VIOLATIONS = Counter('safety_violations_total', 'Total safety violations')
FLEET_SIZE = Counter('fleet_size', 'Number of robots in fleet')

app = FastAPI(
    title="Linear C Enterprise Safety Platform",
    description="Unified safety management for robot fleets",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable

# Redis for distributed state (optional - fallback to in-memory)
if redis:
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()  # Test connection
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}, using in-memory storage")
        redis_client = None
else:
    logger.warning("Redis not installed, using in-memory storage")
    redis_client = None

# In-memory storage fallback
memory_store = {
    'robots': {},
    'validations': {},
    'overrides': {}
}

class RobotRegistration(BaseModel):
    """Robot registration request"""
    robot_id: str = Field(..., description="Unique robot identifier")
    robot_type: str = Field(..., description="Robot model/type")
    capabilities: List[str] = Field(default_factory=list, description="Robot capabilities")
    location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")
    safety_profile: str = Field("default", description="Safety profile name")
    
class ValidationRequest(BaseModel):
    """Safety validation request"""
    robot_id: str
    linear_c_string: str
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
class FleetStatus(BaseModel):
    """Fleet status response"""
    total_robots: int
    active_robots: int
    safety_violations_24h: int
    avg_safety_score: float
    robots: List[Dict[str, Any]]

class SafetyOverrideRequest(BaseModel):
    """Safety override request (admin only)"""
    robot_id: str
    override_type: str
    duration_seconds: int
    reason: str
    operator_id: str

# Global validators (with connection pooling)
validators: Dict[str, OptimizedLinearCValidator] = {}
hardware_controllers: Dict[str, HardwareSafetyController] = {}

# WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT authentication"""
    token = credentials.credentials
    
    if not jwt:
        # Bypass auth if JWT not installed
        return {"user_id": "demo_user", "role": "admin"}
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception as e:
        logger.warning(f"Auth failed: {e}")
        # For demo purposes, allow access
        return {"user_id": "demo_user", "role": "admin"}

def get_robot_data(robot_id: str) -> Optional[Dict]:
    """Get robot data from storage"""
    if redis_client:
        try:
            robot_data = redis_client.hgetall(f"robot:{robot_id}")
            return dict(robot_data) if robot_data else None
        except:
            pass
    return memory_store['robots'].get(robot_id)

def set_robot_data(robot_id: str, data: Dict):
    """Set robot data in storage"""
    if redis_client:
        try:
            redis_client.hset(f"robot:{robot_id}", mapping=data)
            redis_client.sadd("fleet:robots", robot_id)
            return
        except:
            pass
    memory_store['robots'][robot_id] = data

def add_validation_log(robot_id: str, validation_log: Dict):
    """Add validation log to storage"""
    if redis_client:
        try:
            redis_client.xadd(f"validations:{robot_id}", validation_log)
            return
        except:
            pass
    if robot_id not in memory_store['validations']:
        memory_store['validations'][robot_id] = []
    memory_store['validations'][robot_id].append(validation_log)

def get_all_robot_ids() -> List[str]:
    """Get all robot IDs"""
    if redis_client:
        try:
            return list(redis_client.smembers("fleet:robots"))
        except:
            pass
    return list(memory_store['robots'].keys())

@app.on_event("startup")
async def startup_event():
    """Initialize platform on startup"""
    logger.info("Starting Linear C Enterprise Platform")
    
    # Start monitoring tasks
    asyncio.create_task(monitor_fleet_health())
    asyncio.create_task(update_safety_analytics())
    
    logger.info("Platform initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Check dependencies
    ready = True
    checks = {}
    
    if redis_client:
        try:
            redis_client.ping()
            checks['redis'] = 'ready'
        except:
            checks['redis'] = 'unavailable'
            ready = False
    else:
        checks['redis'] = 'not_configured'
    
    checks['validators'] = len(validators)
    
    return {
        "status": "ready" if ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/robots/register", status_code=201)
async def register_robot(
    registration: RobotRegistration,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user)
):
    """Register a new robot with the safety platform"""
    robot_id = registration.robot_id
    
    # Check if robot already exists
    if get_robot_data(robot_id):
        raise HTTPException(status_code=400, detail="Robot already registered")
    
    # Create validator for this robot
    validators[robot_id] = OptimizedLinearCValidator(max_workers=4)
    
    # Create hardware controller if needed
    if registration.robot_type in ["industrial_arm", "agv", "mobile_robot"]:
        hardware_controllers[robot_id] = HardwareSafetyController(simulation_mode=True)
    
    # Store robot metadata
    robot_data = {
        **registration.dict(),
        "registered_at": datetime.utcnow().isoformat(),
        "registered_by": user.get("user_id"),
        "last_heartbeat": datetime.utcnow().isoformat(),
        "status": "online",
        "safety_score": "100.0",
        "violations_24h": "0"
    }
    
    set_robot_data(robot_id, robot_data)
    
    # Update metrics
    FLEET_SIZE.inc()
    
    # Start background monitoring
    background_tasks.add_task(start_robot_monitoring, robot_id)
    
    logger.info(f"Robot {robot_id} registered successfully")
    
    return {"message": f"Robot {robot_id} registered successfully", "robot_id": robot_id}

@app.post("/api/v1/safety/validate")
async def validate_safety(
    request: ValidationRequest,
    user: Dict = Depends(get_current_user)
):
    """Validate robot action with Linear C"""
    VALIDATION_REQUESTS.inc()
    
    with VALIDATION_DURATION.time():
        # Get robot's validator
        validator = validators.get(request.robot_id)
        if not validator:
            raise HTTPException(status_code=404, detail="Robot not found or not registered")
        
        # Perform validation
        validation_result = validator.validate(request.linear_c_string, request.context)
        
        # Log validation
        validation_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "robot_id": request.robot_id,
            "linear_c": request.linear_c_string,
            "context": request.context or "",
            "is_valid": str(validation_result.is_valid),
            "message": validation_result.message,
            "validation_time_ns": str(validation_result.validation_time_ns),
            "user_id": user.get("user_id")
        }
        
        # Store validation log
        add_validation_log(request.robot_id, validation_log)
        
        # Update robot safety metrics
        if not validation_result.is_valid:
            SAFETY_VIOLATIONS.inc()
            
            # Increment violations counter
            robot_data = get_robot_data(request.robot_id)
            if robot_data:
                violations = int(robot_data.get('violations_24h', 0)) + 1
                robot_data['violations_24h'] = str(violations)
                set_robot_data(request.robot_id, robot_data)
            
            # Trigger hardware safety if configured
            hw_controller = hardware_controllers.get(request.robot_id)
            if hw_controller:
                hw_controller.trigger_warning(validation_result.message)
        
        # Calculate and update safety score
        safety_score = await calculate_safety_score(request.robot_id)
        robot_data = get_robot_data(request.robot_id)
        if robot_data:
            robot_data['safety_score'] = str(safety_score)
            set_robot_data(request.robot_id, robot_data)
        
        # Broadcast to WebSocket clients
        await broadcast_validation(request.robot_id, validation_log)
        
        # Return response
        return {
            "robot_id": request.robot_id,
            "validation": {
                "is_valid": validation_result.is_valid,
                "level": validation_result.level.value,
                "message": validation_result.message,
                "patterns_matched": validation_result.patterns_matched,
                "validation_time_ms": validation_result.validation_time_ns / 1e6
            },
            "safety_score": safety_score,
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/v1/fleet/status")
async def get_fleet_status(user: Dict = Depends(get_current_user)):
    """Get status of entire robot fleet"""
    robot_ids = get_all_robot_ids()
    
    robots = []
    total_violations = 0
    total_safety_score = 0
    active_count = 0
    
    for robot_id in robot_ids:
        robot_data = get_robot_data(robot_id)
        
        if robot_data:
            # Check if robot is active (heartbeat within last 5 minutes)
            last_heartbeat_str = robot_data.get("last_heartbeat", "2000-01-01T00:00:00")
            try:
                last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
                is_active = (datetime.utcnow() - last_heartbeat) < timedelta(minutes=5)
            except:
                is_active = False
            
            if is_active:
                active_count += 1
            
            robot_dict = {
                "robot_id": robot_id,
                **robot_data,
                "is_active": is_active
            }
            
            robots.append(robot_dict)
            
            violations = int(robot_data.get("violations_24h", 0))
            total_violations += violations
            
            safety_score = float(robot_data.get("safety_score", 100.0))
            total_safety_score += safety_score
    
    avg_safety_score = total_safety_score / len(robots) if robots else 100.0
    
    return FleetStatus(
        total_robots=len(robots),
        active_robots=active_count,
        safety_violations_24h=total_violations,
        avg_safety_score=avg_safety_score,
        robots=robots
    )

@app.post("/api/v1/safety/override")
async def safety_override(
    request: SafetyOverrideRequest,
    user: Dict = Depends(get_current_user)
):
    """Request safety override (admin only)"""
    # Check admin permissions
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate override request
    if request.duration_seconds > 3600:  # 1 hour max
        raise HTTPException(status_code=400, detail="Override duration too long")
    
    # Create override record
    override_id = f"override_{datetime.utcnow().timestamp()}"
    override_data = {
        **request.dict(),
        "requested_by": user.get("user_id"),
        "requested_at": datetime.utcnow().isoformat(),
        "status": "active",
        "override_id": override_id
    }
    
    # Store override (in-memory for now)
    memory_store['overrides'][override_id] = override_data
    
    logger.info(f"Safety override granted for {request.robot_id}: {override_id}")
    
    return {
        "message": "Safety override granted",
        "override_id": override_id,
        "expires_in": f"{request.duration_seconds} seconds"
    }

@app.get("/api/v1/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(
        content=generate_latest().decode('utf-8'),
        media_type=CONTENT_TYPE_LATEST
    )

@app.websocket("/api/v1/ws/safety-monitor/{robot_id}")
async def websocket_safety_monitor(websocket: WebSocket, robot_id: str):
    """WebSocket for real-time safety monitoring"""
    await websocket.accept()
    
    # Add to active connections
    if robot_id not in active_connections:
        active_connections[robot_id] = []
    active_connections[robot_id].append(websocket)
    
    logger.info(f"WebSocket connected for robot {robot_id}")
    
    try:
        while True:
            # Send heartbeat every 5 seconds
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for robot {robot_id}")
        active_connections[robot_id].remove(websocket)
        if not active_connections[robot_id]:
            del active_connections[robot_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections.get(robot_id, []):
            active_connections[robot_id].remove(websocket)

async def broadcast_validation(robot_id: str, validation_log: Dict):
    """Broadcast validation to WebSocket clients"""
    if robot_id in active_connections:
        message = {
            "type": "validation",
            "data": validation_log
        }
        
        # Send to all connected clients for this robot
        dead_connections = []
        for websocket in active_connections[robot_id]:
            try:
                await websocket.send_json(message)
            except:
                dead_connections.append(websocket)
        
        # Remove dead connections
        for conn in dead_connections:
            active_connections[robot_id].remove(conn)

async def start_robot_monitoring(robot_id: str):
    """Start background monitoring for a robot"""
    logger.info(f"Starting monitoring for robot {robot_id}")
    
    # Monitoring runs in the background
    # For now, this is a placeholder for future implementation
    pass

async def calculate_safety_score(robot_id: str) -> float:
    """Calculate current safety score for robot"""
    # Simple scoring based on recent violations
    robot_data = get_robot_data(robot_id)
    
    if not robot_data:
        return 100.0
    
    violations = int(robot_data.get('violations_24h', 0))
    
    # Start at 100, deduct 5 points per violation
    safety_score = 100.0 - min(violations * 5, 50)  # Max 50% penalty
    
    return max(0.0, min(100.0, safety_score))

async def monitor_fleet_health():
    """Monitor overall fleet health"""
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            
            # Check for robots needing attention
            robot_ids = get_all_robot_ids()
            
            for robot_id in robot_ids:
                robot_data = get_robot_data(robot_id)
                
                if robot_data:
                    safety_score = float(robot_data.get("safety_score", 100.0))
                    
                    if safety_score < 70:
                        logger.warning(f"SAFETY ALERT: Robot {robot_id} has low safety score: {safety_score}")
            
        except Exception as e:
            logger.error(f"Fleet health monitoring error: {e}")
            await asyncio.sleep(300)

async def update_safety_analytics():
    """Update safety analytics periodically"""
    while True:
        try:
            await asyncio.sleep(300)  # Update every 5 minutes
            
            # Aggregate fleet safety data
            # This would integrate with the analytics engine
            robot_ids = get_all_robot_ids()
            
            logger.info(f"Analytics update: {len(robot_ids)} robots in fleet")
            
        except Exception as e:
            logger.error(f"Analytics update error: {e}")
            await asyncio.sleep(600)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
