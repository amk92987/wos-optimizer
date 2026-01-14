"""
Lineup Builder - Recommends optimal lineups based on owned heroes.
Considers game mode, hero levels, skills, gear, and user priorities.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class LineupRecommendation:
    """A complete lineup recommendation."""
    game_mode: str
    heroes: List[Dict[str, Any]]  # List of {hero, slot, role, your_status, hero_class}
    troop_ratio: Dict[str, int]  # e.g., {"infantry": 50, "lancer": 20, "marksman": 30}
    notes: str
    confidence: str  # "high", "medium", "low" based on hero availability
    recommended_to_get: List[Dict[str, Any]] = field(default_factory=list)  # Heroes user should get


# Hero tier values for ranking (S+ = 6, S = 5, ... D = 1)
TIER_VALUES = {"S+": 6, "S": 5, "A": 4, "B": 3, "C": 2, "D": 1}


def calculate_hero_power(hero_stats: dict, hero_data: dict = None) -> int:
    """
    Calculate a hero's effective power based on level, stars, gear, and tier.

    Args:
        hero_stats: User's hero stats {level, stars, gear_slot1_quality, etc.}
        hero_data: Static hero data from heroes.json (for tier info)

    Returns:
        Power score (higher = better)
    """
    score = 0

    # Level contributes most (0-80 range)
    level = hero_stats.get('level', 1)
    score += level * 10  # 0-800 points

    # Stars (0-5)
    stars = hero_stats.get('stars', 0)
    score += stars * 50  # 0-250 points

    # Ascension tier (0-5)
    ascension = hero_stats.get('ascension_tier', 0)
    score += ascension * 30  # 0-150 points

    # Gear quality (4 slots, quality 0-6)
    for slot in range(1, 5):
        quality = hero_stats.get(f'gear_slot{slot}_quality', 0)
        gear_level = hero_stats.get(f'gear_slot{slot}_level', 0)
        score += quality * 15 + gear_level // 10  # 0-100 per slot

    # Expedition skills (for PvP modes)
    exp_skill = hero_stats.get('expedition_skill_1_level', 1)
    score += exp_skill * 20  # 0-100 points

    # Base tier bonus from hero data
    if hero_data:
        tier = hero_data.get('tier_expedition', 'C')
        score += TIER_VALUES.get(tier, 2) * 25  # 25-150 points

    return score


# Hero metadata: class and generation
HERO_METADATA = {
    # Gen 1
    "Jeronimo": {"class": "Infantry", "gen": 1, "tier": "S", "role": "ATK buffer"},
    "Natalia": {"class": "Infantry", "gen": 2, "tier": "S+", "role": "Tank/Sustain"},
    "Flint": {"class": "Infantry", "gen": 2, "tier": "A", "role": "Control/Tank"},
    "Sergey": {"class": "Infantry", "gen": 1, "tier": "B", "role": "Garrison joiner"},
    "Jessie": {"class": "Marksman", "gen": 1, "tier": "B", "role": "Attack joiner"},
    "Bahiti": {"class": "Lancer", "gen": 1, "tier": "B", "role": "Healer/Support"},
    "Patrick": {"class": "Lancer", "gen": 1, "tier": "C", "role": "Early lancer"},
    "Logan": {"class": "Marksman", "gen": 1, "tier": "C", "role": "Backup marksman"},
    # Gen 2
    "Molly": {"class": "Lancer", "gen": 2, "tier": "S", "role": "Healer/DPS"},
    "Alonso": {"class": "Marksman", "gen": 2, "tier": "S+", "role": "Main DPS"},
    "Philly": {"class": "Marksman", "gen": 2, "tier": "A", "role": "Burst DPS"},
    # Gen 3
    "Zinman": {"class": "Lancer", "gen": 3, "tier": "S", "role": "Tank/Control"},
    "Gina": {"class": "Marksman", "gen": 3, "tier": "A", "role": "Healer"},
    # Gen 4
    "Mia": {"class": "Marksman", "gen": 4, "tier": "A", "role": "Support DPS"},
    "Lynn": {"class": "Lancer", "gen": 4, "tier": "A", "role": "DPS Lancer"},
    # Gen 5
    "Greg": {"class": "Infantry", "gen": 5, "tier": "S", "role": "Tank"},
    "Reina": {"class": "Lancer", "gen": 5, "tier": "A", "role": "Support"},
    # Gen 6+
    "Ahmose": {"class": "Infantry", "gen": 6, "tier": "S", "role": "Tank/Control"},
    "Norah": {"class": "Marksman", "gen": 6, "tier": "S", "role": "DPS"},
    "Wayne": {"class": "Lancer", "gen": 7, "tier": "S", "role": "Support"},
    "Jasser": {"class": "Marksman", "gen": 7, "tier": "S", "role": "Rally joiner"},
    "Seo-yoon": {"class": "Marksman", "gen": 8, "tier": "S+", "role": "Rally DPS"},
}

# Standard 3-hero lineup templates by event type
# Each template has required_class for each slot to ensure proper composition
LINEUP_TEMPLATES = {
    "world_march": {
        "name": "World March",
        "slots": [
            {"class": "Infantry", "role": "Lead/Tank", "preferred": ["Jeronimo", "Natalia", "Flint", "Greg", "Ahmose"], "is_lead": True},
            {"class": "Lancer", "role": "Support/Heal", "preferred": ["Molly", "Zinman", "Bahiti", "Lynn", "Wayne"]},
            {"class": "Marksman", "role": "Main DPS", "preferred": ["Alonso", "Philly", "Norah", "Seo-yoon", "Gina"]},
        ],
        "troop_ratio": {"infantry": 50, "lancer": 20, "marksman": 30},
        "notes": "Standard balanced march. Jeronimo for burst, Natalia for sustain.",
        "key_heroes": ["Jeronimo", "Natalia", "Molly", "Alonso"],
    },
    "bear_trap": {
        "name": "Bear Trap Rally",
        "slots": [
            {"class": "Infantry", "role": "ATK Buffer", "preferred": ["Jeronimo", "Natalia", "Greg"], "is_lead": True},
            {"class": "Lancer", "role": "Healer", "preferred": ["Molly", "Zinman", "Bahiti"]},
            {"class": "Marksman", "role": "Main DPS", "preferred": ["Alonso", "Philly", "Seo-yoon", "Norah"]},
        ],
        "troop_ratio": {"infantry": 20, "lancer": 20, "marksman": 60},
        "notes": "Heavy Marksman for max damage. Bear is slow, DPS matters most.",
        "key_heroes": ["Jeronimo", "Molly", "Alonso"],
    },
    "crazy_joe": {
        "name": "Crazy Joe Rally",
        "slots": [
            {"class": "Infantry", "role": "ATK Lead", "preferred": ["Jeronimo", "Natalia", "Greg"], "is_lead": True},
            {"class": "Lancer", "role": "Healer", "preferred": ["Molly", "Bahiti", "Zinman"]},
            {"class": "Marksman", "role": "Support", "preferred": ["Alonso", "Philly", "Logan"]},
        ],
        "troop_ratio": {"infantry": 90, "lancer": 10, "marksman": 0},
        "notes": "Infantry kills before back row attacks. 90/10/0 ratio is key.",
        "key_heroes": ["Jeronimo", "Molly"],
    },
    "svs_attack": {
        "name": "SvS Castle Attack",
        "slots": [
            {"class": "Infantry", "role": "ATK Lead", "preferred": ["Jeronimo", "Natalia", "Greg", "Ahmose"], "is_lead": True},
            {"class": "Lancer", "role": "Support", "preferred": ["Molly", "Zinman", "Wayne"]},
            {"class": "Marksman", "role": "DPS", "preferred": ["Alonso", "Seo-yoon", "Norah", "Philly"]},
        ],
        "troop_ratio": {"infantry": 50, "lancer": 20, "marksman": 30},
        "notes": "Rally leader setup. See Natalia vs Jeronimo tab for when to swap.",
        "key_heroes": ["Jeronimo", "Natalia", "Molly", "Alonso"],
    },
    "garrison": {
        "name": "Castle Garrison",
        "slots": [
            {"class": "Infantry", "role": "Tank Lead", "preferred": ["Natalia", "Greg", "Ahmose", "Flint"], "is_lead": True},
            {"class": "Lancer", "role": "Healer", "preferred": ["Molly", "Zinman", "Bahiti"]},
            {"class": "Marksman", "role": "Counter DPS", "preferred": ["Alonso", "Philly", "Norah"]},
        ],
        "troop_ratio": {"infantry": 60, "lancer": 15, "marksman": 25},
        "notes": "Defense = survival. Natalia's sustain is key.",
        "key_heroes": ["Natalia", "Molly", "Alonso"],
    },
    "rally_joiner_attack": {
        "name": "Rally Joiner (Attack)",
        "slots": [
            {"class": "Marksman", "role": "JOINER (Only this matters!)", "preferred": ["Jessie", "Jasser", "Seo-yoon"], "is_lead": True, "is_joiner": True},
            {"class": "Infantry", "role": "Filler", "preferred": ["any"]},
            {"class": "Lancer", "role": "Filler", "preferred": ["any"]},
        ],
        "troop_ratio": {"infantry": 30, "lancer": 20, "marksman": 50},
        "notes": "ONLY first hero's expedition skill matters! Jessie gives +25% DMG.",
        "key_heroes": ["Jessie"],
        "joiner_warning": "If you don't have Jessie, send troops WITHOUT heroes!",
    },
    "rally_joiner_defense": {
        "name": "Rally Joiner (Garrison)",
        "slots": [
            {"class": "Infantry", "role": "JOINER (Only this matters!)", "preferred": ["Sergey"], "is_lead": True, "is_joiner": True},
            {"class": "Lancer", "role": "Filler", "preferred": ["any"]},
            {"class": "Marksman", "role": "Filler", "preferred": ["any"]},
        ],
        "troop_ratio": {"infantry": 60, "lancer": 20, "marksman": 20},
        "notes": "ONLY first hero's expedition skill matters! Sergey gives -20% DMG taken.",
        "key_heroes": ["Sergey"],
        "joiner_warning": "If you don't have Sergey, send troops WITHOUT heroes!",
    },
    "arena": {
        "name": "Arena (5 Heroes)",
        "slots": [
            {"class": "Infantry", "role": "Primary Tank", "preferred": ["Natalia", "Greg", "Ahmose"], "is_lead": True},
            {"class": "Infantry", "role": "Secondary Tank", "preferred": ["Flint", "Natalia", "Sergey"]},
            {"class": "Marksman", "role": "Main DPS", "preferred": ["Alonso", "Seo-yoon", "Norah"]},
            {"class": "Lancer", "role": "Healer", "preferred": ["Molly", "Zinman", "Wayne"]},
            {"class": "Marksman", "role": "Secondary DPS", "preferred": ["Philly", "Gina", "Mia"]},
        ],
        "troop_ratio": {"infantry": 45, "lancer": 25, "marksman": 30},
        "notes": "5-hero mode. Double infantry frontline is meta.",
        "key_heroes": ["Natalia", "Flint", "Alonso", "Molly"],
    },
    "exploration": {
        "name": "Exploration / PvE",
        "slots": [
            {"class": "Infantry", "role": "Tank", "preferred": ["Natalia", "Zinman", "Sergey", "Greg"], "is_lead": True},
            {"class": "Lancer", "role": "Healer", "preferred": ["Molly", "Bahiti", "Gina"]},
            {"class": "Marksman", "role": "DPS", "preferred": ["Alonso", "Philly", "Logan"]},
        ],
        "troop_ratio": {"infantry": 40, "lancer": 30, "marksman": 30},
        "notes": "Uses EXPLORATION skills (left side). Survival > speed.",
        "key_heroes": ["Natalia", "Molly", "Alonso"],
    },
}

# Legacy IDEAL_LINEUPS for backward compatibility
IDEAL_LINEUPS = {
    "rally_leader_infantry": LINEUP_TEMPLATES["svs_attack"],
    "rally_leader_marksman": LINEUP_TEMPLATES["bear_trap"],
    "rally_joiner_attack": LINEUP_TEMPLATES["rally_joiner_attack"],
    "rally_joiner_defense": LINEUP_TEMPLATES["rally_joiner_defense"],
    "bear_trap": LINEUP_TEMPLATES["bear_trap"],
    "crazy_joe": LINEUP_TEMPLATES["crazy_joe"],
    "garrison": LINEUP_TEMPLATES["garrison"],
    "exploration": LINEUP_TEMPLATES["exploration"],
    "svs_march": LINEUP_TEMPLATES["world_march"],
}


class LineupBuilder:
    """Build optimal lineups from user's available heroes."""

    def __init__(self, heroes_data: dict = None):
        """
        Initialize with static hero data.

        Args:
            heroes_data: Hero data from heroes.json (optional, uses HERO_METADATA if not provided)
        """
        self.heroes_data = heroes_data or {}
        self.hero_lookup = {h['name']: h for h in self.heroes_data.get('heroes', [])}

    def build_personalized_lineup(
        self,
        event_type: str,
        user_heroes: dict,
        max_generation: int = 99
    ) -> LineupRecommendation:
        """
        Build lineup using ONLY the user's owned heroes, ranked by power.

        Args:
            event_type: Key from LINEUP_TEMPLATES
            user_heroes: Dict of {hero_name: {level, stars, gear...}}
            max_generation: Only consider heroes up to this generation

        Returns:
            LineupRecommendation with user's best available heroes
        """
        template = LINEUP_TEMPLATES.get(event_type)
        if not template:
            return LineupRecommendation(
                game_mode=event_type,
                heroes=[],
                troop_ratio={"infantry": 33, "lancer": 33, "marksman": 34},
                notes=f"Unknown event type: {event_type}",
                confidence="low",
                recommended_to_get=[]
            )

        lineup_heroes = []
        used_heroes = set()
        missing_key_heroes = []
        slots_filled = 0

        for slot in template["slots"]:
            slot_class = slot["class"]
            role = slot["role"]
            is_lead = slot.get("is_lead", False)
            preferred = slot.get("preferred", [])

            # Skip filler slots
            if preferred == ["any"]:
                lineup_heroes.append({
                    "hero": "Any hero",
                    "hero_class": slot_class,
                    "slot": role,
                    "role": "Filler",
                    "is_lead": False,
                    "power": 0,
                    "status": "Filler slot"
                })
                continue

            # Find best available hero for this slot from user's collection
            best_hero = None
            best_power = -1

            # First try preferred heroes in order
            for hero_name in preferred:
                if hero_name in user_heroes and hero_name not in used_heroes:
                    hero_meta = HERO_METADATA.get(hero_name, {})
                    if hero_meta.get("gen", 99) <= max_generation:
                        hero_stats = user_heroes[hero_name]
                        hero_data = self.hero_lookup.get(hero_name)
                        power = calculate_hero_power(hero_stats, hero_data)
                        if power > best_power:
                            best_power = power
                            best_hero = hero_name

            # If no preferred hero found, find any hero of the right class
            if not best_hero:
                for hero_name, hero_stats in user_heroes.items():
                    if hero_name in used_heroes:
                        continue
                    hero_meta = HERO_METADATA.get(hero_name, {})
                    if hero_meta.get("class") == slot_class and hero_meta.get("gen", 99) <= max_generation:
                        hero_data = self.hero_lookup.get(hero_name)
                        power = calculate_hero_power(hero_stats, hero_data)
                        if power > best_power:
                            best_power = power
                            best_hero = hero_name

            if best_hero:
                used_heroes.add(best_hero)
                hero_stats = user_heroes[best_hero]
                level = hero_stats.get('level', 1)
                hero_meta = HERO_METADATA.get(best_hero, {})
                lineup_heroes.append({
                    "hero": best_hero,
                    "hero_class": hero_meta.get("class", slot_class),
                    "slot": role,
                    "role": hero_meta.get("role", role),
                    "is_lead": is_lead,
                    "power": best_power,
                    "status": f"Lv{level}"
                })
                slots_filled += 1
            else:
                # No hero available for this slot
                lineup_heroes.append({
                    "hero": f"Need {slot_class}",
                    "hero_class": slot_class,
                    "slot": role,
                    "role": role,
                    "is_lead": is_lead,
                    "power": 0,
                    "status": "Not owned"
                })
                # Track missing key heroes
                for hero in preferred[:2]:  # First 2 preferred are most important
                    if hero not in user_heroes:
                        hero_meta = HERO_METADATA.get(hero, {})
                        if hero_meta.get("gen", 99) <= max_generation:
                            missing_key_heroes.append({
                                "hero": hero,
                                "class": hero_meta.get("class", slot_class),
                                "reason": f"Best {role} for {template['name']}",
                                "gen": hero_meta.get("gen", 1)
                            })

        # Build recommended_to_get from key_heroes user doesn't own
        recommended_to_get = []
        for key_hero in template.get("key_heroes", []):
            if key_hero not in user_heroes:
                hero_meta = HERO_METADATA.get(key_hero, {})
                if hero_meta.get("gen", 99) <= max_generation:
                    recommended_to_get.append({
                        "hero": key_hero,
                        "class": hero_meta.get("class", "Unknown"),
                        "reason": f"Key hero for {template['name']}",
                        "gen": hero_meta.get("gen", 1)
                    })

        # Add missing slot heroes
        for missing in missing_key_heroes:
            if not any(r["hero"] == missing["hero"] for r in recommended_to_get):
                recommended_to_get.append(missing)

        # Calculate confidence
        total_critical_slots = len([s for s in template["slots"] if s.get("preferred", ["any"]) != ["any"]])
        if slots_filled == total_critical_slots:
            confidence = "high"
        elif slots_filled >= total_critical_slots * 0.5:
            confidence = "medium"
        else:
            confidence = "low"

        notes = template.get("notes", "")
        if template.get("joiner_warning") and confidence != "high":
            notes += f"\n⚠️ {template['joiner_warning']}"

        return LineupRecommendation(
            game_mode=template["name"],
            heroes=lineup_heroes,
            troop_ratio=template["troop_ratio"],
            notes=notes,
            confidence=confidence,
            recommended_to_get=recommended_to_get[:4]  # Limit to 4 suggestions
        )

    def build_general_lineup(self, event_type: str, max_generation: int = 8) -> LineupRecommendation:
        """
        Build lineup showing ideal heroes up to a generation (for General Guide mode).

        Args:
            event_type: Key from LINEUP_TEMPLATES
            max_generation: Only show heroes available at this generation

        Returns:
            LineupRecommendation with best available heroes for that gen
        """
        template = LINEUP_TEMPLATES.get(event_type)
        if not template:
            return LineupRecommendation(
                game_mode=event_type,
                heroes=[],
                troop_ratio={"infantry": 33, "lancer": 33, "marksman": 34},
                notes=f"Unknown event type: {event_type}",
                confidence="high",
                recommended_to_get=[]
            )

        lineup_heroes = []
        used_heroes = set()

        for slot in template["slots"]:
            slot_class = slot["class"]
            role = slot["role"]
            is_lead = slot.get("is_lead", False)
            preferred = slot.get("preferred", [])

            if preferred == ["any"]:
                lineup_heroes.append({
                    "hero": "Any hero",
                    "hero_class": slot_class,
                    "slot": role,
                    "role": "Filler",
                    "is_lead": False,
                    "status": "Filler slot"
                })
                continue

            # Find first preferred hero available at this generation
            selected_hero = None
            for hero_name in preferred:
                if hero_name in used_heroes:
                    continue
                hero_meta = HERO_METADATA.get(hero_name, {})
                if hero_meta.get("gen", 99) <= max_generation:
                    selected_hero = hero_name
                    break

            if selected_hero:
                used_heroes.add(selected_hero)
                hero_meta = HERO_METADATA.get(selected_hero, {})
                lineup_heroes.append({
                    "hero": selected_hero,
                    "hero_class": hero_meta.get("class", slot_class),
                    "slot": role,
                    "role": hero_meta.get("role", role),
                    "is_lead": is_lead,
                    "status": f"Gen {hero_meta.get('gen', '?')}"
                })
            else:
                lineup_heroes.append({
                    "hero": f"No {slot_class} available",
                    "hero_class": slot_class,
                    "slot": role,
                    "role": role,
                    "is_lead": is_lead,
                    "status": f"Unlocks later"
                })

        return LineupRecommendation(
            game_mode=template["name"],
            heroes=lineup_heroes,
            troop_ratio=template["troop_ratio"],
            notes=template.get("notes", ""),
            confidence="high",
            recommended_to_get=[]
        )

    def build_lineup(self, game_mode: str, user_heroes: dict, profile=None) -> LineupRecommendation:
        """
        Build the best lineup for a game mode using available heroes.

        Args:
            game_mode: One of the IDEAL_LINEUPS keys
            user_heroes: Dict of {hero_name: {level, stars, skills...}}
            profile: Optional user profile for priority adjustments

        Returns:
            LineupRecommendation with best available heroes
        """
        ideal = IDEAL_LINEUPS.get(game_mode)
        if not ideal:
            return LineupRecommendation(
                game_mode=game_mode,
                heroes=[{"hero": "Unknown mode", "slot": "N/A", "role": "N/A", "your_status": "N/A"}],
                troop_ratio={"infantry": 33, "lancer": 33, "marksman": 34},
                notes=f"Unknown game mode: {game_mode}",
                confidence="low"
            )

        lineup_heroes = []
        confidence_score = 0
        # Only count slots that have specific hero requirements (not "any") for confidence
        critical_slots = [s for s in ideal["slots"] if s["heroes"] != ["any"]]
        max_confidence = len(critical_slots) if critical_slots else 1

        for slot_info in ideal["slots"]:
            position = slot_info["position"]
            preferred_heroes = slot_info["heroes"]
            role = slot_info["role"]

            # Find best available hero from preferred list
            best_hero, status = self._get_best_available(preferred_heroes, user_heroes)

            if best_hero and best_hero != "any":
                # Only count toward confidence if this is a critical slot
                if preferred_heroes != ["any"]:
                    confidence_score += 1
                hero_stats = user_heroes.get(best_hero, {})
                level = hero_stats.get('level', 1)
                lineup_heroes.append({
                    "hero": best_hero,
                    "slot": position,
                    "role": role,
                    "your_status": f"Lv{level}" if level > 1 else status
                })
            else:
                lineup_heroes.append({
                    "hero": preferred_heroes[0] if preferred_heroes[0] != "any" else "Any hero",
                    "slot": position,
                    "role": role,
                    "your_status": "Not owned" if preferred_heroes[0] != "any" else "Filler slot"
                })

        # Calculate confidence based on critical slots filled
        if confidence_score == max_confidence:
            confidence = "high"
        elif confidence_score >= max_confidence * 0.5:
            confidence = "medium"
        else:
            confidence = "low"

        return LineupRecommendation(
            game_mode=ideal["mode"],
            heroes=lineup_heroes,
            troop_ratio=ideal["troop_ratio"],
            notes=ideal["notes"],
            confidence=confidence
        )

    def _get_best_available(self, preferred_heroes: List[str], user_heroes: dict) -> Tuple[Optional[str], str]:
        """
        Get the best available hero from a preference list.

        Args:
            preferred_heroes: List of hero names in preference order
            user_heroes: Dict of user's owned heroes

        Returns:
            (hero_name, status) tuple
        """
        if preferred_heroes == ["any"]:
            return "any", "Filler"

        for hero in preferred_heroes:
            if hero in user_heroes:
                stats = user_heroes[hero]
                level = stats.get('level', 1)
                return hero, f"Owned Lv{level}"

        # None of preferred heroes owned
        return None, "Not owned"

    def get_all_lineups(self, user_heroes: dict, profile=None) -> Dict[str, LineupRecommendation]:
        """
        Get lineups for all game modes.

        Args:
            user_heroes: Dict of user's owned heroes
            profile: Optional user profile

        Returns:
            Dict of {mode: LineupRecommendation}
        """
        result = {}
        for mode in IDEAL_LINEUPS.keys():
            result[mode] = self.build_lineup(mode, user_heroes, profile)
        return result

    def get_joiner_recommendation(self, user_heroes: dict, attack: bool = True) -> Dict[str, Any]:
        """
        Get specific recommendation for joining rallies.

        Args:
            user_heroes: Dict of user's owned heroes
            attack: True for attack rallies, False for defense

        Returns:
            Dict with recommendation details
        """
        if attack:
            best_joiners = ["Jessie", "Jeronimo"]
            skill_name = "Stand of Arms"
            effect = "+25% DMG dealt"
        else:
            best_joiners = ["Sergey", "Natalia"]
            skill_name = "Defenders' Edge"
            effect = "-20% DMG taken"

        for joiner in best_joiners:
            if joiner in user_heroes:
                stats = user_heroes[joiner]
                # Joiner skill is expedition_skill_1 (top-right position)
                exp_skill = stats.get('expedition_skill_1', stats.get('expedition_skill', 1))
                return {
                    "hero": joiner,
                    "status": "owned",
                    "skill_level": exp_skill,
                    "max_skill": 5,
                    "recommendation": f"Use {joiner} in slot 1. Skill at L{exp_skill}/5.",
                    "action": f"Max {joiner}'s expedition skill" if exp_skill < 5 else "Ready to join!",
                    "critical_note": f"ONLY slot 1 hero's top-right skill ({skill_name}: {effect}) applies when joining!"
                }

        # No good joiner owned
        return {
            "hero": None,
            "status": "not_owned",
            "recommendation": f"No good {'attack' if attack else 'defense'} joiner owned.",
            "action": f"REMOVE ALL HEROES when joining {'attack' if attack else 'defense'} rallies. Send troops only!",
            "critical_note": "Sending no heroes is BETTER than contributing a bad skill that bumps out a good one."
        }

    def get_lineup_for_question(self, question: str, user_heroes: dict) -> Optional[LineupRecommendation]:
        """
        Determine appropriate lineup based on a natural language question.

        Args:
            question: User's question about lineups
            user_heroes: Dict of user's owned heroes

        Returns:
            LineupRecommendation if question matches a mode, None otherwise
        """
        question_lower = question.lower()

        # Map question patterns to modes
        mode_patterns = {
            "bear trap": "bear_trap",
            "crazy joe": "crazy_joe",
            "garrison": "garrison",
            "defense": "garrison",
            "reinforce": "rally_joiner_defense",
            "join.*attack": "rally_joiner_attack",
            "join.*rally": "rally_joiner_attack",
            "rally leader": "rally_leader_infantry",
            "lead.*rally": "rally_leader_infantry",
            "marksman": "rally_leader_marksman",
            "exploration": "exploration",
            "pve": "exploration",
            "frozen": "exploration",
            "svs": "svs_march",
            "field": "svs_march"
        }

        import re
        for pattern, mode in mode_patterns.items():
            if re.search(pattern, question_lower):
                return self.build_lineup(mode, user_heroes)

        return None
