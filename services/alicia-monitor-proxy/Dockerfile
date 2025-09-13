# ===== ALICIA BUS ARCHITECTURE MONITOR PROXY =====
# Node.js 18 Alpine with security and performance optimizations
FROM node:18-alpine

# Labels for better container management
LABEL maintainer="Alicia Smart Home AI Assistant"
LABEL description="Bus Architecture Monitor Proxy Service"
LABEL version="1.0.0"

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3001
ENV MQTT_BROKER=alicia_bus_core
ENV MQTT_PORT=1883

# Install security updates and required packages
RUN apk update && apk upgrade && \
    apk add --no-cache \
    dumb-init \
    curl \
    && rm -rf /var/cache/apk/*

# Create app directory with proper permissions
WORKDIR /app

# Create non-root user and group
RUN addgroup -g 1001 -S alicia && \
    adduser -S alicia-monitor -u 1001 -G alicia

# Copy package files first for better caching
COPY --chown=alicia-monitor:alicia package*.json ./

# Install dependencies with security audit
RUN npm ci --only=production && \
    npm audit --audit-level=moderate && \
    npm cache clean --force

# Copy source code with proper ownership
COPY --chown=alicia-monitor:alicia src/ ./src/

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data && \
    chown -R alicia-monitor:alicia /app/logs /app/data

# Switch to non-root user
USER alicia-monitor

# Expose port
EXPOSE 3001

# Health check with improved error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3001/api/health || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["npm", "start"]
