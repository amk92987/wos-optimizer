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
    with open(EVENTS_PATH) as f:
        EVENTS_GUIDE = json.load(f)
else:
    EVENTS_GUIDE = {"events": {}, "cost_categories": {}, "priority_tiers": {}}


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

    with st.container():
        st.markdown(f"""
        <div style="background: rgba(74, 144, 217, 0.1); border: 1px solid rgba(74, 144, 217, 0.3);
                    border-left: 4px solid {priority_color}; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <span style="font-size: 20px; font-weight: bold; color: #E8F4F8;">{event_data.get('name', event_id)}</span>
                    <span style="background: {priority_color}; padding: 2px 8px; border-radius: 4px; margin-left: 8px; font-size: 12px; color: #000;">
                        {priority} Priority
                    </span>
                </div>
                <div>
                    {f2p_badge}
                </div>
            </div>
            <div style="color: #B8D4E8; font-size: 13px; margin-bottom: 8px;">
                {event_data.get('type', '').title()} Event | {event_data.get('frequency', '')} | {event_data.get('duration', '')}
            </div>
            <div style="color: #E8F4F8; margin-bottom: 12px;">
                {event_data.get('description', '')}
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span style="background: {cost_color}; padding: 4px 10px; border-radius: 4px; font-size: 12px;">
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

                key_heroes = prep.get("key_heroes", [])
                if key_heroes:
                    st.markdown(f"**Key Heroes:** {', '.join(key_heroes)}")

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
                <div style="font-size: 24px; font-weight: bold; color: {color};">{tier}</div>
                <div style="font-size: 12px; color: #B8D4E8;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Resource saving guide
    with st.expander("What to Save & When", expanded=True):
        saving_guide = EVENTS_GUIDE.get("resource_saving_guide", {})

        cols = st.columns(3)
        resources = list(saving_guide.items())

        for i, (resource, data) in enumerate(resources):
            with cols[i % 3]:
                save_for = data.get("save_for", [])
                tip = data.get("tip", "")
                st.markdown(f"""
                <div style="background: rgba(255, 215, 0, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                    <div style="font-weight: bold; color: #FFD700; text-transform: capitalize;">{resource.replace('_', ' ')}</div>
                    <div style="font-size: 12px; color: #B8D4E8;">Save for: {', '.join(save_for)}</div>
                </div>
                """, unsafe_allow_html=True)
                st.caption(tip)

    st.markdown("---")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_priority = st.multiselect(
            "Filter by Priority",
            options=["S", "A", "B", "C", "D"],
            default=["S", "A", "B"]
        )

    with col2:
        filter_type = st.multiselect(
            "Filter by Type",
            options=["solo", "alliance", "competitive"],
            default=["solo", "alliance", "competitive"]
        )

    with col3:
        filter_f2p = st.checkbox("F2P Friendly Only", value=False)

    st.markdown("---")

    # Event list
    events = EVENTS_GUIDE.get("events", {})

    # Sort by priority
    priority_order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}
    sorted_events = sorted(
        events.items(),
        key=lambda x: priority_order.get(x[1].get("priority", "C"), 5)
    )

    displayed = 0
    for event_id, event_data in sorted_events:
        # Apply filters
        if event_data.get("priority", "C") not in filter_priority:
            continue
        if event_data.get("type", "solo") not in filter_type:
            continue
        if filter_f2p and event_data.get("f2p_friendly") is False:
            continue

        render_event_card(event_id, event_data)
        displayed += 1

    if displayed == 0:
        st.info("No events match your filters.")

    st.markdown("---")

    # Cost category legend
    with st.expander("Cost Categories Explained"):
        cost_cats = EVENTS_GUIDE.get("cost_categories", {})
        for cat_id, cat_data in cost_cats.items():
            color = cat_data.get("color", "#666")
            st.markdown(f"""
            <span style="background:{color};padding:4px 10px;border-radius:4px;margin-right:8px;">
                {cat_data.get('label', cat_id)}
            </span>
            {cat_data.get('description', '')}
            """, unsafe_allow_html=True)
            st.markdown("")


# Main
render_events_guide()

# Close database session
db.close()
