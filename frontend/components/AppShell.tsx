'use client';

import { useState, useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import Sidebar from './Sidebar';
import { useAuth } from '@/lib/auth';
import { feedbackApi, inboxApi, profileApi, announcementsApi, flagsApi, Announcement, Profile, FeatureFlag } from '@/lib/api';

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

function ImpersonationBanner({ username, email }: { username?: string; email: string }) {
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

  const displayName = username && username !== email ? `${username} (${email})` : email;

  return (
    <div className="bg-fire/20 border-t border-fire/30 px-4 py-2 text-center">
      <span className="text-xs text-fire">
        Viewing as: {displayName}
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

// Announcement type to color mapping
const ANNOUNCEMENT_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  info:    { bg: 'bg-blue-500/15',  border: 'border-blue-500/30',  text: 'text-blue-300' },
  warning: { bg: 'bg-amber-500/15', border: 'border-amber-500/30', text: 'text-amber-300' },
  success: { bg: 'bg-green-500/15', border: 'border-green-500/30', text: 'text-green-300' },
  error:   { bg: 'bg-red-500/15',   border: 'border-red-500/30',   text: 'text-red-300' },
};

function AnnouncementBanners({ announcements, onDismiss }: {
  announcements: Announcement[];
  onDismiss: (id: string) => void;
}) {
  if (announcements.length === 0) return null;

  return (
    <div className="w-full">
      {announcements.map((a) => {
        const colors = ANNOUNCEMENT_COLORS[a.type] || ANNOUNCEMENT_COLORS.info;
        return (
          <div
            key={a.announcement_id}
            className={`${colors.bg} border-b ${colors.border} px-4 py-2.5 flex items-center justify-between gap-3`}
          >
            <div className="flex-1 min-w-0">
              <span className={`text-sm font-medium ${colors.text}`}>
                {a.title}
              </span>
              {a.message && (
                <span className={`text-sm ${colors.text} opacity-80 ml-2`}>
                  &mdash; {a.message}
                </span>
              )}
            </div>
            <button
              onClick={() => onDismiss(a.announcement_id)}
              className={`flex-shrink-0 ${colors.text} opacity-60 hover:opacity-100 transition-opacity text-lg leading-none`}
              aria-label="Dismiss announcement"
            >
              &times;
            </button>
          </div>
        );
      })}
    </div>
  );
}

function MaintenanceScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-8">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-6">🔧</div>
        <h1 className="text-2xl font-bold text-frost mb-3">Under Maintenance</h1>
        <p className="text-frost-muted text-lg mb-4">
          Bear's Den is currently undergoing maintenance. We'll be back shortly!
        </p>
        <p className="text-text-muted text-sm">
          Please check back in a few minutes.
        </p>
      </div>
    </div>
  );
}

function MaintenanceAdminBanner() {
  return (
    <div className="bg-amber-500/20 border-b border-amber-500/40 px-4 py-2 text-center">
      <span className="text-xs font-medium text-amber-300">
        Maintenance mode is active. Users cannot access the site. Disable it in Feature Flags.
      </span>
    </div>
  );
}

