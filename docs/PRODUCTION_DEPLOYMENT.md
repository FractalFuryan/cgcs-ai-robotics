# Linear C Production Deployment Guide

Complete guide for deploying Linear C safety validation in production robotics systems.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Components](#components)
5. [Deployment](#deployment)
6. [Hardware Setup](#hardware-setup)
7. [ROS 2 Integration](#ros-2-integration)
8. [Monitoring & Analytics](#monitoring--analytics)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This production deployment includes:

- **Optimized Validator**: High-performance Linear C validation with caching (10x faster)
- **Hardware Safety Controller**: GPIO-based emergency stop and physical enforcement
- **Monitoring Dashboard**: Real-time safety metrics and violation tracking
- **ROS 2 Integration**: Safety server and bridge nodes (optional)
- **Simulation Support**: Test without physical hardware
- **Auto-deployment**: Automated setup and orchestration scripts

**Performance:**
- Validation latency: <1ms (cached), <5ms (uncached)
- Cache hit rate: >90% in production
- Throughput: >1000 validations/sec
- Hardware response: <10ms emergency stop

---

## Quick Start

### 1. Deploy Everything

```bash
# Clone repository
git clone https://github.com/yourusername/cgcs-ai-robotics.git
cd cgcs-ai-robotics

# Deploy all components in simulation mode
python deploy_all.py --all --simulation

# Start all services
./run_all.sh --simulation

# View dashboard
open http://localhost:8050
```

### 2. Test Validation

```python
from src.core.linear_c.optimized import OptimizedLinearCValidator

validator = OptimizedLinearCValidator()

# Validate an action
result = validator.validate("🔵🧠🚶", "autonomous_movement")
print(f"Valid: {result.is_valid}")

# Get performance metrics
metrics = validator.get_performance_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
```

### 3. Stop All Services

```bash
./stop_all.sh
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Optional: ROS 2 Humble (for ROS integration)
- Optional: Raspberry Pi with GPIO (for hardware control)

### Core Installation

```bash
# Install with development dependencies
pip install -e .[dev]

# Run tests
pytest tests/ -v
```

### Optional Components

```bash
# Hardware support (Raspberry Pi)
pip install -e .[hardware]

# ROS 2 integration
pip install -e .[ros2]

# Simulation tools
pip install -e .[simulation]

# Analytics dashboard
pip install -e .[analytics]

# Install everything
pip install -e .[all]
```

---

## Components

### 1. Optimized Validator

**Location:** `src/core/linear_c/optimized.py`

High-performance validator with:
- LRU caching (10,000 entry default)
- Pre-compiled regex patterns
- Thread-safe metrics collection
- Batch validation support

**Usage:**

```python
from src.core.linear_c.optimized import OptimizedLinearCValidator

# Initialize with custom settings
validator = OptimizedLinearCValidator(
    max_workers=4,      # Thread pool size
    cache_size=10000    # LRU cache size
)

# Single validation
result = validator.validate("🔵🧠🚶", "autonomous_movement")

# Batch validation (parallel)
linear_c_strings = ["🔵🧠🚶", "🟡🧠⚠️", "🛡️🔴⛔"]
results = validator.validate_batch(linear_c_strings)

# Performance metrics
metrics = validator.get_performance_metrics()
print(f"Avg validation time: {metrics['avg_time_ns']/1e6:.2f} ms")
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
print(f"Throughput: {metrics['throughput_per_sec']:.0f} val/sec")
```

**Performance Tuning:**

```python
# Increase cache size for high-variability workloads
validator = OptimizedLinearCValidator(cache_size=50000)

# More workers for heavy batch processing
validator = OptimizedLinearCValidator(max_workers=8)

# Clear cache if patterns change
validator.clear_cache()
```

### 2. Hardware Safety Controller

**Location:** `src/hardware/safety_controller.py`

Physical safety enforcement via GPIO:
- Emergency stop relay
- Warning/fault indication LEDs
- Motor enable/disable control
- Hardware watchdog (prevents deadlock)

**Hardware Wiring (Raspberry Pi):**

```
Pin Layout (BCM numbering):
- GPIO 17: Emergency stop relay (normally open)
- GPIO 23: Motor enable signal
- GPIO 27: Warning LED (yellow)
- GPIO 22: Fault LED (red)
```

**Usage:**

```python
from src.hardware.safety_controller import (
    HardwareSafetyController, 
    HardwareConfig,
    HardwareMode,
    SafetyState
)

# Simulation mode (testing)
config = HardwareConfig(mode=HardwareMode.SIMULATION)
controller = HardwareSafetyController(config)

# Hardware mode (Raspberry Pi)
config = HardwareConfig(
    mode=HardwareMode.GPIO_RPI,
    emergency_stop_pin=17,
    enable_pin=23,
    watchdog_timeout=1.0  # seconds
)
controller = HardwareSafetyController(config)

# Send heartbeat regularly (required to prevent watchdog timeout)
controller.heartbeat()

# Trigger emergency stop on Linear C violation
controller.trigger_emergency_stop("Linear C BLOCK level violation")

# Trigger warning on minor violations
controller.trigger_warning("Linear C WARN level violation")

# Reset from warning state
controller.reset()

# Get current status
status = controller.get_status()
print(f"State: {status['state']}")
```

**Integration with Validator:**

```python
# Register callback for safety violations
def emergency_callback(reason: str):
    logger.critical(f"EMERGENCY: {reason}")
    # Additional shutdown logic here

controller.register_callback(SafetyState.EMERGENCY, emergency_callback)

# Validate action with hardware enforcement
result = validator.validate(linear_c, context)

if result.level == ValidationLevel.BLOCK:
    controller.trigger_emergency_stop(result.message)
elif result.level == ValidationLevel.WARN:
    controller.trigger_warning(result.message)

# Send heartbeat in control loop
controller.heartbeat()
```

### 3. Monitoring Dashboard

**Location:** `src/monitoring/dashboard.py`

Real-time safety monitoring with:
- Live validation metrics
- Violation history
- Safety score tracking
- Performance graphs

**Usage:**

```bash
# Start dashboard
python -m src.monitoring.dashboard

# View at http://localhost:8050
```

**Features:**
- Real-time safety score (0-100)
- Violation count by severity
- Validation latency histogram
- Cache hit rate monitoring
- Alert notifications

---

## Deployment

### Automated Deployment

```bash
# Deploy all components
python deploy_all.py --all

# Deploy specific components
python deploy_all.py --core --hardware --monitoring

# Deploy with ROS 2
python deploy_all.py --all --ros2

# Simulation mode (no hardware)
python deploy_all.py --all --simulation
```

The deployment script:
1. Checks Python version (>= 3.8)
2. Installs dependencies
3. Configures components
4. Runs tests
5. Generates deployment summary

### Manual Deployment

```bash
# 1. Install dependencies
pip install -e .[all]

# 2. Run tests
pytest tests/ -v

# 3. Configure hardware
vi hardware_config.json

# 4. Start components
./run_all.sh
```

### Production Deployment (systemd)

Create systemd service for persistent operation:

```bash
# Create service file
sudo nano /etc/systemd/system/linear-c.service
```

```ini
[Unit]
Description=Linear C Safety System
After=network.target

[Service]
Type=simple
User=robot
WorkingDirectory=/opt/cgcs-ai-robotics
ExecStart=/opt/cgcs-ai-robotics/run_all.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable linear-c
sudo systemctl start linear-c

# Check status
sudo systemctl status linear-c

# View logs
journalctl -u linear-c -f
```

---

## Hardware Setup

### Raspberry Pi GPIO Wiring

**Emergency Stop Circuit:**

```
Raspberry Pi GPIO 17 -> Relay (5V trigger)
Relay NO -> Motor Power
Relay COM -> Motor Controller Enable
```

**Safety Indicators:**

```
GPIO 27 (Warning) -> 330Ω resistor -> Yellow LED -> GND
GPIO 22 (Fault) -> 330Ω resistor -> Red LED -> GND
```

**Motor Enable:**

```
GPIO 23 -> Motor Controller Enable Pin
```

### Testing Hardware (Simulation Mode)

```python
from src.hardware.safety_controller import HardwareSafetyController, HardwareConfig, HardwareMode

# Test in simulation
config = HardwareConfig(mode=HardwareMode.SIMULATION)
controller = HardwareSafetyController(config)

# Test emergency stop
controller.trigger_emergency_stop("Test")
print(controller.get_status())

# Test reset
controller.reset()
print(controller.get_status())

controller.shutdown()
```

### Hardware Validation

```bash
# Run hardware tests (requires GPIO)
pytest tests/unit/test_hardware_safety.py -v -m hardware

# Check GPIO pin status
gpio readall  # On Raspberry Pi
```

---

## ROS 2 Integration

### Prerequisites

```bash
# Install ROS 2 Humble
sudo apt install ros-humble-desktop

# Source ROS 2
source /opt/ros/humble/setup.bash
```

### Building ROS 2 Packages

```bash
# Create workspace
mkdir -p ros2_ws/src
cd ros2_ws/src

# Copy Linear C ROS 2 package
cp -r ../../ros2_packages/linear_c_ros2 .

# Build
cd ..
colcon build --symlink-install

# Source workspace
source install/setup.bash
```

### Running Safety Server

```bash
# Launch safety system
ros2 launch linear_c_ros2 safety_system.launch.py

# Validate action via ROS 2 service
ros2 service call /linear_c/validate linear_c_interfaces/srv/ValidateAction \
  "{linear_c: '🔵🧠🚶', context: 'autonomous_movement', action_name: 'move_forward'}"
```

---

## Monitoring & Analytics

### Dashboard Access

```bash
# Start dashboard
python -m src.monitoring.dashboard

# Open browser
http://localhost:8050
```

**Dashboard Sections:**
1. **Overview**: Safety score, validation count, violation rate
2. **Performance**: Latency histogram, cache metrics, throughput
3. **Violations**: Recent violations, severity breakdown
4. **Trends**: Historical safety metrics, score over time

### Metrics Export

```python
from src.core.linear_c.optimized import OptimizedLinearCValidator

validator = OptimizedLinearCValidator()

# Get metrics
metrics = validator.get_performance_metrics()

# Export to JSON
import json
with open('metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
```

### Log Analysis

```bash
# View all logs
tail -f logs/*.log

# Filter for violations
grep "BLOCK\|EMERGENCY" logs/*.log

# Count violations by type
grep -c "BLOCK" logs/dashboard.log
```

---

## Testing

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific component tests
pytest tests/unit/test_optimized_validator.py -v
pytest tests/unit/test_hardware_safety.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Performance Benchmarks

```bash
# Run benchmark tests
pytest tests/unit/test_optimized_validator.py -v -m benchmark

# Profile validation performance
python -m cProfile -s cumtime examples/linear_c_integration/quickstart.py
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/ -v

# Test ROS 2 integration (requires ROS 2)
pytest tests/integration/test_ros2_bridge.py -v -m ros2

# Test hardware (requires GPIO)
pytest tests/integration/test_hardware_integration.py -v -m hardware
```

### Simulation Tests

```bash
# Run simulation tests
pytest tests/ -v --simulation
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Ensure package is installed in editable mode
pip install -e .

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

#### 2. GPIO Permission Denied

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot required
sudo reboot
```

#### 3. Watchdog Timeout

```python
# Increase watchdog timeout
config = HardwareConfig(watchdog_timeout=2.0)

# Or send heartbeat more frequently
import threading

def heartbeat_loop(controller):
    while True:
        controller.heartbeat()
        time.sleep(0.1)

thread = threading.Thread(target=heartbeat_loop, args=(controller,))
thread.daemon = True
thread.start()
```

#### 4. Cache Not Effective

```python
# Check cache hit rate
metrics = validator.get_performance_metrics()
print(f"Hit rate: {metrics['cache_hit_rate']:.1%}")

# Increase cache size
validator = OptimizedLinearCValidator(cache_size=50000)

# Warm up cache with common patterns
common_patterns = [...]
for pattern in common_patterns:
    validator.validate(pattern, None)
```

#### 5. Dashboard Not Loading

```bash
# Check if port 8050 is available
lsof -i :8050

# Kill conflicting process
kill <PID>

# Start dashboard on different port
DASH_PORT=8051 python -m src.monitoring.dashboard
```

### Debug Mode

```python
import structlog
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
)
```

### Getting Help

1. Check logs: `logs/*.log`
2. Review deployment summary: `deployment_summary.json`
3. Run diagnostics: `python -m src.diagnostics`
4. GitHub Issues: [Report issues](https://github.com/yourusername/cgcs-ai-robotics/issues)

---

## Performance Optimization

### Validation Performance

```python
# Optimize for low latency
validator = OptimizedLinearCValidator(
    max_workers=4,
    cache_size=10000
)

# Warm up cache
for pattern in common_patterns:
    validator.validate(pattern, None)

# Use batch validation for throughput
results = validator.validate_batch(linear_c_strings)
```

### Hardware Performance

```python
# Minimize emergency stop latency
config = HardwareConfig(
    watchdog_timeout=0.5  # Faster timeout
)

# Use callbacks for async handling
controller.register_callback(SafetyState.EMERGENCY, emergency_handler)
```

### Memory Optimization

```python
# Reduce cache size if memory constrained
validator = OptimizedLinearCValidator(cache_size=1000)

# Clear cache periodically
import time
while True:
    time.sleep(3600)  # Every hour
    validator.clear_cache()
```

---

## Production Checklist

- [ ] Install all dependencies: `pip install -e .[all]`
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Configure hardware pins (if using GPIO)
- [ ] Test emergency stop circuit
- [ ] Set up systemd service for auto-start
- [ ] Configure log rotation
- [ ] Set up monitoring/alerting
- [ ] Test ROS 2 integration (if applicable)
- [ ] Benchmark performance under load
- [ ] Create backup/recovery procedures
- [ ] Document custom configuration
- [ ] Train operators on emergency procedures

---

## Support & Resources

- **Documentation**: [docs/](docs/)
- **Examples**: [examples/linear_c_integration/](examples/linear_c_integration/)
- **Tests**: [tests/](tests/)
- **GitHub**: https://github.com/yourusername/cgcs-ai-robotics
- **Issues**: https://github.com/yourusername/cgcs-ai-robotics/issues
