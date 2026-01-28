'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import AppShell from '@/components/AppShell';
import { useAuth } from '@/lib/auth';
import { MetricCard } from '@/components/ui';

// Generation thresholds for server age estimation
const GEN_THRESHOLDS = [
  { gen: 1, minDays: 0, maxDays: 40 },
  { gen: 2, minDays: 40, maxDays: 120 },
  { gen: 3, minDays: 120, maxDays: 200 },
  { gen: 4, minDays: 200, maxDays: 280 },
  { gen: 5, minDays: 280, maxDays: 360 },
  { gen: 6, minDays: 360, maxDays: 440 },
  { gen: 7, minDays: 440, maxDays: 520 },
  { gen: 8, minDays: 520, maxDays: 600 },
  { gen: 9, minDays: 600, maxDays: 680 },
  { gen: 10, minDays: 680, maxDays: 760 },
  { gen: 11, minDays: 760, maxDays: 840 },
  { gen: 12, minDays: 840, maxDays: 920 },
  { gen: 13, minDays: 920, maxDays: 1000 },
  { gen: 14, minDays: 1000, maxDays: 1080 },
];

// Get generation from server age
function getGenerationFromDays(days: number): number {
  for (const t of GEN_THRESHOLDS) {
    if (days < t.maxDays) return t.gen;
  }
  return 14 + Math.floor((days - 1080) / 80);
}

// Get estimated server age range from generation
function getEstimatedDaysFromGeneration(gen: number): string {
  const threshold = GEN_THRESHOLDS.find(t => t.gen === gen);
  if (threshold) {
    return `${threshold.minDays}-${threshold.maxDays}`;
  }
  if (gen > 14) {
    const minDays = 1080 + (gen - 14) * 80;
    return `${minDays}+`;
  }
  return '?';
}

// Generation data with colors
const generations = [
  { gen: 1, days: '0-40', heroes: 'Jessie, Sergey, Natalia, Molly, Jeronimo...', color: 'bg-blue-600' },
  { gen: 2, days: '40-120', heroes: 'Alonso, Flint, Philly', color: 'bg-blue-500' },
  { gen: 3, days: '120-200', heroes: 'Logan, Mia, Greg', color: 'bg-cyan-600' },
  { gen: 4, days: '200-280', heroes: 'Ahmose, Lynn, Reina', color: 'bg-cyan-500' },
  { gen: 5, days: '280-360', heroes: 'Gwen, Hector, Norah', color: 'bg-teal-600' },
  { gen: 6, days: '360-440', heroes: 'Wu Ming, Renee, Wayne', color: 'bg-teal-500' },
  { gen: 7, days: '440-520', heroes: 'Bradley, Edith, Gordon', color: 'bg-green-600' },
  { gen: 8, days: '520-600', heroes: 'Gatot, Hendrik, Sonya', color: 'bg-green-500' },
  { gen: 9, days: '600-680', heroes: 'Fred, Magnus, Xura', color: 'bg-yellow-600' },
  { gen: 10, days: '680-760', heroes: 'Blanchette, Freya, Gregory', color: 'bg-yellow-500' },
  { gen: 11, days: '760-840', heroes: 'Eleonora, Lloyd, Rufus', color: 'bg-orange-600' },
  { gen: 12, days: '840-920', heroes: 'Hervor, Karol, Ligeia', color: 'bg-orange-500' },
  { gen: 13, days: '920-1000', heroes: 'Flora, Gisela, Vulcanus', color: 'bg-red-600' },
  { gen: 14, days: '1000+', heroes: 'Cara, Dominic, Elif', color: 'bg-red-500' },
];

interface DashboardStats {
  generation: number;
  server_age_days: number;
  furnace_display: string;
  owned_heroes: number;
  total_heroes: number;
  username?: string;
}

