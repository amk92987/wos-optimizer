"""
Recommendation Engine for Whiteout Survival hero upgrades.
Prioritizes upgrades based on user's goals and current hero states.

VERIFIED MECHANICS (from WOS_REFERENCE.md):
- Rally Leader: 3 heroes provide 9 expedition skills (all right-side skills)
- Rally Joiner: Only FIRST hero's TOP-RIGHT expedition skill contributes
- Best Attack Joiner: Jessie (Stand of Arms: +25% DMG dealt all troops)
- Best Garrison Joiner: Sergey (Defenders' Edge: -20% DMG taken all troops)
- Combat Order: Infantry → Lancers → Marksmen
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class UpgradeType(Enum):
    LEVEL = "level"
    STARS = "stars"
    EXPLORATION_SKILL = "exploration_skill"
    EXPEDITION_SKILL = "expedition_skill"
    GEAR = "gear"
    JOINER_ROLE = "joiner_role"  # Special recommendation for joiner heroes


@dataclass
class Recommendation:
    """A single upgrade recommendation."""
    hero_name: str
    upgrade_type: UpgradeType
    current_value: int
    target_value: int
    priority_score: float
    reason: str
    category: str  # "high", "medium", "low"

    def to_dict(self) -> dict:
        return {
            'hero_name': self.hero_name,
            'upgrade_type': self.upgrade_type.value,
            'current_value': self.current_value,
            'target_value': self.target_value,
            'priority_score': self.priority_score,
            'reason': self.reason,
            'category': self.category
        }


# Verified joiner hero data
JOINER_HEROES = {
    'attack': {
        'Jessie': {
            'skill_name': 'Stand of Arms',
            'effect': '+25% DMG dealt (all troops)',
            'reason': 'Best attack joiner - affects ALL damage types including skills, pets, teammates'
        }
    },
    'garrison': {
        'Sergey': {
            'skill_name': 'Defenders\' Edge',
            'effect': '-20% DMG taken (all troops)',
            'reason': 'Best garrison joiner - universal damage reduction'
        }
    }
}

# Heroes with strong rally leader potential (verified)
RALLY_LEADERS = {
    'Jeronimo': {
        'reason': 'Multiple "all troops" offensive expedition skills (+25% DMG, +25% ATK, +30% periodic DMG)',
        'priority_modes': ['svs', 'rally']
    },
    'Natalia': {
        'reason': 'Strong defensive expedition skills, +30% DMG dealt, +15% Lethality for rally troops',
        'priority_modes': ['castle_battle', 'garrison']
    }
}


class RecommendationEngine:
    """Generate upgrade recommendations based on user profile and heroes."""

    # Tier multipliers for priority scoring
    TIER_SCORES = {
        "S+": 1.0,
        "S": 0.85,
        "A": 0.7,
        "B": 0.5,
        "C": 0.3,
        "D": 0.15
    }

    # Priority weights for different game modes
    MODE_WEIGHTS = {
        'svs': {'expedition': 1.0, 'exploration': 0.3},
        'rally': {'expedition': 1.0, 'exploration': 0.2},
        'castle_battle': {'expedition': 0.9, 'exploration': 0.4},
        'exploration': {'expedition': 0.3, 'exploration': 1.0},
        'gathering': {'expedition': 0.2, 'exploration': 0.4},
    }

    def __init__(self, heroes_data: dict, user_heroes: list, profile: Any):
        """
        Initialize the recommendation engine.

        Args:
            heroes_data: Static hero data from heroes.json
            user_heroes: List of user's owned heroes with their stats
            profile: User profile with priorities
        """
        self.heroes_data = heroes_data
        self.user_heroes = user_heroes
        self.profile = profile

        # Build hero lookup
        self.hero_lookup = {h['name']: h for h in heroes_data.get('heroes', [])}

        # Calculate priority weights from profile
        self.priority_weights = self._calculate_priority_weights()

    def _calculate_priority_weights(self) -> Dict[str, float]:
        """Calculate normalized priority weights from user profile."""
        raw_priorities = {
            'svs': getattr(self.profile, 'priority_svs', 5),
            'rally': getattr(self.profile, 'priority_rally', 4),
            'castle_battle': getattr(self.profile, 'priority_castle_battle', 4),
            'exploration': getattr(self.profile, 'priority_exploration', 3),
            'gathering': getattr(self.profile, 'priority_gathering', 2),
        }

        total = sum(raw_priorities.values())
        if total == 0:
            total = 1

        return {k: v / total for k, v in raw_priorities.items()}

    def _get_hero_base_score(self, hero_name: str) -> float:
        """Get base score for a hero based on tier ratings."""
        hero_data = self.hero_lookup.get(hero_name)
        if not hero_data:
            return 0.0

        # Get tier scores
        overall_tier = hero_data.get('tier_overall', 'C')
        expedition_tier = hero_data.get('tier_expedition', 'C')
        exploration_tier = hero_data.get('tier_exploration', 'C')

        overall_score = self.TIER_SCORES.get(overall_tier, 0.3)
        expedition_score = self.TIER_SCORES.get(expedition_tier, 0.3)
        exploration_score = self.TIER_SCORES.get(exploration_tier, 0.3)

        # Weight by user's priorities
        weighted_score = 0.0
        for mode, weight in self.priority_weights.items():
            mode_weights = self.MODE_WEIGHTS.get(mode, {'expedition': 0.5, 'exploration': 0.5})
            mode_score = (
                expedition_score * mode_weights['expedition'] +
                exploration_score * mode_weights['exploration']
            )
            weighted_score += mode_score * weight

        # Factor in overall tier
        final_score = (weighted_score * 0.7) + (overall_score * 0.3)

        return final_score

    def _check_generation_relevance(self, hero_name: str) -> float:
        """Check if hero is still relevant for user's generation."""
        hero_data = self.hero_lookup.get(hero_name)
        if not hero_data:
            return 0.5

        hero_gen = hero_data.get('generation', 1)
        server_age = getattr(self.profile, 'server_age_days', 0)

        # Calculate user's current generation
        if server_age < 40:
            current_gen = 1
        elif server_age < 120:
            current_gen = 2
        elif server_age < 200:
            current_gen = 3
        elif server_age < 280:
            current_gen = 4
        elif server_age < 360:
            current_gen = 5
        elif server_age < 440:
            current_gen = 6
        elif server_age < 520:
            current_gen = 7
        else:
            current_gen = 8

        # Heroes from much older generations are less valuable
        gen_diff = current_gen - hero_gen

        if gen_diff <= 0:
            # Future or current gen hero
            return 1.0
        elif gen_diff == 1:
            return 0.9  # Still very relevant
        elif gen_diff == 2:
            return 0.7  # Moderately relevant
        elif gen_diff == 3:
            return 0.5  # Getting outdated
        else:
            return 0.3  # Very old hero

        # Exception: S+ tier heroes stay relevant longer
        tier = hero_data.get('tier_overall', 'C')
        if tier == 'S+':
            return min(1.0, gen_relevance + 0.2)

        return gen_relevance

    def _generate_level_recommendations(self) -> List[Recommendation]:
        """Generate recommendations for hero leveling."""
        recommendations = []

        for user_hero in self.user_heroes:
            hero_name = user_hero.hero.name if hasattr(user_hero, 'hero') else user_hero.get('name', '')
            current_level = getattr(user_hero, 'level', user_hero.get('level', 1))

            if current_level >= 80:
                continue  # Already maxed

            base_score = self._get_hero_base_score(hero_name)
            gen_relevance = self._check_generation_relevance(hero_name)

            # Higher priority if hero is underdeveloped relative to their tier
            level_gap = 80 - current_level
            level_factor = min(level_gap / 40, 1.0)  # Normalize

            priority_score = base_score * gen_relevance * (0.5 + level_factor * 0.5)

            # Determine target level (suggest increments)
            if current_level < 40:
                target_level = min(current_level + 10, 40)
            elif current_level < 60:
                target_level = min(current_level + 10, 60)
            else:
                target_level = min(current_level + 5, 80)

            hero_data = self.hero_lookup.get(hero_name, {})
            tier = hero_data.get('tier_overall', '?')

            recommendations.append(Recommendation(
                hero_name=hero_name,
                upgrade_type=UpgradeType.LEVEL,
                current_value=current_level,
                target_value=target_level,
                priority_score=priority_score,
                reason=f"{tier} tier hero, level boost improves all stats",
                category=self._categorize_score(priority_score)
            ))

        return recommendations

    def _generate_skill_recommendations(self) -> List[Recommendation]:
        """Generate recommendations for skill upgrades."""
        recommendations = []

        # Determine if user prioritizes expedition or exploration
        expedition_priority = (
            self.priority_weights.get('svs', 0) +
            self.priority_weights.get('rally', 0) +
            self.priority_weights.get('castle_battle', 0)
        )
        exploration_priority = (
            self.priority_weights.get('exploration', 0) +
            self.priority_weights.get('gathering', 0)
        )

        for user_hero in self.user_heroes:
            hero_name = user_hero.hero.name if hasattr(user_hero, 'hero') else user_hero.get('name', '')

            base_score = self._get_hero_base_score(hero_name)
            gen_relevance = self._check_generation_relevance(hero_name)

            # Check expedition skills
            exp_skill1 = getattr(user_hero, 'expedition_skill_1_level', 1)
            exp_skill2 = getattr(user_hero, 'expedition_skill_2_level', 1)

            for skill_num, skill_level in [(1, exp_skill1), (2, exp_skill2)]:
                if skill_level < 5:
                    priority_score = base_score * gen_relevance * expedition_priority * 1.2

                    recommendations.append(Recommendation(
                        hero_name=hero_name,
                        upgrade_type=UpgradeType.EXPEDITION_SKILL,
                        current_value=skill_level,
                        target_value=skill_level + 1,
                        priority_score=priority_score,
                        reason=f"Expedition Skill {skill_num} - boosts combat/SvS performance",
                        category=self._categorize_score(priority_score)
                    ))

            # Check exploration skills
            expl_skill1 = getattr(user_hero, 'exploration_skill_1_level', 1)
            expl_skill2 = getattr(user_hero, 'exploration_skill_2_level', 1)

            for skill_num, skill_level in [(1, expl_skill1), (2, expl_skill2)]:
                if skill_level < 5:
                    priority_score = base_score * gen_relevance * exploration_priority * 1.1

                    recommendations.append(Recommendation(
                        hero_name=hero_name,
                        upgrade_type=UpgradeType.EXPLORATION_SKILL,
                        current_value=skill_level,
                        target_value=skill_level + 1,
                        priority_score=priority_score,
                        reason=f"Exploration Skill {skill_num} - boosts PvE/exploration",
                        category=self._categorize_score(priority_score)
                    ))

        return recommendations

    def _generate_star_recommendations(self) -> List[Recommendation]:
        """Generate recommendations for star/ascension upgrades."""
        recommendations = []

        for user_hero in self.user_heroes:
            hero_name = user_hero.hero.name if hasattr(user_hero, 'hero') else user_hero.get('name', '')
            current_stars = getattr(user_hero, 'stars', 1)

            if current_stars >= 5:
                continue

            base_score = self._get_hero_base_score(hero_name)
            gen_relevance = self._check_generation_relevance(hero_name)

            # Stars are expensive, prioritize for top tier heroes
            priority_score = base_score * gen_relevance * 0.9

            hero_data = self.hero_lookup.get(hero_name, {})
            tier = hero_data.get('tier_overall', '?')

            recommendations.append(Recommendation(
                hero_name=hero_name,
                upgrade_type=UpgradeType.STARS,
                current_value=current_stars,
                target_value=current_stars + 1,
                priority_score=priority_score,
                reason=f"Ascend to {current_stars + 1} stars for stat boost (requires shards)",
                category=self._categorize_score(priority_score)
            ))

        return recommendations

    def _generate_joiner_recommendations(self) -> List[Recommendation]:
        """Generate recommendations for joiner role heroes (VERIFIED MECHANICS).

        Critical: When joining rallies, only the FIRST hero's TOP-RIGHT
        expedition skill contributes. This makes specific heroes very valuable.
        """
        recommendations = []

        # Check user's priorities
        rally_priority = self.priority_weights.get('rally', 0)
        svs_priority = self.priority_weights.get('svs', 0)
        castle_priority = self.priority_weights.get('castle_battle', 0)

        attack_priority = rally_priority + svs_priority
        defense_priority = castle_priority

        # Get list of owned hero names
        owned_names = set()
        for uh in self.user_heroes:
            name = uh.hero.name if hasattr(uh, 'hero') else uh.get('name', '')
            owned_names.add(name)

        # Check for attack joiner (Jessie)
        if attack_priority > 0.2:  # User cares about rally/SvS
            if 'Jessie' not in owned_names:
                # HIGH priority - user needs Jessie but doesn't have her
                recommendations.append(Recommendation(
                    hero_name='Jessie',
                    upgrade_type=UpgradeType.JOINER_ROLE,
                    current_value=0,
                    target_value=1,
                    priority_score=0.9 * attack_priority,
                    reason="UNLOCK JESSIE: Best attack joiner. Her top-right skill (+25% DMG dealt) applies when joining rallies. Only this skill matters as joiner!",
                    category="high"
                ))
            else:
                # Check if Jessie's expedition skills are leveled
                for uh in self.user_heroes:
                    name = uh.hero.name if hasattr(uh, 'hero') else uh.get('name', '')
                    if name == 'Jessie':
                        exp_skill = getattr(uh, 'expedition_skill_1_level', 1)
                        if exp_skill < 5:
                            recommendations.append(Recommendation(
                                hero_name='Jessie',
                                upgrade_type=UpgradeType.EXPEDITION_SKILL,
                                current_value=exp_skill,
                                target_value=5,
                                priority_score=0.85 * attack_priority,
                                reason=f"MAX JESSIE'S EXPEDITION SKILL: Her Stand of Arms (+{exp_skill * 5}% → +25% DMG) is the ONLY skill that matters when joining rallies!",
                                category="high"
                            ))
                        break

        # Check for garrison joiner (Sergey)
        if defense_priority > 0.15:  # User cares about castle defense
            if 'Sergey' not in owned_names:
                recommendations.append(Recommendation(
                    hero_name='Sergey',
                    upgrade_type=UpgradeType.JOINER_ROLE,
                    current_value=0,
                    target_value=1,
                    priority_score=0.8 * defense_priority,
                    reason="UNLOCK SERGEY: Best garrison joiner. His top-right skill (-20% DMG taken) applies when reinforcing garrisons.",
                    category="high"
                ))
            else:
                for uh in self.user_heroes:
                    name = uh.hero.name if hasattr(uh, 'hero') else uh.get('name', '')
                    if name == 'Sergey':
                        exp_skill = getattr(uh, 'expedition_skill_1_level', 1)
                        if exp_skill < 5:
                            recommendations.append(Recommendation(
                                hero_name='Sergey',
                                upgrade_type=UpgradeType.EXPEDITION_SKILL,
                                current_value=exp_skill,
                                target_value=5,
                                priority_score=0.75 * defense_priority,
                                reason=f"LEVEL SERGEY'S EXPEDITION SKILL: His Defenders' Edge (-{exp_skill * 4}% → -20% DMG taken) is key for garrison defense!",
                                category="medium"
                            ))
                        break

        # Check for rally leader (Jeronimo)
        if attack_priority > 0.25:
            if 'Jeronimo' in owned_names:
                for uh in self.user_heroes:
                    name = uh.hero.name if hasattr(uh, 'hero') else uh.get('name', '')
                    if name == 'Jeronimo':
                        level = getattr(uh, 'level', 1)
                        if level < 60:
                            recommendations.append(Recommendation(
                                hero_name='Jeronimo',
                                upgrade_type=UpgradeType.LEVEL,
                                current_value=level,
                                target_value=60,
                                priority_score=0.9 * attack_priority,
                                reason="RALLY LEADER PRIORITY: Jeronimo's 9 expedition skills buff your ENTIRE rally. His +25% DMG + +25% ATK affects all troops!",
                                category="high"
                            ))
                        break

        return recommendations

    def _categorize_score(self, score: float) -> str:
        """Categorize priority score into high/medium/low."""
        if score >= 0.6:
            return "high"
        elif score >= 0.35:
            return "medium"
        else:
            return "low"

    def generate_recommendations(self, limit: int = 20) -> List[Recommendation]:
        """Generate all recommendations, sorted by priority.

        Args:
            limit: Maximum number of recommendations to return

        Returns:
            List of Recommendation objects, sorted by priority_score descending

        VERIFIED MECHANICS APPLIED:
        - Joiner heroes (Jessie/Sergey) prioritized for rally-focused users
        - Rally leader (Jeronimo) prioritized for SvS/rally users
        - Expedition skills weighted higher for PvP priorities
        """
        all_recommendations = []

        # Generate different types of recommendations
        all_recommendations.extend(self._generate_level_recommendations())
        all_recommendations.extend(self._generate_skill_recommendations())
        all_recommendations.extend(self._generate_star_recommendations())

        # Add joiner/leader specific recommendations (VERIFIED MECHANICS)
        all_recommendations.extend(self._generate_joiner_recommendations())

        # Sort by priority score
        all_recommendations.sort(key=lambda r: r.priority_score, reverse=True)

        # Return top recommendations
        return all_recommendations[:limit]

    def get_top_heroes_to_invest(self, limit: int = 5) -> List[Dict]:
        """Get the top heroes to invest in based on user's priorities.

        Returns hero data with investment reasoning.
        """
        hero_scores = []

        for hero_data in self.heroes_data.get('heroes', []):
            name = hero_data['name']

            # Check if user owns this hero
            owned = any(
                (uh.hero.name if hasattr(uh, 'hero') else uh.get('name', '')) == name
                for uh in self.user_heroes
            )

            base_score = self._get_hero_base_score(name)
            gen_relevance = self._check_generation_relevance(name)

            final_score = base_score * gen_relevance

            hero_scores.append({
                'name': name,
                'tier': hero_data.get('tier_overall', '?'),
                'class': hero_data.get('hero_class', '?'),
                'generation': hero_data.get('generation', 0),
                'score': final_score,
                'owned': owned,
                'notes': hero_data.get('notes', '')
            })

        # Sort by score
        hero_scores.sort(key=lambda h: h['score'], reverse=True)

        return hero_scores[:limit]
