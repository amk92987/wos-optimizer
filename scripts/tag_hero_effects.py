"""
Tag all heroes' expedition skills with structured effect data.

Effect schema per skill:
  {
    "type": str,          # effect category
    "target": str,        # "all", "infantry", "lancer", "marksman", "enemy"
    "max_value": number,  # max percentage at skill level 5
    "effective_pct": int   # average uptime/trigger rate (100 = always, 50 = 50% chance)
  }

Scoring formula:
  effective_value = max_value * (skill_level / 5) * (effective_pct / 100)

Effect types:
  COMBAT BUFFS (friendly):
    atk_buff, def_buff, hp_buff, dmg_dealt_buff, dmg_reduction,
    lethality_buff, crit_rate_buff, crit_dmg_buff, shield, dodge,
    troop_healing, atk_speed_buff, extra_dmg

  COMBAT DEBUFFS (enemy):
    enemy_atk_debuff, enemy_def_debuff, enemy_dmg_debuff,
    enemy_lethality_debuff, enemy_crit_debuff, enemy_vuln

  PERIODIC:
    periodic_dmg

  UTILITY (non-combat):
    gathering_speed, gathering_capacity, march_speed, training_speed,
    research_speed, building_speed, building_cost_reduction,
    healing_speed, stamina_reduction
"""

import json
import sys
from pathlib import Path

