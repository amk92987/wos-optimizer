"""
Lineup Builder - Recommends optimal lineups based on owned heroes.
Considers game mode, hero levels, skills, and user priorities.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LineupRecommendation:
    """A complete lineup recommendation."""
    game_mode: str
    heroes: List[Dict[str, Any]]  # List of {hero, slot, role, your_status}
    troop_ratio: Dict[str, int]  # e.g., {"infantry": 50, "lancer": 20, "marksman": 30}
    notes: str
    confidence: str  # "high", "medium", "low" based on hero availability


# Ideal lineups by game mode
IDEAL_LINEUPS = {
    "rally_leader_infantry": {
        "mode": "Rally Leader (Infantry Focus)",
        "slots": [
            {"position": "Lead", "heroes": ["Jeronimo", "Natalia", "Flint"], "role": "Tank/Buffer"},
            {"position": "Slot 2", "heroes": ["Natalia", "Flint", "Bahiti"], "role": "Support"},
            {"position": "Slot 3", "heroes": ["Flint", "Bahiti", "Sergey"], "role": "Infantry DPS"}
        ],
        "troop_ratio": {"infantry": 60, "lancer": 20, "marksman": 20},
        "notes": "Infantry-heavy for balanced push. Lead hero buffs determine rally effectiveness."
    },
    "rally_leader_marksman": {
        "mode": "Rally Leader (Marksman Focus)",
        "slots": [
            {"position": "Lead", "heroes": ["Alonso", "Philly", "Logan"], "role": "Marksman DPS"},
            {"position": "Slot 2", "heroes": ["Molly", "Philly", "Mia"], "role": "AOE/DPS"},
            {"position": "Slot 3", "heroes": ["Logan", "Mia", "Cloris"], "role": "Support"}
        ],
        "troop_ratio": {"infantry": 20, "lancer": 20, "marksman": 60},
        "notes": "Marksman-heavy for max DPS. Good for Bear Trap and Crazy Joe."
    },
    "rally_joiner_attack": {
        "mode": "Rally Joiner (Attack)",
        "slots": [
            {"position": "Slot 1 (Critical)", "heroes": ["Jessie", "Jeronimo"], "role": "Attack Joiner - ONLY this hero's top-right skill matters!"},
            {"position": "Slot 2", "heroes": ["any"], "role": "Filler (doesn't matter for joining)"},
            {"position": "Slot 3", "heroes": ["any"], "role": "Filler (doesn't matter for joining)"}
        ],
        "troop_ratio": {"infantry": 30, "lancer": 20, "marksman": 50},
        "notes": "ONLY slot 1 hero matters! If no good attack joiner, remove all heroes and send troops only."
    },
    "rally_joiner_defense": {
        "mode": "Rally Joiner (Garrison/Defense)",
        "slots": [
            {"position": "Slot 1 (Critical)", "heroes": ["Sergey", "Natalia"], "role": "Defense Joiner - ONLY this hero's top-right skill matters!"},
            {"position": "Slot 2", "heroes": ["any"], "role": "Filler"},
            {"position": "Slot 3", "heroes": ["any"], "role": "Filler"}
        ],
        "troop_ratio": {"infantry": 50, "lancer": 30, "marksman": 20},
        "notes": "ONLY slot 1 hero matters! Sergey's Defenders' Edge provides -20% damage taken."
    },
    "bear_trap": {
        "mode": "Bear Trap Rally",
        "slots": [
            {"position": "Lead", "heroes": ["Jeronimo", "Alonso", "Philly"], "role": "DPS Lead"},
            {"position": "Slot 2", "heroes": ["Molly", "Alonso", "Logan"], "role": "AOE DPS"},
            {"position": "Slot 3", "heroes": ["Philly", "Logan", "Mia"], "role": "DPS Support"}
        ],
        "troop_ratio": {"infantry": 0, "lancer": 10, "marksman": 90},
        "notes": "Bear is slow. Maximize marksman DPS. Infantry not needed."
    },
    "crazy_joe": {
        "mode": "Crazy Joe Rally",
        "slots": [
            {"position": "Lead", "heroes": ["Jeronimo", "Natalia", "Flint"], "role": "Infantry Lead"},
            {"position": "Slot 2", "heroes": ["Natalia", "Flint", "Bahiti"], "role": "Tank/Support"},
            {"position": "Slot 3", "heroes": ["Flint", "Bahiti", "Sergey"], "role": "Infantry DPS"}
        ],
        "troop_ratio": {"infantry": 90, "lancer": 10, "marksman": 0},
        "notes": "Infantry kills before Joe's backline attacks. Minimize marksmen."
    },
    "garrison": {
        "mode": "Castle Garrison",
        "slots": [
            {"position": "Lead", "heroes": ["Sergey", "Natalia", "Jeronimo"], "role": "Defensive Lead"},
            {"position": "Slot 2", "heroes": ["Natalia", "Bahiti", "Flint"], "role": "Tank/Healer"},
            {"position": "Slot 3", "heroes": ["Bahiti", "Flint", "Zinman"], "role": "Support"}
        ],
        "troop_ratio": {"infantry": 60, "lancer": 25, "marksman": 15},
        "notes": "Defense-focused. Infantry absorb damage. Sergey's skill provides damage reduction."
    },
    "exploration": {
        "mode": "Exploration/PvE",
        "slots": [
            {"position": "Tank", "heroes": ["Zinman", "Natalia", "Sergey"], "role": "Tank"},
            {"position": "Healer", "heroes": ["Natalia", "Gina", "Bahiti"], "role": "Healer/Support"},
            {"position": "DPS", "heroes": ["Molly", "Alonso", "Jeronimo"], "role": "Damage Dealer"}
        ],
        "troop_ratio": {"infantry": 40, "lancer": 30, "marksman": 30},
        "notes": "Uses EXPLORATION skills (left side). Tank + Healer + DPS composition."
    },
    "svs_march": {
        "mode": "SvS Field March",
        "slots": [
            {"position": "Lead", "heroes": ["Jeronimo", "Alonso", "Molly"], "role": "Primary DPS"},
            {"position": "Slot 2", "heroes": ["Alonso", "Molly", "Philly"], "role": "Secondary DPS"},
            {"position": "Slot 3", "heroes": ["Natalia", "Philly", "Logan"], "role": "Support/DPS"}
        ],
        "troop_ratio": {"infantry": 40, "lancer": 20, "marksman": 40},
        "notes": "Balanced for field combat. Match hero class to your strongest troop type."
    }
}


class LineupBuilder:
    """Build optimal lineups from user's available heroes."""

    def __init__(self, heroes_data: dict):
        """
        Initialize with static hero data.

        Args:
            heroes_data: Hero data from heroes.json
        """
        self.heroes_data = heroes_data
        self.hero_lookup = {h['name']: h for h in heroes_data.get('heroes', [])}

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
