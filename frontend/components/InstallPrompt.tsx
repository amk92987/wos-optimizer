'use client';

import { useState, useEffect } from 'react';
import { isPWA, promptPWAInstall } from '@/lib/useServiceWorker';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

export function InstallPrompt() {
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isAndroid, setIsAndroid] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Don't show if already installed as PWA
    if (isPWA()) {
      return;
    }

    // Only show on mobile devices
    const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
      navigator.userAgent.toLowerCase()
    );
    if (!isMobile) {
      return; // Don't show on desktop
    }

    // Check if user has previously dismissed
    const wasDismissed = localStorage.getItem('pwa-install-dismissed');
    if (wasDismissed) {
      const dismissedTime = parseInt(wasDismissed, 10);
      // Show again after 7 days
      if (Date.now() - dismissedTime < 7 * 24 * 60 * 60 * 1000) {
        return;
      }
    }

    // Detect platform
    const userAgent = navigator.userAgent.toLowerCase();
    const isIOSDevice = /iphone|ipad|ipod/.test(userAgent) && !(window as any).MSStream;
    const isAndroidDevice = /android/.test(userAgent);

    setIsIOS(isIOSDevice);
    setIsAndroid(isAndroidDevice);

    // For iOS, show custom instructions (iOS doesn't support beforeinstallprompt)
    if (isIOSDevice && !(navigator as any).standalone) {
      // Show after a short delay
      const timer = setTimeout(() => setShowPrompt(true), 3000);
      return () => clearTimeout(timer);
    }

    // For Android/Chrome, listen for the install prompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      (window as any).pwaInstallPrompt = e as BeforeInstallPromptEvent;
      setShowPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Check if prompt was already captured
    if ((window as any).pwaInstallPrompt) {
      setShowPrompt(true);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstall = async () => {
    if (isIOS) {
      // iOS doesn't support programmatic install, just show instructions
      return;
    }

    const installed = await promptPWAInstall();
    if (installed) {
      setShowPrompt(false);
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  if (!showPrompt || dismissed) {
    return null;
  }

  return (
    <div className="fixed bottom-20 md:bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm z-50 animate-slide-up">
      <div className="bg-surface/95 backdrop-blur-lg border border-ice/30 rounded-xl p-4 shadow-card">
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 bg-ice/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <span className="text-2xl">📱</span>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-frost mb-1">Install Bear's Den</h3>
            {isIOS ? (
              <p className="text-sm text-text-secondary">
                Tap <span className="inline-flex items-center mx-1 px-1.5 py-0.5 bg-surface rounded text-frost">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                </span> then <span className="text-frost font-medium">"Add to Home Screen"</span>
              </p>
            ) : (
              <p className="text-sm text-text-secondary">
                Add to your home screen for quick access and a better experience.
              </p>
            )}
          </div>
          <button
            onClick={handleDismiss}
            className="text-text-muted hover:text-frost transition-colors p-1"
            aria-label="Dismiss"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {!isIOS && (
          <div className="flex gap-2 mt-4">
            <button
              onClick={handleDismiss}
              className="flex-1 btn-ghost text-sm py-2"
            >
              Not now
            </button>
            <button
              onClick={handleInstall}
              className="flex-1 btn-primary text-sm py-2"
            >
              Install App
            </button>
          </div>
        )}

        {isIOS && (
          <button
            onClick={handleDismiss}
            className="w-full btn-ghost text-sm py-2 mt-3"
          >
            Got it
          </button>
        )}
      </div>
    </div>
  );
}

// Smaller inline install button for header/menu
export function InstallButton() {
  const [canInstall, setCanInstall] = useState(false);

  useEffect(() => {
    if (isPWA()) return;

    const checkInstallable = () => {
      setCanInstall(!!(window as any).pwaInstallPrompt);
    };

    window.addEventListener('beforeinstallprompt', checkInstallable);
    checkInstallable();

    return () => window.removeEventListener('beforeinstallprompt', checkInstallable);
  }, []);

  if (!canInstall) return null;

  return (
    <button
      onClick={() => promptPWAInstall()}
      className="btn-secondary text-sm flex items-center gap-2"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      Install App
    </button>
  );
}
