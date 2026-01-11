"""
Hero Management Page - Track your heroes and their progress.
"""

import streamlit as st
import json
from pathlib import Path
import sys
import base64

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Hero images directory
HERO_IMAGES_DIR = PROJECT_ROOT / "assets" / "heroes"

from database.db import init_db, get_db, get_or_create_profile
from database.models import Hero, UserHero

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load hero data
heroes_file = PROJECT_ROOT / "data" / "heroes.json"
with open(heroes_file, encoding='utf-8') as f:
    HERO_DATA = json.load(f)

GEAR_SYSTEM = HERO_DATA.get('gear_system', {})
QUALITY_LEVELS = GEAR_SYSTEM.get('quality_levels', {})
GEAR_SLOTS = GEAR_SYSTEM.get('slots', ['Weapon', 'Armor', 'Helmet', 'Boots'])
TIER_DESCRIPTIONS = HERO_DATA.get('tier_descriptions', {})

# Hero special roles - what each hero is good for beyond combat
HERO_ROLES = {
    # Gatherers (Growth heroes for specific resources)
    "Smith": {"role": "Gatherer", "detail": "Iron", "icon": "Fe", "color": "#95A5A6"},
    "Eugene": {"role": "Gatherer", "detail": "Wood", "icon": "W", "color": "#8B4513"},
    "Charlie": {"role": "Gatherer", "detail": "Coal", "icon": "C", "color": "#34495E"},
    "Cloris": {"role": "Gatherer", "detail": "Meat", "icon": "M", "color": "#E74C3C"},

    # Stamina/Intel - reduces stamina for beast hunting and intel missions
    "Gina": {"role": "Stamina Saver", "detail": "-20% stamina (hunts/intel)", "icon": "S", "color": "#F39C12"},

    # Research & Building speed boosts
    "Jasser": {"role": "Research Boost", "detail": "+15% research speed", "icon": "R", "color": "#9B59B6"},
    "Zinman": {"role": "Construction", "detail": "+15% build speed, -15% cost", "icon": "B", "color": "#E67E22"},

    # Rally Joiners - Attack (put in leftmost slot when joining rallies)
    "Jessie": {"role": "BEST Attack Joiner", "detail": "+25% DMG dealt (all troops)", "icon": "ATK", "color": "#E74C3C"},
    "Seo-yoon": {"role": "Attack Joiner", "detail": "+25% ATK (all troops)", "icon": "ATK", "color": "#E74C3C"},
    "Natalia": {"role": "Rally Leader", "detail": "+30% DMG, +15% Lethality", "icon": "RL", "color": "#F1C40F"},

    # Rally Joiners - Defense/Garrison (put in leftmost slot when reinforcing)
    "Sergey": {"role": "BEST Garrison Joiner", "detail": "-20% DMG taken (all troops)", "icon": "DEF", "color": "#3498DB"},
    "Logan": {"role": "Best Defender", "detail": "Essential for garrison defense", "icon": "DEF", "color": "#3498DB"},

    # Healers - essential for exploration/PvE content
    "Philly": {"role": "BEST Healer", "detail": "Essential for exploration/PvE", "icon": "HP", "color": "#2ECC71"},

    # Special combat roles
    "Jeronimo": {"role": "Rally Leader", "detail": "+25% DMG, +25% ATK to all", "icon": "RL", "color": "#F1C40F"},
    "Patrick": {"role": "Top Rally Joiner", "detail": "+100% extra damage (Sneak Strike)", "icon": "ATK", "color": "#9B59B6"},
    "Ahmose": {"role": "Defensive Infantry", "detail": "Shield + 30% DMG reflect", "icon": "DEF", "color": "#3498DB"},
}


def get_tier_color(tier: str) -> str:
    colors = {
        "S+": "#FF4444", "S": "#FF8C00", "A": "#9932CC",
        "B": "#4169E1", "C": "#32CD32", "D": "#808080"
    }
    return colors.get(tier, "#808080")


