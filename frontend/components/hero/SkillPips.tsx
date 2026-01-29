'use client';

interface SkillPipsProps {
  level: number;
  maxLevel?: number;
  color?: 'green' | 'orange';
  skillName: string | null;
  skillDesc?: string | null;
  onChange: (level: number) => void;
}

export default function SkillPips({
  level,
  maxLevel = 5,
  color = 'green',
  skillName,
  skillDesc,
  onChange,
}: SkillPipsProps) {
  const handlePipClick = (index: number) => {
    const newLevel = index + 1;
    if (newLevel === level) {
      // Tap current level to decrement
      onChange(Math.max(1, level - 1));
    } else {
      onChange(newLevel);
    }
  };

  const filledClass = color === 'green'
    ? 'bg-emerald-400 border-emerald-400 shadow-[0_0_4px_rgba(52,211,153,0.4)]'
    : 'bg-orange-400 border-orange-400 shadow-[0_0_4px_rgba(251,146,60,0.4)]';

  const emptyClass = color === 'green'
    ? 'border-emerald-400/30 hover:border-emerald-400/60'
    : 'border-orange-400/30 hover:border-orange-400/60';

  return (
    <div className="flex items-center justify-between py-1">
      <div className="flex-1 min-w-0 flex items-center gap-1">
        <span
          className={`text-sm text-frost truncate ${skillDesc ? 'cursor-help' : ''}`}
          title={skillDesc || undefined}
        >
          {skillName || 'Unknown Skill'}
        </span>
        {skillDesc && (
          <span className="text-ice/50 text-xs flex-shrink-0" title={skillDesc}>
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </span>
        )}
      </div>
      <div className="flex items-center gap-1">
        {[...Array(maxLevel)].map((_, i) => (
          <button
            key={i}
            onClick={() => handlePipClick(i)}
            className={`w-5 h-5 rounded-full border-2 transition-all hover:scale-110
              ${i < level ? filledClass : emptyClass}`}
            title={`Level ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
