'use client';

import { getHeroRoles, HeroRole } from '@/lib/heroRoles';

interface HeroRoleBadgesProps {
  heroName: string;
  compact?: boolean;
}

export default function HeroRoleBadges({ heroName, compact = false }: HeroRoleBadgesProps) {
  const roles = getHeroRoles(heroName);

  if (!roles || roles.length === 0) {
    return null;
  }

  const displayRoles = compact ? roles.slice(0, 2) : roles;

  return (
    <div className={`flex flex-wrap gap-1 ${compact ? '' : 'mt-1'}`}>
      {displayRoles.map((role, index) => (
        <span
          key={index}
          className="inline-flex items-center text-[10px] px-1.5 py-0.5 rounded border font-medium cursor-help"
          style={{
            backgroundColor: `${role.color}22`,
            borderColor: role.color,
            color: role.color,
          }}
          title={role.detail}
        >
          {role.role}
        </span>
      ))}
    </div>
  );
}
