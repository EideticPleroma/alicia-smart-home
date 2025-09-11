# Alicia Bus Architecture - Advanced Voice Pipeline Dockerfile
# Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libasound2-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create directories for audio processing and models
RUN mkdir -p /app/audio /app/models /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash alicia && \
    chown -R alicia:alicia /app
USER alicia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8012/health')" || exit 1

# Expose port
EXPOSE 8012

# Start the service
CMD ["python", "main.py"]
