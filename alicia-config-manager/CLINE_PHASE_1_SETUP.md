# Cline Phase 1: Project Setup and Foundation

## 🎯 **Goal**
Create the basic project structure and configuration files for the Alicia Configuration Manager.

## 📁 **Create Project Structure**

```
alicia-config-manager/
├── .clinerules
├── package.json
├── docker-compose.yml
├── .env.example
├── frontend/
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
├── backend/
│   ├── package.json
│   ├── src/
│   │   ├── index.js
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   └── Dockerfile
└── config/
    ├── config.json
    └── devices.json
```

## 📦 **Root package.json**

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

## 🎨 **Frontend package.json**

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

## ⚙️ **Backend package.json**

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

## 🐳 **Docker Configuration**

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

## 🔧 **Environment Variables**

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

## 🎯 **Implementation Steps**

1. **Create the directory structure** as shown above
2. **Create all package.json files** with the exact content provided
3. **Create docker-compose.yml** with the configuration
4. **Create .env.example** with environment variables
5. **Run `npm install`** in the root directory to install workspace dependencies
6. **Run `npm install`** in both frontend and backend directories
7. **Test that the project structure is correct**

## ✅ **Verification**

After implementation, verify:
- [ ] All directories exist
- [ ] All package.json files are created
- [ ] Docker Compose file is valid
- [ ] Environment variables template is ready
- [ ] Dependencies can be installed without errors

**Next Phase**: Backend server implementation

