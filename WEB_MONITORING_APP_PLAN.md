# Alicia Bus Architecture - Web Monitoring App Plan

## 🎯 **Project Overview**

Build a real-time, single-page web application that visualizes the Alicia Bus Architecture microservice ecosystem. The app will show live message flow between services, container health status, and provide detailed service information through an interactive graph interface.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React App     │    │  Node.js Proxy   │    │  Bus Services   │
│  (localhost:3000)│◄──►│  (Docker)        │◄──►│  (23 services)  │
│                 │    │                  │    │                 │
│ • React Flow    │    │ • Socket.io      │    │ • Health APIs   │
│ • Real-time UI  │    │ • HTTP polling   │    │ • MQTT topics   │
│ • Interactive   │    │ • MQTT monitor   │    │ • Heartbeats    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 **Technical Requirements**

### **Frontend (React)**
- **Framework**: React 18+ with hooks
- **Graph Library**: React Flow for node/edge visualization
- **Real-time**: Socket.io client for live updates
- **Styling**: Tailwind CSS for modern UI
- **State Management**: React Context + useReducer
- **Port**: localhost:3000

### **Backend (Node.js Proxy)**
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **Real-time**: Socket.io server
- **HTTP Client**: Axios for health checks
- **MQTT Client**: mqtt.js for bus monitoring
- **Deployment**: Docker container
- **Network**: host.docker.internal for service access

### **Data Flow**
1. **Health Polling**: Proxy polls each service `/health` every 10s
2. **MQTT Monitoring**: Proxy subscribes to all bus topics
3. **Real-time Updates**: Socket.io pushes updates to React app
4. **Graph Rendering**: React Flow renders nodes and edges
5. **Interactive UI**: Click nodes for detailed information

## 🎨 **UI/UX Design**

### **Main Interface**
- **Graph View**: Central React Flow canvas with auto-layout
- **Side Panel**: Collapsible details panel (right side)
- **Status Bar**: Top bar with overall system health
- **Controls**: Zoom, pan, reset view, toggle panel

### **Node Design**
- **Shape**: Circular nodes for services
- **Colors**: 
  - 🟢 Green: Healthy service
  - 🔴 Red: Unhealthy service
  - ⚪ Gray: Dead/disconnected service
- **Size**: Proportional to message volume
- **Animation**: Pulsing for active services

### **Edge Design**
- **Style**: Animated arrows showing message flow
- **Colors**:
  - 🟢 Green: Active message flow
  - ⚪ Gray: No recent messages
- **Animation**: Flowing particles along active edges
- **Thickness**: Proportional to message frequency

### **Side Panel Details**
- **Container Name**: Service identifier
- **Uptime**: Time since last restart
- **Last Heartbeat**: Timestamp of last health check
- **Health Status**: Green/red indicator
- **Subscribed Topics**: List of MQTT topics
- **Published Topics**: List of published topics
- **Latency**: Response time on hover
- **Message Count**: Total messages processed

## 🚀 **Implementation Plan**

### **Phase 1: Project Setup & Structure**

#### **1.1 Frontend Setup**
```bash
# Create React app
npx create-react-app alicia-monitor --template typescript
cd alicia-monitor

# Install dependencies
npm install reactflow socket.io-client tailwindcss
npm install @types/node axios
npm install -D @tailwindcss/forms
```

#### **1.2 Backend Setup**
```bash
# Create proxy server
mkdir alicia-monitor-proxy
cd alicia-monitor-proxy
npm init -y
npm install express socket.io mqtt axios cors
npm install -D nodemon @types/express
```

