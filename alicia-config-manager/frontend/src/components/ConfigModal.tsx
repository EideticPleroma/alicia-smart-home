import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { ServiceConfig } from '../types';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import { X, Save, RotateCcw } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface ConfigModalProps {
  serviceName: string;
  config: ServiceConfig;
  onSave: (config: ServiceConfig) => void;
  onClose: () => void;
}

export const ConfigModal: React.FC<ConfigModalProps> = ({
  serviceName,
  config,
  onSave,
  onClose,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, reset } = useForm<ServiceConfig>({
    defaultValues: config,
  });

  useEffect(() => {
    reset(config);
  }, [config, reset]);

  const onSubmit = async (data: ServiceConfig) => {
    setIsLoading(true);
    try {
      await onSave(data);
      toast.success(`Configuration saved for ${serviceName}`);
    } catch (error) {
      console.error('Failed to save configuration:', error);
      toast.error(`Failed to save configuration for ${serviceName}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    reset(config);
  };

  // Keyboard shortcuts for modal
  useKeyboardShortcuts({
    onEscape: onClose,
    onSave: handleSubmit(onSubmit),
  });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">
            Configure {serviceName}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Basic Settings</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Service Type
                </label>
                <select
                  {...register('service_type')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="stt">Speech-to-Text</option>
                  <option value="tts">Text-to-Speech</option>
                  <option value="llm">Large Language Model</option>
                  <option value="device_control">Device Control</option>
                  <option value="voice_router">Voice Router</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Status
                </label>
                <select
                  {...register('status')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="healthy">Healthy</option>
                  <option value="unhealthy">Unhealthy</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...register('enabled')}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-300">Enabled</span>
              </label>
            </div>
          </div>

          {/* API Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">API Configuration</h3>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                API Key
              </label>
              <input
                type="password"
                {...register('config.api_key')}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter API key..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Provider
                </label>
                <input
                  {...register('config.provider')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., openai, elevenlabs"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Model
                </label>
                <input
                  {...register('config.model')}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., whisper-1, gpt-4"
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-600">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center px-4 py-2 text-gray-300 hover:text-white transition-colors"
            >
              <RotateCcw size={16} className="mr-2" />
              Reset
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-md transition-colors"
            >
              <Save size={16} className="mr-2" />
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
