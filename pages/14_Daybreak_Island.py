"""
Daybreak Island Guide - Battle decorations, Tree of Life, and upgrade priorities.
"""

import streamlit as st
from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.auth import is_authenticated

# Require login - redirect to login page if not authenticated
if not is_authenticated():
    st.query_params["page"] = "login"
    st.rerun()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load Daybreak Island data
DAYBREAK_PATH = PROJECT_ROOT / "data" / "guides" / "daybreak_island_priorities.json"
if DAYBREAK_PATH.exists():
    with open(DAYBREAK_PATH, encoding='utf-8') as f:
        DAYBREAK_DATA = json.load(f)
else:
    DAYBREAK_DATA = {}


def get_priority_color(priority):
    """Get color for priority level."""
    colors = {
        "CRITICAL": "#E74C3C",
        "HIGH": "#F39C12",
        "MEDIUM": "#3498DB",
        "LOW": "#2ECC71"
    }
    return colors.get(priority.upper() if priority else "MEDIUM", "#666")


def render_overview():
    """Render the overview section."""
    overview = DAYBREAK_DATA.get("overview", {})

    st.markdown("### Overview")

    col1, col2 = st.columns(2)
    with col1:
        unlock = overview.get('unlock', 'Furnace Level 19 + Dock')
        st.markdown(
            f'<div style="background:rgba(74,144,217,0.1);padding:16px;border-radius:8px;">'
            f'<strong style="color:#3498DB;">Unlock Requirements</strong><br>'
            f'<span style="color:#E8F4F8;">{unlock}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col2:
        currency = overview.get('currency', 'Life Essence')
        st.markdown(
            f'<div style="background:rgba(46,204,113,0.1);padding:16px;border-radius:8px;">'
            f'<strong style="color:#2ECC71;">Currency</strong><br>'
            f'<span style="color:#E8F4F8;">{currency}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.info(f"**Purpose**: {overview.get('purpose', 'Combat buffs via Tree of Life + Battle Decorations')}")


def render_tree_of_life():
    """Render Tree of Life progression."""
    tol = DAYBREAK_DATA.get("tree_of_life_priority", {})

    st.markdown("### Tree of Life")
    st.markdown(tol.get("description", ""))

    # Milestone priorities
    milestones = tol.get("milestone_priorities", {})
    if milestones:
        st.success(f"**First Priority**: {milestones.get('first_priority', '')}")
        st.warning(f"**Second Priority**: {milestones.get('second_priority', '')}")
        st.caption(f"**Key Insight**: {milestones.get('key_insight', '')}")

    # Level progression
    st.markdown("#### Level Progression")
    buff_prog = tol.get("buff_progression", [])

    for buff in buff_prog:
        level = buff.get("level", 0)
        buff_text = buff.get("buff", "")
        combat_value = buff.get("combat_value", "Low")
        notes = buff.get("notes", "")

        # Color based on combat value
        if combat_value == "CRITICAL":
            bg_color = "rgba(231,76,60,0.2)"
            border_color = "#E74C3C"
        elif combat_value == "HIGH":
            bg_color = "rgba(243,156,18,0.15)"
            border_color = "#F39C12"
        elif combat_value == "Medium":
            bg_color = "rgba(52,152,219,0.1)"
            border_color = "#3498DB"
        else:
            bg_color = "rgba(74,144,217,0.05)"
            border_color = "#666"

        # Build notes text
        notes_text = f" ({notes})" if notes else ""

        # Use simple single-line HTML without nested flexbox
        st.markdown(
            f'<div style="background:{bg_color};border-left:4px solid {border_color};'
            f'padding:10px 14px;border-radius:6px;margin-bottom:6px;">'
            f'<span style="background:{border_color};color:#fff;padding:4px 10px;border-radius:12px;'
            f'font-weight:bold;margin-right:12px;text-shadow:0 1px 2px rgba(0,0,0,0.5);">L{level}</span>'
            f'<span style="color:#E8F4F8;font-weight:bold;">{buff_text}</span>'
            f'<span style="color:#888;font-size:12px;">{notes_text}</span>'
            f'<span style="color:{border_color};font-size:12px;font-weight:bold;float:right;">{combat_value}</span>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_battle_decorations():
    """Render battle enhancer decorations."""
    decorations = DAYBREAK_DATA.get("battle_enhancer_decorations", {})

    st.markdown("### Battle Enhancer Decorations")
    st.markdown(decorations.get("description", "The MAIN source of combat stats from Daybreak"))

    st.error("**These are MORE impactful than Tree of Life for your main troop type!**")

    # Mythic decorations
    mythic = decorations.get("mythic_decorations", {})
    if mythic:
        st.markdown("#### Mythic Decorations (+10% at max level)")

        troop_colors = {"infantry": "#E74C3C", "lancer": "#2ECC71", "marksman": "#3498DB"}

        cols = st.columns(3)
        for i, (troop_type, decos) in enumerate(mythic.items()):
            with cols[i]:
                color = troop_colors.get(troop_type, "#666")
                st.markdown(
                    f'<div style="background:{color}22;border:2px solid {color};padding:12px;border-radius:8px;'
                    f'text-align:center;margin-bottom:8px;">'
                    f'<span style="font-weight:bold;color:{color};text-transform:uppercase;">{troop_type}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                for deco_name, deco_data in decos.items():
                    if isinstance(deco_data, dict):
                        effect = deco_data.get("effect", "")
                    else:
                        effect = deco_data

                    st.markdown(
                        f'<div style="background:rgba(74,144,217,0.1);padding:8px 12px;border-radius:6px;margin:6px 0;">'
                        f'<strong style="color:#E8F4F8;">{deco_name}</strong><br>'
                        f'<span style="color:#B8D4E8;font-size:13px;">{effect}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    # Epic decorations
    epic = decorations.get("epic_decorations", {})
    if epic:
        with st.expander("Epic Decorations (+2.5% at max level)", expanded=False):
            cols = st.columns(3)
            troop_colors = {"infantry": "#E74C3C", "lancer": "#2ECC71", "marksman": "#3498DB"}

            for i, (troop_type, decos) in enumerate(epic.items()):
                with cols[i]:
                    color = troop_colors.get(troop_type, "#666")
                    st.markdown(f"**{troop_type.title()}**")
                    for deco_name, effect in decos.items():
                        st.markdown(f"- {deco_name}: {effect}")


def render_upgrade_strategy():
    """Render upgrade strategy recommendations."""
    strategy = DAYBREAK_DATA.get("upgrade_strategy", {})

    st.markdown("### Upgrade Strategy")

    # F2P vs Spender approaches
    approaches = DAYBREAK_DATA.get("spender_approaches", {})
    if approaches:
        tabs = st.tabs(["F2P", "Low Spender", "Medium+ Spender"])

        for tab, (spender_type, data) in zip(tabs, approaches.items()):
            with tab:
                if isinstance(data, dict):
                    focus = data.get("focus", "")
                    order = data.get("order", [])
                    avoid = data.get("avoid", "")

                    if focus:
                        st.success(f"**Focus**: {focus}")
                    if order:
                        st.markdown("**Priority Order:**")
                        for i, item in enumerate(order, 1):
                            st.markdown(f"{i}. {item}")
                    if avoid:
                        st.warning(f"**Avoid**: {avoid}")

    # General tips
    tips = DAYBREAK_DATA.get("tips", [])
    if tips:
        st.markdown("#### General Tips")
        for tip in tips:
            st.markdown(f"- {tip}")


def render_common_mistakes():
    """Render common mistakes section."""
    mistakes = DAYBREAK_DATA.get("common_mistakes", [])

    if mistakes:
        st.markdown("### Common Mistakes")

        for mistake in mistakes:
            if isinstance(mistake, dict):
                mistake_text = mistake.get("mistake", "")
                why_bad = mistake.get("why_bad", "")
                fix = mistake.get("fix", "")
            else:
                mistake_text = mistake
                why_bad = ""
                fix = ""

            why_html = f'<br><span style="color:#888;font-size:13px;">{why_bad}</span>' if why_bad else ''
            fix_html = f'<br><span style="color:#2ECC71;font-size:13px;"><strong>Fix:</strong> {fix}</span>' if fix else ''

            st.markdown(
                f'<div style="background:rgba(74,144,217,0.05);padding:12px;border-radius:8px;margin-bottom:8px;'
                f'border-left:4px solid #666;">'
                f'<strong style="color:#B8D4E8;">{mistake_text}</strong>'
                f'{why_html}'
                f'{fix_html}'
                f'</div>',
                unsafe_allow_html=True
            )


def render_new_player_tips():
    """Render the getting started tips for new players."""
    tips_data = DAYBREAK_DATA.get("new_player_tips", {})

    if not tips_data:
        return

    # Priority message - big warning
    priority_msg = tips_data.get("priority_message", "")
    if priority_msg:
        st.markdown(
            f'<div style="background:linear-gradient(135deg, rgba(231,76,60,0.2), rgba(243,156,18,0.2));'
            f'border:2px solid #E74C3C;padding:16px;border-radius:12px;margin-bottom:20px;text-align:center;">'
            f'<strong style="color:#E74C3C;font-size:18px;">{priority_msg}</strong>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("### Essential Tips")

    tips = tips_data.get("tips", [])
    for tip_item in tips:
        tip = tip_item.get("tip", "")
        why = tip_item.get("why", "")
        priority = tip_item.get("priority", "MEDIUM")
        priority_color = get_priority_color(priority)

        st.markdown(
            f'<div style="background:rgba(74,144,217,0.1);border-left:4px solid {priority_color};'
            f'padding:12px 14px;border-radius:6px;margin-bottom:8px;">'
            f'<span style="color:#E8F4F8;font-weight:bold;">{tip}</span>'
            f'<span style="background:{priority_color};color:#fff;padding:2px 8px;border-radius:4px;'
            f'font-size:11px;text-shadow:0 1px 2px rgba(0,0,0,0.5);float:right;">{priority}</span>'
            f'<br><span style="color:#B8D4E8;font-size:13px;">{why}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Treasure chests section
    chests = tips_data.get("treasure_chests", {})
    if chests:
        st.markdown("### Treasure Chests")

        spawn_type = chests.get("spawn_type", "")
        contents = chests.get("contents", "")
        strategy = chests.get("strategy", "")

        st.markdown(
            f'<div style="background:rgba(243,156,18,0.15);border:2px solid #F39C12;'
            f'padding:16px;border-radius:8px;margin-bottom:12px;">'
            f'<strong style="color:#F39C12;">Chest Spawn Type</strong><br>'
            f'<span style="color:#E8F4F8;">{spawn_type}</span><br><br>'
            f'<strong style="color:#F39C12;">Contents</strong><br>'
            f'<span style="color:#E8F4F8;">{contents}</span><br><br>'
            f'<strong style="color:#2ECC71;">Strategy</strong><br>'
            f'<span style="color:#E8F4F8;">{strategy}</span>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_daybreak_page():
    """Render the main Daybreak Island page."""
    st.markdown("# Daybreak Island Guide")
    st.markdown("Combat buffs from Battle Decorations and Tree of Life. **Decorations > Tree of Life for combat.**")

    # Quick summary - combat focus warning
    st.markdown(
        '<div style="background:linear-gradient(135deg, rgba(231,76,60,0.2), rgba(243,156,18,0.2));'
        'border:2px solid #E74C3C;padding:16px;border-radius:12px;margin-bottom:20px;">'
        '<strong style="color:#E74C3C;font-size:16px;">Don\'t Chase Prosperity Score!</strong><br><br>'
        '<span style="color:#E8F4F8;">'
        'Focus on <strong>COMBAT STATS</strong>, not a high island score. Mythic Battle Decorations give '
        '<strong>+10% Attack AND +10% Defense</strong> for your troop type - '
        '<strong>MORE</strong> than Tree of Life Level 10 gives universally. '
        'Upgrade Lumber Camps and Tree first to maximize Life Essence production!'
        '</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Getting Started",
        "Battle Decorations",
        "Tree of Life",
        "Strategy"
    ])

    with tab1:
        render_new_player_tips()

    with tab2:
        render_battle_decorations()

    with tab3:
        render_overview()
        st.markdown("---")
        render_tree_of_life()

    with tab4:
        render_upgrade_strategy()
        st.markdown("---")
        render_common_mistakes()


# Main
render_daybreak_page()

# Close database session
db.close()
