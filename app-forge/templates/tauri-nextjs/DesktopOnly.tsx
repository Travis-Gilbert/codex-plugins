// components/DesktopOnly.tsx
// Conditionally renders children only in Tauri desktop environment.
'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { isTauri } from '../lib/tauri-bridge';

export function DesktopOnly({ children }: { children: ReactNode }) {
  const [isDesktop, setIsDesktop] = useState(false);

  useEffect(() => {
    setIsDesktop(isTauri());
  }, []);

  if (!isDesktop) return null;
  return <>{children}</>;
}

export function BrowserOnly({ children }: { children: ReactNode }) {
  const [isBrowser, setIsBrowser] = useState(false);

  useEffect(() => {
    setIsBrowser(!isTauri());
  }, []);

  if (!isBrowser) return null;
  return <>{children}</>;
}
