"""
Events Guide - Which events are worth your time and how to prepare.
"""

import streamlit as st
from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero, Hero
from database.auth import is_authenticated
from engine.analyzers.lineup_builder import LineupBuilder, LINEUP_TEMPLATES

# Require login - redirect to login page if not authenticated
if not is_authenticated():
    st.query_params["page"] = "login"
    st.rerun()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load events guide
EVENTS_PATH = PROJECT_ROOT / "data" / "events_guide.json"
if EVENTS_PATH.exists():
    with open(EVENTS_PATH, encoding='utf-8') as f:
        EVENTS_GUIDE = json.load(f)
else:
    EVENTS_GUIDE = {"events": {}, "cost_categories": {}, "priority_tiers": {}}

# Load heroes data for lineup builder
HEROES_PATH = PROJECT_ROOT / "data" / "heroes.json"
if HEROES_PATH.exists():
    with open(HEROES_PATH, encoding='utf-8') as f:
        HEROES_DATA = json.load(f)
else:
    HEROES_DATA = {"heroes": []}

# Map event IDs to lineup template types (only for combat events)
EVENT_TO_LINEUP = {
    "bear_trap": "bear_trap",           # Rally combat
    "crazy_joe": "crazy_joe",           # Defense combat
    "svs_battle": "svs_attack",         # PvP combat
    "alliance_showdown": "svs_attack",  # Alliance PvP
    "canyon_clash": "svs_attack",       # PvP combat
    "foundry_battle": "svs_attack",     # PvP combat
    "exploration": "exploration",       # PvE exploration
    "frozen_passage": "exploration",    # PvE exploration
}


def get_user_heroes_dict(db, profile) -> dict:
    """Get user's owned heroes as a dict for lineup builder."""
    if not profile:
        return {}

    user_heroes = db.query(UserHero, Hero).join(Hero).filter(
        UserHero.profile_id == profile.id,
        UserHero.owned == True
    ).all()

    heroes_dict = {}
    for uh, h in user_heroes:
        heroes_dict[h.name] = {
            'level': uh.level or 1,
            'stars': uh.stars or 0,
            'ascension_tier': uh.ascension_tier or 0,
            'gear_slot1_quality': uh.gear_slot1_quality or 0,
            'gear_slot2_quality': uh.gear_slot2_quality or 0,
            'gear_slot3_quality': uh.gear_slot3_quality or 0,
            'gear_slot4_quality': uh.gear_slot4_quality or 0,
            'expedition_skill_1_level': uh.expedition_skill_1_level or 1,
        }
    return heroes_dict


