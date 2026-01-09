"""
Item Guide - Reference for all backpack items.
Shows what each item is, where to get it, and what it's used for.
"""

import streamlit as st
from pathlib import Path
import sys
import base64

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Item images directory
ITEMS_DIR = PROJECT_ROOT / "assets" / "items"

# Item data organized by category
ITEM_DATA = {
    "Resources": [
        {"id": "gems", "name": "Gems", "image": "gems.png", "description": "Premium currency for purchases and speedups", "sources": "Daily rewards, Events, Packs, Achievements", "uses": "Lucky Wheel, Instant finish, VIP shop, Refreshes"},
        {"id": "meat", "name": "Meat", "image": "meat.png", "description": "Basic resource for troop training", "sources": "Hunting zones, Resource tiles, Chests", "uses": "Training troops, Troop upkeep"},
        {"id": "wood", "name": "Wood", "image": "wood.png", "description": "Basic resource for construction", "sources": "Lumber mills, Resource tiles, Chests", "uses": "Building upgrades, Research"},
        {"id": "coal", "name": "Coal", "image": "coal.png", "description": "Resource for advanced construction", "sources": "Coal mines, Resource tiles, Chests", "uses": "Building upgrades, Research"},
        {"id": "iron", "name": "Iron", "image": "iron.png", "description": "Rare resource for high-level upgrades", "sources": "Iron mines, Resource tiles, Events", "uses": "Advanced buildings, Elite troops"},
        {"id": "steel", "name": "Steel", "image": "steel.png", "description": "Refined iron for advanced uses", "sources": "Steel production, Events, Chests", "uses": "High-tier construction, Research"},
        {"id": "fire_crystal", "name": "Fire Crystal", "image": "fire_crystal.png", "description": "Currency for Furnace upgrades (FC1-FC5)", "sources": "FC mines, Events, Packs, Bear Trap, Daily missions", "uses": "Furnace building upgrades"},
        {"id": "fire_crystal_shard", "name": "Fire Crystal Shard", "image": "fire_crystal_shard.png", "description": "Component for crafting Fire Crystals", "sources": "Daily missions, Intel missions, Events", "uses": "Convert to Fire Crystals in Crystal Lab"},
        {"id": "refined_fire_crystal", "name": "Refined Fire Crystal", "image": "refined_fire_crystal.png", "description": "Purified FC for higher Furnace levels (FC6+)", "sources": "Crystal Lab Super Refinement, Events, Packs", "uses": "High-level Furnace upgrades (FC6-FC10)"},
        {"id": "stamina", "name": "Chief Stamina", "image": "stamina.png", "description": "Energy for beasts and exploration", "sources": "Natural regen (1/6min), VIP shop, Events", "uses": "Beast attacks, Exploration battles"},
    ],
    "Hero Shards": [
        {"id": "legendary_hero_shard", "name": "Legendary Shard", "image": "legendary_hero_shard.png", "description": "Universal shard for any legendary hero", "sources": "Lucky Wheel, Events, Packs, Hero Hall", "uses": "Unlock/upgrade any legendary hero"},
        {"id": "epic_hero_shard", "name": "Epic Shard", "image": "epic_hero_shard.png", "description": "Universal shard for epic heroes", "sources": "Hero Hall, Events, Exploration", "uses": "Unlock/upgrade any epic hero"},
        {"id": "rare_hero_shard", "name": "Rare Shard", "image": "rare_hero_shard.png", "description": "Universal shard for rare heroes", "sources": "Exploration, Daily rewards, Events", "uses": "Unlock/upgrade any rare hero"},
        {"id": "hero_xp", "name": "Hero XP", "image": "hero_xp.png", "description": "Experience points to level up heroes", "sources": "Exploration, Combat Manuals, Events", "uses": "Leveling up heroes"},
        {"id": "mythic_exploration_manual", "name": "Mythic Exploration Manual", "image": "mythic_exploration_manual.png", "description": "Upgrades exploration skills for Mythic heroes", "sources": "Lighthouse Intel, Exploration bosses, VIP Shop", "uses": "Mythic hero exploration skills"},
        {"id": "epic_exploration_manual", "name": "Epic Exploration Manual", "image": "epic_exploration_manual.png", "description": "Upgrades exploration skills for Epic heroes", "sources": "Lighthouse Intel, Exploration stages, VIP Shop", "uses": "Epic hero exploration skills"},
        {"id": "rare_exploration_manual", "name": "Rare Exploration Manual", "image": "rare_exploration_manual.png", "description": "Upgrades exploration skills for Rare heroes", "sources": "Exploration stages, Daily play, Events", "uses": "Rare hero exploration skills"},
        {"id": "mythic_expedition_manual", "name": "Mythic Expedition Manual", "image": "mythic_expedition_manual.png", "description": "Upgrades expedition skills for Mythic heroes", "sources": "Lighthouse Intel, VIP Shop, Events (rare)", "uses": "Mythic hero expedition skills"},
        {"id": "epic_expedition_manual", "name": "Epic Expedition Manual", "image": "epic_expedition_manual.png", "description": "Upgrades expedition skills for Epic heroes", "sources": "Lighthouse Intel, Exploration, VIP Shop", "uses": "Epic hero expedition skills"},
        {"id": "rare_expedition_manual", "name": "Rare Expedition Manual", "image": "rare_expedition_manual.png", "description": "Upgrades expedition skills for Rare heroes", "sources": "Exploration stages, Events", "uses": "Rare hero expedition skills"},
    ],
    "Hero Gear Materials": [
        {"id": "essence_stone", "name": "Essence Stone", "image": "essence_stone.png", "description": "Critical for Mythic gear mastery. Very valuable", "sources": "Mystery Shop, Arena Shop, Hero gear recycling", "uses": "Mythic Hero Gear Mastery (FC20+)"},
        {"id": "mithril", "name": "Mithril", "image": "mithril.png", "description": "Rare material for Legendary gear empowerment", "sources": "Arena Shop (3/season), Frostdragon event, Packs", "uses": "Empower Legendary Hero Gear at 20/40/60/80/100"},
        {"id": "xp_component", "name": "Enhancement XP Component", "image": "xp_component.png", "description": "Primary material for enhancing hero gear stats", "sources": "Events, Tundra Trading, Daily/Intel missions", "uses": "Leveling up Hero Gear (FC15+)"},
    ],
    "Chief Gear Materials": [
        {"id": "hardened_alloy", "name": "Hardened Alloy", "image": "hardened_alloy.png", "description": "Primary material for chief gear upgrades", "sources": "Polar Terror rallies (Lv.3+), Beast hunts (22+), Crazy Joe", "uses": "Chief gear crafting/upgrades"},
        {"id": "polishing_solution", "name": "Polishing Solution", "image": "polishing_solution.png", "description": "Secondary material for chief gear refinement", "sources": "Crazy Joe, Frostfire Mine, Championship Shop", "uses": "Chief gear refinement"},
        {"id": "design_plans", "name": "Design Plans", "image": "design_plans.png", "description": "Blueprints for Blue+ quality chief gear", "sources": "Alliance Championship, Foundry, Power Region", "uses": "Upgrading chief gear (Blue+)"},
        {"id": "lunar_amber", "name": "Lunar Amber", "image": "lunar_amber.png", "description": "Material for Red+ quality chief gear", "sources": "Material Exchanges, Premium packs, Events", "uses": "High-tier chief gear (Red+)"},
        {"id": "charm_secrets", "name": "Charm Secrets", "image": "charm_secrets.png", "description": "Rare material for L12+ charm upgrades (Gen 7 state required)", "sources": "Events, Material Exchange, Premium packs", "uses": "Chief Charm upgrades L12-L16"},
        {"id": "charm_design", "name": "Charm Design", "image": "charm_design.png", "description": "Primary material for Chief Charm upgrades", "sources": "Events, Giant Elk pet, Packs, Tundra Trading", "uses": "Chief Charm upgrades (all levels)"},
        {"id": "charm_guide", "name": "Charm Guide", "image": "charm_guide.png", "description": "Secondary material for Chief Charm upgrades", "sources": "Alliance Shop, Events, Foundry, Giant Elk pet", "uses": "Chief Charm upgrades (all levels)"},
    ],
    "Pet Materials": [
        {"id": "pet_food", "name": "Pet Food", "image": "pet_food.png", "description": "Nutrient substance for leveling up pets", "sources": "Pet adventures (10 stamina), Beast Cage activities", "uses": "Feeding pets to gain XP"},
        {"id": "taming_manual", "name": "Taming Manual", "image": "taming_manual.png", "description": "Core material for pet potential advancement", "sources": "Pet adventures, Lighthouse Intel missions", "uses": "Pet advancement (all levels)"},
        {"id": "energizing_potion", "name": "Energizing Potion", "image": "energizing_potion.png", "description": "Extra advancement material for pets (Lv.30+)", "sources": "Pet adventures, Events", "uses": "Pet advancement from level 30+"},
        {"id": "strengthening_serum", "name": "Strengthening Serum", "image": "strengthening_serum.png", "description": "Advanced advancement material (Lv.50+)", "sources": "Pet adventures, High-level beast hunts", "uses": "Pet advancement from level 50+"},
        {"id": "common_wild_mark", "name": "Common Wild Mark", "image": "common_wild_mark.png", "description": "Material for basic pet refinement", "sources": "Pet adventures, Various events", "uses": "Pet refinement processes"},
        {"id": "advanced_wild_mark", "name": "Advanced Wild Mark", "image": "advanced_wild_mark.png", "description": "Material for advanced pet refinement", "sources": "Pet adventures, Higher-tier beast hunts", "uses": "Advanced pet refinement"},
    ],
    "Speedups": [
        {"id": "speedup_general", "name": "General Speedup", "image": None, "emoji": "⏱️", "description": "Reduces any timer. Most versatile", "sources": "Events, Chests, Packs, Alliance help", "uses": "Any: construction, research, training, healing", "durations": "1min, 5min, 1hr, 3hr, 8hr, 24hr"},
        {"id": "speedup_construction", "name": "Construction Speedup", "image": None, "emoji": "🏗️", "description": "Reduces building timers only", "sources": "Events, Chests, Construction milestones", "uses": "Building construction and upgrades", "durations": "1min, 5min, 1hr, 3hr, 8hr"},
        {"id": "speedup_research", "name": "Research Speedup", "image": None, "emoji": "🔬", "description": "Reduces research timers only", "sources": "Events, Chests, Research milestones", "uses": "Research projects only", "durations": "1min, 5min, 1hr, 3hr, 8hr"},
        {"id": "speedup_training", "name": "Training Speedup", "image": None, "emoji": "⚔️", "description": "Reduces troop training timers only", "sources": "Events, Chests, Training milestones", "uses": "Troop training only", "durations": "1min, 5min, 1hr, 3hr, 8hr"},
        {"id": "speedup_healing", "name": "Healing Speedup", "image": None, "emoji": "💚", "description": "Reduces hospital healing timers only", "sources": "Events, Chests, Combat rewards", "uses": "Healing wounded troops only", "durations": "1min, 5min, 1hr, 3hr, 8hr"},
    ],
    "Boosts & Buffs": [
        {"id": "shield", "name": "Peace Shield", "image": "shield.png", "description": "Protects city from attacks", "sources": "Events, Packs, Gem shop, Rewards", "uses": "Protecting city when offline", "durations": "2hr, 8hr, 24hr, 3 day, 7 day"},
        {"id": "counter_recon", "name": "Counter Recon", "image": "counter_recon.png", "description": "Hides troop/resource info from scouts", "sources": "Events, Packs, Gem shop", "uses": "Hide army before SvS/battles", "durations": "2hr, 24hr"},
        {"id": "vip_time", "name": "VIP Time", "image": "vip_time.png", "description": "Grants temporary VIP benefits", "sources": "Events, Packs, Daily rewards", "uses": "Activating VIP buffs/discounts", "durations": "24hr, 7 day, 30 day"},
        {"id": "troops_attack_up", "name": "Troop Attack UP", "image": "troops_attack_up.png", "description": "Temporarily increases troop attack", "sources": "City Bonus (2k/20k gems), Events, Packs", "uses": "Activate before rallies/SvS", "durations": "2hr (+10%), 12hr (+20%)"},
        {"id": "troops_defense_up", "name": "Troop Defense UP", "image": "troops_defense_up.png", "description": "Temporarily increases troop defense", "sources": "City Bonus (2k/20k gems), Events, Packs", "uses": "Activate when expecting attacks", "durations": "2hr (+10%), 12hr (+20%)"},
        {"id": "troops_health_up", "name": "Troop Health UP", "image": "troops_health_up.png", "description": "Temporarily increases troop health", "sources": "Events, Packs, City Bonus", "uses": "Activate for major battles", "durations": "2hr (+10%), 12hr (+20%)"},
        {"id": "troops_damage_up", "name": "Troop Lethality UP", "image": "troops_damage_up.png", "description": "Increases damage output. Highest priority stat", "sources": "Pets, Hero Widgets, Events, Packs", "uses": "Maximizing combat damage"},
        {"id": "enemy_attack_down", "name": "Enemy Attack DOWN", "image": "enemy_attack_down.png", "description": "Reduces enemy troop attack", "sources": "Events, Packs, Combat buffs", "uses": "Defensive advantage in battles", "durations": "2hr (-10%), 12hr (-20%)"},
        {"id": "enemy_defense_down", "name": "Enemy Defense DOWN", "image": "enemy_defense_down.png", "description": "Reduces enemy troop defense", "sources": "Events, Packs, Combat buffs", "uses": "Offensive advantage in battles", "durations": "2hr (-10%), 12hr (-20%)"},
        {"id": "march_accelerator", "name": "March Speed Boost", "image": "march_accelerator.png", "description": "Increases march speed", "sources": "Events, Packs, Rewards", "uses": "Faster rallies, Quick reinforcements"},
        {"id": "gathering_speed_boost", "name": "Gathering Boost", "image": "gathering_speed_boost.png", "description": "Increases gathering speed on tiles", "sources": "City Bonus, Events, Packs", "uses": "Faster resource collection", "durations": "8hr, 24hr (+100%)"},
        {"id": "rally_boost", "name": "Rally Attack Boost", "image": "rally_boost.png", "description": "Increases damage during rallies", "sources": "Events, Packs, Alliance rewards", "uses": "Before leading/joining rallies"},
        {"id": "expedition_boost", "name": "Expedition Boost", "image": "expedition_boost.png", "description": "Boosts expedition battle performance", "sources": "Events, Packs", "uses": "Expedition battles"},
        {"id": "training_capacity_boost", "name": "Training Capacity Boost", "image": "training_capacity_boost.png", "description": "Increases troop training capacity", "sources": "Events, Packs, Rewards", "uses": "Train more troops at once"},
        {"id": "deployment_capacity_boost", "name": "Deployment Capacity Boost", "image": "deployment_capacity_boost.png", "description": "Increases troops per march", "sources": "Events, Packs, Rewards", "uses": "Larger army deployments"},
    ],
    "Keys & Tokens": [
        {"id": "platinum_key", "name": "Platinum Key", "image": "platinum_key.png", "description": "Opens platinum chests for rare rewards", "sources": "Events, Packs, Milestones", "uses": "Opening platinum reward chests"},
        {"id": "gold_key", "name": "Gold Key", "image": "gold_key.png", "description": "Opens gold chests for good rewards", "sources": "Events, Packs, Daily alliance ranking", "uses": "Opening gold reward chests"},
        {"id": "lucky_wheel_ticket", "name": "Wheel Ticket", "image": "lucky_wheel_ticket.png", "description": "Free spin on the Lucky Wheel", "sources": "Events, Daily login, Packs", "uses": "Lucky Wheel for shards/items"},
        {"id": "alliance_token", "name": "Alliance Token", "image": "alliance_token.png", "description": "Alliance currency (resets daily/weekly)", "sources": "Tech donations, Crazy Joe, Alliance activities", "uses": "Alliance Shop (teleports, speedups, VIP)"},
        {"id": "arena_token", "name": "Arena Token", "image": "arena_token.png", "description": "Currency from Arena battles", "sources": "Arena battles, Arena rankings", "uses": "Arena Shop (gear, stamina, essence stones)"},
        {"id": "mystery_badge", "name": "Mystery Badge", "image": "mystery_badge.png", "description": "Daily currency for Mystery Shop (cap 80/day)", "sources": "Daily missions (80 free), Mystery Badge Packs", "uses": "Mystery Shop (Custom Mythic gear)"},
        {"id": "frost_star", "name": "Frost Star", "image": "frost_star.png", "description": "Premium currency for special items", "sources": "Events, Battle Pass, Special rewards", "uses": "Frost Star shop exclusives"},
        {"id": "sunfire_token", "name": "Sunfire Token", "image": "sunfire_token.png", "description": "Currency from State vs State (SvS)", "sources": "SvS battles and events", "uses": "SvS shop purchases"},
        {"id": "lost_coin", "name": "Lost Coin", "image": "lost_coin.png", "description": "Currency from Canyon Clash events", "sources": "Canyon Clash participation", "uses": "Canyon-exclusive shop items"},
        {"id": "trade_voucher", "name": "Trade Voucher", "image": "trade_voucher.png", "description": "Premium currency from trading excess items", "sources": "Tundra Trading (shards, manuals, widgets)", "uses": "Legendary Gear, Essence Stones, Mythic Shards"},
        {"id": "championship_badge", "name": "Championship Badge", "image": "championship_badge.png", "description": "Currency from Alliance Championship", "sources": "Alliance Championship participation", "uses": "Championship Shop (Alloy, Polishing Sol.)"},
        {"id": "arsenal_token", "name": "Arsenal Token", "image": "arsenal_token.png", "description": "Currency for arsenal/armory items", "sources": "Events, Special activities", "uses": "Arsenal shop purchases"},
        {"id": "authority", "name": "Authority", "image": "authority.png", "description": "Special token for state events", "sources": "State competitions, Special rankings", "uses": "Event rewards and rankings"},
        {"id": "loyalty", "name": "Loyalty", "image": "loyalty.png", "description": "Alliance loyalty currency", "sources": "Alliance events, Consistent participation", "uses": "Alliance rewards"},
        {"id": "prestige_badge", "name": "Prestige Badge", "image": "prestige_badge.png", "description": "Badge from prestige achievements", "sources": "High-level achievements, Events", "uses": "Prestige shop purchases"},
    ],
    "Teleporters": [
        {"id": "random_teleporter", "name": "Random Teleport", "image": "random_teleporter.png", "description": "Moves city to random location", "sources": "Events, Gem shop (cheap), Rewards", "uses": "Escaping attacks, Relocating"},
        {"id": "advanced_teleporter", "name": "Advanced Teleport", "image": "advanced_teleporter.png", "description": "Moves city to chosen location", "sources": "Events, Packs, Gem shop, Arena Shop", "uses": "Strategic positioning"},
        {"id": "alliance_teleporter", "name": "Alliance Teleport", "image": "alliance_teleporter.png", "description": "Moves city near alliance territory", "sources": "Events, Alliance shop, Packs", "uses": "Joining alliance hive"},
        {"id": "territory_teleporter", "name": "Territory Teleport", "image": "territory_teleporter.png", "description": "Moves city to different region", "sources": "Migration events, Special packs", "uses": "Region/territory migration"},
        {"id": "transfer_pass", "name": "Transfer Pass", "image": "transfer_pass.png", "description": "Relocate entire city to different state", "sources": "Alliance Shop (priority), Events", "uses": "Server/state migration"},
    ],
    "Chests & Boxes": [
        {"id": "resource_chest", "name": "Resource Chest", "image": "resource_chest.png", "description": "Contains choice of basic resources", "sources": "Events, Daily missions, Tundra Trading", "uses": "Choose meat, wood, coal, or iron"},
        {"id": "warriors_chest", "name": "Warrior's Chest", "image": "warriors_chest.png", "description": "Combat-focused rewards chest", "sources": "Combat events, SvS rewards", "uses": "Combat items and resources"},
        {"id": "allys_chest", "name": "Ally's Chest", "image": "allys_chest.png", "description": "Alliance reward chest", "sources": "Alliance events, Helping allies", "uses": "Alliance-related rewards"},
        {"id": "rulers_chest", "name": "Ruler's Chest", "image": "rulers_chest.png", "description": "High-tier reward chest", "sources": "Leadership events, High rankings", "uses": "Premium rewards"},
        {"id": "hero_gear_chest", "name": "Hero Gear Chest", "image": "hero_gear_chest.png", "description": "Contains random hero gear pieces", "sources": "Events, Lucky chests, Frosty Fortune", "uses": "Building hero gear collection"},
        {"id": "chief_gear_chest", "name": "Chief Gear Chest", "image": "chief_gear_chest.png", "description": "Contains chief gear materials", "sources": "Events, Foundry rewards", "uses": "Chief gear crafting materials"},
        {"id": "fire_crystal_chest", "name": "Fire Crystal Chest", "image": "fire_crystal_chest.png", "description": "Contains Fire Crystals or Shards", "sources": "Crystal Reactivation, Daily missions (last 2)", "uses": "Post-FC30 upgrades"},
        {"id": "pet_materials_chest", "name": "Pet Materials Chest", "image": "pet_materials_chest.png", "description": "Contains pet advancement materials", "sources": "Events, Shops, Quest rewards", "uses": "Pet advancement"},
        {"id": "hero_lucky_box", "name": "Hero Lucky Box", "image": "hero_lucky_box.png", "description": "Random hero-related rewards", "sources": "Events, Special promotions", "uses": "Hero shards and materials"},
    ],
    "Other Items": [
        {"id": "vip_points", "name": "VIP Points", "image": "vip_points.png", "description": "Points for permanent VIP bonuses (12 levels)", "sources": "Daily login, Packs, Events, Gem shop", "uses": "Increasing VIP level"},
        {"id": "life_essence", "name": "Life Essence", "image": "life_essence.png", "description": "Daybreak Island currency", "sources": "Daybreak Island activities, Events", "uses": "Daybreak Island shop"},
        {"id": "chief_rename_card", "name": "Chief Rename Card", "image": "chief_rename_card.png", "description": "Allows changing your Chief's name", "sources": "Special events, Packs, Rare drops", "uses": "Cosmetic identity change"},
        {"id": "book_of_knowledge", "name": "Book of Knowledge", "image": "book_of_knowledge.png", "description": "Provides research benefits", "sources": "Events, Special rewards", "uses": "Research boosts"},
        {"id": "common_expert_sigil", "name": "Expert Sigil", "image": "common_expert_sigil.png", "description": "Material for hero expertise trees", "sources": "Events, Expert missions, Shops", "uses": "Hero expertise abilities"},
        {"id": "compass", "name": "Compass", "image": "compass.png", "description": "Navigation/exploration item", "sources": "Exploration events, Rewards", "uses": "Exploration activities"},
        {"id": "lucky_chip", "name": "Lucky Chip", "image": "lucky_chip.png", "description": "Gambling/chance event currency", "sources": "Lucky events, Special promotions", "uses": "Lucky event participation"},
        {"id": "fortune_token", "name": "Fortune Token", "image": "fortune_token.png", "description": "Fortune/luck event currency", "sources": "Fortune events, Packs", "uses": "Fortune event shop"},
        {"id": "frontier_supply", "name": "Frontier Supply", "image": "frontier_supply.png", "description": "Supply from frontier events", "sources": "Frontier/border skirmish events", "uses": "Event-specific rewards"},
        {"id": "trek_supplies", "name": "Trek Supplies", "image": "trek_supplies.png", "description": "Supplies for trek/journey events", "sources": "Trek events, Journey rewards", "uses": "Trek event progression"},
    ],
}


