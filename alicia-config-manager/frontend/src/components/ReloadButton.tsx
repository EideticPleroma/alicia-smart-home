import React, { useState } from 'react';
import { RotateCcw, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

interface ReloadButtonProps {
  onReload: () => Promise<void>;
}

export const ReloadButton: React.FC<ReloadButtonProps> = ({ onReload }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleReload = async () => {
    setIsLoading(true);
    try {
      await onReload();
      toast.success('Configuration reloaded successfully');
    } catch (error) {
      toast.error('Failed to reload configuration');
      console.error('Reload error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleReload}
      disabled={isLoading}
      className="flex items-center px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-md text-sm font-medium transition-colors"
    >
      {isLoading ? (
        <Loader className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        <RotateCcw className="w-4 h-4 mr-2" />
      )}
      {isLoading ? 'Reloading...' : 'Reload Config'}
    </button>
  );
};
