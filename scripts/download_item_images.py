"""
Download item images from Whiteout Survival Wiki and other sources.
Comprehensive library of all available item icons.
"""

import os
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ITEMS_DIR = PROJECT_ROOT / "assets" / "items"
ITEMS_DIR.mkdir(parents=True, exist_ok=True)

# Comprehensive item images to download
ITEM_IMAGES = {
    # === BASIC RESOURCES ===
    "gems": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/05/23121052/item_icon_100001.png",
    "meat": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10114534/item_icon_100011.png",
    "wood": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/item_icon_103.png",
    "coal": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10114623/item_icon_100031.png",
    "iron": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/item_icon_105.png",
    "steel": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/20250617-144040.png",

    # === FIRE CRYSTALS & BUILDING MATERIALS ===
    "fire_crystal": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/07/item_icon_100081.png",
    "refined_fire_crystal": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/05/21122055/item_icon_100082.png",
    "fire_crystal_shard": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/07/item_icon_100083.png",
    "fire_crystal_ember": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/item_icon_720001.png",
    "fire_crystal_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_720002.png",
    "glowstone": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/glowstine.png",

    # === CHIEF GEAR MATERIALS ===
    "hardened_alloy": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Hardened-Alloy.png",
    "polishing_solution": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Polishing-Solution.png",
    "design_plans": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Design-Plan.png",
    "xp_component": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/XP-Component.png",
    "charm_design": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/charm-design.png",
    "charm_guide": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/charm-guide.png",
    "charm_secrets": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/item_icon_600026.png",
    "mithril": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/item_icon_500235.png",
    "lunar_amber": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/item_icon_600051.png",
    "essence_stone": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/14084129/item_icon_500240.png",

    # === HERO MATERIALS ===
    "hero_xp": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/hero-xp.png",
    "legendary_hero_shard": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/item_icon_500220.png",
    "epic_hero_shard": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/item_icon_500221.png",
    "rare_hero_shard": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/item_icon_500222.png",
    "mythic_exploration_manual": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10120616/item_icon_500200.png",
    "epic_exploration_manual": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10120618/item_icon_500201.png",
    "rare_exploration_manual": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10120620/item_icon_500202.png",
    "mythic_expedition_manual": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10120621/item_icon_500210.png",
    "epic_expedition_manual": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10120622/item_icon_500211.png",
    "rare_expedition_manual": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/10120623/item_icon_500212.png",
    "mythic_decoration_component": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/Mythic-General-Decoration-Component.png",

    # === CURRENCIES & TOKENS ===
    "alliance_token": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/alliancetoken.png",
    "arena_token": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/arenatoken.png",
    "sunfire_token": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/sunfiretoken.png",
    "arsenal_token": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/arsenaltoken.png",
    "skin_token": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_117.png",
    "championship_badge": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/acbadge.png",
    "vip_points": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_620000.png",
    "frost_star": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_114.png",
    "lost_coin": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_119.png",
    "life_essence": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_118.png",
    "authority": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_609_01.png",
    "loyalty": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_259.png",
    "loyalty_tag": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_610110.png",
    "lucky_chip": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600027.png",
    "fortune_token": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600029.png",
    "trade_voucher": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600032.png",
    "mystery_badge": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600020.png",
    "prestige_badge": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/Prestige-Badge.png",
    "treasure_hunt_points": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/jump_icon_40161.png",
    "labyrinth_core": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/labyrinthcore.png",
    "medal_of_honor": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/medalofhonor.png",
    "mark_of_valor": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/05/21155058/item_icon_620501.png",

    # === KEYS ===
    "platinum_key": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Platinum-Key.png",
    "gold_key": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Gold-Key.png",

    # === TELEPORTERS ===
    "random_teleporter": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/07/item_icon_610101.png",
    "advanced_teleporter": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/advanced-teleport.png",
    "alliance_teleporter": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/alliance-teleport.png",
    "territory_teleporter": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/territory-teleport.png",

    # === SHIELDS & PROTECTION ===
    "shield": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075049/item_icon_302301.png",
    "counter_recon": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075050/item_icon_302401.png",

    # === BOOSTS & BUFFS ===
    "troops_damage_up": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075033/item_icon_301100.png",
    "troops_attack_up": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075034/item_icon_301200.png",
    "troops_defense_up": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075035/item_icon_301300.png",
    "troops_health_up": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075036/item_icon_301400.png",
    "enemy_attack_down": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075037/item_icon_301500.png",
    "enemy_defense_down": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075038/item_icon_301600.png",
    "deployment_capacity_boost": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075039/item_icon_301700.png",
    "gathering_speed_boost": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075047/item_icon_302000.png",
    "training_capacity_boost": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075048/item_icon_302101.png",
    "expedition_boost": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075041/item_icon_301800.png",
    "rally_boost": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075042/item_icon_301801.png",
    "march_accelerator": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075043/item_icon_301900.png",
    "march_accelerator_2": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/18075044/item_icon_301901.png",

    # === PET MATERIALS ===
    "pet_food": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/09/pet-food.png",
    "taming_manual": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/item_icon_600043.png",
    "energizing_potion": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/item_icon_600044.png",
    "strengthening_serum": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/item_icon_600045.png",
    "common_wild_mark": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/item_icon_600046.png",
    "advanced_wild_mark": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/item_icon_600047.png",

    # === CONSUMABLES & SPECIAL ===
    "stamina": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_610002.png",
    "chief_rename_card": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_610001.png",
    "vip_time": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/11/item_icon_v500210.png",
    "horn_of_cryptid": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Horn-of-the-Cryptid.png",
    "explosive_arrowhead": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/explosive-Arrowheads.png",
    "scattered_parts": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600008.png",
    "hunter_pouch": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Hunter-Pouch.png",
    "loot": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15122900/item_icon_600009.png",
    "transfer_pass": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/item_icon_600052.png",
    "rebirth_tome": "https://whiteoutdata.com/wp-content/uploads/2024/03/rebirth-tome-300x246.webp",

    # === FISHING & EXPLORATION ===
    "ocean_scanner": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600035.png",
    "frosty_prospector": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600038.png",
    "reel_stabilizer": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600034.png",
    "lantern": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600036.png",
    "horn_of_poseidon": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_600037.png",
    "crystallite_core": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/item_icon_620601.png",
    "icefisher_voucher": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15112510/item_icon_600039.png",
    "truck_voucher": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15112532/item_icon_600061.png",

    # === EVENT ITEMS ===
    "lucky_wheel_ticket": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/07/jump_icon_40072.png",
    "pickaxe": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_620188.png",
    "snow_shovel": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_620199.png",
    "pocket_watch": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/item_icon_700020.png",

    # === CHESTS & BOXES ===
    "treasure_box": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15122840/item_icon_510027.png",
    "warriors_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/07/item_icon_710000.png",
    "allys_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/07/item_icon_710001.png",
    "rulers_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/07/item_icon_710002.png",
    "controllers_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/07/item_icon_710003.png",
    "resource_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15161833/item_icon_100091.png",
    "chief_gear_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15120649/item_icon_510000.png",
    "hero_gear_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15120656/item_icon_510001.png",
    "charm_material_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15120658/item_icon_510003.png",
    "scattered_supplies": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15120700/item_icon_510004.png",
    "treasure_hunt_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15120701/item_icon_510006.png",
    "epic_hero_gear_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15120634/item_icon_501000.png",
    "mythic_hero_gear_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15120636/item_icon_501001.png",
    "pet_materials_chest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15122834/item_icon_510019.png",
    "hero_lucky_box": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/06/15122907/item_icon_600010.png",

    # === EXPERT SYSTEM ===
    "common_expert_sigil": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/08/item_icon_570000.png",
    "book_of_knowledge": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/08/item_icon_570300.png",
    "compass": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/10/item_icon_570201.png",
    "fiery_heart": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/10/item_icon_570202.png",
    "sail_of_conquest": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/10/item_icon_570203.png",
    "trek_supplies": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/10/trek_supply.png",
    "frontier_supply": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/10/item_icon_570310.png",
}


def download_image(url: str, filename: str) -> bool:
    """Download an image from URL."""
    filepath = ITEMS_DIR / filename

    if filepath.exists():
        print(f"  Already exists: {filename}")
        return True

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        filepath.write_bytes(response.content)
        print(f"  Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"  Failed: {filename} - {e}")
        return False


def main():
    print("Downloading comprehensive item image library...")
    print(f"Saving to: {ITEMS_DIR}")
    print(f"Total items to download: {len(ITEM_IMAGES)}")
    print()

    success = 0
    failed = 0

    for item_id, url in ITEM_IMAGES.items():
        # Determine extension from URL
        ext = "png"
        if url.endswith(".webp"):
            ext = "webp"
        elif url.endswith(".jpg") or url.endswith(".jpeg"):
            ext = "jpg"

        if download_image(url, f"{item_id}.{ext}"):
            success += 1
        else:
            failed += 1

    print(f"\nDone! Success: {success}, Failed: {failed}")
    print(f"Images saved to: {ITEMS_DIR}")


if __name__ == "__main__":
    main()
