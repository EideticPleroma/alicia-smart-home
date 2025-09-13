# Alicia Config Manager Backend - Development Dockerfile
# Node.js + Express + Socket.io development environment
FROM node:18-alpine

# Labels for better container management
LABEL maintainer="Alicia Smart Home AI Assistant"
LABEL description="Config Manager Backend Development"
LABEL version="1.0.0"

# Set environment variables
ENV NODE_ENV=development
ENV PORT=3000
ENV MQTT_BROKER=alicia_bus_core
ENV MQTT_PORT=1883
ENV MQTT_USERNAME=config_manager
ENV MQTT_PASSWORD=alicia_config_2024
ENV FRONTEND_URL=http://localhost:3002

# Install security updates and required packages
RUN apk update && apk upgrade && \
    apk add --no-cache \
    dumb-init \
    curl \
    && rm -rf /var/cache/apk/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S alicia && \
    adduser -S alicia-backend -u 1001 -G alicia

# Copy package files
COPY --chown=alicia-backend:alicia package*.json ./

# Install dependencies
RUN npm ci && \
    npm cache clean --force

# Copy source code
COPY --chown=alicia-backend:alicia src/ ./src/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R alicia-backend:alicia /app/logs /app/data

# Switch to non-root user
USER alicia-backend

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start development server
CMD ["npm", "run", "dev"]