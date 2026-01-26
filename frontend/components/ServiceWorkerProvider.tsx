'use client';

import { ReactNode } from 'react';
import { useServiceWorker, usePWAInstallPrompt } from '@/lib/useServiceWorker';
import { InstallPrompt } from './InstallPrompt';

interface ServiceWorkerProviderProps {
  children: ReactNode;
}

export function ServiceWorkerProvider({ children }: ServiceWorkerProviderProps) {
  // Register service worker
  useServiceWorker();

  // Set up PWA install prompt handler
  usePWAInstallPrompt();

  return (
    <>
      {children}
      <InstallPrompt />
    </>
  );
}
