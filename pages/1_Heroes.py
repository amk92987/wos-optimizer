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


def get_tier_color(tier: str) -> str:
    """Get color for tier badge."""
    colors = {
        "S+": "#FF4444",
        "S": "#FF8C00",
        "A": "#9932CC",
        "B": "#4169E1",
        "C": "#32CD32",
        "D": "#808080"
    }
    return colors.get(tier, "#808080")


def get_class_color(hero_class: str) -> str:
    """Get color for class badge."""
    colors = {
        "Infantry": "#E74C3C",
        "Marksman": "#3498DB",
        "Lancer": "#2ECC71"
    }
    return colors.get(hero_class, "#808080")


def get_rarity_color(rarity: str) -> str:
    """Get border color for rarity."""
    colors = {
        "Rare": "#3498DB",
        "Epic": "#9B59B6",
        "Legendary": "#F1C40F"
    }
    return colors.get(rarity, "#808080")


def get_class_symbol(hero_class: str) -> str:
    """Get symbol for class."""
    symbols = {
        "Infantry": "🛡️",
        "Marksman": "🏹",
        "Lancer": "⚔️"
    }
    return symbols.get(hero_class, "?")


def get_quality_color(quality: int) -> str:
    """Get color for gear quality."""
    return QUALITY_LEVELS.get(str(quality), {}).get('color', '#666666')


def get_quality_name(quality: int) -> str:
    """Get name for gear quality."""
    return QUALITY_LEVELS.get(str(quality), {}).get('name', 'None')


