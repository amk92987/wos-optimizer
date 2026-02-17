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


# Chief gear priority order
# CRITICAL: Keep all 6 at same tier for set bonuses. When pushing to next tier, Infantry first.
# Set bonuses: 3-piece = Defense ALL, 6-piece = Attack ALL
CHIEF_GEAR_ORDER = [
    {
        "slot": "coat",
        "troop_type": "Infantry",
        "stat": "Attack/Defense",
        "priority": 1,
        "reason": "Infantry frontline - engage first, need survivability"
    },
    {
        "slot": "pants",
        "troop_type": "Infantry",
        "stat": "Attack/Defense",
        "priority": 2,
        "reason": "Infantry frontline - engage first, need survivability"
    },
    {
        "slot": "belt",
        "troop_type": "Marksman",
        "stat": "Attack/Defense",
        "priority": 3,
        "reason": "Marksman - key damage dealers"
    },
    {
        "slot": "weapon",
        "troop_type": "Marksman",
        "stat": "Attack/Defense",
        "priority": 4,
        "reason": "Marksman - key damage dealers"
    },
    {
        "slot": "cap",
        "troop_type": "Lancer",
        "stat": "Attack/Defense",
        "priority": 5,
        "reason": "Lancer - mid-line support, lowest priority"
    },
    {
        "slot": "watch",
        "troop_type": "Lancer",
        "stat": "Attack/Defense",
        "priority": 6,
        "reason": "Lancer - mid-line support, lowest priority"
    }
]

# Quality tiers (matching database: 1=Gray/Common, 2=Green/Uncommon, 3=Blue/Rare, 4=Purple/Epic, 5=Gold, 6=Legendary, 7=Mythic)
QUALITY_TIERS = ["Common", "Uncommon", "Rare", "Epic", "Gold", "Legendary", "Mythic"]
QUALITY_VALUES = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Gold": 5, "Legendary": 6, "Mythic": 7}

# Reverse mapping for numeric qualities from database
QUALITY_NAMES = {1: "Common", 2: "Uncommon", 3: "Rare", 4: "Epic", 5: "Gold", 6: "Legendary", 7: "Mythic"}


