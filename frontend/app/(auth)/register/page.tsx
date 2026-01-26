'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await register(email, password);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Email may already be in use.');
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
      <div className="text-center mb-6">
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
        <h1 className="text-2xl font-bold text-frost">Create Your Account</h1>
        <p className="text-sm text-frost-muted mt-1">Join Bear's Den - it's free!</p>
      </div>

      {/* Benefits */}
      <div className="card p-4 mb-6">
        <ul className="space-y-2 text-sm text-frost-muted">
          <li className="flex items-center gap-2">
            <span className="text-ice">✓</span>
            Track your heroes, gear, and progress
          </li>
          <li className="flex items-center gap-2">
            <span className="text-ice">✓</span>
            Get AI-powered upgrade recommendations
          </li>
          <li className="flex items-center gap-2">
            <span className="text-ice">✓</span>
            Analyze pack values before buying
          </li>
        </ul>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
          {error}
        </div>
      )}

      {/* Register form */}
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
            placeholder="Min 6 characters"
            required
            autoComplete="new-password"
          />
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-frost-muted mb-1">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="input"
            placeholder="Re-enter password"
            required
            autoComplete="new-password"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full py-3"
        >
          {loading ? 'Creating account...' : 'Create Account'}
        </button>
      </form>

      {/* Login link */}
      <p className="mt-6 text-center text-sm text-frost-muted">
        Already have an account?{' '}
        <Link href="/login" className="text-ice hover:text-ice-light transition-colors">
          Sign in
        </Link>
      </p>

      {/* Footer */}
      <div className="mt-8 text-center space-y-3">
        <a
          href="https://randomchaoslabs.com"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-xs text-text-muted hover:text-ice transition-colors"
        >
          <span>🎲</span>
          <span>Random Chaos Labs</span>
        </a>

        <p className="text-xs text-text-muted px-4">
          Bear's Den is not affiliated with Century Games or Whiteout Survival.
        </p>
      </div>
    </div>
  );
}
