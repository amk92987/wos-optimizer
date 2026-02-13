'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { inboxApi } from '@/lib/api';
import { useState, useEffect, useCallback } from 'react';

// Navigation structure matching Streamlit
const userNavigation = [
  {
    label: 'Overview',
    items: [
      { href: '/', label: 'Home', icon: '🏠' },
      { href: '/beginner-guide', label: 'Beginner Guide', icon: '📖' },
    ],
  },
  {
    label: 'Tracker',
    items: [
      { href: '/heroes', label: 'Hero Tracker', icon: '🦸' },
      { href: '/chief', label: 'Chief Tracker', icon: '👑' },
    ],
  },
  {
    label: 'Analytics',
    items: [
      { href: '/advisor', label: 'AI Advisor', icon: '🤖' },
      { href: '/upgrades', label: 'Upgrades', icon: '📈' },
      { href: '/lineups', label: 'Lineups', icon: '⚔️' },
      { href: '/packs', label: 'Packs', icon: '📦' },
    ],
  },
  {
    label: 'Guides',
    items: [
      { href: '/backpack', label: 'Backpack', icon: '🎒' },
      { href: '/events', label: 'Events', icon: '📅' },
      { href: '/combat', label: 'Combat', icon: '⚔️' },
      { href: '/quick-tips', label: 'Quick Tips', icon: '💡' },
      { href: '/battle-tactics', label: 'Battle Tactics', icon: '🎯' },
      { href: '/daybreak', label: 'Daybreak Island', icon: '🏝️' },
    ],
  },
  {
    label: 'Account',
    items: [
      { href: '/inbox', label: 'Inbox', icon: '📬' },
      { href: '/profiles', label: 'Profiles', icon: '💾' },
      { href: '/settings', label: 'Settings', icon: '⚙️' },
    ],
  },
];

