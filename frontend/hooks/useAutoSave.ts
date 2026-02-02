'use client';

import { useCallback, useRef, useState } from 'react';
import { heroesApi, UserHero } from '@/lib/api';

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseAutoSaveOptions {
  heroName: string;
  token: string | null;
  onSaved?: () => void;
  onError?: (error: Error) => void;
  debounceMs?: number;
}

export function useAutoSave({ heroName, token, onSaved, onError, debounceMs = 300 }: UseAutoSaveOptions) {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const pendingChanges = useRef<Partial<UserHero>>({});
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const savedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flush = useCallback(async () => {
    if (!token || Object.keys(pendingChanges.current).length === 0) return;

    const changes = { ...pendingChanges.current };
    pendingChanges.current = {};

    setSaveStatus('saving');
    try {
      await heroesApi.updateHero(token, heroName, changes);
      setSaveStatus('saved');
      onSaved?.();

      // Clear saved indicator after 2s
      if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
      savedTimerRef.current = setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (err) {
      setSaveStatus('error');
      onError?.(err as Error);
      // Clear error after 3s
      if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
      savedTimerRef.current = setTimeout(() => setSaveStatus('idle'), 3000);
    }
  }, [token, heroName, onSaved, onError]);

  const saveField = useCallback((fieldName: string, value: any) => {
    pendingChanges.current = { ...pendingChanges.current, [fieldName]: value };

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(flush, debounceMs);
  }, [flush, debounceMs]);

  const saveFields = useCallback((fields: Partial<UserHero>) => {
    pendingChanges.current = { ...pendingChanges.current, ...fields };

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(flush, debounceMs);
  }, [flush, debounceMs]);

  return { saveField, saveFields, saveStatus };
}
