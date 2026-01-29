'use client';

interface StarRatingProps {
  stars: number;
  ascension: number;
  onStarsChange: (stars: number) => void;
  onAscensionChange: (ascension: number) => void;
}

export default function StarRating({ stars, ascension, onStarsChange, onAscensionChange }: StarRatingProps) {
  const handleStarClick = (index: number) => {
    const newStars = index + 1;
    if (newStars === stars) {
      onStarsChange(stars - 1);
    } else {
      onStarsChange(newStars);
    }
  };

  const handleShardClick = (index: number) => {
    const newAscension = index + 1;
    if (newAscension === ascension) {
      onAscensionChange(ascension - 1);
    } else {
      onAscensionChange(newAscension);
    }
  };

  return (
    <div className="flex flex-col items-start gap-1.5">
      {/* Stars row - clickable */}
      <div className="flex items-center gap-1">
        {[0, 1, 2, 3, 4].map((i) => (
          <button
            key={i}
            onClick={() => handleStarClick(i)}
            className="group relative transition-transform hover:scale-110"
            title={`${i + 1} star${i > 0 ? 's' : ''}`}
          >
            {/* Star shape using SVG */}
            <svg width="24" height="24" viewBox="0 0 24 24" className="drop-shadow-sm">
              <path
                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                fill={i < stars ? '#F59E0B' : 'transparent'}
                stroke={i < stars ? '#F59E0B' : '#52525b'}
                strokeWidth="1.5"
                className={i < stars ? 'drop-shadow-[0_0_3px_rgba(245,158,11,0.5)]' : ''}
              />
            </svg>
          </button>
        ))}
        {stars >= 5 && (
          <span className="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-success/20 text-success uppercase">
            Max
          </span>
        )}
      </div>

      {/* Star shards - small diamonds showing progress toward next star */}
      {stars < 5 && (
        <div className="flex items-center gap-1 ml-0.5">
          {[0, 1, 2, 3, 4].map((i) => (
            <button
              key={i}
              onClick={() => handleShardClick(i)}
              className="transition-transform hover:scale-125"
              title={`Shard ${i + 1}`}
            >
              <svg width="14" height="14" viewBox="0 0 14 14">
                <path
                  d="M7 1 L12 7 L7 13 L2 7 Z"
                  fill={i < ascension ? '#A855F7' : 'transparent'}
                  stroke={i < ascension ? '#A855F7' : '#52525b'}
                  strokeWidth="1.2"
                  className={i < ascension ? 'drop-shadow-[0_0_2px_rgba(168,85,247,0.5)]' : ''}
                />
              </svg>
            </button>
          ))}
          <span className="text-[10px] text-frost-muted ml-0.5">{ascension}/5</span>
        </div>
      )}
    </div>
  );
}