#### **1.3 Docker Configuration**
```dockerfile
# Dockerfile for proxy
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

### **Phase 2: Core Components**

#### **2.1 React Components Structure**
```
src/
├── components/
│   ├── GraphView.tsx          # Main React Flow component
│   ├── ServiceNode.tsx        # Individual service node
│   ├── MessageEdge.tsx        # Animated message flow edge
│   ├── SidePanel.tsx          # Service details panel
│   ├── StatusBar.tsx          # Top status bar
│   └── Controls.tsx           # Zoom/pan controls
├── hooks/
│   ├── useSocket.ts           # Socket.io connection
│   ├── useServiceData.ts      # Service state management
│   └── useGraphLayout.ts      # Auto-layout logic
├── context/
│   └── AppContext.tsx         # Global state management
├── types/
│   └── index.ts               # TypeScript definitions
└── utils/
    ├── graphUtils.ts          # Graph manipulation
    └── dataUtils.ts           # Data processing
```

#### **2.2 Node.js Proxy Structure**
```
proxy/
├── src/
│   ├── server.js              # Express server
│   ├── mqttClient.js          # MQTT monitoring
│   ├── healthChecker.js       # Health polling
│   └── socketHandler.js       # Socket.io events
├── config/
│   └── services.json          # Service configuration
└── Dockerfile
```

### **Phase 3: Real-time Data Flow**

#### **3.1 Service Discovery**
```javascript
// Auto-discover services from docker-compose.bus.yml
const discoverServices = () => {
  // Parse docker-compose.bus.yml
  // Extract service names and ports
  // Build service configuration
};
```

#### **3.2 Health Monitoring**
```javascript
// Poll each service health endpoint
const checkServiceHealth = async (service) => {
  try {
    const response = await axios.get(`http://${service.host}:${service.port}/health`);
    return {
      status: 'healthy',
      uptime: response.data.uptime,
      lastHeartbeat: new Date(),
      latency: response.headers['x-response-time']
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error.message
    };
  }
};
```

#### **3.3 MQTT Monitoring**
```javascript
// Monitor MQTT bus traffic
const monitorMQTT = () => {
  mqttClient.on('message', (topic, message) => {
    // Parse message to extract source/target services
    // Update graph edges
    // Emit to frontend via Socket.io
  });
};
```

### **Phase 4: Graph Visualization**

#### **4.1 Node Rendering**
```jsx
const ServiceNode = ({ data, selected }) => {
  const nodeColor = getNodeColor(data.status);
  const nodeSize = getNodeSize(data.messageCount);
  
  return (
    <div 
      className={`service-node ${selected ? 'selected' : ''}`}
      style={{ 
        backgroundColor: nodeColor,
        width: nodeSize,
        height: nodeSize
      }}
    >
      <div className="service-name">{data.name}</div>
      <div className="service-status">{data.status}</div>
    </div>
  );
};
```

#### **4.2 Edge Animation**
```jsx
const MessageEdge = ({ source, target, active }) => {
  return (
    <animated.path
      d={getEdgePath(source, target)}
      stroke={active ? '#10B981' : '#6B7280'}
      strokeWidth={active ? 3 : 1}
      fill="none"
      style={{
        strokeDasharray: active ? '5,5' : '0',
        animation: active ? 'flow 2s linear infinite' : 'none'
      }}
    />
  );
};
```

#### **4.3 Auto-layout**
```javascript
// Use React Flow's auto-layout
const layoutNodes = (nodes, edges) => {
  const layouted = getLayoutedElements(nodes, edges, 'dagre');
  return {
    nodes: layouted.nodes,
    edges: layouted.edges
  };
};
```

### **Phase 5: Interactive Features**

#### **5.1 Node Click Handler**
```javascript
const handleNodeClick = (event, node) => {
  setSelectedNode(node);
  setSidePanelOpen(true);
  // Update side panel with service details
};
```

#### **5.2 Hover Effects**
```javascript
const handleNodeHover = (event, node) => {
  setHoveredNode(node);
  // Show latency tooltip
  // Highlight connected edges
};
```

#### **5.3 Side Panel**
```jsx
const SidePanel = ({ node, isOpen }) => {
  if (!isOpen || !node) return null;
  
  return (
    <div className="side-panel">
      <h3>{node.data.name}</h3>
      <div className="service-details">
        <div>Status: <span className={node.data.status}>{node.data.status}</span></div>
        <div>Uptime: {node.data.uptime}</div>
        <div>Last Heartbeat: {node.data.lastHeartbeat}</div>
        <div>Latency: {node.data.latency}ms</div>
      </div>
      <div className="topics">
        <h4>Subscribed Topics</h4>
        <ul>{node.data.subscribedTopics.map(topic => <li key={topic}>{topic}</li>)}</ul>
        <h4>Published Topics</h4>
        <ul>{node.data.publishedTopics.map(topic => <li key={topic}>{topic}</li>)}</ul>
      </div>
    </div>
  );
};
```

### **Phase 6: Styling & Animation**

#### **6.1 Tailwind Configuration**
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'healthy': '#10B981',
        'unhealthy': '#EF4444',
        'inactive': '#6B7280'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'flow': 'flow 2s linear infinite'
      }
    }
  }
};
```

