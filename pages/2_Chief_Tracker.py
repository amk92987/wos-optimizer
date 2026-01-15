"""
Chief Gear & Charms - Track your chief equipment progression.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserChiefGear, UserChiefCharm
from utils.theme_colors import get_colors, text_shadow

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Chief Gear Tier Progression - matches the game's actual system
# Format: (tier_id, display_name, color, approx_bonus%)
GEAR_TIERS = [
    (1, "Green 0★", "#2ECC71", 9.35),
    (2, "Green 1★", "#2ECC71", 12.75),
    (3, "Blue 0★", "#3498DB", 17.00),
    (4, "Blue 1★", "#3498DB", 20.25),
    (5, "Blue 2★", "#3498DB", 24.50),
    (6, "Blue 3★", "#3498DB", 29.75),
    (7, "Purple 0★", "#9B59B6", 34.00),
    (8, "Purple 1★", "#9B59B6", 38.00),
    (9, "Purple 2★", "#9B59B6", 42.50),
    (10, "Purple 3★", "#9B59B6", 47.00),
    (11, "Purple T1 0★", "#9B59B6", 48.50),
    (12, "Purple T1 1★", "#9B59B6", 50.00),
    (13, "Purple T1 2★", "#9B59B6", 52.00),
    (14, "Purple T1 3★", "#9B59B6", 54.23),
    (15, "Gold 0★", "#F1C40F", 56.78),
    (16, "Gold 1★", "#F1C40F", 59.50),
    (17, "Gold 2★", "#F1C40F", 62.50),
    (18, "Gold 3★", "#F1C40F", 66.00),
    (19, "Gold T1 0★", "#F1C40F", 69.00),
    (20, "Gold T1 1★", "#F1C40F", 72.00),
    (21, "Gold T1 2★", "#F1C40F", 75.50),
    (22, "Gold T1 3★", "#F1C40F", 79.00),
    (23, "Gold T2 0★", "#F1C40F", 80.50),
    (24, "Gold T2 1★", "#F1C40F", 82.00),
    (25, "Gold T2 2★", "#F1C40F", 83.50),
    (26, "Gold T2 3★", "#F1C40F", 85.00),
    (27, "Pink 0★", "#E84393", 89.25),
    (28, "Pink 1★", "#E84393", 94.00),
    (29, "Pink 2★", "#E84393", 99.00),
    (30, "Pink 3★", "#E84393", 104.50),
    (31, "Pink T1 0★", "#E84393", 110.00),
    (32, "Pink T1 1★", "#E84393", 116.00),
    (33, "Pink T1 2★", "#E84393", 122.50),
    (34, "Pink T1 3★", "#E84393", 129.00),
    (35, "Pink T2 0★", "#E84393", 136.00),
    (36, "Pink T2 1★", "#E84393", 143.50),
    (37, "Pink T2 2★", "#E84393", 151.50),
    (38, "Pink T2 3★", "#E84393", 160.00),
    (39, "Pink T3 0★", "#E84393", 165.00),
    (40, "Pink T3 1★", "#E84393", 171.00),
    (41, "Pink T3 2★", "#E84393", 178.00),
    (42, "Pink T3 3★", "#E84393", 187.00),
]

# Create lookup dictionaries
TIER_BY_ID = {t[0]: t for t in GEAR_TIERS}

# Cascading selector structure: Color -> Subtier -> Stars
# Build from GEAR_TIERS
import re as _re

TIER_STRUCTURE = {}  # {color: {subtier: [stars]}}
TIER_LOOKUP = {}     # {(color, subtier, stars): tier_id}

for _t in GEAR_TIERS:
    _tid, _name, _color_hex, _bonus = _t
    _parts = _name.lower().split()
    _color = _parts[0].capitalize()

    # Extract subtier
    _subtier = "Base"
    for _p in _parts:
        if _p.startswith('t') and len(_p) == 2 and _p[1].isdigit():
            _subtier = _p.upper()
            break

    # Extract stars
    _stars = 0
    _star_match = _re.search(r'(\d)★', _name)
    if _star_match:
        _stars = int(_star_match.group(1))

    if _color not in TIER_STRUCTURE:
        TIER_STRUCTURE[_color] = {}
    if _subtier not in TIER_STRUCTURE[_color]:
        TIER_STRUCTURE[_color][_subtier] = []
    TIER_STRUCTURE[_color][_subtier].append(_stars)
    TIER_LOOKUP[(_color, _subtier, _stars)] = _tid

# Color display order and hex codes
TIER_COLORS_MAP = {
    "Green": "#2ECC71",
    "Blue": "#3498DB",
    "Purple": "#9B59B6",
    "Gold": "#F1C40F",
    "Pink": "#E91E63",
}
TIER_OPTIONS = [(t[0], t[1]) for t in GEAR_TIERS]

# Chief Gear slots with their troop type effects
GEAR_SLOTS = {
    "cap": {"name": "Cap", "icon": "🎩", "troop": "Lancer", "color": "#2ECC71"},
    "watch": {"name": "Watch", "icon": "⌚", "troop": "Lancer", "color": "#2ECC71"},
    "coat": {"name": "Coat", "icon": "🧥", "troop": "Infantry", "color": "#E74C3C"},
    "pants": {"name": "Pants", "icon": "👖", "troop": "Infantry", "color": "#E74C3C"},
    "belt": {"name": "Belt", "icon": "🎯", "troop": "Marksman", "color": "#3498DB"},
    "weapon": {"name": "Weapon", "icon": "⚔️", "troop": "Marksman", "color": "#3498DB"},
}

# Chief Charm level stats (approximate % bonus per level) and shapes
CHARM_STATS = {
    1: {"bonus": 9.0, "shape": "Triangle", "sides": 3},
    2: {"bonus": 15.0, "shape": "Diamond", "sides": 4},
    3: {"bonus": 22.0, "shape": "Square", "sides": 4},
    4: {"bonus": 29.0, "shape": "Square", "sides": 4},
    5: {"bonus": 36.0, "shape": "Pentagon", "sides": 5},
    6: {"bonus": 43.0, "shape": "Pentagon", "sides": 5},
    7: {"bonus": 50.0, "shape": "Hexagon", "sides": 6},
    8: {"bonus": 57.0, "shape": "Hexagon", "sides": 6},
    9: {"bonus": 64.0, "shape": "Heptagon", "sides": 7},
    10: {"bonus": 71.0, "shape": "Octagon", "sides": 8},
    11: {"bonus": 78.0, "shape": "Nonagon", "sides": 9},
    12: {"bonus": 83.0, "shape": "Decagon", "sides": 10},
    13: {"bonus": 88.0, "shape": "Hendecagon", "sides": 11},
    14: {"bonus": 93.0, "shape": "Dodecagon", "sides": 12},
    15: {"bonus": 97.0, "shape": "Near-Circle", "sides": 13},
    16: {"bonus": 100.0, "shape": "Circle", "sides": 16},
}

# Gear image paths (base images for fallback)
GEAR_IMAGES = {
    "cap": "assets/chief_gear/hat.png",
    "watch": "assets/chief_gear/watch.png",
    "coat": "assets/chief_gear/coat.png",
    "pants": "assets/chief_gear/pants.png",
    "belt": "assets/chief_gear/ring.png",  # belt uses ring image
    "weapon": "assets/chief_gear/staff.png",
}


def get_tiered_gear_image(slot_id: str, tier_id: int) -> Path:
    """Get the gear image path for a specific tier.

    Generated images are in: assets/chief_gear/tiers/{slot}_{color}_t{tier}_{stars}star.png
    """
    import re

    tier_info = TIER_BY_ID.get(tier_id, GEAR_TIERS[0])
    tier_name = tier_info[1]  # e.g., "Green 0★", "Blue T2 3★", "Pink T3 3★"

    # Parse tier name to extract color, tier number, and stars
    # Format: "Color [T#] #★"
    parts = tier_name.lower().split()
    color = parts[0]  # "green", "blue", "purple", "gold", "pink"

    # Extract stars - look for digit before ★ (e.g., "0★", "3★")
    stars = 0
    star_match = re.search(r'(\d)★', tier_name)
    if star_match:
        stars = int(star_match.group(1))

    # Extract tier number (T1, T2, T3) - default to 0 (base) if not specified
    tier_num = 0
    tier_match = re.search(r't(\d)', tier_name.lower())
    if tier_match:
        tier_num = int(tier_match.group(1))

    # Build filename
    filename = f"{slot_id}_{color}_t{tier_num}_{stars}star.png"
    tiered_path = PROJECT_ROOT / "assets" / "chief_gear" / "tiers" / filename

    # Fallback to base image if tiered doesn't exist
    if tiered_path.exists():
        return tiered_path
    else:
        return PROJECT_ROOT / GEAR_IMAGES.get(slot_id, "")

# Charm type per gear piece (each gear has 3 charms of the SAME type)
# Gear determines charm type based on troop category
GEAR_CHARM_TYPE = {
    "cap": {"type": "keenness", "name": "Keenness", "icon": "⚡", "troop": "Lancer", "color": "#2ECC71"},
    "watch": {"type": "keenness", "name": "Keenness", "icon": "⚡", "troop": "Lancer", "color": "#2ECC71"},
    "coat": {"type": "protection", "name": "Protection", "icon": "🛡️", "troop": "Infantry", "color": "#E74C3C"},
    "pants": {"type": "protection", "name": "Protection", "icon": "🛡️", "troop": "Infantry", "color": "#E74C3C"},
    "belt": {"type": "vision", "name": "Vision", "icon": "👁️", "troop": "Marksman", "color": "#3498DB"},
    "weapon": {"type": "vision", "name": "Vision", "icon": "👁️", "troop": "Marksman", "color": "#3498DB"},
}

# All charm level options including sub-levels for 4+
# Format: ("display_value", "db_value")
# Levels 1-3 are simple, 4+ have sub-levels
def get_charm_level_options():
    """Generate all possible charm level values with sub-levels."""
    options = []
    for level in range(1, 17):
        if level < 4:
            # Simple levels 1-3
            options.append(str(level))
        else:
            # Levels 4-16 have sub-levels: 4-1, 4-2, 4-3, then 5, etc.
            options.append(f"{level}-1")
            options.append(f"{level}-2")
            options.append(f"{level}-3")
    return options

CHARM_LEVEL_OPTIONS = get_charm_level_options()

def parse_charm_level(value):
    """Parse a charm level string to (main_level, sub_level)."""
    if value is None:
        return (1, 0)
    value = str(value)
    if "-" in value:
        parts = value.split("-")
        return (int(parts[0]), int(parts[1]))
    else:
        return (int(value), 0)

def get_charm_bonus(level_str):
    """Get the bonus percentage for a charm level (uses main level only)."""
    main_level, _ = parse_charm_level(level_str)
    return CHARM_STATS.get(main_level, {"bonus": 9.0})["bonus"]

def format_charm_level_display(level_str):
    """Format charm level for display."""
    main_level, sub_level = parse_charm_level(level_str)
    shape = get_shape_symbol(main_level)
    bonus = CHARM_STATS.get(main_level, {"bonus": 9.0})["bonus"]
    if sub_level > 0:
        return f"{shape} {main_level}-{sub_level} (+{bonus:.0f}%)"
    else:
        return f"{shape} Lv.{main_level} (+{bonus:.0f}%)"


def get_or_create_chief_gear():
    """Get or create chief gear record for current profile."""
    try:
        gear = db.query(UserChiefGear).filter(UserChiefGear.profile_id == profile.id).first()
        if not gear:
            gear = UserChiefGear(profile_id=profile.id)
            db.add(gear)
            db.commit()
            db.refresh(gear)
        return gear
    except Exception as e:
        st.error(f"Database error loading gear: {e}. Try deleting wos_optimizer.db and restarting.")
        return None


def get_or_create_chief_charms():
    """Get or create chief charms record for current profile."""
    try:
        charms = db.query(UserChiefCharm).filter(UserChiefCharm.profile_id == profile.id).first()
        if not charms:
            charms = UserChiefCharm(profile_id=profile.id)
            db.add(charms)
            db.commit()
            db.refresh(charms)
        return charms
    except Exception as e:
        st.error(f"Database error loading charms: {e}. Try deleting wos_optimizer.db and restarting.")
        return None


def render_gear_slot(slot_id, slot_info, gear_data):
    """Render a single gear slot with tier selector."""
    # Map old field names to new slot IDs
    field_map = {
        "cap": "helmet",  # Using helmet field for cap
        "watch": "ring",  # Using ring field for watch
        "coat": "armor",  # Using armor field for coat
        "pants": "boots",  # Using boots field for pants
        "belt": "gloves",  # Using gloves field for belt
        "weapon": "amulet",  # Using amulet field for weapon
    }

    db_field = field_map.get(slot_id, slot_id)
    quality_attr = f"{db_field}_quality"
    level_attr = f"{db_field}_level"

    # Current tier is stored in quality field (1-42)
    current_tier_id = getattr(gear_data, quality_attr, 1) if gear_data else 1
    if current_tier_id is None or current_tier_id < 1 or current_tier_id > len(GEAR_TIERS):
        current_tier_id = 1

    tier_info = TIER_BY_ID.get(current_tier_id, GEAR_TIERS[0])
    tier_color = tier_info[2]
    tier_name = tier_info[1]
    tier_bonus = tier_info[3]

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    # Get tiered gear image based on current tier
    gear_image_path = get_tiered_gear_image(slot_id, current_tier_id)

    col_img, col_info = st.columns([1, 3])

    with col_img:
        if gear_image_path.exists():
            st.image(str(gear_image_path), width=60)
        else:
            st.markdown(f'<div style="font-size:48px;text-align:center;">{slot_info["icon"]}</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-weight:bold;color:#E8F4F8;font-size:16px;{text_shadow}">{slot_info["name"]}</span>'
            f'<span style="background:{tier_color};color:#000;padding:4px 12px;border-radius:4px;'
            f'font-size:12px;font-weight:bold;">{tier_name}</span>'
            f'</div>'
            f'<div style="color:#B8D4E8;font-size:12px;margin-top:4px;{text_shadow}">'
            f'{slot_info["troop"]}: <span style="color:{tier_color};font-weight:bold;">+{tier_bonus:.1f}%</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Parse current tier to get color, subtier, stars
    current_tier_name = tier_info[1]
    current_parts = current_tier_name.lower().split()
    current_color = current_parts[0].capitalize()

    current_subtier = "Base"
    for p in current_parts:
        if p.startswith('t') and len(p) == 2 and p[1].isdigit():
            current_subtier = p.upper()
            break

    current_stars = 0
    import re
    star_match = re.search(r'(\d)★', current_tier_name)
    if star_match:
        current_stars = int(star_match.group(1))

    # 3 cascading selectors
    col_color, col_subtier, col_stars = st.columns(3)

    with col_color:
        colors = list(TIER_STRUCTURE.keys())
        color_idx = colors.index(current_color) if current_color in colors else 0
        selected_color = st.selectbox(
            "Color",
            options=colors,
            index=color_idx,
            key=f"gear_{slot_id}_color",
            label_visibility="collapsed"
        )

    with col_subtier:
        subtiers = list(TIER_STRUCTURE.get(selected_color, {"Base": [0]}).keys())
        subtier_idx = subtiers.index(current_subtier) if current_subtier in subtiers else 0
        selected_subtier = st.selectbox(
            "Tier",
            options=subtiers,
            index=min(subtier_idx, len(subtiers) - 1),
            key=f"gear_{slot_id}_subtier",
            label_visibility="collapsed"
        )

    with col_stars:
        stars_list = TIER_STRUCTURE.get(selected_color, {}).get(selected_subtier, [0])
        stars_idx = stars_list.index(current_stars) if current_stars in stars_list else 0
        selected_stars = st.selectbox(
            "Stars",
            options=stars_list,
            format_func=lambda x: f"{x}★",
            index=min(stars_idx, len(stars_list) - 1),
            key=f"gear_{slot_id}_stars",
            label_visibility="collapsed"
        )

    # Look up the tier_id from selections
    new_tier_id = TIER_LOOKUP.get((selected_color, selected_subtier, selected_stars), current_tier_id)

    # Save if changed
    if new_tier_id != current_tier_id:
        setattr(gear_data, quality_attr, new_tier_id)
        setattr(gear_data, level_attr, new_tier_id)  # Keep in sync
        db.commit()
        st.toast(f"Saved {slot_info['name']}")
        st.rerun()


def render_chief_gear_tab():
    """Render the Chief Gear tracking tab."""
    st.markdown("### Chief Gear")
    st.markdown("*Unlocks at Furnace Level 22*")

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    # Explanation
    st.markdown(
        f'<div style="background:rgba(74,144,217,0.15);border:1px solid rgba(74,144,217,0.3);'
        f'padding:12px;border-radius:8px;margin-bottom:16px;">'
        f'<div style="color:#E8F4F8;{text_shadow}">'
        f'Chief Gear boosts your troops based on type. Each piece progresses through tiers '
        f'(Green → Blue → Purple → Gold → Pink) with sub-tiers (T1, T2, T3) and stars (0-3★).'
        f'</div>'
        f'<div style="color:#FFD700;font-size:13px;margin-top:8px;{text_shadow}">'
        f'<strong>Set Bonus:</strong> 3-piece = Defense boost | 6-piece = Attack boost (same tier)'
        f'</div>'
        f'<div style="color:#2ECC71;font-size:11px;margin-top:6px;{text_shadow}">'
        f'All changes auto-save immediately.'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    gear_data = get_or_create_chief_gear()
    if gear_data is None:
        return

    # Group by troop type - Order: Lancer (cap/watch), Infantry (coat/pants), Marksman (belt/weapon)
    troop_groups = [
        ("Lancer", ["cap", "watch"]),
        ("Infantry", ["coat", "pants"]),
        ("Marksman", ["belt", "weapon"]),
    ]
    troop_colors = {"Infantry": "#E74C3C", "Lancer": "#2ECC71", "Marksman": "#3498DB"}

    for troop_type, slots in troop_groups:
        st.markdown(
            f'<div style="background:{troop_colors[troop_type]}22;border-left:4px solid {troop_colors[troop_type]};'
            f'padding:8px 12px;margin:16px 0 8px 0;border-radius:4px;">'
            f'<span style="color:{troop_colors[troop_type]};font-weight:bold;{text_shadow}">{troop_type} Gear</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        for i, slot_id in enumerate(slots):
            with col1 if i == 0 else col2:
                render_gear_slot(slot_id, GEAR_SLOTS[slot_id], gear_data)


def get_shape_symbol(level):
    """Get a unicode shape symbol for the charm level."""
    shapes = {
        1: "△",      # Triangle
        2: "◇",      # Diamond
        3: "□",      # Square
        4: "□",      # Square
        5: "⬠",      # Pentagon
        6: "⬠",      # Pentagon
        7: "⬡",      # Hexagon
        8: "⬡",      # Hexagon
        9: "○",      # Higher polygon (approx)
        10: "○",     # Octagon (approx)
        11: "○",     # Nonagon (approx)
        12: "○",     # Decagon (approx)
        13: "○",     # Hendecagon (approx)
        14: "○",     # Dodecagon (approx)
        15: "○",     # Near-circle
        16: "●",     # Circle (filled)
    }
    return shapes.get(level, "○")


def render_gear_charms(gear_id, gear_name, gear_data, charm_data, key_prefix):
    """Render a gear piece with its 3 charm slots in triangular layout.

    Each gear piece has 3 charms of the SAME type:
    - Cap/Watch → Keenness (Lancer)
    - Coat/Pants → Protection (Infantry)
    - Belt/Weapon → Vision (Marksman)

    Layout: 1 charm on top, 2 charms below (triangle formation)
    """
    # Map slot IDs to database fields for gear tier
    field_map = {
        "cap": "helmet",
        "watch": "ring",
        "coat": "armor",
        "pants": "boots",
        "belt": "gloves",
        "weapon": "amulet",
    }

    db_field = field_map.get(gear_id, gear_id)
    quality_attr = f"{db_field}_quality"

    # Get current gear tier for image
    current_tier_id = getattr(gear_data, quality_attr, 1) if gear_data else 1
    if current_tier_id < 1 or current_tier_id > len(GEAR_TIERS):
        current_tier_id = 1

    tier_info = TIER_BY_ID.get(current_tier_id, GEAR_TIERS[0])
    tier_name = tier_info[1]

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    # Get charm type info for this gear
    charm_info = GEAR_CHARM_TYPE[gear_id]
    charm_name = charm_info["name"]
    charm_icon = charm_info["icon"]
    charm_color = charm_info["color"]
    charm_troop = charm_info["troop"]

    # Get tiered gear image
    gear_image_path = get_tiered_gear_image(gear_id, current_tier_id)

    # Header: gear image + name + charm type
    col_img, col_info = st.columns([1, 3])

    with col_img:
        if gear_image_path.exists():
            st.image(str(gear_image_path), width=60)
        else:
            st.markdown(f'<div style="font-size:48px;text-align:center;">{GEAR_SLOTS[gear_id]["icon"]}</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(
            f'<div style="font-weight:bold;color:#E8F4F8;font-size:16px;{text_shadow}">{gear_name}</div>'
            f'<div style="color:#B8D4E8;font-size:12px;{text_shadow}">{tier_name}</div>'
            f'<div style="color:{charm_color};font-size:11px;margin-top:4px;{text_shadow}">'
            f'{charm_icon} 3× {charm_name} ({charm_troop})</div>',
            unsafe_allow_html=True
        )

    # Get current levels for all 3 slots
    slot_fields = [f"{gear_id}_slot_1", f"{gear_id}_slot_2", f"{gear_id}_slot_3"]
    current_levels = []
    for field in slot_fields:
        level = getattr(charm_data, field, "1") if charm_data else "1"
        if level is None:
            level = "1"
        current_levels.append(str(level))

    # Triangular layout: 1 on top (centered), 2 below
    # Top charm (slot 1) - centered
    _, col_top, _ = st.columns([1, 2, 1])
    with col_top:
        current_bonus = get_charm_bonus(current_levels[0])
        st.markdown(
            f'<div style="text-align:center;font-size:10px;{text_shadow}">'
            f'<span style="color:{charm_color};">{charm_icon}</span> '
            f'<span style="color:#FFD700;">+{current_bonus:.0f}%</span></div>',
            unsafe_allow_html=True
        )
        current_idx = CHARM_LEVEL_OPTIONS.index(current_levels[0]) if current_levels[0] in CHARM_LEVEL_OPTIONS else 0
        new_level = st.selectbox(
            "Slot 1",
            options=CHARM_LEVEL_OPTIONS,
            index=current_idx,
            format_func=format_charm_level_display,
            key=f"{key_prefix}_{slot_fields[0]}",
            label_visibility="collapsed"
        )
        if charm_data and new_level != current_levels[0]:
            setattr(charm_data, slot_fields[0], new_level)
            db.commit()
            st.toast(f"Saved {charm_name}")
            st.rerun()

    # Bottom two charms (slots 2 and 3)
    col_left, col_right = st.columns(2)

    for i, col in enumerate([col_left, col_right]):
        slot_idx = i + 1  # slots 2 and 3
        with col:
            current_bonus = get_charm_bonus(current_levels[slot_idx])
            st.markdown(
                f'<div style="text-align:center;font-size:10px;{text_shadow}">'
                f'<span style="color:{charm_color};">{charm_icon}</span> '
                f'<span style="color:#FFD700;">+{current_bonus:.0f}%</span></div>',
                unsafe_allow_html=True
            )
            current_idx = CHARM_LEVEL_OPTIONS.index(current_levels[slot_idx]) if current_levels[slot_idx] in CHARM_LEVEL_OPTIONS else 0
            new_level = st.selectbox(
                f"Slot {slot_idx + 1}",
                options=CHARM_LEVEL_OPTIONS,
                index=current_idx,
                format_func=format_charm_level_display,
                key=f"{key_prefix}_{slot_fields[slot_idx]}",
                label_visibility="collapsed"
            )
            if charm_data and new_level != current_levels[slot_idx]:
                setattr(charm_data, slot_fields[slot_idx], new_level)
                db.commit()
                st.toast(f"Saved {charm_name}")
                st.rerun()


def render_chief_charms_tab():
    """Render the Chief Charms tracking tab."""
    st.markdown("### Chief Charms")
    st.markdown("*Unlocks at Furnace Level 25 | Level 16 requires Gen 7*")

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    # Explanation
    st.markdown(
        f'<div style="background:rgba(74,144,217,0.15);border:1px solid rgba(74,144,217,0.3);'
        f'padding:12px;border-radius:8px;margin-bottom:16px;">'
        f'<div style="color:#E8F4F8;{text_shadow}">'
        f'Each gear piece has <strong>3 charm slots</strong> of the <strong>same type</strong> (18 total). '
        f'Charms progress through sub-levels at 4+ (e.g., 4-1 → 4-2 → 4-3 → 5).'
        f'</div>'
        f'<div style="color:#B8D4E8;font-size:12px;margin-top:8px;{text_shadow}">'
        f'<span style="color:#2ECC71;">⚡ Keenness</span> = Cap & Watch (Lancer) &nbsp;|&nbsp; '
        f'<span style="color:#E74C3C;">🛡️ Protection</span> = Coat & Pants (Infantry) &nbsp;|&nbsp; '
        f'<span style="color:#3498DB;">👁️ Vision</span> = Belt & Weapon (Marksman)'
        f'</div>'
        f'<div style="color:#888;font-size:11px;margin-top:6px;{text_shadow}">'
        f'Shape progression: △ Triangle → ◇ Diamond → □ Square → ⬠ Pentagon → ⬡ Hexagon → ● Circle'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    charm_data = get_or_create_chief_charms()
    gear_data = get_or_create_chief_gear()
    if charm_data is None or gear_data is None:
        return

    # Gear grouped by troop type with game names
    # Order: Lancer (top), Infantry (middle), Marksman (bottom)
    troop_groups = [
        ("Lancer", "#2ECC71", [
            ("cap", "Gale's Helm"),
            ("watch", "Astral Pointer"),
        ]),
        ("Infantry", "#E74C3C", [
            ("coat", "Valor's Embrace"),
            ("pants", "Triumph's Stride"),
        ]),
        ("Marksman", "#3498DB", [
            ("belt", "Ring of Eureka"),
            ("weapon", "Starfier's Melody"),
        ]),
    ]

    for troop_type, troop_color, gear_pieces in troop_groups:
        st.markdown(
            f'<div style="background:{troop_color}22;border-left:4px solid {troop_color};'
            f'padding:8px 12px;margin:16px 0 8px 0;border-radius:4px;">'
            f'<span style="color:{troop_color};font-weight:bold;{text_shadow}">{troop_type} Gear Charms</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        for i, (gear_id, gear_name) in enumerate(gear_pieces):
            with col1 if i == 0 else col2:
                render_gear_charms(gear_id, gear_name, gear_data, charm_data, f"charm_{troop_type}")

    # Summary by charm type (which corresponds to troop buff)
    st.markdown("---")
    st.markdown("### Summary by Charm Type")

    def get_main_level(level_str):
        """Extract main level from level string (e.g., '4-2' -> 4)."""
        main, _ = parse_charm_level(level_str)
        return main

    # Calculate totals for each charm type (6 charms each = 2 gear pieces × 3 slots)
    # Keenness: Cap + Watch (Lancer gear)
    keenness_charms = ["cap_slot_1", "cap_slot_2", "cap_slot_3",
                       "watch_slot_1", "watch_slot_2", "watch_slot_3"]
    # Protection: Coat + Pants (Infantry gear)
    protection_charms = ["coat_slot_1", "coat_slot_2", "coat_slot_3",
                         "pants_slot_1", "pants_slot_2", "pants_slot_3"]
    # Vision: Belt + Weapon (Marksman gear)
    vision_charms = ["belt_slot_1", "belt_slot_2", "belt_slot_3",
                     "weapon_slot_1", "weapon_slot_2", "weapon_slot_3"]

    keenness_levels = [get_main_level(getattr(charm_data, c, "1") or "1") for c in keenness_charms]
    protection_levels = [get_main_level(getattr(charm_data, c, "1") or "1") for c in protection_charms]
    vision_levels = [get_main_level(getattr(charm_data, c, "1") or "1") for c in vision_charms]

    keenness_total = sum(keenness_levels)
    protection_total = sum(protection_levels)
    vision_total = sum(vision_levels)

    col1, col2, col3 = st.columns(3)
    with col1:
        avg_level = keenness_total / 6
        avg_bonus = CHARM_STATS.get(int(avg_level), {"bonus": 9.0})["bonus"]
        st.markdown(
            f'<div style="background:rgba(46,204,113,0.15);padding:12px;border-radius:8px;text-align:center;">'
            f'<div style="font-weight:bold;color:#2ECC71;{text_shadow}">⚡ Keenness</div>'
            f'<div style="font-size:13px;color:#B8D4E8;{text_shadow}">Lancer Buff</div>'
            f'<div style="font-size:24px;color:#E8F4F8;{text_shadow}">{keenness_total}/96</div>'
            f'<div style="font-size:12px;color:#B8D4E8;{text_shadow}">Avg Lv.{avg_level:.1f} (~{avg_bonus:.0f}%)</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col2:
        avg_level = protection_total / 6
        avg_bonus = CHARM_STATS.get(int(avg_level), {"bonus": 9.0})["bonus"]
        st.markdown(
            f'<div style="background:rgba(231,76,60,0.15);padding:12px;border-radius:8px;text-align:center;">'
            f'<div style="font-weight:bold;color:#E74C3C;{text_shadow}">🛡️ Protection</div>'
            f'<div style="font-size:13px;color:#B8D4E8;{text_shadow}">Infantry Buff</div>'
            f'<div style="font-size:24px;color:#E8F4F8;{text_shadow}">{protection_total}/96</div>'
            f'<div style="font-size:12px;color:#B8D4E8;{text_shadow}">Avg Lv.{avg_level:.1f} (~{avg_bonus:.0f}%)</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col3:
        avg_level = vision_total / 6
        avg_bonus = CHARM_STATS.get(int(avg_level), {"bonus": 9.0})["bonus"]
        st.markdown(
            f'<div style="background:rgba(52,152,219,0.15);padding:12px;border-radius:8px;text-align:center;">'
            f'<div style="font-weight:bold;color:#3498DB;{text_shadow}">👁️ Vision</div>'
            f'<div style="font-size:13px;color:#B8D4E8;{text_shadow}">Marksman Buff</div>'
            f'<div style="font-size:24px;color:#E8F4F8;{text_shadow}">{vision_total}/96</div>'
            f'<div style="font-size:12px;color:#B8D4E8;{text_shadow}">Avg Lv.{avg_level:.1f} (~{avg_bonus:.0f}%)</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_upgrade_priority_tab():
    """Render upgrade priority guidance."""
    st.markdown("### Upgrade Priority")

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    st.markdown(
        f'<div style="background:rgba(74,144,217,0.15);border:1px solid rgba(74,144,217,0.3);'
        f'padding:16px;border-radius:8px;margin-bottom:16px;">'
        f'<div style="color:#FFD700;font-weight:bold;margin-bottom:8px;{text_shadow}">When to Focus on Chief Gear/Charms</div>'
        f'<div style="color:#E8F4F8;{text_shadow}">'
        f'Chief Gear and Charms become increasingly important as you progress. Here\'s the general priority:'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    priorities = [
        ("Early Game (F1-22)", "Focus on heroes and furnace. Chief gear unlocks at F22.", "#95A5A6"),
        ("Mid Game (F22-FC)", "Start upgrading Chief Gear. Keep all pieces at same tier for set bonus.", "#3498DB"),
        ("Late Game (FC+)", "Chief Gear/Charms become major power source. Balance with hero investment.", "#2ECC71"),
    ]

    for stage, desc, color in priorities:
        st.markdown(
            f'<div style="border-left:4px solid {color};padding:12px;margin-bottom:8px;'
            f'background:rgba(74,144,217,0.1);border-radius:4px;">'
            f'<div style="font-weight:bold;color:{color};{text_shadow}">{stage}</div>'
            f'<div style="color:#B8D4E8;font-size:13px;{text_shadow}">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### Gear Upgrade Order")
    st.markdown(
        f'<div style="color:#E8F4F8;{text_shadow}">'
        f'<strong>1. Infantry gear first</strong> (Coat & Pants) - Frontline absorbs damage<br>'
        f'<strong>2. Marksman gear second</strong> (Belt & Weapon) - Key damage dealers<br>'
        f'<strong>3. Lancer gear last</strong> (Cap & Watch) - Less exposed to direct fire'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("#### Key Tips")
    tips = [
        "Keep all 6 gear pieces at the same tier before advancing any single piece (set bonus)",
        "Gold T2 3★ unlocks the Enhancement Material Exchange",
        "Charms level 12+ require Jewel Secrets - plan your materials",
        "Charm level 16 requires your state to reach Generation 7",
    ]
    for tip in tips:
        st.markdown(f"- {tip}")


def render_chief_page():
    """Render the main chief page with tabs."""
    st.markdown("# Chief Equipment")
    st.markdown("Track your Chief Gear and Charms progression.")

    tab1, tab2, tab3 = st.tabs(["Chief Gear", "Chief Charms", "Upgrade Priority"])

    with tab1:
        render_chief_gear_tab()

    with tab2:
        render_chief_charms_tab()

    with tab3:
        render_upgrade_priority_tab()


# Main
render_chief_page()

# Close database session
db.close()
