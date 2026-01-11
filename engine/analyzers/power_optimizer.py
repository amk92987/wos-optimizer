"""
Power Optimizer - Analyzes upgrade paths and calculates power efficiency.
Uses collected game data to provide power-backed upgrade recommendations.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PowerUpgrade:
    """A power-based upgrade recommendation."""
    upgrade_type: str  # chief_gear, chief_charm, hero_level, hero_star, troop_tier, war_academy, research, pet, daybreak
    target: str        # Slot name, hero name, troop type, etc.
    from_level: Any    # Current level/tier
    to_level: Any      # Target level/tier
    power_gain: float  # Estimated or exact power gain
    bonus_gain: float  # % bonus gain (for gear/charms)
    resource_cost: Dict[str, int]  # Resources required
    efficiency: float  # power_gain / normalized_cost (higher = better)
    priority: int      # 1-5, 1 being highest
    reason: str        # Explanation for the recommendation
    confidence: str    # "exact", "estimated", "qualitative"
    relevance_tags: List[str] = field(default_factory=list)


# Slot display names
GEAR_SLOT_NAMES = {
    "cap": "Cap (Lancer)",
    "watch": "Watch (Lancer)",
    "coat": "Coat (Infantry)",
    "pants": "Pants (Infantry)",
    "belt": "Belt (Marksman)",
    "weapon": "Weapon (Marksman)"
}

CHARM_TYPE_NAMES = {
    "protection": "Protection (Infantry)",
    "keenness": "Keenness (Lancer)",
    "vision": "Vision (Marksman)"
}


class PowerOptimizer:
    """Analyze upgrade paths and calculate power efficiency."""

    def __init__(self, data_path: str = None):
        """
        Initialize with game data files.

        Args:
            data_path: Path to the data directory. Defaults to project data/ folder.
        """
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data"
        else:
            data_path = Path(data_path)

        self.data_path = data_path

        # Load data files
        self.chief_equipment = self._load_json("chief_equipment_data.json")
        self.hero_power = self._load_json("hero_power_data.json")
        self.troop_data = self._load_json("troop_data.json")
        self.war_academy = self._load_json("upgrades/war_academy.steps.json")

        # Build lookup tables
        self.gear_tiers = {t["tier"]: t for t in self.chief_equipment.get("chief_gear", {}).get("tier_progression", [])}
        self.charm_levels = {c["level"]: c for c in self.chief_equipment.get("chief_charms", {}).get("level_progression", [])}
        self.troop_power = self.troop_data.get("power_per_unit", {}).get("tiers", {})
        self.war_academy_edges = {e["from"]["level"]: e for e in self.war_academy.get("edges", [])}

    def _load_json(self, filename: str) -> dict:
        """Load a JSON data file."""
        filepath = self.data_path / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def analyze(self, profile, user_data: dict) -> List[PowerUpgrade]:
        """
        Analyze user data and generate power-based upgrade recommendations.

        Args:
            profile: User profile with priorities and server info
            user_data: Dict containing user_heroes, user_gear, user_charms

        Returns:
            List of PowerUpgrade recommendations sorted by efficiency
        """
        recommendations = []

        # Analyze each system
        recommendations.extend(self._analyze_chief_gear(user_data.get("user_gear", [])))
        recommendations.extend(self._analyze_chief_charms(user_data.get("user_charms", [])))
        recommendations.extend(self._analyze_hero_upgrades(user_data.get("user_heroes", []), profile))
        recommendations.extend(self._analyze_troop_upgrades(profile))
        recommendations.extend(self._analyze_war_academy(profile))

        # Add qualitative recommendations for systems we don't track
        recommendations.extend(self._analyze_research())
        recommendations.extend(self._analyze_pets())
        recommendations.extend(self._analyze_daybreak())

        # Sort by efficiency (descending) then priority (ascending)
        recommendations.sort(key=lambda x: (-x.efficiency, x.priority))

        return recommendations

    def _analyze_chief_gear(self, user_gear: list) -> List[PowerUpgrade]:
        """
        Analyze chief gear upgrades.
        Exact % bonus data available for all 42 tiers.
        """
        recommendations = []

        # Build current gear state
        # UserChiefGear ORM model uses: helmet, armor, gloves, boots, ring, amulet
        # Map to game slots: cap, watch, coat, pants, belt, weapon
        orm_slot_map = {
            'helmet': 'cap',
            'armor': 'coat',
            'gloves': 'pants',  # best guess
            'boots': 'watch',   # best guess
            'ring': 'belt',
            'amulet': 'weapon'
        }

        gear_by_slot = {}
        for g in user_gear:
            if isinstance(g, dict):
                slot = g.get('slot')
                tier = g.get('tier', 1)
                if slot:
                    gear_by_slot[slot] = tier
            else:
                # Handle ORM object - extract from quality_level columns
                for orm_slot, game_slot in orm_slot_map.items():
                    quality = getattr(g, f'{orm_slot}_quality', 1)
                    level = getattr(g, f'{orm_slot}_level', 1)
                    # Convert quality (1-7) to approximate tier (1-42)
                    # Quality 1=Gray(1-2), 2=Green(1-4), 3=Blue(3-6), 4=Purple(7-14), 5=Gold(15-26), 6=Pink(27-42)
                    tier_base = {1: 1, 2: 1, 3: 3, 4: 7, 5: 15, 6: 27, 7: 35}.get(quality, 1)
                    estimated_tier = min(42, tier_base + level - 1)
                    gear_by_slot[game_slot] = estimated_tier

        # Default to tier 1 for unset slots
        for slot in ["cap", "watch", "coat", "pants", "belt", "weapon"]:
            if slot not in gear_by_slot:
                gear_by_slot[slot] = 1

        # Priority order: Infantry (coat/pants) > Marksman (belt/weapon) > Lancer (cap/watch)
        slot_priority = {
            "coat": 1, "pants": 1,
            "belt": 2, "weapon": 2,
            "cap": 3, "watch": 3
        }

        for slot, current_tier in gear_by_slot.items():
            if current_tier >= 42:
                continue  # Already maxed

            current_data = self.gear_tiers.get(current_tier, {})
            next_tier = current_tier + 1
            next_data = self.gear_tiers.get(next_tier, {})

            if not next_data:
                continue

            current_bonus = current_data.get("bonus_percent", 0)
            next_bonus = next_data.get("bonus_percent", 0)
            bonus_gain = next_bonus - current_bonus

            # Estimate power gain from bonus increase
            # Each 1% bonus ~= 500-1000 power depending on base stats
            estimated_power = bonus_gain * 750

            # Efficiency based on tier progression cost (higher tiers cost more)
            # Early tiers: high efficiency. Late tiers: lower efficiency
            efficiency = estimated_power / (current_tier * 100)

            base_priority = slot_priority.get(slot, 2)
            # Adjust priority based on how far behind this slot is
            avg_tier = sum(gear_by_slot.values()) / len(gear_by_slot)
            if current_tier < avg_tier - 3:
                priority = max(1, base_priority - 1)  # Boost priority for lagging slots
            else:
                priority = base_priority

            recommendations.append(PowerUpgrade(
                upgrade_type="chief_gear",
                target=GEAR_SLOT_NAMES.get(slot, slot),
                from_level=current_data.get("name", f"Tier {current_tier}"),
                to_level=next_data.get("name", f"Tier {next_tier}"),
                power_gain=estimated_power,
                bonus_gain=bonus_gain,
                resource_cost={"hardened_alloy": current_tier * 50, "polishing_solution": current_tier * 30},
                efficiency=efficiency,
                priority=priority,
                reason=f"+{bonus_gain:.1f}% bonus ({current_bonus:.1f}% → {next_bonus:.1f}%)",
                confidence="estimated",
                relevance_tags=["gear", "all"]
            ))

        return recommendations

    def _analyze_chief_charms(self, user_charms: list) -> List[PowerUpgrade]:
        """
        Analyze chief charm upgrades.
        Exact % bonus data available for all 16 levels.
        """
        recommendations = []

        # Build current charm state: {(gear_slot, charm_type): level}
        # UserChiefCharm ORM model has columns like: cap_protection, cap_keenness, cap_vision, etc.
        gear_slots = ["cap", "watch", "coat", "pants", "belt", "weapon"]
        charm_types = ["protection", "keenness", "vision"]

        charms_by_key = {}
        for c in user_charms:
            if isinstance(c, dict):
                # Dict format: individual charm objects
                gear_slot = c.get('gear_slot')
                charm_type = c.get('charm_type')
                level = c.get('level', 1)
                if gear_slot and charm_type:
                    charms_by_key[(gear_slot, charm_type)] = level
            else:
                # ORM object: has columns like cap_protection, watch_keenness, etc.
                for slot in gear_slots:
                    for ctype in charm_types:
                        attr_name = f"{slot}_{ctype}"
                        level = getattr(c, attr_name, 1)
                        if level:
                            charms_by_key[(slot, ctype)] = level

        # Default to level 1 for unset charms
        for slot in gear_slots:
            for charm_type in charm_types:
                if (slot, charm_type) not in charms_by_key:
                    charms_by_key[(slot, charm_type)] = 1

        # Priority: Protection (Infantry) > Vision (Marksman) > Keenness (Lancer)
        type_priority = {"protection": 1, "vision": 2, "keenness": 3}

        for (slot, charm_type), current_level in charms_by_key.items():
            if current_level >= 16:
                continue  # Already maxed

            current_data = self.charm_levels.get(current_level, {})
            next_level = current_level + 1
            next_data = self.charm_levels.get(next_level, {})

            if not next_data:
                continue

            current_bonus = current_data.get("bonus_percent", 0)
            next_bonus = next_data.get("bonus_percent", 0)
            bonus_gain = next_bonus - current_bonus

            # Estimate power gain
            estimated_power = bonus_gain * 500

            # Efficiency decreases as level increases (higher levels cost more)
            efficiency = estimated_power / (current_level * 75)

            priority = type_priority.get(charm_type, 2)

            # Check if this is a major milestone (shape change)
            current_shape = current_data.get("shape", "")
            next_shape = next_data.get("shape", "")
            shape_change = f" ({current_shape} → {next_shape})" if current_shape != next_shape else ""

            slot_name = GEAR_SLOT_NAMES.get(slot, slot).split(" ")[0]
            type_name = CHARM_TYPE_NAMES.get(charm_type, charm_type).split(" ")[0]

            recommendations.append(PowerUpgrade(
                upgrade_type="chief_charm",
                target=f"{slot_name} {type_name}",
                from_level=f"Lv{current_level}",
                to_level=f"Lv{next_level}",
                power_gain=estimated_power,
                bonus_gain=bonus_gain,
                resource_cost={"charm_designs": current_level * 20, "charm_guides": current_level * 15},
                efficiency=efficiency,
                priority=priority,
                reason=f"+{bonus_gain:.0f}% bonus ({current_bonus:.0f}% → {next_bonus:.0f}%){shape_change}",
                confidence="estimated",
                relevance_tags=["charms", "all"]
            ))

        return recommendations

    def _analyze_hero_upgrades(self, user_heroes: list, profile) -> List[PowerUpgrade]:
        """
        Analyze hero level and star upgrades.
        Uses XP requirements and stat scaling estimates.
        """
        recommendations = []

        xp_data = self.hero_power.get("hero_xp_requirements", {}).get("levels", {})
        star_data = self.hero_power.get("hero_stars", {}).get("shards_required", {})

        for hero in user_heroes:
            name = getattr(hero, 'hero', None)
            if hasattr(name, 'name'):
                name = name.name
            elif hasattr(hero, 'name'):
                name = hero.name
            else:
                name = hero.get('name', 'Unknown')

            level = getattr(hero, 'level', 1) if hasattr(hero, 'level') else hero.get('level', 1)
            stars = getattr(hero, 'star_rank', 0) if hasattr(hero, 'star_rank') else hero.get('stars', 0)

            # Level upgrade recommendation
            if level < 80:
                next_level = min(level + 5, 80)  # Suggest 5-level jumps

                # Estimate power gain per level (scales with level)
                power_per_level = 500 + (level * 20)  # Base 500, +20 per level
                power_gain = power_per_level * (next_level - level)

                # XP cost for efficiency calculation
                xp_cost = sum(int(xp_data.get(str(l), {}).get("xp", 0)) for l in range(level, next_level))
                efficiency = power_gain / max(1, xp_cost / 10000)

                priority = 2 if level < 40 else 3

                recommendations.append(PowerUpgrade(
                    upgrade_type="hero_level",
                    target=name,
                    from_level=f"Lv{level}",
                    to_level=f"Lv{next_level}",
                    power_gain=power_gain,
                    bonus_gain=0,
                    resource_cost={"hero_xp": xp_cost},
                    efficiency=efficiency,
                    priority=priority,
                    reason=f"~{power_per_level:,} power/level. Higher levels increase troop capacity.",
                    confidence="estimated",
                    relevance_tags=["heroes", "all"]
                ))

            # Star upgrade recommendation
            if stars < 5:
                next_star = stars + 1
                star_names = {0: "unlock", 1: "1_star", 2: "2_stars", 3: "3_stars", 4: "4_stars", 5: "5_stars"}
                shards_needed = star_data.get(star_names.get(next_star, ""), 0)

                # Star upgrades provide significant stat boosts (~10-15% per star)
                power_gain = 15000 + (stars * 5000)  # Bigger gains at higher stars
                efficiency = power_gain / max(1, shards_needed * 100)

                priority = 2 if stars < 3 else 3

                unlocks = ""
                if next_star == 1:
                    unlocks = " Unlocks Exclusive Gear slot!"
                elif next_star == 4:
                    unlocks = " Can max all skills!"

                recommendations.append(PowerUpgrade(
                    upgrade_type="hero_star",
                    target=name,
                    from_level=f"{stars}★",
                    to_level=f"{next_star}★",
                    power_gain=power_gain,
                    bonus_gain=0,
                    resource_cost={f"{name}_shards": shards_needed},
                    efficiency=efficiency,
                    priority=priority,
                    reason=f"~10-15% stat boost. Needs {shards_needed} shards.{unlocks}",
                    confidence="estimated",
                    relevance_tags=["heroes", "all"]
                ))

        return recommendations

    def _analyze_troop_upgrades(self, profile) -> List[PowerUpgrade]:
        """
        Analyze troop tier upgrades.
        Exact power per unit data available for all tiers.
        """
        recommendations = []

        # Get user's current highest troop tier from profile if available
        current_tier = getattr(profile, 'troop_tier', 5) if profile else 5

        if current_tier >= 11:
            return recommendations  # Already at T11

        next_tier = current_tier + 1
        tier_key = f"T{current_tier}"
        next_tier_key = f"T{next_tier}"

        current_power = self.troop_power.get(tier_key, {})
        next_power = self.troop_power.get(next_tier_key, {})

        if not next_power:
            return recommendations

        for troop_type in ["infantry", "lancer", "marksman"]:
            curr_ppu = current_power.get(troop_type, 0)
            next_ppu = next_power.get(troop_type, 0)
            power_diff = next_ppu - curr_ppu

            # Assume 50,000 troops for power calculation
            troop_count = 50000
            total_power_gain = power_diff * troop_count

            # T11 is special - much bigger jump for lancers/marksmen
            if next_tier == 11 and troop_type in ["lancer", "marksman"]:
                priority = 1
                reason = f"MASSIVE jump: {curr_ppu} → {next_ppu} power/unit! T11 requires War Academy."
            else:
                priority = 3
                reason = f"+{power_diff} power/unit ({curr_ppu} → {next_ppu}). Per 50k troops: +{total_power_gain:,} power."

            efficiency = total_power_gain / 10000  # Normalized

            recommendations.append(PowerUpgrade(
                upgrade_type="troop_tier",
                target=troop_type.capitalize(),
                from_level=tier_key,
                to_level=next_tier_key,
                power_gain=total_power_gain,
                bonus_gain=0,
                resource_cost={"camp_upgrade": 1},
                efficiency=efficiency,
                priority=priority,
                reason=reason,
                confidence="exact",
                relevance_tags=["troops", "all"]
            ))

        return recommendations

    def _analyze_war_academy(self, profile) -> List[PowerUpgrade]:
        """
        Analyze War Academy upgrades.
        Has EXACT power_gain values from game data!
        """
        recommendations = []

        # Get current war academy level from profile
        current_level = getattr(profile, 'war_academy_level', 'FC1-0') if profile else 'FC1-0'

        edge = self.war_academy_edges.get(current_level)
        if not edge:
            return recommendations

        power_gain = edge.get("power_gain", 0)
        to_level = edge.get("to", {}).get("level", "")
        cost = edge.get("cost", {})
        prereq = edge.get("prereq", {}).get("furnace_fc_level", "")

        # Calculate efficiency based on fire crystal cost
        fc_cost = cost.get("fire_crystal_shards", 0) + cost.get("refined_fire_crystals", 0) * 10
        efficiency = power_gain / max(1, fc_cost)

        # Parse FC level for priority
        fc_num = int(current_level.split("-")[0].replace("FC", "")) if "FC" in current_level else 1
        priority = 2 if fc_num < 5 else 3

        cost_summary = []
        if cost.get("fire_crystal_shards", 0) > 0:
            cost_summary.append(f"{cost['fire_crystal_shards']} FC shards")
        if cost.get("refined_fire_crystals", 0) > 0:
            cost_summary.append(f"{cost['refined_fire_crystals']} refined FC")

        recommendations.append(PowerUpgrade(
            upgrade_type="war_academy",
            target="War Academy",
            from_level=current_level,
            to_level=to_level,
            power_gain=power_gain,
            bonus_gain=0,
            resource_cost=cost,
            efficiency=efficiency,
            priority=priority,
            reason=f"EXACT: +{power_gain:,} power. Requires {prereq}. Cost: {', '.join(cost_summary)}",
            confidence="exact",
            relevance_tags=["war_academy", "troops", "all"]
        ))

        return recommendations

    def _analyze_research(self) -> List[PowerUpgrade]:
        """
        Provide qualitative research recommendations.
        We don't track user's research progress.
        """
        return [PowerUpgrade(
            upgrade_type="research",
            target="Research Trees",
            from_level="Current",
            to_level="Next",
            power_gain=0,
            bonus_gain=0,
            resource_cost={},
            efficiency=0,
            priority=4,
            reason="Focus: Battle tree for combat, Growth tree for resources, Economy for production. Not tracked.",
            confidence="qualitative",
            relevance_tags=["research", "all"]
        )]

    def _analyze_pets(self) -> List[PowerUpgrade]:
        """
        Provide qualitative pet recommendations.
        We don't track user's pet levels.
        """
        return [PowerUpgrade(
            upgrade_type="pet",
            target="Pets",
            from_level="Current",
            to_level="Next",
            power_gain=0,
            bonus_gain=0,
            resource_cost={},
            efficiency=0,
            priority=4,
            reason="Priority: Panda (All troops buff), Fox (Marksman), Bear (Infantry), Lion (Lancer). Not tracked.",
            confidence="qualitative",
            relevance_tags=["pets", "all"]
        )]

    def _analyze_daybreak(self) -> List[PowerUpgrade]:
        """
        Provide qualitative Daybreak Island recommendations.
        We don't track user's Tree of Life progress.
        """
        return [PowerUpgrade(
            upgrade_type="daybreak",
            target="Daybreak Island - Tree of Life",
            from_level="Current",
            to_level="Next",
            power_gain=0,
            bonus_gain=0,
            resource_cost={},
            efficiency=0,
            priority=5,
            reason="Tree of Life provides troop stat buffs. Unlocks at higher FC levels. Not tracked.",
            confidence="qualitative",
            relevance_tags=["daybreak", "all"]
        )]

    def get_top_recommendations(self, profile, user_data: dict, limit: int = 10) -> List[PowerUpgrade]:
        """
        Get top N recommendations by efficiency.
        Filters out qualitative (untracked) recommendations by default.
        """
        all_recs = self.analyze(profile, user_data)

        # Filter to only exact/estimated confidence
        tracked_recs = [r for r in all_recs if r.confidence != "qualitative"]

        return tracked_recs[:limit]

    def get_recommendations_by_type(self, profile, user_data: dict, upgrade_type: str) -> List[PowerUpgrade]:
        """Get recommendations filtered by upgrade type."""
        all_recs = self.analyze(profile, user_data)
        return [r for r in all_recs if r.upgrade_type == upgrade_type]
