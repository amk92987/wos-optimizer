"""
Pack Analyzer - Evaluate real value of in-game purchase packs.
Cuts through inflated % values to show what you're actually paying for.
"""

import streamlit as st
from pathlib import Path
import sys
import json
import base64

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Assets directory
ITEMS_DIR = PROJECT_ROOT / "assets" / "items"

# Load resource hierarchy for value calculations
HIERARCHY_PATH = PROJECT_ROOT / "data" / "conversions" / "resource_value_hierarchy.json"
if HIERARCHY_PATH.exists():
    with open(HIERARCHY_PATH) as f:
        RESOURCE_HIERARCHY = json.load(f)
else:
    RESOURCE_HIERARCHY = {"resources": {}, "value_tiers": {}}

# Price options
PRICE_OPTIONS = [0.99, 1.99, 2.99, 4.99, 9.99, 14.99, 19.99, 29.99, 49.99, 99.99]

# Item definitions with Frost Star values (1 FS = $0.01), tiers, images, and descriptions
# Values derived from pack back-calculations and shop cross-references
PACK_ITEMS = {
    "hero": {
        "label": "Hero Items",
        "category": "unique",
        "items": [
            {"id": "mythic_shard", "name": "Mythic Shards", "image": "mythic_hero_shard.png", "fs_value": 33, "tier": "A", "desc": "Gold/orange shards for Mythic (Legendary) heroes"},
            {"id": "epic_shard", "name": "Epic Shards", "image": "epic_hero_shard.png", "fs_value": 17, "tier": "B", "desc": "Purple shards for Epic heroes"},
            {"id": "rare_shard", "name": "Rare Shards", "image": "rare_hero_shard.png", "fs_value": 8, "tier": "C", "desc": "Blue shards for Rare heroes"},
            {"id": "specific_mythic_shard", "name": "Specific Hero Shards", "image": "mythic_hero_shard.png", "fs_value": 40, "tier": "A", "desc": "Shards for specific heroes (Molly, etc.)"},
            {"id": "hero_xp_1k", "name": "Hero XP (1k)", "image": "hero_xp.png", "fs_value": 1, "tier": "C", "desc": "1000 experience points"},
            {"id": "hero_xp_5k", "name": "Hero XP (5k)", "image": "hero_xp.png", "fs_value": 5, "tier": "C", "desc": "5000 experience points"},
            {"id": "mythic_exploration_manual", "name": "Mythic Explore Manual", "image": "mythic_exploration_manual.png", "fs_value": 3.7, "tier": "B", "desc": "Upgrades exploration skills for Mythic heroes"},
            {"id": "epic_exploration_manual", "name": "Epic Explore Manual", "image": "epic_exploration_manual.png", "fs_value": 17, "tier": "B", "desc": "Upgrades exploration skills for Epic heroes"},
            {"id": "rare_exploration_manual", "name": "Rare Explore Manual", "image": "rare_exploration_manual.png", "fs_value": 5, "tier": "C", "desc": "Upgrades exploration skills for Rare heroes"},
            {"id": "mythic_expedition_manual", "name": "Mythic Expedition Manual", "image": "mythic_expedition_manual.png", "fs_value": 3.7, "tier": "B", "desc": "Upgrades expedition skills for Mythic heroes"},
            {"id": "epic_expedition_manual", "name": "Epic Expedition Manual", "image": "epic_expedition_manual.png", "fs_value": 17, "tier": "B", "desc": "Upgrades expedition skills for Epic heroes"},
            {"id": "rare_expedition_manual", "name": "Rare Expedition Manual", "image": "rare_expedition_manual.png", "fs_value": 5, "tier": "C", "desc": "Upgrades expedition skills for Rare heroes"},
        ]
    },
    "hero_gear": {
        "label": "Hero Gear",
        "category": "unique",
        "items": [
            {"id": "essence_stone", "name": "Essence Stones", "image": "essence_stone.png", "fs_value": 22, "tier": "A", "desc": "For Mythic gear mastery. $0.22 each"},
            {"id": "mithril", "name": "Mithril", "image": "mithril.png", "fs_value": 141, "tier": "S", "desc": "Rare material for gear empowerment. $1.41 each"},
            {"id": "xp_component", "name": "Hero Gear XP (per 100)", "image": "xp_component.png", "fs_value": 13, "tier": "B", "desc": "Enhancement XP components"},
            {"id": "lucky_hero_gear_chest", "name": "Lucky Gear Chest", "image": "mythic_hero_gear_chest.png", "fs_value": 22, "tier": "A", "desc": "Random hero gear pieces"},
            {"id": "epic_hero_gear_chest", "name": "Epic Gear Chest", "image": "epic_hero_gear_chest.png", "fs_value": 12, "tier": "B", "desc": "Contains random epic hero gear pieces"},
            {"id": "hero_gear_chest", "name": "Hero Gear Chest", "image": "hero_gear_chest.png", "fs_value": 8, "tier": "C", "desc": "Contains random hero gear pieces"},
        ]
    },
    "hero_gear_chests": {
        "label": "Custom Gear Chests",
        "category": "unique",
        "items": [
            {"id": "custom_hero_gear_s1", "name": "Custom Gear S1", "image": "mythic_hero_gear_chest.png", "fs_value": 22, "tier": "B", "desc": "Choose hero gear (Gen 1 - oldest)"},
            {"id": "custom_hero_gear_s2", "name": "Custom Gear S2", "image": "mythic_hero_gear_chest.png", "fs_value": 24, "tier": "B", "desc": "Choose hero gear (Gen 2)"},
            {"id": "custom_hero_gear_s3", "name": "Custom Gear S3", "image": "mythic_hero_gear_chest.png", "fs_value": 26, "tier": "B", "desc": "Choose hero gear (Gen 3)"},
            {"id": "custom_hero_gear_s4", "name": "Custom Gear S4", "image": "mythic_hero_gear_chest.png", "fs_value": 28, "tier": "B", "desc": "Choose hero gear (Gen 4)"},
            {"id": "custom_hero_gear_s5", "name": "Custom Gear S5", "image": "mythic_hero_gear_chest.png", "fs_value": 30, "tier": "B", "desc": "Choose hero gear (Gen 5)"},
            {"id": "custom_hero_gear_s6", "name": "Custom Gear S6", "image": "mythic_hero_gear_chest.png", "fs_value": 32, "tier": "A", "desc": "Choose hero gear (Gen 6)"},
            {"id": "custom_hero_gear_s7", "name": "Custom Gear S7", "image": "mythic_hero_gear_chest.png", "fs_value": 34, "tier": "A", "desc": "Choose hero gear (Gen 7)"},
            {"id": "custom_hero_gear_s8", "name": "Custom Gear S8", "image": "mythic_hero_gear_chest.png", "fs_value": 36, "tier": "A", "desc": "Choose hero gear (Gen 8)"},
            {"id": "custom_hero_gear_s9", "name": "Custom Gear S9", "image": "mythic_hero_gear_chest.png", "fs_value": 38, "tier": "A", "desc": "Choose hero gear (Gen 9)"},
            {"id": "custom_hero_gear_s10", "name": "Custom Gear S10", "image": "mythic_hero_gear_chest.png", "fs_value": 40, "tier": "A", "desc": "Choose hero gear (Gen 10)"},
            {"id": "custom_hero_gear_s11", "name": "Custom Gear S11", "image": "mythic_hero_gear_chest.png", "fs_value": 42, "tier": "A", "desc": "Choose hero gear (Gen 11)"},
            {"id": "custom_hero_gear_s12", "name": "Custom Gear S12", "image": "mythic_hero_gear_chest.png", "fs_value": 44, "tier": "A", "desc": "Choose hero gear (Gen 12)"},
            {"id": "custom_hero_gear_s13", "name": "Custom Gear S13", "image": "mythic_hero_gear_chest.png", "fs_value": 46, "tier": "S", "desc": "Choose hero gear (Gen 13)"},
            {"id": "custom_hero_gear_s14", "name": "Custom Gear S14", "image": "mythic_hero_gear_chest.png", "fs_value": 48, "tier": "S", "desc": "Choose hero gear (Gen 14)"},
            {"id": "custom_hero_gear_s15", "name": "Custom Gear S15", "image": "mythic_hero_gear_chest.png", "fs_value": 50, "tier": "S", "desc": "Choose hero gear (Gen 15 - newest)"},
        ]
    },
    "chief_gear": {
        "label": "Chief Gear & Charms",
        "category": "unique",
        "items": [
            {"id": "hardened_alloy", "name": "Hardened Alloy", "image": "hardened_alloy.png", "fs_value": 0.067, "tier": "C", "desc": "Primary material for chief gear (cheap)"},
            {"id": "polishing_solution", "name": "Polishing Solution", "image": "polishing_solution.png", "fs_value": 6.7, "tier": "B", "desc": "1 Polish = 100 Alloy in value"},
            {"id": "design_plans", "name": "Design Plans", "image": "design_plans.png", "fs_value": 10, "tier": "B", "desc": "Blueprints for Blue+ quality chief gear"},
            {"id": "charm_design", "name": "Charm Designs", "image": "charm_design.png", "fs_value": 22, "tier": "A", "desc": "Primary material for Chief Charm upgrades"},
            {"id": "charm_guide", "name": "Charm Guides", "image": "charm_guide.png", "fs_value": 6.5, "tier": "B", "desc": "Secondary material for Chief Charm upgrades"},
            {"id": "chief_gear_chest", "name": "Chief Gear Chest", "image": "chief_gear_chest.png", "fs_value": 8, "tier": "C", "desc": "Contains chief gear materials"},
        ]
    },
    "currency": {
        "label": "Currency & Premium",
        "category": "currency",
        "items": [
            {"id": "gems", "name": "Gems", "image": "gems.png", "fs_value": 0.033, "tier": "A", "desc": "Premium currency (30 gems = 1 FS)"},
            {"id": "stamina", "name": "Stamina", "image": "stamina.png", "fs_value": 1, "tier": "A", "desc": "Energy for beasts and exploration"},
            {"id": "fire_crystal", "name": "Fire Crystals", "image": "fire_crystal.png", "fs_value": 1.7, "tier": "B", "desc": "Currency for Furnace upgrades (FC1-FC5)"},
            {"id": "vip_xp_10", "name": "VIP XP 10", "image": "vip_points.png", "fs_value": 0.7, "tier": "C", "desc": "10 VIP experience points"},
            {"id": "vip_xp_100", "name": "VIP XP 100", "image": "vip_points.png", "fs_value": 7, "tier": "B", "desc": "100 VIP experience points"},
            {"id": "vip_xp_1000", "name": "VIP XP 1000", "image": "vip_points.png", "fs_value": 70, "tier": "A", "desc": "1000 VIP experience points"},
            {"id": "vip_xp_10000", "name": "VIP XP 10000", "image": "vip_points.png", "fs_value": 700, "tier": "S", "desc": "10000 VIP experience points"},
            {"id": "vip_time", "name": "VIP Time (24h)", "image": "vip_time.png", "fs_value": 8, "tier": "B", "desc": "Grants temporary VIP benefits"},
            {"id": "gold_key", "name": "Gold Keys", "image": "gold_key.png", "fs_value": 50, "tier": "A", "desc": "Opens gold chests for good rewards"},
            {"id": "platinum_key", "name": "Platinum Keys", "image": "platinum_key.png", "fs_value": 17, "tier": "B", "desc": "Opens platinum chests for rare rewards"},
            {"id": "mystery_badge", "name": "Mystery Badges", "image": "mystery_badge.png", "fs_value": 0.1, "tier": "B", "desc": "Event currency for mystery shop"},
        ]
    },
    "war_items": {
        "label": "War & Utility",
        "category": "unique",
        "items": [
            {"id": "advanced_teleport", "name": "Advanced Teleport", "image": "advanced_teleporter.png", "fs_value": 67, "tier": "A", "desc": "Teleport to any location on the map"},
            {"id": "random_teleport", "name": "Random Teleport", "image": "random_teleporter.png", "fs_value": 33, "tier": "B", "desc": "Teleport to random location"},
            {"id": "alliance_teleport", "name": "Alliance Teleport", "image": "alliance_teleporter.png", "fs_value": 67, "tier": "A", "desc": "Teleport near alliance territory"},
            {"id": "transfer_pass", "name": "Transfer Pass", "image": "transfer_pass.png", "fs_value": 100, "tier": "S", "desc": "Transfer to another state"},
            {"id": "march_accelerator_1", "name": "March Accelerator I", "image": "march_accelerator.png", "fs_value": 10, "tier": "B", "desc": "Speeds up march by 50%"},
            {"id": "march_accelerator_2", "name": "March Accelerator II", "image": "march_accelerator_2.png", "fs_value": 20, "tier": "B", "desc": "Speeds up march by 100%"},
            {"id": "counter_recon_2h", "name": "Counter Recon (2hr)", "image": "counter_recon.png", "fs_value": 9, "tier": "C", "desc": "Hide troop info for 2 hours"},
            {"id": "counter_recon_8h", "name": "Counter Recon (8hr)", "image": "counter_recon.png", "fs_value": 35, "tier": "B", "desc": "Hide troop info for 8 hours"},
            {"id": "peace_shield_8h", "name": "Peace Shield (8hr)", "image": "shield.png", "fs_value": 20, "tier": "B", "desc": "Protect city for 8 hours"},
            {"id": "peace_shield_24h", "name": "Peace Shield (24hr)", "image": "shield.png", "fs_value": 50, "tier": "A", "desc": "Protect city for 24 hours"},
            # Emoji items at end for alignment
            {"id": "expedition_recall", "name": "Expedition Recall", "emoji": "↩️", "fs_value": 17, "tier": "B", "desc": "Recall troops from march instantly"},
            {"id": "accessory_contract", "name": "Accessory Contract", "emoji": "📜", "fs_value": 50, "tier": "A", "desc": "General accessory construction contract"},
        ]
    },
    "pets": {
        "label": "Pet Items",
        "category": "unique",
        "items": [
            {"id": "pet_food", "name": "Pet Food", "image": "pet_food.png", "fs_value": 0.024, "tier": "C", "desc": "Nutrient substance for leveling up pets"},
            {"id": "taming_manual", "name": "Taming Manuals", "image": "taming_manual.png", "fs_value": 4, "tier": "B", "desc": "Core material for pet potential advancement"},
            {"id": "energizing_potion", "name": "Energizing Potion", "image": "energizing_potion.png", "fs_value": 14, "tier": "A", "desc": "Extra advancement material for pets (Lv.30+)"},
            {"id": "strengthening_serum", "name": "Strengthening Serum", "image": "strengthening_serum.png", "fs_value": 28, "tier": "A", "desc": "Advanced advancement material (Lv.50+)"},
            {"id": "common_wild_mark", "name": "Common Wild Mark", "image": "common_wild_mark.png", "fs_value": 17, "tier": "B", "desc": "Material for basic pet refinement"},
            {"id": "advanced_wild_mark", "name": "Advanced Wild Mark", "image": "advanced_wild_mark.png", "fs_value": 71, "tier": "S", "desc": "Material for advanced pet refinement. $0.71 each"},
            {"id": "pet_materials_chest", "name": "Pet Materials Chest", "image": "pet_materials_chest.png", "fs_value": 10, "tier": "B", "desc": "Contains random pet advancement materials"},
        ]
    },
    "speedups": {
        "label": "Speedups",
        "category": "speedups",
        "is_speedup_grid": True,
        "columns": {
            "general": {"label": "General", "emoji": "⏱️"},
            "build": {"label": "Build", "emoji": "🔨"},
            "research": {"label": "Research", "emoji": "🔬"},
            "training": {"label": "Training", "emoji": "🪖"},
            "healing": {"label": "Healing", "emoji": "💉"}
        },
        "durations": [
            {"key": "1m", "label": "1 min", "minutes": 1, "color": "#888888"},
            {"key": "5m", "label": "5 min", "minutes": 5, "color": "#27AE60"},
            {"key": "10m", "label": "10 min", "minutes": 10, "color": "#27AE60"},
            {"key": "30m", "label": "30 min", "minutes": 30, "color": "#3498DB"},
            {"key": "1h", "label": "1 hour", "minutes": 60, "color": "#3498DB"},
            {"key": "3h", "label": "3 hour", "minutes": 180, "color": "#9B59B6"},
            {"key": "8h", "label": "8 hour", "minutes": 480, "color": "#E67E22"},
            {"key": "24h", "label": "24 hour", "minutes": 1440, "color": "#FFD700"}
        ],
        "items": [
            # General speedups - 0.24 FS per minute = 14 FS per hour
            {"id": "speed_gen_1m", "name": "General 1m", "type": "general", "duration": "1m", "fs_value": 0.24, "tier": "C"},
            {"id": "speed_gen_5m", "name": "General 5m", "type": "general", "duration": "5m", "fs_value": 1.2, "tier": "C"},
            {"id": "speed_gen_10m", "name": "General 10m", "type": "general", "duration": "10m", "fs_value": 2.4, "tier": "C"},
            {"id": "speed_gen_30m", "name": "General 30m", "type": "general", "duration": "30m", "fs_value": 7, "tier": "B"},
            {"id": "speed_gen_1h", "name": "General 1h", "type": "general", "duration": "1h", "fs_value": 14, "tier": "B"},
            {"id": "speed_gen_3h", "name": "General 3h", "type": "general", "duration": "3h", "fs_value": 42, "tier": "A"},
            {"id": "speed_gen_8h", "name": "General 8h", "type": "general", "duration": "8h", "fs_value": 112, "tier": "A"},
            {"id": "speed_gen_24h", "name": "General 24h", "type": "general", "duration": "24h", "fs_value": 336, "tier": "S"},
            # Build speedups - same rate
            {"id": "speed_build_1m", "name": "Build 1m", "type": "build", "duration": "1m", "fs_value": 0.24, "tier": "C"},
            {"id": "speed_build_5m", "name": "Build 5m", "type": "build", "duration": "5m", "fs_value": 1.2, "tier": "C"},
            {"id": "speed_build_10m", "name": "Build 10m", "type": "build", "duration": "10m", "fs_value": 2.4, "tier": "C"},
            {"id": "speed_build_30m", "name": "Build 30m", "type": "build", "duration": "30m", "fs_value": 7, "tier": "B"},
            {"id": "speed_build_1h", "name": "Build 1h", "type": "build", "duration": "1h", "fs_value": 14, "tier": "B"},
            {"id": "speed_build_3h", "name": "Build 3h", "type": "build", "duration": "3h", "fs_value": 42, "tier": "A"},
            {"id": "speed_build_8h", "name": "Build 8h", "type": "build", "duration": "8h", "fs_value": 112, "tier": "A"},
            {"id": "speed_build_24h", "name": "Build 24h", "type": "build", "duration": "24h", "fs_value": 336, "tier": "S"},
            # Research speedups
            {"id": "speed_research_1m", "name": "Research 1m", "type": "research", "duration": "1m", "fs_value": 0.24, "tier": "C"},
            {"id": "speed_research_5m", "name": "Research 5m", "type": "research", "duration": "5m", "fs_value": 1.2, "tier": "C"},
            {"id": "speed_research_10m", "name": "Research 10m", "type": "research", "duration": "10m", "fs_value": 2.4, "tier": "C"},
            {"id": "speed_research_30m", "name": "Research 30m", "type": "research", "duration": "30m", "fs_value": 7, "tier": "B"},
            {"id": "speed_research_1h", "name": "Research 1h", "type": "research", "duration": "1h", "fs_value": 14, "tier": "B"},
            {"id": "speed_research_3h", "name": "Research 3h", "type": "research", "duration": "3h", "fs_value": 42, "tier": "A"},
            {"id": "speed_research_8h", "name": "Research 8h", "type": "research", "duration": "8h", "fs_value": 112, "tier": "A"},
            {"id": "speed_research_24h", "name": "Research 24h", "type": "research", "duration": "24h", "fs_value": 336, "tier": "S"},
            # Training speedups
            {"id": "speed_train_1m", "name": "Training 1m", "type": "training", "duration": "1m", "fs_value": 0.24, "tier": "C"},
            {"id": "speed_train_5m", "name": "Training 5m", "type": "training", "duration": "5m", "fs_value": 1.2, "tier": "C"},
            {"id": "speed_train_10m", "name": "Training 10m", "type": "training", "duration": "10m", "fs_value": 2.4, "tier": "C"},
            {"id": "speed_train_30m", "name": "Training 30m", "type": "training", "duration": "30m", "fs_value": 7, "tier": "B"},
            {"id": "speed_train_1h", "name": "Training 1h", "type": "training", "duration": "1h", "fs_value": 14, "tier": "B"},
            {"id": "speed_train_3h", "name": "Training 3h", "type": "training", "duration": "3h", "fs_value": 42, "tier": "A"},
            {"id": "speed_train_8h", "name": "Training 8h", "type": "training", "duration": "8h", "fs_value": 112, "tier": "A"},
            {"id": "speed_train_24h", "name": "Training 24h", "type": "training", "duration": "24h", "fs_value": 336, "tier": "S"},
            # Healing speedups - VALUE = 0 (batch healing is free!)
            {"id": "speed_heal_1m", "name": "Healing 1m", "type": "healing", "duration": "1m", "fs_value": 0, "tier": "D"},
            {"id": "speed_heal_5m", "name": "Healing 5m", "type": "healing", "duration": "5m", "fs_value": 0, "tier": "D"},
            {"id": "speed_heal_10m", "name": "Healing 10m", "type": "healing", "duration": "10m", "fs_value": 0, "tier": "D"},
            {"id": "speed_heal_30m", "name": "Healing 30m", "type": "healing", "duration": "30m", "fs_value": 0, "tier": "D"},
            {"id": "speed_heal_1h", "name": "Healing 1h", "type": "healing", "duration": "1h", "fs_value": 0, "tier": "D"},
            {"id": "speed_heal_3h", "name": "Healing 3h", "type": "healing", "duration": "3h", "fs_value": 0, "tier": "D"},
            {"id": "speed_heal_8h", "name": "Healing 8h", "type": "healing", "duration": "8h", "fs_value": 0, "tier": "D"},
            {"id": "speed_heal_24h", "name": "Healing 24h", "type": "healing", "duration": "24h", "fs_value": 0, "tier": "D"},
        ]
    },
    "late_game": {
        "label": "Late Game (FC5+)",
        "category": "unique",
        "items": [
            {"id": "expert_sigil", "name": "Expert Sigils", "image": "common_expert_sigil.png", "fs_value": 20, "tier": "A", "desc": "Material for hero expertise trees"},
            {"id": "lunar_amber", "name": "Lunar Amber", "image": "lunar_amber.png", "fs_value": 35, "tier": "A", "desc": "Material for Red+ quality chief gear"},
            {"id": "charm_secrets", "name": "Charm Secrets", "image": "charm_secrets.png", "fs_value": 50, "tier": "S", "desc": "Rare material for L12+ charm upgrades"},
            {"id": "refined_fire_crystal", "name": "Refined FC", "image": "refined_fire_crystal.png", "fs_value": 30, "tier": "A", "desc": "Purified FC for higher Furnace levels (FC6+)"},
            {"id": "mythic_decoration", "name": "Mythic Decoration Component", "image": "mythic_decoration_component.png", "fs_value": 56, "tier": "A", "desc": "Material for hero decoration upgrades"},
        ]
    },
    "boosts": {
        "label": "Boosts & Buffs",
        "category": "unique",
        "items": [
            # Troop Attack Boost - 2hr and 12hr
            {"id": "troop_attack_boost_2h", "name": "Troop Attack Boost (2hr)", "image": "troops_attack_up.png", "fs_value": 42, "tier": "B", "desc": "Increases troop attack for 2 hours"},
            {"id": "troop_attack_boost_12h", "name": "Troop Attack Boost (12hr)", "image": "troops_attack_up.png", "fs_value": 167, "tier": "A", "desc": "Increases troop attack for 12 hours"},
            # Troop Defense Boost - 2hr and 12hr
            {"id": "troop_defense_boost_2h", "name": "Troop Defense Boost (2hr)", "image": "troops_defense_up.png", "fs_value": 42, "tier": "B", "desc": "Increases troop defense for 2 hours"},
            {"id": "troop_defense_boost_12h", "name": "Troop Defense Boost (12hr)", "image": "troops_defense_up.png", "fs_value": 167, "tier": "A", "desc": "Increases troop defense for 12 hours"},
            # Enemy Attack Down - 2hr and 12hr
            {"id": "enemy_attack_down_2h", "name": "Enemy Attack Down (2hr)", "image": "enemy_attack_down.png", "fs_value": 42, "tier": "B", "desc": "Reduces enemy attack for 2 hours"},
            {"id": "enemy_attack_down_12h", "name": "Enemy Attack Down (12hr)", "image": "enemy_attack_down.png", "fs_value": 167, "tier": "A", "desc": "Reduces enemy attack for 12 hours"},
            # Enemy Defense Down - 2hr and 12hr
            {"id": "enemy_defense_down_2h", "name": "Enemy Defense Down (2hr)", "image": "enemy_defense_down.png", "fs_value": 42, "tier": "B", "desc": "Reduces enemy defense for 2 hours"},
            {"id": "enemy_defense_down_12h", "name": "Enemy Defense Down (12hr)", "image": "enemy_defense_down.png", "fs_value": 167, "tier": "A", "desc": "Reduces enemy defense for 12 hours"},
            # Gathering Speed - 8hr and 24hr
            {"id": "gathering_speed_boost_8h", "name": "Gathering Speed Boost (8hr)", "image": "gathering_speed_boost.png", "fs_value": 4, "tier": "C", "desc": "Increases gathering speed for 8 hours"},
            {"id": "gathering_speed_boost_24h", "name": "Gathering Speed Boost (24hr)", "image": "gathering_speed_boost.png", "fs_value": 10, "tier": "C", "desc": "Increases gathering speed for 24 hours"},
            # Training Capacity - 2hr only
            {"id": "training_capacity_boost_2h", "name": "Training Capacity Boost (2hr)", "image": "training_capacity_boost.png", "fs_value": 50, "tier": "B", "desc": "Increases troop training capacity for 2 hours"},
            # Deployment/Rally - assuming similar to training
            {"id": "deployment_capacity_boost_2h", "name": "Deployment Capacity Boost (2hr)", "image": "deployment_capacity_boost.png", "fs_value": 50, "tier": "B", "desc": "Increases march deployment capacity for 2 hours"},
            {"id": "deployment_capacity_boost_12h", "name": "Deployment Capacity Boost (12hr)", "image": "deployment_capacity_boost.png", "fs_value": 167, "tier": "A", "desc": "Increases march deployment capacity for 12 hours"},
            {"id": "rally_boost_2h", "name": "Rally Capacity Boost (2hr)", "image": "rally_boost.png", "fs_value": 50, "tier": "B", "desc": "Increases rally troop capacity for 2 hours"},
            {"id": "rally_boost_12h", "name": "Rally Capacity Boost (12hr)", "image": "rally_boost.png", "fs_value": 167, "tier": "A", "desc": "Increases rally troop capacity for 12 hours"},
            # Expedition Boost
            {"id": "expedition_boost", "name": "Expedition Boost", "image": "expedition_boost.png", "fs_value": 10, "tier": "C", "desc": "Boosts expedition rewards or speed"},
        ]
    },
    "resources": {
        "label": "Resources (Filler)",
        "category": "resources",
        "is_resource_grid": True,
        "columns": {
            "meat": {"label": "Meat", "image": "meat.png"},
            "wood": {"label": "Wood", "image": "wood.png"},
            "coal": {"label": "Coal", "image": "coal.png"},
            "iron": {"label": "Iron", "image": "iron.png"},
            "steel": {"label": "Steel", "image": "steel.png"}
        },
        "denominations": [
            {"key": "100", "label": "100", "multiplier": 0.01},
            {"key": "1k", "label": "1k", "multiplier": 0.1},
            {"key": "10k", "label": "10k", "multiplier": 1},
            {"key": "100k", "label": "100k", "multiplier": 10},
            {"key": "1m", "label": "1M", "multiplier": 100}
        ],
        "items": [
            # Meat - base value 0.054 FS per 10k
            {"id": "meat_100", "name": "Meat 100", "type": "meat", "denom": "100", "image": "meat.png", "fs_value": 0.00054, "tier": "D"},
            {"id": "meat_1k", "name": "Meat 1k", "type": "meat", "denom": "1k", "image": "meat.png", "fs_value": 0.0054, "tier": "D"},
            {"id": "meat_10k", "name": "Meat 10k", "type": "meat", "denom": "10k", "image": "meat.png", "fs_value": 0.054, "tier": "D"},
            {"id": "meat_100k", "name": "Meat 100k", "type": "meat", "denom": "100k", "image": "meat.png", "fs_value": 0.54, "tier": "D"},
            {"id": "meat_1m", "name": "Meat 1M", "type": "meat", "denom": "1m", "image": "meat.png", "fs_value": 5.4, "tier": "D"},
            # Wood - base value 0.054 FS per 10k
            {"id": "wood_100", "name": "Wood 100", "type": "wood", "denom": "100", "image": "wood.png", "fs_value": 0.00054, "tier": "D"},
            {"id": "wood_1k", "name": "Wood 1k", "type": "wood", "denom": "1k", "image": "wood.png", "fs_value": 0.0054, "tier": "D"},
            {"id": "wood_10k", "name": "Wood 10k", "type": "wood", "denom": "10k", "image": "wood.png", "fs_value": 0.054, "tier": "D"},
            {"id": "wood_100k", "name": "Wood 100k", "type": "wood", "denom": "100k", "image": "wood.png", "fs_value": 0.54, "tier": "D"},
            {"id": "wood_1m", "name": "Wood 1M", "type": "wood", "denom": "1m", "image": "wood.png", "fs_value": 5.4, "tier": "D"},
            # Coal - base value 0.27 FS per 10k (5x meat/wood)
            {"id": "coal_100", "name": "Coal 100", "type": "coal", "denom": "100", "image": "coal.png", "fs_value": 0.0027, "tier": "D"},
            {"id": "coal_1k", "name": "Coal 1k", "type": "coal", "denom": "1k", "image": "coal.png", "fs_value": 0.027, "tier": "D"},
            {"id": "coal_10k", "name": "Coal 10k", "type": "coal", "denom": "10k", "image": "coal.png", "fs_value": 0.27, "tier": "D"},
            {"id": "coal_100k", "name": "Coal 100k", "type": "coal", "denom": "100k", "image": "coal.png", "fs_value": 2.7, "tier": "D"},
            {"id": "coal_1m", "name": "Coal 1M", "type": "coal", "denom": "1m", "image": "coal.png", "fs_value": 27, "tier": "D"},
            # Iron - base value 1.08 FS per 10k (4x coal)
            {"id": "iron_100", "name": "Iron 100", "type": "iron", "denom": "100", "image": "iron.png", "fs_value": 0.0108, "tier": "D"},
            {"id": "iron_1k", "name": "Iron 1k", "type": "iron", "denom": "1k", "image": "iron.png", "fs_value": 0.108, "tier": "D"},
            {"id": "iron_10k", "name": "Iron 10k", "type": "iron", "denom": "10k", "image": "iron.png", "fs_value": 1.08, "tier": "D"},
            {"id": "iron_100k", "name": "Iron 100k", "type": "iron", "denom": "100k", "image": "iron.png", "fs_value": 10.8, "tier": "D"},
            {"id": "iron_1m", "name": "Iron 1M", "type": "iron", "denom": "1m", "image": "iron.png", "fs_value": 108, "tier": "D"},
            # Steel - base value 5.6 FS per 1k (special - refined iron)
            {"id": "steel_100", "name": "Steel 100", "type": "steel", "denom": "100", "image": "steel.png", "fs_value": 0.56, "tier": "C"},
            {"id": "steel_1k", "name": "Steel 1k", "type": "steel", "denom": "1k", "image": "steel.png", "fs_value": 5.6, "tier": "C"},
            {"id": "steel_10k", "name": "Steel 10k", "type": "steel", "denom": "10k", "image": "steel.png", "fs_value": 56, "tier": "C"},
            {"id": "steel_100k", "name": "Steel 100k", "type": "steel", "denom": "100k", "image": "steel.png", "fs_value": 560, "tier": "B"},
            {"id": "steel_1m", "name": "Steel 1M", "type": "steel", "denom": "1m", "image": "steel.png", "fs_value": 5600, "tier": "A"},
        ]
    }
}