def normalize_quality(quality) -> int:
    """Convert quality to numeric value, handling both strings and ints."""
    if isinstance(quality, int):
        return quality
    if isinstance(quality, str):
        return QUALITY_VALUES.get(quality, 1)
    return 1

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

    def analyze(self, profile, user_gear: dict = None, user_charms: dict = None) -> List[GearRecommendation]:
        """
        Analyze user's gear and generate recommendations.

        Args:
            profile: User profile with spending_profile and priorities
            user_gear: Dict with 'chief_gear' and 'hero_gear' status
            user_charms: Optional dict of charm slot levels

        Returns:
            List of GearRecommendation objects
        """
        recommendations = []
        user_gear = user_gear or {}

        spending_profile = getattr(profile, 'spending_profile', 'f2p')
        priority_pvp = getattr(profile, 'priority_pvp_attack', 5)

        # Chief gear recommendations (applies to everyone)
        recommendations.extend(
            self._analyze_chief_gear(user_gear.get('chief_gear', {}), priority_pvp)
        )

        # Stat balance analysis (gear pairs + charms)
        recommendations.extend(
            self._analyze_stat_balance(user_gear.get('chief_gear', {}), user_charms)
        )

        # Hero gear recommendations (spender-aware)
        recommendations.extend(
            self._analyze_hero_gear(
                user_gear.get('hero_gear', {}),
                spending_profile,
                priority_pvp
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
                action="Keep all 6 Chief Gear pieces at SAME TIER for set bonuses",
                gear_type="chief",
                piece="all",
                reason="6-piece set bonus gives Attack to ALL troops. Don't max one piece while others lag.",
                resources="Hardened Alloy, Polishing Solution, Design Plans",
                relevance_tags=['all', 'svs', 'rally'],
                rule_id="set_bonus_first"
            ))
            recommendations.append(GearRecommendation(
                priority=2,
                action="Upgrade Infantry gear (Coat/Pants) first when pushing to next tier",
                gear_type="chief",
                piece="coat/pants",
                reason="Infantry engage first in battle - frontline survivability is critical.",
                resources="Hardened Alloy, Polishing Solution, Design Plans",
                relevance_tags=['svs', 'rally', 'pvp'],
                rule_id="infantry_first"
            ))
            return recommendations

        # Analyze each piece
        for piece_info in CHIEF_GEAR_ORDER:
            slot = piece_info["slot"]
            current_quality = chief_gear.get(slot.lower(), 1)
            quality_value = normalize_quality(current_quality)
            quality_name = QUALITY_NAMES.get(quality_value, "Common")

            # Check if this piece needs upgrading (Legendary = 6)
            if quality_value < 6:  # Not Legendary yet
                priority = piece_info["priority"]

                # Adjust priority based on current quality gap
                if quality_value < 3:  # Below Rare
                    priority = max(1, priority - 1)  # Bump up priority

                recommendations.append(GearRecommendation(
                    priority=priority,
                    action=f"Upgrade {slot} to Legendary (currently {quality_name})",
                    gear_type="chief",
                    piece=slot,
                    reason=piece_info["reason"],
                    resources="Hardened Alloy, Polishing Solution, Design Plans",
                    relevance_tags=['all'],
                    rule_id=f"upgrade_{slot.lower()}"
                ))

        # Check set bonus status and Mythic push eligibility
        qualities = {slot["slot"]: normalize_quality(chief_gear.get(slot["slot"], 1))
                     for slot in CHIEF_GEAR_ORDER}
        min_quality = min(qualities.values())
        max_quality = max(qualities.values())

        # Warning if pieces are at different tiers (losing set bonus)
        if max_quality - min_quality >= 2:
            lagging_pieces = [slot for slot, q in qualities.items() if q < max_quality]
            recommendations.insert(0, GearRecommendation(
                priority=1,
                action=f"Bring lagging pieces ({', '.join(lagging_pieces)}) up to same tier",
                gear_type="chief",
                piece="multiple",
                reason="Keep all 6 pieces at SAME TIER for set bonuses. 6-piece Attack bonus helps ALL troops.",
                resources="Hardened Alloy, Polishing Solution, Design Plans",
                relevance_tags=['critical', 'efficiency'],
                rule_id="set_bonus_warning"
            ))

        # If all at Legendary, recommend Mythic push (Infantry first)
        if min_quality >= 6:  # All at Legendary or higher
            for piece_info in CHIEF_GEAR_ORDER:  # Infantry first, then Marksman, then Lancer
                slot = piece_info["slot"]
                if qualities[slot] < 7:  # Not Mythic yet
                    recommendations.append(GearRecommendation(
                        priority=2 if piece_info["troop_type"] == "Infantry" else 3,
                        action=f"Push {slot} to Mythic",
                        gear_type="chief",
                        piece=slot,
                        reason=f"All Legendary done. {piece_info['troop_type']} ({slot}) - {piece_info['reason']}",
                        resources="Lunar Amber, Mythic materials",
                        relevance_tags=['endgame'],
                        rule_id=f"mythic_{slot}"
                    ))
                    break  # Only recommend one piece at a time

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

    def _analyze_stat_balance(self, chief_gear: dict, user_charms: dict = None) -> List[GearRecommendation]:
        """
        Identify weakest gear pairs and charm imbalances.

        Marginal returns are highest on the weakest stat — going from +10% to +20%
        gives more combat impact than +60% to +70%.
        """
        recommendations = []
        if not chief_gear:
            return recommendations

        # Map gear pairs to troop types
        troop_gear_pairs = {
            'Infantry': {'slots': ['coat', 'pants'], 'label': 'Coat/Pants'},
            'Marksman': {'slots': ['belt', 'weapon'], 'label': 'Belt/Weapon'},
            'Lancer': {'slots': ['cap', 'watch'], 'label': 'Cap/Watch'},
        }

        # Calculate average quality per troop type
        troop_qualities: Dict[str, float] = {}
        for troop, info in troop_gear_pairs.items():
            avg = sum(normalize_quality(chief_gear.get(s, 1)) for s in info['slots']) / len(info['slots'])
            troop_qualities[troop] = avg

        if not troop_qualities:
            return recommendations

        max_quality = max(troop_qualities.values())
        min_quality = min(troop_qualities.values())

        # Only flag if there's a meaningful gap (at least 1 full tier)
        if max_quality - min_quality >= 1.0:
            weakest_troop = min(troop_qualities, key=troop_qualities.get)  # type: ignore
            strongest_troop = max(troop_qualities, key=troop_qualities.get)  # type: ignore
            weak_info = troop_gear_pairs[weakest_troop]
            strong_info = troop_gear_pairs[strongest_troop]

            weak_name = QUALITY_NAMES.get(int(troop_qualities[weakest_troop]), 'Common')
            strong_name = QUALITY_NAMES.get(int(troop_qualities[strongest_troop]), 'Common')

            recommendations.append(GearRecommendation(
                priority=2,
                action=f"Upgrade {weakest_troop} gear ({weak_info['label']}) — lagging behind",
                gear_type="chief",
                piece=weak_info['label'],
                reason=(
                    f"Your {weakest_troop} stats are lagging ({weak_name} vs {strong_name} {strongest_troop}). "
                    f"{weak_info['label']} upgrades will have higher marginal impact than pushing {strong_info['label']} further."
                ),
                resources="Hardened Alloy, Polishing Solution, Design Plans",
                relevance_tags=['stat_balance', 'efficiency'],
                rule_id="stat_balance_gear"
            ))

        # Analyze charm balance if data is provided
        if user_charms:
            charm_recs = self._analyze_charm_balance(user_charms)
            recommendations.extend(charm_recs)

        return recommendations

    def _analyze_charm_balance(self, user_charms: dict) -> List[GearRecommendation]:
        """Detect lopsided charm levels across troop types."""
        recommendations = []
        if not user_charms:
            return recommendations

        # Charm slots map: gear piece → troop type
        charm_troop_map = {
            'cap': 'Lancer', 'watch': 'Lancer',
            'coat': 'Infantry', 'pants': 'Infantry',
            'belt': 'Marksman', 'weapon': 'Marksman',
        }

        # Collect charm levels per troop type
        troop_charm_totals: Dict[str, List[int]] = {'Infantry': [], 'Lancer': [], 'Marksman': []}

        for piece, troop in charm_troop_map.items():
            for slot_num in range(1, 4):
                key = f"{piece}_slot_{slot_num}"
                val = user_charms.get(key, 0)
                # Parse charm level — could be string like "4-2" (sub-levels) or int
                if isinstance(val, str) and '-' in val:
                    level = int(val.split('-')[0])
                elif val:
                    level = int(val)
                else:
                    level = 0
                troop_charm_totals[troop].append(level)

        # Calculate average charm level per troop type
        troop_charm_avg: Dict[str, float] = {}
        for troop, levels in troop_charm_totals.items():
            if levels:
                troop_charm_avg[troop] = sum(levels) / len(levels)
            else:
                troop_charm_avg[troop] = 0

        if not troop_charm_avg or max(troop_charm_avg.values()) == 0:
            return recommendations

        max_avg = max(troop_charm_avg.values())
        min_avg = min(troop_charm_avg.values())

        # Flag if one troop type's charms are significantly behind (2+ levels)
        if max_avg - min_avg >= 2.0:
            weakest = min(troop_charm_avg, key=troop_charm_avg.get)  # type: ignore
            strongest = max(troop_charm_avg, key=troop_charm_avg.get)  # type: ignore

            recommendations.append(GearRecommendation(
                priority=2,
                action=f"Upgrade {weakest} charms — lagging behind other types",
                gear_type="chief",
                piece=f"{weakest} charms",
                reason=(
                    f"Your {weakest} charms (avg L{min_avg:.0f}) are behind {strongest} charms (avg L{max_avg:.0f}). "
                    f"Upgrade {weakest} charms before pushing {strongest} charms further — "
                    f"balanced charms also unlock the army-wide bonus."
                ),
                resources="Charm materials",
                relevance_tags=['stat_balance', 'charms'],
                rule_id="stat_balance_charms"
            ))

        return recommendations

    def _check_common_mistakes(self, user_gear: dict, spending_profile: str) -> List[GearRecommendation]:
        """Check for common gear investment mistakes."""
        recommendations = []
        chief_gear = user_gear.get('chief_gear', {})
        hero_gear = user_gear.get('hero_gear', {})

        # Get all chief gear qualities
        qualities = {slot["slot"]: normalize_quality(chief_gear.get(slot["slot"], 1))
                     for slot in CHIEF_GEAR_ORDER}
        min_quality = min(qualities.values()) if qualities else 1
        max_quality = max(qualities.values()) if qualities else 1

        geared_heroes = [h for h, g in hero_gear.items() if g.get('has_gear', False)]

        # Mistake: Hero gear before Chief Gear is at Legendary
        if geared_heroes and min_quality < 6:  # 6 = Legendary
            recommendations.append(GearRecommendation(
                priority=1,
                action="Prioritize Chief Gear over Hero Gear",
                gear_type="chief",
                piece="all",
                reason="Chief Gear multiplies ALL damage. Hero Gear only affects one hero. Get 6-piece Legendary set first.",
                resources="Hardened Alloy, Polishing Solution",
                relevance_tags=['warning', 'efficiency'],
                rule_id="chief_before_hero"
            ))

        # Mistake: Pieces at different tiers (losing set bonus)
        if max_quality - min_quality >= 2:
            recommendations.append(GearRecommendation(
                priority=1,
                action="Stop upgrading one piece while others lag behind",
                gear_type="chief",
                piece="multiple",
                reason="You're losing set bonuses! 6-piece Attack bonus requires all pieces at same tier. Bring lagging pieces up first.",
                resources="N/A - redirect to lagging pieces",
                relevance_tags=['warning', 'critical'],
                rule_id="set_bonus_mistake"
            ))

        # Mistake: Upgrading Lancer before Infantry when pushing to next tier
        infantry_min = min(qualities.get('coat', 1), qualities.get('pants', 1))
        lancer_max = max(qualities.get('cap', 1), qualities.get('watch', 1))

        if lancer_max > infantry_min and min_quality >= 4:  # Only relevant at higher tiers
            recommendations.append(GearRecommendation(
                priority=2,
                action="Prioritize Infantry gear (Coat/Pants) over Lancer (Cap/Watch)",
                gear_type="chief",
                piece="coat/pants",
                reason="Infantry engage first in battle - frontline survivability is critical. Upgrade Infantry before Lancer.",
                resources="N/A - redirect to Infantry gear",
                relevance_tags=['warning'],
                rule_id="infantry_before_lancer"
            ))

        return recommendations

    def get_gear_priority_order(self, spending_profile: str = "f2p") -> List[dict]:
        """Return the recommended gear upgrade order."""
        order = []

        # Set bonus priority note
        order.append({
            "type": "chief",
            "piece": "ALL 6 pieces",
            "reason": "Keep all at SAME TIER for 6-piece Attack set bonus (benefits ALL troops)",
            "priority": "Critical"
        })

        # Chief gear in troop priority order (Infantry > Marksman > Lancer)
        for piece in CHIEF_GEAR_ORDER[:2]:  # Infantry: Coat, Pants
            order.append({
                "type": "chief",
                "piece": piece["slot"],
                "reason": piece["reason"],
                "priority": "High (Infantry first when pushing next tier)"
            })

        for piece in CHIEF_GEAR_ORDER[2:4]:  # Marksman: Belt, Weapon
            order.append({
                "type": "chief",
                "piece": piece["slot"],
                "reason": piece["reason"],
                "priority": "Medium (Marksman second)"
            })

        for piece in CHIEF_GEAR_ORDER[4:]:  # Lancer: Cap, Watch
            order.append({
                "type": "chief",
                "piece": piece["slot"],
                "reason": piece["reason"],
                "priority": "Lower (Lancer last)"
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
