"""
Combat Optimization - Find your hidden weaknesses and stat gaps.
Why similar-power players crush each other: the hidden multipliers.
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

# Load combat optimization guide
GUIDE_PATH = PROJECT_ROOT / "data" / "guides" / "combat_optimization_audit.json"
if GUIDE_PATH.exists():
    with open(GUIDE_PATH, encoding='utf-8') as f:
        COMBAT_GUIDE = json.load(f)
else:
    COMBAT_GUIDE = {}


def get_impact_color(impact):
    """Get color for impact level."""
    colors = {
        "CRITICAL": "#E74C3C",
        "VERY HIGH": "#E74C3C",
        "HIGH": "#F39C12",
        "MEDIUM-HIGH": "#F1C40F",
        "MEDIUM": "#3498DB",
        "LOW-MEDIUM": "#2ECC71",
        "LOW": "#95A5A6"
    }
    return colors.get(impact.upper(), "#666")


def get_phase_color(phase):
    """Get color for game phase."""
    colors = {
        "early_game": "#2ECC71",
        "mid_game": "#3498DB",
        "late_game": "#9B59B6",
        "endgame": "#E74C3C"
    }
    return colors.get(phase, "#666")


def render_core_insight():
    """Render the core insight section."""
    insight = COMBAT_GUIDE.get("core_insight", {})

    st.markdown(f"### {insight.get('title', 'Why You Lost')}")
    st.markdown(insight.get('explanation', ''))

    st.markdown(f"""
    <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 8px; margin: 12px 0; font-family: monospace;">
        <span style="color: #F1C40F;">Formula:</span> {insight.get('key_formula', '')}
    </div>
    """, unsafe_allow_html=True)

    st.caption(insight.get('implication', ''))


def render_stat_source(source_id, source_data):
    """Render a single stat source card."""
    impact = source_data.get("impact", "MEDIUM")
    impact_color = get_impact_color(impact)
    neglected = source_data.get("often_neglected", False)

    neglected_badge = ""
    if neglected:
        neglected_badge = "<span style='background:#E74C3C;padding:2px 8px;border-radius:4px;font-size:11px;margin-left:8px;'>OFTEN NEGLECTED</span>"

    with st.expander(f"{source_data.get('name', source_id)} - {impact} Impact"):
        # Header
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="background:{impact_color};padding:4px 12px;border-radius:4px;font-size:12px;">
                {impact} IMPACT
            </span>
            <span style="color:#B8D4E8;margin-left:12px;font-size:13px;">
                {source_data.get('category', '').replace('_', ' ').title()}
            </span>
            {neglected_badge}
        </div>
        """, unsafe_allow_html=True)

        # Overview (for Daybreak)
        overview = source_data.get("overview", "")
        if overview:
            st.warning(overview)

        # Stats provided (simple format)
        stats = source_data.get("stats_provided", {})
        if stats:
            st.markdown("**Stats Provided:**")
            cols = st.columns(2)
            stat_items = list(stats.items())
            for i, (stat_name, stat_desc) in enumerate(stat_items[:8]):  # Limit to 8
                with cols[i % 2]:
                    display_name = stat_name.replace("_", " ").title()
                    st.markdown(f"- **{display_name}**: {stat_desc}")

        # Mythic decorations (Daybreak specific)
        mythic_decs = source_data.get("mythic_decorations", {})
        if mythic_decs:
            st.markdown("**Mythic Battle Decorations (+10% at max):**")
            desc = mythic_decs.get("description", "")
            if desc:
                st.caption(desc)
            cols = st.columns(3)
            troop_types = ["infantry", "lancer", "marksman"]
            for col, troop_type in zip(cols, troop_types):
                with col:
                    troop_data = mythic_decs.get(troop_type, {})
                    if troop_data:
                        st.markdown(f"**{troop_type.title()}:**")
                        for deco_name, deco_effect in troop_data.items():
                            st.markdown(f"- {deco_name}: {deco_effect}")

        # Epic decorations (Daybreak specific)
        epic_decs = source_data.get("epic_decorations", {})
        if epic_decs:
            st.markdown("**Epic Decorations (+2.5% at max):**")
            cols = st.columns(3)
            troop_types = ["infantry", "lancer", "marksman"]
            for col, troop_type in zip(cols, troop_types):
                with col:
                    troop_data = epic_decs.get(troop_type, {})
                    if troop_data:
                        st.markdown(f"**{troop_type.title()}:**")
                        for deco_name, deco_effect in troop_data.items():
                            st.markdown(f"- {deco_name}")

        # Tree of Life stats (Daybreak specific)
        tol_stats = source_data.get("tree_of_life_stats", {})
        if tol_stats:
            st.markdown("**Tree of Life (Universal Buffs):**")
            for level, effect in tol_stats.items():
                st.markdown(f"- {level.replace('_', ' ').title()}: {effect}")

        # Max potential (Daybreak specific)
        max_pot = source_data.get("max_potential", {})
        if max_pot:
            st.success(f"**Max Potential:** {max_pot.get('per_troop_type', '')} | With Tree of Life: {max_pot.get('with_tree_of_life', '')}")

        # Priority order
        priority = source_data.get("priority_order", [])
        if priority:
            st.markdown("**Priority Order:**")
            for item in priority:
                st.markdown(f"- {item}")

        # Common mistake
        mistake = source_data.get("common_mistake", "")
        if mistake:
            st.error(f"**Common Mistake:** {mistake}")

        # Quick check
        check = source_data.get("quick_check", "")
        if check:
            st.info(f"**Quick Check:** {check}")


