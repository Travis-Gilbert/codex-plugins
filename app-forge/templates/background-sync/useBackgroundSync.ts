// hooks/useBackgroundSync.ts
// Coordinates Web Worker polling + SSE + sync status state.
'use client';

import { useEffect, useRef, useState } from 'react';
import { sseClient } from '../lib/sse-client';

interface SyncState {
  isOnline: boolean;
  sseConnected: boolean;
  pendingMutations: number;
  lastSyncTimestamp: number | null;
}

export function useBackgroundSync(config: {
  apiUrl: string;
  token: string;
  pollInterval?: number;
  sseUrl?: string;
  endpoints?: string[];
}) {
  const {
    apiUrl,
    token,
    pollInterval = 30000,
    sseUrl,
    endpoints = [],
  } = config;

  const workerRef = useRef<Worker | null>(null);
  const [syncState, setSyncState] = useState<SyncState>({
    isOnline: true,
    sseConnected: false,
    pendingMutations: 0,
    lastSyncTimestamp: null,
  });

  // Online/offline detection
  useEffect(() => {
    const handleOnline = () => setSyncState((s) => ({ ...s, isOnline: true }));
    const handleOffline = () =>
      setSyncState((s) => ({ ...s, isOnline: false }));

    setSyncState((s) => ({ ...s, isOnline: navigator.onLine }));
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Web Worker polling
  useEffect(() => {
    if (endpoints.length === 0) return;

    const worker = new Worker(
      new URL('../workers/connection-monitor.ts', import.meta.url)
    );

    worker.onmessage = (event) => {
      if (event.data.type === 'POLL_RESULT') {
        setSyncState((s) => ({
          ...s,
          lastSyncTimestamp: Date.now(),
        }));
      }
    };

    worker.postMessage({
      type: 'START',
      config: { apiUrl, token, pollInterval, endpoints },
    });

    workerRef.current = worker;

    return () => {
      worker.postMessage({ type: 'STOP' });
      worker.terminate();
    };
  }, [apiUrl, token, pollInterval, endpoints]);

  // SSE connection
  useEffect(() => {
    if (!sseUrl) return;

    sseClient.connect(sseUrl, token);

    const checkInterval = setInterval(() => {
      setSyncState((s) => ({
        ...s,
        sseConnected: sseClient.isConnected,
      }));
    }, 5000);

    return () => {
      clearInterval(checkInterval);
      sseClient.disconnect();
    };
  }, [sseUrl, token]);

  return {
    ...syncState,
    sseClient,
    pollNow: () => {
      workerRef.current?.postMessage({
        type: 'POLL_NOW',
        config: { apiUrl, token, pollInterval, endpoints },
      });
    },
  };
}
