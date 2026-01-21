'use client';

import { useState, ReactNode } from 'react';

interface ExpanderProps {
  title: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export default function Expander({ title, children, defaultOpen = false, className = '' }: ExpanderProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`expander ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="expander-header w-full"
      >
        <div className="flex-1 text-left">{title}</div>
        <svg
          className={`w-5 h-5 text-zinc-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && (
        <div className="expander-content animate-fadeIn">
          {children}
        </div>
      )}
    </div>
  );
}
