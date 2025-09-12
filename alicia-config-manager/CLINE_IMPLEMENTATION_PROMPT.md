# Cline Implementation Prompt: Alicia Configuration Manager

## Project Overview
Create a **separate** configuration management web application for the Alicia Smart Home AI Assistant Docker microservices ecosystem. This is **NOT** part of the existing alicia-monitor - it's a completely independent application that provides configuration management capabilities.

## Phase 1: Project Foundation and Setup

### 1.1 Project Structure
Create the following directory structure:

```
alicia-config-manager/
├── .clinerules                    # Cline rules (already provided)
├── package.json                   # Root package.json for workspace
├── docker-compose.yml             # Docker configuration
├── .env.example                   # Environment variables template
├── README.md                      # Project documentation
├── frontend/                      # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       ├── hooks/
│       ├── services/
│       ├── types/
│       └── utils/
├── backend/                       # Node.js backend
│   ├── package.json
│   ├── src/
│   │   ├── index.js
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   └── Dockerfile
└── config/                        # Configuration files (Docker volumes)
    ├── config.json
    └── devices.json
```

### 1.2 Package.json Dependencies

**Root package.json:**
```json
{
  "name": "alicia-config-manager",
  "version": "1.0.0",
  "private": true,
  "workspaces": ["frontend", "backend"],
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && npm run dev",
    "build": "npm run build:frontend && npm run build:backend",
    "build:frontend": "cd frontend && npm run build",
    "build:backend": "cd backend && npm run build",
    "start": "concurrently \"npm run start:backend\" \"npm run start:frontend\"",
    "start:frontend": "cd frontend && npm run start",
    "start:backend": "cd backend && npm run start"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
```

**Frontend package.json:**
```json
{
  "name": "alicia-config-manager-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "start": "vite preview --port 3002"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "reactflow": "^11.10.1",
    "socket.io-client": "^4.7.0",
    "axios": "^1.6.0",
    "react-hook-form": "^7.45.0",
    "react-hot-toast": "^2.4.0",
    "lucide-react": "^0.263.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^1.14.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@tailwindcss/forms": "^0.5.0"
  }
}
```

**Backend package.json:**
```json
{
  "name": "alicia-config-manager-backend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "nodemon src/index.js",
    "start": "node src/index.js",
    "build": "echo 'No build step required for Node.js'"
  },
  "dependencies": {
    "express": "^4.18.2",
    "socket.io": "^4.7.0",
    "mqtt": "^5.1.0",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "express-rate-limit": "^6.8.0",
    "joi": "^17.9.0",
    "winston": "^3.10.0",
    "fs-extra": "^11.1.0",
    "chokidar": "^3.5.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0"
  }
}
```

### 1.3 Docker Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  alicia-config-manager:
    build: .
    ports:
      - "3002:3000"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - NODE_ENV=production
      - MQTT_BROKER=alicia_mqtt
      - MQTT_PORT=1883
      - MQTT_USERNAME=config_manager
      - MQTT_PASSWORD=alicia_config_2024
      - CONFIG_PATH=/app/config
    depends_on:
      - alicia_mqtt
    networks:
      - alicia_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  alicia_network:
    external: true
```

**Backend Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY backend/package*.json ./
RUN npm ci --only=production

# Copy source code
COPY backend/src ./src

# Create config and logs directories
RUN mkdir -p /app/config /app/logs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start application
CMD ["node", "src/index.js"]
```

### 1.4 TypeScript Configuration

**frontend/tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 1.5 Vite Configuration

**frontend/vite.config.ts:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3002,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

## Phase 2: Backend Implementation

### 2.1 Main Server File

**backend/src/index.js:**
```javascript
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import winston from 'winston';
import configRoutes from './routes/config.js';
import deviceRoutes from './routes/devices.js';
import systemRoutes from './routes/system.js';
import { MQTTService } from './services/mqtt.js';
import { ConfigService } from './services/config.js';
import { DeviceService } from './services/device.js';

// Logger configuration
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

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

### 2.2 MQTT Service

**backend/src/services/mqtt.js:**
```javascript
import mqtt from 'mqtt';
import winston from 'winston';

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

### 2.3 Configuration Service