const adminNavigation = [
  {
    label: 'Overview',
    items: [
      { href: '/admin', label: 'Dashboard', icon: '📊' },
      { href: '/admin/users', label: 'Users', icon: '👥' },
    ],
  },
  {
    label: 'Communication',
    items: [
      { href: '/admin/announcements', label: 'Announcements', icon: '📢' },
      { href: '/admin/inbox', label: 'Inbox', icon: '📬' },
    ],
  },
  {
    label: 'System',
    items: [
      { href: '/admin/feature-flags', label: 'Feature Flags', icon: '🚩' },
      { href: '/admin/ai', label: 'AI Settings', icon: '🤖' },
      { href: '/admin/audit-log', label: 'Audit Log', icon: '📋' },
      { href: '/admin/database', label: 'Database', icon: '🗄️' },
      { href: '/admin/data-integrity', label: 'Data Integrity', icon: '✅' },
    ],
  },
  {
    label: 'Data',
    items: [
      { href: '/admin/game-data', label: 'Game Data', icon: '🎮' },
      { href: '/admin/usage-reports', label: 'Usage Reports', icon: '📈' },
      { href: '/admin/export', label: 'Export', icon: '📤' },
    ],
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, token } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [userUnreadCount, setUserUnreadCount] = useState(0);
  const [adminUnreadCount, setAdminUnreadCount] = useState(0);

  // Fetch unread notification count
  const fetchUnreadCount = useCallback(async () => {
    if (!token) return;
    try {
      const data = await inboxApi.getUnreadCount(token);
      setUserUnreadCount(data.unread_notifications);
      setAdminUnreadCount(data.error_count || 0);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }, [token]);

  // Fetch unread count on mount and periodically
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  // Persist collapsed state
  useEffect(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    if (saved) {
      setIsCollapsed(saved === 'true');
    }
  }, []);

  const toggleCollapse = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    localStorage.setItem('sidebar-collapsed', String(newState));
  };

  const isAdmin = user?.role === 'admin';
  const isAdminRoute = pathname?.startsWith('/admin');
  const navigation = isAdminRoute ? adminNavigation : userNavigation;

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed md:sticky top-0 left-0 z-50 md:z-auto
          ${isCollapsed ? 'w-16' : 'w-64'}
          h-full md:h-screen
          bg-gradient-sidebar border-r border-surface-border
          flex flex-col
          transform transition-all duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Logo and collapse toggle */}
        <div className="p-3 border-b border-surface-border/50">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3" onClick={onClose}>
              <div className="relative w-10 h-10 flex-shrink-0">
                <Image
                  src="/icons/bear_paw.png"
                  alt="Bear's Den"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
              {!isCollapsed && (
                <div>
                  <h1 className="font-bold text-frost text-lg flex items-start gap-0.5">
                    Bear's Den
                    <svg className="w-4 h-4 text-ice drop-shadow-[0_0_6px_rgba(74,144,217,0.8)] -mt-1" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2L12 22M2 12L22 12M4.93 4.93L19.07 19.07M19.07 4.93L4.93 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none"/>
                      <circle cx="12" cy="12" r="2" fill="currentColor"/>
                    </svg>
                  </h1>
                </div>
              )}
            </Link>
            {/* Collapse toggle - desktop only */}
            <button
              onClick={toggleCollapse}
              className="hidden md:flex w-8 h-8 items-center justify-center rounded-lg
                         text-text-secondary hover:text-frost hover:bg-surface/50 transition-colors"
              title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              <svg
                className={`w-4 h-4 transition-transform ${isCollapsed ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
          </div>
        </div>


        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-2">
          {navigation.map((group) => (
            <div key={group.label} className={`${isCollapsed ? 'px-2' : 'px-3'} py-2`}>
              {!isCollapsed && (
                <p className="px-3 mb-1 text-xs font-semibold text-text-muted uppercase tracking-wider">
                  {group.label}
                </p>
              )}
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const isActive = pathname === item.href;
                  const isUserInbox = item.href === '/inbox';
                  const isAdminInbox = item.href === '/admin/inbox';
                  const badgeCount = isUserInbox ? userUnreadCount : isAdminInbox ? (userUnreadCount + adminUnreadCount) : 0;
                  const showBadge = badgeCount > 0;

                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={onClose}
                        className={`
                          flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}
                          ${isCollapsed ? 'px-2' : 'px-3'} py-2 rounded-lg
                          transition-all duration-200 text-sm relative
                          ${
                            isActive
                              ? 'bg-ice/10 text-ice border border-ice/20'
                              : 'text-text-secondary hover:text-frost hover:bg-surface/50'
                          }
                        `}
                        title={isCollapsed ? item.label : undefined}
                      >
                        <span className={`${isCollapsed ? 'text-lg' : 'text-base'} relative`}>
                          {item.icon}
                          {showBadge && isCollapsed && (
                            <span className="absolute -top-1 -right-1 w-4 h-4 bg-error text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                              {badgeCount > 9 ? '9+' : badgeCount}
                            </span>
                          )}
                        </span>
                        {!isCollapsed && (
                          <>
                            <span className="font-medium flex-1">{item.label}</span>
                            {showBadge && (
                              <span className="w-5 h-5 bg-error text-white text-xs font-bold rounded-full flex items-center justify-center">
                                {badgeCount > 9 ? '9+' : badgeCount}
                              </span>
                            )}
                          </>
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* Footer with Admin Mode indicator and Random Chaos Labs */}
        <div className="mt-auto">
          {/* Admin Mode - above the divider */}
          {isAdminRoute && !isCollapsed && (
            <div className="px-4 py-2 text-center">
              <span className="text-sm font-medium text-fire">Admin Mode</span>
            </div>
          )}
          {isAdminRoute && isCollapsed && (
            <div className="p-2 text-center">
              <span className="text-xs text-fire" title="Admin Mode">⚙️</span>
            </div>
          )}

          {/* Divider and Random Chaos Labs */}
          <div className="border-t border-surface-border/50">
            {!isCollapsed ? (
              <div className="p-4 text-center">
                <a
                  href="https://randomchaoslabs.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2"
                >
                  <span className="text-2xl">🎲</span>
                  <span className="text-sm font-bold animate-gold-shine">Random Chaos Labs</span>
                </a>
              </div>
            ) : (
              <div className="p-2 text-center">
                <a
                  href="https://randomchaoslabs.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-2xl hover:scale-110 transition-transform inline-block"
                  title="Random Chaos Labs"
                >
                  🎲
                </a>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
