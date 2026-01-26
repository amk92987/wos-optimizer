'use client';

type BadgeVariant = 'ice' | 'fire' | 'success' | 'warning' | 'error' | 'default';
type TierVariant = 'splus' | 's' | 'a' | 'b' | 'c' | 'd';
type ClassVariant = 'infantry' | 'lancer' | 'marksman';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

interface TierBadgeProps {
  tier: TierVariant;
  className?: string;
}

interface ClassBadgeProps {
  heroClass: ClassVariant;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  ice: 'badge-ice',
  fire: 'badge-fire',
  success: 'badge-success',
  warning: 'badge-warning',
  error: 'badge-error',
  default: 'badge bg-surface text-text-secondary border border-surface-border',
};

export default function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span className={`${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
}

// Tier badge component
export function TierBadge({ tier, className = '' }: TierBadgeProps) {
  const tierLabels: Record<TierVariant, string> = {
    splus: 'S+',
    s: 'S',
    a: 'A',
    b: 'B',
    c: 'C',
    d: 'D',
  };

  return (
    <span className={`tier-${tier} ${className}`}>
      {tierLabels[tier]}
    </span>
  );
}

// Hero class badge component
export function ClassBadge({ heroClass, className = '' }: ClassBadgeProps) {
  const classLabels: Record<ClassVariant, string> = {
    infantry: 'Infantry',
    lancer: 'Lancer',
    marksman: 'Marksman',
  };

  return (
    <span className={`class-${heroClass} ${className}`}>
      {classLabels[heroClass]}
    </span>
  );
}

// Generation badge
interface GenBadgeProps {
  gen: number;
  className?: string;
}

export function GenBadge({ gen, className = '' }: GenBadgeProps) {
  // Color based on generation (older = cooler, newer = warmer)
  const genColors: Record<number, string> = {
    1: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    2: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    3: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    4: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    5: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
    6: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
    7: 'bg-green-500/20 text-green-400 border-green-500/30',
    8: 'bg-green-500/20 text-green-400 border-green-500/30',
    9: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    10: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    11: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    12: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    13: 'bg-red-500/20 text-red-400 border-red-500/30',
    14: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  return (
    <span className={`badge border ${genColors[gen] || genColors[14]} ${className}`}>
      Gen {gen}
    </span>
  );
}