def render_quick_audit():
    """Render the quick audit as informational list."""
    checklist = COMBAT_GUIDE.get("quick_audit_checklist", {})
    milestones = checklist.get("milestones", [])

    st.markdown("### Combat Stat Priorities")
    st.markdown("Key milestones to check at each game phase.")

    # Group by phase
    phases = {"early_game": [], "mid_game": [], "late_game": []}
    for m in milestones:
        phase = m.get("phase", "mid_game")
        if phase in phases:
            phases[phase].append(m)

    phase_labels = {
        "early_game": ("Early Game (F9-19)", "#2ECC71"),
        "mid_game": ("Mid Game (F20-29)", "#3498DB"),
        "late_game": ("Late Game (F30+)", "#9B59B6")
    }

    for phase_id, (phase_label, phase_color) in phase_labels.items():
        phase_milestones = phases.get(phase_id, [])
        if not phase_milestones:
            continue

        with st.expander(f"{phase_label}", expanded=(phase_id == "early_game")):
            # Sort by impact
            impact_order = {"Critical": 0, "Very High": 1, "High": 2, "Medium-High": 3, "Medium": 4}
            sorted_milestones = sorted(phase_milestones, key=lambda x: impact_order.get(x.get("impact", "Medium"), 5))

            for m in sorted_milestones:
                impact = m.get("impact", "Medium")
                impact_color = get_impact_color(impact)
                # Clean up question text and ensure it starts with capital letter
                question = m.get("question", "")
                question = question.replace("Have you ", "").replace("Do you have ", "").replace("Are your ", "").replace("?", "")
                if question:
                    question = question[0].upper() + question[1:]
                why = m.get("why", "")

                st.markdown(f"""
                <div style="background:rgba(74,144,217,0.1);border-left:3px solid {impact_color};padding:8px 12px;margin:6px 0;border-radius:4px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="background:{impact_color};color:#fff;text-shadow:0 1px 2px rgba(0,0,0,0.8), 0 0 4px rgba(0,0,0,0.5);padding:2px 6px;border-radius:3px;font-size:10px;">{impact}</span>
                        <span style="font-weight:bold;color:#E8F4F8;">{question}</span>
                    </div>
                    <div style="font-size:12px;color:#B8D4E8;margin-top:4px;">{why}</div>
                </div>
                """, unsafe_allow_html=True)


