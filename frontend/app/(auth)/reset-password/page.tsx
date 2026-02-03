'use client';

import { useState, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (!token) {
      setError('Invalid or missing reset token. Please request a new reset link.');
      return;
    }

    setLoading(true);

    try {
      await api('/api/auth/reset-password', {
        method: 'POST',
        body: { token, new_password: newPassword },
      });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to reset password. The link may have expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-sm animate-fade-in">
      {/* Back link */}
      <Link
        href="/login"
        className="inline-flex items-center gap-2 text-sm text-ice hover:text-ice-light transition-colors mb-6"
      >
        &larr; Back to Sign In
      </Link>

      {/* Logo */}
      <div className="text-center mb-8">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 50 50"
          className="w-14 h-14 mx-auto mb-3"
        >
          <defs>
            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style={{ stopColor: '#7DD3FC' }} />
              <stop offset="100%" style={{ stopColor: '#E8F4F8' }} />
            </linearGradient>
          </defs>
          <circle cx="25" cy="28" r="12" fill="url(#logoGrad)" />
          <circle cx="12" cy="15" r="6" fill="url(#logoGrad)" />
          <circle cx="25" cy="8" r="6" fill="url(#logoGrad)" />
          <circle cx="38" cy="15" r="6" fill="url(#logoGrad)" />
        </svg>
        <h1 className="text-2xl font-bold text-frost">Set New Password</h1>
        <p className="text-sm text-frost-muted mt-1">
          Choose a new password for your account
        </p>
      </div>

      {/* No token warning */}
      {!token && !success && (
        <div className="mb-4 p-3 rounded-lg bg-amber-500/20 border border-amber-500/30 text-amber-400 text-sm">
          No reset token found. Please use the link from your email, or{' '}
          <Link href="/forgot-password" className="underline">request a new one</Link>.
        </div>
      )}

      {/* Success message */}
      {success ? (
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-green-500/20 border border-green-500/30 text-green-400 text-sm">
            Your password has been reset successfully. You can now sign in with your new password.
          </div>
          <Link
            href="/login"
            className="btn-primary w-full py-3 block text-center"
          >
            Sign In
          </Link>
        </div>
      ) : (
        <>
          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
              {error}
            </div>
          )}

          {/* Reset password form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-frost-muted mb-1">
                New Password
              </label>
              <input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="input"
                placeholder="At least 8 characters"
                required
                minLength={8}
                autoComplete="new-password"
                autoFocus
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-frost-muted mb-1">
                Confirm New Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input"
                placeholder="Re-enter your new password"
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !token}
              className="btn-primary w-full py-3"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        </>
      )}

      {/* Footer */}
      <div className="mt-8 text-center">
        <a
          href="https://randomchaoslabs.com"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-xs text-text-muted hover:text-ice transition-colors"
        >
          <span>Random Chaos Labs</span>
        </a>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="w-full max-w-sm animate-fade-in">
        <div className="text-center">
          <div className="h-14 w-14 mx-auto mb-3 bg-surface rounded-full animate-pulse"></div>
          <div className="h-8 bg-surface rounded w-48 mx-auto mb-2 animate-pulse"></div>
          <div className="h-4 bg-surface rounded w-64 mx-auto animate-pulse"></div>
        </div>
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}
