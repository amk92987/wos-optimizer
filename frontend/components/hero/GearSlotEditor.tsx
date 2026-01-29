'use client';

import NumberStepper from './NumberStepper';

const QUALITY_OPTIONS = ['None', 'Gray', 'Green', 'Blue', 'Purple', 'Gold', 'Legendary'];
const QUALITY_COLORS: Record<number, string> = {
  0: 'bg-zinc-700 text-zinc-500 border-zinc-600',
  1: 'bg-zinc-600 text-zinc-300 border-zinc-500',
  2: 'bg-green-900/50 text-green-400 border-green-700/50',
  3: 'bg-blue-900/50 text-blue-400 border-blue-700/50',
  4: 'bg-purple-900/50 text-purple-400 border-purple-700/50',
  5: 'bg-amber-900/50 text-amber-400 border-amber-700/50',
  6: 'bg-orange-900/50 text-orange-300 border-orange-700/50',
};

interface GearSlotEditorProps {
  label: string;
  icon: string;
  quality: number;
  level: number;
  mastery: number;
  onQualityChange: (quality: number) => void;
  onLevelChange: (level: number) => void;
  onMasteryChange: (mastery: number) => void;
}

export default function GearSlotEditor({
  label,
  icon,
  quality,
  level,
  mastery,
  onQualityChange,
  onLevelChange,
  onMasteryChange,
}: GearSlotEditorProps) {
  const showLevel = quality > 0;
  const showMastery = quality >= 5 && level >= 20;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1 text-xs text-frost-muted">
        <span>{icon}</span>
        <span>{label}</span>
      </div>

      {/* Quality dropdown - always visible */}
      <select
        value={quality}
        onChange={(e) => onQualityChange(parseInt(e.target.value))}
        className={`w-full py-1 px-2 text-xs rounded border transition-colors cursor-pointer
          ${QUALITY_COLORS[quality]} outline-none focus:ring-1 focus:ring-ice/30`}
      >
        {QUALITY_OPTIONS.map((q, i) => (
          <option key={i} value={i}>{q}</option>
        ))}
      </select>

      {/* Level stepper */}
      {showLevel && (
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-frost-muted">Lv</span>
          <NumberStepper value={level} min={0} max={100} onChange={onLevelChange} />
        </div>
      )}

      {/* Mastery stepper - Gold+ quality, level 20+ */}
      {showMastery && (
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-frost-muted">M</span>
          <NumberStepper value={mastery} min={0} max={20} onChange={onMasteryChange} />
        </div>
      )}
    </div>
  );
}
