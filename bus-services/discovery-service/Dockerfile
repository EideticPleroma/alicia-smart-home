# Alicia Discovery Service Dockerfile
# Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY main.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (no HTTP API for discovery service)
# Port not needed as this is MQTT-only service

# Health check (MQTT connectivity)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('alicia_bus_core', 1883))" || exit 1

# Start service
CMD ["python", "main.py"]