function UserMenu({ unreadCount = 0 }: { unreadCount?: number }) {
  const [isOpen, setIsOpen] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [switchingProfile, setSwitchingProfile] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
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

  // Fetch profiles for profile switcher
  useEffect(() => {
    if (!token) return;
    profileApi.list(token)
      .then((data) => setProfiles(data.profiles || []))
      .catch(() => {});
  }, [token]);

  const handleSwitchProfile = async (profileId: string) => {
    if (!token) return;
    setSwitchingProfile(profileId);
    try {
      await profileApi.switch(token, profileId);
      window.location.reload();
    } catch (error) {
      console.error('Failed to switch profile:', error);
    } finally {
      setSwitchingProfile(null);
    }
  };

  const displayName = user?.email?.split('@')[0] || 'User';
  const isAdmin = user?.role === 'admin';

  return (
    <div className="relative" ref={menuRef}>
      {/* Menu trigger with unread notification dot */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-2 rounded-lg hover:bg-surface/50 transition-colors relative"
      >
        <div className={`w-8 h-8 rounded-full flex items-center justify-center bg-ice/20 shadow-glow-sm relative`}>
          {isAdmin ? (
            <svg className="w-4 h-4 text-ice drop-shadow-[0_0_4px_rgba(74,144,217,0.6)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          ) : (
            <svg className="w-4 h-4 text-ice" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          )}
          {/* Unread notification dot */}
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-error rounded-full border-2 border-background" />
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
        <div className="absolute right-0 mt-2 w-64 bg-surface/95 backdrop-blur-xl border border-ice/15 rounded-xl shadow-card overflow-hidden z-50 animate-fade-in">
          {/* User info header */}
          <div className="p-4 border-b border-surface-border/50 bg-background-light">
            <p className="font-medium text-frost truncate">{user?.email}</p>
            <p className="text-xs text-text-muted capitalize">{user?.role || 'user'}</p>
          </div>

          {/* Menu items */}
          <div className="py-2">
            {/* Inbox - non-admin users */}
            {!isAdmin && (
              <Link
                href="/inbox"
                className="flex items-center gap-3 px-4 py-2.5 text-sm text-frost hover:bg-surface-hover transition-colors"
                onClick={() => setIsOpen(false)}
              >
                <span>📬</span>
                <span className="flex-1">Inbox</span>
                {unreadCount > 0 && (
                  <span className="w-5 h-5 bg-error text-white text-xs font-bold rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Link>
            )}

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

            {/* Profile Switcher - only show if more than 1 profile */}
            {profiles.length > 1 && (
              <>
                <div className="my-2 border-t border-surface-border/50" />
                <div className="px-4 py-1.5">
                  <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-1">Switch Profile</p>
                </div>
                {profiles.map((profile) => (
                  <button
                    key={profile.profile_id}
                    onClick={() => handleSwitchProfile(profile.profile_id)}
                    disabled={switchingProfile === profile.profile_id || profile.is_active}
                    className={`w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors ${
                      profile.is_active
                        ? 'text-ice bg-ice/5 cursor-default'
                        : 'text-frost hover:bg-surface-hover'
                    } disabled:opacity-50`}
                  >
                    <span>{profile.is_farm_account ? '🌾' : '⚔️'}</span>
                    <span className="flex-1 text-left truncate">
                      {profile.name || `Profile ${profile.profile_id.slice(0, 6)}`}
                      {profile.state_number ? ` (S${profile.state_number})` : ''}
                    </span>
                    {profile.is_active && (
                      <span className="text-xs text-ice font-medium">Active</span>
                    )}
                    {switchingProfile === profile.profile_id && (
                      <span className="text-xs text-frost-muted">...</span>
                    )}
                  </button>
                ))}
              </>
            )}

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

            {/* Admin / User Panel toggle - only for admins */}
            {isAdmin && (
              <>
                <div className="my-2 border-t border-surface-border/50" />
                {pathname?.startsWith('/admin') ? (
                  <Link
                    href="/"
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-ice hover:bg-surface-hover transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    <span>🏠</span>
                    <span>User Panel</span>
                  </Link>
                ) : (
                  <Link
                    href="/admin"
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-fire hover:bg-surface-hover transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    <span>⚙️</span>
                    <span>Admin Panel</span>
                  </Link>
                )}
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
      await feedbackApi.submit(token, {
        category,
        description: description.trim(),
        page: window.location.pathname,
      });
      setSuccess(true);
      setTimeout(() => {
        onClose();
      }, 2000);
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
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());
  const [unreadCount, setUnreadCount] = useState(0);
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [flagsLoaded, setFlagsLoaded] = useState(false);
  const pathname = usePathname();
  const { user, token, isImpersonating } = useAuth();

  const isAdmin = user?.role === 'admin';

  // Close sidebar on route change
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  // Fetch active announcements (for non-admin users)
  useEffect(() => {
    if (!token || isAdmin) return;
    announcementsApi.getActive(token)
      .then((data) => {
        // Filter to only banner/both display types
        const bannerAnnouncements = (data.announcements || []).filter(
          (a) => a.display_type === 'banner' || a.display_type === 'both'
        );
        setAnnouncements(bannerAnnouncements);
      })
      .catch(() => {});
  }, [token, isAdmin]);

  // Fetch unread notification count
  useEffect(() => {
    if (!token) return;
    const fetchUnread = () => {
      inboxApi.getUnreadCount(token)
        .then((data) => setUnreadCount(data.total_unread || 0))
        .catch(() => {});
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 60000);
    return () => clearInterval(interval);
  }, [token]);

  // Check maintenance mode feature flag
  useEffect(() => {
    if (!token) return;
    flagsApi.getAll(token)
      .then((data) => {
        const maintenanceFlag = (data.flags || []).find(
          (f: FeatureFlag) => f.flag_name === 'maintenance_mode'
        );
        setMaintenanceMode(maintenanceFlag?.is_enabled || false);
        setFlagsLoaded(true);
      })
      .catch(() => {
        setFlagsLoaded(true);
      });
  }, [token]);

  const handleDismissAnnouncement = (id: string) => {
    setDismissedIds((prev) => new Set([...Array.from(prev), id]));
  };

  // Filter out dismissed announcements
  const visibleAnnouncements = announcements.filter(
    (a) => !dismissedIds.has(a.announcement_id)
  );

  // If maintenance mode is active and user is not admin, show maintenance screen
  if (flagsLoaded && maintenanceMode && !isAdmin) {
    return <MaintenanceScreen />;
  }

  // Check if running as standalone PWA
  const isStandalone = typeof window !== 'undefined' &&
    (window.matchMedia('(display-mode: standalone)').matches ||
     ('standalone' in window.navigator && (window.navigator as Navigator & { standalone?: boolean }).standalone));

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
            <UserMenu unreadCount={unreadCount} />
          </div>

          {/* Impersonation banner */}
          {isImpersonating && user && (
            <ImpersonationBanner username={user.username} email={user.email} />
          )}

          {/* Maintenance mode warning for admins */}
          {maintenanceMode && isAdmin && (
            <MaintenanceAdminBanner />
          )}
        </header>

        {/* Announcement banners - above main content, below header */}
        {!isAdmin && visibleAnnouncements.length > 0 && (
          <AnnouncementBanners
            announcements={visibleAnnouncements}
            onDismiss={handleDismissAnnouncement}
          />
        )}

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