TIER_COLORS = {
    "S": "#FFD700",  # Gold
    "A": "#9B59B6",  # Purple
    "B": "#3498DB",  # Blue
    "C": "#95A5A6",  # Gray
    "D": "#E74C3C",  # Red (filler)
}


def get_image_base64(image_name: str) -> str:
    """Get base64 encoded image for inline display."""
    if not image_name:
        return None
    image_path = ITEMS_DIR / image_name
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def calculate_pack_analysis(quantities: dict, price: float, farmer_mode: bool = False) -> dict:
    """Calculate pack value from item quantities. Values in Frost Stars (1 FS = $0.01)."""
    total_value = 0
    resource_value = 0
    currency_value = 0
    speedup_value = 0
    unique_value = 0
    filler_value = 0  # Resources + Healing speedups
    breakdown = []

    for cat_key, cat_data in PACK_ITEMS.items():
        category_type = cat_data.get("category", "unique")

        for item in cat_data["items"]:
            qty = quantities.get(item["id"], 0)
            if qty > 0:
                fs_val = item.get("fs_value", item.get("gem_value", 0))
                base_value = qty * fs_val

                # In farmer mode, resources are worth $0
                if farmer_mode and category_type == "resources":
                    value = 0
                else:
                    value = base_value

                total_value += value

                # Categorize
                is_filler = item["tier"] == "D" or category_type == "resources"
                if category_type == "resources":
                    resource_value += value
                    filler_value += value
                elif category_type == "currency":
                    currency_value += value
                elif category_type == "speedups":
                    speedup_value += value
                    if item["tier"] == "D":  # Healing speedups
                        filler_value += value
                else:
                    unique_value += value

                breakdown.append({
                    "name": item["name"],
                    "image": item.get("image"),
                    "emoji": item.get("emoji"),
                    "desc": item.get("desc", item["name"]),
                    "quantity": qty,
                    "tier": item["tier"],
                    "tier_color": TIER_COLORS.get(item["tier"], "#666"),
                    "value": value,
                    "base_value": base_value,  # Value before farmer mode adjustment
                    "is_filler": is_filler,
                    "category": category_type
                })

    # Sort by value descending
    breakdown.sort(key=lambda x: -x["value"])

    # Calculate percentages and metrics
    price_fs = price * 100  # Convert $ to Frost Stars
    filler_pct = (filler_value / total_value * 100) if total_value > 0 else 0
    value_efficiency = (total_value / price_fs * 100) if price_fs > 0 else 0

    return {
        "total_value": total_value,
        "total_value_dollars": total_value / 100,
        "resource_value": resource_value,
        "currency_value": currency_value,
        "speedup_value": speedup_value,
        "unique_value": unique_value,
        "filler_value": filler_value,
        "filler_pct": filler_pct,
        "value_efficiency": value_efficiency,
        "breakdown": breakdown,
        "price": price,
        "price_fs": price_fs,
        "farmer_mode": farmer_mode
    }


