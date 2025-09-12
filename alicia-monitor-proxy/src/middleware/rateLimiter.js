const rateLimit = require('express-rate-limit');

// Create rate limiter middleware
const createRateLimiter = (windowMs, maxRequests, message = 'Too many requests, please try again later.') => {
  return rateLimit({
    windowMs, // Time window in milliseconds
    max: maxRequests, // Maximum number of requests per window
    message: {
      error: true,
      message,
      retryAfter: Math.ceil(windowMs / 1000)
    },
    standardHeaders: true, // Return rate limit info in `RateLimit-*` headers
    legacyHeaders: false, // Disable `X-RateLimit-*` headers
    // Skip rate limiting for health checks
    skip: (req) => req.path === '/health' || req.path === '/api/health',
    // Use IP address for rate limiting
    keyGenerator: (req) => {
      return req.ip || req.connection.remoteAddress;
    }
  });
};

// API rate limiter - General API endpoints
const apiLimiter = createRateLimiter(
  parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
  parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // 100 requests per 15 minutes
  'API rate limit exceeded. Please try again later.'
);

// Strict rate limiter for sensitive endpoints
const strictLimiter = createRateLimiter(
  5 * 60 * 1000, // 5 minutes
  20, // 20 requests per 5 minutes
  'Too many requests to sensitive endpoint. Please try again later.'
);

// WebSocket/Socket.io rate limiter
const socketLimiter = createRateLimiter(
  60 * 1000, // 1 minute
  30, // 30 requests per minute
  'Socket connection rate limit exceeded.'
);

// MQTT Message throttling limiter
const mqttMessageLimiter = createRateLimiter(
  1000, // 1 second
  50, // 50 MQTT messages per second
  'MQTT message rate limit exceeded.'
);

// Health check rate limiter (more permissive)
const healthLimiter = createRateLimiter(
  60 * 1000, // 1 minute
  120, // 120 health checks per minute
  'Health check rate limit exceeded.'
);

module.exports = {
  apiLimiter,
  strictLimiter,
  socketLimiter,
  mqttMessageLimiter,
  healthLimiter,
  createRateLimiter
};
