# Dockerfile for Analytics Engine
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy code
COPY src ./src
COPY platform ./platform

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    pandas==2.0.3 \
    numpy==1.24.3 \
    scikit-learn==1.3.2 \
    redis==5.0.1

# Run the analytics engine
CMD ["python", "platform/analytics-engine/advanced_analytics.py"]