def render_analysis_section(analysis: dict):
    """Render the analysis results with dollar values and category breakdown."""
    if not analysis or analysis["total_value"] == 0:
        st.markdown("""
        <div style="background:rgba(74,144,217,0.1);border:1px dashed rgba(74,144,217,0.3);
                    border-radius:12px;padding:30px;text-align:center;color:#888;">
            <div style="font-size:48px;margin-bottom:10px;">📦</div>
            <div>Enter item quantities below to see analysis</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Calculate derived values
    total_dollars = analysis["total_value_dollars"]
    efficiency = analysis["value_efficiency"]
    filler_pct = analysis["filler_pct"]
    farmer_mode = analysis.get("farmer_mode", False)

    # Color based on efficiency (100% = break even)
    if efficiency >= 100:
        eff_color = "#2ECC71"
        eff_label = "Good Value"
    elif efficiency >= 70:
        eff_color = "#F1C40F"
        eff_label = "Fair Value"
    else:
        eff_color = "#E74C3C"
        eff_label = "Poor Value"

    filler_warning = " (Heavy filler!)" if filler_pct > 50 else ""

    # Main value card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(74,144,217,0.2),rgba(46,90,140,0.3));
                border-radius:12px;padding:20px;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px;">
            <div style="text-align:center;flex:1;min-width:120px;">
                <div style="font-size:28px;font-weight:bold;color:#2ECC71;">${total_dollars:.2f}</div>
                <div style="color:#B8D4E8;font-size:12px;">Actual Value</div>
            </div>
            <div style="text-align:center;flex:1;min-width:120px;">
                <div style="font-size:28px;font-weight:bold;color:#E8F4F8;">${analysis['price']:.2f}</div>
                <div style="color:#B8D4E8;font-size:12px;">Pack Price</div>
            </div>
            <div style="text-align:center;flex:1;min-width:120px;">
                <div style="font-size:28px;font-weight:bold;color:{eff_color};">{efficiency:.0f}%</div>
                <div style="color:#B8D4E8;font-size:12px;">{eff_label}</div>
            </div>
            <div style="text-align:center;flex:1;min-width:120px;">
                <div style="font-size:28px;font-weight:bold;color:#E74C3C;">{filler_pct:.0f}%</div>
                <div style="color:#B8D4E8;font-size:12px;">Filler{filler_warning}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Category breakdown bar
    total = analysis["total_value"]
    if total > 0:
        currency_pct = (analysis["currency_value"] / total * 100)
        unique_pct = (analysis["unique_value"] / total * 100)
        speedup_pct = (analysis["speedup_value"] / total * 100)
        resource_pct = (analysis["resource_value"] / total * 100)

        st.markdown("**Value Breakdown by Category:**")
        st.markdown(f"""
        <div style="display:flex;height:24px;border-radius:6px;overflow:hidden;margin:8px 0 16px 0;">
            <div style="width:{currency_pct}%;background:#FFD700;" title="Currency: {currency_pct:.1f}%"></div>
            <div style="width:{unique_pct}%;background:#9B59B6;" title="Unique Items: {unique_pct:.1f}%"></div>
            <div style="width:{speedup_pct}%;background:#3498DB;" title="Speedups: {speedup_pct:.1f}%"></div>
            <div style="width:{resource_pct}%;background:#E74C3C;" title="Resources: {resource_pct:.1f}%"></div>
        </div>
        <div style="display:flex;justify-content:center;gap:20px;font-size:11px;color:#B8D4E8;margin-bottom:16px;">
            <span><span style="color:#FFD700;">●</span> Currency {currency_pct:.0f}%</span>
            <span><span style="color:#9B59B6;">●</span> Unique {unique_pct:.0f}%</span>
            <span><span style="color:#3498DB;">●</span> Speedups {speedup_pct:.0f}%</span>
            <span><span style="color:#E74C3C;">●</span> Resources {resource_pct:.0f}%</span>
        </div>
        """, unsafe_allow_html=True)

        if farmer_mode:
            st.caption("*Farmer Mode: Resources valued at $0*")

    # Breakdown table
    if analysis["breakdown"]:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Item Breakdown**")
            for item in analysis["breakdown"][:10]:  # Top 10 items
                pct = (item["value"] / analysis["total_value"] * 100) if analysis["total_value"] > 0 else 0
                tooltip = item.get("desc") or item["name"]
                item_dollars = item["value"] / 100  # Convert FS to dollars

                # Get image or emoji (use 'or' to handle explicit None)
                img_b64 = get_image_base64(item.get("image"))
                if img_b64:
                    icon_html = f'<img src="data:image/png;base64,{img_b64}" width="20" height="20" style="vertical-align:middle;margin-right:6px;">'
                else:
                    emoji = item.get("emoji") or "📦"
                    icon_html = f'<span style="margin-right:6px;">{emoji}</span>'

                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:6px 10px;margin:2px 0;background:rgba(0,0,0,0.2);border-radius:4px;
                            border-left:3px solid {item['tier_color']};" title="{tooltip}">
                    <span>{icon_html}{item['name']}</span>
                    <span><span style="font-weight:bold;color:#E8F4F8;font-size:14px;">x{item['quantity']:,}</span> <span style="color:#888;">→</span> <span style="color:{item['tier_color']}">${item_dollars:.2f}</span> <span style="color:#666;">({pct:.1f}%)</span></span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("**Verdict**")

            # Get S and A tier items
            high_value = [i for i in analysis["breakdown"] if i["tier"] in ["S", "A"] and not i["is_filler"]]

            if high_value:
                st.success(f"Good: {', '.join(i['name'] for i in high_value[:3])}")
            else:
                st.error("No S/A tier items")

            if filler_pct > 50:
                st.warning(f"{filler_pct:.0f}% is filler")

            if efficiency >= 100:
                st.info("Good value per $")
            elif efficiency < 70:
                st.error("Poor value")


def render_item_grid(category_key: str, category_data: dict, quantities: dict):
    """Render a grid of items with quantity inputs."""
    items = category_data["items"]

    # Determine column count based on item count
    cols_per_row = min(len(items), 5)
    rows = (len(items) + cols_per_row - 1) // cols_per_row

    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            item_idx = row * cols_per_row + col_idx
            if item_idx >= len(items):
                break

            item = items[item_idx]
            with col:
                # Item header with image or emoji (larger, no tier badge)
                img_b64 = get_image_base64(item.get("image"))
                tooltip = item.get("desc", item["name"])

                if img_b64:
                    icon_html = f'<img src="data:image/png;base64,{img_b64}" width="48" height="48" style="border-radius:6px;cursor:help;" title="{tooltip}">'
                else:
                    icon_html = f'<span style="font-size:40px;cursor:help;" title="{tooltip}">{item.get("emoji", "📦")}</span>'

                st.markdown(f"""
                <div style="text-align:center;margin-bottom:4px;" title="{tooltip}">
                    {icon_html}
                </div>
                <div style="text-align:center;font-size:11px;color:#B8D4E8;margin-bottom:4px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{tooltip}">
                    {item['name']}
                </div>
                """, unsafe_allow_html=True)

                # Quantity input
                qty = st.number_input(
                    item["name"],
                    min_value=0,
                    value=quantities.get(item["id"], 0),
                    key=f"qty_{item['id']}",
                    label_visibility="collapsed"
                )
                quantities[item["id"]] = qty


def render_speedup_grid(category_data: dict, quantities: dict):
    """Render speedups in a grid with columns by type and rows by duration."""
    columns_def = category_data["columns"]
    durations = category_data["durations"]
    items = category_data["items"]

    # Build lookup: items_by[type][duration] = item
    items_by = {}
    for item in items:
        t = item["type"]
        d = item["duration"]
        if t not in items_by:
            items_by[t] = {}
        items_by[t][d] = item

    # Column headers
    col_keys = list(columns_def.keys())
    header_cols = st.columns([1] + [1] * len(col_keys))

    with header_cols[0]:
        st.markdown("**Duration**")

    for i, col_key in enumerate(col_keys):
        with header_cols[i + 1]:
            col_info = columns_def[col_key]
            st.markdown(f"**{col_info['emoji']} {col_info['label']}**")

    # Rows by duration
    for dur in durations:
        dur_key = dur["key"]
        dur_label = dur["label"]
        dur_color = dur.get("color", "#B8D4E8")

        row_cols = st.columns([1] + [1] * len(col_keys))

        with row_cols[0]:
            st.markdown(f"<div style='padding-top:8px;color:{dur_color};font-weight:bold;'>{dur_label}</div>", unsafe_allow_html=True)

        for i, col_key in enumerate(col_keys):
            with row_cols[i + 1]:
                item = items_by.get(col_key, {}).get(dur_key)
                if item:
                    qty = st.number_input(
                        item["name"],
                        min_value=0,
                        value=quantities.get(item["id"], 0),
                        key=f"qty_{item['id']}",
                        label_visibility="collapsed"
                    )
                    quantities[item["id"]] = qty
                else:
                    st.markdown("")  # Empty cell


def render_resource_grid(category_data: dict, quantities: dict):
    """Render resources in a grid with columns by type and rows by denomination."""
    columns_def = category_data["columns"]
    denominations = category_data["denominations"]
    items = category_data["items"]

    # Build lookup: items_by[type][denom] = item
    items_by = {}
    for item in items:
        t = item["type"]
        d = item["denom"]
        if t not in items_by:
            items_by[t] = {}
        items_by[t][d] = item

    # Column headers with images
    col_keys = list(columns_def.keys())
    header_cols = st.columns([1] + [1] * len(col_keys))

    with header_cols[0]:
        st.markdown("**Amount**")

    for i, col_key in enumerate(col_keys):
        with header_cols[i + 1]:
            col_info = columns_def[col_key]
            img_b64 = get_image_base64(col_info.get("image"))
            if img_b64:
                st.markdown(f"""
                <div style="text-align:center;">
                    <img src="data:image/png;base64,{img_b64}" width="24" height="24" style="vertical-align:middle;">
                    <span style="font-weight:bold;margin-left:4px;">{col_info['label']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"**{col_info['label']}**")

    # Rows by denomination
    denom_colors = {
        "100": "#888888",
        "1k": "#27AE60",
        "10k": "#3498DB",
        "100k": "#9B59B6",
        "1m": "#FFD700"
    }

    for denom in denominations:
        denom_key = denom["key"]
        denom_label = denom["label"]
        denom_color = denom_colors.get(denom_key, "#B8D4E8")

        row_cols = st.columns([1] + [1] * len(col_keys))

        with row_cols[0]:
            st.markdown(f"<div style='padding-top:8px;color:{denom_color};font-weight:bold;'>{denom_label}</div>", unsafe_allow_html=True)

        for i, col_key in enumerate(col_keys):
            with row_cols[i + 1]:
                item = items_by.get(col_key, {}).get(denom_key)
                if item:
                    qty = st.number_input(
                        item["name"],
                        min_value=0,
                        value=quantities.get(item["id"], 0),
                        key=f"qty_{item['id']}",
                        label_visibility="collapsed"
                    )
                    quantities[item["id"]] = qty
                else:
                    st.markdown("")  # Empty cell


# =============================================================================
# MAIN PAGE
# =============================================================================

st.markdown("# Pack Value Analyzer")
st.markdown("Cut through inflated % values. See what you're *actually* paying for.")

# Initialize session state
if "pack_quantities" not in st.session_state:
    st.session_state.pack_quantities = {}  # Accumulated pack contents
if "farmer_mode" not in st.session_state:
    st.session_state.farmer_mode = False

# Valuation Settings (always visible)
st.session_state.farmer_mode = st.checkbox(
    "I'm a resource farmer (set resources to $0)",
    value=st.session_state.farmer_mode,
    help="If you actively gather, mine, and farm resources, they're essentially free for you"
)
if st.session_state.farmer_mode:
    st.info("**Farmer Mode ON:** Resources (Meat, Wood, Coal, Iron, Steel) valued at $0. Only counting items you can't farm.")

st.markdown("""
**The Fluff Problem:** Packs bundle items together, making specific items feel more valuable than they are.

For example, if you only want Essence Stones:
- A \\$4.99 pack contains ~\\$0.22 worth of Essence Stones (10 stones x \\$0.022 each)
- That's only **4.4%** of the pack - you're paying a **23x markup** for what you actually want!
""")

st.markdown("---")

# =============================================================================
# ANALYSIS SECTION (TOP)
# =============================================================================
# Price selector - compact
col_price, col_spacer = st.columns([1, 9])
with col_price:
    price = st.selectbox("Pack Price", options=PRICE_OPTIONS, index=3, format_func=lambda x: f"${x:.2f}")

analysis = calculate_pack_analysis(st.session_state.pack_quantities, price, st.session_state.farmer_mode)
render_analysis_section(analysis)

st.markdown("---")

# =============================================================================
# ITEM ENTRY SECTION (BOTTOM)
# =============================================================================
# Form for Enter key support (clear_on_submit resets inputs after adding)
with st.form("pack_entry_form", clear_on_submit=True):
    # Header with Add and Clear buttons
    col_header, col_add, col_clear = st.columns([3, 1, 1])
    with col_header:
        st.markdown("### Enter Pack Contents")
    with col_add:
        submitted = st.form_submit_button("Add to Pack", type="primary", use_container_width=True)
    with col_clear:
        clear_clicked = st.form_submit_button("Clear Pack", use_container_width=True)

    # Tabs for item categories
    tab_names = [cat_data["label"] for cat_data in PACK_ITEMS.values()]
    tabs = st.tabs(tab_names)

    input_quantities = {}

    for tab, (cat_key, cat_data) in zip(tabs, PACK_ITEMS.items()):
        with tab:
            if cat_data.get("is_speedup_grid"):
                render_speedup_grid(cat_data, input_quantities)
            elif cat_data.get("is_resource_grid"):
                render_resource_grid(cat_data, input_quantities)
            else:
                render_item_grid(cat_key, cat_data, input_quantities)

if submitted:
    # Add all non-zero quantities to pack
    for item_id, qty in input_quantities.items():
        if qty > 0:
            current = st.session_state.pack_quantities.get(item_id, 0)
            st.session_state.pack_quantities[item_id] = current + qty
    st.rerun()

if clear_clicked:
    st.session_state.pack_quantities = {}
    st.rerun()

# Tips
st.markdown("---")
with st.expander("💡 Understanding Pack Value"):
    st.markdown("""
    **Item Tiers:**
    - **S Tier** (Gold): Mithril (\\$1.41), Advanced Wild Marks (\\$0.71), 24h Speedups - premium items
    - **A Tier** (Purple): Essence Stones (\\$0.22), Gold Keys (\\$0.50), Gems - solid value
    - **B Tier** (Blue): Hourly speedups (\\$0.14), Manuals, Charm Designs - useful but common
    - **C Tier** (Gray): Small speedups, Steel, Hero XP - low value
    - **D Tier** (Red): Resources, Healing speedups - FILLER (free for active players!)

    **Value Efficiency:**
    - **100%+** = Actual value exceeds price (good deal)
    - **70-99%** = Fair value, buy if you need the items
    - **Below 70%** = Poor value, consider skipping

    **The Fluff Problem:**
    Packs bundle items to inflate "value". Example: A \\$4.99 pack might show "500% VALUE"
    but if you only want Essence Stones, you're paying \\$4.99 for ~\\$0.22 worth of stones (4.4%).
    That's a **23x markup** on what you actually want!

    **Farmer Mode:**
    Active players gather/mine resources constantly. If you have 800M Meat in storage,
    the resources in packs have zero practical value to you. Enable Farmer Mode to see
    what you're really paying for.
    """)

# Close database session
db.close()
