'use client';

import NumberStepper from './NumberStepper';

interface MythicGearEditorProps {
  gearName: string;
  unlocked: boolean;
  level: number;
  skillLevel: number;
  onUnlockedChange: (unlocked: boolean) => void;
  onLevelChange: (level: number) => void;
  onSkillLevelChange: (level: number) => void;
}

export default function MythicGearEditor({
  gearName,
  unlocked,
  level,
  skillLevel,
  onUnlockedChange,
  onLevelChange,
  onSkillLevelChange,
}: MythicGearEditorProps) {
  return (
    <div className="space-y-3">
      {/* Toggle unlocked */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-frost">{gearName}</span>
        <button
          onClick={() => onUnlockedChange(!unlocked)}
          className={`relative w-10 h-5 rounded-full transition-colors ${
            unlocked ? 'bg-pink-500' : 'bg-zinc-600'
          }`}
        >
          <span
            className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
              unlocked ? 'translate-x-5' : 'translate-x-0.5'
            }`}
          />
        </button>
      </div>

      {unlocked && (
        <div className="space-y-3">
          {/* Gear Level */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-frost-muted">Gear Level</span>
            <NumberStepper value={level} min={0} max={100} onChange={onLevelChange} size="md" />
          </div>

          {/* Exclusive Skill Level - 1-10 pips */}
          <div>
            <span className="text-sm text-frost-muted block mb-2">Exclusive Skill</span>
            <div className="flex items-center gap-1.5">
              {[...Array(10)].map((_, i) => (
                <button
                  key={i}
                  onClick={() => {
                    if (i + 1 === skillLevel) {
                      onSkillLevelChange(Math.max(0, skillLevel - 1));
                    } else {
                      onSkillLevelChange(i + 1);
                    }
                  }}
                  className={`w-5 h-5 rounded-full border-2 transition-all hover:scale-110
                    ${i < skillLevel
                      ? 'bg-pink-400 border-pink-400 shadow-[0_0_4px_rgba(244,114,182,0.4)]'
                      : 'border-pink-400/30 hover:border-pink-400/60'
                    }`}
                  title={`Level ${i + 1}`}
                />
              ))}
              <span className="text-xs text-frost-muted ml-1">{skillLevel}/10</span>
            </div>
          </div>
        </div>
      )}

      {!unlocked && (
        <p className="text-xs text-frost-muted">Not unlocked</p>
      )}
    </div>
  );
}
