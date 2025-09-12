# Cline Phase 2: Backend Server Implementation

## 🎯 **Goal**
Create the Express server with MQTT integration and basic API endpoints.

## 📁 **Backend Structure**

```
backend/
├── package.json (already created)
├── src/
│   ├── index.js
│   ├── routes/
│   │   ├── config.js
│   │   ├── devices.js
│   │   └── system.js
│   ├── services/
│   │   ├── mqtt.js
│   │   ├── config.js
│   │   └── device.js
│   └── utils/
│       ├── logger.js
│       └── validation.js
└── Dockerfile
```

## 🚀 **Main Server File**

**backend/src/index.js:**
```javascript
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { logger } from './utils/logger.js';
import configRoutes from './routes/config.js';
import deviceRoutes from './routes/devices.js';
import systemRoutes from './routes/system.js';
import { MQTTService } from './services/mqtt.js';
import { ConfigService } from './services/config.js';
import { DeviceService } from './services/device.js';

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3002",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:3002",
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});
app.use('/api/', limiter);

// Initialize services
const mqttService = new MQTTService(logger);
const configService = new ConfigService(logger);
const deviceService = new DeviceService(logger);

// Routes
app.use('/api/config', configRoutes(configService, mqttService));
app.use('/api/devices', deviceRoutes(deviceService, mqttService));
app.use('/api/system', systemRoutes(mqttService));

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      mqtt: mqttService.isConnected(),
      config: configService.isReady(),
      device: deviceService.isReady()
    }
  });
});

// Socket.io connection handling
io.on('connection', (socket) => {
  logger.info(`Client connected: ${socket.id}`);
  
  // Send initial data
  socket.emit('config:update', configService.getAllConfigs());
  socket.emit('devices:update', deviceService.getAllDevices());
  
  socket.on('disconnect', () => {
    logger.info(`Client disconnected: ${socket.id}`);
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

const PORT = process.env.PORT || 3000;

// Start server
server.listen(PORT, async () => {
  logger.info(`Alicia Config Manager server running on port ${PORT}`);
  
  // Initialize services
  await mqttService.connect();
  await configService.initialize();
  await deviceService.initialize();
  
  logger.info('All services initialized successfully');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    mqttService.disconnect();
    process.exit(0);
  });
});

export { app, server, io };
```

## 🔧 **Logger Utility**

**backend/src/utils/logger.js:**
```javascript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ 
      filename: process.env.ERROR_LOG_FILE || 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: process.env.LOG_FILE || 'logs/combined.log' 
    }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

export { logger };
```

## 📡 **MQTT Service**

**backend/src/services/mqtt.js:**
```javascript
import mqtt from 'mqtt';
import { logger } from '../utils/logger.js';

export class MQTTService {
  constructor(logger) {
    this.logger = logger;
    this.client = null;
    this.isConnected = false;
    this.subscriptions = new Map();
  }

  async connect() {
    const brokerUrl = `mqtt://${process.env.MQTT_BROKER}:${process.env.MQTT_PORT}`;
    
    this.client = mqtt.connect(brokerUrl, {
      username: process.env.MQTT_USERNAME,
      password: process.env.MQTT_PASSWORD,
      clientId: 'alicia-config-manager',
      clean: true,
      reconnectPeriod: 5000,
      connectTimeout: 30 * 1000
    });

    this.client.on('connect', () => {
      this.isConnected = true;
      this.logger.info('Connected to MQTT broker');
      this.subscribeToTopics();
    });

    this.client.on('disconnect', () => {
      this.isConnected = false;
      this.logger.warn('Disconnected from MQTT broker');
    });

    this.client.on('error', (error) => {
      this.logger.error('MQTT connection error:', error);
    });

    this.client.on('message', (topic, message) => {
      this.handleMessage(topic, message);
    });
  }

  subscribeToTopics() {
    const topics = [
      'alicia/system/health/#',
      'alicia/system/discovery/#',
      'alicia/config/#',
      'alicia/device/#'
    ];

    topics.forEach(topic => {
      this.client.subscribe(topic, (err) => {
        if (err) {
          this.logger.error(`Failed to subscribe to ${topic}:`, err);
        } else {
          this.logger.info(`Subscribed to ${topic}`);
        }
      });
    });
  }

  handleMessage(topic, message) {
    try {
      const data = JSON.parse(message.toString());
      this.logger.debug(`MQTT message received on ${topic}:`, data);
      
      // Emit to connected Socket.io clients
      if (this.io) {
        this.io.emit('mqtt:message', { topic, data, timestamp: new Date().toISOString() });
      }
    } catch (error) {
      this.logger.error('Error parsing MQTT message:', error);
    }
  }

  publish(topic, message) {
    if (!this.isConnected) {
      this.logger.warn('MQTT not connected, cannot publish message');
      return false;
    }

    const payload = JSON.stringify(message);
    this.client.publish(topic, payload, (err) => {
      if (err) {
        this.logger.error(`Failed to publish to ${topic}:`, err);
      } else {
        this.logger.debug(`Published to ${topic}:`, message);
      }
    });
    return true;
  }

  setSocketIO(io) {
    this.io = io;
  }

  disconnect() {
    if (this.client) {
      this.client.end();
    }
  }
}
```

## ⚙️ **Configuration Service**

**backend/src/services/config.js:**
```javascript
import fs from 'fs-extra';
import path from 'path';
import Joi from 'joi';
import { logger } from '../utils/logger.js';

