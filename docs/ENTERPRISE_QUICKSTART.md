# 🚀 Linear C Enterprise Platform - Quick Start Guide

Welcome to the **Linear C Enterprise Safety Platform**! This guide will help you deploy and use the complete enterprise-grade safety system for robot fleets.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Architecture](#architecture)
- [Deployment Options](#deployment-options)
- [API Usage](#api-usage)
- [Dashboard](#dashboard)
- [Advanced Features](#advanced-features)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The Linear C Enterprise Platform provides:

✅ **Unified Control Plane** - Single API for all safety operations  
✅ **Real-time Dashboard** - React-based monitoring interface  
✅ **Multi-Robot Fleet Management** - Scale from 1 to 1000+ robots  
✅ **Advanced Analytics** - ML-powered predictive safety  
✅ **Enterprise Security** - JWT authentication, RBAC  
✅ **Cloud Native** - Kubernetes-ready deployment  

## ⚡ Quick Start (5 Minutes)

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Git

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/FractalFuryan/cgcs-ai-robotics.git
cd cgcs-ai-robotics

# Install dependencies
pip install -e .[enterprise]
```

### 2. Deploy with Docker Compose

```bash
# Deploy entire platform
python deploy_enterprise.py --environment development --type docker-compose
```

That's it! The platform is now running:

- 🌐 **Control Plane API**: http://localhost:8000
- 📊 **API Docs**: http://localhost:8000/api/docs
- 🎨 **Dashboard**: http://localhost:3000
- 📈 **Prometheus**: http://localhost:9090
- 📉 **Grafana**: http://localhost:3001 (admin/admin)

### 3. Register Your First Robot

```bash
curl -X POST http://localhost:8000/api/v1/robots/register \
  -H 'Authorization: Bearer demo-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "robot_id": "robot-001",
    "robot_type": "agv",
    "capabilities": ["navigation", "manipulation"],
    "safety_profile": "default"
  }'
```

### 4. Test Safety Validation

```bash
# Valid pattern - should pass
curl -X POST http://localhost:8000/api/v1/safety/validate \
  -H 'Authorization: Bearer demo-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "robot_id": "robot-001",
    "linear_c_string": "🟢🧠",
    "context": "navigation"
  }'

# Prohibited pattern - should fail
curl -X POST http://localhost:8000/api/v1/safety/validate \
  -H 'Authorization: Bearer demo-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "robot_id": "robot-001",
    "linear_c_string": "🔴🚶",
    "context": "navigation"
  }'
```

### 5. View Fleet Status

```bash
curl http://localhost:8000/api/v1/fleet/status \
  -H 'Authorization: Bearer demo-token'
```

### 6. Open Dashboard

Visit http://localhost:3000 to see the real-time safety dashboard.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Linear C Enterprise Platform              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Dashboard  │  │  Control     │  │  Analytics   │      │
│  │   (React)    │  │  Plane API   │  │  Engine      │      │
│  │              │  │  (FastAPI)   │  │  (ML)        │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┼──────────────────┘               │
│                           │                                  │
│                    ┌──────┴───────┐                         │
│                    │     Redis    │                         │
│                    │ (State Store)│                         │
│                    └──────────────┘                         │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Monitoring: Prometheus + Grafana                            │
│  Security: JWT Auth, RBAC, TLS                              │
│  Storage: Redis + PostgreSQL (optional)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚢 Deployment Options

### Option 1: Docker Compose (Development)

**Best for:** Local development, testing, demos

```bash
python deploy_enterprise.py --type docker-compose
```

**Services deployed:**
- Control Plane API (port 8000)
- Dashboard (port 3000)
- Redis (port 6379)
- Prometheus (port 9090)
- Grafana (port 3001)
- Analytics Engine

**Manage services:**
```bash
# View logs
docker-compose -f deployments/docker-compose/enterprise.yml logs -f

# Stop services
docker-compose -f deployments/docker-compose/enterprise.yml down

# Restart
docker-compose -f deployments/docker-compose/enterprise.yml restart
```

### Option 2: Kubernetes (Production)

**Best for:** Production deployments, scaling, high availability

```bash
# Deploy to Kubernetes
python deploy_enterprise.py --type kubernetes --environment production

# Or manually with kubectl
kubectl apply -f deployments/kubernetes/linear-c-platform.yaml
```

**Features:**
- Auto-scaling (2-10 replicas)
- Load balancing
- High availability
- Rolling updates
- Health checks

**Manage deployment:**
```bash
# View pods
kubectl get pods -n linear-c-safety

# View logs
kubectl logs -f -n linear-c-safety deployment/control-plane

# Scale manually
kubectl scale -n linear-c-safety deployment/control-plane --replicas=5

# Delete deployment
kubectl delete namespace linear-c-safety
```

### Option 3: Cloud Providers

**AWS EKS:**
```bash
# Create EKS cluster
eksctl create cluster --name linear-c-cluster --region us-east-1

# Deploy
kubectl apply -f deployments/kubernetes/linear-c-platform.yaml
```

**Google GKE:**
```bash
# Create GKE cluster
gcloud container clusters create linear-c-cluster --zone us-central1-a

# Deploy
kubectl apply -f deployments/kubernetes/linear-c-platform.yaml
```

**Azure AKS:**
```bash
# Create AKS cluster
az aks create --resource-group linear-c-rg --name linear-c-cluster

# Deploy
kubectl apply -f deployments/kubernetes/linear-c-platform.yaml
```

## 📡 API Usage

### Authentication

All API requests require a JWT token:

```bash
curl http://localhost:8000/api/v1/endpoint \
  -H 'Authorization: Bearer <your-token-here>'
```

For development, use: `Bearer demo-token`

### Core Endpoints

#### 1. Register Robot
```bash
POST /api/v1/robots/register
```

**Request:**
```json
{
  "robot_id": "robot-001",
  "robot_type": "agv",
  "capabilities": ["navigation", "manipulation"],
  "location": {"lat": 37.7749, "lon": -122.4194},
  "safety_profile": "industrial"
}
```

**Response:**
```json
{
  "message": "Robot robot-001 registered successfully",
  "robot_id": "robot-001"
}
```

#### 2. Validate Safety
```bash
POST /api/v1/safety/validate
```

**Request:**
```json
{
  "robot_id": "robot-001",
  "linear_c_string": "🟢🧠",
  "context": "navigation",
  "metadata": {"speed": 0.5}
}
```

**Response:**
```json
{
  "robot_id": "robot-001",
  "validation": {
    "is_valid": true,
    "level": "safe",
    "message": "Safe pattern validated",
    "patterns_matched": ["🟢"],
    "validation_time_ms": 1.23
  },
  "safety_score": 95.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 3. Get Fleet Status
```bash
GET /api/v1/fleet/status
```

**Response:**
```json
{
  "total_robots": 10,
  "active_robots": 8,
  "safety_violations_24h": 5,
  "avg_safety_score": 92.3,
  "robots": [
    {
      "robot_id": "robot-001",
      "robot_type": "agv",
      "status": "online",
      "safety_score": 95.5,
      "violations_24h": 0,
      "is_active": true
    }
  ]
}
```

#### 4. Safety Override (Admin Only)
```bash
POST /api/v1/safety/override
```

**Request:**
```json
{
  "robot_id": "robot-001",
  "override_type": "temporary",
  "duration_seconds": 300,
  "reason": "Emergency maintenance",
  "operator_id": "admin-user"
}
```

### WebSocket - Real-time Monitoring

Connect to WebSocket for real-time validation events:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/safety-monitor/robot-001');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'validation') {
    console.log('Validation event:', data.data);
  }
};
```

## 🎨 Dashboard

The enterprise dashboard provides:

### Fleet Overview Tab
- **Fleet summary** - Total robots, active robots, violations
- **Safety score distribution** - Visual bar charts
- **Robot table** - Detailed robot status with filters

### Robot Details Tab
- **Real-time monitoring** - Live validation feed
- **Performance metrics** - Response times, success rates
- **Historical data** - Trend analysis

### Safety Alerts Tab
- **Active alerts** - Current safety violations
- **Alert history** - Past incidents
- **Severity levels** - High, medium, low

### Analytics Tab (Advanced)
- **Predictive safety** - ML-based risk predictions
- **Anomaly detection** - Unusual behavior alerts
- **Pattern analysis** - Fleet-wide safety patterns

## 🧠 Advanced Features

### Predictive Safety (ML)

The analytics engine provides predictive safety scores:

```python
from platform.analytics_engine.advanced_analytics import AdvancedAnalyticsEngine

engine = AdvancedAnalyticsEngine()

# Predict safety risk
features = {
    'velocity': 1.2,
    'proximity_to_human': 0.8,
    'battery_level': 45.0,
    'violation_count_1h': 2
}

prediction = await engine.predict_safety_risk('robot-001', features)
print(f"Risk: {prediction.prediction}")
print(f"Confidence: {prediction.confidence:.2%}")
print(f"Action: {prediction.recommended_action}")
```

### Anomaly Detection

Detect unusual robot behavior:

```python
# Detect anomalies
recent_validations = [...]  # List of recent validation data
anomaly = await engine.detect_anomalies('robot-001', recent_validations)

if anomaly.is_anomaly:
    print(f"Anomaly detected: {anomaly.anomaly_type}")
    print(f"Severity: {anomaly.severity}")
    print(f"Contributing factors: {anomaly.features_contributing}")
```

### Safety Reports

Generate comprehensive safety reports:

```python
# Generate daily report
report = await engine.generate_safety_report(robot_data, 'daily')

print(f"Total validations: {report['metrics']['total_validations']}")
print(f"Violation rate: {report['metrics']['violation_rate']:.2%}")
print(f"Insights: {len(report['insights'])} insights")
```

## 🔒 Production Deployment

### Security Checklist

- [ ] **Change default secrets** in `deployments/kubernetes/linear-c-platform.yaml`
- [ ] **Enable TLS** for all endpoints
- [ ] **Configure JWT secret** from environment variable
- [ ] **Set up Redis password** authentication
- [ ] **Enable network policies** in Kubernetes
- [ ] **Configure backup** for Redis data
- [ ] **Set resource limits** for all pods
- [ ] **Enable monitoring** and alerting
- [ ] **Configure log aggregation** (ELK, Splunk)
- [ ] **Set up disaster recovery** plan

### Performance Tuning

**Control Plane:**
```yaml
# Increase replicas
replicas: 10

# Adjust resources
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

**Redis:**
```yaml
# Enable persistence
command: redis-server --appendonly yes --maxmemory 2gb

# Use Redis Cluster for HA
# Deploy Redis Sentinel for failover
```

**Auto-scaling:**
```yaml
# HPA configuration
minReplicas: 5
maxReplicas: 50
targetCPUUtilizationPercentage: 60
```

### Monitoring Setup

**Prometheus Alerts:**
```yaml
# High violation rate alert
- alert: HighViolationRate
  expr: rate(safety_violations_total[5m]) > 0.1
  for: 5m
  annotations:
    summary: "High safety violation rate"
```

**Grafana Dashboards:**
1. Fleet Overview
2. Safety Metrics
3. Performance Metrics
4. System Health

### Backup Strategy

**Redis Backup:**
```bash
# Automated daily backups
kubectl exec -n linear-c-safety redis-master-0 -- redis-cli BGSAVE

# Copy backup
kubectl cp linear-c-safety/redis-master-0:/data/dump.rdb ./backup/
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Services not starting

```bash
# Check Docker Compose logs
docker-compose -f deployments/docker-compose/enterprise.yml logs

# Check pod status
kubectl get pods -n linear-c-safety
kubectl describe pod <pod-name> -n linear-c-safety
```

#### 2. Redis connection failed

```bash
# Test Redis connectivity
redis-cli -h localhost -p 6379 ping

# Check Redis logs
docker-compose -f deployments/docker-compose/enterprise.yml logs redis
```

#### 3. API authentication errors

- Verify JWT token is included in header
- Check token format: `Bearer <token>`
- For development, use: `Bearer demo-token`

#### 4. WebSocket connection issues

- Verify WebSocket URL uses `ws://` or `wss://`
- Check firewall allows WebSocket connections
- Verify CORS configuration in API

### Debug Mode

Enable detailed logging:

```bash
# Docker Compose
export LOG_LEVEL=DEBUG
docker-compose -f deployments/docker-compose/enterprise.yml up

# Kubernetes
kubectl set env -n linear-c-safety deployment/control-plane LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# Control Plane health
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Metrics
curl http://localhost:8000/api/v1/metrics
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/api/docs
- **Linear C Core Docs**: [LINEAR_C_QUICKSTART.md](LINEAR_C_QUICKSTART.md)
- **Production Deployment**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **GitHub Repository**: https://github.com/FractalFuryan/cgcs-ai-robotics

## 🆘 Support

For issues and questions:
- **GitHub Issues**: https://github.com/FractalFuryan/cgcs-ai-robotics/issues
- **Documentation**: Check docs/ directory
- **Examples**: See examples/ directory

## 📄 License

Apache License 2.0 - See [LICENSE.md](../LICENSE.md)

---

**🎉 Congratulations!** You now have a production-ready enterprise safety platform for robot fleets!
