import { useEffect, useState, useRef } from 'react';
import io, { Socket } from 'socket.io-client';
import { ParsingProgress } from '@/types/document';

interface UseSocketProgressOptions {
  documentId?: string;
  onProgress?: (progress: ParsingProgress) => void;
  autoConnect?: boolean;
}

export function useSocketProgress(options: UseSocketProgressOptions = {}) {
  const { documentId, onProgress, autoConnect = true } = options;
  const [isConnected, setIsConnected] = useState(false);
  const [lastProgress, setLastProgress] = useState<ParsingProgress | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!autoConnect || !documentId) return;

    const socket = io();
    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      console.log('Socket.IO connected');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Socket.IO disconnected');
    });

    socket.on('progress', (data: ParsingProgress) => {
      setLastProgress(data);
      onProgress?.(data);
    });

    // Join document room
    socket.emit('join-document', documentId);

    return () => {
      if (documentId) {
        socket.emit('leave-document', documentId);
      }
      socket.close();
      socketRef.current = null;
    };
  }, [documentId, autoConnect, onProgress]);

  const joinDocument = (docId: string) => {
    if (socketRef.current) {
      socketRef.current.emit('join-document', docId);
    }
  };

  const leaveDocument = (docId: string) => {
    if (socketRef.current) {
      socketRef.current.emit('leave-document', docId);
    }
  };

  const disconnect = () => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
  };

  return {
    isConnected,
    lastProgress,
    joinDocument,
    leaveDocument,
    disconnect,
  };
}
