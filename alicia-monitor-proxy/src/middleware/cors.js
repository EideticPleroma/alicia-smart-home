const cors = require('cors');

// CORS configuration for different environments
const corsOptions = {
  // Development: Allow localhost origins
  development: {
    origin: function (origin, callback) {
      const allowedOrigins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3001'
      ];

      // Allow requests with no origin (mobile apps, etc.)
      if (!origin) return callback(null, true);

      if (allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error(`CORS policy violation: ${origin} not allowed`));
      }
    },
    credentials: true,
    optionsSuccessStatus: 200,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allowedHeaders: [
      'Content-Type',
      'Authorization',
      'X-Requested-With',
      'Accept',
      'Origin',
      'Access-Control-Request-Method',
      'Access-Control-Request-Headers'
    ],
    exposedHeaders: ['X-RateLimit-Remaining', 'X-RateLimit-Reset'],
    maxAge: 86400 // 24 hours
  },

  // Production: Strict CORS policy
  production: {
    origin: function (origin, callback) {
      const allowedOrigins = process.env.CORS_ORIGINS?.split(',') || [];

      // Allow requests with no origin (server-to-server, mobile apps)
      if (!origin) return callback(null, true);

      if (allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error(`CORS policy violation: ${origin} not allowed in production`));
      }
    },
    credentials: true,
    optionsSuccessStatus: 200,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: [
      'Content-Type',
      'Authorization',
      'X-Requested-With',
      'Accept'
    ],
    exposedHeaders: ['X-RateLimit-Remaining', 'X-RateLimit-Reset'],
    maxAge: 7200 // 2 hours
  },

  // Test: Allow all for testing
  test: {
    origin: true,
    credentials: true,
    optionsSuccessStatus: 200
  }
};

// Get CORS configuration based on environment
const getCorsConfig = () => {
  const env = process.env.NODE_ENV || 'development';
  return corsOptions[env] || corsOptions.development;
};

// Create CORS middleware
const corsMiddleware = cors(getCorsConfig());

module.exports = {
  corsMiddleware,
  getCorsConfig,
  corsOptions
};
