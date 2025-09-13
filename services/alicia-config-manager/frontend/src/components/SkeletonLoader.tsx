import React from 'react';

interface SkeletonLoaderProps {
  className?: string;
  lines?: number;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className = '',
  lines = 1
}) => {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="h-4 bg-gray-700 rounded mb-2"
          style={{ width: `${Math.random() * 40 + 60}%` }}
        />
      ))}
    </div>
  );
};

export const ServiceNodeSkeleton: React.FC = () => {
  return (
    <div className="bg-gray-800 border border-gray-600 rounded-lg p-4 min-w-[200px]">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-gray-700 rounded animate-pulse" />
          <div className="h-4 w-24 bg-gray-700 rounded animate-pulse" />
        </div>
        <div className="w-3 h-3 bg-gray-700 rounded-full animate-pulse" />
      </div>
      <div className="space-y-1">
        <SkeletonLoader lines={3} />
      </div>
    </div>
  );
};

export const DeviceCardSkeleton: React.FC = () => {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
      <div className="flex items-center space-x-4">
        <div className="w-3 h-3 bg-gray-600 rounded-full animate-pulse" />
        <div>
          <div className="h-4 w-32 bg-gray-600 rounded animate-pulse mb-1" />
          <div className="h-3 w-48 bg-gray-600 rounded animate-pulse" />
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-gray-600 rounded animate-pulse" />
        <div className="w-8 h-8 bg-gray-600 rounded animate-pulse" />
      </div>
    </div>
  );
};

export default SkeletonLoader;
