import { useState, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { ServiceGraph } from './components/ServiceGraph';
import { ConfigModal } from './components/ConfigModal';
import { DeviceManager } from './components/DeviceManager';
import { EnvConfigModal } from './components/EnvConfigModal';
import { ReloadButton } from './components/ReloadButton';
import { StatusBar } from './components/StatusBar';
import { ServiceNodeSkeleton, DeviceCardSkeleton } from './components/SkeletonLoader.tsx';
import { useSocket } from './hooks/useSocket';
import { useConfig } from './hooks/useConfig';
import { useDevices } from './hooks/useDevices';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { ServiceConfig } from './types';

function App() {
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [isDeviceManagerOpen, setIsDeviceManagerOpen] = useState(false);
  const [isEnvConfigModalOpen, setIsEnvConfigModalOpen] = useState(false);

  const { isConnected } = useSocket();
  const { configs, updateConfig, reloadConfigs, loading: configsLoading } = useConfig();
  const { devices, addDevice, updateDevice, deleteDevice, loading: devicesLoading } = useDevices();

  const handleServiceClick = useCallback((serviceName: string) => {
    setSelectedService(serviceName);
    setIsConfigModalOpen(true);
  }, []);

  const handleConfigSave = useCallback(async (serviceName: string, config: ServiceConfig) => {
    try {
      await updateConfig(serviceName, config);
      toast.success(`Configuration saved successfully for ${serviceName}`);
      setIsConfigModalOpen(false);
      setSelectedService(null);
    } catch (error) {
      console.error('Failed to save configuration:', error);
      toast.error(`Failed to save configuration for ${serviceName}`);
    }
  }, [updateConfig]);

  const handleReload = useCallback(async () => {
    try {
      await reloadConfigs();
      toast.success('Configurations reloaded successfully');
    } catch (error) {
      console.error('Failed to reload configurations:', error);
      toast.error('Failed to reload configurations');
    }
  }, [reloadConfigs]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onEscape: () => {
      if (isConfigModalOpen) {
        setIsConfigModalOpen(false);
        setSelectedService(null);
      } else if (isDeviceManagerOpen) {
        setIsDeviceManagerOpen(false);
      }
    },
    onReload: handleReload,
    onDeviceManager: () => setIsDeviceManagerOpen(true),
  });

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
                onClick={() => setIsEnvConfigModalOpen(true)}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-md text-sm font-medium transition-colors"
              >
                Environment
              </button>
              <button
                onClick={() => setIsDeviceManagerOpen(true)}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md text-sm font-medium transition-colors"
              >
                Manage Devices
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {configsLoading || devicesLoading ? (
          <div className="w-full h-screen p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Service Node Skeletons */}
              {Array.from({ length: 6 }).map((_, index) => (
                <ServiceNodeSkeleton key={`service-${index}`} />
              ))}
            </div>

            {/* Device Manager Skeleton */}
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="h-6 w-48 bg-gray-700 rounded animate-pulse mb-4" />
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, index) => (
                  <DeviceCardSkeleton key={`device-${index}`} />
                ))}
              </div>
            </div>
          </div>
        ) : (
          <ServiceGraph
            services={configs}
            devices={devices}
            onServiceClick={handleServiceClick}
          />
        )}
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

      {isEnvConfigModalOpen && (
        <EnvConfigModal
          isOpen={isEnvConfigModalOpen}
          onClose={() => setIsEnvConfigModalOpen(false)}
        />
      )}
    </div>
  );
}

export default App;
