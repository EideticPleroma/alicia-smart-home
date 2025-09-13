# Alicia Config Manager Frontend - Development Dockerfile
# React + Vite + TypeScript development environment
FROM node:18-alpine

# Labels for better container management
LABEL maintainer="Alicia Smart Home AI Assistant"
LABEL description="Config Manager Frontend Development"
LABEL version="1.0.0"

# Set environment variables
ENV NODE_ENV=development
ENV VITE_API_URL=http://localhost:3000
ENV VITE_SOCKET_URL=http://localhost:3000

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
    adduser -S alicia-frontend -u 1001 -G alicia

# Copy package files
COPY --chown=alicia-frontend:alicia package*.json ./

# Install dependencies
RUN npm ci && \
    npm cache clean --force

# Copy source code
COPY --chown=alicia-frontend:alicia . .

# Switch to non-root user
USER alicia-frontend

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3002 || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
