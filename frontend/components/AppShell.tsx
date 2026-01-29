'use client';

import { useState, useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
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
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user, token, logout } = useAuth();

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

  // Listen for custom event to open feedback modal from other pages
  useEffect(() => {
    function handleOpenFeedback() {
      setShowFeedbackModal(true);
    }
    window.addEventListener('open-feedback-modal', handleOpenFeedback);
    return () => window.removeEventListener('open-feedback-modal', handleOpenFeedback);
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
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${isAdmin ? 'bg-fire/20' : 'bg-ice/20'}`}>
          {isAdmin ? (
            <svg className="w-4 h-4 text-fire" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          ) : (
            <svg className="w-4 h-4 text-ice" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          )}
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
              <Image src="/images/frost_star.png" alt="" width={20} height={20} />
              <span>Support Bear's Den</span>
            </a>

            {/* Feedback */}
            <button
              onClick={() => {
                setIsOpen(false);
                setShowFeedbackModal(true);
              }}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-frost hover:bg-surface-hover transition-colors"
            >
              <span>💬</span>
              <span>Send Feedback</span>
            </button>

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

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <FeedbackModal
          token={token || ''}
          onClose={() => setShowFeedbackModal(false)}
        />
      )}
    </div>
  );
}

function FeedbackModal({ token, onClose }: { token: string; onClose: () => void }) {
  const [category, setCategory] = useState<string>('feature');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    { value: 'bug', label: 'Bug Report', icon: '🐛' },
    { value: 'feature', label: 'Feature Request', icon: '💡' },
    { value: 'bad_recommendation', label: 'Bad AI Recommendation', icon: '🤖' },
    { value: 'data_error', label: 'Data Error', icon: '📊' },
    { value: 'other', label: 'Other', icon: '💬' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || description.length < 10) {
      setError('Please provide at least 10 characters of feedback');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const res = await fetch('http://localhost:8000/api/feedback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category,
          description: description.trim(),
          page: window.location.pathname,
        }),
      });

      if (res.ok) {
        setSuccess(true);
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to submit feedback');
      }
    } catch (err) {
      setError('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100]" onClick={onClose} />
      {/* Modal */}
      <div className="fixed inset-0 z-[101] flex items-center justify-center p-4 pointer-events-none">
        <div className="bg-surface rounded-xl border border-surface-border max-w-md w-full p-6 animate-fade-in pointer-events-auto max-h-[90vh] overflow-y-auto"
             onClick={e => e.stopPropagation()}>
        {success ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">✓</div>
            <h3 className="text-lg font-bold text-frost mb-2">Thank you, Chief!</h3>
            <p className="text-frost-muted">Your feedback has been submitted.</p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-frost">Send Feedback</h2>
              <button
                onClick={onClose}
                className="text-frost-muted hover:text-frost transition-colors"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {/* Category Selection */}
              <div className="mb-4">
                <label className="block text-sm text-frost-muted mb-2">Category</label>
                <div className="grid grid-cols-2 gap-2">
                  {categories.map((cat) => (
                    <button
                      key={cat.value}
                      type="button"
                      onClick={() => setCategory(cat.value)}
                      className={`p-2 rounded-lg text-sm text-left transition-colors ${
                        category === cat.value
                          ? 'bg-ice/20 text-ice ring-1 ring-ice'
                          : 'bg-surface-hover text-frost-muted hover:text-frost'
                      }`}
                    >
                      <span className="mr-2">{cat.icon}</span>
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Description */}
              <div className="mb-4">
                <label className="block text-sm text-frost-muted mb-2">
                  {category === 'bug' ? 'What happened? Steps to reproduce?' :
                   category === 'feature' ? 'What would you like to see?' :
                   category === 'bad_recommendation' ? 'What was wrong with the recommendation?' :
                   category === 'data_error' ? 'What data is incorrect?' :
                   'Your feedback'}
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Please be specific so we can help..."
                  className="input w-full h-32 resize-none"
                  autoFocus
                />
              </div>

              {error && (
                <div className="mb-4 p-3 rounded-lg bg-error/10 border border-error/30 text-error text-sm">
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary flex-1"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary flex-1"
                  disabled={isSubmitting || !description.trim()}
                >
                  {isSubmitting ? 'Sending...' : 'Send Feedback'}
                </button>
              </div>
            </form>
          </>
        )}
        </div>
      </div>
    </>
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