@st.cache_data
def get_hero_image_base64(image_filename: str) -> str:
    """Get hero image as base64 string for embedding in HTML."""
    image_path = HERO_IMAGES_DIR / image_filename
    if image_path.exists():
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            # Determine mime type from extension
            ext = image_filename.split('.')[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64,{data}"
    return None


def render_star_rating(stars: int, ascension: int = 0, max_stars: int = 5) -> str:
    """Render star rating as HTML with ascension progress."""
    # Full stars
    filled = "★" * stars

    # Partial star based on ascension (if not at max stars)
    partial = ""
    if stars < max_stars and ascension > 0:
        # Use a half-star or progress indicator
        partial = f'<span style="color:#FF6B35;opacity:0.7;">✦</span>'

    # Empty stars (minus one if we have partial)
    remaining = max_stars - stars - (1 if partial else 0)
    empty = "☆" * remaining

    # Ascension fraction (0-5, where 6 would become next star)
    ascension_text = ""
    if ascension > 0 and stars < max_stars:
        ascension_text = f'<span style="color:#FF6B35;font-size:10px;margin-left:2px;">{ascension}/5</span>'

    return f'<span style="color:#FFD700;">{filled}</span>{partial}<span style="color:#4A5568;">{empty}</span>{ascension_text}'


def get_user_hero(hero_name: str):
    """Get user's hero data if they own it."""
    hero_ref = db.query(Hero).filter(Hero.name == hero_name).first()
    if not hero_ref:
        return None
    return db.query(UserHero).filter(
        UserHero.profile_id == profile.id,
        UserHero.hero_id == hero_ref.id
    ).first()


def save_user_hero(hero_data: dict, level: int, stars: int, ascension: int,
                   exp_skill1: int, exp_skill2: int,
                   exped_skill1: int, exped_skill2: int,
                   gear_data: dict = None, mythic_data: dict = None):
    """Save or update user hero."""
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
        user_hero.expedition_skill_1_level = exped_skill1
        user_hero.expedition_skill_2_level = exped_skill2

        # Update gear if provided
        if gear_data:
            user_hero.gear_slot1_quality = gear_data.get('slot1_quality', 0)
            user_hero.gear_slot1_level = gear_data.get('slot1_level', 0)
            user_hero.gear_slot2_quality = gear_data.get('slot2_quality', 0)
            user_hero.gear_slot2_level = gear_data.get('slot2_level', 0)
            user_hero.gear_slot3_quality = gear_data.get('slot3_quality', 0)
            user_hero.gear_slot3_level = gear_data.get('slot3_level', 0)
            user_hero.gear_slot4_quality = gear_data.get('slot4_quality', 0)
            user_hero.gear_slot4_level = gear_data.get('slot4_level', 0)

        if mythic_data:
            user_hero.mythic_gear_unlocked = mythic_data.get('unlocked', False)
            user_hero.mythic_gear_quality = mythic_data.get('quality', 0)
            user_hero.mythic_gear_level = mythic_data.get('level', 0)
    else:
        user_hero = UserHero(
            profile_id=profile.id,
            hero_id=hero_ref.id,
            level=level,
            stars=stars,
            ascension_tier=ascension,
            exploration_skill_1_level=exp_skill1,
            exploration_skill_2_level=exp_skill2,
            expedition_skill_1_level=exped_skill1,
            expedition_skill_2_level=exped_skill2
        )
        db.add(user_hero)

    db.commit()
    return True


def remove_user_hero(hero_name: str):
    """Remove a hero from user's collection."""
    hero_ref = db.query(Hero).filter(Hero.name == hero_name).first()
    if hero_ref:
        user_hero = db.query(UserHero).filter(
            UserHero.profile_id == profile.id,
            UserHero.hero_id == hero_ref.id
        ).first()
        if user_hero:
            db.delete(user_hero)
            db.commit()


def render_gear_widget(slot_num: int, slot_name: str, quality: int, level: int, hero_key: str):
    """Render a single gear slot widget."""
    color = get_quality_color(quality)
    quality_name = get_quality_name(quality)

    html = f'''
    <div style="background:rgba(30,42,58,0.8);border:2px solid {color};border-radius:6px;padding:6px;text-align:center;margin:2px;">
        <div style="font-size:10px;color:#B8D4E8;">{slot_name}</div>
        <div style="font-size:12px;color:{color};font-weight:bold;">{quality_name}</div>
        <div style="font-size:10px;color:#808080;">Lv.{level}</div>
    </div>
    '''
    return html


def render_hero_card_with_editor(hero: dict, owned_data=None, show_editor: bool = False):
    """Render a hero card with optional inline editor."""
    tier = hero['tier_overall']
    tier_color = get_tier_color(tier)
    tier_desc = TIER_DESCRIPTIONS.get(tier, '')
    class_color = get_class_color(hero['hero_class'])
    rarity = hero.get('rarity', 'Legendary')
    rarity_color = get_rarity_color(rarity)
    class_symbol = get_class_symbol(hero['hero_class'])
    generation = hero['generation']
    best_use = hero.get('best_use', '')
    mythic_gear = hero.get('mythic_gear')

    # Get hero portrait image
    image_filename = hero.get('image_filename', '')
    hero_image_b64 = get_hero_image_base64(image_filename) if image_filename else None

    # Card styling
    bg_opacity = "0.2" if not owned_data else "0.35"

    # Gen badge
    gen_badge = ""
    if generation > 1:
        gen_badge = f' <span style="background:rgba(74,144,217,0.3);color:#B8D4E8;padding:1px 6px;border-radius:3px;font-size:10px;">G{generation}</span>'

    # Owned info
    owned_info = ""
    if owned_data:
        star_rating = render_star_rating(owned_data.stars, owned_data.ascension_tier)
        owned_info = f'<div style="margin-top:8px;">{star_rating}</div><div style="color:#4A90D9;font-size:12px;">Lv. {owned_data.level}/80</div>'

    # Gear display for owned heroes
    gear_html = ""
    if owned_data:
        gear_parts = []
        for i, slot_name in enumerate(GEAR_SLOTS, 1):
            quality = getattr(owned_data, f'gear_slot{i}_quality', 0)
            level = getattr(owned_data, f'gear_slot{i}_level', 0)
            color = get_quality_color(quality)
            gear_parts.append(f'<div style="display:inline-block;width:22%;margin:1%;background:rgba(30,42,58,0.8);border:2px solid {color};border-radius:4px;padding:2px;text-align:center;"><div style="font-size:8px;color:#B8D4E8;">{slot_name[:3]}</div><div style="font-size:9px;color:{color};">{get_quality_name(quality)[:3]}</div></div>')
        gear_html = f'<div style="margin-top:8px;">{"".join(gear_parts)}</div>'

        # Mythic gear if applicable
        if mythic_gear and owned_data.mythic_gear_unlocked:
            m_color = get_quality_color(owned_data.mythic_gear_quality)
            gear_html += f'<div style="margin-top:4px;background:rgba(233,30,99,0.2);border:1px solid #E91E63;border-radius:4px;padding:2px;text-align:center;"><div style="font-size:9px;color:#E91E63;">{mythic_gear}</div></div>'

    # Best use blurb - fixed height, centered text
    blurb_color = "#FF6B35" if tier in ["S+", "S"] else "#B8D4E8"
    blurb_text = best_use if best_use else "&nbsp;"
    blurb_html = f'<div style="margin-top:8px;padding:6px;background:rgba(0,0,0,0.3);border-radius:4px;font-size:10px;color:{blurb_color};line-height:1.3;min-height:50px;max-height:50px;overflow:hidden;display:flex;align-items:center;justify-content:center;text-align:center;">{blurb_text}</div>'

    # Build HTML - tier badge has tooltip on hover
    html_parts = [
        f'<div style="background:rgba(46,90,140,{bg_opacity});border:3px solid {rarity_color};border-radius:12px;padding:12px;margin-bottom:12px;box-shadow:0 0 8px {rarity_color}40;">',
        f'<div style="display:flex;justify-content:space-between;margin-bottom:8px;">',
        f'<span style="background:{tier_color};color:white;padding:2px 8px;border-radius:4px;font-weight:bold;font-size:12px;cursor:help;" title="{tier_desc}">{tier}</span>',
        f'<span style="background:rgba(255,255,255,0.1);border-left:3px solid {class_color};padding:2px 8px;font-size:11px;color:#E8F4F8;">{hero["hero_class"]}</span>',
        '</div>',
        '<div style="text-align:center;margin:8px 0;">',
        f'<div style="width:70px;height:70px;margin:0 auto;background:rgba(30,42,58,0.8);border:2px solid {class_color};border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center;">' +
        (f'<img src="{hero_image_b64}" style="width:100%;height:100%;object-fit:cover;border-radius:6px;" />' if hero_image_b64 else f'<span style="font-size:32px;">{class_symbol}</span>') +
        '</div>',
        '</div>',
        '<div style="text-align:center;">',
        f'<div style="font-weight:bold;color:#E8F4F8;font-size:16px;">{hero["name"]}{gen_badge}</div>',
        owned_info,
        gear_html,
        blurb_html,
        '</div>',
        '</div>'
    ]

    st.markdown(''.join(html_parts), unsafe_allow_html=True)


def render_hero_editor(hero: dict, existing):
    """Render the inline editor for a hero."""
    hero_key = hero['name'].replace(' ', '_').lower()

    with st.expander(f"✏️ Edit {hero['name']}", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            level = st.slider(
                "Level", 1, 80,
                existing.level if existing else 1,
                key=f"level_{hero_key}"
            )

            # Stars and ascension
            st.markdown("**Star Progress**")
            star_col1, star_col2 = st.columns(2)
            with star_col1:
                stars = st.selectbox(
                    "Stars",
                    options=[0, 1, 2, 3, 4, 5],
                    index=existing.stars if existing else 0,
                    key=f"stars_{hero_key}"
                )
            with star_col2:
                # Ascension 0-5 (6 would mean next star), disabled at 5 stars
                if stars < 5:
                    ascension = st.selectbox(
                        "Ascension",
                        options=[0, 1, 2, 3, 4, 5],
                        index=min(existing.ascension_tier if existing else 0, 5),
                        key=f"ascension_{hero_key}",
                        help="Progress toward next star (0-5)"
                    )
                else:
                    st.selectbox(
                        "Ascension",
                        options=[0],
                        index=0,
                        key=f"ascension_{hero_key}",
                        disabled=True,
                        help="Max stars reached"
                    )
                    ascension = 0

        with col2:
            st.markdown("**Exploration Skills**")
            exp1 = st.slider(
                hero['exploration_skill_1'][:20], 1, 5,
                existing.exploration_skill_1_level if existing else 1,
                key=f"exp1_{hero_key}"
            )
            exp2 = st.slider(
                hero['exploration_skill_2'][:20], 1, 5,
                existing.exploration_skill_2_level if existing else 1,
                key=f"exp2_{hero_key}"
            )

        st.markdown("**Expedition Skills**")
        col3, col4 = st.columns(2)
        with col3:
            exped1 = st.slider(
                hero['expedition_skill_1'][:20], 1, 5,
                existing.expedition_skill_1_level if existing else 1,
                key=f"exped1_{hero_key}"
            )
        with col4:
            exped2 = st.slider(
                hero['expedition_skill_2'][:20], 1, 5,
                existing.expedition_skill_2_level if existing else 1,
                key=f"exped2_{hero_key}"
            )

        # Gear section
        st.markdown("---")
        st.markdown("**Hero Gear**")

        quality_options = ["None", "Gray", "Green", "Blue", "Purple", "Orange", "Mythic"]

        gear_data = {}
        gear_cols = st.columns(4)
        for i, slot_name in enumerate(GEAR_SLOTS):
            with gear_cols[i]:
                current_quality = getattr(existing, f'gear_slot{i+1}_quality', 0) if existing else 0
                current_level = getattr(existing, f'gear_slot{i+1}_level', 0) if existing else 0

                quality = st.selectbox(
                    f"{slot_name}",
                    quality_options,
                    index=current_quality,
                    key=f"gear{i+1}_q_{hero_key}"
                )
                gear_data[f'slot{i+1}_quality'] = quality_options.index(quality)

                max_level = GEAR_SYSTEM.get('max_level_by_quality', {}).get(str(quality_options.index(quality)), 20)
                level_val = st.number_input(
                    "Level",
                    0, max_level,
                    min(current_level, max_level),
                    key=f"gear{i+1}_l_{hero_key}"
                )
                gear_data[f'slot{i+1}_level'] = level_val

        # Mythic gear section
        mythic_data = {}
        mythic_gear_name = hero.get('mythic_gear')
        if mythic_gear_name:
            st.markdown("---")
            st.markdown(f"**Mythic Gear: {mythic_gear_name}**")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                has_mythic = st.checkbox(
                    "Unlocked",
                    existing.mythic_gear_unlocked if existing else False,
                    key=f"mythic_unlocked_{hero_key}"
                )
                mythic_data['unlocked'] = has_mythic
            if has_mythic:
                with col_m2:
                    m_quality = st.selectbox(
                        "Quality",
                        quality_options[1:],  # Skip "None"
                        index=max(0, (existing.mythic_gear_quality if existing else 1) - 1),
                        key=f"mythic_q_{hero_key}"
                    )
                    mythic_data['quality'] = quality_options.index(m_quality)
                with col_m3:
                    m_level = st.number_input(
                        "Level",
                        0, 120,
                        existing.mythic_gear_level if existing else 0,
                        key=f"mythic_l_{hero_key}"
                    )
                    mythic_data['level'] = m_level

        # Save/Remove buttons
        col_save, col_remove = st.columns(2)
        with col_save:
            if st.button("💾 Save", key=f"save_{hero_key}", type="primary", use_container_width=True):
                save_user_hero(
                    hero, level, stars, ascension,
                    exp1, exp2, exped1, exped2,
                    gear_data, mythic_data if mythic_gear_name else None
                )
                st.success(f"Saved {hero['name']}!")
                st.rerun()

        with col_remove:
            if existing:
                if st.button("🗑️ Remove", key=f"remove_{hero_key}", type="secondary", use_container_width=True):
                    remove_user_hero(hero['name'])
                    st.warning(f"Removed {hero['name']}")
                    st.rerun()


# Page content
st.markdown("# 🦸 Hero Management")
st.markdown("Track your heroes, their levels, skills, and gear.")

# Tier explanation
with st.expander("📊 Tier Explanations"):
    for tier, desc in HERO_DATA.get('tier_descriptions', {}).items():
        color = get_tier_color(tier)
        st.markdown(f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-weight:bold;">{tier}</span> {desc}', unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["📋 All Heroes", "⭐ My Heroes"])

with tab1:
    st.markdown("### All Heroes by Generation")

    # Group heroes by generation
    heroes_by_gen = {}
    for hero in HERO_DATA['heroes']:
        gen = hero['generation']
        if gen not in heroes_by_gen:
            heroes_by_gen[gen] = []
        heroes_by_gen[gen].append(hero)

    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_gen = st.selectbox("Filter by Generation",
                                  ["All"] + [f"Gen {i}" for i in sorted(heroes_by_gen.keys())])
    with col2:
        filter_class = st.selectbox("Filter by Class",
                                    ["All", "Infantry", "Marksman", "Lancer"])
    with col3:
        filter_tier = st.selectbox("Filter by Tier",
                                   ["All", "S+", "S", "A", "B", "C", "D"])

    # Display heroes
    for gen in sorted(heroes_by_gen.keys()):
        if filter_gen != "All" and filter_gen != f"Gen {gen}":
            continue

        heroes = heroes_by_gen[gen]

        if filter_class != "All":
            heroes = [h for h in heroes if h['hero_class'] == filter_class]
        if filter_tier != "All":
            heroes = [h for h in heroes if h['tier_overall'] == filter_tier]

        if not heroes:
            continue

        with st.expander(f"Generation {gen}", expanded=(gen <= 2)):
            cols = st.columns(3)
            for i, hero in enumerate(heroes):
                with cols[i % 3]:
                    user_hero = get_user_hero(hero['name'])
                    render_hero_card_with_editor(hero, user_hero)
                    render_hero_editor(hero, user_hero)

with tab2:
    st.markdown("### My Hero Collection")

    user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()

    if not user_heroes:
        st.info("You haven't added any heroes yet. Go to 'All Heroes' and use the editor to add heroes!")
    else:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Heroes", len(user_heroes))
        with col2:
            avg_level = sum(h.level for h in user_heroes) / len(user_heroes)
            st.metric("Avg Level", f"{avg_level:.1f}")
        with col3:
            max_level_hero = max(user_heroes, key=lambda h: h.level)
            st.metric("Highest Level", max_level_hero.level)
        with col4:
            total_stars = sum(h.stars for h in user_heroes)
            st.metric("Total Stars", total_stars)

        st.markdown("---")

        # Display owned heroes
        cols = st.columns(3)
        for i, user_hero in enumerate(user_heroes):
            hero_data = next((h for h in HERO_DATA['heroes']
                            if h['name'] == user_hero.hero.name), None)
            if hero_data:
                with cols[i % 3]:
                    render_hero_card_with_editor(hero_data, user_hero)
                    render_hero_editor(hero_data, user_hero)

# Close database
db.close()
