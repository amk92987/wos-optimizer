"""
Lineup Builder - Recommends optimal lineups based on owned heroes.
Considers game mode, hero levels, skills, gear, and user priorities.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


# Cache for hero metadata loaded from heroes.json
_HERO_METADATA_CACHE = None


def load_hero_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Load hero metadata from heroes.json.

    This is the single source of truth for hero data.
    Returns dict mapping hero_name -> {class, gen, tier, role}
    """
    global _HERO_METADATA_CACHE

    if _HERO_METADATA_CACHE is not None:
        return _HERO_METADATA_CACHE

    # Find heroes.json relative to this file
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    heroes_file = project_root / "data" / "heroes.json"

    metadata = {}

    try:
        with open(heroes_file, encoding='utf-8') as f:
            data = json.load(f)

        for hero in data.get('heroes', []):
            name = hero.get('name', '')
            if name:
                metadata[name] = {
                    'class': hero.get('hero_class', 'Unknown'),
                    'gen': hero.get('generation', 1),
                    'tier': hero.get('tier_overall', 'C'),
                    'tier_expedition': hero.get('tier_expedition', 'C'),
                    'role': hero.get('best_use', 'Unknown')[:30] if hero.get('best_use') else 'Unknown',
                    'rarity': hero.get('rarity', 'Rare'),
                }
    except FileNotFoundError:
        # Fallback to empty dict - will use defaults
        pass

    _HERO_METADATA_CACHE = metadata
    return metadata


def get_hero_metadata(hero_name: str) -> Dict[str, Any]:
    """Get metadata for a specific hero."""
    metadata = load_hero_metadata()
    return metadata.get(hero_name, {
        'class': 'Unknown',
        'gen': 99,
        'tier': 'C',
        'tier_expedition': 'C',
        'role': 'Unknown',
        'rarity': 'Rare',
    })


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


# HERO_METADATA is now loaded dynamically from heroes.json via load_hero_metadata()
# This ensures we always use the source of truth for hero data