# fmt: off
HERO_EXPEDITION_EFFECTS = {

    # ============================================================
    # GEN 1
    # ============================================================

    "Bahiti": {
        "expedition_skill_1_effects": [
            {"type": "dmg_reduction", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # 50% chance of increasing damage dealt by 10-50%
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 50, "effective_pct": 50},
        ],
    },

    "Charlie": {
        "expedition_skill_1_effects": [
            {"type": "gathering_speed", "target": "coal", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "gathering_capacity", "target": "coal", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Cloris": {
        "expedition_skill_1_effects": [
            {"type": "gathering_speed", "target": "meat", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "gathering_capacity", "target": "meat", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Eugene": {
        "expedition_skill_1_effects": [
            {"type": "gathering_speed", "target": "wood", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "gathering_capacity", "target": "wood", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Gina": {
        "expedition_skill_1_effects": [
            {"type": "stamina_reduction", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "march_speed", "target": "all", "max_value": 100, "effective_pct": 100},
        ],
    },

    "Jasser": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "research_speed", "target": "all", "max_value": 15, "effective_pct": 100},
        ],
    },

    "Jeronimo": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # 2 turns every 4 turns = 50% uptime
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 30, "effective_pct": 50},
        ],
    },

    "Jessie": {
        "expedition_skill_1_effects": [
            # Best attack joiner skill in the game
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "dmg_reduction", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
    },

    "Ling Xue": {
        "expedition_skill_1_effects": [
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "training_speed", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Lumak Bokan": {
        "expedition_skill_1_effects": [
            {"type": "enemy_dmg_debuff", "target": "enemy", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "march_speed", "target": "all", "max_value": 100, "effective_pct": 100},
        ],
    },

    "Molly": {
        "expedition_skill_1_effects": [
            # 40% chance of reducing damage taken by 10-50%
            {"type": "dmg_reduction", "target": "all", "max_value": 50, "effective_pct": 40},
        ],
        "expedition_skill_2_effects": [
            # 50% chance of increasing damage dealt by 10-50%
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 50, "effective_pct": 50},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Natalia": {
        "expedition_skill_1_effects": [
            # 40% chance to reduce damage taken by 10-50%
            {"type": "dmg_reduction", "target": "all", "max_value": 50, "effective_pct": 40},
        ],
        "expedition_skill_2_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Patrick": {
        "expedition_skill_1_effects": [
            {"type": "hp_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Seo-yoon": {
        "expedition_skill_1_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "healing_speed", "target": "all", "max_value": 50, "effective_pct": 100},
        ],
    },

    "Sergey": {
        "expedition_skill_1_effects": [
            # Best garrison joiner skill - reduces damage taken for ALL troops
            {"type": "dmg_reduction", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # "Reduces enemy attack power during combat" - estimated 20% based on similar Gen 1 skills
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 20, "effective_pct": 100},
        ],
    },

    "Smith": {
        "expedition_skill_1_effects": [
            {"type": "gathering_speed", "target": "iron", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "gathering_capacity", "target": "iron", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Zinman": {
        "expedition_skill_1_effects": [
            {"type": "building_speed", "target": "all", "max_value": 15, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "building_cost_reduction", "target": "all", "max_value": 15, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # Garrison-specific damage reduction
            {"type": "dmg_reduction", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
    },

    # ============================================================
    # GEN 2
    # ============================================================

    "Alonso": {
        "expedition_skill_1_effects": [
            # 40% chance of granting lethality boost
            {"type": "lethality_buff", "target": "all", "max_value": 50, "effective_pct": 40},
        ],
        "expedition_skill_2_effects": [
            # 20% chance to reduce enemy damage for 2 turns
            {"type": "enemy_dmg_debuff", "target": "enemy", "max_value": 50, "effective_pct": 20},
        ],
        "expedition_skill_3_effects": [
            # 50% chance to deal additional damage
            {"type": "extra_dmg", "target": "all", "max_value": 50, "effective_pct": 50},
        ],
    },

    "Flint": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 100, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "lethality_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Philly": {
        "expedition_skill_1_effects": [
            # Dual buff: ATK 3-15% and DEF 2-10%
            {"type": "atk_buff", "target": "all", "max_value": 15, "effective_pct": 100},
            {"type": "def_buff", "target": "all", "max_value": 10, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # 25% chance of dealing +120-200% damage
            {"type": "extra_dmg", "target": "all", "max_value": 200, "effective_pct": 25},
        ],
        "expedition_skill_3_effects": [
            # 40% chance of reducing damage taken by 10-50%
            {"type": "dmg_reduction", "target": "all", "max_value": 50, "effective_pct": 40},
        ],
    },

    # ============================================================
    # GEN 3
    # ============================================================

    "Greg": {
        "expedition_skill_1_effects": [
            # 20% chance of increasing damage dealt by 8-40% for 3 turns
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 40, "effective_pct": 20},
        ],
        "expedition_skill_2_effects": [
            # 20% chance of reducing enemy damage dealt by 10-50% for 2 turns
            {"type": "enemy_dmg_debuff", "target": "enemy", "max_value": 50, "effective_pct": 20},
        ],
        "expedition_skill_3_effects": [
            {"type": "hp_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Logan": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "lancer", "max_value": 50, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "def_buff", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
    },

    "Mia": {
        "expedition_skill_1_effects": [
            # 50% chance of cursing targets, increasing their damage taken by 10-50%
            {"type": "enemy_vuln", "target": "enemy", "max_value": 50, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            # 50% chance of dealing 10-50% additional damage
            {"type": "extra_dmg", "target": "all", "max_value": 50, "effective_pct": 50},
        ],
        "expedition_skill_3_effects": [
            # 40% chance of reducing damage taken by 10-50%
            {"type": "dmg_reduction", "target": "all", "max_value": 50, "effective_pct": 40},
        ],
    },

    # ============================================================
    # GEN 4
    # ============================================================

    "Ahmose": {
        "expedition_skill_1_effects": [
            # Infantry pauses every 4 attacks: infantry -70% dmg taken, lancer/marksman -30%, for 2 turns
            # Uptime: 2 of 4 turns = 50%
            {"type": "dmg_reduction", "target": "infantry", "max_value": 70, "effective_pct": 50},
            {"type": "dmg_reduction", "target": "lancer", "max_value": 30, "effective_pct": 50},
            {"type": "dmg_reduction", "target": "marksman", "max_value": 30, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 100, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # +12-60% damage per infantry attack AND +5-25% enemy damage taken for 1 turn
            {"type": "extra_dmg", "target": "infantry", "max_value": 60, "effective_pct": 100},
            {"type": "enemy_vuln", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Lynn": {
        "expedition_skill_1_effects": [
            # 40% chance of increasing damage dealt by 10-50%
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 50, "effective_pct": 40},
        ],
        "expedition_skill_2_effects": [
            {"type": "enemy_dmg_debuff", "target": "enemy", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # +1-5% ATK per 3 attacks, stacking to end of battle
            # Average over ~20 attacks: ~7 stacks at level 5 = 35% avg ATK
            {"type": "atk_buff", "target": "marksman", "max_value": 35, "effective_pct": 100},
        ],
    },

    "Reina": {
        "expedition_skill_1_effects": [
            # Increases normal attack damage by 10-30% for all troops
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 30, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # 4-20% chance of dodging normal attacks
            {"type": "dodge", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # 25% chance of extra attack dealing 120-200% damage (Lancers)
            {"type": "extra_dmg", "target": "lancer", "max_value": 200, "effective_pct": 25},
        ],
    },

    # ============================================================
    # GEN 5
    # ============================================================

    "Gwen": {
        "expedition_skill_1_effects": [
            # Marks targets, increasing their damage taken by up to 25%
            {"type": "enemy_vuln", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # Increases Marksmen damage and team-wide combat buffs
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # Periodic AoE bombardment
            {"type": "periodic_dmg", "target": "enemy", "max_value": 25, "effective_pct": 50},
        ],
    },

    "Hector": {
        "expedition_skill_1_effects": [
            # 40% chance of reducing damage taken by 10-50%
            {"type": "dmg_reduction", "target": "all", "max_value": 50, "effective_pct": 40},
        ],
        "expedition_skill_2_effects": [
            # Infantry: 100-200% for 10 attacks (diminishing), Marksman: 20-100%
            # Averaged over battle: ~50% uptime with diminishing returns
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 200, "effective_pct": 25},
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 100, "effective_pct": 25},
        ],
        "expedition_skill_3_effects": [
            # 25% chance of dealing 120-200% damage
            {"type": "extra_dmg", "target": "all", "max_value": 200, "effective_pct": 25},
        ],
    },

    "Norah": {
        "expedition_skill_1_effects": [
            # -3-15% damage taken AND +3-15% damage dealt for Infantry and Marksman
            {"type": "dmg_reduction", "target": "infantry", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_reduction", "target": "marksman", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 15, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # 20% chance of dealing 20-100% extra damage to all enemies
            # Best rally joiner skill (after Jessie's Stand of Arms)
            {"type": "extra_dmg", "target": "all", "max_value": 100, "effective_pct": 20},
        ],
        "expedition_skill_3_effects": [
            # +5-25% damage dealt and -5-25% damage taken every 5 lancer attacks for 2 turns
            # Uptime: ~35% (depends on lancer attack frequency)
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 35},
            {"type": "dmg_reduction", "target": "all", "max_value": 25, "effective_pct": 35},
        ],
    },

    # ============================================================
    # GEN 6
    # ============================================================

    "Renee": {
        "expedition_skill_1_effects": [
            # Dream Marks: extra 40-200% Lancer Damage every 2 turns
            {"type": "extra_dmg", "target": "lancer", "max_value": 200, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            # Marked targets take 30-150% more troop damage (while mark active ~50% uptime)
            {"type": "enemy_vuln", "target": "enemy", "max_value": 150, "effective_pct": 50},
        ],
        "expedition_skill_3_effects": [
            # +15-75% damage dealt to marked targets for all troops
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 75, "effective_pct": 50},
        ],
    },

    "Wayne": {
        "expedition_skill_1_effects": [
            # All troops extra attack every 4 turns, dealing 20-100% damage
            {"type": "extra_dmg", "target": "all", "max_value": 100, "effective_pct": 25},
        ],
        "expedition_skill_2_effects": [
            # Every other attack, Marksmen deal 8-40% extra to lancers, 4-20% to marksmen
            # Averaged: ~30% extra damage, 50% uptime
            {"type": "extra_dmg", "target": "marksman", "max_value": 30, "effective_pct": 50},
        ],
        "expedition_skill_3_effects": [
            {"type": "crit_rate_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Wu Ming": {
        "expedition_skill_1_effects": [
            # Reduces damage from normal attacks by 5-25% and skills by 6-30%
            # Weighted average: ~28%
            {"type": "dmg_reduction", "target": "all", "max_value": 28, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # Skill damage only (~40% of total damage)
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 40},
        ],
    },

    # ============================================================
    # GEN 7
    # ============================================================

    "Bradley": {
        "expedition_skill_1_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # +6-30% vs Lancers, +5-25% vs Infantry (averaged ~25% across targets)
            {"type": "extra_dmg", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # 6-30% offense boost for 2 turns every 4 turns = 50% uptime
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 30, "effective_pct": 50},
        ],
    },

    "Edith": {
        "expedition_skill_1_effects": [
            # Shields ranged: reduces damage TO marksmen by 4-20%, increases lancer damage by 4-20%
            {"type": "dmg_reduction", "target": "marksman", "max_value": 20, "effective_pct": 100},
            {"type": "dmg_dealt_buff", "target": "lancer", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "dmg_reduction", "target": "infantry", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "hp_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Gordon": {
        "expedition_skill_1_effects": [
            # Lancers deal 20-100% extra every 2 attacks = 50% uptime
            {"type": "extra_dmg", "target": "lancer", "max_value": 100, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            # Lancer +30-150% damage AND enemy -6-30% damage for 1 turn every 3 = 33%
            {"type": "dmg_dealt_buff", "target": "lancer", "max_value": 150, "effective_pct": 33},
            {"type": "enemy_dmg_debuff", "target": "enemy", "max_value": 30, "effective_pct": 33},
        ],
        "expedition_skill_3_effects": [
            # Increases enemy Infantry damage taken by 6-30%
            {"type": "enemy_vuln", "target": "enemy", "max_value": 30, "effective_pct": 100},
        ],
    },

    # ============================================================
    # GEN 8
    # ============================================================

    "Gatot": {
        "expedition_skill_1_effects": [
            {"type": "def_buff", "target": "infantry", "max_value": 30, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # Shield equal to ATK x 6-30% per attack for 1 turn
            {"type": "shield", "target": "infantry", "max_value": 30, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Hendrik": {
        "expedition_skill_1_effects": [
            # Reduces ALL enemy troops' Defense by 5-25%
            {"type": "enemy_def_debuff", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # Increases friendly Defense by 6-30% every 4 turns for 2 turns = 50%
            {"type": "def_buff", "target": "all", "max_value": 30, "effective_pct": 50},
        ],
        "expedition_skill_3_effects": [
            # Every 3 turns, marksmen deal 8-40% damage to all enemies = 33%
            {"type": "periodic_dmg", "target": "enemy", "max_value": 40, "effective_pct": 33},
        ],
    },

    "Sonya": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # Lancers +15-75% extra every 2 attacks AND +5-25% ATK for all troops for 1 turn
            {"type": "extra_dmg", "target": "lancer", "max_value": 75, "effective_pct": 50},
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 50},
        ],
        "expedition_skill_3_effects": [
            # Lancers deal 50-250% damage every 5 turns = 20% uptime + stun
            {"type": "periodic_dmg", "target": "lancer", "max_value": 250, "effective_pct": 20},
        ],
    },

    # ============================================================
    # GEN 9
    # ============================================================

    "Fred": {
        "expedition_skill_1_effects": [
            # +3-15% enemy damage taken for 2 turns every 4 turns = 50%
            {"type": "enemy_vuln", "target": "enemy", "max_value": 15, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            # Lancers +20-100% extra every 3 turns AND -5-25% enemy ATK for 1 turn
            {"type": "extra_dmg", "target": "lancer", "max_value": 100, "effective_pct": 33},
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 25, "effective_pct": 33},
        ],
        "expedition_skill_3_effects": [
            # 10-50% damage to all enemies every 3 turns = 33%
            {"type": "periodic_dmg", "target": "enemy", "max_value": 50, "effective_pct": 33},
        ],
    },

    "Magnus": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 100, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # Shield: 6-30% of ATK every 3 turns for 1 turn = 33%
            {"type": "shield", "target": "infantry", "max_value": 30, "effective_pct": 33},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_reduction", "target": "infantry", "max_value": 15, "effective_pct": 100},
        ],
    },

    "Xura": {
        "expedition_skill_1_effects": [
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "dmg_reduction", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 100, "effective_pct": 100},
        ],
    },

    # ============================================================
    # GEN 10
    # ============================================================

    "Blanchette": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 100, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # +5-25% bonus damage vs wounded targets
            {"type": "extra_dmg", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "crit_rate_buff", "target": "all", "max_value": 20, "effective_pct": 100},
            {"type": "crit_dmg_buff", "target": "all", "max_value": 50, "effective_pct": 100},
        ],
    },

    "Freya": {
        "expedition_skill_1_effects": [
            # Infantry and Marksmen: -3-15% damage taken, +3-15% damage dealt
            {"type": "dmg_reduction", "target": "infantry", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_reduction", "target": "marksman", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 15, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # Marked enemies take 20-100% extra from Lancers, spread 10-50% to nearby
            {"type": "extra_dmg", "target": "lancer", "max_value": 100, "effective_pct": 100},
            {"type": "periodic_dmg", "target": "enemy", "max_value": 50, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Gregory": {
        "expedition_skill_1_effects": [
            # +10-50% Infantry damage every 4 turns for 2 turns = 50%
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 50, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_reduction", "target": "infantry", "max_value": 20, "effective_pct": 100},
        ],
    },

    # ============================================================
    # GEN 11
    # ============================================================

    "Eleonora": {
        "expedition_skill_1_effects": [
            {"type": "hp_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # 10-50% damage to all enemies every 4 turns = 25%
            {"type": "periodic_dmg", "target": "enemy", "max_value": 50, "effective_pct": 25},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 100, "effective_pct": 100},
        ],
    },

    "Lloyd": {
        "expedition_skill_1_effects": [
            {"type": "enemy_lethality_debuff", "target": "enemy", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # Lancer ATK +30-150% every 3 turns for 1 turn = 33%
            {"type": "atk_buff", "target": "lancer", "max_value": 150, "effective_pct": 33},
        ],
        "expedition_skill_3_effects": [
            {"type": "lethality_buff", "target": "all", "max_value": 50, "effective_pct": 100},
        ],
    },

    "Rufus": {
        "expedition_skill_1_effects": [
            # Infantry +12-60% damage AND +5-25% enemy damage taken, 2 turns every 4 = 50%
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 60, "effective_pct": 50},
            {"type": "enemy_vuln", "target": "enemy", "max_value": 25, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            {"type": "enemy_lethality_debuff", "target": "enemy", "max_value": 50, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 100, "effective_pct": 100},
        ],
    },

    # ============================================================
    # GEN 12
    # ============================================================

    "Hervor": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "dmg_reduction", "target": "infantry", "max_value": 30, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # Infantry: +20-100% damage AND -4-20% damage taken
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 100, "effective_pct": 100},
            {"type": "dmg_reduction", "target": "infantry", "max_value": 20, "effective_pct": 100},
        ],
    },

    "Karol": {
        "expedition_skill_1_effects": [
            {"type": "dmg_reduction", "target": "all", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # +6-30% vs Lancers, +5-25% vs Infantry (averaged ~25%)
            {"type": "extra_dmg", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Ligeia": {
        "expedition_skill_1_effects": [
            # Marksmen deal 20-100% extra every 2 attacks = 50%
            {"type": "extra_dmg", "target": "marksman", "max_value": 100, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            # +5-25% enemy damage taken for 2 turns every 3 turns = 67%
            {"type": "enemy_vuln", "target": "enemy", "max_value": 25, "effective_pct": 67},
        ],
        "expedition_skill_3_effects": [
            {"type": "enemy_def_debuff", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
    },

    # ============================================================
    # GEN 13
    # ============================================================

    "Flora": {
        "expedition_skill_1_effects": [
            # 10-50% chance to increase enemy damage taken by 10-50%
            # At level 5: 50% chance, 50% vuln
            {"type": "enemy_vuln", "target": "enemy", "max_value": 50, "effective_pct": 50},
        ],
        "expedition_skill_2_effects": [
            # Heals 5-25% of max HP every 4 turns = 25%
            {"type": "troop_healing", "target": "all", "max_value": 25, "effective_pct": 25},
        ],
        "expedition_skill_3_effects": [
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
    },

    "Gisela": {
        "expedition_skill_1_effects": [
            {"type": "def_buff", "target": "infantry", "max_value": 30, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "atk_buff", "target": "all", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # 10-50% damage every 3 turns = 33%
            {"type": "periodic_dmg", "target": "enemy", "max_value": 50, "effective_pct": 33},
        ],
    },

    "Vulcanus": {
        "expedition_skill_1_effects": [
            # +12-60% Marksmen ATK AND -12-60% enemy Infantry/Lancer Defense (~67% of enemies)
            {"type": "atk_buff", "target": "marksman", "max_value": 60, "effective_pct": 100},
            {"type": "enemy_def_debuff", "target": "enemy", "max_value": 60, "effective_pct": 67},
        ],
        "expedition_skill_2_effects": [
            # +10-50% damage vs high-defense targets (most PvP targets qualify ~80%)
            {"type": "extra_dmg", "target": "all", "max_value": 50, "effective_pct": 80},
        ],
        "expedition_skill_3_effects": [
            # Bleed: 2-10% extra per turn for 2 turns on every attack
            {"type": "extra_dmg", "target": "all", "max_value": 10, "effective_pct": 100},
        ],
    },

    # ============================================================
    # GEN 14
    # ============================================================

    "Cara": {
        "expedition_skill_1_effects": [
            {"type": "enemy_crit_debuff", "target": "enemy", "max_value": 20, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # +6-30% normal attack damage for all troops
            {"type": "dmg_dealt_buff", "target": "all", "max_value": 30, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 100, "effective_pct": 100},
        ],
    },

    "Dominic": {
        "expedition_skill_1_effects": [
            {"type": "dmg_dealt_buff", "target": "lancer", "max_value": 100, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            # 10-50% damage every 3 turns = 33%
            {"type": "periodic_dmg", "target": "enemy", "max_value": 50, "effective_pct": 33},
        ],
        "expedition_skill_3_effects": [
            # Infantry and Marksmen: -3-15% damage taken, +3-15% damage dealt
            {"type": "dmg_reduction", "target": "infantry", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_reduction", "target": "marksman", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 15, "effective_pct": 100},
            {"type": "dmg_dealt_buff", "target": "marksman", "max_value": 15, "effective_pct": 100},
        ],
    },

    "Elif": {
        "expedition_skill_1_effects": [
            {"type": "enemy_atk_debuff", "target": "enemy", "max_value": 25, "effective_pct": 100},
        ],
        "expedition_skill_2_effects": [
            {"type": "dmg_dealt_buff", "target": "infantry", "max_value": 100, "effective_pct": 100},
        ],
        "expedition_skill_3_effects": [
            # Shield: 6-30% of ATK every 3 turns for infantry = 33%
            {"type": "shield", "target": "infantry", "max_value": 30, "effective_pct": 33},
        ],
    },
}
# fmt: on


def main():
    heroes_path = Path(__file__).parent.parent / "data" / "heroes.json"
    with open(heroes_path, encoding="utf-8") as f:
        data = json.load(f)

    heroes = data["heroes"]
    tagged = 0
    effects_added = 0

    for hero in heroes:
        name = hero["name"]
        if name in HERO_EXPEDITION_EFFECTS:
            effects_data = HERO_EXPEDITION_EFFECTS[name]
            for key, effects_list in effects_data.items():
                hero[key] = effects_list
                effects_added += len(effects_list)
            tagged += 1

    # Also clear any old _effects fields for heroes NOT in our map
    # (in case we removed a hero or renamed)
    for hero in heroes:
        if hero["name"] not in HERO_EXPEDITION_EFFECTS:
            for i in range(1, 4):
                for prefix in ["expedition_skill", "exploration_skill"]:
                    key = f"{prefix}_{i}_effects"
                    if key in hero:
                        del hero[key]

    with open(heroes_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Tagged {tagged} heroes with {effects_added} total effects")
    print(f"Heroes without effects: {len(heroes) - tagged}")

    # Verify all heroes in our map exist in heroes.json
    hero_names = {h["name"] for h in heroes}
    for name in HERO_EXPEDITION_EFFECTS:
        if name not in hero_names:
            print(f"WARNING: {name} in effects map but not in heroes.json!")

    # Show heroes without combat effects
    print("\nHeroes with no expedition combat effects (utility-only or gathering):")
    for hero in sorted(heroes, key=lambda h: (h.get("generation", 0), h["name"])):
        name = hero["name"]
        if name not in HERO_EXPEDITION_EFFECTS:
            print(f"  {name} (Gen {hero.get('generation', '?')})")
            continue
        effects_data = HERO_EXPEDITION_EFFECTS[name]
        combat_effects = []
        for key, effects_list in effects_data.items():
            for eff in effects_list:
                if eff["type"] not in (
                    "gathering_speed", "gathering_capacity", "march_speed",
                    "training_speed", "research_speed", "building_speed",
                    "building_cost_reduction", "healing_speed", "stamina_reduction",
                ):
                    combat_effects.append(eff)
        if not combat_effects:
            print(f"  {name} (Gen {hero.get('generation', '?')}) - utility only")


if __name__ == "__main__":
    main()
