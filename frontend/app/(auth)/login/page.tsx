'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-sm animate-fade-in">
      {/* Back link */}
      <Link
        href="/landing"
        className="inline-flex items-center gap-2 text-sm text-ice hover:text-ice-light transition-colors mb-6"
      >
        ← Back to Home
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
        <h1 className="text-2xl font-bold text-frost">Welcome Back</h1>
        <p className="text-sm text-frost-muted mt-1">Sign in to Bear's Den</p>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
          {error}
        </div>
      )}

      {/* Login form */}
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

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-frost-muted mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
            placeholder="Enter your password"
            required
            autoComplete="current-password"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full py-3"
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>

      {/* Forgot password link */}
      <p className="mt-4 text-center text-sm">
        <Link href="/forgot-password" className="text-ice hover:text-ice-light transition-colors">
          Forgot your password?
        </Link>
      </p>

      {/* Register link */}
      <p className="mt-6 text-center text-sm text-frost-muted">
        Don't have an account?{' '}
        <Link href="/register" className="text-ice hover:text-ice-light transition-colors">
          Create one
        </Link>
      </p>

      {/* Footer */}
      <div className="mt-8 text-center">
        <a
          href="https://randomchaoslabs.com"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-xs text-text-muted hover:text-ice transition-colors"
        >
          <span>🎲</span>
          <span>Random Chaos Labs</span>
        </a>
      </div>
    </div>
  );
}