**backend/src/services/config.js:**
```javascript
import fs from 'fs-extra';
import path from 'path';
import Joi from 'joi';
import winston from 'winston';

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
        // Create default config file
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
      },
      'tts-service': {
        service_name: 'tts-service',
        service_type: 'tts',
        status: 'unknown',
        enabled: true,
        version: '1.0.0',
        last_updated: new Date().toISOString(),
        config: {
          api_key: '',
          provider: 'elevenlabs',
          voice: 'ara-female-2',
          language: 'en-US',
          endpoints: [{
            type: 'tts',
            provider: 'elevenlabs',
            ip: 'http://tts:8002',
            port: 8002,
            protocol: 'http'
          }],
          settings: {
            stability: 0.5,
            similarity_boost: 0.75,
            style: 0.0,
            use_speaker_boost: true
          }
        }
      },
      'grok-service': {
        service_name: 'grok-service',
        service_type: 'llm',
        status: 'unknown',
        enabled: true,
        version: '1.0.0',
        last_updated: new Date().toISOString(),
        config: {
          api_key: '',
          provider: 'xai',
          model: 'grok-1.5',
          temperature: 0.7,
          max_tokens: 1000,
          endpoints: [{
            type: 'llm',
            model: 'grok-1.5',
            ip: 'http://grok:8003',
            port: 8003,
            protocol: 'http'
          }],
          settings: {
            stream: true,
            timeout: 60,
            retry_attempts: 3,
            conversation_memory: true
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
      // Validate configuration
      const { error, value } = CONFIG_SCHEMA.validate(config);
      if (error) {
        throw new Error(`Configuration validation failed: ${error.details[0].message}`);
      }

      // Update configuration
      this.configs.set(serviceName, value);
      
      // Save to file
      await this.saveConfigs(this.getAllConfigs());
      
      this.logger.info(`Configuration updated for ${serviceName}`);
      return value;
    } catch (error) {
      this.logger.error(`Error updating configuration for ${serviceName}:`, error);
      throw error;
    }
  }

  async deleteConfig(serviceName) {
    try {
      if (this.configs.has(serviceName)) {
        this.configs.delete(serviceName);
        await this.saveConfigs(this.getAllConfigs());
        this.logger.info(`Configuration deleted for ${serviceName}`);
        return true;
      }
      return false;
    } catch (error) {
      this.logger.error(`Error deleting configuration for ${serviceName}:`, error);
      throw error;
    }
  }

  maskApiKey(apiKey) {
    if (!apiKey || apiKey.length < 8) return apiKey;
    return apiKey.substring(0, 4) + 'x'.repeat(apiKey.length - 8) + apiKey.substring(apiKey.length - 4);
  }
}
```

## Phase 3: Frontend Implementation

### 3.1 Main App Component

**frontend/src/App.tsx:**
```typescript
import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { ServiceGraph } from './components/ServiceGraph';
import { ConfigModal } from './components/ConfigModal';
import { DeviceManager } from './components/DeviceManager';
import { ReloadButton } from './components/ReloadButton';
import { StatusBar } from './components/StatusBar';
import { useSocket } from './hooks/useSocket';
import { useConfig } from './hooks/useConfig';
import { useDevices } from './hooks/useDevices';
import { ServiceConfig, Device } from './types';
import './App.css';

function App() {
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [isDeviceManagerOpen, setIsDeviceManagerOpen] = useState(false);

  const { isConnected, emit } = useSocket();
  const { configs, updateConfig, reloadConfigs } = useConfig();
  const { devices, addDevice, updateDevice, deleteDevice } = useDevices();

  const handleServiceClick = (serviceName: string) => {
    setSelectedService(serviceName);
    setIsConfigModalOpen(true);
  };

  const handleConfigSave = async (serviceName: string, config: ServiceConfig) => {
    try {
      await updateConfig(serviceName, config);
      setIsConfigModalOpen(false);
      setSelectedService(null);
    } catch (error) {
      console.error('Failed to save configuration:', error);
    }
  };

  const handleReload = async () => {
    try {
      await reloadConfigs();
    } catch (error) {
      console.error('Failed to reload configurations:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">Alicia Config Manager</h1>
            </div>
            <div className="flex items-center space-x-4">
              <StatusBar 
                isConnected={isConnected}
                serviceCount={Object.keys(configs).length}
                deviceCount={devices.length}
              />
              <ReloadButton onReload={handleReload} />
              <button
                onClick={() => setIsDeviceManagerOpen(true)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm font-medium transition-colors"
              >
                Manage Devices
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <ServiceGraph
          services={configs}
          devices={devices}
          onServiceClick={handleServiceClick}
        />
      </main>

      {/* Modals */}
      {isConfigModalOpen && selectedService && (
        <ConfigModal
          serviceName={selectedService}
          config={configs[selectedService]}
          onSave={(config) => handleConfigSave(selectedService, config)}
          onClose={() => {
            setIsConfigModalOpen(false);
            setSelectedService(null);
          }}
        />
      )}

      {isDeviceManagerOpen && (
        <DeviceManager
          devices={devices}
          onAddDevice={addDevice}
          onUpdateDevice={updateDevice}
          onDeleteDevice={deleteDevice}
          onClose={() => setIsDeviceManagerOpen(false)}
        />
      )}
    </div>
  );
}

export default App;
```

