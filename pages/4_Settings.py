"""
Settings Page - Configure your profile and priorities.
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero, UserInventory

st.set_page_config(page_title="Settings - WoS Optimizer", page_icon="⚙️", layout="wide")

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)


def get_current_generation(server_age_days: int) -> int:
    """Calculate current hero generation based on server age."""
    if server_age_days < 40:
        return 1
    elif server_age_days < 120:
        return 2
    elif server_age_days < 200:
        return 3
    elif server_age_days < 280:
        return 4
    elif server_age_days < 360:
        return 5
    elif server_age_days < 440:
        return 6
    elif server_age_days < 520:
        return 7
    else:
        return 8 + ((server_age_days - 520) // 80)


def save_profile():
    """Save profile changes to database."""
    db.commit()
    st.success("Settings saved!")


# Page content
st.markdown("# ⚙️ Settings")
st.markdown("Configure your game profile and optimization priorities.")

st.markdown("---")

# Two column layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🏰 Game Profile")

    # Chief name
    profile.name = st.text_input("Chief Name", value=profile.name or "Chief")

    # Server age estimation
    st.markdown("### Server Age")
    st.markdown("*Estimate based on what you see in-game:*")

    estimate_method = st.radio(
        "How do you want to set server age?",
        ["Estimate from milestones", "Enter manually"],
        horizontal=True
    )

    if estimate_method == "Estimate from milestones":
        st.markdown("**Answer these questions:**")

        # Question 1: What heroes are available?
        available_gen = st.selectbox(
            "What's the newest hero generation available on your server?",
            [
                "Gen 1 only (Jeronimo, Natalia, Molly, Zinman)",
                "Gen 2 (Flint, Philly, Alonso)",
                "Gen 3 (Logan, Mia, Greg)",
                "Gen 4 (Ahmose, Reina, Lynn)",
                "Gen 5 (Wu Ming, Hector, Jessie)",
                "Gen 6 (Patrick, Charlie, Cloris)",
                "Gen 7 (Gordon, Renee, Nora)",
                "Gen 8+",
            ],
            index=min(max(0, (profile.server_age_days // 80)), 7)
        )

        # Question 2: SvS history
        svs_status = st.selectbox(
            "Have you had State vs State (SvS) yet?",
            [
                "No SvS yet (server < 84 days)",
                "Had first SvS recently",
                "Had 2-3 SvS events",
                "Had 4+ SvS events",
            ]
        )

        # Calculate estimate
        gen_num = int(available_gen.split()[1]) if "Gen" in available_gen else 8
        gen_base_days = {1: 20, 2: 80, 3: 160, 4: 240, 5: 320, 6: 400, 7: 480, 8: 560}

        svs_adjustment = {
            "No SvS yet (server < 84 days)": -20,
            "Had first SvS recently": 0,
            "Had 2-3 SvS events": 30,
            "Had 4+ SvS events": 60,
        }

        estimated_days = gen_base_days.get(gen_num, 560) + svs_adjustment.get(svs_status, 0)
        estimated_days = max(0, estimated_days)

        st.markdown(f"**Estimated server age: ~{estimated_days} days**")

        if st.button("Use this estimate"):
            profile.server_age_days = estimated_days
            db.commit()
            st.success(f"Set server age to {estimated_days} days")
            st.rerun()

    else:
        profile.server_age_days = st.number_input(
            "Days since server started",
            min_value=0,
            max_value=2000,
            value=profile.server_age_days,
            help="If you know the exact number"
        )

    gen = get_current_generation(profile.server_age_days)
    st.info(f"📅 Current setting: **Generation {gen}** (Day {profile.server_age_days})")

    # Generation timeline preview
    gen_ranges = [
        (1, 0, 40), (2, 40, 120), (3, 120, 200), (4, 200, 280),
        (5, 280, 360), (6, 360, 440), (7, 440, 520), (8, 520, 600)
    ]

    for g, start, end in gen_ranges:
        if g == gen:
            days_in_gen = profile.server_age_days - start
            days_total = end - start
            progress = min(days_in_gen / days_total, 1.0)
            st.progress(progress, text=f"Gen {g}: Day {days_in_gen}/{days_total}")
            if g < 8:
                days_to_next = end - profile.server_age_days
                st.caption(f"⏳ {days_to_next} days until Gen {g+1}")
            break

    st.markdown("---")

    # Furnace level
    st.markdown("### Furnace Level")

    # Build furnace level options: 1-30, then FC1, FC2, FC3, etc.
    furnace_options = [str(i) for i in range(1, 31)] + ["FC1", "FC2", "FC3", "FC4", "FC5"]

    # Convert stored value to display format
    current_furnace = profile.furnace_level
    if current_furnace <= 30:
        current_display = str(current_furnace)
    else:
        current_display = f"FC{current_furnace - 30}"

    # Find index of current value
    try:
        current_index = furnace_options.index(current_display)
    except ValueError:
        current_index = 0

    selected_furnace = st.selectbox(
        "Current Furnace Level",
        furnace_options,
        index=current_index,
        help="Your main building level (1-30, then FC1, FC2, etc.)"
    )

    # Convert selection back to numeric for storage
    if selected_furnace.startswith("FC"):
        profile.furnace_level = 30 + int(selected_furnace[2:])
    else:
        profile.furnace_level = int(selected_furnace)

    # Milestone indicators
    milestones = [
        (15, "Hero Gear unlocks"),
        (16, "SvS eligible"),
        (18, "Pets unlock"),
        (22, "Chief Gear unlocks"),
        (25, "Chief Charms unlock"),
        (30, "Fire Crystal era begins"),
    ]

    st.markdown("#### Furnace Milestones")
    for level, desc in milestones:
        if profile.furnace_level >= level:
            st.markdown(f"✅ **Lv.{level}**: {desc}")
        else:
            st.markdown(f"⬜ **Lv.{level}**: {desc}")

with col2:
    st.markdown("## 🎯 Priorities")
    st.markdown("Set your gameplay focus. Higher = more important for recommendations.")

    # Priority sliders
    st.markdown("### Combat Priorities")

    profile.priority_svs = st.slider(
        "⚔️ SvS / State vs State",
        min_value=1, max_value=5,
        value=profile.priority_svs,
        help="Priority for State of Power events"
    )

    profile.priority_rally = st.slider(
        "🎯 Rally Attacks",
        min_value=1, max_value=5,
        value=profile.priority_rally,
        help="Priority for rally attacks (Bear Hunt, Crazy Joe, etc.)"
    )

    profile.priority_castle_battle = st.slider(
        "🏰 Castle Battles",
        min_value=1, max_value=5,
        value=profile.priority_castle_battle,
        help="Priority for castle siege and defense"
    )

    st.markdown("### Other Priorities")

    profile.priority_exploration = st.slider(
        "🗺️ Exploration / PvE",
        min_value=1, max_value=5,
        value=profile.priority_exploration,
        help="Priority for Frozen Stages, exploration content"
    )

    profile.priority_gathering = st.slider(
        "📦 Resource Gathering",
        min_value=1, max_value=5,
        value=profile.priority_gathering,
        help="Priority for gathering and economy"
    )

    # Priority visualization
    st.markdown("### Priority Distribution")
    priorities = {
        "SvS": profile.priority_svs,
        "Rally": profile.priority_rally,
        "Castle": profile.priority_castle_battle,
        "PvE": profile.priority_exploration,
        "Gather": profile.priority_gathering,
    }

    # Simple bar chart
    for name, value in priorities.items():
        bar = "█" * value + "░" * (5 - value)
        color = "#FF6B35" if value >= 4 else "#4A90D9" if value >= 2 else "#808080"
        st.markdown(f"**{name}**: {bar} ({value}/5)")

st.markdown("---")

# SvS Tracking
st.markdown("## ⚔️ SvS History")

col3, col4, col5 = st.columns(3)

with col3:
    profile.svs_wins = st.number_input(
        "SvS Wins",
        min_value=0,
        value=profile.svs_wins
    )

with col4:
    profile.svs_losses = st.number_input(
        "SvS Losses",
        min_value=0,
        value=profile.svs_losses
    )

with col5:
    total = profile.svs_wins + profile.svs_losses
    if total > 0:
        win_rate = (profile.svs_wins / total) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")
    else:
        st.metric("Win Rate", "N/A")

# Last SvS date
if st.checkbox("Record last SvS date"):
    last_svs = st.date_input("Last SvS Date")
    profile.last_svs_date = datetime.combine(last_svs, datetime.min.time())

st.markdown("---")

# Save button
if st.button("💾 Save All Settings", type="primary", use_container_width=True):
    save_profile()
    st.rerun()

# Data management
st.markdown("---")
st.markdown("## 🗃️ Data Management")

st.info("💡 **Tip:** Use the **Profiles** page to save/load your data across computers!")

st.markdown("### 🔧 Reset Options")

col6, col7 = st.columns(2)

with col6:
    if st.button("🔄 Reset Priorities to Default", use_container_width=True):
        profile.priority_svs = 5
        profile.priority_rally = 4
        profile.priority_castle_battle = 4
        profile.priority_exploration = 3
        profile.priority_gathering = 2
        db.commit()
        st.success("Priorities reset to defaults!")
        st.rerun()

with col7:
    if st.button("⚠️ Reset All Data", type="secondary", use_container_width=True):
        st.warning("This will clear all your saved heroes and inventory!")
        if st.button("Confirm Reset", type="secondary"):
            # Clear user heroes and inventory
            db.query(UserHero).filter(UserHero.profile_id == profile.id).delete()
            db.query(UserInventory).filter(UserInventory.profile_id == profile.id).delete()
            db.commit()
            st.success("All data has been reset.")
            st.rerun()

# Close database
db.close()