export default function HomePage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);

  // Redirect to landing if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/landing');
    }
  }, [isLoading, user, router]);

  // Fetch dashboard stats
  useEffect(() => {
    if (token) {
      fetch('http://localhost:8000/api/dashboard/stats', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then(setStats)
        .catch(console.error);
    }
  }, [token]);

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-ice border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-text-secondary">Loading...</p>
        </div>
      </div>
    );
  }

  const displayName = stats?.username || user.email?.split('@')[0] || 'Chief';

  return (
    <AppShell>
      <div className="max-w-5xl mx-auto">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-frost">
            Welcome back, {displayName}!
          </h1>
        </div>

        {/* Quick Start & Status */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Quick Start */}
          <div className="md:col-span-2 card">
            <h2 className="section-header">Quick Start</h2>
            <ul className="space-y-2 text-sm text-frost-muted mb-4">
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span><strong className="text-frost">Hero Tracker</strong> - Track heroes, levels, skills, and gear</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span><strong className="text-frost">Chief Tracker</strong> - Monitor chief gear tiers and charms</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span><strong className="text-frost">AI Advisor</strong> - Get personalized upgrade recommendations</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-ice">•</span>
                <span><strong className="text-frost">Packs</strong> - Analyze pack values before buying</span>
              </li>
            </ul>

            <h3 className="text-frost font-semibold mb-2">Tips</h3>
            <ol className="space-y-1 text-sm text-frost-muted list-decimal list-inside">
              <li>Go to <strong className="text-ice">Settings</strong> to set your generation and Furnace Level</li>
              <li>Add your heroes in <strong className="text-ice">Hero Tracker</strong> for personalized advice</li>
              <li>Set your chief gear in <strong className="text-ice">Chief Tracker</strong> for better advice</li>
              <li>Check <strong className="text-ice">AI Advisor</strong> for your next upgrade priorities</li>
            </ol>
          </div>

          {/* Your Status */}
          <div className="space-y-4">
            <div className="card text-center">
              <p className="text-text-secondary text-xs uppercase tracking-wide mb-1">Generation</p>
              <p className="text-2xl font-bold text-success">Gen {stats?.generation || '?'}</p>
              {stats?.generation && (
                <p className="text-xs text-frost-muted mt-1">
                  Day {getEstimatedDaysFromGeneration(stats.generation)}
                </p>
              )}
            </div>
            <div className="card text-center">
              <p className="text-text-secondary text-xs uppercase tracking-wide mb-1">Server Age</p>
              <p className="text-2xl font-bold text-ice">{stats?.server_age_days || '?'} days</p>
              {stats?.server_age_days && (
                <p className="text-xs text-frost-muted mt-1">
                  = Gen {getGenerationFromDays(stats.server_age_days)}
                </p>
              )}
            </div>
            <div className="card text-center">
              <p className="text-text-secondary text-xs uppercase tracking-wide mb-1">Furnace Level</p>
              <p className="text-2xl font-bold text-fire">{stats?.furnace_display || 'FC-?'}</p>
            </div>
          </div>
        </div>

        {/* Donate Banner */}
        <div className="card mb-8 border-fire/30 bg-gradient-to-r from-fire/10 to-fire/5">
          <div className="flex flex-wrap items-center gap-4">
            <div className="w-10 h-10 relative flex-shrink-0">
              <Image
                src="/images/frost_star.png"
                alt="Frost Star"
                fill
                className="object-contain"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <p className="text-frost font-medium">
                Chief, running this Settlement costs resources!
              </p>
              <p className="text-sm text-frost-muted">
                If Bear's Den has helped your journey, consider fueling us with some Frost Stars.
              </p>
            </div>
            <a
              href="https://ko-fi.com/randomchaoslabs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-fire whitespace-nowrap"
            >
              Support Us
            </a>
          </div>
        </div>

        {/* Generation Timeline */}
        <div className="card mb-8">
          <h2 className="section-header">Generation Timeline</h2>
          <p className="text-sm text-frost-muted mb-4">
            Know what heroes are coming and when to prepare.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2">
            {generations.map((g) => (
              <div
                key={g.gen}
                className={`p-3 rounded-lg ${g.color} ${
                  stats?.generation === g.gen ? 'ring-2 ring-white' : ''
                }`}
              >
                <p className="font-bold text-white">Gen {g.gen}</p>
                <p className="text-xs text-white/80">{g.days}</p>
                <p className="text-xs text-white/70 mt-1 line-clamp-2">{g.heroes}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Submit Feedback */}
        <div className="card">
          <details className="group">
            <summary className="flex items-center justify-between cursor-pointer text-frost font-medium">
              <span>See something wrong? Make a suggestion!</span>
              <span className="text-ice group-open:rotate-180 transition-transform">▼</span>
            </summary>
            <div className="mt-4 pt-4 border-t border-surface-border">
              <p className="text-sm text-frost-muted mb-3">
                Help us improve Bear's Den by reporting bugs, suggesting features, or pointing out data errors.
              </p>
              <Link href="/inbox" className="btn-secondary inline-block">
                Submit Feedback
              </Link>
            </div>
          </details>
        </div>
      </div>
    </AppShell>
  );
}
