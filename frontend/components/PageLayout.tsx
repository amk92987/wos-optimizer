'use client';

import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo } from 'react';
import AppShell from './AppShell';

interface PageLayoutProps {
  children: React.ReactNode;
}

function Snowflakes() {
  const flakes = useMemo(() =>
    Array.from({ length: 20 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      delay: Math.random() * 3,
      duration: 2.5 + Math.random() * 3,
      size: 3 + Math.random() * 5,
      opacity: 0.2 + Math.random() * 0.35,
      drift: -15 + Math.random() * 30,
    })),
  []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <style>{`
        @keyframes snowfall {
          0% { transform: translateY(-10px) translateX(0); opacity: 0; }
          10% { opacity: var(--flake-opacity); }
          90% { opacity: var(--flake-opacity); }
          100% { transform: translateY(100vh) translateX(var(--flake-drift)); opacity: 0; }
        }
      `}</style>
      {flakes.map((f) => (
        <div
          key={f.id}
          className="absolute rounded-full bg-white"
          style={{
            left: `${f.left}%`,
            top: '-8px',
            width: f.size,
            height: f.size,
            ['--flake-opacity' as any]: f.opacity,
            ['--flake-drift' as any]: `${f.drift}px`,
            animation: `snowfall ${f.duration}s ${f.delay}s linear infinite`,
            opacity: 0,
          }}
        />
      ))}
    </div>
  );
}

export default function PageLayout({ children }: PageLayoutProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center relative">
        <Snowflakes />
        <div className="text-center relative z-10">
          <img
            src="/images/bear_paw.png"
            alt="Loading"
            className="w-16 h-16 mx-auto mb-4 animate-pulse opacity-60 drop-shadow-[0_0_12px_rgba(74,144,217,0.4)]"
          />
          <p className="text-zinc-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <AppShell>
      {children}
    </AppShell>
  );
}
