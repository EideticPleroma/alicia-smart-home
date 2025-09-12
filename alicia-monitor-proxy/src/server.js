const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const mqtt = require('mqtt');
const axios = require('axios');
const compression = require('compression');
const ServiceDiscovery = require('./serviceDiscovery');

// Import security middlewares
const { corsMiddleware } = require('./middleware/cors');
const { createSecurityMiddleware } = require('./middleware/securityHeaders');
const { apiLimiter } = require('./middleware/rateLimiter');
const { sanitizeInput, validateContentType } = require('./middleware/validation');

// Import performance middlewares
const { messageThrottleMiddleware, createSocketRateLimit, createMessageDebouncer } = require('./middleware/messageThrottling');
const { HealthCache, createCachedHealthChecker, createBatchHealthChecker } = require('./middleware/healthCache');
const { MessageStorage } = require('./middleware/messageStorage');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.NODE_ENV === 'production'
      ? (process.env.CORS_ORIGINS?.split(',') || [])
      : ["http://localhost:3000", "http://127.0.0.1:3000"],
    methods: ["GET", "POST"],
    credentials: true
  }
});

// Performance Middleware (Order matters!)
app.use(compression()); // Response compression first

// Security Middleware (Order matters!)
app.use(createSecurityMiddleware()); // Security headers first
app.use(corsMiddleware); // CORS configuration
app.use(apiLimiter); // Rate limiting
app.use(express.json({ limit: '10mb' })); // JSON parsing with size limit
app.use(sanitizeInput); // Input sanitization

// MQTT Configuration
const MQTT_BROKER = process.env.MQTT_BROKER || 'localhost';
const MQTT_PORT = process.env.MQTT_PORT || 1883;
const MQTT_USERNAME = process.env.MQTT_USERNAME || 'monitor';
const MQTT_PASSWORD = process.env.MQTT_PASSWORD || 'alicia_monitor_2024';

// Initialize service discovery
const serviceDiscovery = new ServiceDiscovery();
let services = [];

// Store service health data
let serviceHealth = {};
let messageFlow = [];

// Initialize performance middlewares
const messageThrottler = messageThrottleMiddleware(io);
const socketRateLimiter = createSocketRateLimit(io);
const messageDebouncer = createMessageDebouncer(io);

// Initialize health cache
const healthCache = new HealthCache(30000); // 30 second TTL
const cachedHealthChecker = createCachedHealthChecker(axios, healthCache);

// MQTT Client
const mqttClient = mqtt.connect(`mqtt://${MQTT_BROKER}:${MQTT_PORT}`, {
  username: MQTT_USERNAME,
  password: MQTT_PASSWORD,
  clientId: 'alicia-monitor-proxy'
});

// MQTT event handlers
mqttClient.on('connect', () => {
  console.log('Connected to MQTT broker');
  mqttClient.subscribe('alicia/#', (err) => {
    if (!err) {
      console.log('Subscribed to alicia/#');
    }
  });
});

mqttClient.on('message', (topic, message) => {
  try {
    const messageData = JSON.parse(message.toString());
    console.log(`MQTT Message: ${topic}`, messageData);

    // Check message debouncing
    if (!messageDebouncer(topic, messageData)) {
      return; // Skip duplicate message
    }

    // Track message flow
    const flowData = {
      topic,
      timestamp: new Date().toISOString(),
      data: messageData
    };
    messageFlow.push(flowData);

    // Keep only last 100 messages
    if (messageFlow.length > 100) {
      messageFlow = messageFlow.slice(-100);
    }

    // Use throttled message broadcasting
    messageThrottler.throttleMessage('mqtt_message', flowData);
  } catch (error) {
    console.error('Error parsing MQTT message:', error);
  }
});

mqttClient.on('error', (error) => {
  console.error('MQTT connection error:', error);
});

// Health check function
async function checkServiceHealth(service) {
  if (service.type === 'mqtt') {
    // For MQTT broker, check if we can connect
    return {
      name: service.name,
      status: mqttClient.connected ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      uptime: mqttClient.connected ? 'Connected' : 'Disconnected'
    };
  }

  try {
    const response = await axios.get(`http://${service.host}:${service.port}${service.healthEndpoint}`, {
      timeout: 5000
    });

    return {
      name: service.name,
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: response.data.uptime || 'Unknown',
      latency: response.headers['x-response-time'] || 'Unknown',
      details: response.data
    };
  } catch (error) {
    return {
      name: service.name,
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    };
  }
}

// Health monitoring interval with caching
setInterval(async () => {
  const healthPromises = services.map(service => cachedHealthChecker(service));
  const healthResults = await Promise.all(healthPromises);

  // Update health data
  healthResults.forEach(result => {
    serviceHealth[result.name] = result;
  });

  // Emit health update to clients
  io.emit('health_update', serviceHealth);
}, 10000); // Check every 10 seconds

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Apply socket rate limiting
  const rateLimitCheck = socketRateLimiter(socket);
  if (!rateLimitCheck) {
    console.log('Socket rate limited:', socket.id);
    return; // Connection rejected due to rate limiting
  }

  // Send current health data on connection
  socket.emit('health_update', serviceHealth);
  socket.emit('message_flow', messageFlow);

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// API endpoints
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: serviceHealth
  });
});

app.get('/api/messages', (req, res) => {
  res.json({
    messages: messageFlow
  });
});

app.get('/api/services', (req, res) => {
  res.json({
    services: services,
    health: serviceHealth
  });
});

// Initialize service discovery on startup
async function initializeServices() {
  try {
    services = await serviceDiscovery.discoverServices();
    console.log(`Initialized with ${services.length} services`);
  } catch (error) {
    console.error('Failed to discover services:', error);
    console.log('Using default service configuration');
  }
}

// Start server
const PORT = process.env.PORT || 3002;
const HOST = process.env.HOST || '127.0.0.1';
server.listen(PORT, HOST, async () => {
  console.log(`Alicia Monitor Proxy server running on ${HOST}:${PORT}`);
  console.log(`React app should connect to http://${HOST}:${PORT}`);

  // Initialize service discovery
  await initializeServices();
});

module.exports = { app, server, io };
