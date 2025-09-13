# Alicia Bus Architecture - Sonos Service Dockerfile
# Python 3.11.7+, SoCo 0.29+, FastAPI 0.104.1+

FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio and networking
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY service_wrapper.py .

# Create directories for audio and data
RUN mkdir -p /app/audio /app/data /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash alicia && \
    chown -R alicia:alicia /app
USER alicia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8017/health || exit 1

# Expose port
EXPOSE 8017

# Start the service
CMD ["python", "main.py"]
