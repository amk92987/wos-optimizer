"""
Battle Strategies - Advanced tactics for Castle Battles, Bear Trap, Foundry, and Frostfire Mine.
Coordination techniques that win battles against stronger opponents.
"""

import streamlit as st
from pathlib import Path
import sys
import json

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

# Load battle strategies
STRATEGIES_PATH = PROJECT_ROOT / "data" / "guides" / "battle_strategies.json"
if STRATEGIES_PATH.exists():
    with open(STRATEGIES_PATH) as f:
        BATTLE_STRATEGIES = json.load(f)
else:
    BATTLE_STRATEGIES = {}


def get_priority_color(priority):
    """Get color for priority level."""
    colors = {
        "CRITICAL": "#E74C3C",
        "HIGH": "#F39C12",
        "MEDIUM": "#3498DB",
        "LOW": "#2ECC71"
    }
    return colors.get(priority, "#666")


def render_tactic_card(tactic_id, tactic_data):
    """Render a single tactic card."""
    name = tactic_data.get("name", tactic_id)
    priority = tactic_data.get("priority", "MEDIUM")
    priority_color = get_priority_color(priority)
    description = tactic_data.get("description", "")
    how_it_works = tactic_data.get("how_it_works", [])
    execution_tips = tactic_data.get("execution_tips", [])
    why_effective = tactic_data.get("why_effective", "")
    common_mistakes = tactic_data.get("common_mistakes", [])
    timing_window = tactic_data.get("timing_window", "")
    advanced_note = tactic_data.get("advanced_note", "")
    when_to_use = tactic_data.get("when_to_use", [])
    risks = tactic_data.get("risks", "")

    with st.expander(f"**{name}** - {description}", expanded=False):
        # Priority badge
        st.markdown(f"""
        <span style="background:{priority_color};color:white;padding:4px 12px;border-radius:4px;font-weight:bold;font-size:12px;">
            {priority} PRIORITY
        </span>
        """, unsafe_allow_html=True)

        # How it works
        if how_it_works:
            st.markdown("#### How It Works")
            for i, step in enumerate(how_it_works, 1):
                st.markdown(f"**{i}.** {step}")

        # Why effective
        if why_effective:
            st.markdown("#### Why It's Effective")
            st.info(why_effective)

        # Timing window
        if timing_window:
            st.markdown("#### Timing Window")
            st.warning(timing_window)

        # Execution tips
        if execution_tips:
            st.markdown("#### Execution Tips")
            for tip in execution_tips:
                st.markdown(f"- {tip}")

        # When to use
        if when_to_use:
            st.markdown("#### When to Use")
            for use in when_to_use:
                st.markdown(f"- {use}")

        # Advanced note
        if advanced_note:
            st.markdown("#### Advanced Note")
            st.caption(advanced_note)

        # Risks
        if risks:
            st.markdown("#### Risks")
            st.error(risks)

        # Common mistakes
        if common_mistakes:
            st.markdown("#### Common Mistakes")
            for mistake in common_mistakes:
                st.markdown(f"- {mistake}")