# Standard 3-hero lineup templates by event type
# Each template has required_class for each slot to ensure proper composition
LINEUP_TEMPLATES = {
    "world_march": {
        "name": "World March",
        "slots": [
            # Infantry: S+ first (Elif, Hervor, Magnus, Wu Ming, Jeronimo), then S (Gatot, Edith), then A
            {"class": "Infantry", "role": "Lead/Tank", "preferred": ["Jeronimo", "Wu Ming", "Elif", "Hervor", "Magnus", "Gatot", "Edith", "Natalia", "Flint"], "is_lead": True},
            # Lancer: S first (Dominic, Flora, Karol, Freya, Sonya, Gordon, Renee, Norah), then A
            {"class": "Lancer", "role": "Support/Heal", "preferred": ["Dominic", "Flora", "Karol", "Freya", "Sonya", "Gordon", "Renee", "Norah", "Lloyd", "Fred", "Molly"]},
            # Marksman: S+ first (Vulcanus, Blanchette), then S, then A
            {"class": "Marksman", "role": "Main DPS", "preferred": ["Vulcanus", "Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
        ],
        "troop_ratio": {"infantry": 50, "lancer": 20, "marksman": 30},
        "notes": "Standard balanced march. Jeronimo for burst, Wu Ming/Natalia for sustain.",
        "key_heroes": ["Jeronimo", "Wu Ming", "Natalia", "Molly", "Alonso"],
        "hero_explanations": {
            # Infantry
            "Jeronimo": "S+ Gen 1 Infantry. +50% offense buffs. Best lead for quick kills.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% ALL damage taken. Better for extended fights.",
            "Elif": "S+ Gen 14 Infantry. Shield + enemy ATK reduction. Latest top-tier tank.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + damage combo. Strong balanced option.",
            "Magnus": "S+ Gen 9 Infantry. Shield + damage reduction. Reliable tank.",
            "Gatot": "S Gen 8 Infantry. 3/3 sustain skills. Pure defensive option.",
            "Edith": "S Gen 7 Infantry. 3/3 sustain skills. Extremely tanky.",
            "Natalia": "A-tier Infantry. Feral Protection sustain. Good for longer fights.",
            "Flint": "A-tier Infantry. Control abilities + tank. Solid backup.",
            # Lancer
            "Dominic": "S Gen 14 Lancer. +100% Lancer damage + sustain mix.",
            "Flora": "S Gen 13 Lancer. Heals troops 5-25% HP every 4 turns. True healer.",
            "Karol": "S Gen 12 Lancer. Reduces ALL troops damage taken by 4-20%.",
            "Freya": "S Gen 10 Lancer. Reduces Infantry/Marksman damage taken.",
            "Sonya": "S Gen 8 Lancer. Offense-focused with damage buffs.",
            "Gordon": "S Gen 7 Lancer. Venom + enemy damage debuff.",
            "Renee": "S Gen 6 Lancer. Infantry ATK boost. Supports your tank.",
            "Norah": "S Gen 5 Lancer. -15% damage taken AND +15% damage dealt. Balanced.",
            "Philly": "A Gen 2 Lancer. Best early healer. ATK/DEF buffs.",
            "Molly": "B-tier Lancer. Damage reduction chance. Budget healer option.",
            # Marksman
            "Vulcanus": "S+ Gen 13 Marksman. Sustain + defense + high DPS. Top-tier.",
            "Blanchette": "S+ Gen 10 Marksman. Pure offense powerhouse.",
            "Cara": "S Gen 14 Marksman. Sustain + offense mix.",
            "Ligeia": "S Gen 12 Marksman. Sustain + offense balanced.",
            "Rufus": "S Gen 11 Marksman. High damage output.",
            "Xura": "S Gen 9 Marksman. Sustain + high DPS.",
            "Hendrik": "S Gen 8 Marksman. Defense buffs + single-target DPS.",
            "Bradley": "S Gen 6 Marksman. Solid ranged damage.",
            "Gwen": "A Gen 4 Marksman. Good mid-game DPS option.",
            "Wayne": "A Gen 6 Marksman. Sustained DPS.",
            "Alonso": "A Gen 2 Marksman. Early-game best DPS. Reliable."
        },
        "ratio_explanation": "Balanced 50/20/30 ratio works for general field combat. Infantry tanks damage, Marksman deals DPS, Lancer provides healing and utility."
    },
    "bear_trap": {
        "name": "Bear Trap Rally",
        "slots": [
            # Marksman: S+ first (Vulcanus, Blanchette), then S (Cara, Ligeia, Rufus, Xura, Hendrik, etc.)
            {"class": "Marksman", "role": "Main DPS Lead", "preferred": ["Vulcanus", "Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"], "is_lead": True},
            {"class": "Marksman", "role": "Secondary DPS", "preferred": ["Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
            # Infantry: S+ for ATK buffs (Jeronimo, Wu Ming, Elif, Hervor, Magnus)
            {"class": "Infantry", "role": "Frontline Buffer", "preferred": ["Jeronimo", "Wu Ming", "Elif", "Hervor", "Magnus", "Natalia", "Flint"]},
        ],
        "troop_ratio": {"infantry": 0, "lancer": 10, "marksman": 90},
        "notes": "Bear moves SLOWLY - maximize ranged damage window. 90% Marksman troops deal massive DPS before melee begins.",
        "key_heroes": ["Hendrik", "Alonso", "Jeronimo"],
        "hero_explanations": {
            # Marksman (primary - 2 slots)
            "Vulcanus": "S+ Gen 13 Marksman. Top DPS with sustain. Best lead if available.",
            "Blanchette": "S+ Gen 10 Marksman. Pure offense powerhouse. Excellent lead.",
            "Cara": "S Gen 14 Marksman. Sustain + offense. Great for longer fights.",
            "Ligeia": "S Gen 12 Marksman. Balanced sustain + damage.",
            "Rufus": "S Gen 11 Marksman. High burst damage output.",
            "Xura": "S Gen 9 Marksman. Sustain + excellent DPS.",
            "Hendrik": "S Gen 8 Marksman. Best single-target DPS. Defense buffs bonus.",
            "Bradley": "S Gen 6 Marksman. Solid ranged damage dealer.",
            "Gwen": "A Gen 4 Marksman. Good mid-game option.",
            "Wayne": "A Gen 6 Marksman. Strong sustained DPS.",
            "Alonso": "A Gen 2 Marksman. Early-game best. Reliable damage.",
            "Bahiti": "B Gen 1 Marksman. Budget backup option.",
            "Zinman": "C Gen 1 Marksman. Starter option if no others available.",
            # Infantry (buffer slot - 1 slot)
            "Jeronimo": "S+ Gen 1 Infantry. +50% ATK/DMG buffs apply to ALL troops including Marksman.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% damage taken. Good if bear reaches melee.",
            "Elif": "S+ Gen 14 Infantry. Shield + ATK reduction. Latest gen tank.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + offense. Balanced.",
            "Magnus": "S+ Gen 9 Infantry. Shield + damage reduction.",
            "Natalia": "A-tier Infantry. Feral Protection for sustained survival.",
            "Flint": "A-tier Infantry. Control + tank. Solid backup."
        },
        "ratio_explanation": "Bear Trap's slow movement creates an extended ranged damage window. 90% Marksman troops exploit this by dealing maximum DPS before the bear reaches melee range. 10% Lancer provides minimal frontline."
    },
    "crazy_joe": {
        "name": "Crazy Joe Rally",
        "slots": [
            # Infantry only - S+ first, then S, then A
            {"class": "Infantry", "role": "ATK Lead", "preferred": ["Jeronimo", "Wu Ming", "Elif", "Hervor", "Magnus", "Gatot", "Edith", "Natalia", "Gregory"], "is_lead": True},
            {"class": "Infantry", "role": "Tank Support", "preferred": ["Wu Ming", "Elif", "Hervor", "Magnus", "Gatot", "Edith", "Natalia", "Gregory", "Sergey"]},
            {"class": "Infantry", "role": "Infantry DPS", "preferred": ["Elif", "Hervor", "Magnus", "Gatot", "Edith", "Natalia", "Gregory", "Hector"]},
        ],
        "troop_ratio": {"infantry": 90, "lancer": 10, "marksman": 0},
        "notes": "Infantry kills before back row attacks. 90/10/0 ratio is key. Joe targets backline first - 0% Marksman is MANDATORY.",
        "key_heroes": ["Jeronimo", "Wu Ming"],
        "hero_explanations": {
            # All Infantry (3 slots - Joe requires infantry-only lineup)
            "Jeronimo": "S+ Gen 1 Infantry. +50% ATK/DMG buffs. Best for burst - kill Joe before he kills you.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% ALL damage taken. Better for sustained fights against tougher Joes.",
            "Elif": "S+ Gen 14 Infantry. Shield + enemy ATK reduction. Top-tier tank for Joe.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + offense. Strong balanced pick.",
            "Magnus": "S+ Gen 9 Infantry. Shield + damage reduction. Reliable defensive option.",
            "Gatot": "S Gen 8 Infantry. 3/3 sustain skills. Pure defense for survival-focused strategy.",
            "Edith": "S Gen 7 Infantry. 3/3 sustain skills. Extremely tanky backup.",
            "Natalia": "A-tier Infantry. Feral Protection (-50% damage). Great sustain backup.",
            "Gregory": "A-tier Infantry. Tank with control abilities.",
            "Sergey": "A-tier Infantry. Defensive skills. Solid backup option.",
            "Hector": "A-tier Infantry. DPS-focused. Good damage backup.",
            "Flint": "A-tier Infantry. Control + tank. Reliable option.",
            "Ahmose": "A-tier Infantry. Balanced tank. Early backup option."
        },
        "ratio_explanation": "Crazy Joe's AI targets BACKLINE FIRST. With 0% Marksman troops, Joe finds no backline and is forced into unfavorable frontline combat against your 90% Infantry."
    },
    "svs_attack": {
        "name": "SvS Castle Attack",
        "slots": [
            # Infantry: S+ first for offense (Jeronimo, Wu Ming, Elif, Hervor, Magnus)
            {"class": "Infantry", "role": "ATK Lead", "preferred": ["Jeronimo", "Wu Ming", "Elif", "Hervor", "Magnus", "Gatot", "Edith", "Natalia", "Flint"], "is_lead": True},
            # Lancer: S first, then A (Molly is B-tier, should be last)
            {"class": "Lancer", "role": "Support", "preferred": ["Dominic", "Flora", "Karol", "Freya", "Sonya", "Gordon", "Renee", "Norah", "Lloyd", "Fred", "Molly"]},
            # Marksman: S+ first (Vulcanus, Blanchette), then S, then A
            {"class": "Marksman", "role": "DPS", "preferred": ["Vulcanus", "Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
        ],
        "troop_ratio": {"infantry": 50, "lancer": 20, "marksman": 30},
        "notes": "Rally leader setup. See Natalia vs Jeronimo tab for when to swap.",
        "key_heroes": ["Jeronimo", "Natalia", "Molly", "Alonso"],
        "hero_explanations": {
            # Infantry (attack lead)
            "Jeronimo": "S+ Gen 1 Infantry. +50% ATK/DMG. Best for quick kills against weak garrisons.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% damage taken. Better against strong garrisons.",
            "Elif": "S+ Gen 14 Infantry. Shield + ATK reduction. Latest top-tier option.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + offense. Strong balanced pick.",
            "Magnus": "S+ Gen 9 Infantry. Shield + damage reduction. Reliable tank.",
            "Gatot": "S Gen 8 Infantry. 3/3 sustain. For prolonged siege survival.",
            "Edith": "S Gen 7 Infantry. 3/3 sustain. Extremely tanky for long fights.",
            "Natalia": "A-tier Infantry. Feral Protection sustain. Good against tough garrisons.",
            "Flint": "A-tier Infantry. Control + tank. Solid backup.",
            # Lancer (support/heal)
            "Dominic": "S Gen 14 Lancer. +100% Lancer damage + sustain.",
            "Flora": "S Gen 13 Lancer. Heals 5-25% HP every 4 turns. Best healer.",
            "Karol": "S Gen 12 Lancer. -4-20% damage taken for ALL troops.",
            "Freya": "S Gen 10 Lancer. Reduces Infantry/Marksman damage taken.",
            "Sonya": "S Gen 8 Lancer. Offense-focused buffs.",
            "Gordon": "S Gen 7 Lancer. Venom + enemy debuff.",
            "Renee": "S Gen 6 Lancer. Infantry ATK boost.",
            "Norah": "S Gen 5 Lancer. -15% damage AND +15% dealt. Balanced.",
            "Philly": "A Gen 2 Lancer. Best early healer. ATK/DEF buffs.",
            "Molly": "B-tier Lancer. Damage reduction chance. Budget healer.",
            # Marksman (DPS)
            "Vulcanus": "S+ Gen 13 Marksman. Sustain + defense + high DPS.",
            "Blanchette": "S+ Gen 10 Marksman. Pure offense. Maximum kill speed.",
            "Cara": "S Gen 14 Marksman. Sustain + offense mix.",
            "Ligeia": "S Gen 12 Marksman. Balanced sustain + damage.",
            "Rufus": "S Gen 11 Marksman. High burst damage.",
            "Xura": "S Gen 9 Marksman. Sustain + excellent DPS.",
            "Hendrik": "S Gen 8 Marksman. Defense + single-target DPS.",
            "Bradley": "S Gen 6 Marksman. Solid ranged damage.",
            "Gwen": "A Gen 4 Marksman. Good mid-game DPS.",
            "Wayne": "A Gen 6 Marksman. Sustained DPS.",
            "Alonso": "A Gen 2 Marksman. Early-game best. Reliable."
        },
        "ratio_explanation": "SvS castle attacks use balanced 50/20/30 to handle varied garrison compositions. Infantry leads and absorbs damage, Marksman provides kill power."
    },
    "garrison": {
        "name": "Castle Garrison",
        "slots": [
            # Infantry: S+ first by power, sustain tip shown separately
            {"class": "Infantry", "role": "Tank Lead", "preferred": ["Elif", "Hervor", "Magnus", "Wu Ming", "Jeronimo", "Gatot", "Edith", "Natalia", "Flint", "Ahmose"], "is_lead": True},
            # Lancer: S first by power
            {"class": "Lancer", "role": "Healer", "preferred": ["Dominic", "Flora", "Karol", "Freya", "Sonya", "Gordon", "Renee", "Norah", "Lloyd", "Fred", "Molly"]},
            # Marksman: S+ first by power
            {"class": "Marksman", "role": "Counter DPS", "preferred": ["Vulcanus", "Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
        ],
        "troop_ratio": {"infantry": 60, "lancer": 15, "marksman": 25},
        "notes": "Defense = survival.",
        "key_heroes": ["Natalia", "Gatot", "Edith", "Wu Ming"],
        "sustain_heroes": {
            "Natalia": "Feral Protection reduces damage taken by up to 50%. Great for sustained defense.",
            "Gatot": "3/3 sustain skills: Defense+, Shield, enemy ATK reduction. Built for pure defense.",
            "Edith": "3/3 sustain skills: DMG reduction, Health+. Extremely tanky.",
            "Wu Ming": "Shadow's Evasion reduces ALL damage taken by 25%. Top sustain among S+ tier."
        },
        "hero_explanations": {
            # Infantry
            "Elif": "S+ Gen 14 Infantry. Shield + enemy ATK reduction for sustained defense.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + damage combo. Strong tank.",
            "Magnus": "S+ Gen 9 Infantry. Shield + damage reduction. Solid defensive option.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% ALL damage taken. Best sustain among S+ tier.",
            "Jeronimo": "S+ Gen 1 Infantry. Pure offense (+25% DMG/ATK). Less ideal for defense.",
            "Gatot": "S Gen 8 Infantry. 3/3 sustain skills (Defense+, Shield, ATK-). Built for defense.",
            "Edith": "S Gen 7 Infantry. 3/3 sustain skills (DMG reduction, Health+). Extremely tanky.",
            "Natalia": "A-tier Infantry. Feral Protection reduces damage by up to 50%. Garrison queen.",
            "Flint": "A-tier Infantry tank. Solid backup with control abilities.",
            # Lancer
            "Dominic": "S Gen 14 Lancer. +100% Lancer damage + some sustain.",
            "Flora": "S Gen 13 Lancer. Heals troops 5-25% HP every 4 turns. True healer.",
            "Karol": "S Gen 12 Lancer. Reduces ALL troops damage taken by 4-20%.",
            "Freya": "S Gen 10 Lancer. Reduces Infantry/Marksman damage taken.",
            "Sonya": "S Gen 8 Lancer. Offense-focused with damage buffs.",
            "Gordon": "S Gen 7 Lancer. Venom damage + enemy damage increase debuff.",
            "Norah": "S Gen 5 Lancer. Balanced -15% damage taken AND +15% damage dealt.",
            "Philly": "A Gen 2 Lancer. Best early healer - ATK/DEF buffs + damage reduction.",
            "Molly": "B-tier Lancer. Damage reduction chance + damage buffs.",
            # Marksman
            "Vulcanus": "S+ Gen 13 Marksman. Sustain + defense + high damage output.",
            "Blanchette": "S+ Gen 10 Marksman. Pure offense powerhouse.",
            "Cara": "S Gen 14 Marksman. Sustain + offense mix.",
            "Ligeia": "S Gen 12 Marksman. Sustain + offense for counterattacks.",
            "Xura": "S Gen 9 Marksman. Sustain + high DPS.",
            "Hendrik": "S Gen 8 Marksman. Defense buffs + strong single-target DPS.",
            "Alonso": "A-tier Marksman. Reliable DPS for counterattacks."
        },
        "ratio_explanation": "Garrison defense prioritizes survival with 60% Infantry. Lower Marksman (25%) because they die fast under rallies - Infantry survives longer."
    },
    "rally_joiner_attack": {
        "name": "Rally Joiner (Attack)",
        "slots": [
            {"class": "Marksman", "role": "JOINER (Only this matters!)", "preferred": ["Jessie"], "is_lead": True, "is_joiner": True},
            {"class": "Infantry", "role": "Filler", "preferred": ["any"]},
            {"class": "Lancer", "role": "Filler", "preferred": ["any"]},
        ],
        "troop_ratio": {"infantry": 30, "lancer": 20, "marksman": 50},
        "notes": "ONLY slot 1 hero's TOP-RIGHT expedition skill matters! Jessie's Stand of Arms gives +25% DMG to ALL your troops.",
        "key_heroes": ["Jessie"],
        "joiner_warning": "If you don't have Jessie, send troops WITHOUT heroes - other heroes' skills won't help!",
        "hero_explanations": {
            "Jessie": "CRITICAL: Stand of Arms expedition skill gives +25% damage dealt to ALL your troops in the rally. Her stats/level/gear are IRRELEVANT - only skill level matters."
        },
        "ratio_explanation": "When joining rallies, your troop composition supports the rally leader. 50% Marksman for damage, 30% Infantry for survival, 20% Lancer for balance."
    },
    "rally_joiner_defense": {
        "name": "Garrison Joiner (Defense)",
        "slots": [
            {"class": "Infantry", "role": "JOINER (Only this matters!)", "preferred": ["Sergey", "Patrick"], "is_lead": True, "is_joiner": True},
            {"class": "Infantry", "role": "Filler", "preferred": ["any"]},
            {"class": "Lancer", "role": "Filler", "preferred": ["any"]},
        ],
        "troop_ratio": {"infantry": 50, "lancer": 30, "marksman": 20},
        "notes": "ONLY slot 1 hero's TOP-RIGHT expedition skill matters! Sergey's Defenders' Edge gives -20% DMG taken for ENTIRE garrison. Patrick is an alternative with +25% HP boost.",
        "key_heroes": ["Sergey", "Patrick"],
        "hero_explanations": {
            "Sergey": "CRITICAL: Defenders' Edge expedition skill reduces damage taken by 20% for the ENTIRE garrison. His stats/level/gear are IRRELEVANT - only skill level matters. Mathematically better against multiple attack waves.",
            "Patrick": "ALTERNATIVE: Health boost expedition skill gives +25% HP to garrison troops. Some rally leaders prefer raw HP over damage reduction. Better for surviving a single massive hit."
        },
        "ratio_explanation": "Garrison defense prioritizes survival. 50% Infantry absorbs damage, 30% Lancer provides balanced support, 20% Marksman adds counterattack without overexposure.",
        "joiner_warning": "If you don't have Sergey or Patrick, send troops WITHOUT heroes!",
    },
    "arena": {
        "name": "Arena (5 Heroes)",
        "slots": [
            # Infantry: S+ and S first for raw power
            {"class": "Infantry", "role": "Primary Tank", "preferred": ["Elif", "Hervor", "Magnus", "Wu Ming", "Jeronimo", "Gatot", "Edith", "Natalia"], "is_lead": True},
            {"class": "Infantry", "role": "Secondary Tank", "preferred": ["Hervor", "Magnus", "Wu Ming", "Gatot", "Edith", "Natalia", "Flint", "Sergey"]},
            # Marksman: S+ first
            {"class": "Marksman", "role": "Main DPS", "preferred": ["Vulcanus", "Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
            # Lancer: S first
            {"class": "Lancer", "role": "Healer", "preferred": ["Dominic", "Flora", "Karol", "Freya", "Sonya", "Gordon", "Renee", "Norah", "Lloyd", "Fred", "Molly"]},
            {"class": "Marksman", "role": "Secondary DPS", "preferred": ["Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
        ],
        "troop_ratio": {"infantry": 45, "lancer": 25, "marksman": 30},
        "notes": "5-hero mode. Double infantry frontline is meta.",
        "key_heroes": ["Natalia", "Flint", "Alonso", "Molly"],
        "hero_explanations": {
            # Infantry (2 slots - double frontline)
            "Elif": "S+ Gen 14 Infantry. Shield + ATK reduction. Top primary tank.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + offense. Strong pick.",
            "Magnus": "S+ Gen 9 Infantry. Shield + damage reduction. Reliable.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% damage taken. Great sustain.",
            "Jeronimo": "S+ Gen 1 Infantry. +50% offense. Good for burst kills.",
            "Gatot": "S Gen 8 Infantry. 3/3 sustain. Pure defense tank.",
            "Edith": "S Gen 7 Infantry. 3/3 sustain. Extremely tanky.",
            "Natalia": "A-tier Infantry. Feral Protection sustain. Pairs well with S+ for double frontline.",
            "Flint": "A-tier Infantry. Control abilities. Good secondary tank.",
            "Sergey": "A-tier Infantry. Defensive skills. Solid backup tank.",
            # Marksman (2 slots - double DPS)
            "Vulcanus": "S+ Gen 13 Marksman. Sustain + defense + high DPS. Best primary DPS.",
            "Blanchette": "S+ Gen 10 Marksman. Pure offense. Excellent damage.",
            "Cara": "S Gen 14 Marksman. Sustain + offense. Strong pick.",
            "Ligeia": "S Gen 12 Marksman. Balanced damage dealer.",
            "Rufus": "S Gen 11 Marksman. High burst damage.",
            "Xura": "S Gen 9 Marksman. Sustain + DPS.",
            "Hendrik": "S Gen 8 Marksman. Defense + single-target damage.",
            "Bradley": "S Gen 6 Marksman. Solid ranged damage.",
            "Gwen": "A Gen 4 Marksman. Good mid-game option.",
            "Wayne": "A Gen 6 Marksman. Sustained DPS.",
            "Alonso": "A Gen 2 Marksman. Early-game best. Reliable.",
            # Lancer (1 slot - healer)
            "Dominic": "S Gen 14 Lancer. +100% Lancer damage + sustain.",
            "Flora": "S Gen 13 Lancer. Heals 5-25% HP. Best healer for arena.",
            "Karol": "S Gen 12 Lancer. -4-20% damage taken for ALL.",
            "Freya": "S Gen 10 Lancer. Reduces damage taken.",
            "Sonya": "S Gen 8 Lancer. Offense-focused.",
            "Gordon": "S Gen 7 Lancer. Venom + debuff.",
            "Renee": "S Gen 6 Lancer. Infantry ATK boost.",
            "Norah": "S Gen 5 Lancer. Balanced -15%/+15%. Good healer alternative.",
            "Philly": "A Gen 2 Lancer. Best early healer.",
            "Molly": "B-tier Lancer. Budget healer option."
        },
        "ratio_explanation": "Arena's 5-hero format benefits from double Infantry (45%) to create a stronger frontline. Marksman (30%) provides kill power while Lancer (25%) heals."
    },
    "exploration": {
        "name": "Exploration / PvE",
        "slots": [
            # For exploration, sustain/survival heroes preferred - Natalia's heal keeps her at top
            {"class": "Infantry", "role": "Tank", "preferred": ["Natalia", "Elif", "Hervor", "Magnus", "Wu Ming", "Gatot", "Edith", "Flint", "Sergey"], "is_lead": True},
            # Lancer: S first for healing
            {"class": "Lancer", "role": "Healer", "preferred": ["Dominic", "Flora", "Karol", "Freya", "Sonya", "Gordon", "Renee", "Norah", "Lloyd", "Fred", "Molly"]},
            # Marksman: S+ first
            {"class": "Marksman", "role": "DPS", "preferred": ["Vulcanus", "Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
        ],
        "troop_ratio": {"infantry": 40, "lancer": 30, "marksman": 30},
        "notes": "Uses EXPLORATION skills (left side). Survival > speed.",
        "key_heroes": ["Natalia", "Molly", "Alonso"],
        "hero_explanations": {
            # Infantry (tank - sustain prioritized for PvE)
            "Natalia": "A-tier Infantry. Exploration heal keeps you going through waves. TOP for PvE.",
            "Elif": "S+ Gen 14 Infantry. Shield + sustain. Great PvE tank.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + damage. Strong pick.",
            "Magnus": "S+ Gen 9 Infantry. Shield + defense. Reliable.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% damage taken. Excellent sustain.",
            "Gatot": "S Gen 8 Infantry. 3/3 sustain. Pure survival.",
            "Edith": "S Gen 7 Infantry. 3/3 sustain. Extremely tanky.",
            "Flint": "A-tier Infantry. Good exploration skills. Solid tank.",
            "Sergey": "A-tier Infantry. Defensive skills. Backup tank.",
            # Lancer (healer - healing crucial for multi-wave PvE)
            "Dominic": "S Gen 14 Lancer. Damage + sustain mix.",
            "Flora": "S Gen 13 Lancer. Heals 5-25% HP. Best PvE healer.",
            "Karol": "S Gen 12 Lancer. -4-20% damage taken for ALL.",
            "Freya": "S Gen 10 Lancer. Reduces damage taken.",
            "Sonya": "S Gen 8 Lancer. Offense-focused buffs.",
            "Gordon": "S Gen 7 Lancer. Venom + debuff.",
            "Renee": "S Gen 6 Lancer. Infantry ATK boost.",
            "Norah": "S Gen 5 Lancer. -15% damage AND +15% dealt.",
            "Philly": "A Gen 2 Lancer. Best early healer. Essential for early PvE.",
            "Molly": "B-tier Lancer. Budget healer. Essential for long sessions.",
            # Marksman (DPS - clear enemies efficiently)
            "Vulcanus": "S+ Gen 13 Marksman. Sustain + high DPS. Great for PvE.",
            "Blanchette": "S+ Gen 10 Marksman. Pure offense. Fast clears.",
            "Cara": "S Gen 14 Marksman. Sustain + offense.",
            "Ligeia": "S Gen 12 Marksman. Balanced damage.",
            "Rufus": "S Gen 11 Marksman. High burst damage.",
            "Xura": "S Gen 9 Marksman. Sustain + DPS.",
            "Hendrik": "S Gen 8 Marksman. Defense + single-target.",
            "Bradley": "S Gen 6 Marksman. Solid damage.",
            "Gwen": "A Gen 4 Marksman. Mid-game DPS option.",
            "Wayne": "A Gen 6 Marksman. Sustained DPS.",
            "Alonso": "A Gen 2 Marksman. Early-game best. Efficient clears."
        },
        "ratio_explanation": "Exploration uses EXPLORATION skills (left side of hero skill panel), not expedition skills. Balanced 40/30/30 maximizes sustainability for multi-wave PvE content."
    },
    "svs_march": {
        "name": "SvS Field March",
        "slots": [
            # Infantry: S+ first for field combat (Jeronimo for offense buffs)
            {"class": "Infantry", "role": "Lead/Tank", "preferred": ["Jeronimo", "Wu Ming", "Elif", "Hervor", "Magnus", "Gatot", "Edith", "Natalia", "Flint"], "is_lead": True},
            # Lancer: S first
            {"class": "Lancer", "role": "Support/Heal", "preferred": ["Dominic", "Flora", "Karol", "Freya", "Sonya", "Gordon", "Renee", "Norah", "Lloyd", "Fred", "Molly"]},
            # Marksman: S+ first
            {"class": "Marksman", "role": "Main DPS", "preferred": ["Vulcanus", "Blanchette", "Cara", "Ligeia", "Rufus", "Xura", "Hendrik", "Bradley", "Gwen", "Wayne", "Alonso"]},
        ],
        "troop_ratio": {"infantry": 40, "lancer": 20, "marksman": 40},
        "notes": "Balanced for unpredictable SvS field combat. Jeronimo for burst, Wu Ming for sustain.",
        "key_heroes": ["Jeronimo", "Wu Ming", "Molly", "Alonso"],
        "hero_explanations": {
            # Infantry (lead/tank for field combat)
            "Jeronimo": "S+ Gen 1 Infantry. +50% ATK/DMG. Best for burst kills in field.",
            "Wu Ming": "S+ Gen 6 Infantry. -25% damage taken. Better for extended engagements.",
            "Elif": "S+ Gen 14 Infantry. Shield + ATK reduction. Latest top-tier.",
            "Hervor": "S+ Gen 12 Infantry. Damage reduction + offense. Strong balanced pick.",
            "Magnus": "S+ Gen 9 Infantry. Shield + damage reduction. Reliable.",
            "Gatot": "S Gen 8 Infantry. 3/3 sustain. Pure defense tank.",
            "Edith": "S Gen 7 Infantry. 3/3 sustain. Extremely tanky.",
            "Natalia": "A-tier Infantry. Feral Protection sustain. Good for multiple skirmishes.",
            "Flint": "A-tier Infantry. Control + tank. Solid backup.",
            # Lancer (support/heal)
            "Dominic": "S Gen 14 Lancer. +100% Lancer damage + sustain.",
            "Flora": "S Gen 13 Lancer. Heals 5-25% HP. Best healer.",
            "Karol": "S Gen 12 Lancer. -4-20% damage taken for ALL.",
            "Freya": "S Gen 10 Lancer. Reduces damage taken.",
            "Sonya": "S Gen 8 Lancer. Offense-focused buffs.",
            "Gordon": "S Gen 7 Lancer. Venom + debuff.",
            "Renee": "S Gen 6 Lancer. Infantry ATK boost.",
            "Norah": "S Gen 5 Lancer. -15% damage AND +15% dealt.",
            "Philly": "A Gen 2 Lancer. Best early healer.",
            "Molly": "B-tier Lancer. Keeps you alive between fights.",
            # Marksman (DPS)
            "Vulcanus": "S+ Gen 13 Marksman. Sustain + defense + high DPS.",
            "Blanchette": "S+ Gen 10 Marksman. Pure offense. Maximum kill speed.",
            "Cara": "S Gen 14 Marksman. Sustain + offense mix.",
            "Ligeia": "S Gen 12 Marksman. Balanced damage.",
            "Rufus": "S Gen 11 Marksman. High burst damage.",
            "Xura": "S Gen 9 Marksman. Sustain + DPS.",
            "Hendrik": "S Gen 8 Marksman. Defense + single-target.",
            "Bradley": "S Gen 6 Marksman. Solid ranged damage.",
            "Gwen": "A Gen 4 Marksman. Mid-game option.",
            "Wayne": "A Gen 6 Marksman. Sustained DPS.",
            "Alonso": "A Gen 2 Marksman. Early-game best. High kill potential."
        },
        "ratio_explanation": "SvS field combat is unpredictable. 40/20/40 balanced ratio handles varied enemy compositions - enough Infantry to tank, enough Marksman to kill, Lancer for utility."
    },
}

# Frontend-friendly aliases for LINEUP_TEMPLATES
LINEUP_TEMPLATES["rally_attack"] = LINEUP_TEMPLATES["rally_joiner_attack"]
LINEUP_TEMPLATES["rally_defense"] = LINEUP_TEMPLATES["rally_joiner_defense"]

# Legacy IDEAL_LINEUPS for backward compatibility
IDEAL_LINEUPS = {
    "rally_leader_infantry": LINEUP_TEMPLATES["svs_attack"],
    "rally_leader_marksman": LINEUP_TEMPLATES["bear_trap"],
    "rally_joiner_attack": LINEUP_TEMPLATES["rally_joiner_attack"],
    "rally_joiner_defense": LINEUP_TEMPLATES["rally_joiner_defense"],
    "bear_trap": LINEUP_TEMPLATES["bear_trap"],
    "crazy_joe": LINEUP_TEMPLATES["crazy_joe"],
    "garrison": LINEUP_TEMPLATES["garrison"],
    "garrison_joiner": LINEUP_TEMPLATES["rally_joiner_defense"],  # Same as rally defense joiner
    "rally_joiner": LINEUP_TEMPLATES["rally_joiner_attack"],  # Alias for attack joiner
    "exploration": LINEUP_TEMPLATES["exploration"],
    "svs_march": LINEUP_TEMPLATES["svs_march"],  # Now uses dedicated 40/20/40 template
    "world_march": LINEUP_TEMPLATES["world_march"],
    # Frontend event type aliases
    "svs_attack": LINEUP_TEMPLATES["svs_attack"],
    "rally_attack": LINEUP_TEMPLATES["rally_joiner_attack"],
    "rally_defense": LINEUP_TEMPLATES["rally_joiner_defense"],
}


class LineupBuilder:
    """Build optimal lineups from user's available heroes."""

    def __init__(self, heroes_data: dict = None):
        """
        Initialize with static hero data.

        Args:
            heroes_data: Hero data from heroes.json (optional, loaded automatically if not provided)
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

            # For lead slots, follow preferred order strictly (first available wins)
            # For non-lead slots, pick highest power among preferred
            use_strict_order = is_lead

            # First try preferred heroes in order
            for hero_name in preferred:
                if hero_name in user_heroes and hero_name not in used_heroes:
                    hero_meta = get_hero_metadata(hero_name)
                    if hero_meta.get("gen", 99) <= max_generation:
                        hero_stats = user_heroes[hero_name]
                        hero_data = self.hero_lookup.get(hero_name)
                        power = calculate_hero_power(hero_stats, hero_data)

                        if use_strict_order:
                            # Lead slot: take FIRST available preferred hero
                            best_hero = hero_name
                            best_power = power
                            break
                        else:
                            # Non-lead slot: take highest power preferred hero
                            if power > best_power:
                                best_power = power
                                best_hero = hero_name

            # If no preferred hero found, find any hero of the right class
            if not best_hero:
                for hero_name, hero_stats in user_heroes.items():
                    if hero_name in used_heroes:
                        continue
                    hero_meta = get_hero_metadata(hero_name)
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
                hero_meta = get_hero_metadata(best_hero)
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
                        hero_meta = get_hero_metadata(hero)
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
                hero_meta = get_hero_metadata(key_hero)
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

        # Add specific warnings for missing critical joiner heroes
        hero_names_in_lineup = [h.get('hero', '') for h in lineup_heroes]
        if event_type in ['rally_joiner_defense', 'garrison_joiner']:
            if 'Sergey' not in user_heroes:
                notes += "\n⚠️ Sergey not available - garrison joining loses his Defenders' Edge skill (-20% damage taken for entire garrison)."
            elif 'Sergey' not in hero_names_in_lineup:
                notes += "\n💡 Tip: Put Sergey in slot 1 for garrison joining - his Defenders' Edge skill applies to the entire garrison."

        if event_type in ['rally_joiner_attack', 'rally_joiner']:
            if 'Jessie' not in user_heroes:
                notes += "\n⚠️ Jessie not available - rally joining loses her Stand of Arms skill (+25% damage dealt for your troops)."
            elif 'Jessie' not in hero_names_in_lineup:
                notes += "\n💡 Tip: Put Jessie in slot 1 for rally joining - her Stand of Arms skill gives +25% damage to all your troops."

        # For garrison, check if a sustain hero is close in power to the selected lead
        if event_type == 'garrison':
            sustain_heroes = template.get("sustain_heroes", {})
            lead_hero = next((h for h in lineup_heroes if h.get("is_lead")), None)
            if lead_hero and lead_hero.get("hero") not in sustain_heroes:
                lead_power = lead_hero.get("power", 0)
                # Check if any sustain hero is within 20% power of the lead
                for sustain_name, sustain_desc in sustain_heroes.items():
                    if sustain_name in user_heroes and sustain_name not in hero_names_in_lineup:
                        sustain_stats = user_heroes[sustain_name]
                        sustain_data = self.hero_lookup.get(sustain_name)
                        sustain_power = calculate_hero_power(sustain_stats, sustain_data)
                        if sustain_power > 0 and lead_power > 0:
                            power_ratio = sustain_power / lead_power
                            if power_ratio >= 0.8:  # Within 20% power
                                notes += f"\n💡 *{sustain_name} might be better for garrison - {sustain_desc}"
                                break  # Only show one suggestion

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
                hero_meta = get_hero_metadata(hero_name)
                if hero_meta.get("gen", 99) <= max_generation:
                    selected_hero = hero_name
                    break

            if selected_hero:
                used_heroes.add(selected_hero)
                hero_meta = get_hero_metadata(selected_hero)
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
        critical_slots = [s for s in ideal["slots"] if s.get("preferred", s.get("heroes", [])) != ["any"]]
        max_confidence = len(critical_slots) if critical_slots else 1

        for slot_info in ideal["slots"]:
            position = slot_info.get("position", slot_info.get("class", "Unknown"))
            preferred_heroes = slot_info.get("preferred", slot_info.get("heroes", []))
            role = slot_info.get("role", "Unknown")

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
            game_mode=ideal.get("mode", ideal.get("name", game_mode)),
            heroes=lineup_heroes,
            troop_ratio=ideal.get("troop_ratio", {"infantry": 33, "lancer": 33, "marksman": 34}),
            notes=ideal.get("notes", ""),
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
            # Sergey: Defenders' Edge (-20% DMG taken) - best for multiple rally waves
            # Patrick: Health boost (+25% HP) - alternative if leader prefers raw HP
            best_joiners = ["Sergey", "Patrick", "Natalia"]
            skill_name = "Defenders' Edge"
            effect = "-20% DMG taken"

        for joiner in best_joiners:
            if joiner in user_heroes:
                stats = user_heroes[joiner]
                # Joiner skill is expedition_skill_1 (top-right position)
                exp_skill = stats.get('expedition_skill_1', stats.get('expedition_skill', 1))

                # Build recommendation text based on hero
                if joiner == "Patrick":
                    rec_text = f"Use {joiner} in slot 1. Skill at L{exp_skill}/5. Provides +25% HP boost."
                    note = "Patrick's health boost is an alternative to Sergey's -20% damage reduction. Sergey is generally better for multi-wave defense, but some rally leaders prefer the raw HP from Patrick."
                elif joiner == "Sergey":
                    rec_text = f"Use {joiner} in slot 1. Skill at L{exp_skill}/5."
                    note = f"ONLY slot 1 hero's top-right skill ({skill_name}: {effect}) applies when joining!"
                    # If Patrick is also owned, mention the alternative
                    if "Patrick" in user_heroes:
                        patrick_skill = user_heroes["Patrick"].get('expedition_skill_1', user_heroes["Patrick"].get('expedition_skill', 1))
                        note += f"\n💡 Alternative: Patrick (L{patrick_skill}/5) provides +25% HP instead. Some leaders prefer health over damage reduction."
                else:
                    rec_text = f"Use {joiner} in slot 1. Skill at L{exp_skill}/5."
                    note = f"ONLY slot 1 hero's top-right skill ({skill_name}: {effect}) applies when joining!"

                return {
                    "hero": joiner,
                    "status": "owned",
                    "skill_level": exp_skill,
                    "max_skill": 5,
                    "recommendation": rec_text,
                    "action": f"Max {joiner}'s expedition skill" if exp_skill < 5 else "Ready to join!",
                    "critical_note": note
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
