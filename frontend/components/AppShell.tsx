'use client';

import { useState, useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Sidebar from './Sidebar';
import { useAuth } from '@/lib/auth';

interface AppShellProps {
  children: React.ReactNode;
}

// Mobile bottom navigation items (simplified)
const mobileNavItems = [
  { href: '/', label: 'Home', icon: '🏠' },
  { href: '/heroes', label: 'Heroes', icon: '🦸' },
  { href: '/advisor', label: 'AI', icon: '🤖' },
  { href: '/lineups', label: 'Lineups', icon: '⚔️' },
  { href: '/settings', label: 'More', icon: '☰' },
];

function ImpersonationBanner({ email }: { email: string }) {
  const { switchBack } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const handleSwitchBack = async () => {
    setIsLoading(true);
    try {
      await switchBack();
      window.location.href = '/admin/users';
    } catch (error) {
      console.error('Failed to switch back:', error);
      alert('Failed to switch back to admin');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-fire/20 border-t border-fire/30 px-4 py-2 text-center">
      <span className="text-xs text-fire">
        Viewing as: {email}
      </span>
      <button
        onClick={handleSwitchBack}
        disabled={isLoading}
        className="ml-2 text-xs text-frost underline hover:text-ice transition-colors disabled:opacity-50"
      >
        {isLoading ? 'Switching...' : 'Switch Back'}
      </button>
    </div>
  );
}

function UserMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const displayName = user?.email?.split('@')[0] || 'User';
  const isAdmin = user?.role === 'admin';

  return (
    <div className="relative" ref={menuRef}>
      {/* Menu trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-2 rounded-lg hover:bg-surface/50 transition-colors"
      >
        <div className="w-8 h-8 bg-ice/20 rounded-full flex items-center justify-center">
          <span className="text-sm">👤</span>
        </div>
        <span className="hidden md:block text-sm text-frost max-w-[120px] truncate">
          {displayName}
        </span>
        <svg
          className={`hidden md:block w-4 h-4 text-text-secondary transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-surface border border-surface-border rounded-xl shadow-card overflow-hidden z-50 animate-fade-in">
          {/* User info header */}
          <div className="p-4 border-b border-surface-border/50 bg-background-light">
            <p className="font-medium text-frost truncate">{user?.email}</p>
            <p className="text-xs text-text-muted capitalize">{user?.role || 'user'}</p>
          </div>

          {/* Menu items */}
          <div className="py-2">
            {/* Support */}
            <a
              href="https://ko-fi.com/randomchaoslabs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-4 py-2.5 text-sm text-frost hover:bg-surface-hover transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <span>☕</span>
              <span>Support Bear's Den</span>
            </a>

            {/* Feedback */}
            <Link
              href="/inbox"
              className="flex items-center gap-3 px-4 py-2.5 text-sm text-frost hover:bg-surface-hover transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <span>💬</span>
              <span>Send Feedback</span>
            </Link>

            <div className="my-2 border-t border-surface-border/50" />

            {/* Change Password */}
            <Link
              href="/settings?tab=password"
              className="flex items-center gap-3 px-4 py-2.5 text-sm text-frost hover:bg-surface-hover transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <span>🔑</span>
              <span>Change Password</span>
            </Link>

            {/* Change Email */}
            <Link
              href="/settings?tab=email"
              className="flex items-center gap-3 px-4 py-2.5 text-sm text-frost hover:bg-surface-hover transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <span>📧</span>
              <span>Change Email</span>
            </Link>

            {/* Admin Panel - only for admins */}
            {isAdmin && (
              <>
                <div className="my-2 border-t border-surface-border/50" />
                <Link
                  href="/admin"
                  className="flex items-center gap-3 px-4 py-2.5 text-sm text-fire hover:bg-surface-hover transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  <span>⚙️</span>
                  <span>Admin Panel</span>
                </Link>
              </>
            )}

            <div className="my-2 border-t border-surface-border/50" />

            {/* Logout */}
            <button
              onClick={() => {
                logout();
                setIsOpen(false);
              }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-text-secondary hover:text-frost hover:bg-surface-hover transition-colors"
            >
              <span>🚪</span>
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const { user } = useAuth();

  // Close sidebar on route change
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  // Check if running as standalone PWA
  const isStandalone = typeof window !== 'undefined' &&
    (window.matchMedia('(display-mode: standalone)').matches ||
     (window.navigator as any).standalone);

  return (
    <div className="flex min-h-screen min-h-[100dvh]">
      {/* Sidebar - hidden on mobile unless opened */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header - visible on all screen sizes */}
        <header className="sticky top-0 z-30 bg-background/95 backdrop-blur-lg border-b border-surface-border safe-top">
          <div className="flex items-center justify-between px-4 py-3">
            {/* Left side - hamburger on mobile, empty on desktop */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 -ml-2 rounded-lg text-text-secondary hover:text-frost hover:bg-surface/50 transition-colors md:hidden"
                aria-label="Open menu"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              {/* Logo - mobile only */}
              <Link href="/" className="flex items-start gap-0.5 md:hidden">
                <span className="text-lg font-bold text-frost">Bear's Den</span>
                <svg className="w-4 h-4 text-ice drop-shadow-[0_0_6px_rgba(74,144,217,0.8)] -mt-1" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L12 22M2 12L22 12M4.93 4.93L19.07 19.07M19.07 4.93L4.93 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none"/>
                  <circle cx="12" cy="12" r="2" fill="currentColor"/>
                </svg>
              </Link>
            </div>

            {/* Right side - User menu */}
            <UserMenu />
          </div>

          {/* Impersonation banner */}
          {user?.impersonating && (
            <ImpersonationBanner email={user.email} />
          )}
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 md:p-6 lg:p-8 pb-20 md:pb-6 animate-fade-in">
          {children}
        </main>

        {/* Mobile bottom navigation */}
        <nav className="mobile-nav">
          {mobileNavItems.map((item) => {
            const isActive = pathname === item.href ||
              (item.href !== '/' && pathname?.startsWith(item.href));

            // Special handling for "More" button
            if (item.label === 'More') {
              return (
                <button
                  key={item.href}
                  onClick={() => setSidebarOpen(true)}
                  className={`mobile-nav-item ${isActive ? 'text-ice' : ''}`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span className="text-[10px]">{item.label}</span>
                </button>
              );
            }

            return (
              <Link
                key={item.href}
                href={item.href}
                className={isActive ? 'mobile-nav-item-active' : 'mobile-nav-item'}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="text-[10px]">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
