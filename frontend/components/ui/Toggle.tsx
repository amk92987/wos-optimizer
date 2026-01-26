'use client';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: {
    track: 'w-8 h-4',
    thumb: 'w-3 h-3',
    translate: 'translate-x-4',
  },
  md: {
    track: 'w-11 h-6',
    thumb: 'w-5 h-5',
    translate: 'translate-x-5',
  },
  lg: {
    track: 'w-14 h-7',
    thumb: 'w-6 h-6',
    translate: 'translate-x-7',
  },
};

export default function Toggle({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  size = 'md',
}: ToggleProps) {
  const sizes = sizeClasses[size];

  return (
    <label className={`flex items-center gap-3 ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`
          relative inline-flex shrink-0 ${sizes.track}
          rounded-full border-2 border-transparent
          transition-colors duration-200 ease-in-out
          focus:outline-none focus-visible:ring-2 focus-visible:ring-ice focus-visible:ring-offset-2 focus-visible:ring-offset-background
          ${checked ? 'bg-ice' : 'bg-surface'}
        `}
      >
        <span
          aria-hidden="true"
          className={`
            pointer-events-none inline-block ${sizes.thumb}
            rounded-full bg-white shadow-lg ring-0
            transition duration-200 ease-in-out
            ${checked ? sizes.translate : 'translate-x-0.5'}
          `}
        />
      </button>
      {(label || description) && (
        <div className="flex-1">
          {label && (
            <span className="text-sm font-medium text-frost">{label}</span>
          )}
          {description && (
            <p className="text-xs text-text-secondary mt-0.5">{description}</p>
          )}
        </div>
      )}
    </label>
  );
}