def get_hero_role_badge(hero_name: str) -> str:
    """Get HTML badge for hero's special role, if any."""
    role_info = HERO_ROLES.get(hero_name)
    if not role_info:
        return ""

    role = role_info["role"]
    detail = role_info["detail"]
    color = role_info["color"]

    return f'''<div style="
        display:inline-block;
        background:{color}22;
        border:1px solid {color};
        border-radius:4px;
        padding:2px 6px;
        font-size:10px;
        color:{color};
        margin-top:2px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    " title="{detail}"><b>{role}</b>: {detail}</div>'''


def get_class_color(hero_class: str) -> str:
    colors = {"Infantry": "#E74C3C", "Marksman": "#3498DB", "Lancer": "#2ECC71"}
    return colors.get(hero_class, "#808080")


def get_rarity_color(rarity: str) -> str:
    colors = {"Rare": "#3498DB", "Epic": "#9B59B6", "Legendary": "#F1C40F"}
    return colors.get(rarity, "#808080")


def get_class_symbol(hero_class: str) -> str:
    symbols = {"Infantry": "🛡️", "Marksman": "🏹", "Lancer": "⚔️"}
    return symbols.get(hero_class, "?")


def get_quality_color(quality: int) -> str:
    return QUALITY_LEVELS.get(str(quality), {}).get('color', '#666666')


def get_quality_name(quality: int) -> str:
    return QUALITY_LEVELS.get(str(quality), {}).get('name', 'None')


