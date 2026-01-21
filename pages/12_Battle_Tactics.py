"""
Battle Strategies - Advanced tactics for Castle Battles, Bear Trap, Canyon Clash, Foundry, and Frostfire Mine.
Coordination techniques that win battles against stronger opponents.
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

# Load battle strategies
STRATEGIES_PATH = PROJECT_ROOT / "data" / "guides" / "battle_strategies.json"
if STRATEGIES_PATH.exists():
    with open(STRATEGIES_PATH, encoding='utf-8') as f:
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
            st.markdown(f"- {item}")

    with col2:
        st.markdown("#### Garrison Defense Checklist")
        checklist = quick_ref.get("garrison_defense_checklist", [])
        for item in checklist:
            st.markdown(f"- {item}")


def render_foundry():
    """Render foundry strategies."""
    foundry_data = BATTLE_STRATEGIES.get("foundry", {})

    st.markdown("### Foundry Clash")
    st.markdown(foundry_data.get("overview", foundry_data.get("description", "")))

    # Event basics
    basics = foundry_data.get("event_basics", {})
    if basics:
        st.success(f"**Duration**: {basics.get('duration', '60 minutes')} | **Frequency**: {basics.get('frequency', 'Biweekly')} | **Key**: {basics.get('key_mechanic', 'No troop deaths')}")

    # Battlefield Map Image
    with st.expander("View Battlefield Map", expanded=False):
        st.markdown("*Map showing building locations and layout*")
        try:
            st.image(
                "https://cdn-www.bluestacks.com/bs-images/WhiteoutSurvival_Guide_FoundryBattleGuide_EN2.jpg",
                caption="Foundry Battle Map (Source: BlueStacks)",
                width="stretch"
            )
        except Exception:
            st.warning("Could not load map image. View it at: [BlueStacks Foundry Guide](https://www.bluestacks.com/blog/game-guides/white-out-survival/wos-foundry-battle-event-guide-en.html)")

        st.caption("Key locations: Imperial Foundry (center), Transit Station (50% teleport CD), Boiler Room (faster captures)")

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

            # Build details text
            details_parts = []
            if first_cap:
                details_parts.append(f"First Capture: {first_cap:,} pts | {per_min:,} pts/min")
            if special:
                details_parts.append(f"<em>{special}</em>")
            details_html = "<br>".join(details_parts) if details_parts else ""

            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.1);padding:12px;border-radius:8px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:bold;color:#4A90D9;">{name}</span>
                    <span style="background:{priority_color};color:white;padding:2px 8px;border-radius:4px;font-size:11px;">{priority}</span>
                </div>
                <div style="color:#B8D4E8;font-size:13px;margin-top:4px;">{details_html}</div>
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
            structure = strat_data.get("structure", {})
            tip = strat_data.get("tip", "")
            when_to_use = strat_data.get("when_to_use", "")

            with st.expander(f"**{name}**", expanded=False):
                if description:
                    st.info(description)
                if steps:
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"**{i}.** {step}")
                # Handle structure field (for Team Division)
                if structure:
                    for role, desc in structure.items():
                        role_name = role.replace("_", " ").title()
                        st.markdown(f"- **{role_name}**: {desc}")
                if tip:
                    st.success(f"**Tip**: {tip}")
                if when_to_use:
                    st.caption(f"**When to use**: {when_to_use}")

    # Team Coordination (Discord strategies)
    team_coord = foundry_data.get("team_coordination", {})
    if team_coord:
        st.markdown("---")
        st.markdown("## Team Coordination (Discord/Voice)")
        st.info(team_coord.get("description", ""))

        # Team Structure
        team_struct = team_coord.get("team_structure", {})
        if team_struct:
            with st.expander("**4-Team Formation** - How to split your 30 players", expanded=True):
                st.markdown(f"*{team_struct.get('overview', '')}*")

                teams = team_struct.get("teams", {})
                cols = st.columns(2)

                for i, (team_id, team_data) in enumerate(teams.items()):
                    with cols[i % 2]:
                        is_attack = team_id.startswith("A")
                        color = "#E74C3C" if is_attack else "#3498DB"
                        st.markdown(f"""
                        <div style="background:rgba({'231,76,60' if is_attack else '52,152,219'},0.15);
                                    border-left:4px solid {color};padding:12px;border-radius:8px;margin-bottom:8px;">
                            <div style="font-weight:bold;color:{color};font-size:16px;">{team_id}: {team_data.get('name', '')}</div>
                            <div style="color:#F39C12;font-size:13px;margin:4px 0;">{team_data.get('size', '')} - {team_data.get('composition', '')}</div>
                            <div style="color:#B8D4E8;font-size:13px;">{team_data.get('role', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                subs = team_struct.get("substitutes", "")
                if subs:
                    st.caption(f"**Substitutes**: {subs}")

        # Attack Rotation
        attack_rot = team_coord.get("attack_rotation", {})
        if attack_rot:
            with st.expander(f"**{attack_rot.get('name', 'Attack Rotation')}** - Never let enemy rest", expanded=False):
                st.markdown(attack_rot.get("description", ""))

                cycle = attack_rot.get("cycle", [])
                for phase in cycle:
                    phase_name = phase.get("phase", "")
                    a1_action = phase.get("A1", "")
                    a2_action = phase.get("A2", "")
                    note = phase.get("note", "")

                    if note:
                        st.markdown(f"**{phase_name}**: {note}")
                    else:
                        st.markdown(f"""
                        <div style="background:rgba(74,144,217,0.1);padding:8px 12px;border-radius:6px;margin-bottom:6px;">
                            <span style="font-weight:bold;color:#F39C12;">{phase_name}:</span>
                            <span style="color:#E74C3C;">A1: {a1_action}</span> |
                            <span style="color:#3498DB;">A2: {a2_action}</span>
                        </div>
                        """, unsafe_allow_html=True)

                insight = attack_rot.get("key_insight", "")
                if insight:
                    st.success(f"**Key Insight**: {insight}")

        # Double Rally Strike
        coord_strikes = team_coord.get("coordinated_strikes", {})
        if coord_strikes:
            with st.expander(f"**{coord_strikes.get('name', 'Double Rally')}** - CRITICAL tactic", expanded=False):
                st.markdown(coord_strikes.get("description", ""))

                execution = coord_strikes.get("execution", [])
                if execution:
                    st.markdown("#### Execution Steps")
                    for i, step in enumerate(execution, 1):
                        st.markdown(f"**{i}.** {step}")

                timing = coord_strikes.get("timing_script", {})
                if timing:
                    st.markdown("#### Discord Script")
                    st.markdown(f"""
                    <div style="background:rgba(155,89,182,0.2);border:1px solid #9B59B6;padding:12px;border-radius:8px;font-family:monospace;">
                        <div style="color:#9B59B6;margin-bottom:4px;">Captain: {timing.get('captain', '')}</div>
                        <div style="color:#E74C3C;margin-bottom:4px;">A1 Leader: {timing.get('a1_leader', '')}</div>
                        <div style="color:#9B59B6;margin-bottom:4px;">Captain: {timing.get('captain', '').split(',')[0] if ',' in str(timing.get('captain', '')) else 'A2 follow countdown...'}</div>
                        <div style="color:#3498DB;">A2 Leader: {timing.get('a2_leader', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                why = coord_strikes.get("why_10_seconds", "")
                if why:
                    st.caption(f"**Why 10 seconds?** {why}")

        # Final Push
        final_push = team_coord.get("final_push", {})
        if final_push:
            with st.expander(f"**{final_push.get('name', 'Final Push')}** - Win in the last 10 minutes", expanded=False):
                st.warning(f"**When to use**: {final_push.get('when_to_use', '')}")
                st.markdown(final_push.get("description", ""))

                execution = final_push.get("execution", [])
                if execution:
                    st.markdown("#### Execution")
                    for i, step in enumerate(execution, 1):
                        st.markdown(f"**{i}.** {step}")

                factors = final_push.get("success_factors", [])
                if factors:
                    st.markdown("#### Success Factors")
                    for factor in factors:
                        st.markdown(f"- {factor}")

        # Discord Callouts
        callouts = team_coord.get("discord_callouts", {})
        if callouts:
            with st.expander(f"**{callouts.get('name', 'Voice Chat')}** - Standard callouts", expanded=False):
                st.markdown(callouts.get("description", ""))

                roles = callouts.get("roles", {})
                if roles:
                    st.markdown("#### Designated Roles")
                    for role, desc in roles.items():
                        role_name = role.replace("_", " ").title()
                        st.markdown(f"- **{role_name}**: {desc}")

                std_callouts = callouts.get("standard_callouts", [])
                if std_callouts:
                    st.markdown("#### Standard Callouts")
                    for callout in std_callouts:
                        st.markdown(f"""
                        <div style="background:rgba(46,204,113,0.1);padding:6px 10px;border-radius:4px;margin-bottom:4px;font-family:monospace;font-size:13px;">
                            {callout}
                        </div>
                        """, unsafe_allow_html=True)

        # Building Assignments
        bldg_assign = team_coord.get("building_assignments", {})
        if bldg_assign:
            with st.expander("**Building Assignments** - Pre-assign to avoid confusion", expanded=False):
                st.markdown(bldg_assign.get("description", ""))

                for phase_id in ["phase_1", "phase_2", "phase_3"]:
                    phase_data = bldg_assign.get(phase_id, {})
                    if phase_data:
                        phase_name = phase_id.replace("_", " ").title()
                        st.markdown(f"**{phase_name}**")

                        if "all_teams" in phase_data:
                            st.markdown(f"- All Teams: {phase_data['all_teams']}")
                        else:
                            for team, assignment in phase_data.items():
                                if isinstance(assignment, list):
                                    st.markdown(f"- **{team}**: {', '.join(assignment)}")
                                else:
                                    st.markdown(f"- **{team}**: {assignment}")

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
                st.markdown(f"- {item}")

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

    # Skill Build - prominent at top
    skill_build = frostfire_data.get("skill_build", {})
    if skill_build:
        tldr = skill_build.get("tldr", "R-R-L-L-R")
        st.markdown(f"""
        <div style="background:rgba(155,89,182,0.2);border:2px solid #9B59B6;padding:16px;border-radius:12px;margin:16px 0;">
            <div style="display:flex;align-items:center;gap:16px;">
                <div style="font-size:14px;color:#9B59B6;font-weight:bold;">SKILL BUILD:</div>
                <div style="font-size:32px;font-weight:bold;color:#2ECC71;letter-spacing:8px;">{tldr}</div>
            </div>
            <div style="color:#888;font-size:12px;margin-top:8px;">Right → Right → Left → Left → Right</div>
        </div>
        """, unsafe_allow_html=True)

        # Skill details in expander
        with st.expander("View Skill Details", expanded=False):
            st.caption(skill_build.get("description", ""))
            recommended = skill_build.get("recommended_build", {})
            if recommended:
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
                tip = skill_build.get("skill_5_tip", "")
                if tip:
                    st.warning(f"**Skill 5 Tip**: {tip}")

    # Minute-by-Minute Play-by-Play
    minute_by_minute = frostfire_data.get("minute_by_minute", {})
    if minute_by_minute:
        with st.expander("📋 Minute-by-Minute Play-by-Play", expanded=True):
            st.caption(minute_by_minute.get("description", ""))

            # Column headers
            st.markdown("""
            <div style="display:flex;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.1);">
                <div style="width:120px;font-weight:bold;color:#4A90D9;font-size:14px;">Event Time</div>
                <div style="flex:1;font-weight:bold;color:#4A90D9;font-size:14px;">Strategy</div>
            </div>
            """, unsafe_allow_html=True)

            phases = minute_by_minute.get("phases", [])
            for phase_data in phases:
                time = phase_data.get("time", "")
                phase = phase_data.get("phase", "")
                priority = phase_data.get("priority", "MEDIUM")
                actions = phase_data.get("actions", [])

                # Color based on priority
                if priority == "CRITICAL":
                    bg_color = "rgba(231,76,60,0.2)"
                    border_color = "#E74C3C"
                elif priority == "HIGH":
                    bg_color = "rgba(243,156,18,0.15)"
                    border_color = "#F39C12"
                elif priority == "SITUATIONAL":
                    bg_color = "rgba(155,89,182,0.15)"
                    border_color = "#9B59B6"
                else:
                    bg_color = "rgba(74,144,217,0.1)"
                    border_color = "#3498DB"

                # Two-column layout: timestamp outside, strategy inside box
                st.markdown(f"""
                <div style="display:flex;margin-bottom:10px;align-items:flex-start;">
                    <div style="width:120px;flex-shrink:0;padding-top:12px;">
                        <span style="font-weight:bold;color:{border_color};font-size:15px;">{time}</span>
                    </div>
                    <div style="flex:1;background:{bg_color};border-left:4px solid {border_color};padding:12px;border-radius:6px;">
                        <div style="font-weight:bold;color:#E8F4F8;margin-bottom:8px;">{phase}</div>
                        {"".join([f'<div style="color:#B8D4E8;font-size:13px;">• {action}</div>' for action in actions])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

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

        # Smelter - with "Is it worth it?" decision
        smelter = map_elements.get("smelter", {})
        if smelter:
            st.markdown("### Smelter (Middle Objective)")
            st.warning(f"**Opens at**: {smelter.get('opens_at', '')} remaining")

            # Is it worth it? section
            worth_it = smelter.get("is_it_worth_it", {})
            if worth_it:
                short_answer = worth_it.get("short_answer", "NO for most players")
                explanation = worth_it.get("explanation", "")
                go_for_it = worth_it.get("go_for_it_if", [])
                skip_it = worth_it.get("skip_it_if", [])
                alternative = worth_it.get("better_alternative", "")

                st.markdown(f"""
                <div style="background:rgba(231,76,60,0.15);border:2px solid #E74C3C;padding:16px;border-radius:12px;margin:12px 0;">
                    <div style="font-weight:bold;color:#E74C3C;font-size:16px;margin-bottom:8px;">
                        🎯 Is the Smelter Worth It?
                    </div>
                    <div style="font-size:24px;font-weight:bold;color:#E74C3C;margin-bottom:12px;">
                        {short_answer}
                    </div>
                    <div style="color:#E8F4F8;margin-bottom:12px;">{explanation}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✓ Go for it IF:**")
                    for item in go_for_it:
                        st.markdown(f"- {item}")
                with col2:
                    st.markdown("**✗ Skip it IF:**")
                    for item in skip_it:
                        st.markdown(f"- {item}")

                if alternative:
                    st.info(f"**Better Alternative**: {alternative}")

            rewards = smelter.get("rewards", {})
            if rewards:
                st.caption(f"Rewards: 1st Place: {rewards.get('1st_place', 0):,} | 10th Place: {rewards.get('10th_place', 0):,}")

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
                st.markdown(f"- {item}")


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
            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.15);border-left:4px solid #3498DB;padding:16px;border-radius:8px;min-height:180px;">
                <div style="font-weight:bold;color:#3498DB;font-size:16px;margin-bottom:8px;">Rally Leader</div>
                <div style="color:#E8F4F8;margin-bottom:12px;">{leader.get("description", "")}</div>
                <div style="color:#B8D4E8;font-size:13px;font-style:italic;">{leader.get("note", "")}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background:rgba(46,204,113,0.15);border-left:4px solid #2ECC71;padding:16px;border-radius:8px;min-height:180px;">
                <div style="font-weight:bold;color:#2ECC71;font-size:16px;margin-bottom:8px;">Rally Joiner</div>
                <div style="color:#E8F4F8;margin-bottom:8px;">{joiner.get("description", "")}</div>
                <div style="color:#E8F4F8;margin-bottom:12px;"><strong>Selection:</strong> {joiner.get('selection', '')}</div>
                <div style="color:#F39C12;font-size:13px;font-style:italic;">{joiner.get("tip", "")}</div>
            </div>
            """, unsafe_allow_html=True)

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

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        st.info(f"**Why Marksman?** {troop_comp.get('why_marksman', '')}")

    # Hero selection
    hero_sel = bear_data.get("hero_selection", {})
    if hero_sel:
        st.markdown("---")
        st.markdown("## Hero Selection")

        # Jeronimo Decision Box - THE decisive answer
        jeronimo_decision = hero_sel.get("jeronimo_decision", {})
        if jeronimo_decision:
            answer = jeronimo_decision.get("answer", "LEAD")
            reasoning = jeronimo_decision.get("reasoning", "")
            leader_value = jeronimo_decision.get("leader_value", {})
            joiner_value = jeronimo_decision.get("joiner_value", {})
            optimal = jeronimo_decision.get("optimal_strategy", "")

            st.markdown(f"""
            <div style="background:rgba(155,89,182,0.2);border:2px solid #9B59B6;padding:20px;border-radius:12px;margin-bottom:20px;">
                <div style="font-weight:bold;color:#9B59B6;font-size:18px;margin-bottom:8px;">
                    🎯 Should Jeronimo Lead or Join Rallies?
                </div>
                <div style="font-size:28px;font-weight:bold;color:#2ECC71;margin-bottom:12px;">
                    ANSWER: {answer} RALLIES
                </div>
                <div style="color:#E8F4F8;margin-bottom:16px;">{reasoning}</div>
                <div style="display:flex;gap:16px;margin-bottom:16px;">
                    <div style="flex:1;background:rgba(46,204,113,0.2);padding:12px;border-radius:8px;">
                        <div style="font-weight:bold;color:#2ECC71;margin-bottom:4px;">As Leader ({leader_value.get('skills_applied', 3)} skills)</div>
                        <div style="color:#B8D4E8;font-size:13px;">{"<br>".join(leader_value.get('effects', []))}</div>
                    </div>
                    <div style="flex:1;background:rgba(231,76,60,0.2);padding:12px;border-radius:8px;">
                        <div style="font-weight:bold;color:#E74C3C;margin-bottom:4px;">As Joiner ({joiner_value.get('skills_applied', 1)} skill)</div>
                        <div style="color:#B8D4E8;font-size:13px;">{"<br>".join(joiner_value.get('effects', []))}</div>
                        <div style="color:#888;font-size:12px;margin-top:4px;">{joiner_value.get('comparison', '')}</div>
                    </div>
                </div>
                <div style="background:rgba(46,204,113,0.15);padding:12px;border-radius:8px;border-left:4px solid #2ECC71;">
                    <span style="font-weight:bold;color:#2ECC71;">✓ Optimal:</span>
                    <span style="color:#E8F4F8;">{optimal}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Generation-based recommendations
        gen_recs = hero_sel.get("generation_recommendations", {})
        if gen_recs:
            with st.expander("📊 Generation-Based Leader Recommendations", expanded=False):
                st.caption(gen_recs.get("description", ""))

                by_gen = gen_recs.get("by_generation", {})

                # Gen 1-7
                gen_1_7 = by_gen.get("gen_1_to_7", {})
                if gen_1_7:
                    st.markdown(f"""
                    <div style="background:rgba(74,144,217,0.15);padding:12px;border-radius:8px;margin-bottom:8px;">
                        <div style="font-weight:bold;color:#3498DB;">Gen 1-7: {gen_1_7.get('best_leader', 'Jeronimo')}</div>
                        <div style="color:#B8D4E8;font-size:13px;">{gen_1_7.get('reason', '')}</div>
                        <div style="color:#2ECC71;font-size:12px;margin-top:4px;">Best joiners: {', '.join(gen_1_7.get('best_joiners', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Gen 8+
                gen_8 = by_gen.get("gen_8_plus", {})
                if gen_8:
                    st.markdown(f"""
                    <div style="background:rgba(243,156,18,0.15);padding:12px;border-radius:8px;margin-bottom:8px;">
                        <div style="font-weight:bold;color:#F39C12;">Gen 8+: {gen_8.get('best_leader', 'Jeronimo')}</div>
                        <div style="color:#B8D4E8;font-size:13px;margin-bottom:4px;"><strong>Alternative:</strong> {gen_8.get('alternative', 'Hendrik')}</div>
                        <div style="color:#888;font-size:12px;">{gen_8.get('hendrik_case', '')}</div>
                        <div style="color:#2ECC71;font-size:12px;margin-top:4px;">Best joiners: {', '.join(gen_8.get('best_joiners', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Gen 12+
                gen_12 = by_gen.get("gen_12_plus", {})
                if gen_12:
                    st.markdown(f"""
                    <div style="background:rgba(155,89,182,0.15);padding:12px;border-radius:8px;margin-bottom:8px;">
                        <div style="font-weight:bold;color:#9B59B6;">Gen 12+: {gen_12.get('best_leader', 'Jeronimo')}</div>
                        <div style="color:#B8D4E8;font-size:13px;">{gen_12.get('why_jeronimo_wins', '')}</div>
                        <div style="color:#888;font-size:12px;margin-top:4px;">{gen_12.get('hervor_note', '')}</div>
                        <div style="color:#2ECC71;font-size:12px;margin-top:4px;">Best joiners: {', '.join(gen_12.get('best_joiners', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Exception note
                exception = gen_recs.get("exception", "")
                if exception:
                    st.warning(f"**Exception:** {exception}")

        # Full Allocation Guide
        full_alloc = hero_sel.get("full_allocation", {})
        if full_alloc:
            st.markdown("### Complete 7-Rally Allocation")
            st.caption(full_alloc.get("description", ""))

            # Critical insight about joining without heroes
            critical = full_alloc.get("critical_insight", {})
            if critical:
                useless_skills = critical.get("useless_skills", [])
                st.markdown(f"""
                <div style="background:rgba(231,76,60,0.2);border:2px solid #E74C3C;padding:16px;border-radius:12px;margin-bottom:16px;">
                    <div style="font-weight:bold;color:#E74C3C;font-size:16px;margin-bottom:8px;">
                        ⚠️ {critical.get('title', 'Important')}
                    </div>
                    <div style="color:#E8F4F8;margin-bottom:12px;">{critical.get('explanation', '')}</div>
                    <div style="background:rgba(46,204,113,0.15);padding:10px;border-radius:6px;margin-bottom:12px;border-left:4px solid #2ECC71;">
                        <span style="font-weight:bold;color:#2ECC71;">Rule:</span>
                        <span style="color:#E8F4F8;">{critical.get('rule', '')}</span>
                    </div>
                    <div style="color:#F39C12;font-size:13px;margin-bottom:8px;">
                        <strong>Useless skills to avoid:</strong> {', '.join(useless_skills)}
                    </div>
                    <div style="color:#888;font-size:12px;font-style:italic;">
                        Example: {critical.get('example', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                lead_rally = full_alloc.get("lead_rally", {})
                st.markdown(f"""
                <div style="background:rgba(74,144,217,0.15);border-left:4px solid #3498DB;padding:16px;border-radius:8px;">
                    <div style="font-weight:bold;color:#3498DB;font-size:16px;margin-bottom:8px;">
                        Lead Rally (All 3 Skills Apply)
                    </div>
                    {"".join([f'<div style="color:#E8F4F8;margin-bottom:4px;">• {h}</div>' for h in lead_rally.get('recommended', [])])}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                example = full_alloc.get("example_allocation", {})
                st.markdown(f"""
                <div style="background:rgba(46,204,113,0.15);border-left:4px solid #2ECC71;padding:16px;border-radius:8px;">
                    <div style="font-weight:bold;color:#2ECC71;font-size:16px;margin-bottom:4px;">
                        Realistic Setup
                    </div>
                    <div style="color:#888;font-size:12px;margin-bottom:8px;">{example.get('description', '')}</div>
                    <div style="color:#F39C12;font-weight:bold;margin-bottom:4px;">Lead: {example.get('lead', '')}</div>
                    <div style="color:#B8D4E8;font-size:13px;">Join 1: {example.get('join_1', '')}</div>
                    <div style="color:#B8D4E8;font-size:13px;">Join 2: {example.get('join_2', '')}</div>
                    <div style="color:#B8D4E8;font-size:13px;">Join 3: {example.get('join_3', '')}</div>
                    <div style="color:#E74C3C;font-size:13px;">Join 4: {example.get('join_4', '')}</div>
                    <div style="color:#E74C3C;font-size:13px;">Join 5: {example.get('join_5', '')}</div>
                    <div style="color:#E74C3C;font-size:13px;">Join 6: {example.get('join_6', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            # Realistic note
            realistic_note = full_alloc.get("realistic_note", "")
            if realistic_note:
                st.caption(realistic_note)

            # Joiner priority table
            join_rallies = full_alloc.get("join_rallies", {})
            priority_order = join_rallies.get("priority_order", [])
            if priority_order:
                st.markdown("#### Joiner Priority (Leftmost Slot)")
                st.caption("Use heroes you have based on your generation. Only top-right expedition skill counts.")

                # Display as compact table
                for hero_data in priority_order:
                    rank = hero_data.get("rank", 0)
                    hero = hero_data.get("hero", "")
                    skill = hero_data.get("skill", "")
                    tier = hero_data.get("tier", "")
                    gen = hero_data.get("gen", 0)

                    # Determine background color
                    if hero == "NO HERO":
                        bg_color = "rgba(231,76,60,0.15)"
                    elif rank != "—" and isinstance(rank, int) and rank <= 3:
                        bg_color = "rgba(155,89,182,0.2)"
                    else:
                        bg_color = "rgba(74,144,217,0.1)"

                    gen_text = f"Gen {gen}" if gen and gen > 0 else ""
                    rank_text = "—" if rank == "—" else f"#{rank}"

                    st.markdown(f"""
                    <div style="background:{bg_color};padding:8px 12px;border-radius:6px;margin-bottom:4px;display:flex;align-items:center;gap:8px;">
                        <span style="font-weight:bold;color:#9B59B6;width:28px;">{rank_text}</span>
                        <span style="font-weight:bold;color:#4A90D9;width:90px;">{hero}</span>
                        <span style="color:#888;font-size:11px;width:45px;">{gen_text}</span>
                        <span style="color:#2ECC71;flex:1;font-size:13px;">{skill}</span>
                        <span style="background:rgba(74,144,217,0.3);padding:2px 6px;border-radius:4px;font-size:11px;">{tier}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Note about generation
                note = join_rallies.get("note", "")
                if note:
                    st.caption(note)

        st.markdown("### Best Joiners (Expedition Skills)")
        best_joiners = hero_sel.get("best_joiners", [])
        for joiner in best_joiners:
            priority = joiner.get("priority", "HIGH")
            priority_color = get_priority_color(priority) if priority != "BEST" else "#9B59B6"
            # Use dark text on orange/yellow backgrounds for readability
            text_color = "#1a1a1a" if priority in ["HIGH", "LOW"] else "white"
            st.markdown(f"""
            <div style="background:rgba(74,144,217,0.1);padding:10px;border-radius:8px;margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:bold;color:#4A90D9;">{joiner.get('hero', '')}</span>
                    <span style="background:{priority_color};color:{text_color};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;">{priority}</span>
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

        # Key math insight
        key_math = quick_ref.get("key_math", "")
        if key_math:
            st.markdown(f"""
            <div style="background:rgba(155,89,182,0.2);border:1px solid #9B59B6;padding:16px;border-radius:8px;margin-bottom:16px;">
                <div style="font-weight:bold;color:#9B59B6;margin-bottom:4px;">💡 Key Insight</div>
                <div style="color:#E8F4F8;">{key_math}</div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Joiner Strategy")
            for item in quick_ref.get("joiner_checklist", []):
                st.markdown(f"• {item}")

        with col2:
            st.markdown("#### Leader Strategy")
            for item in quick_ref.get("leader_checklist", []):
                st.markdown(f"• {item}")

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


def render_canyon_clash():
    """Render canyon clash strategies."""
    canyon_data = BATTLE_STRATEGIES.get("canyon_clash", {})

    st.markdown("### Canyon Clash")
    st.markdown(canyon_data.get("overview", canyon_data.get("description", "")))

    # Display Canyon Clash banner image if available
    banner_path = PROJECT_ROOT / "assets" / "events" / "canyon_clash_banner.png"
    if banner_path.exists():
        with open(banner_path, "rb") as f:
            banner_data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="text-align:center;margin:16px 0;">
            <img src="data:image/png;base64,{banner_data}"
                 style="max-width:100%;max-height:300px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.3);"
                 alt="Canyon Clash Event">
        </div>
        """, unsafe_allow_html=True)

    # Event basics
    basics = canyon_data.get("event_basics", {})
    if basics:
        st.warning(f"**{basics.get('type', 'Alliance PvP')}** - {basics.get('key_resource', 'Fuel management is critical')}")

    # Schedule
    schedule = canyon_data.get("schedule", {})
    if schedule:
        st.markdown("---")
        st.markdown("## Weekly Schedule")
        cols = st.columns(4)
        with cols[0]:
            st.markdown(f"**Mon-Tue**\n\n{schedule.get('monday_tuesday', '')}")
        with cols[1]:
            st.markdown(f"**Wed-Thu**\n\n{schedule.get('wednesday_thursday', '')}")
        with cols[2]:
            st.markdown(f"**Friday**\n\n{schedule.get('friday', '')}")
        with cols[3]:
            st.markdown(f"**Battle Day**\n\n{schedule.get('battle_day', '')}")

    # Phases
    phases = canyon_data.get("phases", [])
    if phases:
        st.markdown("---")
        st.markdown("## Battle Phases")
        for phase in phases:
            phase_num = phase.get("phase", "?")
            phase_name = phase.get("name", "")
            duration = phase.get("duration", "")
            objective = phase.get("objective", "")
            tips = phase.get("tips", [])

            color = ["#3498DB", "#2ECC71", "#F39C12", "#E74C3C"][phase_num - 1] if phase_num <= 4 else "#666"

            with st.expander(f"Phase {phase_num}: {phase_name} ({duration})", expanded=phase_num == 4):
                st.markdown(f"**Objective:** {objective}")
                if tips:
                    st.markdown("**Tips:**")
                    for tip in tips:
                        st.markdown(f"- {tip}")

    # Team Strategy
    team_strat = canyon_data.get("team_strategy", {})
    if team_strat:
        st.markdown("---")
        st.markdown("## Three-Team Strategy")

        three_team = team_strat.get("three_team_split", {})
        if three_team:
            st.info(three_team.get("description", ""))

            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div style="background:rgba(52,152,219,0.15);border-left:4px solid #3498DB;padding:12px;border-radius:8px;">
                    <div style="font-weight:bold;color:#3498DB;margin-bottom:8px;">Team 1</div>
                    <div style="color:#E8F4F8;">{three_team.get('team_1', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div style="background:rgba(46,204,113,0.15);border-left:4px solid #2ECC71;padding:12px;border-radius:8px;">
                    <div style="font-weight:bold;color:#2ECC71;margin-bottom:8px;">Team 2</div>
                    <div style="color:#E8F4F8;">{three_team.get('team_2', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div style="background:rgba(231,76,60,0.15);border-left:4px solid #E74C3C;padding:12px;border-radius:8px;">
                    <div style="font-weight:bold;color:#E74C3C;margin-bottom:8px;">Team 3 (Citadel)</div>
                    <div style="color:#E8F4F8;">{three_team.get('team_3', '')}</div>
                </div>
                """, unsafe_allow_html=True)

    # Fuel Management
    fuel = canyon_data.get("fuel_management", {})
    if fuel:
        st.markdown("---")
        st.markdown("## Fuel Management")
        st.error(f"**{fuel.get('importance', '')}**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Fuel Costs:**")
            for cost in fuel.get("fuel_costs", []):
                st.markdown(f"- {cost}")
        with col2:
            st.markdown(f"**Recovery:** {fuel.get('fuel_recovery', '')}")
            st.markdown(f"**Common Mistake:** {fuel.get('common_mistake', '')}")
            st.success(f"**Tip:** {fuel.get('tip', '')}")

    # Frozen Citadel
    citadel = canyon_data.get("frozen_citadel", {})
    if citadel:
        st.markdown("---")
        st.markdown("## The Frozen Citadel")
        st.warning(f"**{citadel.get('importance', '')}**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Unlock:** {citadel.get('unlock', '')}")
            st.markdown(f"**Capture:** {citadel.get('capture', '')}")
        with col2:
            st.markdown(f"**If You Control:** {citadel.get('if_you_control', '')}")
            st.markdown(f"**If Enemy Controls:** {citadel.get('if_enemy_controls', '')}")

    # Communication
    comm = canyon_data.get("communication", {})
    if comm:
        st.markdown("---")
        st.markdown("## Communication")
        st.info(f"**Voice Chat:** {comm.get('voice_chat', '')}")

        callouts = comm.get("callouts", [])
        if callouts:
            st.markdown("**Key Callouts:** " + " • ".join(callouts))

    # Common Mistakes
    mistakes = canyon_data.get("common_mistakes", [])
    if mistakes:
        st.markdown("---")
        st.markdown("## Common Mistakes")
        for mistake in mistakes:
            st.markdown(f"""
            <div style="background:rgba(231,76,60,0.1);border-left:4px solid #E74C3C;padding:12px;border-radius:8px;margin-bottom:8px;">
                <div style="color:#E74C3C;font-weight:bold;margin-bottom:4px;">Mistake: {mistake.get('mistake', '')}</div>
                <div style="color:#2ECC71;">Fix: {mistake.get('correction', '')}</div>
            </div>
            """, unsafe_allow_html=True)

    # Quick Reference
    quick_ref = canyon_data.get("quick_reference", {})
    if quick_ref:
        st.markdown("---")
        st.markdown("## Quick Reference Checklist")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Before Event")
            for item in quick_ref.get("before_event", []):
                st.markdown(f"- {item}")

        with col2:
            st.markdown("#### During Event")
            for item in quick_ref.get("during_event", []):
                st.markdown(f"- {item}")

        with col3:
            st.markdown("#### Key Tips")
            for tip in quick_ref.get("key_tips", []):
                st.markdown(f"- {tip}")


def render_labyrinth():
    """Render labyrinth strategies."""
    st.markdown("## The Labyrinth")
    st.markdown("Weekly competitive PvP with 6 zones - each tests different parts of your account!")

    st.info("""
    **Key Mechanics:**
    - Most zones provide **Lv.10 troops** (your troop tier doesn't matter)
    - **Gaia Heart** (Sunday) uses YOUR actual troops
    - 5 daily attempts per zone
    """)

    # Zone overview table
    st.markdown("### Zone Summary")
    st.markdown("""
    | Zone | Days | Format | Stats That Matter | Floor 1-9 Ratio | Floor 10 Ratio |
    |------|------|--------|-------------------|-----------------|----------------|
    | **Land of the Brave** | Mon-Tue | 3v3 | Heroes, Hero Gear, Exclusive Gear | 50/20/30 | 40/15/45 |
    | **Cave of Monsters** | Wed-Thu | 2v2 | Pets, Pet Skills | 52/13/35 | 40/15/45 |
    | **Glowstone Mine** | Wed-Thu | 2v2 | Chief Charms (FC25+) | 52/13/35 | 40/15/45 |
    | **Earthlab** | Fri-Sat | 2v2 | Research, War Academy | 52/13/35 | 40/15/45 |
    | **Dark Forge** | Fri-Sat | 2v2 | Chief Gear (FC22+) | 52/13/35 | 40/15/45 |
    | **Gaia Heart** | Sunday | 3v3 | ALL stats + YOUR troops | 50/20/30 | 40/15/45 |
    """)

    st.markdown("""
    **Floor 10 Strategy:** AI switches from 33/33/33 to **53/27/20** (Infantry-heavy) on Floor 10.
    Counter with more Marksmen (40/15/45) to exploit their Infantry focus.
    """)

    # Detailed zone tabs
    with st.expander("📋 Detailed Zone Strategies"):
        zone_tabs = st.tabs(["Land of Brave", "Cave of Monsters", "Glowstone Mine", "Earthlab", "Dark Forge", "Gaia Heart"])

        with zone_tabs[0]:
            st.markdown("**Land of the Brave** (Mon-Tue)")
            st.markdown("Format: 3v3 with up to 9 heroes")
            st.success("Stats: Heroes, Hero Gear, Hero Exclusive Gear")
            st.markdown("Strategy: Focus on exclusive gear upgrades, pick heroes with AoE/CC")

        with zone_tabs[1]:
            st.markdown("**Cave of Monsters** (Wed-Thu)")
            st.markdown("Format: 2v2 squad battles")
            st.success("Stats: Pets, Pet Skills only")
            st.markdown("Strategy: Pair tank heroes with healing pets. Turn order is random.")

        with zone_tabs[2]:
            st.markdown("**Glowstone Mine** (Wed-Thu)")
            st.markdown("Format: 2v2 squad battles | Unlocks: FC25")
            st.success("Stats: Chief Charms only")
            st.markdown("Strategy: Balance offensive and defensive charms")

        with zone_tabs[3]:
            st.markdown("**Earthlab** (Fri-Sat)")
            st.markdown("Format: 2v2 squad battles")
            st.success("Stats: Research Center Tech, War Academy Tech")
            st.markdown("Strategy: Max your tech levels - long-term investment")

        with zone_tabs[4]:
            st.markdown("**Dark Forge** (Fri-Sat)")
            st.markdown("Format: 2v2 squad battles | Unlocks: FC22")
            st.success("Stats: Chief Gear only")
            st.markdown("Strategy: Balance all gear slots, don't neglect any piece")

        with zone_tabs[5]:
            st.markdown("**Gaia Heart** (Sunday)")
            st.markdown("Format: 3v3 with YOUR troops")
            st.warning("This is the ONLY zone where your troop tier matters!")
            st.success("Stats: ALL stats combined")
            st.markdown("Strategy: Use your best Fire Crystal/Helios troops")


def render_battle_strategies():
    """Render the battle strategies page."""
    st.markdown("# Battle Strategies")
    st.markdown("Advanced tactics for competitive events. Coordination and timing beat raw power.")

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Castle Battles",
        "Bear Trap",
        "Canyon Clash",
        "Foundry",
        "Frostfire Mine",
        "Labyrinth"
    ])

    with tab1:
        render_castle_battles()

    with tab2:
        render_bear_trap()

    with tab3:
        render_canyon_clash()

    with tab4:
        render_foundry()

    with tab5:
        render_frostfire()

    with tab6:
        render_labyrinth()

    # Footer
    st.markdown("---")
    st.caption("Battle strategies are most effective with alliance coordination. Practice these tactics before important events!")


# Main
render_battle_strategies()

# Close database session
db.close()