### 3.2 Service Graph Component

**frontend/src/components/ServiceGraph.tsx:**
```typescript
import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  NodeTypes,
  EdgeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { ServiceNode } from './ServiceNode';
import { MessageEdge } from './MessageEdge';
import { ServiceConfig, Device } from '../types';

interface ServiceGraphProps {
  services: Record<string, ServiceConfig>;
  devices: Device[];
  onServiceClick: (serviceName: string) => void;
}

const nodeTypes: NodeTypes = {
  serviceNode: ServiceNode,
};

const edgeTypes: EdgeTypes = {
  messageEdge: MessageEdge,
};

export const ServiceGraph: React.FC<ServiceGraphProps> = ({
  services,
  devices,
  onServiceClick,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Convert services to React Flow nodes
  const serviceNodes = useMemo(() => {
    return Object.entries(services).map(([serviceName, serviceData], index) => {
      const x = (index % 4) * 300 + 100;
      const y = Math.floor(index / 4) * 200 + 100;

      return {
        id: serviceName,
        type: 'serviceNode',
        position: { x, y },
        data: {
          ...serviceData,
          name: serviceName,
          onClick: () => onServiceClick(serviceName),
        },
      } as Node;
    });
  }, [services, onServiceClick]);

  // Convert devices to React Flow nodes
  const deviceNodes = useMemo(() => {
    return devices.map((device, index) => {
      const x = 1200 + (index % 2) * 300;
      const y = 100 + Math.floor(index / 2) * 200;

      return {
        id: `device-${device.device_id}`,
        type: 'serviceNode',
        position: { x, y },
        data: {
          ...device,
          name: device.device_name,
          service_type: 'device',
          onClick: () => {}, // Devices don't have config modals
        },
      } as Node;
    });
  }, [devices]);

  // Create edges between services
  const serviceEdges = useMemo(() => {
    const edges: Edge[] = [];
    const serviceNames = Object.keys(services);
    
    // Create connections based on service types
    serviceNames.forEach((source, index) => {
      const target = serviceNames[(index + 1) % serviceNames.length];
      if (source !== target) {
        edges.push({
          id: `${source}-${target}`,
          source,
          target,
          type: 'messageEdge',
          animated: true,
          data: {
            messageCount: Math.floor(Math.random() * 10) + 1,
            lastMessage: new Date().toISOString(),
          },
        });
      }
    });

    return edges;
  }, [services]);

  // Update nodes when data changes
  React.useEffect(() => {
    setNodes([...serviceNodes, ...deviceNodes]);
  }, [serviceNodes, deviceNodes, setNodes]);

  React.useEffect(() => {
    setEdges(serviceEdges);
  }, [serviceEdges, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="w-full h-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        attributionPosition="top-right"
      >
        <Controls />
        <MiniMap />
        <Background color="#374151" gap={16} />
      </ReactFlow>
    </div>
  );
};
```

### 3.3 Custom Hooks

**frontend/src/hooks/useSocket.ts:**
```typescript
import { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

export const useSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    const newSocket = io(import.meta.env.VITE_API_URL || 'http://localhost:3001', {
      transports: ['websocket'],
      timeout: 20000,
    });

    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to server');
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    });

    newSocket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setIsConnected(false);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const emit = (event: string, data?: any) => {
    if (socket && isConnected) {
      socket.emit(event, data);
    }
  };

  const on = (event: string, callback: (data: any) => void) => {
    if (socket) {
      socket.on(event, callback);
    }
  };

  const off = (event: string, callback?: (data: any) => void) => {
    if (socket) {
      socket.off(event, callback);
    }
  };

  return {
    isConnected,
    socket,
    emit,
    on,
    off,
  };
};
```