def render_castle_battles():
    """Render castle/facility battle strategies."""
    castle_data = BATTLE_STRATEGIES.get("castle_battles", {})

    st.markdown("### Castle Battles / Facility Battles")
    st.markdown(castle_data.get("overview", ""))

    # Quick win message
    st.success("**Key Insight**: A well-coordinated double rally beats a stronger garrison every time. Timing > Raw Power.")

    # Attack tactics
    st.markdown("---")
    st.markdown("## Attack Tactics")
    st.markdown("*How to take facilities from defenders*")

    attack_tactics = castle_data.get("attack_tactics", {})

    # Order by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sorted_tactics = sorted(
        attack_tactics.items(),
        key=lambda x: priority_order.get(x[1].get("priority", "MEDIUM"), 2)
    )

    for tactic_id, tactic_data in sorted_tactics:
        render_tactic_card(tactic_id, tactic_data)

    # Defense tactics
    st.markdown("---")
    st.markdown("## Defense Tactics")
    st.markdown("*How to hold facilities against attackers*")

    defense_tactics = castle_data.get("defense_tactics", {})
    sorted_defense = sorted(
        defense_tactics.items(),
        key=lambda x: priority_order.get(x[1].get("priority", "MEDIUM"), 2)
    )

    for tactic_id, tactic_data in sorted_defense:
        render_tactic_card(tactic_id, tactic_data)

    # Coordination requirements
    st.markdown("---")
    st.markdown("## Coordination Requirements")

    coord_req = castle_data.get("coordination_requirements", {})
    cols = st.columns(2)
    for i, (req_name, req_desc) in enumerate(coord_req.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.15);padding:12px;border-radius:8px;margin-bottom:8px;">
                <div style="font-weight:bold;color:#4A90D9;text-transform:capitalize;">{req_name.replace('_', ' ')}</div>
                <div style="color:#B8D4E8;font-size:14px;">{req_desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Common mistakes
    st.markdown("---")
    st.markdown("## Common Mistakes to Avoid")

    mistakes = castle_data.get("common_mistakes", [])
    for mistake in mistakes:
        st.markdown(f"""
        <div style="background:rgba(74,144,217,0.1);padding:12px;border-radius:8px;margin-bottom:8px;">
            <div style="color:#E74C3C;font-weight:bold;margin-bottom:4px;">
                {mistake.get('mistake', '')}
            </div>
            <div style="color:#2ECC71;">
                {mistake.get('correction', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Quick reference checklists
    st.markdown("---")
    st.markdown("## Quick Reference Checklists")

    quick_ref = castle_data.get("quick_reference", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Double Rally Checklist")
        checklist = quick_ref.get("double_rally_checklist", [])
        for item in checklist:
            st.checkbox(item, key=f"dr_{item[:20]}", value=False)

    with col2:
        st.markdown("#### Garrison Defense Checklist")
        checklist = quick_ref.get("garrison_defense_checklist", [])
        for item in checklist:
            st.checkbox(item, key=f"gd_{item[:20]}", value=False)


def render_foundry():
    """Render foundry strategies."""
    foundry_data = BATTLE_STRATEGIES.get("foundry", {})

    st.markdown("### Foundry Clash")
    st.markdown(foundry_data.get("overview", foundry_data.get("description", "")))

    # Event basics
    basics = foundry_data.get("event_basics", {})
    if basics:
        st.success(f"**Duration**: {basics.get('duration', '60 minutes')} | **Frequency**: {basics.get('frequency', 'Biweekly')} | **Key**: {basics.get('key_mechanic', 'No troop deaths')}")

    # Phases overview
    phases = foundry_data.get("phases", {})
    if phases:
        st.markdown("---")
        st.markdown("## Battle Phases")

        for phase_id, phase_data in phases.items():
            phase_name = phase_id.replace("_", " ").title()
            with st.expander(f"**{phase_name}** ({phase_data.get('time', '')})", expanded=False):
                st.markdown(f"**Priority**: {phase_data.get('priority', '')}")
                buildings = phase_data.get("buildings", [])
                if buildings:
                    st.markdown("**Buildings Available:**")
                    for b in buildings:
                        st.markdown(f"- {b}")

    # Buildings value
    buildings = foundry_data.get("buildings", {})
    if buildings:
        st.markdown("---")
        st.markdown("## Building Values")

        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_buildings = sorted(
            buildings.items(),
            key=lambda x: priority_order.get(x[1].get("priority", "MEDIUM"), 2)
        )

        for building_id, building_data in sorted_buildings:
            name = building_id.replace("_", " ").title()
            priority = building_data.get("priority", "MEDIUM")
            priority_color = get_priority_color(priority)
            first_cap = building_data.get("first_capture", 0)
            per_min = building_data.get("points_per_minute", 0)
            special = building_data.get("special", "")

            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.1);padding:12px;border-radius:8px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:bold;color:#4A90D9;">{name}</span>
                    <span style="background:{priority_color};color:white;padding:2px 8px;border-radius:4px;font-size:11px;">{priority}</span>
                </div>
                <div style="color:#B8D4E8;font-size:13px;margin-top:4px;">
                    {f"First Capture: {first_cap:,} pts | {per_min:,} pts/min" if first_cap else ""}
                    {f"<br><em>{special}</em>" if special else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Strategies
    strategies = foundry_data.get("strategies", {})
    if strategies:
        st.markdown("---")
        st.markdown("## Strategies")

        for strat_id, strat_data in strategies.items():
            name = strat_data.get("name", strat_id.replace("_", " ").title())
            priority = strat_data.get("priority", "MEDIUM")
            steps = strat_data.get("steps", [])
            description = strat_data.get("description", "")

            with st.expander(f"**{name}**", expanded=False):
                if description:
                    st.info(description)
                if steps:
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"**{i}.** {step}")

    # Player strategies by spending level
    player_strats = foundry_data.get("player_strategies", {})
    if player_strats:
        st.markdown("---")
        st.markdown("## Strategy by Spending Level")

        cols = st.columns(3)
        for i, (level, data) in enumerate(player_strats.items()):
            with cols[i % 3]:
                st.markdown(f"#### {level.upper()}")
                st.markdown(f"**Focus**: {data.get('focus', '')}")
                st.markdown(f"**Avoid**: {data.get('avoid', '')}")

    # Common mistakes
    mistakes = foundry_data.get("common_mistakes", [])
    if mistakes:
        st.markdown("---")
        st.markdown("## Common Mistakes to Avoid")

        for mistake in mistakes:
            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.1);padding:12px;border-radius:8px;margin-bottom:8px;">
                <div style="color:#E74C3C;font-weight:bold;margin-bottom:4px;">
                    {mistake.get('mistake', '')}
                </div>
                <div style="color:#2ECC71;">
                    {mistake.get('correction', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Quick reference
    quick_ref = foundry_data.get("quick_reference", {})
    if quick_ref:
        st.markdown("---")
        st.markdown("## Quick Reference")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Pre-Battle Checklist")
            for item in quick_ref.get("pre_battle_checklist", []):
                st.checkbox(item, key=f"fc_pre_{item[:15]}", value=False)

        with col2:
            st.markdown("#### Phase Priorities")
            for item in quick_ref.get("phase_priorities", []):
                st.markdown(f"- {item}")


def render_frostfire():
    """Render frostfire mine strategies."""
    frostfire_data = BATTLE_STRATEGIES.get("frostfire_mine", {})

    st.markdown("### Frostfire Mine")
    st.markdown(frostfire_data.get("overview", frostfire_data.get("description", "")))

    # Event basics
    basics = frostfire_data.get("event_basics", {})
    if basics:
        st.success(f"**Duration**: {basics.get('duration', '30 minutes')} | **Key**: {basics.get('key_mechanic', 'NO troop losses!')}")

    # Skill progression - important section
    skill_prog = frostfire_data.get("skill_progression", {})
    if skill_prog:
        st.markdown("---")
        st.markdown("## Skill Progression (IMPORTANT)")
        st.info(skill_prog.get("description", ""))

        recommended = skill_prog.get("recommended_build", {})
        if recommended:
            st.markdown(f"### {recommended.get('name', 'Recommended Build')}")

            skill_order = ["level_1", "level_2", "level_3", "level_4", "level_5"]
            for skill_key in skill_order:
                if skill_key in recommended:
                    skill = recommended[skill_key]
                    level_num = skill_key.replace("level_", "")
                    choice = skill.get("choice", "")
                    effect = skill.get("effect", "")
                    st.markdown(f"""
                    <div style="background:rgba(46,204,113,0.15);padding:8px 12px;border-radius:6px;margin-bottom:6px;">
                        <span style="font-weight:bold;color:#2ECC71;">Level {level_num}:</span>
                        <span style="color:#F39C12;font-weight:bold;">{choice}</span> -
                        <span style="color:#B8D4E8;">{effect}</span>
                    </div>
                    """, unsafe_allow_html=True)

            tip = skill_prog.get("skill_5_tip", "")
            if tip:
                st.warning(f"**Skill 5 Tip**: {tip}")

    # Map elements
    map_elements = frostfire_data.get("map_elements", {})
    if map_elements:
        st.markdown("---")
        st.markdown("## Map Elements")

        # Vein Outbursts - most important
        outbursts = map_elements.get("vein_outbursts", {})
        if outbursts:
            st.markdown("### Vein Outbursts (CRITICAL)")
            st.error(f"**{outbursts.get('capacity', 4000)} Orichalcum in {outbursts.get('deplete_time', '20 seconds')}!** {outbursts.get('priority', '')}")
            spawn_times = outbursts.get("spawn_times", [])
            if spawn_times:
                st.markdown(f"**Spawn Times**: {', '.join(spawn_times)}")
            st.markdown(f"**Alerts**: {outbursts.get('alerts', '')}")

        # Regular veins
        veins = map_elements.get("veins", {})
        if veins:
            st.markdown("### Regular Veins")
            levels = veins.get("levels", [])
            if levels:
                cols = st.columns(3)
                for i, level in enumerate(levels):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background:rgba(74,144,217,0.15);padding:10px;border-radius:6px;text-align:center;">
                            <div style="font-weight:bold;color:#4A90D9;">Level {level.get('level', i+1)}</div>
                            <div style="color:#B8D4E8;font-size:13px;">{level.get('rate', '')}</div>
                            <div style="color:#888;font-size:12px;">Capacity: {level.get('capacity', 0):,}</div>
                        </div>
                        """, unsafe_allow_html=True)
            loot = veins.get("loot_mechanic", "")
            if loot:
                st.caption(loot)

        # Smelter
        smelter = map_elements.get("smelter", {})
        if smelter:
            st.markdown("### Smelter")
            st.warning(f"**Opens at**: {smelter.get('opens_at', '')} remaining")
            rewards = smelter.get("rewards", {})
            if rewards:
                st.markdown(f"**Rewards**: 1st Place: {rewards.get('1st_place', 0):,} | 10th Place: {rewards.get('10th_place', 0):,}")

    # Critical timing
    timing = frostfire_data.get("critical_timing", [])
    if timing:
        st.markdown("---")
        st.markdown("## Critical Timing Events")

        for event in timing:
            st.markdown(f"""
            <div style="background:rgba(243,156,18,0.15);padding:8px 12px;border-radius:6px;margin-bottom:6px;">
                <span style="font-weight:bold;color:#F39C12;">{event.get('time_remaining', '')}</span> -
                <span style="color:#B8D4E8;">{event.get('event', '')}</span>
            </div>
            """, unsafe_allow_html=True)

    # Strategies
    strategies = frostfire_data.get("strategies", {})
    if strategies:
        st.markdown("---")
        st.markdown("## Strategies")

        for strat_id, strat_data in strategies.items():
            name = strat_data.get("name", strat_id.replace("_", " ").title())
            priority = strat_data.get("priority", "MEDIUM")
            philosophy = strat_data.get("philosophy", "")
            steps = strat_data.get("steps", [])
            pros = strat_data.get("pros", "")
            cons = strat_data.get("cons", "")

            with st.expander(f"**{name}**", expanded=False):
                if philosophy:
                    st.info(philosophy)
                if steps:
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"**{i}.** {step}")
                if pros or cons:
                    col1, col2 = st.columns(2)
                    with col1:
                        if pros:
                            st.markdown(f"**Pros**: {pros}")
                    with col2:
                        if cons:
                            st.markdown(f"**Cons**: {cons}")

    # Common mistakes
    mistakes = frostfire_data.get("common_mistakes", [])
    if mistakes:
        st.markdown("---")
        st.markdown("## Common Mistakes to Avoid")

        for mistake in mistakes:
            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.1);padding:12px;border-radius:8px;margin-bottom:8px;">
                <div style="color:#E74C3C;font-weight:bold;margin-bottom:4px;">
                    {mistake.get('mistake', '')}
                </div>
                <div style="color:#2ECC71;">
                    {mistake.get('correction', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Quick reference
    quick_ref = frostfire_data.get("quick_reference", {})
    if quick_ref:
        st.markdown("---")
        st.markdown("## Quick Reference")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### During Event")
            for item in quick_ref.get("during_event", []):
                st.markdown(f"- {item}")

        with col2:
            st.markdown("#### Don't Forget")
            for item in quick_ref.get("dont_forget", []):
                st.checkbox(item, key=f"ff_df_{item[:15]}", value=False)


def render_bear_trap():
    """Render bear trap strategies."""
    bear_data = BATTLE_STRATEGIES.get("bear_trap", {})

    st.markdown("### Bear Trap (Bear Hunt)")
    st.markdown(bear_data.get("overview", bear_data.get("description", "")))

    # Event basics
    basics = bear_data.get("event_basics", {})
    if basics:
        st.error(f"**{basics.get('priority', 'S-TIER EVENT')}** - {basics.get('skill_type', 'Uses EXPEDITION skills')}")

    # Rally mechanics
    rally_mech = bear_data.get("rally_mechanics", {})
    if rally_mech:
        st.markdown("---")
        st.markdown("## Rally Mechanics")

        leader = rally_mech.get("leader_contribution", {})
        joiner = rally_mech.get("joiner_contribution", {})

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Rally Leader")
            st.markdown(leader.get("description", ""))
            if leader.get("note"):
                st.info(leader.get("note"))

        with col2:
            st.markdown("#### Rally Joiner")
            st.markdown(joiner.get("description", ""))
            st.markdown(f"**Selection**: {joiner.get('selection', '')}")
            if joiner.get("tip"):
                st.warning(joiner.get("tip"))

    # Troop composition
    troop_comp = bear_data.get("troop_composition", {})
    if troop_comp:
        st.markdown("---")
        st.markdown("## Optimal Troop Composition")

        optimal = troop_comp.get("optimal", {})
        if optimal:
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div style="background:rgba(231,76,60,0.15);padding:15px;border-radius:8px;text-align:center;">
                    <div style="font-weight:bold;color:#E74C3C;font-size:24px;">{optimal.get('infantry', '0-10%')}</div>
                    <div style="color:#B8D4E8;">Infantry</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div style="background:rgba(52,152,219,0.15);padding:15px;border-radius:8px;text-align:center;">
                    <div style="font-weight:bold;color:#3498DB;font-size:24px;">{optimal.get('lancer', '10%')}</div>
                    <div style="color:#B8D4E8;">Lancer</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div style="background:rgba(46,204,113,0.15);padding:15px;border-radius:8px;text-align:center;">
                    <div style="font-weight:bold;color:#2ECC71;font-size:24px;">{optimal.get('marksman', '80-90%')}</div>
                    <div style="color:#B8D4E8;">Marksman</div>
                </div>
                """, unsafe_allow_html=True)

        st.info(f"**Why Marksman?** {troop_comp.get('why_marksman', '')}")

    # Hero selection
    hero_sel = bear_data.get("hero_selection", {})
    if hero_sel:
        st.markdown("---")
        st.markdown("## Hero Selection")

        st.markdown("### Best Joiners (Expedition Skills)")
        best_joiners = hero_sel.get("best_joiners", [])
        for joiner in best_joiners:
            priority = joiner.get("priority", "HIGH")
            priority_color = get_priority_color(priority) if priority != "BEST" else "#9B59B6"
            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.1);padding:10px;border-radius:8px;margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:bold;color:#4A90D9;">{joiner.get('hero', '')}</span>
                    <span style="background:{priority_color};color:white;padding:2px 8px;border-radius:4px;font-size:11px;">{priority}</span>
                </div>
                <div style="color:#2ECC71;font-weight:bold;">{joiner.get('skill', '')}</div>
                <div style="color:#888;font-size:12px;">{joiner.get('note', '')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Heroes to AVOID")
        avoid = hero_sel.get("heroes_to_avoid", [])
        for hero in avoid:
            st.error(f"**{hero.get('hero', '')}**: {hero.get('reason', '')}")

        slot_placement = hero_sel.get("slot_placement", "")
        if slot_placement:
            st.warning(f"**Slot Placement**: {slot_placement}")

    # Strategies
    strategies = bear_data.get("strategies", {})
    if strategies:
        st.markdown("---")
        st.markdown("## Strategies")

        for strat_id, strat_data in strategies.items():
            name = strat_data.get("name", strat_id.replace("_", " ").title())
            priority = strat_data.get("priority", "MEDIUM")
            steps = strat_data.get("steps", [])

            with st.expander(f"**{name}**", expanded=False):
                priority_color = get_priority_color(priority)
                st.markdown(f"""
                <span style="background:{priority_color};color:white;padding:4px 12px;border-radius:4px;font-weight:bold;font-size:12px;">
                    {priority} PRIORITY
                </span>
                """, unsafe_allow_html=True)
                if steps:
                    st.markdown("")
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"**{i}.** {step}")

    # Common mistakes
    mistakes = bear_data.get("common_mistakes", [])
    if mistakes:
        st.markdown("---")
        st.markdown("## Common Mistakes to Avoid")

        for mistake in mistakes:
            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.1);padding:12px;border-radius:8px;margin-bottom:8px;">
                <div style="color:#E74C3C;font-weight:bold;margin-bottom:4px;">
                    {mistake.get('mistake', '')}
                </div>
                <div style="color:#2ECC71;">
                    {mistake.get('correction', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Quick reference
    quick_ref = bear_data.get("quick_reference", {})
    if quick_ref:
        st.markdown("---")
        st.markdown("## Quick Reference")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Joiner Checklist")
            for item in quick_ref.get("joiner_checklist", []):
                st.checkbox(item, key=f"bt_jc_{item[:15]}", value=False)

        with col2:
            st.markdown("#### Leader Checklist")
            for item in quick_ref.get("leader_checklist", []):
                st.checkbox(item, key=f"bt_lc_{item[:15]}", value=False)

        st.markdown("#### Best Expedition Skills")
        skills = quick_ref.get("best_expedition_skills", [])
        cols = st.columns(len(skills))
        for i, skill in enumerate(skills):
            with cols[i]:
                st.markdown(f"""
                <div style="background:rgba(46,204,113,0.1);padding:8px;border-radius:6px;text-align:center;font-size:12px;">
                    {skill}
                </div>
                """, unsafe_allow_html=True)


def render_battle_strategies():
    """Render the battle strategies page."""
    st.markdown("# Battle Strategies")
    st.markdown("Advanced tactics for competitive events. Coordination and timing beat raw power.")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Castle Battles",
        "Bear Trap",
        "Foundry",
        "Frostfire Mine"
    ])

    with tab1:
        render_castle_battles()

    with tab2:
        render_bear_trap()

    with tab3:
        render_foundry()

    with tab4:
        render_frostfire()

    # Footer
    st.markdown("---")
    st.caption("Battle strategies are most effective with alliance coordination. Practice these tactics before important events!")


# Main
render_battle_strategies()

# Close database session
db.close()
