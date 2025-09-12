# Cline Phase 3: Frontend React Application

## 🎯 **Goal**
Create the React frontend with TypeScript, Tailwind CSS, and React Flow integration.

## 📁 **Frontend Structure**

```
frontend/
├── package.json (already created)
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── components/
    │   ├── ServiceGraph.tsx
    │   ├── ServiceNode.tsx
    │   ├── ConfigModal.tsx
    │   ├── DeviceManager.tsx
    │   ├── ReloadButton.tsx
    │   └── StatusBar.tsx
    ├── hooks/
    │   ├── useSocket.ts
    │   ├── useConfig.ts
    │   └── useDevices.ts
    ├── services/
    │   └── api.ts
    ├── types/
    │   └── index.ts
    └── utils/
        └── cn.ts
```

## ⚙️ **Configuration Files**

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

**frontend/tsconfig.json:**
```typescript
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

**frontend/tailwind.config.js:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

**frontend/postcss.config.js:**
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**frontend/index.html:**
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Alicia Config Manager</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## 🎨 **Main Application**

**frontend/src/main.tsx:**
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**frontend/src/App.tsx:**
```typescript
import React, { useState } from 'react';
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

function App() {
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [isDeviceManagerOpen, setIsDeviceManagerOpen] = useState(false);

  const { isConnected } = useSocket();
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

## 🎣 **Custom Hooks**

**frontend/src/hooks/useSocket.ts:**
```typescript
import { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

export const useSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);

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

## 🎯 **Implementation Steps**

1. **Create the frontend directory structure** as shown
2. **Create all configuration files** with the exact content provided
3. **Create the main App component** and custom hooks
4. **Install dependencies** by running `npm install` in the frontend directory
5. **Test the frontend** by running `npm run dev` in the frontend directory

## ✅ **Verification**

After implementation, verify:
- [ ] Frontend starts without errors
- [ ] TypeScript compilation works
- [ ] Tailwind CSS is working
- [ ] Socket.io connection is established
- [ ] API calls work correctly

**Next Phase**: React Flow components and service visualization

