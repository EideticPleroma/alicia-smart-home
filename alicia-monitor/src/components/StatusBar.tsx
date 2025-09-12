import React from 'react';

interface StatusBarProps {
  isConnected: boolean;
  serviceCount: number;
  healthyCount: number;
}

const StatusBar: React.FC<StatusBarProps> = ({ isConnected, serviceCount, healthyCount }) => {
  return (
    <div className="bg-gray-900 text-white p-4 flex justify-between items-center shadow-lg">
      <div className="flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-connected' : 'bg-disconnected'}`}></div>
        <span className="text-sm font-medium">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      <div className="text-sm">
        Services: {serviceCount} | Healthy: {healthyCount}
      </div>

      <div className="text-sm font-semibold">
        Alicia Bus Architecture Monitor
      </div>
    </div>
  );
};

export default StatusBar;
