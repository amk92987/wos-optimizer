'use client';

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: 'ice' | 'fire' | 'success' | 'warning' | 'error' | 'gold';
  showLabel?: boolean;
  label?: string;
  className?: string;
  animate?: boolean;
}

export default function ProgressBar({
  value,
  max = 100,
  size = 'md',
  color = 'ice',
  showLabel = false,
  label,
  className = '',
  animate = true,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  const colorClasses = {
    ice: 'bg-gradient-to-r from-ice to-ice-light',
    fire: 'bg-gradient-to-r from-fire to-fire-light',
    success: 'bg-gradient-to-r from-green-500 to-green-400',
    warning: 'bg-gradient-to-r from-yellow-500 to-yellow-400',
    error: 'bg-gradient-to-r from-red-500 to-red-400',
    gold: 'bg-gradient-to-r from-yellow-500 to-amber-400',
  };

  const glowClasses = {
    ice: 'shadow-[0_0_10px_rgba(74,144,217,0.5)]',
    fire: 'shadow-[0_0_10px_rgba(255,107,53,0.5)]',
    success: 'shadow-[0_0_10px_rgba(34,197,94,0.5)]',
    warning: 'shadow-[0_0_10px_rgba(245,158,11,0.5)]',
    error: 'shadow-[0_0_10px_rgba(239,68,68,0.5)]',
    gold: 'shadow-[0_0_10px_rgba(255,215,0,0.5)]',
  };

  return (
    <div className={className}>
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-frost-muted">{label}</span>
          {showLabel && (
            <span className="text-xs text-frost">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-surface rounded-full overflow-hidden ${sizeClasses[size]}`}>
        <div
          className={`${sizeClasses[size]} ${colorClasses[color]} ${glowClasses[color]} rounded-full ${
            animate ? 'transition-all duration-500 ease-out' : ''
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// Circular progress indicator
interface CircularProgressProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  color?: 'ice' | 'fire' | 'success' | 'warning' | 'error' | 'gold';
  showLabel?: boolean;
  className?: string;
}

export function CircularProgress({
  value,
  max = 100,
  size = 64,
  strokeWidth = 6,
  color = 'ice',
  showLabel = true,
  className = '',
}: CircularProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  const colorValues = {
    ice: '#4A90D9',
    fire: '#FF6B35',
    success: '#22C55E',
    warning: '#F59E0B',
    error: '#EF4444',
    gold: '#FFD700',
  };

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(74, 144, 217, 0.2)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colorValues[color]}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500 ease-out"
          style={{
            filter: `drop-shadow(0 0 4px ${colorValues[color]}50)`,
          }}
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-frost font-medium text-sm">{Math.round(percentage)}%</span>
        </div>
      )}
    </div>
  );
}

// Skill pips (1-5 filled dots)
interface SkillPipsProps {
  level: number;
  maxLevel?: number;
  size?: 'sm' | 'md';
  color?: 'ice' | 'gold' | 'purple';
  className?: string;
}

export function SkillPips({
  level,
  maxLevel = 5,
  size = 'md',
  color = 'ice',
  className = '',
}: SkillPipsProps) {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
  };

  const colorClasses = {
    ice: { filled: 'bg-ice shadow-[0_0_4px_rgba(74,144,217,0.6)]', empty: 'bg-surface' },
    gold: { filled: 'bg-yellow-400 shadow-[0_0_4px_rgba(255,215,0,0.6)]', empty: 'bg-surface' },
    purple: { filled: 'bg-purple-400 shadow-[0_0_4px_rgba(168,85,247,0.6)]', empty: 'bg-surface' },
  };

  return (
    <div className={`flex gap-1 ${className}`}>
      {Array.from({ length: maxLevel }).map((_, i) => (
        <div
          key={i}
          className={`${sizeClasses[size]} rounded-full transition-all ${
            i < level ? colorClasses[color].filled : colorClasses[color].empty
          }`}
        />
      ))}
    </div>
  );
}
