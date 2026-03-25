// components/SyncStatus.tsx
// Online/offline indicator with pending changes count and last sync time.
'use client';

import { useEffect, useState } from 'react';

interface SyncState {
  isOnline: boolean;
  pendingCount: number;
  lastSync: number | null;
}

function formatRelativeTime(timestamp: number): string {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export function SyncStatus() {
  const [state, setState] = useState<SyncState>({
    isOnline: true,
    pendingCount: 0,
    lastSync: null,
  });

  useEffect(() => {
    const handleOnline = () => setState(s => ({ ...s, isOnline: true }));
    const handleOffline = () => setState(s => ({ ...s, isOnline: false }));

    setState(s => ({ ...s, isOnline: navigator.onLine }));
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <div className="flex items-center gap-2 text-xs px-3 py-1">
      <span className={state.isOnline ? 'text-green-500' : 'text-amber-500'}>
        {state.isOnline ? '\u25CF' : '\u25CB'}
      </span>
      {state.pendingCount > 0 && (
        <span className="text-amber-600">{state.pendingCount} pending</span>
      )}
      {state.lastSync && (
        <span className="text-muted-foreground">
          Synced {formatRelativeTime(state.lastSync)}
        </span>
      )}
    </div>
  );
}
