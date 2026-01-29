'use client';

import { SaveStatus } from '@/hooks/useAutoSave';

interface SaveIndicatorProps {
  status: SaveStatus;
}

export default function SaveIndicator({ status }: SaveIndicatorProps) {
  if (status === 'idle') return null;

  return (
    <span className="inline-flex items-center gap-1 text-xs">
      {status === 'saving' && (
        <>
          <span className="w-2 h-2 rounded-full bg-amber animate-pulse" />
          <span className="text-amber">Saving...</span>
        </>
      )}
      {status === 'saved' && (
        <>
          <svg className="w-3 h-3 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-success">Saved</span>
        </>
      )}
      {status === 'error' && (
        <>
          <span className="w-2 h-2 rounded-full bg-error" />
          <span className="text-error">Error</span>
        </>
      )}
    </span>
  );
}
