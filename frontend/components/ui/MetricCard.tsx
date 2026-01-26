'use client';

interface MetricCardProps {
  value: string | number;
  label: string;
  icon?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'ice' | 'fire' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
}

const colorClasses = {
  ice: 'text-ice',
  fire: 'text-fire',
  success: 'text-success',
  warning: 'text-warning',
  error: 'text-error',
};

const sizeClasses = {
  sm: 'text-xl',
  md: 'text-2xl md:text-3xl',
  lg: 'text-3xl md:text-4xl',
};

export default function MetricCard({
  value,
  label,
  icon,
  trend,
  color = 'ice',
  size = 'md',
}: MetricCardProps) {
  return (
    <div className="card text-center p-4 hover:border-ice/30 transition-colors">
      {icon && <div className="text-2xl mb-2">{icon}</div>}
      <div className={`font-bold ${sizeClasses[size]} ${colorClasses[color]}`}>
        {value}
      </div>
      <div className="text-xs md:text-sm text-text-secondary mt-1 uppercase tracking-wide">
        {label}
      </div>
      {trend && (
        <div
          className={`text-xs mt-2 ${
            trend.isPositive ? 'text-success' : 'text-error'
          }`}
        >
          {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
        </div>
      )}
    </div>
  );
}
