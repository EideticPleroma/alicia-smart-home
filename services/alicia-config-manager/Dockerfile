# Alicia Config Manager - Main Dockerfile
# Multi-stage build for Node.js backend and React frontend
FROM node:18-alpine AS base

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
    adduser -S alicia-config -u 1001 -G alicia

# ===== BACKEND BUILD STAGE =====
FROM base AS backend-build

# Copy backend package files
COPY backend/package*.json ./backend/
WORKDIR /app/backend

# Install backend dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy backend source
COPY backend/src ./src

# ===== FRONTEND BUILD STAGE =====
FROM base AS frontend-build

# Copy frontend package files
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend

# Install frontend dependencies
RUN npm ci

# Copy frontend source
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html ./
COPY frontend/vite.config.ts ./
COPY frontend/tsconfig*.json ./
COPY frontend/tailwind.config.js ./
COPY frontend/postcss.config.js ./

# Build frontend
RUN npm run build

# ===== PRODUCTION STAGE =====
FROM base AS production

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV MQTT_BROKER=alicia_bus_core
ENV MQTT_PORT=1883
ENV MQTT_USERNAME=config_manager
ENV MQTT_PASSWORD=alicia_config_2024

# Copy backend from build stage
COPY --from=backend-build --chown=alicia-config:alicia /app/backend /app/backend

# Copy frontend build from build stage
COPY --from=frontend-build --chown=alicia-config:alicia /app/frontend/dist /app/frontend/dist

# Copy root package.json for workspace management
COPY --chown=alicia-config:alicia package*.json ./

# Install workspace dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy configuration files
COPY --chown=alicia-config:alicia config/ ./config/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R alicia-config:alicia /app/logs /app/data

# Switch to non-root user
USER alicia-config

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["npm", "start"]
