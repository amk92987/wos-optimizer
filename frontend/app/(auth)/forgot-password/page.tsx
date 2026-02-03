'use client';

import { useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api('/api/auth/forgot-password', {
        method: 'POST',
        body: { email },
      });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.');
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
        <h1 className="text-2xl font-bold text-frost">Reset Password</h1>
        <p className="text-sm text-frost-muted mt-1">
          Enter your email to receive a reset link
        </p>
      </div>

      {/* Success message */}
      {success ? (
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-green-500/20 border border-green-500/30 text-green-400 text-sm">
            If an account exists with that email, we've sent a password reset link.
            Please check your inbox.
          </div>
          <Link
            href="/login"
            className="btn-primary w-full py-3 block text-center"
          >
            Back to Sign In
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

          {/* Forgot password form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-frost-muted mb-1">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="your@email.com"
                required
                autoComplete="email"
                autoFocus
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>

          {/* Back to login */}
          <p className="mt-6 text-center text-sm text-frost-muted">
            Remember your password?{' '}
            <Link href="/login" className="text-ice hover:text-ice-light transition-colors">
              Sign in
            </Link>
          </p>
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