def get_image_base64(image_name):
    """Get base64 encoded image for inline display."""
    if not image_name:
        return None
    image_path = ITEMS_DIR / image_name
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def render_item_table(items):
    """Render items as a clean table."""
    # Build table HTML
    rows_html = ""
    for item in items:
        # Get image
        img_html = ""
        if item.get("image"):
            img_b64 = get_image_base64(item["image"])
            if img_b64:
                img_html = f'<img src="data:image/png;base64,{img_b64}" width="32" height="32" style="border-radius:4px;vertical-align:middle;">'

        if not img_html and item.get("emoji"):
            img_html = f'<span style="font-size:24px;">{item["emoji"]}</span>'

        if not img_html:
            img_html = '<span style="font-size:24px;">📦</span>'

        # Duration note if applicable
        duration_note = ""
        if item.get("durations"):
            duration_note = f'<br><span style="color:#FFD700;font-size:10px;">{item["durations"]}</span>'

        rows_html += f'''<tr style="border-bottom:1px solid rgba(74,144,217,0.2);">
            <td style="padding:10px;text-align:center;width:50px;">{img_html}</td>
            <td style="padding:10px;font-weight:bold;color:#E8F4F8;white-space:nowrap;">{item["name"]}</td>
            <td style="padding:10px;color:#B8D4E8;font-size:12px;">{item["description"]}{duration_note}</td>
            <td style="padding:10px;color:#888;font-size:11px;">{item["sources"]}</td>
            <td style="padding:10px;color:#4A90D9;font-size:11px;">{item["uses"]}</td>
        </tr>'''

    table_html = f'''<table style="width:100%;border-collapse:collapse;background:rgba(46,90,140,0.1);border-radius:8px;overflow:hidden;">
        <thead>
            <tr style="background:rgba(46,90,140,0.3);border-bottom:2px solid rgba(74,144,217,0.3);">
                <th style="padding:10px;text-align:center;width:50px;"></th>
                <th style="padding:10px;text-align:left;color:#E8F4F8;font-size:12px;text-transform:uppercase;">Name</th>
                <th style="padding:10px;text-align:left;color:#E8F4F8;font-size:12px;text-transform:uppercase;">Description</th>
                <th style="padding:10px;text-align:left;color:#E8F4F8;font-size:12px;text-transform:uppercase;">Sources</th>
                <th style="padding:10px;text-align:left;color:#E8F4F8;font-size:12px;text-transform:uppercase;">Uses</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>'''

    st.markdown(table_html, unsafe_allow_html=True)


# Page content
st.markdown("# Item Guide")
st.markdown("Reference for backpack items - what they are, where to get them, and what they're used for.")

# Search
search = st.text_input("Search items", placeholder="Type to filter items...")

# Tabs for categories
categories = list(ITEM_DATA.keys())
tabs = st.tabs(categories)

for tab, category in zip(tabs, categories):
    with tab:
        items = ITEM_DATA[category]

        # Filter by search
        if search:
            search_lower = search.lower()
            items = [item for item in items if
                     search_lower in item['name'].lower() or
                     search_lower in item['description'].lower() or
                     search_lower in item['sources'].lower() or
                     search_lower in item['uses'].lower()]

        if not items:
            st.caption("No items match your search.")
        else:
            render_item_table(items)
