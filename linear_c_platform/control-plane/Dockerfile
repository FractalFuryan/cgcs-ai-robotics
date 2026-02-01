# Dockerfile for Linear C Control Plane
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY src ./src
COPY linear_c_platform ./linear_c_platform

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    redis==5.0.1 \
    PyJWT==2.8.0 \
    prometheus-client==0.19.0 \
    websockets==12.0 \
    structlog==23.2.0 \
    numpy==1.24.3

# Expose ports
EXPOSE 8000 8001

# Run the application
CMD ["python", "-m", "uvicorn", "platform.control-plane.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