@st.cache_data
def get_hero_image_base64(image_filename: str) -> str:
    image_path = HERO_IMAGES_DIR / image_filename
    if image_path.exists():
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            ext = image_filename.split('.')[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64,{data}"
    return None


def get_user_hero(hero_name: str):
    hero_ref = db.query(Hero).filter(Hero.name == hero_name).first()
    if not hero_ref:
        return None
    return db.query(UserHero).filter(
        UserHero.profile_id == profile.id,
        UserHero.hero_id == hero_ref.id
    ).first()


def save_user_hero(hero_data: dict, level: int = 1, stars: int = 0, ascension: int = 0,
                   exp_skill1: int = 1, exp_skill2: int = 1, exp_skill3: int = 1,
                   exped_skill1: int = 1, exped_skill2: int = 1, exped_skill3: int = 1,
                   gear_data: dict = None, mythic_data: dict = None):
    hero_ref = db.query(Hero).filter(Hero.name == hero_data['name']).first()
    if not hero_ref:
        hero_ref = Hero(
            name=hero_data['name'],
            generation=hero_data['generation'],
            hero_class=hero_data['hero_class'],
            rarity=hero_data['rarity'],
            tier_overall=hero_data['tier_overall'],
            tier_expedition=hero_data['tier_expedition'],
            tier_exploration=hero_data['tier_exploration'],
            image_filename=hero_data['image_filename']
        )
        db.add(hero_ref)
        db.commit()
        db.refresh(hero_ref)

    user_hero = db.query(UserHero).filter(
        UserHero.profile_id == profile.id,
        UserHero.hero_id == hero_ref.id
    ).first()

    if user_hero:
        user_hero.level = level
        user_hero.stars = stars
        user_hero.ascension_tier = ascension
        user_hero.exploration_skill_1_level = exp_skill1
        user_hero.exploration_skill_2_level = exp_skill2
        user_hero.exploration_skill_3_level = exp_skill3
        user_hero.expedition_skill_1_level = exped_skill1
        user_hero.expedition_skill_2_level = exped_skill2
        user_hero.expedition_skill_3_level = exped_skill3
        if gear_data:
            user_hero.gear_slot1_quality = gear_data.get('slot1_quality', 0)
            user_hero.gear_slot1_level = gear_data.get('slot1_level', 0)
            user_hero.gear_slot1_mastery = gear_data.get('slot1_mastery', 0)
            user_hero.gear_slot2_quality = gear_data.get('slot2_quality', 0)
            user_hero.gear_slot2_level = gear_data.get('slot2_level', 0)
            user_hero.gear_slot2_mastery = gear_data.get('slot2_mastery', 0)
            user_hero.gear_slot3_quality = gear_data.get('slot3_quality', 0)
            user_hero.gear_slot3_level = gear_data.get('slot3_level', 0)
            user_hero.gear_slot3_mastery = gear_data.get('slot3_mastery', 0)
            user_hero.gear_slot4_quality = gear_data.get('slot4_quality', 0)
            user_hero.gear_slot4_level = gear_data.get('slot4_level', 0)
            user_hero.gear_slot4_mastery = gear_data.get('slot4_mastery', 0)
        if mythic_data:
            user_hero.mythic_gear_unlocked = mythic_data.get('unlocked', False)
            user_hero.mythic_gear_quality = mythic_data.get('quality', 0)
            user_hero.mythic_gear_level = mythic_data.get('level', 0)
            user_hero.mythic_gear_mastery = mythic_data.get('mastery', 0)
    else:
        user_hero = UserHero(
            profile_id=profile.id,
            hero_id=hero_ref.id,
            level=level,
            stars=stars,
            ascension_tier=ascension,
            exploration_skill_1_level=exp_skill1,
            exploration_skill_2_level=exp_skill2,
            exploration_skill_3_level=exp_skill3,
            expedition_skill_1_level=exped_skill1,
            expedition_skill_2_level=exped_skill2,
            expedition_skill_3_level=exped_skill3
        )
        db.add(user_hero)

    db.commit()
    return True


def remove_user_hero(hero_name: str):
    hero_ref = db.query(Hero).filter(Hero.name == hero_name).first()
    if hero_ref:
        user_hero = db.query(UserHero).filter(
            UserHero.profile_id == profile.id,
            UserHero.hero_id == hero_ref.id
        ).first()
        if user_hero:
            db.delete(user_hero)
            db.commit()


def render_hero_row(hero: dict, user_hero, hero_key: str):
    """Render a single hero row with large image on left."""
    is_owned = user_hero is not None
    tier = hero['tier_overall']
    tier_color = get_tier_color(tier)
    tier_desc = TIER_DESCRIPTIONS.get(tier, '')
    class_color = get_class_color(hero['hero_class'])
    rarity_color = get_rarity_color(hero.get('rarity', 'Legendary'))

    # Get image
    image_filename = hero.get('image_filename', '')
    hero_image_b64 = get_hero_image_base64(image_filename) if image_filename else None

    # Opacity for heroes not owned
    opacity = "1.0" if is_owned else "0.4"
    border_color = rarity_color if is_owned else "#555"

    # Stars and ascension display
    if user_hero:
        filled = "★" * user_hero.stars
        empty = "☆" * (5 - user_hero.stars)
        stars_html = f'<span style="color:#FFD700;">{filled}</span><span style="color:#4A5568;">{empty}</span>'
        # Show ascension pips if not at max stars
        if user_hero.stars < 5 and user_hero.ascension_tier > 0:
            asc_filled = "●" * user_hero.ascension_tier
            asc_empty = "○" * (5 - user_hero.ascension_tier)
            stars_html += f' <span style="color:#9B59B6;font-size:10px;">{asc_filled}{asc_empty}</span>'
        level_display = f"Lv.{user_hero.level}"
    else:
        stars_html = '<span style="color:#4A5568;">☆☆☆☆☆</span>'
        level_display = "-"

    # Main layout: Large image on left, content on right
    img_col, content_col = st.columns([1, 6])

    with img_col:
        # Large hero image
        if hero_image_b64:
            st.markdown(f'<img src="{hero_image_b64}" style="width:80px;height:80px;border-radius:8px;border:3px solid {border_color};opacity:{opacity};">', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="width:80px;height:80px;background:#1E2A3A;border-radius:8px;border:3px solid {border_color};display:flex;align-items:center;justify-content:center;font-size:32px;opacity:{opacity};">{get_class_symbol(hero["hero_class"])}</div>', unsafe_allow_html=True)

    with content_col:
        # Info row: Name | Class | Tier | Gen | Stars | Level | Owned checkbox
        info_cols = st.columns([2.5, 1.5, 1, 1, 2, 1, 1.5])

        with info_cols[0]:
            # Hero name and role badge
            role_badge = get_hero_role_badge(hero["name"])
            name_html = f'<div style="font-weight:bold;color:#E8F4F8;opacity:{opacity};padding-top:4px;font-size:16px;">{hero["name"]}</div>'
            if role_badge:
                name_html += role_badge
            st.markdown(name_html, unsafe_allow_html=True)

        with info_cols[1]:
            st.markdown(f'<div style="color:{class_color};opacity:{opacity};padding-top:4px;">{hero["hero_class"]}</div>', unsafe_allow_html=True)

        with info_cols[2]:
            st.markdown(f'<span style="background:{tier_color};color:white;padding:2px 8px;border-radius:4px;font-size:12px;opacity:{opacity};" title="{tier_desc}">{tier}</span>', unsafe_allow_html=True)

        with info_cols[3]:
            st.markdown(f'<div style="color:#B8D4E8;opacity:{opacity};padding-top:4px;">G{hero["generation"]}</div>', unsafe_allow_html=True)

        with info_cols[4]:
            st.markdown(f'<div style="opacity:{opacity};padding-top:4px;">{stars_html}</div>', unsafe_allow_html=True)

        with info_cols[5]:
            st.markdown(f'<div style="color:#4A90D9;opacity:{opacity};padding-top:4px;">{level_display}</div>', unsafe_allow_html=True)

        with info_cols[6]:
            # "Owned" checkbox with label
            new_owned = st.checkbox("Owned", value=is_owned, key=f"owned_{hero_key}")
            if new_owned != is_owned:
                if new_owned:
                    save_user_hero(hero)
                    # Mark this hero to auto-expand after rerun
                    st.session_state.auto_expand_hero = hero_key
                    st.rerun()
                else:
                    remove_user_hero(hero['name'])
                    st.rerun()

        # Expandable section below info row
        if is_owned:
            # Check if this hero should auto-expand (just marked as owned)
            should_expand = st.session_state.get('auto_expand_hero') == hero_key
            if should_expand:
                st.session_state.auto_expand_hero = None  # Clear after use
            with st.expander(f"Edit {hero['name']}", expanded=should_expand):
                render_hero_editor(hero, user_hero, hero_key)
        else:
            with st.expander(f"View {hero['name']} — check 'Owned' to track progress", expanded=False):
                render_hero_info(hero)


def render_skill_with_tooltip(skill_name: str, skill_desc: str = None) -> str:
    """Return HTML for a skill name with hover tooltip."""
    tooltip = skill_desc if skill_desc else "Skill description coming soon"
    return f'<span title="{tooltip}" style="cursor:help;border-bottom:1px dotted #4A90D9;">{skill_name}</span>'


def render_hero_info(hero: dict):
    """Render read-only hero info for locked heroes."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Exploration Skills**")
        skill1 = render_skill_with_tooltip(hero.get('exploration_skill_1', 'Unknown'), hero.get('exploration_skill_1_desc'))
        st.markdown(f"• {skill1}", unsafe_allow_html=True)
        skill2 = render_skill_with_tooltip(hero.get('exploration_skill_2', 'Unknown'), hero.get('exploration_skill_2_desc'))
        st.markdown(f"• {skill2}", unsafe_allow_html=True)
        if hero.get('exploration_skill_3'):
            skill3 = render_skill_with_tooltip(hero['exploration_skill_3'], hero.get('exploration_skill_3_desc'))
            st.markdown(f"• {skill3}", unsafe_allow_html=True)

    with col2:
        st.markdown("**Expedition Skills**")
        skill1 = render_skill_with_tooltip(hero.get('expedition_skill_1', 'Unknown'), hero.get('expedition_skill_1_desc'))
        st.markdown(f"• {skill1}", unsafe_allow_html=True)
        skill2 = render_skill_with_tooltip(hero.get('expedition_skill_2', 'Unknown'), hero.get('expedition_skill_2_desc'))
        st.markdown(f"• {skill2}", unsafe_allow_html=True)
        if hero.get('expedition_skill_3'):
            skill3 = render_skill_with_tooltip(hero['expedition_skill_3'], hero.get('expedition_skill_3_desc'))
            st.markdown(f"• {skill3}", unsafe_allow_html=True)

    if hero.get('best_use'):
        st.markdown(f"**Best Use:** {hero['best_use']}")

    if hero.get('mythic_gear'):
        st.markdown(f"**Mythic Gear:** {hero['mythic_gear']}")

    st.info("Check 'Owned' above to track this hero's level, skills, and gear.")


def render_skill_row(skill_name: str, current_level: int, key: str, skill_desc: str = None) -> int:
    """Render a skill with name and level selector. Returns selected level."""
    col_name, col_level = st.columns([3, 1])
    with col_name:
        # Display skill name with visual pips and tooltip
        pips = "●" * current_level + "○" * (5 - current_level)
        tooltip = skill_desc if skill_desc else "Skill description coming soon"
        # Wrap skill name in span with title for hover tooltip
        st.markdown(f'<div style="font-size:15px;color:#B8D4E8;line-height:1.8;"><span title="{tooltip}" style="cursor:help;border-bottom:1px dotted #4A90D9;">{skill_name[:25]}</span> <span style="color:#4A90D9;font-size:18px;">{pips}</span></div>', unsafe_allow_html=True)
    with col_level:
        selected = st.selectbox("Lv", [1, 2, 3, 4, 5], index=current_level - 1, key=key, label_visibility="collapsed")
    return selected


def render_hero_editor(hero: dict, existing, hero_key: str):
    """Render the editor for an unlocked hero - compact visual layout."""

    # Row 1: Level, Stars, Ascension
    col_lvl, col_stars, col_asc = st.columns([2, 2, 2])

    with col_lvl:
        st.markdown('<div style="font-size:12px;color:#B8D4E8;">LEVEL</div>', unsafe_allow_html=True)
        level = st.number_input("Level", 1, 80, existing.level if existing else 1, key=f"level_{hero_key}", label_visibility="collapsed")

    with col_stars:
        st.markdown('<div style="font-size:12px;color:#B8D4E8;">STARS</div>', unsafe_allow_html=True)
        stars = st.selectbox("Stars", [0, 1, 2, 3, 4, 5], index=existing.stars if existing else 0, key=f"stars_{hero_key}", label_visibility="collapsed")
        filled = "★" * stars
        empty = "☆" * (5 - stars)
        st.markdown(f'<span style="color:#FFD700;font-size:16px;">{filled}</span><span style="color:#4A5568;">{empty}</span>', unsafe_allow_html=True)

    with col_asc:
        st.markdown('<div style="font-size:12px;color:#B8D4E8;">ASCENSION</div>', unsafe_allow_html=True)
        if stars < 5:
            ascension = st.selectbox("Ascension", [0, 1, 2, 3, 4, 5], index=min(existing.ascension_tier if existing else 0, 5), key=f"ascension_{hero_key}", label_visibility="collapsed")
            asc_pips = "●" * ascension + "○" * (5 - ascension)
            st.markdown(f'<span style="color:#9B59B6;font-size:14px;">{asc_pips}</span> <span style="color:#666;font-size:11px;">({ascension}/5)</span>', unsafe_allow_html=True)
        else:
            st.selectbox("Ascension", [0], disabled=True, key=f"ascension_{hero_key}", label_visibility="collapsed")
            ascension = 0
            st.markdown('<span style="color:#4CAF50;font-size:12px;">MAX</span>', unsafe_allow_html=True)

    st.markdown("---")

    # Row 2: Skills - side by side
    col_explore, col_exped = st.columns(2)

    with col_explore:
        st.markdown('<div style="font-size:12px;color:#4A90D9;font-weight:bold;margin-bottom:8px;">EXPLORATION</div>', unsafe_allow_html=True)
        exp1 = render_skill_row(hero.get('exploration_skill_1', 'Skill 1'), existing.exploration_skill_1_level if existing else 1, f"exp1_{hero_key}", hero.get('exploration_skill_1_desc'))
        exp2 = render_skill_row(hero.get('exploration_skill_2', 'Skill 2'), existing.exploration_skill_2_level if existing else 1, f"exp2_{hero_key}", hero.get('exploration_skill_2_desc'))
        if hero.get('exploration_skill_3'):
            exp3 = render_skill_row(hero['exploration_skill_3'], existing.exploration_skill_3_level if existing else 1, f"exp3_{hero_key}", hero.get('exploration_skill_3_desc'))
        else:
            exp3 = 1

    with col_exped:
        st.markdown('<div style="font-size:12px;color:#FF6B35;font-weight:bold;margin-bottom:8px;">EXPEDITION</div>', unsafe_allow_html=True)
        exped1 = render_skill_row(hero.get('expedition_skill_1', 'Skill 1'), existing.expedition_skill_1_level if existing else 1, f"exped1_{hero_key}", hero.get('expedition_skill_1_desc'))
        exped2 = render_skill_row(hero.get('expedition_skill_2', 'Skill 2'), existing.expedition_skill_2_level if existing else 1, f"exped2_{hero_key}", hero.get('expedition_skill_2_desc'))
        if hero.get('expedition_skill_3'):
            exped3 = render_skill_row(hero['expedition_skill_3'], existing.expedition_skill_3_level if existing else 1, f"exped3_{hero_key}", hero.get('expedition_skill_3_desc'))
        else:
            exped3 = 1

    st.markdown("---")

    # Row 3: Gear
    st.markdown('<div style="font-size:12px;color:#B8D4E8;font-weight:bold;margin-bottom:8px;">HERO GEAR</div>', unsafe_allow_html=True)
    quality_options = ["None", "Gray", "Green", "Blue", "Purple", "Gold", "Legendary"]
    gear_icons = ["⚔️", "🛡️", "⛑️", "👢"]

    gear_data = {}
    gear_cols = st.columns(4)
    for i, slot_name in enumerate(GEAR_SLOTS):
        with gear_cols[i]:
            current_quality = getattr(existing, f'gear_slot{i+1}_quality', 0) if existing else 0
            current_level = getattr(existing, f'gear_slot{i+1}_level', 0) if existing else 0
            current_mastery = getattr(existing, f'gear_slot{i+1}_mastery', 0) if existing else 0

            st.markdown(f'<div style="font-size:11px;color:#888;">{gear_icons[i]} {slot_name}</div>', unsafe_allow_html=True)
            q_idx = st.selectbox("Quality", range(len(quality_options)), index=min(current_quality, len(quality_options)-1),
                                format_func=lambda x: quality_options[x], key=f"gear{i+1}_q_{hero_key}", label_visibility="collapsed")
            gear_data[f'slot{i+1}_quality'] = q_idx

            if q_idx > 0:
                # Max level is 100 for all gear
                level_val = st.number_input("Level", 0, 100, min(current_level, 100), key=f"gear{i+1}_l_{hero_key}")
                gear_data[f'slot{i+1}_level'] = level_val

                # Mastery forging (only for Gold and above, at gear level 20+)
                if q_idx >= 5 and level_val >= 20:
                    mastery = st.number_input("Mastery", 0, 20, min(current_mastery, 20), key=f"gear{i+1}_m_{hero_key}")
                    gear_data[f'slot{i+1}_mastery'] = mastery
            else:
                gear_data[f'slot{i+1}_level'] = 0

    # Exclusive/Mythic gear - compact
    mythic_data = {}
    mythic_gear_name = hero.get('mythic_gear')
    if mythic_gear_name:
        st.markdown("---")
        st.markdown(f'<div style="font-size:12px;color:#E91E63;font-weight:bold;margin-bottom:8px;">EXCLUSIVE GEAR: {mythic_gear_name}</div>', unsafe_allow_html=True)
        col_m1, col_m2, col_m3, col_m4 = st.columns([1.5, 1.5, 1, 1])
        with col_m1:
            has_mythic = st.checkbox("Unlocked", existing.mythic_gear_unlocked if existing else False, key=f"mythic_unlocked_{hero_key}")
            mythic_data['unlocked'] = has_mythic
        if has_mythic:
            with col_m2:
                mythic_quality_options = ["Gray", "Green", "Blue", "Purple", "Gold", "Legendary"]
                m_q_idx = st.selectbox("Quality", range(len(mythic_quality_options)),
                                       index=max(0, (existing.mythic_gear_quality if existing else 1) - 1),
                                       format_func=lambda x: mythic_quality_options[x], key=f"mythic_q_{hero_key}", label_visibility="collapsed")
                mythic_data['quality'] = m_q_idx + 1  # Offset since we don't have "None"
            with col_m3:
                m_level = st.number_input("Level", 0, 100, existing.mythic_gear_level if existing else 0, key=f"mythic_l_{hero_key}")
                mythic_data['level'] = m_level
            with col_m4:
                # Mastery for Gold+ exclusive gear
                if m_q_idx >= 4 and m_level >= 20:
                    current_mythic_mastery = existing.mythic_gear_mastery if existing else 0
                    m_mastery = st.number_input("Mastery", 0, 20, min(current_mythic_mastery, 20), key=f"mythic_m_{hero_key}")
                    mythic_data['mastery'] = m_mastery

    # Save button - right aligned
    col_space, col_save = st.columns([3, 1])
    with col_save:
        if st.button("💾 Save", key=f"save_{hero_key}", type="primary"):
            save_user_hero(hero, level, stars, ascension, exp1, exp2, exp3, exped1, exped2, exped3, gear_data, mythic_data if mythic_gear_name else None)
            st.toast(f"✅ {hero['name']} saved!", icon="✅")
            st.rerun()


# Page content
st.markdown("# Hero Management")
st.markdown("Browse all heroes and check **Owned** to add them to your collection and track progress.")

# Filter controls
col1, col2, col3, col4 = st.columns(4)
with col1:
    filter_gen = st.selectbox("Generation", ["All"] + [f"Gen {i}" for i in range(1, 15)])
with col2:
    filter_class = st.selectbox("Class", ["All", "Infantry", "Marksman", "Lancer"])
with col3:
    filter_tier = st.selectbox("Tier", ["All", "S+", "S", "A", "B", "C", "D"])
with col4:
    filter_unlocked = st.selectbox("Status", ["All", "Owned", "Not Owned"])

st.markdown("---")

# Table header - matches new layout with image on left
header_img_col, header_content_col = st.columns([1, 6])
with header_img_col:
    st.markdown("")  # Image column - no header needed
with header_content_col:
    header_cols = st.columns([2.5, 1.5, 1, 1, 2, 1, 1.5])
    with header_cols[0]:
        st.markdown("**Name**")
    with header_cols[1]:
        st.markdown("**Class**")
    with header_cols[2]:
        st.markdown("**Tier**")
    with header_cols[3]:
        st.markdown("**Gen**")
    with header_cols[4]:
        st.markdown("**Stars**")
    with header_cols[5]:
        st.markdown("**Level**")
    with header_cols[6]:
        st.markdown("**Owned**")

# Group heroes by generation
heroes_by_gen = {}
for hero in HERO_DATA['heroes']:
    gen = hero['generation']
    if gen not in heroes_by_gen:
        heroes_by_gen[gen] = []
    heroes_by_gen[gen].append(hero)

# Display heroes
for gen in sorted(heroes_by_gen.keys()):
    if filter_gen != "All" and filter_gen != f"Gen {gen}":
        continue

    heroes = heroes_by_gen[gen]

    # Apply filters
    if filter_class != "All":
        heroes = [h for h in heroes if h['hero_class'] == filter_class]
    if filter_tier != "All":
        heroes = [h for h in heroes if h['tier_overall'] == filter_tier]

    # Filter by owned status
    if filter_unlocked != "All":
        filtered_heroes = []
        for h in heroes:
            user_hero = get_user_hero(h['name'])
            if filter_unlocked == "Owned" and user_hero:
                filtered_heroes.append(h)
            elif filter_unlocked == "Not Owned" and not user_hero:
                filtered_heroes.append(h)
        heroes = filtered_heroes

    if not heroes:
        continue

    # Generation header
    st.markdown(f"### Generation {gen}")

    for hero in heroes:
        hero_key = hero['name'].replace(' ', '_').replace("'", "").lower()
        user_hero = get_user_hero(hero['name'])
        render_hero_row(hero, user_hero, hero_key)

    st.markdown("")  # Spacing between generations

# Summary at bottom
st.markdown("---")
user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()
total_owned = len(user_heroes)
total_heroes = len(HERO_DATA['heroes'])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Owned Heroes", f"{total_owned}/{total_heroes}")
with col2:
    if user_heroes:
        avg_level = sum(h.level for h in user_heroes) / len(user_heroes)
        st.metric("Avg Level", f"{avg_level:.1f}")
    else:
        st.metric("Avg Level", "-")
with col3:
    if user_heroes:
        total_stars = sum(h.stars for h in user_heroes)
        st.metric("Total Stars", total_stars)
    else:
        st.metric("Total Stars", "-")

# Close database
db.close()
