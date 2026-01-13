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
        tier = hero_data.get('tier_overall', 'C')

        gen_diff = current_gen - hero_gen

        # Base relevance by generation gap
        if gen_diff <= 0:
            relevance = 1.0  # Current or future gen
        elif gen_diff == 1:
            relevance = 0.9  # Still very relevant
        elif gen_diff == 2:
            relevance = 0.7  # Moderately relevant
        elif gen_diff == 3:
            relevance = 0.5  # Getting outdated
        else:
            relevance = 0.3  # Very old

        # S+ tier heroes stay relevant longer
        if tier == 'S+' and gen_diff <= 3:
            relevance = min(1.0, relevance + 0.15)

        return relevance

    def rank_heroes_by_value(self, hero_stats: dict, current_gen: int) -> List[str]:
        """
        Rank owned heroes by investment value (tier * generation relevance).

        Returns list of hero names sorted by value (highest first).
        """
        hero_values = []
        for name in hero_stats.keys():
            hero_data = self.hero_lookup.get(name, {})
            tier = hero_data.get('tier_overall', 'C')
            tier_score = TIER_SCORES.get(tier, 0.3)
            gen_relevance = self.get_generation_relevance(name, current_gen)
            level = hero_stats[name].get('level', 1)

            # Value = tier * generation relevance * level factor
            level_factor = min(1.0, level / 50)  # Incentivize investing in already-leveled heroes
            value = tier_score * gen_relevance * (0.5 + 0.5 * level_factor)
            hero_values.append((name, value))

        # Sort by value descending
        hero_values.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in hero_values]

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

        # Get spending profile and farm status
        spending_profile = getattr(profile, 'spending_profile', 'f2p')
        is_farm = getattr(profile, 'is_farm_account', False)

        # Hero investment limits by spending profile
        hero_limits = {
            'f2p': 3,       # F2P should focus on 3 core heroes
            'minnow': 4,    # Minnows can invest in 4 heroes
            'dolphin': 6,   # Dolphins can spread across 6 heroes
            'orca': 10,     # Orcas have more flexibility
            'whale': 999,   # Whales can max everything
        }
        max_hero_focus = hero_limits.get(spending_profile, 3)

        # Build owned heroes set
        owned_heroes = set()
        hero_stats = {}
        for uh in user_heroes:
            name = uh.hero.name if hasattr(uh, 'hero') and uh.hero else getattr(uh, 'name', '')
            if name:
                owned_heroes.add(name)

                # Get individual skill levels (UserHero has 3 of each type)
                # Use 'or 1' to handle None values from database
                exp_skill_1 = getattr(uh, 'expedition_skill_1_level', None) or 1
                exp_skill_2 = getattr(uh, 'expedition_skill_2_level', None) or 1
                exp_skill_3 = getattr(uh, 'expedition_skill_3_level', None) or 1
                expl_skill_1 = getattr(uh, 'exploration_skill_1_level', None) or 1
                expl_skill_2 = getattr(uh, 'exploration_skill_2_level', None) or 1
                expl_skill_3 = getattr(uh, 'exploration_skill_3_level', None) or 1

                hero_stats[name] = {
                    'level': getattr(uh, 'level', 1),
                    'stars': getattr(uh, 'stars', 1),
                    # Individual expedition skills (skill 1 is the joiner skill for Jessie/Sergey)
                    'expedition_skill_1': exp_skill_1,
                    'expedition_skill_2': exp_skill_2,
                    'expedition_skill_3': exp_skill_3,
                    # Average for general skill recommendations
                    'expedition_skill': max(exp_skill_1, exp_skill_2, exp_skill_3),
                    'exploration_skill': max(expl_skill_1, expl_skill_2, expl_skill_3),
                    # Min for detecting undertrained skills
                    'expedition_skill_min': min(exp_skill_1, exp_skill_2, exp_skill_3),
                    'exploration_skill_min': min(expl_skill_1, expl_skill_2, expl_skill_3),
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

        # Get ranked heroes for investment priority
        ranked_heroes = self.rank_heroes_by_value(hero_stats, current_gen)
        top_heroes = set(ranked_heroes[:max_hero_focus])

        # Rule 4: Check skill gaps (spending-aware)
        recommendations.extend(
            self._check_skill_gaps(hero_stats, priority_rally, priority_pve, current_gen,
                                   top_heroes, spending_profile)
        )

        # Rule 5: Check star progression opportunities (spending-aware)
        recommendations.extend(
            self._check_star_progression(hero_stats, current_gen, top_heroes, spending_profile)
        )

        # Rule 6: Farm account specific recommendations
        if is_farm:
            recommendations.extend(
                self._check_farm_account(hero_stats, ranked_heroes, priority_svs)
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
                # Jessie's joiner skill is expedition_skill_1 (Stand of Arms)
                jessie_skill = stats["Jessie"]['expedition_skill_1']
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
                # Sergey's joiner skill is expedition_skill_1 (Defenders' Edge)
                sergey_skill = stats["Sergey"]['expedition_skill_1']
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

            if not owned_from_gen and gen <= current_gen and gen_heroes:
                priority = 2 if gen == current_gen else 3
                # Safely get hero names for recommendation
                hero_names = ", ".join(gen_heroes[:2]) if gen_heroes else f"Gen {gen} heroes"
                reason_heroes = " or ".join(gen_heroes[:2]) if len(gen_heroes) >= 2 else (gen_heroes[0] if gen_heroes else f"Gen {gen} hero")
                recommendations.append(HeroRecommendation(
                    priority=priority,
                    action=f"Acquire Gen {gen} heroes",
                    hero=hero_names,
                    reason=f"Gen {gen} heroes are significant upgrades. {reason_heroes} recommended.",
                    resources="Hero shards from events, packs, or VIP shop",
                    relevance_tags=['svs', 'rally', 'progression'],
                    rule_id=f"acquire_gen{gen}"
                ))

        return recommendations

    def _check_skill_gaps(self, stats: dict, rally_priority: int, pve_priority: int,
                          current_gen: int, top_heroes: set, spending_profile: str) -> List[HeroRecommendation]:
        """Check for skill upgrade opportunities (spending-profile-aware)."""
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

            # For F2P/minnow: Only recommend skills for top heroes
            is_top_hero = name in top_heroes
            if spending_profile in ('f2p', 'minnow') and not is_top_hero:
                continue

            # Adjust priority based on whether this is a focus hero
            priority_bonus = 0 if is_top_hero else 1

            # Check expedition skill gap (for rally/SvS players)
            if rally_priority >= 3 and exp_skill < 5 and level >= 30:
                reason = f"{tier} tier hero. Expedition skills boost rally/SvS performance."
                if not is_top_hero and spending_profile == 'dolphin':
                    reason += " (Lower priority - focus on core heroes first.)"

                recommendations.append(HeroRecommendation(
                    priority=2 + priority_bonus,
                    action=f"Upgrade {name}'s expedition skill to L{exp_skill + 1}",
                    hero=name,
                    reason=reason,
                    resources="Expedition Manuals",
                    relevance_tags=['rally', 'svs'],
                    rule_id="upgrade_expedition_skill"
                ))

            # Check exploration skill gap (for PvE players)
            if pve_priority >= 3 and expl_skill < 5 and level >= 30:
                reason = f"{tier} tier hero. Exploration skills help clear PvE content."
                if not is_top_hero and spending_profile == 'dolphin':
                    reason += " (Lower priority - focus on core heroes first.)"

                recommendations.append(HeroRecommendation(
                    priority=3 + priority_bonus,
                    action=f"Upgrade {name}'s exploration skill to L{expl_skill + 1}",
                    hero=name,
                    reason=reason,
                    resources="Exploration Manuals",
                    relevance_tags=['pve', 'exploration'],
                    rule_id="upgrade_exploration_skill"
                ))

        return recommendations

    def _check_star_progression(self, stats: dict, current_gen: int,
                                 top_heroes: set, spending_profile: str) -> List[HeroRecommendation]:
        """Check for star/ascension opportunities (spending-profile-aware)."""
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

            # For F2P/minnow: Only recommend stars for top heroes
            is_top_hero = name in top_heroes
            if spending_profile in ('f2p', 'minnow') and not is_top_hero:
                continue

            # Adjust priority based on whether this is a focus hero
            priority_bonus = 0 if is_top_hero else 1

            # Check for star breakpoints
            if stars < 5 and level >= 40:
                reason = f"{tier} tier hero at {stars} stars. Star upgrades provide significant stat boosts."

                # Add spending-aware advice
                if spending_profile == 'f2p':
                    reason += " Save universal shards for top 3 heroes only."
                elif spending_profile == 'minnow' and not is_top_hero:
                    reason += " (Lower priority - focus resources on core heroes.)"

                recommendations.append(HeroRecommendation(
                    priority=3 + priority_bonus,
                    action=f"Ascend {name} to {stars + 1} stars",
                    hero=name,
                    reason=reason,
                    resources=f"{name} shards or universal shards",
                    relevance_tags=['all'],
                    rule_id="ascend_stars"
                ))

        return recommendations

    def _check_farm_account(self, hero_stats: dict, ranked_heroes: List[str],
                            svs_priority: int) -> List[HeroRecommendation]:
        """Generate farm account specific recommendations."""
        recommendations = []

        # Farm accounts should focus on minimal hero investment
        if len(ranked_heroes) > 1:
            # Recommend focusing on just 1-2 heroes for farms
            recommendations.append(HeroRecommendation(
                priority=1,
                action="Focus on 1-2 heroes only",
                hero="Farm Focus",
                reason="Farm accounts should minimize hero investment. Pick 1 main hero (usually your strongest infantry) and possibly 1 joiner hero.",
                resources="Redirect other resources to main account",
                relevance_tags=['farm'],
                rule_id="farm_hero_focus"
            ))

        # If SvS priority is high, recommend Jessie for joining
        if svs_priority >= 3:
            has_jessie = "Jessie" in hero_stats
            if has_jessie:
                jessie_skill = hero_stats["Jessie"].get('expedition_skill_1', 1)
                if jessie_skill < 5:
                    recommendations.append(HeroRecommendation(
                        priority=2,
                        action=f"Max Jessie's expedition skill on farm",
                        hero="Jessie",
                        reason=f"Farm accounts joining rallies should max Jessie's Stand of Arms (currently L{jessie_skill}). Other heroes don't matter.",
                        resources="Expedition Manuals",
                        relevance_tags=['farm', 'rally'],
                        rule_id="farm_jessie_skill"
                    ))
            else:
                recommendations.append(HeroRecommendation(
                    priority=2,
                    action="Unlock Jessie on farm account",
                    hero="Jessie",
                    reason="For farm accounts joining rallies, Jessie is the only hero that matters. Get her and max her expedition skill.",
                    resources="Jessie shards from events",
                    relevance_tags=['farm', 'rally'],
                    rule_id="farm_unlock_jessie"
                ))

        # Recommend not investing in exploration skills on farms
        has_expl_investment = any(
            hero_stats[h].get('exploration_skill', 1) > 1
            for h in hero_stats
        )
        if has_expl_investment:
            recommendations.append(HeroRecommendation(
                priority=3,
                action="Skip exploration skills on farm",
                hero="Farm Focus",
                reason="Exploration skills are wasted on farm accounts. Save manuals for your main account.",
                resources="Transfer resources to main",
                relevance_tags=['farm'],
                rule_id="farm_skip_exploration"
            ))

        return recommendations
