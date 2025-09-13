import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface UseSocketOptions {
  url: string;
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export const useSocket = ({
  url,
  autoConnect = true,
  reconnectAttempts = 5,
  reconnectDelay = 1000
}: UseSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef(0);

  const connect = () => {
    if (socketRef.current?.connected) return;

    try {
      socketRef.current = io(url, {
        autoConnect: false,
        reconnection: false // We'll handle reconnection manually
      });

      socketRef.current.on('connect', () => {
        setIsConnected(true);
        setError(null);
        reconnectCountRef.current = 0;
      });

      socketRef.current.on('disconnect', () => {
        setIsConnected(false);
        attemptReconnect();
      });

      socketRef.current.on('connect_error', (err) => {
        setError(err.message);
        attemptReconnect();
      });

      socketRef.current.connect();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    }
  };

  const attemptReconnect = () => {
    if (reconnectCountRef.current >= reconnectAttempts) {
      setError('Max reconnection attempts reached');
      return;
    }

    reconnectCountRef.current++;
    const delay = reconnectDelay * Math.pow(2, reconnectCountRef.current - 1);

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    socketRef.current?.disconnect();
    setIsConnected(false);
  };

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url, autoConnect]);

  return {
    socket: socketRef.current,
    isConnected,
    error,
    connect,
    disconnect
  };
};
