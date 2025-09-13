# Alicia Bus Architecture - AI Service Dockerfile
# Python 3.11.7+, FastAPI 0.104.1+, OpenAI 1.3.0+

FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY service_wrapper.py .

# Create directories for conversation data
RUN mkdir -p /app/data /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash alicia && \
    chown -R alicia:alicia /app
USER alicia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8005/health')" || exit 1

# Expose port
EXPOSE 8005

# Start the service
CMD ["python", "main.py"]