def render_blind_spots():
    """Render common blind spots section."""
    blind_spots = COMBAT_GUIDE.get("common_blind_spots", {}).get("blind_spots", [])

    st.markdown("### Common Blind Spots")
    st.markdown("Things most players skip that cost them battles.")

    for spot in blind_spots:
        severity = spot.get("severity", "MEDIUM")
        severity_color = get_impact_color(severity)

        with st.expander(f"{spot.get('name', '')} ({severity})"):
            st.markdown(f"""
            <div style="border-left:4px solid {severity_color};padding-left:12px;">
                <div style="color:#E8F4F8;margin-bottom:8px;">{spot.get('explanation', '')}</div>
                <div style="background:rgba(46,204,113,0.2);padding:8px 12px;border-radius:4px;">
                    <strong style="color:#2ECC71;">Fix:</strong> {spot.get('fix', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_phase_priorities():
    """Render priorities by game phase."""
    phases = COMBAT_GUIDE.get("priority_by_phase", {})

    st.markdown("### What to Focus on By Phase")

    phase_order = ["early_game", "mid_game", "late_game", "endgame"]
    phase_labels = {
        "early_game": "Early Game (F9-19)",
        "mid_game": "Mid Game (F20-29)",
        "late_game": "Late Game (F30+)",
        "endgame": "Endgame (FC5+)"
    }

    tabs = st.tabs([phase_labels.get(p, p) for p in phase_order])

    for tab, phase_id in zip(tabs, phase_order):
        with tab:
            phase_data = phases.get(phase_id, {})
            phase_color = get_phase_color(phase_id)

            st.markdown(f"**Phase:** {phase_data.get('phase', '')}")
            st.markdown(f"**Combat Focus:** {phase_data.get('combat_focus', '')}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Top Priorities:**")
                for p in phase_data.get("top_priorities", []):
                    st.markdown(f"- {p}")

            with col2:
                skip = phase_data.get("skip_for_now", [])
                if skip:
                    st.markdown("**Skip For Now:**")
                    for s in skip:
                        st.markdown(f"- {s}")


def render_stat_stacking_example():
    """Render the stat stacking comparison."""
    example = COMBAT_GUIDE.get("stat_stacking_example", {})

    st.markdown("### How Stats Compound: A Real Example")
    st.markdown(f"*{example.get('scenario', '')}*")

    col1, col2 = st.columns(2)

    player_a = example.get("player_a", {})
    player_b = example.get("player_b", {})

    with col1:
        st.markdown(f"""
        <div style="background:rgba(231,76,60,0.1);border:2px solid #E74C3C;padding:16px;border-radius:8px;">
            <div style="font-size:18px;font-weight:bold;color:#E74C3C;margin-bottom:12px;">
                {player_a.get('label', 'Player A')}
            </div>
            <div style="font-size:13px;color:#B8D4E8;">
                <div>Battle Research Attack: {player_a.get('battle_research_attack', '')}</div>
                <div>Battle Research Lethality: {player_a.get('battle_research_lethality', '')}</div>
                <div>Daybreak Decorations: {player_a.get('daybreak_decorations', player_a.get('daybreak', ''))}</div>
                <div>Chief Gear Set: {player_a.get('chief_gear_set', '')}</div>
                <div>Chief Gear Infantry: {player_a.get('chief_gear_infantry', '')}</div>
                <div>Charms: {player_a.get('charms', '')}</div>
                <div>Pet Buff: {player_a.get('pet_buff', '')}</div>
            </div>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid #E74C3C;">
                <div>Total Attack: <strong>{player_a.get('total_attack_bonus', '')}</strong></div>
                <div>Total Lethality: <strong>{player_a.get('total_lethality_bonus', '')}</strong></div>
                <div style="font-size:16px;color:#E74C3C;margin-top:8px;">
                    Damage Multiplier: <strong>{player_a.get('effective_damage_multiplier', '')}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background:rgba(46,204,113,0.1);border:2px solid #2ECC71;padding:16px;border-radius:8px;">
            <div style="font-size:18px;font-weight:bold;color:#2ECC71;margin-bottom:12px;">
                {player_b.get('label', 'Player B')}
            </div>
            <div style="font-size:13px;color:#B8D4E8;">
                <div>Battle Research Attack: {player_b.get('battle_research_attack', '')}</div>
                <div>Battle Research Lethality: {player_b.get('battle_research_lethality', '')}</div>
                <div>Daybreak Decorations: {player_b.get('daybreak_decorations', player_b.get('daybreak', ''))}</div>
                <div>Chief Gear Set: {player_b.get('chief_gear_set', '')}</div>
                <div>Chief Gear Infantry: {player_b.get('chief_gear_infantry', '')}</div>
                <div>Charms: {player_b.get('charms', '')}</div>
                <div>Pet Buff: {player_b.get('pet_buff', '')}</div>
            </div>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid #2ECC71;">
                <div>Total Attack: <strong>{player_b.get('total_attack_bonus', '')}</strong></div>
                <div>Total Lethality: <strong>{player_b.get('total_lethality_bonus', '')}</strong></div>
                <div style="font-size:16px;color:#2ECC71;margin-top:8px;">
                    Damage Multiplier: <strong>{player_b.get('effective_damage_multiplier', '')}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(241,196,15,0.2);padding:16px;border-radius:8px;margin-top:16px;text-align:center;">
        <div style="font-size:18px;color:#F1C40F;font-weight:bold;">
            {example.get('result', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_combat_optimization():
    """Render the combat optimization page."""
    st.markdown("# Combat Optimization Guide")
    st.markdown("Find your hidden weaknesses. Understand why similar-power players crush each other.")

    # PvE vs PvP explanation
    with st.expander("Understanding PvE vs PvP Combat", expanded=False):
        st.markdown("""
**PvE (Player vs Environment)** - Fighting against the game:
- Bear Trap, Crazy Joe, Labyrinth, Exploration
- Uses **Exploration Skills**
- You can retry for better RNG (especially Bear Trap)

**PvP (Player vs Player)** - Fighting against other players:
- Rally Leader/Joiner, Garrison Defense, SvS, Arena, Brothers in Arms
- Uses **Expedition Skills**
- No retries - optimize your lineup before engaging

**City Attacks (Brothers in Arms, SvS):**
When attacking enemy cities, use your **Rally Leader** lineup with your strongest Expedition heroes. Always attack in a rally - never solo. The combined troop strength greatly increases odds of victory and reduces losses.

**Key Difference:** PvE content often rewards RNG-heavy heroes (like Mia) since you can retry. PvP rewards consistent buffs and debuffs that don't rely on luck.
        """)

    # Core insight
    render_core_insight()

    st.markdown("---")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Quick Audit",
        "All Stat Sources",
        "Blind Spots",
        "Phase Priorities"
    ])

    with tab1:
        render_quick_audit()
        st.markdown("---")
        render_stat_stacking_example()

    with tab2:
        st.markdown("### All Combat Stat Sources")
        st.markdown("Every place your combat stats come from. Expand each to see details.")

        sources = COMBAT_GUIDE.get("stat_sources", {})

        # Sort by impact
        impact_order = {"VERY HIGH": 0, "HIGH": 1, "MEDIUM-HIGH": 2, "MEDIUM": 3, "LOW-MEDIUM": 4, "LOW": 5}
        sorted_sources = sorted(
            sources.items(),
            key=lambda x: impact_order.get(x[1].get("impact", "MEDIUM").upper(), 5)
        )

        for source_id, source_data in sorted_sources:
            render_stat_source(source_id, source_data)

    with tab3:
        render_blind_spots()

    with tab4:
        render_phase_priorities()


# Main
render_combat_optimization()

# Close database session
db.close()
