import React from 'react';
import { ServiceData } from '../types';

interface SidePanelProps {
  node: { id: string; data: ServiceData } | null;
  onClose: () => void;
}

const SidePanel: React.FC<SidePanelProps> = ({ node, onClose }) => {
  if (!node) return null;

  const { data } = node;
  const isOpen = true; // Always open when node is selected

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return '#10B981';
      case 'unhealthy':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const formatUptime = (uptime: string) => {
    if (!uptime) return 'Unknown';
    // Simple formatting - could be enhanced
    return uptime;
  };

  const formatTimestamp = (timestamp: string) => {
    if (!timestamp) return 'Unknown';
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Side Panel */}
      <div className="fixed top-0 right-0 w-96 h-full bg-white shadow-2xl z-50 overflow-y-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
          <h2 className="m-0 text-2xl font-bold text-gray-900">
            Service Details
          </h2>
          <button
            onClick={onClose}
            className="bg-none border-none text-2xl cursor-pointer text-gray-500 p-1 rounded hover:bg-gray-100 transition-colors"
          >
            ×
          </button>
        </div>

        {/* Service Name */}
        <div className="mb-5">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            {data.name}
          </h3>
        </div>

        {/* Status */}
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: getStatusColor(data.status) }}
            />
            <span className="text-base font-medium text-gray-900 capitalize">
              {data.status}
            </span>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
              Uptime
            </label>
            <div className="text-sm text-gray-900 font-medium">
              {formatUptime(data.uptime || 'Unknown')}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
              Latency
            </label>
            <div className="text-sm text-gray-900 font-medium">
              {data.latency ? `${data.latency}ms` : 'Unknown'}
            </div>
          </div>

          <div className="col-span-2">
            <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
              Last Updated
            </label>
            <div className="text-sm text-gray-900 font-medium">
              {formatTimestamp(data.timestamp || '')}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {data.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-5">
            <div className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-1">
              Error
            </div>
            <div className="text-sm text-red-800">
              {data.error}
            </div>
          </div>
        )}

        {/* Topics */}
        <div className="mb-5">
          <h4 className="text-base font-semibold text-gray-700 mb-3">
            MQTT Topics
          </h4>

          {/* Subscribed Topics */}
          <div className="mb-4">
            <div className="text-sm font-medium text-gray-500 mb-2">
              Subscribed Topics
            </div>
            {data.subscribedTopics && data.subscribedTopics.length > 0 ? (
              <div className="flex flex-col gap-1">
                {data.subscribedTopics.map((topic, index) => (
                  <div
                    key={index}
                    className="text-sm text-gray-700 bg-gray-100 px-2 py-1 rounded font-mono"
                  >
                    {topic}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-400 italic">
                No subscribed topics
              </div>
            )}
          </div>

          {/* Published Topics */}
          <div>
            <div className="text-sm font-medium text-gray-500 mb-2">
              Published Topics
            </div>
            {data.publishedTopics && data.publishedTopics.length > 0 ? (
              <div className="flex flex-col gap-1">
                {data.publishedTopics.map((topic, index) => (
                  <div
                    key={index}
                    className="text-sm text-gray-700 bg-gray-100 px-2 py-1 rounded font-mono"
                  >
                    {topic}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-400 italic">
                No published topics
              </div>
            )}
          </div>
        </div>

        {/* Additional Details */}
        {data.details && (
          <div>
            <h4 className="text-base font-semibold text-gray-700 mb-3">
              Additional Details
            </h4>
            <pre className="bg-gray-50 p-3 rounded-lg text-xs text-gray-700 overflow-auto max-h-48">
              {JSON.stringify(data.details, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </>
  );
};

export default SidePanel;
