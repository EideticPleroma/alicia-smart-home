const Joi = require('joi');

// Input validation schemas
const schemas = {
  // Service configuration validation
  serviceConfig: Joi.object({
    name: Joi.string().min(1).max(100).required()
      .pattern(/^[a-zA-Z0-9_-]+$/)
      .messages({
        'string.pattern.base': 'Service name must contain only letters, numbers, hyphens, and underscores'
      }),
    status: Joi.string().valid('healthy', 'unhealthy', 'unknown').required(),
    uptime: Joi.string().optional(),
    latency: Joi.string().optional(),
    timestamp: Joi.date().iso().optional(),
    error: Joi.string().max(500).optional(),
    details: Joi.object().optional(),
    subscribedTopics: Joi.array().items(Joi.string()).optional(),
    publishedTopics: Joi.array().items(Joi.string()).optional()
  }),

  // MQTT message validation
  mqttMessage: Joi.object({
    topic: Joi.string().min(1).max(200).required()
      .pattern(/^alicia\/[a-zA-Z0-9_\/]+$/)
      .messages({
        'string.pattern.base': 'Topic must start with "alicia/" and contain only valid characters'
      }),
    timestamp: Joi.date().iso().required(),
    data: Joi.object().required(),
    messageId: Joi.string().uuid().optional(),
    source: Joi.string().optional(),
    destination: Joi.string().optional()
  }),

  // Health check validation
  healthCheck: Joi.object({
    service: Joi.string().min(1).max(100).required(),
    status: Joi.string().valid('healthy', 'unhealthy', 'unknown').required(),
    timestamp: Joi.date().iso().required(),
    uptime: Joi.string().optional(),
    version: Joi.string().optional(),
    details: Joi.object().optional()
  }),

  // API request validation
  apiRequest: Joi.object({
    limit: Joi.number().integer().min(1).max(1000).optional(),
    offset: Joi.number().integer().min(0).optional(),
    filter: Joi.string().max(100).optional(),
    sortBy: Joi.string().valid('name', 'status', 'timestamp', 'uptime').optional(),
    sortOrder: Joi.string().valid('asc', 'desc').optional()
  })
};

// Validation middleware factory
const createValidationMiddleware = (schemaName, property = 'body') => {
  return (req, res, next) => {
    const schema = schemas[schemaName];

    if (!schema) {
      return res.status(500).json({
        error: true,
        message: `Validation schema '${schemaName}' not found`
      });
    }

    const { error, value } = schema.validate(req[property], {
      abortEarly: false, // Collect all validation errors
      stripUnknown: true, // Remove unknown properties
      convert: true // Convert types where possible
    });

    if (error) {
      const errorDetails = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message,
        value: detail.context?.value
      }));

      return res.status(400).json({
        error: true,
        message: 'Validation failed',
        details: errorDetails,
        timestamp: new Date().toISOString()
      });
    }

    // Replace request data with validated/sanitized data
    req[property] = value;
    next();
  };
};

// Specific validation middlewares
const validateServiceConfig = createValidationMiddleware('serviceConfig');
const validateMqttMessage = createValidationMiddleware('mqttMessage');
const validateHealthCheck = createValidationMiddleware('healthCheck');
const validateApiRequest = createValidationMiddleware('apiRequest', 'query');

// Custom sanitization middleware
const sanitizeInput = (req, res, next) => {
  // Sanitize string inputs to prevent XSS
  const sanitizeString = (str) => {
    if (typeof str !== 'string') return str;
    return str
      .replace(/</g, '<')
      .replace(/>/g, '>')
      .replace(/"/g, '"')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  };

  // Recursively sanitize object properties
  const sanitizeObject = (obj) => {
    if (typeof obj === 'string') {
      return sanitizeString(obj);
    } else if (Array.isArray(obj)) {
      return obj.map(item => sanitizeObject(item));
    } else if (obj && typeof obj === 'object') {
      const sanitized = {};
      for (const [key, value] of Object.entries(obj)) {
        sanitized[key] = sanitizeObject(value);
      }
      return sanitized;
    }
    return obj;
  };

  // Sanitize request body, query, and params
  if (req.body && typeof req.body === 'object') {
    req.body = sanitizeObject(req.body);
  }

  if (req.query && typeof req.query === 'object') {
    req.query = sanitizeObject(req.query);
  }

  if (req.params && typeof req.params === 'object') {
    req.params = sanitizeObject(req.params);
  }

  next();
};

// Content type validation
const validateContentType = (allowedTypes = ['application/json']) => {
  return (req, res, next) => {
    const contentType = req.headers['content-type'];

    if (!contentType) {
      return res.status(400).json({
        error: true,
        message: 'Content-Type header is required'
      });
    }

    const isAllowed = allowedTypes.some(type =>
      contentType.toLowerCase().includes(type.toLowerCase())
    );

    if (!isAllowed) {
      return res.status(415).json({
        error: true,
        message: `Content-Type '${contentType}' is not supported. Allowed types: ${allowedTypes.join(', ')}`
      });
    }

    next();
  };
};

// Request size limit validation
const validateRequestSize = (maxSize = '10mb') => {
  return (req, res, next) => {
    const contentLength = parseInt(req.headers['content-length']);

    if (contentLength && contentLength > parseSize(maxSize)) {
      return res.status(413).json({
        error: true,
        message: `Request size exceeds limit of ${maxSize}`
      });
    }

    next();
  };
};

// Helper function to parse size strings
const parseSize = (size) => {
  const units = {
    b: 1,
    kb: 1024,
    mb: 1024 * 1024,
    gb: 1024 * 1024 * 1024
  };

  const match = size.toLowerCase().match(/^(\d+(?:\.\d+)?)\s*(b|kb|mb|gb)?$/);
  if (!match) return 1024 * 1024 * 10; // Default 10MB

  const value = parseFloat(match[1]);
  const unit = match[2] || 'b';

  return Math.floor(value * units[unit]);
};

module.exports = {
  createValidationMiddleware,
  validateServiceConfig,
  validateMqttMessage,
  validateHealthCheck,
  validateApiRequest,
  sanitizeInput,
  validateContentType,
  validateRequestSize
};
