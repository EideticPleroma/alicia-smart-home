import 'dotenv/config';
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
import envConfigRoutes from './routes/envConfig.js';
import { MQTTService } from './services/mqtt.js';
import { ConfigService } from './services/config.js';
import { DeviceService } from './services/device.js';
import { EnvConfigService } from './services/envConfig.js';

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
const envConfigService = new EnvConfigService(logger);

// Set Socket.io reference for MQTT service
mqttService.setSocketIO(io);

// Set services in app for middleware access
app.set('mqttService', mqttService);
app.set('configService', configService);
app.set('deviceService', deviceService);
app.set('envConfigService', envConfigService);
app.set('io', io);

// Routes
app.use('/api/config', configRoutes);
app.use('/api/devices', deviceRoutes);
app.use('/api/system', systemRoutes);
app.use('/api/env', envConfigRoutes);

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
const HOST = process.env.NODE_ENV === 'production' ? '0.0.0.0' : 'localhost';

// Start server
server.listen(PORT, HOST, async () => {
  logger.info(`Alicia Config Manager server running on port ${PORT}`);

  // Initialize services
  await mqttService.connect();
  await configService.initialize();
  await deviceService.initialize();
  await envConfigService.initialize();

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