**frontend/src/hooks/useConfig.ts:**
```typescript
import { useState, useEffect } from 'react';
import { useSocket } from './useSocket';
import { ServiceConfig } from '../types';
import { api } from '../services/api';

export const useConfig = () => {
  const [configs, setConfigs] = useState<Record<string, ServiceConfig>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { on, off } = useSocket();

  useEffect(() => {
    loadConfigs();
  }, []);

  useEffect(() => {
    const handleConfigUpdate = (data: Record<string, ServiceConfig>) => {
      setConfigs(data);
    };

    on('config:update', handleConfigUpdate);

    return () => {
      off('config:update', handleConfigUpdate);
    };
  }, [on, off]);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      const response = await api.get('/config');
      setConfigs(response.data);
    } catch (err) {
      setError('Failed to load configurations');
      console.error('Error loading configs:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = async (serviceName: string, config: ServiceConfig) => {
    try {
      const response = await api.patch(`/config/${serviceName}`, config);
      setConfigs(prev => ({
        ...prev,
        [serviceName]: response.data
      }));
      return response.data;
    } catch (err) {
      setError('Failed to update configuration');
      throw err;
    }
  };

  const reloadConfigs = async () => {
    try {
      await api.post('/config/reload');
      await loadConfigs();
    } catch (err) {
      setError('Failed to reload configurations');
      throw err;
    }
  };

  return {
    configs,
    loading,
    error,
    updateConfig,
    reloadConfigs,
  };
};
```

## Phase 4: Type Definitions

**frontend/src/types/index.ts:**
```typescript
export interface ServiceConfig {
  service_name: string;
  service_type: 'stt' | 'tts' | 'llm' | 'device_control' | 'voice_router';
  status: 'healthy' | 'unhealthy' | 'unknown';
  enabled: boolean;
  version: string;
  last_updated: string;
  config: {
    api_key?: string;
    provider?: string;
    model?: string;
    voice?: string;
    language?: string;
    temperature?: number;
    max_tokens?: number;
    endpoints: Array<{
      type: string;
      model?: string;
      ip: string;
      port?: number;
      protocol?: 'http' | 'https' | 'tcp' | 'udp';
    }>;
    settings?: Record<string, any>;
  };
}

export interface Device {
  device_id: string;
  device_name: string;
  device_type: 'external_api' | 'local_service' | 'hardware';
  status: 'online' | 'offline' | 'unknown';
  last_seen: string;
  connection: {
    host: string;
    port: number;
    protocol: 'http' | 'https' | 'tcp' | 'udp' | 'mqtt';
    authentication: {
      type: 'api_key' | 'oauth' | 'basic' | 'certificate';
      credentials: Record<string, any>;
    };
  };
  capabilities: string[];
  metadata: Record<string, any>;
}

export interface MQTTMessage {
  topic: string;
  data: any;
  timestamp: string;
}
```

## Phase 5: Environment Configuration

**.env.example:**
```env
# Backend Configuration
NODE_ENV=development
PORT=3000
CONFIG_PATH=./config

# MQTT Configuration
MQTT_BROKER=alicia_mqtt
MQTT_PORT=1883
MQTT_USERNAME=config_manager
MQTT_PASSWORD=alicia_config_2024

# Frontend Configuration
VITE_API_URL=http://localhost:3001
VITE_SOCKET_URL=http://localhost:3001

# Logging
LOG_LEVEL=info
LOG_FILE=logs/combined.log
ERROR_LOG_FILE=logs/error.log
```

## Implementation Instructions

1. **Create the project structure** as shown above
2. **Install dependencies** using the provided package.json files
3. **Set up environment variables** using the .env.example template
4. **Implement each phase** in order, following the code snippets provided
5. **Test each phase** before moving to the next
6. **Use Docker Compose** to run the complete application
7. **Follow the .clinerules** for code quality and architecture

This implementation provides a complete, production-ready configuration management application that is separate from the existing monitoring system while integrating seamlessly with the Alicia microservices ecosystem.

