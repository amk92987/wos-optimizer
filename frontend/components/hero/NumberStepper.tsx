'use client';

import { useState, useRef, useEffect } from 'react';

interface NumberStepperProps {
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
  label?: string;
  size?: 'sm' | 'md';
}

export default function NumberStepper({ value, min, max, onChange, label, size = 'sm' }: NumberStepperProps) {
  const [isTyping, setIsTyping] = useState(false);
  const [inputValue, setInputValue] = useState(String(value));
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isTyping) setInputValue(String(value));
  }, [value, isTyping]);

  const handleBlur = () => {
    setIsTyping(false);
    const parsed = parseInt(inputValue);
    if (!isNaN(parsed)) {
      const clamped = Math.max(min, Math.min(max, parsed));
      onChange(clamped);
      setInputValue(String(clamped));
    } else {
      setInputValue(String(value));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      (e.target as HTMLInputElement).blur();
    }
  };

  const step = (delta: number) => {
    const next = Math.max(min, Math.min(max, value + delta));
    if (next !== value) onChange(next);
  };

  const btnClass = size === 'sm'
    ? 'w-6 h-6 text-xs'
    : 'w-8 h-8 text-sm';

  const inputClass = size === 'sm'
    ? 'w-8 text-xs h-6'
    : 'w-10 text-sm h-8';

  return (
    <div className="flex items-center gap-0.5">
      {label && <span className="text-xs text-frost-muted mr-1">{label}</span>}
      <button
        onClick={() => step(-1)}
        disabled={value <= min}
        className={`${btnClass} flex items-center justify-center rounded bg-surface-hover text-frost-muted
                   hover:bg-surface hover:text-frost disabled:opacity-30 disabled:cursor-not-allowed transition-colors`}
      >
        -
      </button>
      {isTyping ? (
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          className={`${inputClass} text-center bg-surface border border-ice/30 rounded text-zinc-100
                     outline-none focus:border-ice`}
          autoFocus
        />
      ) : (
        <button
          onClick={() => {
            setIsTyping(true);
            setInputValue(String(value));
          }}
          className={`${inputClass} text-center font-medium text-zinc-100 rounded
                     hover:bg-surface-hover transition-colors cursor-text`}
        >
          {value}
        </button>
      )}
      <button
        onClick={() => step(1)}
        disabled={value >= max}
        className={`${btnClass} flex items-center justify-center rounded bg-surface-hover text-frost-muted
                   hover:bg-surface hover:text-frost disabled:opacity-30 disabled:cursor-not-allowed transition-colors`}
      >
        +
      </button>
    </div>
  );
}
