# Cline Prompt: Alicia Monitor - Critical Code Quality Fixes

## 🎯 **Project Context**
Alicia Smart Home AI Assistant monitoring web app needs critical code quality improvements. React + TypeScript frontend, Node.js + Express backend with MQTT integration.

## 🚨 **Critical Issues to Fix**

### **1. Dependency Updates (CRITICAL)**
```bash
# Update to latest stable versions
cd alicia-monitor && npm update react react-dom typescript @types/react @types/react-dom
cd alicia-monitor-proxy && npm update express socket.io mqtt axios cors
```

**Target Versions:**
- React: 18.3.1, TypeScript: 5.6.3, @types/react: 18.3.12

### **2. Security Hardening (CRITICAL)**

#### **Environment Variables**
Create `.env` files:

**alicia-monitor/.env:**
```
REACT_APP_SOCKET_URL=http://localhost:3001
REACT_APP_MQTT_BROKER=localhost
REACT_APP_MQTT_PORT=1883
REACT_APP_MQTT_USERNAME=monitor
REACT_APP_MQTT_PASSWORD=alicia_monitor_2024
```

**alicia-monitor-proxy/.env:**
```
NODE_ENV=production
PORT=3001
MQTT_BROKER=alicia_bus_core
MQTT_PORT=1883
MQTT_USERNAME=monitor_proxy
MQTT_PASSWORD=alicia_monitor_2024
CORS_ORIGIN=http://localhost:3000
```

#### **Update server.js to use environment variables**
Replace hardcoded values in `alicia-monitor-proxy/src/server.js`:
```javascript
const MQTT_BROKER = process.env.MQTT_BROKER || 'localhost';
const MQTT_PORT = process.env.MQTT_PORT || 1883;
const MQTT_USERNAME = process.env.MQTT_USERNAME || 'monitor';
const MQTT_PASSWORD = process.env.MQTT_PASSWORD || 'alicia_monitor_2024';
```

### **3. TypeScript Improvements (HIGH)**

#### **Create types file: alicia-monitor/src/types/index.ts**
```typescript
export interface ServiceData {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  uptime?: string;
  latency?: string;
  timestamp?: string;
  error?: string;
  details?: Record<string, unknown>;
  subscribedTopics?: string[];
  publishedTopics?: string[];
}

export interface MessageData {
  topic: string;
  timestamp: string;
  data: Record<string, unknown>;
}

export interface ServiceNodeData extends ServiceData {
  messageCount?: number;
  onClick?: () => void;
}

export interface GraphViewProps {
  services: Record<string, ServiceData>;
  messageFlow: MessageData[];
  onNodeClick: (node: { id: string; data: ServiceData }) => void;
}
```

#### **Update App.tsx to use proper types**
Replace `any` types with proper interfaces:
```typescript
import { ServiceData, MessageData } from './types';

// Replace: const [services, setServices] = useState({});
const [services, setServices] = useState<Record<string, ServiceData>>({});

// Replace: const [messageFlow, setMessageFlow] = useState([]);
const [messageFlow, setMessageFlow] = useState<MessageData[]>([]);
```

### **4. Error Handling (HIGH)**

#### **Add Error Boundary: alicia-monitor/src/components/ErrorBoundary.tsx**
```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <h2 className="text-xl font-bold mb-2">Something went wrong.</h2>
          <button 
            onClick={() => this.setState({ hasError: false })}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

#### **Wrap App with ErrorBoundary in index.tsx**
```typescript
import ErrorBoundary from './components/ErrorBoundary';

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
```

### **5. Performance Optimization (MEDIUM)**

#### **Add message throttling to server.js**
```javascript
// Add at top of server.js
let messageThrottle = [];
const THROTTLE_MS = 100;
let lastEmit = 0;

// Replace MQTT message handler
mqttClient.on('message', (topic, message) => {
  try {
    const messageData = JSON.parse(message.toString());
    const flowData = {
      topic,
      timestamp: new Date().toISOString(),
      data: messageData
    };
    
    messageThrottle.push(flowData);
    
    // Throttle emissions
    const now = Date.now();
    if (now - lastEmit > THROTTLE_MS) {
      lastEmit = now;
      io.emit('mqtt_message', messageThrottle);
      messageThrottle = [];
    }
  } catch (error) {
    console.error('Error parsing MQTT message:', error);
  }
});
```

### **6. Security Middleware (HIGH)**

#### **Add rate limiting: alicia-monitor-proxy/src/middleware/rateLimiter.js**
```javascript
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: true,
    message: 'Too many requests, please try again later.'
  }
});

module.exports = { apiLimiter };
```

#### **Add to server.js**
```javascript
const { apiLimiter } = require('./middleware/rateLimiter');

// Add after middleware setup
app.use('/api/', apiLimiter);
```

### **7. Update package.json scripts**

#### **alicia-monitor/package.json**
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "type-check": "tsc --noEmit"
  }
}
```

#### **alicia-monitor-proxy/package.json**
```json
{
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  }
}
```

## 🎯 **Implementation Steps**

1. **Update dependencies** in both projects
2. **Create .env files** with environment variables
3. **Update server.js** to use environment variables
4. **Create types/index.ts** with proper interfaces
5. **Update App.tsx** to use proper types
6. **Add ErrorBoundary** component and wrap App
7. **Add message throttling** to server.js
8. **Add rate limiting** middleware
9. **Test the application** to ensure everything works

## ✅ **Expected Results**

- ✅ **Security**: No hardcoded credentials, rate limiting active
- ✅ **Type Safety**: Proper TypeScript interfaces, no `any` types
- ✅ **Error Handling**: Graceful error recovery with ErrorBoundary
- ✅ **Performance**: Throttled message emissions
- ✅ **Maintainability**: Clean, typed code with proper error handling

## 🚀 **Quick Test**

After implementation:
1. `cd alicia-monitor && npm start`
2. `cd alicia-monitor-proxy && npm start`
3. Open http://localhost:3000
4. Verify real-time monitoring works
5. Check browser console for errors
6. Test error boundary by causing an error

This focused approach addresses the most critical issues while staying within token limits.