#### **6.2 CSS Animations**
```css
@keyframes flow {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: 20; }
}

@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.service-node {
  transition: all 0.3s ease;
}

.service-node:hover {
  transform: scale(1.1);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}
```

### **Phase 7: Docker Integration**

#### **7.1 Docker Compose Addition**
```yaml
# Add to docker-compose.bus.yml
alicia-monitor-proxy:
  container_name: alicia_monitor_proxy
  build: ./alicia-monitor-proxy
  ports:
    - "3001:3001"
  environment:
    - MQTT_BROKER=alicia_bus_core
    - MQTT_PORT=1883
    - MQTT_USERNAME=monitor
    - MQTT_PASSWORD=alicia_monitor_2024
  network_mode: host
  depends_on:
    - alicia-bus-core
```

#### **7.2 Service Configuration**
```json
// services.json
{
  "services": [
    {
      "name": "alicia-bus-core",
      "host": "localhost",
      "port": 1883,
      "type": "mqtt",
      "healthEndpoint": null
    },
    {
      "name": "alicia-health-monitor",
      "host": "localhost", 
      "port": 8083,
      "type": "http",
      "healthEndpoint": "/health"
    }
    // ... other services
  ]
}
```

## 🎯 **Key Features**

### **Real-time Visualization**
- Live message flow animation
- Dynamic node status updates
- Smooth transitions and animations
- Responsive graph layout

### **Interactive Interface**
- Click nodes for detailed information
- Hover for latency and quick stats
- Zoom and pan controls
- Collapsible side panel

### **Health Monitoring**
- 10-second health check polling
- Visual status indicators
- Uptime and heartbeat tracking
- Error state handling

### **MQTT Integration**
- Real-time topic monitoring
- Message flow visualization
- Service communication mapping
- Bus traffic analysis

## 🚀 **Deployment Steps**

### **1. Development Setup**
```bash
# Clone and setup
git clone <repository>
cd alicia-monitor
npm install

# Start development
npm start
```

### **2. Proxy Setup**
```bash
# Build and run proxy
cd alicia-monitor-proxy
docker build -t alicia-monitor-proxy .
docker run --network host alicia-monitor-proxy
```

### **3. Integration**
```bash
# Add to existing docker-compose.bus.yml
# Start all services
docker-compose -f docker-compose.bus.yml up -d

# Open browser
open http://localhost:3000
```

## 📊 **Expected Outcome**

A beautiful, real-time visualization of the Alicia Bus Architecture that shows:
- **Living System**: Animated message flow between services
- **Health Status**: Real-time health monitoring with visual indicators
- **Interactive Details**: Click any service for comprehensive information
- **Smooth Experience**: Fluid animations and responsive interface
- **Professional Look**: Modern UI that feels like monitoring enterprise infrastructure

The app will make the microservice architecture feel alive, showing the "arteries" of the system as messages flow between services in real-time.

---

*This plan provides a comprehensive roadmap for building a production-ready microservice monitoring web application that perfectly complements the Alicia Bus Architecture.*