const CONFIG_SCHEMA = Joi.object({
  service_name: Joi.string().required(),
  service_type: Joi.string().valid('stt', 'tts', 'llm', 'device_control', 'voice_router').required(),
  status: Joi.string().valid('healthy', 'unhealthy', 'unknown').required(),
  enabled: Joi.boolean().required(),
  version: Joi.string().required(),
  last_updated: Joi.string().isoDate().required(),
  config: Joi.object({
    api_key: Joi.string().optional(),
    provider: Joi.string().optional(),
    model: Joi.string().optional(),
    voice: Joi.string().optional(),
    language: Joi.string().optional(),
    endpoints: Joi.array().items(Joi.object({
      type: Joi.string().required(),
      model: Joi.string().optional(),
      ip: Joi.string().required(),
      port: Joi.number().optional(),
      protocol: Joi.string().valid('http', 'https', 'tcp', 'udp').optional()
    })).required(),
    settings: Joi.object().optional()
  }).required()
});

export class ConfigService {
  constructor(logger) {
    this.logger = logger;
    this.configPath = path.join(process.env.CONFIG_PATH || './config', 'config.json');
    this.configs = new Map();
    this.isReady = false;
  }

  async initialize() {
    try {
      await this.loadConfigs();
      this.isReady = true;
      this.logger.info('Config service initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize config service:', error);
      throw error;
    }
  }

  async loadConfigs() {
    try {
      if (await fs.pathExists(this.configPath)) {
        const data = await fs.readJson(this.configPath);
        this.configs = new Map(Object.entries(data));
        this.logger.info(`Loaded ${this.configs.size} configurations`);
      } else {
        await this.createDefaultConfig();
      }
    } catch (error) {
      this.logger.error('Error loading configurations:', error);
      throw error;
    }
  }

  async createDefaultConfig() {
    const defaultConfigs = {
      'whisper-service': {
        service_name: 'whisper-service',
        service_type: 'stt',
        status: 'unknown',
        enabled: true,
        version: '1.0.0',
        last_updated: new Date().toISOString(),
        config: {
          api_key: '',
          provider: 'openai',
          model: 'whisper-1',
          language: 'en',
          endpoints: [{
            type: 'stt',
            model: 'whisper-1',
            ip: 'http://whisper:8001',
            port: 8001,
            protocol: 'http'
          }],
          settings: {
            temperature: 0.0,
            max_tokens: 1000,
            timeout: 30
          }
        }
      }
    };

    await this.saveConfigs(defaultConfigs);
    this.logger.info('Created default configuration file');
  }

  async saveConfigs(configs) {
    try {
      await fs.ensureDir(path.dirname(this.configPath));
      await fs.writeJson(this.configPath, configs, { spaces: 2 });
      this.logger.info('Configurations saved successfully');
    } catch (error) {
      this.logger.error('Error saving configurations:', error);
      throw error;
    }
  }

  getAllConfigs() {
    return Object.fromEntries(this.configs);
  }

  getConfig(serviceName) {
    return this.configs.get(serviceName) || null;
  }

  async updateConfig(serviceName, config) {
    try {
      const { error, value } = CONFIG_SCHEMA.validate(config);
      if (error) {
        throw new Error(`Configuration validation failed: ${error.details[0].message}`);
      }

      this.configs.set(serviceName, value);
      await this.saveConfigs(this.getAllConfigs());
      
      this.logger.info(`Configuration updated for ${serviceName}`);
      return value;
    } catch (error) {
      this.logger.error(`Error updating configuration for ${serviceName}:`, error);
      throw error;
    }
  }
}
```

## 🎯 **Implementation Steps**

1. **Create the backend directory structure** as shown
2. **Create all the service files** with the exact content provided
3. **Create the logger utility** for structured logging
4. **Test the server** by running `npm run dev` in the backend directory
5. **Verify MQTT connection** works with your existing broker

## ✅ **Verification**

After implementation, verify:
- [ ] Server starts without errors
- [ ] MQTT connection is established
- [ ] Health check endpoint responds
- [ ] Configuration service initializes
- [ ] Socket.io connection works

**Next Phase**: Frontend React application

