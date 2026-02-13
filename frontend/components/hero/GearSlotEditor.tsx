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

// Legendary enhancement XP costs per level (index = from-level, 0→1 through 99→100)
const LEGENDARY_XP = [
  0,2500,2550,2600,2650,2700,2750,2800,2850,2900,2950,3000,3050,3100,3150,3200,3250,3300,3350,0,
  3500,3550,3600,3650,3700,3750,3800,3850,3900,3950,4000,4050,4100,4150,4200,4250,4300,4350,4400,0,
  4450,4500,4550,4600,4650,4700,4750,4800,4850,4900,4950,5000,5050,5100,5150,5200,5250,5300,5350,0,
  5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,0,
  7500,7600,7700,7800,7900,8000,8100,8200,8300,8400,8500,8600,8700,8800,8900,9000,9100,9200,9300,0,
];
const LEGENDARY_MILESTONES: Record<number, { mithril: number; gear: number }> = {
  0: { mithril: 0, gear: 2 }, 19: { mithril: 10, gear: 3 }, 39: { mithril: 20, gear: 5 },
  59: { mithril: 30, gear: 5 }, 79: { mithril: 40, gear: 10 }, 99: { mithril: 50, gear: 10 },
};

// Mastery forging costs per level (index = from-level, 0→1 through 19→20)
const MASTERY_STONES = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200];
const MASTERY_GEAR = [0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8,9,10];

function getNextLevelHint(quality: number, level: number): string | null {
  if (quality === 6 && level < 100) {
    const m = LEGENDARY_MILESTONES[level];
    if (m) {
      const parts = [];
      if (m.mithril > 0) parts.push(`${m.mithril} Mithril`);
      parts.push(`${m.gear} Gear`);
      return parts.join(' + ');
    }
    return `${LEGENDARY_XP[level].toLocaleString()} XP`;
  }
  return null;
}

function getNextMasteryHint(mastery: number): string | null {
  if (mastery < 20) {
    const stones = MASTERY_STONES[mastery];
    const gear = MASTERY_GEAR[mastery];
    if (gear > 0) return `${stones} Stones + ${gear} Gear`;
    return `${stones} Stones`;
  }
  return null;
}

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
        <>
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-frost-muted">Lv</span>
            <NumberStepper value={level} min={0} max={100} onChange={onLevelChange} />
          </div>
          {(() => {
            const hint = getNextLevelHint(quality, level);
            return hint ? (
              <div className="text-[9px] text-frost-muted/60 text-right" title="Cost to reach next level">
                Next: {hint}
              </div>
            ) : null;
          })()}
        </>
      )}

      {/* Mastery stepper - Gold+ quality, level 20+ */}
      {showMastery && (
        <>
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-frost-muted">M</span>
            <NumberStepper value={mastery} min={0} max={20} onChange={onMasteryChange} />
          </div>
          {(() => {
            const hint = getNextMasteryHint(mastery);
            return hint ? (
              <div className="text-[9px] text-frost-muted/60 text-right" title="Cost to reach next mastery level">
                Next: {hint}
              </div>
            ) : null;
          })()}
        </>
      )}
    </div>
  );
}
