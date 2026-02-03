'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi, AdminUser } from '@/lib/api';

function AdminUsersContent() {
  const { token, user } = useAuth();
  const searchParams = useSearchParams();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('All');
  const [filterState, setFilterState] = useState('All States');
  const [filterTest, setFilterTest] = useState(searchParams.get('filter') === 'test');
  const [activeTab, setActiveTab] = useState<'list' | 'create'>('list');
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);

  useEffect(() => {
    if (token) {
      fetchUsers();
    }
  }, [token]);

  const fetchUsers = async () => {
    try {
      const data = await adminApi.listUsers(token!);
      setUsers(Array.isArray(data.users) ? data.users : Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleActive = async (userId: string, isActive: boolean) => {
    try {
      await adminApi.updateUser(token!, String(userId), { is_active: !isActive });
      fetchUsers();
    } catch (error) {
      console.error('Failed to toggle user status:', error);
    }
  };

  const handleCycleAI = async (userId: string, currentLevel: string) => {
    const nextLevel: Record<string, string> = {
      'off': 'limited',
      'limited': 'unlimited',
      'unlimited': 'off'
    };
    try {
      await adminApi.updateUser(token!, String(userId), { ai_access_level: nextLevel[currentLevel] || 'limited' } as any);
      fetchUsers();
    } catch (error) {
      console.error('Failed to update AI access:', error);
    }
  };

  const { impersonate } = useAuth();

  const handleImpersonate = async (userId: string) => {
    try {
      await impersonate(userId);
      // Redirect to home page after impersonation
      window.location.href = '/';
    } catch (error: any) {
      console.error('Failed to impersonate user:', error);
      alert('Failed to impersonate: ' + error.message);
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user? This cannot be undone!')) return;
    try {
      await adminApi.deleteUser(token!, String(userId));
      fetchUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  // Calculate stats
  const regularUsers = users.filter(u => u.role !== 'admin');
  const adminUsers = users.filter(u => u.role === 'admin');
  const activeIn7d = regularUsers.filter(u => u.usage_7d > 0).length;
  const uniqueStates = Array.from(new Set(users.flatMap(u => u.states || []))).sort((a, b) => a - b);
  const suspendedCount = users.filter(u => !u.is_active).length;
  const testCount = users.filter(u => u.is_test_account).length;

  // Filter users
  const filteredUsers = users
    .filter((u) => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!u.email.toLowerCase().includes(query) && !u.username.toLowerCase().includes(query)) {
          return false;
        }
      }
      // Status filter
      if (filterStatus === 'Active' && !u.is_active) return false;
      if (filterStatus === 'Suspended' && u.is_active) return false;
      if (filterStatus === 'Inactive (30d+)') {
        if (!u.last_login) return true; // Never logged in = inactive
        const lastLogin = new Date(u.last_login);
        const daysSince = Math.floor((Date.now() - lastLogin.getTime()) / (1000 * 60 * 60 * 24));
        if (daysSince < 30) return false;
      }
      // State filter
      if (filterState !== 'All States') {
        const targetState = parseInt(filterState);
        if (!u.states?.includes(targetState)) return false;
      }
      // Test filter
      if (filterTest && !u.is_test_account) return false;
      return true;
    })
    .sort((a, b) => {
      // Sort by last login (most recent first)
      if (!a.last_login && !b.last_login) return 0;
      if (!a.last_login) return 1;
      if (!b.last_login) return -1;
      return new Date(b.last_login).getTime() - new Date(a.last_login).getTime();
    });

  const formatLastLogin = (dateStr: string | null) => {
    if (!dateStr) return 'Never';
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return `${d.getMonth() + 1}/${d.getDate()}/${String(d.getFullYear()).slice(-2)}`;
  };

  const getUsageColor = (days: number) => {
    if (days >= 5) return 'bg-success';
    if (days >= 2) return 'bg-warning';
    return 'bg-error';
  };

  const getStatusInfo = (u: AdminUser) => {
    if (!u.is_active) return { label: 'Suspended', class: 'text-error' };
    if (!u.last_login) return { label: 'Inactive', class: 'text-frost-muted' };
    const lastLogin = new Date(u.last_login);
    const daysSince = Math.floor((Date.now() - lastLogin.getTime()) / (1000 * 60 * 60 * 24));
    if (daysSince > 30) return { label: 'Inactive', class: 'text-frost-muted' };
    return { label: 'Active', class: 'text-success' };
  };

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">🔒</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
          <p className="text-frost-muted">You don't have permission to view this page.</p>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-7xl mx-auto animate-fadeIn">
        {/* Header */}
        <h1 className="text-3xl font-bold text-frost mb-6">👥 User Management</h1>

        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-3 mb-6">
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-frost">{regularUsers.length}</p>
            <p className="text-xs text-frost-muted">Total Users</p>
          </div>
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-fire">{adminUsers.length}</p>
            <p className="text-xs text-frost-muted">Admins</p>
          </div>
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-success">{activeIn7d}</p>
            <p className="text-xs text-frost-muted">Active (7d)</p>
          </div>
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-ice">{uniqueStates.length}</p>
            <p className="text-xs text-frost-muted">States</p>
          </div>
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-error">{suspendedCount}</p>
            <p className="text-xs text-frost-muted">Suspended</p>
          </div>
          <div className="card text-center py-3">
            <p className="text-2xl font-bold text-warning">{testCount}</p>
            <p className="text-xs text-frost-muted">Test Accts</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setActiveTab('list')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'list'
                ? 'bg-ice/20 text-ice border border-ice/30'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            📋 User Database
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'create'
                ? 'bg-ice/20 text-ice border border-ice/30'
                : 'text-frost-muted hover:text-frost hover:bg-surface'
            }`}
          >
            ➕ Create User
          </button>
        </div>

        {activeTab === 'list' ? (
          <>
            {/* Filters */}
            <div className="card mb-4">
              <div className="flex flex-wrap gap-3 items-center">
                <div className="flex-1 min-w-[200px]">
                  <input
                    type="text"
                    placeholder="🔍 Search username or email..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input text-sm"
                  />
                </div>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="input w-auto text-sm"
                >
                  <option>All</option>
                  <option>Active</option>
                  <option>Suspended</option>
                  <option>Inactive (30d+)</option>
                </select>
                <select
                  value={filterState}
                  onChange={(e) => setFilterState(e.target.value)}
                  className="input w-auto text-sm"
                >
                  <option>All States</option>
                  {uniqueStates.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
                <label className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filterTest}
                    onChange={(e) => setFilterTest(e.target.checked)}
                    className="w-4 h-4 rounded border-surface-border"
                  />
                  <span className="text-sm text-frost-muted">Test Only</span>
                </label>
              </div>
            </div>

            <p className="text-sm text-frost-muted mb-2">Showing {filteredUsers.length} users</p>

            {/* Users Table */}
            <div className="card overflow-hidden">
              {isLoading ? (
                <div className="space-y-4 p-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="flex items-center gap-4 animate-pulse">
                      <div className="w-8 h-8 rounded-full bg-surface-hover" />
                      <div className="flex-1">
                        <div className="h-4 bg-surface-hover rounded w-48 mb-2" />
                        <div className="h-3 bg-surface-hover rounded w-32" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : filteredUsers.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">👥</div>
                  <p className="text-frost-muted">No users found</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-surface-border">
                        <th className="text-center p-2 text-xs font-medium text-frost-muted w-10">Role</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted">User</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted w-16">Profiles</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted w-20">State(s)</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted w-20">Status</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted w-16">Usage</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted w-20">Last</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted w-12">AI</th>
                        <th className="text-center p-2 text-xs font-medium text-frost-muted">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredUsers.map((u) => {
                        const status = getStatusInfo(u);
                        const isSelf = u.id === user?.id;
                        return (
                          <tr key={u.id} className="border-b border-surface-border/50 hover:bg-surface/50">
                            {/* Role */}
                            <td className="p-2 text-center">
                              <span title={u.role === 'admin' ? 'Admin' : 'User'}>
                                {u.role === 'admin' ? '👑' : '🛡️'}
                              </span>
                            </td>
                            {/* User */}
                            <td className="p-2">
                              <div className="text-xs">
                                <span className="font-medium text-frost">{u.username}</span>
                                {u.is_test_account && (
                                  <code className="ml-1 px-1 py-0.5 bg-warning/20 text-warning text-[10px] rounded">TEST</code>
                                )}
                                {isSelf && (
                                  <span className="ml-1 text-frost-muted italic">(you)</span>
                                )}
                              </div>
                            </td>
                            {/* Profiles */}
                            <td className="p-2 text-center text-frost-muted text-xs">
                              {u.profile_count || 0}
                            </td>
                            {/* States */}
                            <td className="p-2 text-center text-frost-muted text-xs">
                              {u.states?.length > 0 ? u.states.join(', ') : '—'}
                            </td>
                            {/* Status */}
                            <td className={`p-2 text-center text-xs ${status.class}`}>
                              {status.label}
                            </td>
                            {/* Usage */}
                            <td className="p-2">
                              <div className="flex items-center justify-center gap-0.5">
                                {[...Array(7)].map((_, i) => (
                                  <div
                                    key={i}
                                    className={`w-1.5 h-3 rounded-sm ${
                                      i < (u.usage_7d || 0) ? getUsageColor(u.usage_7d || 0) : 'bg-surface-hover'
                                    }`}
                                  />
                                ))}
                              </div>
                            </td>
                            {/* Last Login */}
                            <td className="p-2 text-center text-frost-muted text-xs">
                              {formatLastLogin(u.last_login)}
                            </td>
                            {/* AI */}
                            <td className="p-2 text-center">
                              {u.role !== 'admin' ? (
                                <div className="flex flex-col items-center gap-0.5">
                                  <button
                                    onClick={() => handleCycleAI(u.id, u.ai_access_level || 'limited')}
                                    className={`px-2 py-0.5 text-[10px] rounded font-medium ${
                                      u.ai_access_level === 'off' ? 'bg-surface text-frost-muted' :
                                      u.ai_access_level === 'unlimited' ? 'bg-warning/20 text-warning' :
                                      u.ai_daily_limit ? 'bg-ice/20 text-ice' : 'bg-success/20 text-success'
                                    }`}
                                  >
                                    {u.ai_access_level === 'off' ? 'Off' :
                                     u.ai_access_level === 'unlimited' ? 'Unl' :
                                     u.ai_daily_limit ? 'Custom' : 'Ltd'}
                                  </button>
                                  {u.ai_access_level === 'limited' && u.ai_daily_limit && (
                                    <span className="text-[9px] text-ice">{u.ai_requests_today}/{u.ai_daily_limit}</span>
                                  )}
                                </div>
                              ) : (
                                <span className="text-frost-muted text-xs">—</span>
                              )}
                            </td>
                            {/* Actions */}
                            <td className="p-2">
                              <div className="flex items-center justify-center gap-1">
                                <button
                                  onClick={() => setEditingUser(u)}
                                  className="px-2 py-1 text-[10px] text-ice hover:bg-ice/10 rounded transition-colors"
                                >
                                  Edit
                                </button>
                                {!isSelf && (
                                  <>
                                    <button
                                      onClick={() => handleImpersonate(u.id)}
                                      className="px-2 py-1 text-[10px] text-ice hover:bg-ice/10 rounded transition-colors"
                                    >
                                      Login
                                    </button>
                                    <button
                                      onClick={() => handleToggleActive(u.id, u.is_active)}
                                      className={`px-2 py-1 text-[10px] rounded transition-colors ${
                                        u.is_active
                                          ? 'text-warning hover:bg-warning/10'
                                          : 'text-success hover:bg-success/10'
                                      }`}
                                    >
                                      {u.is_active ? 'Suspend' : 'Activate'}
                                    </button>
                                    <button
                                      onClick={() => handleDelete(u.id)}
                                      className="px-2 py-1 text-[10px] text-error hover:bg-error/10 rounded transition-colors"
                                    >
                                      Delete
                                    </button>
                                  </>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        ) : (
          <CreateUserForm token={token || ''} onCreated={() => { setActiveTab('list'); fetchUsers(); }} />
        )}

        {/* Edit User Modal */}
        {editingUser && (
          <EditUserModal
            token={token || ''}
            user={editingUser}
            onClose={() => setEditingUser(null)}
            onUpdated={() => {
              setEditingUser(null);
              fetchUsers();
            }}
          />
        )}
      </div>
    </PageLayout>
  );
}

// Create User Form Component
function CreateUserForm({ token, onCreated }: { token: string; onCreated: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const [isTestAccount, setIsTestAccount] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email || !email.includes('@') || !email.includes('.')) {
      setError('Invalid email format');
      return;
    }
    if (!password || password.length < 6) {
      setError('Password must be 6+ characters');
      return;
    }

    setIsLoading(true);
    try {
      await adminApi.createUser(token, {
        email,
        password,
        role,
        is_test_account: isTestAccount,
      });

      setSuccess(`Created user: ${email}${isTestAccount ? ' (test account)' : ''}`);
      setEmail('');
      setPassword('');
      setRole('user');
      setIsTestAccount(false);
      onCreated();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card max-w-lg">
      <h2 className="text-xl font-bold text-frost mb-4">Create New User</h2>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 rounded-lg bg-success/20 border border-success/30 text-success text-sm">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">Email *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              placeholder="user@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="input"
            >
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">Password *</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              required
              minLength={6}
            />
          </div>
          <div className="flex items-end pb-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isTestAccount}
                onChange={(e) => setIsTestAccount(e.target.checked)}
                className="w-4 h-4 rounded border-surface-border"
              />
              <span className="text-sm text-frost-muted">Test Account</span>
            </label>
          </div>
        </div>

        <p className="text-xs text-frost-muted">Email is used as login credential</p>

        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full"
        >
          {isLoading ? 'Creating...' : '➕ Create User'}
        </button>
      </form>
    </div>
  );
}

// Edit User Modal Component
function EditUserModal({
  token,
  user,
  onClose,
  onUpdated,
}: {
  token: string;
  user: AdminUser;
  onClose: () => void;
  onUpdated: () => void;
}) {
  const [email, setEmail] = useState(user.email);
  const [isTestAccount, setIsTestAccount] = useState(user.is_test_account);
  const [isAdmin, setIsAdmin] = useState(user.role === 'admin');
  const [aiAccessLevel, setAiAccessLevel] = useState<'off' | 'limited' | 'unlimited'>(user.ai_access_level || 'limited');
  const [aiDailyLimit, setAiDailyLimit] = useState<string>(user.ai_daily_limit?.toString() || '');
  const [newPassword, setNewPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await adminApi.updateUser(token, String(user.id), {
        email,
        is_test_account: isTestAccount,
        role: isAdmin ? 'admin' : 'user',
      } as any);

      onUpdated();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-xl border border-surface-border max-w-md w-full p-6 animate-fadeIn">
        <h2 className="text-xl font-bold text-frost mb-4">Edit User</h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-frost-muted mb-1">
              New Password (leave blank to keep current)
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="input"
              minLength={6}
              placeholder="Enter new password..."
            />
          </div>

          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isTestAccount}
                onChange={(e) => setIsTestAccount(e.target.checked)}
                className="w-4 h-4 rounded border-surface-border"
              />
              <span className="text-sm text-frost-muted">Test</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isAdmin}
                onChange={(e) => setIsAdmin(e.target.checked)}
                className="w-4 h-4 rounded border-surface-border"
              />
              <span className="text-sm text-frost-muted">Admin</span>
            </label>
          </div>

          {/* AI Access Level */}
          <div>
            <label className="block text-sm font-medium text-frost-muted mb-2">AI Access Level</label>
            <div className="flex gap-2">
              {(['off', 'limited', 'unlimited'] as const).map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setAiAccessLevel(level)}
                  className={`flex-1 p-2 rounded-lg text-sm font-medium transition-colors ${
                    aiAccessLevel === level
                      ? level === 'off' ? 'bg-error/20 text-error border border-error/30'
                        : level === 'unlimited' ? 'bg-warning/20 text-warning border border-warning/30'
                        : 'bg-success/20 text-success border border-success/30'
                      : 'bg-surface text-frost-muted hover:bg-surface-hover'
                  }`}
                >
                  {level === 'off' ? '🚫 Off' : level === 'limited' ? '📊 Limited' : '♾️ Unlimited'}
                </button>
              ))}
            </div>
          </div>

          {/* Custom Daily Limit */}
          {aiAccessLevel === 'limited' && (
            <div>
              <label className="block text-sm font-medium text-frost-muted mb-2">
                Custom Daily Limit
              </label>
              <input
                type="number"
                value={aiDailyLimit}
                onChange={(e) => setAiDailyLimit(e.target.value)}
                className="input"
                placeholder="Leave blank for global default"
                min={1}
              />
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary flex-1"
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function AdminUsersPage() {
  return (
    <Suspense fallback={<PageLayout><div className="text-center py-16">Loading...</div></PageLayout>}>
      <AdminUsersContent />
    </Suspense>
  );
}
