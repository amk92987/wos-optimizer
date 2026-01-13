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
    with open(EVENTS_PATH, encoding='utf-8') as f:
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

                key_heroes = prep.get("key_heroes", [])
                if key_heroes:
                    st.markdown(f"**Key Heroes:** {', '.join(key_heroes)}")

            # Troop ratio if available
            troop_ratio = event_data.get("troop_ratio", {})
            if troop_ratio:
                infantry = troop_ratio.get("infantry", "")
                lancer = troop_ratio.get("lancer", "")
                marksman = troop_ratio.get("marksman", "")
                reasoning = troop_ratio.get("reasoning", "")

                st.markdown("---")
                st.markdown("### Recommended Troop Ratio")
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

    # Event list (no filters - show all)
    events = EVENTS_GUIDE.get("events", {})

    # Sort by priority
    priority_order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}
    sorted_events = sorted(
        events.items(),
        key=lambda x: priority_order.get(x[1].get("priority", "C"), 5)
    )

    for event_id, event_data in sorted_events:
        render_event_card(event_id, event_data)

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