def get_recommended_heroes_for_event(event_id: str, db, profile) -> list:
    """
    Get recommended heroes for an event using the lineup engine.
    Returns list of hero names appropriate for user's roster.
    Falls back to static list filtered by generation if no profile.
    """
    lineup_type = EVENT_TO_LINEUP.get(event_id)
    if not lineup_type:
        return []

    # Get user's owned heroes
    user_heroes = get_user_heroes_dict(db, profile)

    # Determine max generation from profile
    max_gen = 14  # Default
    if profile and profile.furnace_level:
        # Rough mapping: Gen unlocks around furnace level progression
        # Gen 1-4 at F1-F18, Gen 5-8 at F19-F25, Gen 9+ at F26+
        fl = profile.furnace_level
        if fl < 19:
            max_gen = min(4, (fl // 5) + 1)
        elif fl < 26:
            max_gen = min(8, 4 + ((fl - 18) // 2))
        else:
            max_gen = 14

    if user_heroes:
        # Use lineup engine with user's heroes
        builder = LineupBuilder(HEROES_DATA)
        lineup = builder.build_personalized_lineup(lineup_type, user_heroes, max_generation=max_gen)

        # Extract hero names from lineup (exclude "Need X" and "Any hero")
        heroes = []
        for h in lineup.heroes:
            hero_name = h.get('hero', '')
            if hero_name and not hero_name.startswith('Need ') and hero_name != 'Any hero':
                heroes.append(hero_name)
        return heroes
    else:
        # No user heroes - show general recommendation filtered by generation
        builder = LineupBuilder(HEROES_DATA)
        lineup = builder.build_general_lineup(lineup_type, max_generation=max_gen)

        heroes = []
        for h in lineup.heroes:
            hero_name = h.get('hero', '')
            if hero_name and 'available' not in hero_name.lower() and hero_name != 'Any hero':
                heroes.append(hero_name)
        return heroes


def get_priority_color(priority):
    """Get color for priority tier."""
    colors = {
        "S": "#FFD700",  # Gold
        "A": "#9B59B6",  # Purple
        "B": "#3498DB",  # Blue
        "C": "#95A5A6",  # Gray
        "D": "#E74C3C",  # Red
    }
    return colors.get(priority, "#666")


def get_cost_color(cost_category):
    """Get color for cost category."""
    categories = EVENTS_GUIDE.get("cost_categories", {})
    return categories.get(cost_category, {}).get("color", "#666")


def get_cost_label(cost_category):
    """Get label for cost category."""
    categories = EVENTS_GUIDE.get("cost_categories", {})
    return categories.get(cost_category, {}).get("label", cost_category)


def get_event_name(event_id):
    """Get proper event name from event ID."""
    events = EVENTS_GUIDE.get("events", {})
    if event_id in events:
        return events[event_id].get("name", event_id.replace("_", " ").title())
    return event_id.replace("_", " ").title()


def render_intel_strategy_timeline(intel_strategy):
    """Render visual timeline for Flame and Fang intel claiming strategy."""
    timeline = intel_strategy.get("timeline", {})
    normal_total = intel_strategy.get("normal_total", 168)
    trick_total = intel_strategy.get("with_trick_total", 184)
    refresh_times = intel_strategy.get("refresh_times", [])

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    # Header with core comparison
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(231, 76, 60, 0.2), rgba(46, 204, 113, 0.2));
                border: 2px solid #F39C12; border-radius: 12px; padding: 20px; margin: 16px 0;">
        <div style="text-align: center; margin-bottom: 16px;">
            <div style="font-size: 18px; font-weight: bold; color: #F1C40F; {text_shadow}">The Extra 16 Cores Trick</div>
            <div style="color: #B8D4E8; margin-top: 8px; {text_shadow}">
                Intel refreshes at: <span style="color: #3498DB; font-weight: bold;">{' | '.join(refresh_times)}</span> server time
            </div>
        </div>
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 16px;">
            <div style="text-align: center;">
                <div style="font-size: 32px; font-weight: bold; color: #95A5A6; {text_shadow}">{normal_total}</div>
                <div style="color: #95A5A6; font-size: 12px; {text_shadow}">Normal</div>
            </div>
            <div style="font-size: 24px; color: #F39C12; align-self: center; {text_shadow}">vs</div>
            <div style="text-align: center;">
                <div style="font-size: 32px; font-weight: bold; color: #2ECC71; {text_shadow}">{trick_total}</div>
                <div style="color: #2ECC71; font-size: 12px; {text_shadow}">With Trick</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Timeline visualization
    st.markdown("#### Claiming Timeline")

    # Timeline is now a list
    for step in timeline:
        day = step.get("day", "")
        time = step.get("time", "")
        action = step.get("action", "")
        step_type = step.get("type", "normal")

        # Style based on type
        if step_type == "warning":
            bg_style = "background: rgba(231, 76, 60, 0.3); border: 2px solid #E74C3C;"
            time_color = "#E74C3C"
            action_color = "#E74C3C"
            action_weight = "font-weight: bold;"
        elif step_type == "claim":
            bg_style = "background: rgba(46, 204, 113, 0.2); border: 2px solid #2ECC71;"
            time_color = "#2ECC71"
            action_color = "#2ECC71"
            action_weight = "font-weight: bold;"
        elif step_type == "final":
            bg_style = "background: rgba(241, 196, 15, 0.2); border: 2px solid #F1C40F;"
            time_color = "#F1C40F"
            action_color = "#F1C40F"
            action_weight = "font-weight: bold;"
        else:
            bg_style = "background: rgba(74, 144, 217, 0.1); border-left: 4px solid #3498DB;"
            time_color = "#3498DB"
            action_color = "#B8D4E8"
            action_weight = ""

        st.markdown(f"""
        <div style="{bg_style} padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;
                    display: flex; align-items: center; gap: 16px;">
            <div style="min-width: 60px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: {time_color}; {text_shadow}">{time}</div>
            </div>
            <div style="flex: 1;">
                <div style="color: #B8D4E8; font-size: 12px; {text_shadow}">{day}</div>
                <div style="color: {action_color}; font-size: 14px; margin-top: 2px; {action_weight} {text_shadow}">{action}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_spending_priority(spending_priority):
    """Render spending priority for Flame and Fang cores."""
    order = spending_priority.get("order", [])
    avoid = spending_priority.get("avoid", [])
    warning = spending_priority.get("warning", "")

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    st.markdown("#### Spending Priority")

    # Priority list
    for item in order:
        priority_num = item.get("priority", 0)
        item_name = item.get("item", "")
        note = item.get("note", "")

        color = "#2ECC71" if priority_num <= 2 else "#F39C12" if priority_num == 3 else "#95A5A6"
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: {color}; color: #000; width: 28px; height: 28px; border-radius: 50%;
                        display: flex; align-items: center; justify-content: center; font-weight: bold;">
                {priority_num}
            </div>
            <div>
                <span style="color: #E8F4F8; font-weight: bold; {text_shadow}">{item_name}</span>
                <span style="color: #B8D4E8; font-size: 12px; margin-left: 8px; {text_shadow}">({note})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Avoid section
    if avoid:
        st.markdown(f"""
        <div style="background: rgba(231, 76, 60, 0.2); border-left: 4px solid #E74C3C;
                    padding: 8px 12px; border-radius: 4px; margin-top: 12px;">
            <span style="color: #E74C3C; font-weight: bold; {text_shadow}">AVOID:</span>
            <span style="color: #E8F4F8; {text_shadow}"> {', '.join(avoid)}</span>
        </div>
        """, unsafe_allow_html=True)

    # Warning
    if warning:
        st.markdown(f"""
        <div style="background: rgba(241, 196, 15, 0.2); border: 2px solid #F1C40F;
                    padding: 12px; border-radius: 8px; margin-top: 12px; text-align: center;">
            <span style="font-size: 18px;">&#9888;</span>
            <span style="color: #F1C40F; font-weight: bold; {text_shadow}"> {warning}</span>
        </div>
        """, unsafe_allow_html=True)


def render_event_card(event_id, event_data):
    """Render a single event card."""
    priority = event_data.get("priority", "C")
    priority_color = get_priority_color(priority)
    cost_category = event_data.get("cost_category", "free")
    cost_color = get_cost_color(cost_category)
    cost_label = get_cost_label(cost_category)
    f2p = event_data.get("f2p_friendly", False)

    # F2P indicator
    if f2p is True:
        f2p_badge = "<span style='background:#2ECC71;padding:2px 8px;border-radius:4px;font-size:11px;'>F2P Friendly</span>"
    elif f2p == "partially":
        f2p_badge = "<span style='background:#F1C40F;padding:2px 8px;border-radius:4px;font-size:11px;color:#000;'>Partial F2P</span>"
    else:
        f2p_badge = "<span style='background:#E74C3C;padding:2px 8px;border-radius:4px;font-size:11px;'>Pay to Progress</span>"

    text_shadow = "text-shadow: 1px 1px 2px rgba(0,0,0,0.8);"

    with st.container():
        st.markdown(f"""
        <div style="background: rgba(74, 144, 217, 0.1); border: 1px solid rgba(74, 144, 217, 0.3);
                    border-left: 4px solid {priority_color}; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <span style="font-size: 20px; font-weight: bold; color: #E8F4F8; {text_shadow}">{event_data.get('name', event_id)}</span>
                    <span style="background: {priority_color}; padding: 2px 8px; border-radius: 4px; margin-left: 8px; font-size: 12px; color: #000;">
                        {priority} Priority
                    </span>
                </div>
                <div>
                    {f2p_badge}
                </div>
            </div>
            <div style="color: #B8D4E8; font-size: 13px; margin-bottom: 8px; {text_shadow}">
                {event_data.get('type', '').title()} Event | {event_data.get('frequency', '')} | {event_data.get('duration', '')}
            </div>
            <div style="color: #E8F4F8; margin-bottom: 8px; {text_shadow}">
                {event_data.get('description', '')}
            </div>
            <div style="color: #B8D4E8; font-size: 13px; margin-bottom: 12px; font-style: italic; {text_shadow}">
                {event_data.get('gameplay', '')}
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span style="background: {cost_color}; padding: 4px 10px; border-radius: 4px; font-size: 12px; {text_shadow}">
                    {cost_label}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Expandable details
        with st.expander("Details & Preparation"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Rewards:**")
                rewards = event_data.get("rewards", {})
                primary = rewards.get("primary", [])
                if primary:
                    for r in primary:
                        st.markdown(f"- {r}")

                backpack = rewards.get("backpack_items", [])
                if backpack:
                    st.markdown("**Backpack Items:**")
                    st.markdown(", ".join(backpack))

            with col2:
                st.markdown("**Preparation:**")
                prep = event_data.get("preparation", {})

                save_before = prep.get("save_before", [])
                if save_before:
                    if len(save_before) > 5:
                        # Long list - show as bullet points
                        for item in save_before:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**Save:** {', '.join(save_before)}")

                heroes_needed = prep.get("heroes_needed", "")
                if heroes_needed and heroes_needed != "none":
                    st.markdown(f"**Heroes:** {heroes_needed.title()} skills")

                # Use lineup engine for recommended heroes if this is a combat event
                recommended_heroes = get_recommended_heroes_for_event(event_id, db, profile)
                if recommended_heroes:
                    # Show personalized recommendation
                    st.markdown(f"**Recommended Heroes:** {', '.join(recommended_heroes)}")
                    if profile and get_user_heroes_dict(db, profile):
                        st.caption("*Based on your owned heroes*")
                else:
                    # Fall back to static key_heroes for non-combat events
                    key_heroes = prep.get("key_heroes", [])
                    if key_heroes:
                        st.markdown(f"**Key Heroes:** {', '.join(key_heroes)}")

            # Troop ratio if available
            troop_ratio = event_data.get("troop_ratio", {})
            if troop_ratio:
                st.markdown("---")
                st.markdown("### Recommended Troop Ratio")

                # Check if it has leader/joiner sub-structure
                if "leader" in troop_ratio or "joiner" in troop_ratio:
                    # Multi-ratio format (e.g., Bear Trap)
                    for role in ["leader", "joiner"]:
                        if role in troop_ratio:
                            ratio = troop_ratio[role]
                            infantry = ratio.get("infantry", "")
                            lancer = ratio.get("lancer", "")
                            marksman = ratio.get("marksman", "")
                            reasoning = ratio.get("reasoning", "")
                            role_label = "Rally Leader" if role == "leader" else "Rally Joiner"
                            role_color = "#FFD700" if role == "leader" else "#9B59B6"

                            st.markdown(f"""
                            <div style="background: rgba(74, 144, 217, 0.15); border-left: 4px solid {role_color};
                                        padding: 12px 16px; border-radius: 8px; margin: 8px 0;">
                                <div style="font-weight: bold; color: {role_color}; margin-bottom: 8px;">{role_label}</div>
                                <div style="display: flex; gap: 24px; margin-bottom: 8px;">
                                    <div style="text-align: center;">
                                        <div style="font-size: 24px; font-weight: bold; color: #3498DB;">{infantry}</div>
                                        <div style="font-size: 12px; color: #B8D4E8;">Infantry</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 24px; font-weight: bold; color: #2ECC71;">{lancer}</div>
                                        <div style="font-size: 12px; color: #B8D4E8;">Lancer</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 24px; font-weight: bold; color: #E74C3C;">{marksman}</div>
                                        <div style="font-size: 12px; color: #B8D4E8;">Marksman</div>
                                    </div>
                                </div>
                                <div style="color: #B8D4E8; font-size: 13px; font-style: italic;">{reasoning}</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    # Simple ratio format
                    infantry = troop_ratio.get("infantry", "")
                    lancer = troop_ratio.get("lancer", "")
                    marksman = troop_ratio.get("marksman", "")
                    reasoning = troop_ratio.get("reasoning", "")

                    st.markdown(f"""
                    <div style="background: rgba(74, 144, 217, 0.15); border-left: 4px solid #F39C12;
                                padding: 12px 16px; border-radius: 8px; margin: 8px 0;">
                        <div style="display: flex; gap: 24px; margin-bottom: 8px;">
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold; color: #3498DB;">{infantry}</div>
                                <div style="font-size: 12px; color: #B8D4E8;">Infantry</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold; color: #2ECC71;">{lancer}</div>
                                <div style="font-size: 12px; color: #B8D4E8;">Lancer</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 24px; font-weight: bold; color: #E74C3C;">{marksman}</div>
                                <div style="font-size: 12px; color: #B8D4E8;">Marksman</div>
                            </div>
                        </div>
                        <div style="color: #B8D4E8; font-size: 13px; font-style: italic;">{reasoning}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Wave mechanics (Crazy Joe)
            wave_mechanics = event_data.get("wave_mechanics", {})
            if wave_mechanics:
                st.markdown("---")
                st.markdown("### Wave Breakdown")

                # Special callouts first
                online_waves = wave_mechanics.get("online_waves", "")
                high_value = wave_mechanics.get("high_value_waves", "")

                if online_waves or high_value:
                    st.markdown(f"""
                    <div style="background: rgba(241, 196, 15, 0.2); border: 2px solid #F1C40F;
                                padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        <div style="font-weight: bold; color: #F1C40F; margin-bottom: 4px;">Key Waves</div>
                        <div style="color: #E8F4F8; font-size: 13px;">{online_waves}</div>
                        <div style="color: #2ECC71; font-size: 13px; margin-top: 4px;">{high_value}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Wave list
                wave_order = ["waves_1_9", "wave_10", "waves_11_19", "wave_20", "wave_21"]
                for wave_key in wave_order:
                    if wave_key in wave_mechanics:
                        wave_label = wave_key.replace("_", " ").replace("waves", "Waves").replace("wave", "Wave").title()
                        wave_desc = wave_mechanics[wave_key]
                        is_hq = "HQ" in wave_desc
                        border_color = "#E74C3C" if is_hq else "#3498DB"
                        st.markdown(f"""
                        <div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid {border_color};
                                    padding: 8px 12px; border-radius: 4px; margin-bottom: 6px;">
                            <span style="color: #E8F4F8; font-weight: bold;">{wave_label}:</span>
                            <span style="color: #B8D4E8;"> {wave_desc}</span>
                        </div>
                        """, unsafe_allow_html=True)

            # SvS Prep Phase day-by-day breakdown
            phases = event_data.get("phases", {})
            if phases:
                st.markdown("---")
                st.markdown("### Day-by-Day Breakdown")
                for phase_id, phase_data in phases.items():
                    with st.expander(phase_data.get("name", phase_id)):
                        st.markdown(f"**Focus:** {phase_data.get('focus', '')}")

                        tasks = phase_data.get("best_value_tasks", [])
                        if tasks:
                            st.markdown("**Best Point Tasks:**")
                            for task in tasks:
                                pts = task.get("points", "?")
                                per = task.get("per", "")
                                st.markdown(f"- {task.get('task', '')}: **{pts}** pts/{per}")

                        save_for = phase_data.get("save_for_this_day", [])
                        if save_for:
                            st.success(f"**Use on this day:** {', '.join(save_for)}")

                        note = phase_data.get("note", "")
                        if note:
                            st.warning(note)

            # Battle mechanics for SvS Battle
            mechanics = event_data.get("mechanics", {})
            if mechanics:
                st.markdown("---")
                st.markdown("### Battle Mechanics")
                for key, value in mechanics.items():
                    label = key.replace("_", " ").title()
                    st.markdown(f"- **{label}:** {value}")

            # Intel strategy timeline (Flame and Fang)
            intel_strategy = event_data.get("intel_strategy", {})
            if intel_strategy:
                st.markdown("---")
                render_intel_strategy_timeline(intel_strategy)

            # Spending priority (Flame and Fang)
            spending_priority = event_data.get("spending_priority", {})
            if spending_priority:
                st.markdown("---")
                render_spending_priority(spending_priority)

            # Phase strategy (Canyon Clash, Foundry Battle)
            phase_strategy = event_data.get("phase_strategy", {})
            if phase_strategy:
                st.markdown("---")
                st.markdown("### Phase Strategy")
                for phase_key, phase_desc in phase_strategy.items():
                    phase_label = phase_key.replace("_", " ").replace("phase", "Phase").title()
                    is_critical = "CITADEL" in phase_desc.upper() or "FOUNDRY" in phase_desc.upper()
                    border_color = "#FFD700" if is_critical else "#3498DB"
                    st.markdown(f"""
                    <div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid {border_color};
                                padding: 8px 12px; border-radius: 4px; margin-bottom: 6px;">
                        <span style="color: #E8F4F8; font-weight: bold;">{phase_label}:</span>
                        <span style="color: #B8D4E8;"> {phase_desc}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Scoring mechanics (Foundry Battle)
            scoring = event_data.get("scoring", {})
            if scoring:
                st.markdown("---")
                st.markdown("### Scoring")

                combat_pts = scoring.get("combat_points", {})
                if combat_pts:
                    st.markdown("**Combat Points:**")
                    for action, pts in combat_pts.items():
                        st.markdown(f"- {action.title()}: {pts}")

                building_pts = scoring.get("building_points", {})
                if building_pts:
                    st.markdown("**Building Points:**")
                    for building, data in building_pts.items():
                        building_name = building.replace("_", " ").title()
                        first_cap = data.get("first_capture", "?")
                        per_min = data.get("per_minute", "?")
                        st.markdown(f"- **{building_name}**: {first_cap} (first capture) + {per_min}/min")

                loot = scoring.get("loot_mechanic", "")
                if loot:
                    st.info(f"**Loot Mechanic:** {loot}")

            # Fuel management (Canyon Clash)
            fuel = event_data.get("fuel_management", {})
            if fuel:
                st.markdown("---")
                st.markdown("### Fuel Management")
                critical = fuel.get("critical_rule", "")
                if critical:
                    st.warning(f"**CRITICAL:** {critical}")
                fuel_tips = fuel.get("tips", [])
                for tip in fuel_tips:
                    st.markdown(f"- {tip}")

            # Daily stages (Hall of Chiefs, King of Icefield)
            daily_stages = event_data.get("daily_stages", {})
            if daily_stages:
                st.markdown("---")
                st.markdown("### Daily Stages")

                # Check if it's Hall of Chiefs format with gen_1/gen_2 sections
                if "gen_1_season_1" in daily_stages or "gen_2_season_2_plus" in daily_stages:
                    for season_key, season_data in daily_stages.items():
                        if season_key.startswith("gen_"):
                            duration = season_data.get("duration", "")
                            hero = season_data.get("featured_hero", "")
                            with st.expander(f"{hero} Season ({duration})", expanded=season_key == "gen_2_season_2_plus"):
                                stages = season_data.get("stages", [])
                                for stage in stages:
                                    day = stage.get("day", "")
                                    focus = stage.get("focus", "")
                                    activities = stage.get("activities", "")
                                    st.markdown(f"""
                                    <div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid #4A90D9;
                                                padding: 8px 12px; border-radius: 4px; margin-bottom: 6px;">
                                        <span style="color: #FFD700; font-weight: bold;">Day {day}:</span>
                                        <span style="color: #E8F4F8; font-weight: bold;"> {focus}</span>
                                        <div style="color: #B8D4E8; font-size: 13px; margin-top: 4px;">{activities}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    # King of Icefield format with stages array
                    desc = daily_stages.get("description", "")
                    if desc:
                        st.caption(desc)
                    stages = daily_stages.get("stages", [])
                    for stage in stages:
                        day = stage.get("day", "")
                        focus = stage.get("focus", "")
                        reward = stage.get("reward", "")
                        activities = stage.get("activities", "")
                        reward_color = "#FFD700" if "Shards" in reward else "#4A90D9"
                        st.markdown(f"""
                        <div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid {reward_color};
                                    padding: 8px 12px; border-radius: 4px; margin-bottom: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #FFD700; font-weight: bold;">Day {day}: {focus}</span>
                                <span style="color: {reward_color}; font-size: 12px;">Reward: {reward}</span>
                            </div>
                            <div style="color: #B8D4E8; font-size: 13px; margin-top: 4px;">{activities}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Victory Points (Alliance Showdown)
            victory_points = event_data.get("victory_points", {})
            if victory_points:
                st.markdown("---")
                st.markdown("### Victory Points")
                desc = victory_points.get("description", "")
                if desc:
                    st.info(desc)

                breakdown = victory_points.get("breakdown", [])
                if breakdown:
                    cols = st.columns(len(breakdown))
                    for col, day_data in zip(cols, breakdown):
                        day = day_data.get("day", "")
                        points = day_data.get("points", 0)
                        note = day_data.get("note", "")
                        is_critical = points >= 4
                        bg_color = "rgba(231, 76, 60, 0.2)" if is_critical else "rgba(74, 144, 217, 0.1)"
                        border_color = "#E74C3C" if is_critical else "#4A90D9"
                        with col:
                            st.markdown(f"""
                            <div style="background: {bg_color}; border: 2px solid {border_color};
                                        padding: 10px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 12px; color: #B8D4E8;">Day {day}</div>
                                <div style="font-size: 28px; font-weight: bold; color: {border_color};">{points}</div>
                                <div style="font-size: 10px; color: #B8D4E8;">VP</div>
                            </div>
                            """, unsafe_allow_html=True)

                strategy = victory_points.get("strategy", "")
                if strategy:
                    st.success(f"**Strategy:** {strategy}")

            # Star System (Alliance Showdown)
            star_system = event_data.get("star_system", {})
            if star_system:
                st.markdown("---")
                st.markdown("### Star Rating System")
                desc = star_system.get("description", "")
                if desc:
                    st.caption(desc)
                win_effect = star_system.get("win_effect", "")
                loss_effect = star_system.get("loss_effect", "")
                star_rewards = star_system.get("star_rewards", "")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Win:** {win_effect}")
                    st.markdown(f"**Lose:** {loss_effect}")
                with col2:
                    st.markdown(f"**Rewards:** {star_rewards}")

            # Tundra Trade Route (Alliance Showdown companion event)
            tundra = event_data.get("tundra_trade_route", {})
            if tundra:
                st.markdown("---")
                st.markdown("### Tundra Trade Route (Concurrent Event)")
                desc = tundra.get("description", "")
                if desc:
                    st.caption(desc)
                tundra_tips = tundra.get("tips", [])
                for tip in tundra_tips:
                    st.markdown(f"- {tip}")

            # Medal System (King of Icefield)
            medal_system = event_data.get("medal_system", {})
            if medal_system:
                st.markdown("---")
                st.markdown("### Medal System")
                desc = medal_system.get("description", "")
                if desc:
                    st.caption(desc)
                medals_per_day = medal_system.get("medals_per_day", 0)
                medal_shop = medal_system.get("medal_shop", "")
                st.markdown(f"**Medals per day:** {medals_per_day}")
                st.markdown(f"**Medal Shop:** {medal_shop}")

            # F2P Strategy section
            f2p_strategy = event_data.get("f2p_strategy", {})
            if f2p_strategy:
                st.markdown("---")
                st.markdown("### F2P Strategy")
                focus_stages = f2p_strategy.get("focus_stages", [])
                if focus_stages:
                    st.markdown(f"**Focus on:** {', '.join(focus_stages)}")
                f2p_tips = f2p_strategy.get("tips", [])
                for tip in f2p_tips:
                    st.markdown(f"- {tip}")

            tips = event_data.get("preparation", {}).get("tips", [])
            if tips:
                st.markdown("**Tips:**")
                for tip in tips:
                    st.markdown(f"- {tip}")

            notes = event_data.get("notes", "")
            if notes:
                st.info(notes)


def render_events_guide():
    """Render the events guide page."""
    st.markdown("# Events Guide")
    st.markdown("Which events are worth your time (and money) - and how to prepare.")

    # Quick reference
    st.markdown("---")
    st.markdown("### Quick Priority Guide")

    priority_tiers = EVENTS_GUIDE.get("priority_tiers", {})
    summary = EVENTS_GUIDE.get("summary_by_priority", {})

    cols = st.columns(5)
    tier_keys = ["S", "A", "B", "C", "D"]
    tier_labels = ["Must Do", "High Priority", "Do If Active", "Low Priority", "Skip"]

    for col, tier, label in zip(cols, tier_keys, tier_labels):
        with col:
            color = get_priority_color(tier)
            st.markdown(f"""
            <div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid {color};
                        padding: 12px; border-radius: 4px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: {color}; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">{tier}</div>
                <div style="font-size: 12px; color: #B8D4E8; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Resource saving guide - clean table layout
    with st.expander("What to Save & When", expanded=True):
        saving_guide = EVENTS_GUIDE.get("resource_saving_guide", {})

        # Create a proper table layout
        st.markdown("""
        <style>
        .save-table { width: 100%; border-collapse: collapse; }
        .save-table th { text-align: left; padding: 8px 12px; border-bottom: 1px solid #4A90D9; color: #B8D4E8; font-size: 12px; text-transform: uppercase; }
        .save-table td { padding: 10px 12px; border-bottom: 1px solid rgba(74, 144, 217, 0.2); vertical-align: top; }
        .save-table tr:hover { background: rgba(74, 144, 217, 0.1); }
        .resource-name { color: #E8F4F8; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .save-for { color: #FFD700; font-size: 13px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .save-tip { color: #B8D4E8; font-size: 12px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        </style>
        """, unsafe_allow_html=True)

        table_html = '<table class="save-table"><thead><tr><th style="width:20%;">Resource</th><th style="width:25%;">Save For</th><th>Tip</th></tr></thead><tbody>'

        for resource, data in saving_guide.items():
            save_for = data.get("save_for", [])
            # Convert event IDs to proper names
            save_for_names = [get_event_name(event_id) for event_id in save_for]
            tip = data.get("tip", "")
            resource_display = resource.replace('_', ' ').title()

            table_html += f'<tr><td class="resource-name">{resource_display}</td><td class="save-for">{", ".join(save_for_names)}</td><td class="save-tip">{tip}</td></tr>'

        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")

    # Event categories for tabs
    EVENT_CATEGORIES = {
        "all": {
            "label": "All Events",
            "events": None,  # Special: show all
            "description": "All events sorted by priority"
        },
        "alliance_pve": {
            "label": "Alliance PvE",
            "events": ["bear_trap", "crazy_joe", "mercenary_prestige", "frostdragon_tyrant", "labyrinth", "frostfire_mine"],
            "description": "Alliance rallies against PvE bosses and dungeons"
        },
        "pvp_svs": {
            "label": "PvP / SvS",
            "events": ["svs_prep", "svs_battle", "alliance_showdown", "king_of_icefield", "canyon_clash", "foundry_battle", "brother_in_arms", "alliance_championship", "tundra_arms_league"],
            "description": "State vs State and alliance combat"
        },
        "growth": {
            "label": "Growth",
            "events": ["hall_of_chiefs", "hero_rally", "flame_and_fang", "tundra_album"],
            "description": "Power growth, progression, and collection systems"
        },
        "solo_gacha": {
            "label": "Solo / Gacha",
            "events": ["lucky_wheel", "artisans_trove", "flame_lotto", "mix_and_match", "treasure_hunter", "tundra_trading", "snowbusters", "fishing_tournament"],
            "description": "Individual rewards and lucky draws"
        }
    }

    # Create tabs
    tab_labels = [cat["label"] for cat in EVENT_CATEGORIES.values()]
    tabs = st.tabs(tab_labels)

    events = EVENTS_GUIDE.get("events", {})
    priority_order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}

    for tab, (cat_id, cat_info) in zip(tabs, EVENT_CATEGORIES.items()):
        with tab:
            st.caption(cat_info["description"])

            # Filter events for this category
            if cat_info["events"] is None:
                # "All" tab - show everything
                filtered_events = events.items()
            else:
                # Filter to only events in this category
                filtered_events = [(eid, events[eid]) for eid in cat_info["events"] if eid in events]

            # Sort by priority
            sorted_events = sorted(
                filtered_events,
                key=lambda x: priority_order.get(x[1].get("priority", "C"), 5)
            )

            if sorted_events:
                for event_id, event_data in sorted_events:
                    render_event_card(event_id, event_data)
            else:
                st.info("No events in this category yet.")

    st.markdown("---")

    # Cost category legend
    with st.expander("Cost Categories Explained"):
        cost_cats = EVENTS_GUIDE.get("cost_categories", {})
        for cat_id, cat_data in cost_cats.items():
            color = cat_data.get("color", "#666")
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <span style="background:{color};padding:4px 10px;border-radius:4px;margin-right:8px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">
                    {cat_data.get('label', cat_id)}
                </span>
                <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">{cat_data.get('description', '')}</span>
            </div>
            """, unsafe_allow_html=True)


# Main
render_events_guide()

# Close database session
db.close()
