import React from 'react';
import { Wifi, WifiOff, Server, Database } from 'lucide-react';

interface StatusBarProps {
  isConnected: boolean;
  serviceCount: number;
  deviceCount: number;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  isConnected,
  serviceCount,
  deviceCount,
}) => {
  return (
    <div className="flex items-center space-x-4 text-sm">
      <div className="flex items-center space-x-2">
        {isConnected ? (
          <Wifi className="w-4 h-4 text-green-400" />
        ) : (
          <WifiOff className="w-4 h-4 text-red-400" />
        )}
        <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      <div className="flex items-center space-x-2">
        <Server className="w-4 h-4 text-blue-400" />
        <span className="text-blue-400">{serviceCount} Services</span>
      </div>

      <div className="flex items-center space-x-2">
        <Database className="w-4 h-4 text-purple-400" />
        <span className="text-purple-400">{deviceCount} Devices</span>
      </div>
    </div>
  );
};
