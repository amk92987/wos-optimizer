"""
Progression Tracker - Identifies player's current game phase and provides phase-specific tips.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


def parse_fc_level(fc_level_raw) -> Optional[int]:
    """Parse FC level from various formats (int, 'FC5', 'FC2-0', '5', etc.)."""
    if fc_level_raw is None:
        return None
    if isinstance(fc_level_raw, int):
        return fc_level_raw
    if isinstance(fc_level_raw, str):
        # Extract first number from strings like "FC5", "FC10", "FC2-0", "5"
        match = re.search(r'\d+', fc_level_raw)
        if match:
            return int(match.group())
    return None


@dataclass
class ProgressionTip:
    """A progression-related tip or recommendation."""
    priority: int
    phase: str
    action: str
    reason: str
    relevance_tags: List[str]
    rule_id: str


# Progression phases based on Furnace level and server age
PHASES = {
    "early_game": {
        "name": "Early Game",
        "furnace_range": (1, 18),
        "state_age_range": (0, 54),
        "focus": [
            "Rush Furnace to L19 for Daybreak Island",
            "Unlock Research Center (Furnace L9)",
            "Build troop capacity",
            "Level main 3 heroes"
        ],
        "common_mistakes": [
            "Spreading hero investment too thin",
            "Buying resources with gems",
            "Upgrading defensive chief gear first",
            "Ignoring expedition skills"
        ],
        "bottlenecks": ["speedups", "resources"],
        "priorities": ["furnace", "heroes", "troops"]
    },
    "mid_game": {
        "name": "Mid Game",
        "furnace_range": (19, 29),
        "state_age_range": (55, 199),
        "focus": [
            "Push Furnace to L30 for FC unlock",
            "Develop pet collection (unlocked at L18 + 55 days)",
            "Establish charm progression (L25)",
            "Build Gen 3-5 hero roster"
        ],
        "common_mistakes": [
            "Ignoring Chief Gear for Hero Gear",
            "Wrong skill priorities (exploration vs expedition)",
            "Not preparing for FC transition",
            "Over-investing in Gen 1 heroes"
        ],
        "bottlenecks": ["speedups", "hero_shards", "charm_materials"],
        "priorities": ["furnace_30", "chief_gear", "heroes", "pets"]
    },
    "late_game": {
        "name": "Late Game (FC Era)",
        "furnace_range": (30, 30),
        "furnace_fc_range": ("FC1", "FC5"),
        "state_age_range": (200, 400),
        "focus": [
            "FC Furnace progression",
            "War Academy for troop efficiency",
            "Hero Gear Mastery leveling",
            "T10+ troop development"
        ],
        "common_mistakes": [
            "Still using Gen 1 lineups",
            "Not adapting to meta shifts",
            "Ignoring Fire Crystal economy",
            "Under-investing in War Academy"
        ],
        "bottlenecks": ["fire_crystals", "fc_speedups", "essence_stones"],
        "priorities": ["fc_progression", "war_academy", "hero_gear", "troops"]
    },
    "endgame": {
        "name": "Endgame",
        "furnace_fc_range": ("FC5", "FC10+"),
        "state_age_range": (400, 9999),
        "focus": [
            "Complete FC10 progression",
            "Max Hero Gear Mastery",
            "Charm L12-16 (Gen 7+)",
            "Power efficiency for SvS"
        ],
        "common_mistakes": [
            "Not optimizing marginal gains",
            "Ignoring new generation features",
            "Inefficient resource allocation"
        ],
        "bottlenecks": ["time", "whale_currencies", "refined_fc"],
        "priorities": ["optimization", "power_efficiency", "svs_dominance"]
    }
}


class ProgressionTracker:
    """Track player progression and provide phase-specific recommendations."""

    def __init__(self, phases_data: dict = None):
        """
        Initialize with optional custom phases data.

        Args:
            phases_data: Custom phases data (defaults to PHASES)
        """
        self.phases = phases_data or PHASES

    def detect_phase(self, profile) -> str:
        """
        Detect player's current progression phase.

        Args:
            profile: User profile with furnace_level and server_age_days

        Returns:
            Phase ID string
        """
        furnace_level = getattr(profile, 'furnace_level', 1)
        server_age = getattr(profile, 'server_age_days', 0)
        fc_level = parse_fc_level(getattr(profile, 'furnace_fc_level', None))

        # Check for endgame (FC5+)
        if fc_level and fc_level >= 5:
            return "endgame"

        # Check for late game (FC era)
        if furnace_level >= 30 or fc_level:
            return "late_game"

        # Check for mid game (Daybreak Island unlocked)
        if furnace_level >= 19 or server_age >= 55:
            return "mid_game"

        return "early_game"

    def get_phase_info(self, phase_id: str) -> dict:
        """Get information about a specific phase."""
        return self.phases.get(phase_id, self.phases["early_game"])

    def get_phase_tips(self, profile) -> List[ProgressionTip]:
        """
        Get progression tips for the current phase.

        Args:
            profile: User profile

        Returns:
            List of ProgressionTip objects
        """
        phase_id = self.detect_phase(profile)
        phase = self.get_phase_info(phase_id)
        tips = []

        # Add focus area tips
        for i, focus in enumerate(phase["focus"][:3]):
            tips.append(ProgressionTip(
                priority=i + 2,
                phase=phase["name"],
                action=focus,
                reason=f"Key focus for {phase['name']} players",
                relevance_tags=['progression', phase_id],
                rule_id=f"phase_{phase_id}_focus_{i}"
            ))

        # Add mistake warnings
        for mistake in phase["common_mistakes"][:2]:
            tips.append(ProgressionTip(
                priority=4,
                phase=phase["name"],
                action=f"Avoid: {mistake}",
                reason=f"Common mistake in {phase['name']}",
                relevance_tags=['warning', phase_id],
                rule_id=f"phase_{phase_id}_warning"
            ))

        return tips

    def get_next_milestone(self, profile) -> Dict[str, Any]:
        """
        Get the next major milestone for the player.

        Args:
            profile: User profile

        Returns:
            Dict with milestone info
        """
        furnace_level = getattr(profile, 'furnace_level', 1)
        server_age = getattr(profile, 'server_age_days', 0)
        fc_level = parse_fc_level(getattr(profile, 'furnace_fc_level', None)) or 0

        milestones = [
            {"level": 9, "name": "Research Center", "benefit": "Unlock research tree"},
            {"level": 18, "name": "Pets Prep", "benefit": "Pets unlock at L18 + 55 days state age"},
            {"level": 19, "name": "Daybreak Island", "benefit": "Major progression system"},
            {"level": 25, "name": "Chief Charms", "benefit": "New stat boost system"},
            {"level": 30, "name": "Fire Crystal Era", "benefit": "FC progression begins"},
        ]

        fc_milestones = [
            {"fc": 1, "name": "FC1 Complete", "benefit": "T9 troops available"},
            {"fc": 3, "name": "FC3 Complete", "benefit": "T10 troops, War Academy expands"},
            {"fc": 5, "name": "FC5 Complete", "benefit": "T11 troops, endgame progression"},
        ]

        # Find next furnace milestone
        for milestone in milestones:
            if furnace_level < milestone["level"]:
                return {
                    "type": "furnace",
                    "target": f"Furnace L{milestone['level']}",
                    "name": milestone["name"],
                    "benefit": milestone["benefit"],
                    "distance": milestone["level"] - furnace_level
                }

        # At L30, check FC milestones
        if furnace_level >= 30:
            for milestone in fc_milestones:
                if fc_level < milestone["fc"]:
                    return {
                        "type": "fc",
                        "target": f"FC{milestone['fc']}",
                        "name": milestone["name"],
                        "benefit": milestone["benefit"],
                        "distance": milestone["fc"] - fc_level
                    }

        return {
            "type": "endgame",
            "target": "Optimization",
            "name": "Endgame Optimization",
            "benefit": "Focus on power efficiency and SvS dominance",
            "distance": 0
        }

    def get_resource_priorities(self, profile) -> List[str]:
        """
        Get prioritized resource list for current phase.

        Args:
            profile: User profile

        Returns:
            List of resource names in priority order
        """
        phase_id = self.detect_phase(profile)
        phase = self.get_phase_info(phase_id)

        # Map bottlenecks to resources
        resource_map = {
            "speedups": ["General Speedups", "Building Speedups", "Research Speedups"],
            "resources": ["Meat", "Wood", "Coal", "Iron"],
            "hero_shards": ["Legendary Shards", "Epic Shards"],
            "charm_materials": ["Charm Designs", "Charm Guides"],
            "fire_crystals": ["Fire Crystals", "Refined Fire Crystals"],
            "fc_speedups": ["FC Speedups", "General Speedups"],
            "essence_stones": ["Essence Stones", "Mithril"],
            "whale_currencies": ["Gems", "Frost Stars"],
            "refined_fc": ["Refined Fire Crystals"],
            "time": ["General Speedups"]
        }

        resources = []
        for bottleneck in phase.get("bottlenecks", []):
            resources.extend(resource_map.get(bottleneck, []))

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for r in resources:
            if r not in seen:
                seen.add(r)
                unique.append(r)

        return unique
