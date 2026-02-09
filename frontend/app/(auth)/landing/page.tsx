'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useState } from 'react';

const problemCards = [
  {
    emoji: '💸',
    title: 'Spending Without Progress',
    description: '"I keep buying packs but I\'m not getting any stronger..."',
  },
  {
    emoji: '😵‍💫',
    title: 'Hero Overload',
    description: '"I have 20+ heroes and no idea which ones to upgrade next."',
  },
  {
    emoji: '💀',
    title: 'Losing Battles',
    description: '"My rally got crushed. What lineup should I be using?"',
  },
];

const features = [
  {
    emoji: '🤖',
    title: 'AI-Powered Advisor',
    description: 'Get personalized upgrade recommendations based on your account, spending level, and goals.',
  },
  {
    emoji: '📦',
    title: 'Pack Value Analyzer',
    description: 'Know exactly what you\'re getting before you spend. Compare pack values instantly.',
  },
  {
    emoji: '🦸',
    title: 'Hero Tracker',
    description: 'Track all your heroes, their levels, skills, and gear in one organized place.',
  },
  {
    emoji: '⚔️',
    title: 'Lineup Builder',
    description: 'Build optimal lineups for Bear Trap, Crazy Joe, SvS, garrison, and more.',
  },
  {
    emoji: '👑',
    title: 'Chief Gear & Charms',
    description: 'Track your chief gear progression and charm levels across all slots.',
  },
  {
    emoji: '📚',
    title: 'Strategy Guides',
    description: 'Access quick tips, battle tactics, event guides, and Daybreak Island strategies.',
  },
];

// Snowflake component
function Snowflake({ style, char }: { style: React.CSSProperties; char: string }) {
  return (
    <div
      className="absolute text-white/20 pointer-events-none animate-drift"
      style={style}
    >
      {char}
    </div>
  );
}

export default function LandingPage() {
  const [snowflakes, setSnowflakes] = useState<Array<{ id: number; style: React.CSSProperties; char: string }>>([]);

  useEffect(() => {
    // Generate snowflakes on mount
    const chars = ['❄', '❅', '❆'];
    const flakes = Array.from({ length: 20 }, (_, i) => ({
      id: i,
      char: chars[i % chars.length],
      style: {
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        fontSize: `${12 + Math.random() * 20}px`,
        animationDelay: `${Math.random() * 8}s`,
        animationDuration: `${6 + Math.random() * 4}s`,
      },
    }));
    setSnowflakes(flakes);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-landing overflow-hidden relative">
      {/* Snowflakes */}
      {snowflakes.map((flake) => (
        <Snowflake key={flake.id} style={flake.style} char={flake.char} />
      ))}

      {/* Header */}
      <header className="relative z-10 px-6 py-4">
        <nav className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 relative">
              <Image
                src="/icons/bear_paw.png"
                alt="Bear's Den"
                fill
                className="object-contain"
              />
            </div>
            <span className="text-xl font-bold text-frost hidden sm:block">Bear's Den</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-4 py-2 text-sm font-medium text-ice border border-ice/30 rounded-lg
                         hover:bg-ice/10 transition-all duration-300"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-ice to-sky-500
                         rounded-lg shadow-glow hover:shadow-glow-lg hover:-translate-y-0.5
                         transition-all duration-300"
            >
              Get Started Free
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 px-6 py-16 md:py-24 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-frost mb-6 drop-shadow-glow">
            Stop Guessing.<br />
            <span className="text-ice">Start Dominating.</span>
          </h1>
          <p className="text-lg md:text-xl text-frost-muted max-w-2xl mx-auto mb-8">
            Bear's Den is your strategic advisor for Whiteout Survival.
            We analyze your account and tell you exactly what to upgrade,
            what to buy, and how to win.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/register"
              className="px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-ice to-sky-500
                         rounded-xl shadow-glow-lg hover:shadow-glow-xl hover:-translate-y-1
                         transition-all duration-300"
            >
              Get Started Free
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 text-lg font-semibold text-ice border-2 border-ice/40 rounded-xl
                         hover:bg-ice/10 hover:border-ice/60 transition-all duration-300"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="relative z-10 px-6 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-frost text-center mb-4">
            Sound Familiar?
          </h2>
          <p className="text-frost-muted text-center mb-10 max-w-xl mx-auto">
            Every Chief faces these challenges. You're not alone.
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {problemCards.map((card, i) => (
              <div
                key={i}
                className="card-glass p-6 text-center hover:scale-105 transition-transform duration-300"
              >
                <div className="text-4xl mb-4">{card.emoji}</div>
                <h3 className="text-lg font-semibold text-frost mb-2">{card.title}</h3>
                <p className="text-sm text-frost-muted italic">{card.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="relative z-10 px-6 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-frost mb-4">
            Your Strategic Advisor in Your Pocket
          </h2>
          <p className="text-frost-muted text-lg max-w-2xl mx-auto">
            Bear's Den analyzes your heroes, gear, and progress to give you
            personalized recommendations. No more guessing. No more wasted resources.
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative z-10 px-6 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-frost text-center mb-12">
            Everything You Need to Dominate
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <div
                key={i}
                className="card-glass p-6 text-center hover:scale-105 hover:border-ice/40 transition-all duration-300"
              >
                <div className="text-3xl mb-4">{feature.emoji}</div>
                <h3 className="text-lg font-semibold text-frost mb-2">{feature.title}</h3>
                <p className="text-sm text-frost-muted">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-frost mb-6">
            Ready to Level Up Your Game?
          </h2>
          <p className="text-frost-muted text-lg mb-8">
            Join thousands of Chiefs who've stopped guessing and started winning.
          </p>
          <Link
            href="/register"
            className="inline-block px-10 py-4 text-xl font-bold text-white
                       bg-gradient-to-r from-ice to-sky-500 rounded-xl
                       shadow-glow-xl hover:shadow-glow-2xl hover:-translate-y-1
                       transition-all duration-300"
          >
            Get Started Free
          </Link>
          <p className="text-sm text-frost-muted mt-4">
            No credit card required. Free forever.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-12 border-t border-ice/10">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="text-2xl">🎲</span>
            <a
              href="https://randomchaoslabs.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-ice hover:text-ice-light transition-colors"
            >
              Random Chaos Labs
            </a>
          </div>
          <div className="card-glass p-4 mb-6 text-xs text-frost-muted">
            Bear's Den is not affiliated with, endorsed by, or connected to Century Games
            or Whiteout Survival. All trademarks are property of their respective owners.
            Use at your own risk.
          </div>
          <p className="text-sm text-frost-muted">
            © 2025 Random Chaos Labs. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
