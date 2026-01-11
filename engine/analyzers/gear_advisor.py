"""
Gear Advisor - Recommends chief gear and hero gear upgrades.
Uses spender-level-aware rules to avoid wasting resources.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class GearRecommendation:
    """A single gear-related recommendation."""
    priority: int  # 1-5, 1 being highest
    action: str
    gear_type: str  # 'chief' or 'hero'
    piece: str  # Specific piece name
    reason: str
    resources: str
    relevance_tags: List[str]
    rule_id: str


# Chief gear priority order (universal truth)
CHIEF_GEAR_ORDER = [
    {
        "slot": "Ring",
        "stat": "Troop Attack (All)",
        "priority": 1,
        "reason": "Universal attack buff for ALL troops"
    },
    {
        "slot": "Amulet",
        "stat": "Lethality/Damage",
        "priority": 2,
        "reason": "PvP decisive - affects kill rates in SvS"
    },
    {
        "slot": "Gloves",
        "stat": "Marksman Attack",
        "priority": 3,
        "reason": "Boosts marksman heroes (Alonso, Molly)"
    },
    {
        "slot": "Boots",
        "stat": "Lancer Attack",
        "priority": 4,
        "reason": "Boosts lancer heroes"
    },
    {
        "slot": "Helmet",
        "stat": "Infantry Defense",
        "priority": 5,
        "reason": "Defensive - less impactful than attack stats"
    },
    {
        "slot": "Armor",
        "stat": "Infantry Health",
        "priority": 6,
        "reason": "Defensive - least priority"
    }
]

# Quality tiers
QUALITY_TIERS = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
QUALITY_VALUES = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Legendary": 5, "Mythic": 6}

# Hero gear limits by spender type
HERO_GEAR_LIMITS = {
    "f2p": {
        "allowed_count": 1,
        "targets": ["Molly", "Alonso"],
        "roles": ["field_dps"],
        "avoid": ["Jessie", "Sergey", "any joiner hero"]
    },
    "low_spender": {
        "allowed_count": 2,
        "targets": ["Alonso", "Jeronimo", "Molly"],
        "roles": ["field_dps", "rally_leader"],
        "avoid": ["Jessie", "Sergey", "any joiner hero"]
    },
    "medium_spender": {
        "allowed_count": 4,
        "targets": ["Jeronimo", "Alonso", "Molly", "situational"],
        "roles": ["rally_leader", "primary_dps", "secondary_dps", "situational"],
        "avoid": ["pure joiners"]
    },
    "whale": {
        "allowed_count": 999,
        "targets": ["all core heroes"],
        "roles": ["all"],
        "avoid": []
    }
}


class GearAdvisor:
    """Generate gear upgrade recommendations based on spender level."""

    def __init__(self, gear_data: dict = None):
        """
        Initialize with gear data.

        Args:
            gear_data: Chief gear data from chief_gear.json (optional)
        """
        self.gear_data = gear_data or {}

    def analyze(self, profile, user_gear: dict = None) -> List[GearRecommendation]:
        """
        Analyze user's gear and generate recommendations.

        Args:
            profile: User profile with spending_profile and priorities
            user_gear: Dict with 'chief_gear' and 'hero_gear' status

        Returns:
            List of GearRecommendation objects
        """
        recommendations = []
        user_gear = user_gear or {}

        spending_profile = getattr(profile, 'spending_profile', 'f2p')
        priority_svs = getattr(profile, 'priority_svs', 5)
        priority_rally = getattr(profile, 'priority_rally', 4)

        # Chief gear recommendations (applies to everyone)
        recommendations.extend(
            self._analyze_chief_gear(user_gear.get('chief_gear', {}), priority_svs)
        )

        # Hero gear recommendations (spender-aware)
        recommendations.extend(
            self._analyze_hero_gear(
                user_gear.get('hero_gear', {}),
                spending_profile,
                priority_rally
            )
        )

        # Anti-pattern warnings
        recommendations.extend(
            self._check_common_mistakes(user_gear, spending_profile)
        )

        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)

        return recommendations

    def _analyze_chief_gear(self, chief_gear: dict, svs_priority: int) -> List[GearRecommendation]:
        """Analyze chief gear and recommend upgrades."""
        recommendations = []

        # If no chief gear data, give general advice
        if not chief_gear:
            recommendations.append(GearRecommendation(
                priority=1,
                action="Focus on upgrading Ring to Legendary",
                gear_type="chief",
                piece="Ring",
                reason="Ring affects ALL troop attack. Top priority for everyone.",
                resources="Hardened Alloy, Polishing Solution, Design Plans",
                relevance_tags=['all', 'svs', 'rally'],
                rule_id="ring_first"
            ))
            recommendations.append(GearRecommendation(
                priority=2,
                action="Upgrade Amulet to Legendary",
                gear_type="chief",
                piece="Amulet",
                reason="Amulet provides Lethality - crucial for PvP kill rates.",
                resources="Hardened Alloy, Polishing Solution, Design Plans",
                relevance_tags=['svs', 'rally', 'pvp'],
                rule_id="amulet_second"
            ))
            return recommendations

        # Analyze each piece
        for piece_info in CHIEF_GEAR_ORDER:
            slot = piece_info["slot"]
            current_quality = chief_gear.get(slot.lower(), "Common")
            quality_value = QUALITY_VALUES.get(current_quality, 1)

            # Check if this piece needs upgrading
            if quality_value < 5:  # Not Legendary yet
                priority = piece_info["priority"]

                # Adjust priority based on current quality gap
                if quality_value < 3:  # Below Rare
                    priority = max(1, priority - 1)  # Bump up priority

                recommendations.append(GearRecommendation(
                    priority=priority,
                    action=f"Upgrade {slot} to Legendary (currently {current_quality})",
                    gear_type="chief",
                    piece=slot,
                    reason=piece_info["reason"],
                    resources="Hardened Alloy, Polishing Solution, Design Plans",
                    relevance_tags=['all'],
                    rule_id=f"upgrade_{slot.lower()}"
                ))

        # Check for Mythic push on Ring/Amulet
        ring_quality = QUALITY_VALUES.get(chief_gear.get('ring', 'Common'), 1)
        amulet_quality = QUALITY_VALUES.get(chief_gear.get('amulet', 'Common'), 1)

        if ring_quality >= 5 and amulet_quality >= 5:  # Both at Legendary
            if ring_quality < 6:
                recommendations.append(GearRecommendation(
                    priority=2,
                    action="Push Ring to Mythic",
                    gear_type="chief",
                    piece="Ring",
                    reason="Legendary Ring done. Mythic Ring is long-term goal for max attack.",
                    resources="Lunar Amber, Mythic materials",
                    relevance_tags=['endgame'],
                    rule_id="mythic_ring"
                ))
            if amulet_quality < 6:
                recommendations.append(GearRecommendation(
                    priority=3,
                    action="Push Amulet to Mythic",
                    gear_type="chief",
                    piece="Amulet",
                    reason="Legendary Amulet done. Mythic Amulet is next priority.",
                    resources="Lunar Amber, Mythic materials",
                    relevance_tags=['endgame'],
                    rule_id="mythic_amulet"
                ))

        return recommendations

    def _analyze_hero_gear(self, hero_gear: dict, spending_profile: str, rally_priority: int) -> List[GearRecommendation]:
        """Analyze hero gear based on spender profile."""
        recommendations = []
        limits = HERO_GEAR_LIMITS.get(spending_profile, HERO_GEAR_LIMITS["f2p"])

        # Count current hero gear investments
        geared_heroes = [h for h, g in hero_gear.items() if g.get('has_gear', False)]
        geared_count = len(geared_heroes)

        # F2P specific warning
        if spending_profile == "f2p":
            if geared_count > 1:
                recommendations.append(GearRecommendation(
                    priority=1,
                    action="Stop spreading hero gear investment",
                    gear_type="hero",
                    piece="general",
                    reason=f"F2P should only gear 1 hero (you have {geared_count}). Chief Gear Ring/Amulet should be priority.",
                    resources="N/A - this is a warning",
                    relevance_tags=['f2p', 'efficiency'],
                    rule_id="f2p_hero_gear_limit"
                ))
            elif geared_count == 0:
                recommendations.append(GearRecommendation(
                    priority=3,
                    action="Consider hero gear for Molly OR Alonso (not both)",
                    gear_type="hero",
                    piece="Molly or Alonso",
                    reason="F2P can invest in one field DPS hero. Only after Ring/Amulet are at Legendary.",
                    resources="Hero Gear XP, Essence Stones",
                    relevance_tags=['f2p', 'field_pvp'],
                    rule_id="f2p_first_hero_gear"
                ))

        # Check for joiner hero gear (always bad)
        joiner_heroes = {"Jessie", "Sergey"}
        geared_joiners = joiner_heroes.intersection(set(geared_heroes))

        if geared_joiners and spending_profile != "whale":
            for joiner in geared_joiners:
                recommendations.append(GearRecommendation(
                    priority=1,
                    action=f"Don't invest more hero gear in {joiner}",
                    gear_type="hero",
                    piece=joiner,
                    reason=f"{joiner} is a joiner hero. Only their expedition skill matters in rallies - hero gear is wasted.",
                    resources="N/A - redirect to Chief Gear",
                    relevance_tags=['warning', 'efficiency'],
                    rule_id="no_joiner_gear"
                ))

        # Low/Medium spender targets
        if spending_profile in ["low_spender", "medium_spender"]:
            targets = limits["targets"]
            for target in targets:
                if target in hero_gear and not hero_gear[target].get('has_gear', False):
                    if geared_count < limits["allowed_count"]:
                        recommendations.append(GearRecommendation(
                            priority=3,
                            action=f"Start hero gear on {target}",
                            gear_type="hero",
                            piece=target,
                            reason=f"{target} is a good hero gear target for {spending_profile}s. Used across multiple modes.",
                            resources="Hero Gear XP, Essence Stones, Mithril",
                            relevance_tags=['hero_gear'],
                            rule_id=f"hero_gear_{target.lower()}"
                        ))

        return recommendations

    def _check_common_mistakes(self, user_gear: dict, spending_profile: str) -> List[GearRecommendation]:
        """Check for common gear investment mistakes."""
        recommendations = []
        chief_gear = user_gear.get('chief_gear', {})
        hero_gear = user_gear.get('hero_gear', {})

        # Mistake: Hero gear before Ring/Amulet
        ring_quality = QUALITY_VALUES.get(chief_gear.get('ring', 'Common'), 1)
        amulet_quality = QUALITY_VALUES.get(chief_gear.get('amulet', 'Common'), 1)

        geared_heroes = [h for h, g in hero_gear.items() if g.get('has_gear', False)]

        if geared_heroes and (ring_quality < 5 or amulet_quality < 5):
            recommendations.append(GearRecommendation(
                priority=1,
                action="Prioritize Chief Gear Ring/Amulet over Hero Gear",
                gear_type="chief",
                piece="Ring/Amulet",
                reason="Chief Gear multiplies ALL damage. Hero Gear only affects one hero. Ring/Amulet to Legendary first.",
                resources="Hardened Alloy, Polishing Solution",
                relevance_tags=['warning', 'efficiency'],
                rule_id="chief_before_hero"
            ))

        # Mistake: Upgrading Helmet/Armor before Ring/Amulet
        helmet_quality = QUALITY_VALUES.get(chief_gear.get('helmet', 'Common'), 1)
        armor_quality = QUALITY_VALUES.get(chief_gear.get('armor', 'Common'), 1)

        if (helmet_quality > ring_quality or armor_quality > amulet_quality):
            recommendations.append(GearRecommendation(
                priority=2,
                action="Stop upgrading Infantry defensive gear",
                gear_type="chief",
                piece="Helmet/Armor",
                reason="Defensive gear is low priority. Ring/Amulet attack stats win more battles than infantry defense.",
                resources="N/A - redirect materials to Ring/Amulet",
                relevance_tags=['warning'],
                rule_id="attack_before_defense"
            ))

        return recommendations

    def get_gear_priority_order(self, spending_profile: str = "f2p") -> List[dict]:
        """Return the recommended gear upgrade order."""
        order = []

        # Chief gear always first
        for piece in CHIEF_GEAR_ORDER[:2]:  # Ring, Amulet
            order.append({
                "type": "chief",
                "piece": piece["slot"],
                "reason": piece["reason"],
                "priority": "Critical"
            })

        # Remaining chief gear
        for piece in CHIEF_GEAR_ORDER[2:]:
            order.append({
                "type": "chief",
                "piece": piece["slot"],
                "reason": piece["reason"],
                "priority": "Important"
            })

        # Hero gear based on spender
        limits = HERO_GEAR_LIMITS.get(spending_profile, HERO_GEAR_LIMITS["f2p"])
        for i, target in enumerate(limits["targets"][:limits["allowed_count"]]):
            order.append({
                "type": "hero",
                "piece": target,
                "reason": f"Hero gear target #{i + 1} for {spending_profile}",
                "priority": "After Chief Gear"
            })

        return order
