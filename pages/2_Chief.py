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

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# Gear image paths
GEAR_IMAGES = {
    "cap": "assets/chief_gear/hat.png",
    "watch": "assets/chief_gear/watch.png",
    "coat": "assets/chief_gear/coat.png",
    "pants": "assets/chief_gear/pants.png",
    "belt": "assets/chief_gear/ring.png",  # belt uses ring image
    "weapon": "assets/chief_gear/staff.png",
}

# Charm types per gear slot
CHARM_TYPES = {
    "protection": {"name": "Protection", "icon": "🛡️", "troop": "Infantry", "color": "#2ECC71"},
    "keenness": {"name": "Keenness", "icon": "⚡", "troop": "Lancer", "color": "#3498DB"},
    "vision": {"name": "Vision", "icon": "👁️", "troop": "Marksman", "color": "#F1C40F"},
}


def get_or_create_chief_gear():
    """Get or create chief gear record for current profile."""
    gear = db.query(UserChiefGear).filter(UserChiefGear.profile_id == profile.id).first()
    if not gear:
        gear = UserChiefGear(profile_id=profile.id)
        db.add(gear)
        db.commit()
        db.refresh(gear)
    return gear


def get_or_create_chief_charms():
    """Get or create chief charms record for current profile."""
    charms = db.query(UserChiefCharm).filter(UserChiefCharm.profile_id == profile.id).first()
    if not charms:
        charms = UserChiefCharm(profile_id=profile.id)
        db.add(charms)
        db.commit()
        db.refresh(charms)
    return charms


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
    current_tier_id = getattr(gear_data, quality_attr, 1)
    if current_tier_id < 1 or current_tier_id > len(GEAR_TIERS):
        current_tier_id = 1

    tier_info = TIER_BY_ID.get(current_tier_id, GEAR_TIERS[0])
    tier_color = tier_info[2]
    tier_name = tier_info[1]
    tier_bonus = tier_info[3]

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    # Show gear image if available
    gear_image_path = PROJECT_ROOT / GEAR_IMAGES.get(slot_id, "")

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

    # Tier selector
    tier_index = current_tier_id - 1
    new_tier_id = st.selectbox(
        f"Select {slot_info['name']} Tier",
        options=[t[0] for t in GEAR_TIERS],
        format_func=lambda x: TIER_BY_ID[x][1],
        index=tier_index,
        key=f"gear_{slot_id}_tier",
        label_visibility="collapsed"
    )

    # Save if changed
    if new_tier_id != current_tier_id:
        setattr(gear_data, quality_attr, new_tier_id)
        setattr(gear_data, level_attr, new_tier_id)  # Keep in sync
        db.commit()
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
        f'</div>',
        unsafe_allow_html=True
    )

    gear_data = get_or_create_chief_gear()

    # Group by troop type
    troop_groups = {
        "Infantry": ["coat", "pants"],
        "Lancer": ["cap", "watch"],
        "Marksman": ["belt", "weapon"],
    }
    troop_colors = {"Infantry": "#E74C3C", "Lancer": "#2ECC71", "Marksman": "#3498DB"}

    for troop_type, slots in troop_groups.items():
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


