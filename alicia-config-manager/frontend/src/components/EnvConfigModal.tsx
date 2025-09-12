import React, { useState, useEffect } from 'react';
import { X, Save, Download, Upload, RefreshCw, Eye, EyeOff } from 'lucide-react';
import { useEnvConfig } from '../hooks/useEnvConfig';
import { toast } from 'react-hot-toast';

interface EnvConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface EnvVariable {
  key: string;
  value: string;
  isSensitive: boolean;
}

export const EnvConfigModal: React.FC<EnvConfigModalProps> = ({ isOpen, onClose }) => {
  const { envVars, loading, error, updateEnvVar, updateMultipleEnvVars, createBackup, refreshEnvVars } = useEnvConfig();
  const [editingVars, setEditingVars] = useState<Record<string, string>>({});
  const [showSensitive, setShowSensitive] = useState<Record<string, boolean>>({});
  const [isSaving, setIsSaving] = useState(false);

  // Initialize editing variables when modal opens
  useEffect(() => {
    if (isOpen) {
      setEditingVars({ ...envVars });
    }
  }, [isOpen, envVars]);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      // Find changed variables
      const changes: Record<string, string> = {};
      Object.keys(editingVars).forEach(key => {
        if (editingVars[key] !== envVars[key]) {
          changes[key] = editingVars[key];
        }
      });

      if (Object.keys(changes).length === 0) {
        toast.success('No changes to save');
        return;
      }

      // Create backup before making changes
      await createBackup();
      
      // Update environment variables
      await updateMultipleEnvVars(changes);
      
      toast.success(`Updated ${Object.keys(changes).length} environment variables`);
      onClose();
    } catch (error) {
      console.error('Error saving environment variables:', error);
      toast.error('Failed to save environment variables');
    } finally {
      setIsSaving(false);
    }
  };

  const handleVariableChange = (key: string, value: string) => {
    setEditingVars(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const toggleSensitiveVisibility = (key: string) => {
    setShowSensitive(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const isSensitiveKey = (key: string) => {
    const sensitiveKeys = [
      'GROK_API_KEY', 'OPENAI_API_KEY', 'HA_TOKEN', 'JWT_SECRET',
      'MQTT_PASSWORD', 'SMTP_PASS', 'FCM_SERVER_KEY'
    ];
    return sensitiveKeys.includes(key);
  };

  const getDisplayValue = (key: string, value: string) => {
    if (isSensitiveKey(key) && !showSensitive[key]) {
      return value.includes('*') ? value : '*'.repeat(Math.min(value.length, 8));
    }
    return value;
  };

  const hasChanges = () => {
    return Object.keys(editingVars).some(key => editingVars[key] !== envVars[key]);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Environment Configuration</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={refreshEnvVars}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {Object.entries(editingVars).map(([key, value]) => (
                <div key={key} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-300">
                      {key}
                    </label>
                    {isSensitiveKey(key) && (
                      <button
                        onClick={() => toggleSensitiveVisibility(key)}
                        className="p-1 text-gray-400 hover:text-white transition-colors"
                        title={showSensitive[key] ? 'Hide value' : 'Show value'}
                      >
                        {showSensitive[key] ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    )}
                  </div>
                  <input
                    type={isSensitiveKey(key) && !showSensitive[key] ? 'password' : 'text'}
                    value={getDisplayValue(key, value)}
                    onChange={(e) => handleVariableChange(key, e.target.value)}
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={`Enter ${key} value`}
                  />
                  {isSensitiveKey(key) && (
                    <p className="text-xs text-gray-400 mt-1">
                      This is a sensitive value and will be masked in logs
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-600">
          <div className="text-sm text-gray-400">
            {Object.keys(editingVars).length} environment variables
            {hasChanges() && (
              <span className="text-yellow-400 ml-2">• Unsaved changes</span>
            )}
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges() || isSaving}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-md transition-colors flex items-center space-x-2"
            >
              {isSaving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
