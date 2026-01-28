'use client';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
}

export default function Skeleton({
  className = '',
  width,
  height,
  rounded = 'md',
}: SkeletonProps) {
  const roundedClasses = {
    none: '',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`bg-surface/50 animate-pulse ${roundedClasses[rounded]} ${className}`}
      style={style}
    />
  );
}

// Pre-built skeleton for cards
export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`card space-y-4 ${className}`}>
      <Skeleton height={20} width="60%" />
      <div className="space-y-2">
        <Skeleton height={16} width="100%" />
        <Skeleton height={16} width="80%" />
        <Skeleton height={16} width="90%" />
      </div>
      <div className="flex gap-2 pt-2">
        <Skeleton height={32} width={80} rounded="lg" />
        <Skeleton height={32} width={80} rounded="lg" />
      </div>
    </div>
  );
}

// Pre-built skeleton for table rows
export function SkeletonTable({
  rows = 5,
  columns = 4,
  className = '',
}: {
  rows?: number;
  columns?: number;
  className?: string;
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {/* Header */}
      <div className="flex gap-4 pb-2 border-b border-surface-border">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} height={16} className="flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 py-2">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton
              key={colIndex}
              height={20}
              className="flex-1"
              width={colIndex === 0 ? '40%' : undefined}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// Hero card skeleton
export function SkeletonHeroCard() {
  return (
    <div className="card flex gap-4">
      {/* Portrait */}
      <Skeleton width={80} height={80} rounded="lg" />
      {/* Content */}
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <Skeleton height={20} width={120} />
          <Skeleton height={20} width={40} rounded="full" />
        </div>
        <Skeleton height={16} width="60%" />
        <div className="flex gap-2">
          <Skeleton height={24} width={60} rounded="full" />
          <Skeleton height={24} width={60} rounded="full" />
        </div>
      </div>
    </div>
  );
}