def render_single_charm(gear_name, charm_type, charm_data, key_prefix):
    """Render a single charm with its level selector."""
    charm_info = CHARM_TYPES[charm_type]
    field_name = f"{gear_name}_{charm_type}"
    current_level = getattr(charm_data, field_name, 1)
    charm_stat = CHARM_STATS.get(current_level, {"bonus": 9.0, "shape": "Triangle"})

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    # Try to load charm image
    charm_image_path = PROJECT_ROOT / "assets" / "chief_charms" / f"lvl{current_level}.png"

    col_img, col_info, col_slider = st.columns([1, 2, 3])

    with col_img:
        if charm_image_path.exists():
            st.image(str(charm_image_path), width=40)
        else:
            st.markdown(f'<div style="font-size:24px;text-align:center;">{charm_info["icon"]}</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(
            f'<div style="color:{charm_info["color"]};font-weight:bold;font-size:13px;{text_shadow}">'
            f'{charm_info["name"]}</div>'
            f'<div style="color:#B8D4E8;font-size:11px;{text_shadow}">'
            f'Lv.{current_level} · {charm_stat["shape"]}</div>',
            unsafe_allow_html=True
        )

    with col_slider:
        new_level = st.slider(
            f"{gear_name} {charm_type}",
            min_value=1,
            max_value=16,
            value=current_level,
            key=f"{key_prefix}_{field_name}",
            label_visibility="collapsed"
        )

        if new_level != current_level:
            setattr(charm_data, field_name, new_level)
            db.commit()
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
        f'Each gear piece has <strong>3 charm slots</strong> - one per troop type. '
        f'Each charm levels from 1 to 16 independently. That\'s 18 charms total (6 gear × 3 types).'
        f'</div>'
        f'<div style="margin-top:8px;display:flex;gap:16px;flex-wrap:wrap;">'
        f'<span style="color:#2ECC71;{text_shadow}">🛡️ Protection = Infantry</span>'
        f'<span style="color:#3498DB;{text_shadow}">⚡ Keenness = Lancer</span>'
        f'<span style="color:#F1C40F;{text_shadow}">👁️ Vision = Marksman</span>'
        f'</div>'
        f'<div style="color:#B8D4E8;font-size:12px;margin-top:8px;{text_shadow}">'
        f'Shape progression: Triangle (1) → Diamond (2) → Square (3-4) → Pentagon (5-6) → '
        f'Hexagon (7-8) → Higher polygons → Circle (16)'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    charm_data = get_or_create_chief_charms()

    # Organize by gear piece - each piece has 3 charms
    gear_pieces = [
        ("cap", "Cap", "🎩", "#2ECC71"),
        ("watch", "Watch", "⌚", "#2ECC71"),
        ("coat", "Coat", "🧥", "#E74C3C"),
        ("pants", "Pants", "👖", "#E74C3C"),
        ("belt", "Belt", "🎯", "#3498DB"),
        ("weapon", "Weapon", "⚔️", "#3498DB"),
    ]

    for gear_id, gear_name, gear_icon, gear_color in gear_pieces:
        with st.expander(f"{gear_icon} {gear_name} Charms", expanded=False):
            for charm_type in ["protection", "keenness", "vision"]:
                render_single_charm(gear_id, charm_type, charm_data, f"charm_{gear_id}")
            st.markdown("")

    # Summary by troop type
    st.markdown("---")
    st.markdown("### Summary by Troop Type")

    # Calculate totals for each troop type (6 charms each)
    infantry_charms = ["cap_protection", "watch_protection", "coat_protection",
                       "pants_protection", "belt_protection", "weapon_protection"]
    lancer_charms = ["cap_keenness", "watch_keenness", "coat_keenness",
                     "pants_keenness", "belt_keenness", "weapon_keenness"]
    marksman_charms = ["cap_vision", "watch_vision", "coat_vision",
                       "pants_vision", "belt_vision", "weapon_vision"]

    infantry_total = sum(getattr(charm_data, c, 1) for c in infantry_charms)
    lancer_total = sum(getattr(charm_data, c, 1) for c in lancer_charms)
    marksman_total = sum(getattr(charm_data, c, 1) for c in marksman_charms)

    col1, col2, col3 = st.columns(3)
    with col1:
        avg_level = infantry_total / 6
        avg_bonus = CHARM_STATS.get(int(avg_level), {"bonus": 9.0})["bonus"]
        st.markdown(
            f'<div style="background:rgba(231,76,60,0.15);padding:12px;border-radius:8px;text-align:center;">'
            f'<div style="font-weight:bold;color:#E74C3C;{text_shadow}">🛡️ Infantry</div>'
            f'<div style="font-size:24px;color:#E8F4F8;{text_shadow}">{infantry_total}/96</div>'
            f'<div style="font-size:12px;color:#B8D4E8;{text_shadow}">Avg Lv.{avg_level:.1f} (~{avg_bonus:.0f}%)</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col2:
        avg_level = lancer_total / 6
        avg_bonus = CHARM_STATS.get(int(avg_level), {"bonus": 9.0})["bonus"]
        st.markdown(
            f'<div style="background:rgba(46,204,113,0.15);padding:12px;border-radius:8px;text-align:center;">'
            f'<div style="font-weight:bold;color:#2ECC71;{text_shadow}">⚡ Lancer</div>'
            f'<div style="font-size:24px;color:#E8F4F8;{text_shadow}">{lancer_total}/96</div>'
            f'<div style="font-size:12px;color:#B8D4E8;{text_shadow}">Avg Lv.{avg_level:.1f} (~{avg_bonus:.0f}%)</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col3:
        avg_level = marksman_total / 6
        avg_bonus = CHARM_STATS.get(int(avg_level), {"bonus": 9.0})["bonus"]
        st.markdown(
            f'<div style="background:rgba(52,152,219,0.15);padding:12px;border-radius:8px;text-align:center;">'
            f'<div style="font-weight:bold;color:#3498DB;{text_shadow}">👁️ Marksman</div>'
            f'<div style="font-size:24px;color:#E8F4F8;{text_shadow}">{marksman_total}/96</div>'
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
