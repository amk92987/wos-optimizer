"""
Hero Analyzer - Analyzes user's heroes and recommends upgrades.
Detects level gaps, skill gaps, star progression opportunities.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HeroRecommendation:
    """A single hero-related recommendation."""
    priority: int  # 1-5, 1 being highest
    action: str
    hero: str
    reason: str
    resources: str
    relevance_tags: List[str]  # e.g., ['rally', 'svs', 'pve']
    rule_id: str


# Generation timeline (days since state creation)
GENERATION_TIMELINE = {
    1: (0, 40),
    2: (40, 120),
    3: (120, 200),
    4: (200, 280),
    5: (280, 360),
    6: (360, 440),
    7: (440, 520),
    8: (520, 9999)
}

# Tier value scores for prioritization
TIER_SCORES = {
    "S+": 1.0, "S": 0.85, "A": 0.7, "B": 0.5, "C": 0.3, "D": 0.15
}

# Best joiner heroes (verified)
JOINER_HEROES = {
    "attack": {
        "hero": "Jessie",
        "skill": "Stand of Arms",
        "effect_per_level": [5, 10, 15, 20, 25],
        "unit": "% DMG dealt"
    },
    "defense": {
        "hero": "Sergey",
        "skill": "Defenders' Edge",
        "effect_per_level": [4, 8, 12, 16, 20],
        "unit": "% DMG reduction"
    }
}


class HeroAnalyzer:
    """Analyze heroes and generate upgrade recommendations."""

    def __init__(self, heroes_data: dict):
        """
        Initialize with static hero data.

        Args:
            heroes_data: Hero data from heroes.json
        """
        self.heroes_data = heroes_data
        self.hero_lookup = {h['name']: h for h in heroes_data.get('heroes', [])}

    def get_current_generation(self, server_age_days: int) -> int:
        """Determine current generation based on server age."""
        for gen, (start, end) in GENERATION_TIMELINE.items():
            if start <= server_age_days < end:
                return gen
        return 8

    def get_generation_relevance(self, hero_name: str, current_gen: int) -> float:
        """Calculate how relevant a hero is based on generation."""
        hero_data = self.hero_lookup.get(hero_name, {})
        hero_gen = hero_data.get('generation', 1)

        gen_diff = current_gen - hero_gen

        if gen_diff <= 0:
            return 1.0  # Current or future gen
        elif gen_diff == 1:
            return 0.9  # Still very relevant
        elif gen_diff == 2:
            return 0.7  # Moderately relevant
        elif gen_diff == 3:
            return 0.5  # Getting outdated
        else:
            return 0.3  # Very old

        # S+ tier heroes stay relevant longer
        tier = hero_data.get('tier_overall', 'C')
        if tier == 'S+' and gen_diff <= 3:
            return min(1.0, relevance + 0.15)

        return relevance

    def analyze(self, profile, user_heroes: list) -> List[HeroRecommendation]:
        """
        Analyze user's heroes and generate recommendations.

        Args:
            profile: User profile with priorities and server info
            user_heroes: List of user's owned heroes with stats

        Returns:
            List of HeroRecommendation objects
        """
        recommendations = []
        server_age = getattr(profile, 'server_age_days', 0)
        current_gen = self.get_current_generation(server_age)

        # Get priority weights
        priority_svs = getattr(profile, 'priority_svs', 5)
        priority_rally = getattr(profile, 'priority_rally', 4)
        priority_castle = getattr(profile, 'priority_castle_battle', 4)
        priority_pve = getattr(profile, 'priority_exploration', 3)

        # Build owned heroes set
        owned_heroes = set()
        hero_stats = {}
        for uh in user_heroes:
            name = uh.hero.name if hasattr(uh, 'hero') and uh.hero else getattr(uh, 'name', '')
            if name:
                owned_heroes.add(name)
                hero_stats[name] = {
                    'level': getattr(uh, 'level', 1),
                    'stars': getattr(uh, 'star_rank', getattr(uh, 'stars', 1)),
                    'exploration_skill': getattr(uh, 'exploration_skill_level', 1),
                    'expedition_skill': getattr(uh, 'expedition_skill_level', 1)
                }

        # Rule 1: Check for main three heroes underlevel
        recommendations.extend(
            self._check_main_three(hero_stats, current_gen)
        )

        # Rule 2: Check joiner heroes (Jessie/Sergey)
        recommendations.extend(
            self._check_joiner_heroes(owned_heroes, hero_stats, priority_rally, priority_castle)
        )

        # Rule 3: Check generation-appropriate heroes
        recommendations.extend(
            self._check_generation_heroes(owned_heroes, current_gen, priority_svs)
        )

        # Rule 4: Check skill gaps
        recommendations.extend(
            self._check_skill_gaps(hero_stats, priority_rally, priority_pve, current_gen)
        )

        # Rule 5: Check star progression opportunities
        recommendations.extend(
            self._check_star_progression(hero_stats, current_gen)
        )

        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)

        return recommendations

    def _check_main_three(self, hero_stats: dict, current_gen: int) -> List[HeroRecommendation]:
        """Check if user has at least 3 heroes at decent levels."""
        recommendations = []

        if not hero_stats:
            return [HeroRecommendation(
                priority=1,
                action="Add heroes to your profile",
                hero="Any",
                reason="No heroes tracked. Add your heroes to get personalized recommendations.",
                resources="N/A",
                relevance_tags=['all'],
                rule_id="no_heroes"
            )]

        # Count heroes at level 40+
        high_level_count = sum(1 for stats in hero_stats.values() if stats['level'] >= 40)

        if high_level_count < 3:
            # Find the best candidates to level
            underlevel_heroes = [
                (name, stats) for name, stats in hero_stats.items()
                if stats['level'] < 40
            ]

            for name, stats in underlevel_heroes[:3 - high_level_count]:
                hero_data = self.hero_lookup.get(name, {})
                tier = hero_data.get('tier_overall', 'C')
                tier_score = TIER_SCORES.get(tier, 0.3)

                if tier_score >= 0.7:  # A tier or higher
                    recommendations.append(HeroRecommendation(
                        priority=1,
                        action=f"Level {name} to 40+",
                        hero=name,
                        reason=f"{tier} tier hero, only Lv{stats['level']}. Focus main 3 heroes before spreading investment.",
                        resources="Hero XP items, Meat for barracks",
                        relevance_tags=['all'],
                        rule_id="level_main_three"
                    ))

        return recommendations

    def _check_joiner_heroes(self, owned: set, stats: dict, rally_priority: int, castle_priority: int) -> List[HeroRecommendation]:
        """Check joiner hero status (Jessie for attack, Sergey for defense)."""
        recommendations = []

        # Check Jessie for attack joining
        if rally_priority >= 3:
            if "Jessie" not in owned:
                recommendations.append(HeroRecommendation(
                    priority=1 if rally_priority >= 4 else 2,
                    action="Unlock Jessie",
                    hero="Jessie",
                    reason="Best attack joiner. Her Stand of Arms (+5-25% DMG) is the top skill when joining rallies.",
                    resources="Jessie shards from events/shop",
                    relevance_tags=['rally', 'svs'],
                    rule_id="unlock_jessie"
                ))
            elif "Jessie" in stats:
                jessie_skill = stats["Jessie"]['expedition_skill']
                if jessie_skill < 5:
                    current_bonus = JOINER_HEROES["attack"]["effect_per_level"][jessie_skill - 1]
                    recommendations.append(HeroRecommendation(
                        priority=1 if rally_priority >= 4 else 2,
                        action=f"Max Jessie's expedition skill (currently Lv{jessie_skill})",
                        hero="Jessie",
                        reason=f"Stand of Arms at +{current_bonus}% → +25% at L5. Put her slot 1 when joining rallies!",
                        resources="Expedition Manuals",
                        relevance_tags=['rally', 'svs'],
                        rule_id="level_jessie_skill"
                    ))

        # Check Sergey for defense joining
        if castle_priority >= 3:
            if "Sergey" not in owned:
                recommendations.append(HeroRecommendation(
                    priority=2,
                    action="Unlock Sergey",
                    hero="Sergey",
                    reason="Best defense joiner. His Defenders' Edge (-4-20% DMG taken) protects garrison.",
                    resources="Sergey shards from events/shop",
                    relevance_tags=['castle', 'garrison'],
                    rule_id="unlock_sergey"
                ))
            elif "Sergey" in stats:
                sergey_skill = stats["Sergey"]['expedition_skill']
                if sergey_skill < 5:
                    current_bonus = JOINER_HEROES["defense"]["effect_per_level"][sergey_skill - 1]
                    recommendations.append(HeroRecommendation(
                        priority=2,
                        action=f"Level Sergey's expedition skill (currently Lv{sergey_skill})",
                        hero="Sergey",
                        reason=f"Defenders' Edge at -{current_bonus}% → -20% at L5. Put him slot 1 when reinforcing!",
                        resources="Expedition Manuals",
                        relevance_tags=['castle', 'garrison'],
                        rule_id="level_sergey_skill"
                    ))

        return recommendations

    def _check_generation_heroes(self, owned: set, current_gen: int, svs_priority: int) -> List[HeroRecommendation]:
        """Check if user has generation-appropriate heroes."""
        recommendations = []

        if current_gen < 2:
            return recommendations  # Gen 1 only, no newer heroes available

        # Key heroes by generation
        GEN_HEROES = {
            2: ["Flint", "Philly", "Alonso"],
            3: ["Logan", "Mia", "Greg"],
            4: ["Ahmose", "Reina", "Lynn"],
            5: ["Hector", "Wu Ming"],
            6: ["Patrick", "Charlie", "Cloris"],
            7: ["Gordon", "Renee", "Eugene"]
        }

        # Check if user has any heroes from recent generations
        for gen in range(max(2, current_gen - 1), current_gen + 1):
            gen_heroes = GEN_HEROES.get(gen, [])
            owned_from_gen = owned.intersection(gen_heroes)

            if not owned_from_gen and gen <= current_gen:
                priority = 2 if gen == current_gen else 3
                recommendations.append(HeroRecommendation(
                    priority=priority,
                    action=f"Acquire Gen {gen} heroes",
                    hero=", ".join(gen_heroes[:2]),
                    reason=f"Gen {gen} heroes are significant upgrades. {gen_heroes[0]} or {gen_heroes[1]} recommended.",
                    resources="Hero shards from events, packs, or VIP shop",
                    relevance_tags=['svs', 'rally', 'progression'],
                    rule_id=f"acquire_gen{gen}"
                ))

        return recommendations

    def _check_skill_gaps(self, stats: dict, rally_priority: int, pve_priority: int, current_gen: int) -> List[HeroRecommendation]:
        """Check for skill upgrade opportunities."""
        recommendations = []

        for name, hero_stats in stats.items():
            hero_data = self.hero_lookup.get(name, {})
            tier = hero_data.get('tier_overall', 'C')
            tier_score = TIER_SCORES.get(tier, 0.3)
            gen_relevance = self.get_generation_relevance(name, current_gen)

            # Skip low-tier or outdated heroes
            if tier_score * gen_relevance < 0.4:
                continue

            level = hero_stats['level']
            exp_skill = hero_stats['expedition_skill']
            expl_skill = hero_stats['exploration_skill']

            # Check expedition skill gap (for rally/SvS players)
            if rally_priority >= 3 and exp_skill < 5 and level >= 30:
                recommendations.append(HeroRecommendation(
                    priority=2,
                    action=f"Upgrade {name}'s expedition skill to L{exp_skill + 1}",
                    hero=name,
                    reason=f"{tier} tier hero. Expedition skills boost rally/SvS performance.",
                    resources="Expedition Manuals",
                    relevance_tags=['rally', 'svs'],
                    rule_id="upgrade_expedition_skill"
                ))

            # Check exploration skill gap (for PvE players)
            if pve_priority >= 3 and expl_skill < 5 and level >= 30:
                recommendations.append(HeroRecommendation(
                    priority=3,
                    action=f"Upgrade {name}'s exploration skill to L{expl_skill + 1}",
                    hero=name,
                    reason=f"{tier} tier hero. Exploration skills help clear PvE content.",
                    resources="Exploration Manuals",
                    relevance_tags=['pve', 'exploration'],
                    rule_id="upgrade_exploration_skill"
                ))

        return recommendations

    def _check_star_progression(self, stats: dict, current_gen: int) -> List[HeroRecommendation]:
        """Check for star/ascension opportunities."""
        recommendations = []

        for name, hero_stats in stats.items():
            hero_data = self.hero_lookup.get(name, {})
            tier = hero_data.get('tier_overall', 'C')
            tier_score = TIER_SCORES.get(tier, 0.3)
            gen_relevance = self.get_generation_relevance(name, current_gen)

            # Only recommend star upgrades for relevant heroes
            if tier_score * gen_relevance < 0.5:
                continue

            stars = hero_stats['stars']
            level = hero_stats['level']

            # Check for star breakpoints
            if stars < 5 and level >= 40:
                recommendations.append(HeroRecommendation(
                    priority=3,
                    action=f"Ascend {name} to {stars + 1} stars",
                    hero=name,
                    reason=f"{tier} tier hero at {stars}★. Star upgrades provide significant stat boosts.",
                    resources=f"{name} shards or universal shards",
                    relevance_tags=['all'],
                    rule_id="ascend_stars"
                ))

        return recommendations
