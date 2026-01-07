"""
Settings Page - Configure your profile and priorities.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero, UserInventory


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

    # Chief name - use key to prevent overwriting on rerender
    chief_name = st.text_input("Chief Name", value=profile.name or "Chief", key="chief_name_input")

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
                "Gen 1 (Jeronimo, Natalia, Molly, Zinman, Jessie, Sergey)",
                "Gen 2 (Flint, Philly, Alonso)",
                "Gen 3 (Logan, Mia, Greg)",
                "Gen 4 (Ahmose, Reina, Lynn)",
                "Gen 5 (Wu Ming, Hector)",
                "Gen 6 (Patrick, Charlie, Cloris)",
                "Gen 7 (Gordon, Renee, Eugene)",
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

    # Build furnace level options: 1-30, then FC levels (each FC has 5 sub-steps: 0-4)
    furnace_options = [str(i) for i in range(1, 31)] + ["30-1", "30-2", "30-3", "30-4"]
    for fc in range(1, 11):
        for sub in range(5):  # 0, 1, 2, 3, 4
            furnace_options.append(f"FC{fc}-{sub}")

    # Determine current display value
    if profile.furnace_level < 30:
        current_display = str(profile.furnace_level)
    elif profile.furnace_fc_level:
        current_display = profile.furnace_fc_level
    else:
        current_display = "30"

    # Find index of current value
    try:
        current_index = furnace_options.index(current_display)
    except ValueError:
        current_index = 0

    selected_furnace = st.selectbox(
        "Current Furnace Level",
        furnace_options,
        index=current_index,
        help="Your main building level (1-30, then FC progression)"
    )

    # Store selection
    if selected_furnace.startswith("FC") or selected_furnace.startswith("30-"):
        profile.furnace_level = 30
        profile.furnace_fc_level = selected_furnace
    else:
        profile.furnace_level = int(selected_furnace)
        profile.furnace_fc_level = None

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

    # Game phase indicator
    st.markdown("---")
    st.markdown("#### Current Game Phase")

    def get_game_phase(furnace_level, fc_level):
        if furnace_level < 19:
            return ("early_game", "Early Game", "Rush to F19 for Daybreak Island, unlock Research")
        elif furnace_level < 30:
            return ("mid_game", "Mid Game", "Rush to F30 for FC, max Tool Enhancement VII")
        elif fc_level and (fc_level.startswith("FC5") or fc_level.startswith("FC6") or
                          fc_level.startswith("FC7") or fc_level.startswith("FC8") or
                          fc_level.startswith("FC9") or fc_level.startswith("FC10")):
            return ("endgame", "Endgame", "FC10 completion, max Mastery, Charms L12-16")
        else:
            return ("late_game", "Late Game (FC Era)", "FC progression, War Academy, Hero Gear Mastery")

    phase_id, phase_name, phase_focus = get_game_phase(profile.furnace_level, profile.furnace_fc_level)

    phase_colors = {
        "early_game": "#4CAF50",
        "mid_game": "#2196F3",
        "late_game": "#FF9800",
        "endgame": "#E91E63"
    }
    phase_color = phase_colors.get(phase_id, "#808080")

    st.markdown(f"""
    <div style="background: {phase_color}22; border-left: 4px solid {phase_color};
                padding: 10px; border-radius: 4px; margin: 10px 0;">
        <strong style="color: {phase_color};">{phase_name}</strong><br>
        <small>{phase_focus}</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("## 🤖 Optimizer Settings")
    st.markdown("Configure how the optimizer makes recommendations for you.")

    # Spending Profile
    spending_options = {
        "f2p": "Free to Play - No spending",
        "minnow": "Minnow - $5-30/month (monthly pass)",
        "dolphin": "Dolphin - $30-100/month (regular packs)",
        "orca": "Orca - $100-500/month (heavy spender)",
        "whale": "Whale - $500+/month (unlimited)"
    }
    spending_keys = list(spending_options.keys())
    current_spending_idx = spending_keys.index(profile.spending_profile) if profile.spending_profile in spending_keys else 0

    selected_spending = st.selectbox(
        "💰 Spending Profile",
        spending_keys,
        index=current_spending_idx,
        format_func=lambda x: spending_options[x],
        help="Affects which upgrades are recommended (F2P skips whale-only content)"
    )
    profile.spending_profile = selected_spending

    # Show efficiency threshold info
    efficiency_thresholds = {"f2p": 0.8, "minnow": 0.7, "dolphin": 0.5, "orca": 0.3, "whale": 0.0}
    threshold = efficiency_thresholds.get(selected_spending, 0.5)
    if threshold > 0:
        st.caption(f"Efficiency threshold: {threshold:.0%} (lower-value upgrades filtered)")
    else:
        st.caption("No efficiency filter (all upgrades shown)")

    # Priority Focus
    focus_options = {
        "svs_combat": "SvS Combat - Maximize troop power and combat stats",
        "balanced_growth": "Balanced Growth - Steady progression across all systems",
        "economy_focus": "Economy Focus - Resource generation and efficiency"
    }
    focus_keys = list(focus_options.keys())
    current_focus_idx = focus_keys.index(profile.priority_focus) if profile.priority_focus in focus_keys else 1

    selected_focus = st.selectbox(
        "🎯 Priority Focus",
        focus_keys,
        index=current_focus_idx,
        format_func=lambda x: focus_options[x],
        help="Determines which systems get priority in recommendations"
    )
    profile.priority_focus = selected_focus

    # Alliance Role
    role_options = {
        "rally_lead": "Rally Lead - Leads rallies in SvS and events",
        "filler": "Filler - Joins rallies and reinforces",
        "farmer": "Farmer - Resource generation focus",
        "casual": "Casual - Plays for fun, no specific role"
    }
    role_keys = list(role_options.keys())
    current_role_idx = role_keys.index(profile.alliance_role) if profile.alliance_role in role_keys else 1

    selected_role = st.selectbox(
        "👥 Alliance Role",
        role_keys,
        index=current_role_idx,
        format_func=lambda x: role_options[x],
        help="Rally leads get troop priority boosts"
    )
    profile.alliance_role = selected_role

    st.markdown("---")

    st.markdown("## 🎯 Detailed Priorities")
    st.markdown("Fine-tune your gameplay focus. Higher = more important for recommendations.")

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

# Save button
if st.button("💾 Save All Settings", type="primary", use_container_width=True):
    # Save chief name from the input
    profile.name = chief_name
    db.commit()
    st.success("Settings saved!")

    # Lightning strike effect - forking from top-left to bottom-right
    st.markdown("""
    <style>
    @keyframes lightning-flash {
        0% { opacity: 0; }
        5% { opacity: 1; }
        10% { opacity: 0.3; }
        15% { opacity: 1; }
        20% { opacity: 0; }
        25% { opacity: 0.7; }
        30% { opacity: 0; }
        100% { opacity: 0; }
    }
    @keyframes bolt-draw {
        0% { stroke-dashoffset: 2000; opacity: 0; }
        10% { opacity: 1; }
        50% { stroke-dashoffset: 0; opacity: 1; }
        70% { stroke-dashoffset: 0; opacity: 0.6; }
        100% { stroke-dashoffset: 0; opacity: 0; }
    }
    @keyframes glow-pulse {
        0% { filter: drop-shadow(0 0 5px #4A90D9); }
        50% { filter: drop-shadow(0 0 30px #E8F4F8) drop-shadow(0 0 60px #4A90D9); }
        100% { filter: drop-shadow(0 0 5px #4A90D9); }
    }
    .lightning-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 9999;
        overflow: hidden;
    }
    .lightning-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(ellipse at 20% 10%, rgba(74, 144, 217, 0.5) 0%, transparent 50%),
                    radial-gradient(ellipse at 60% 40%, rgba(232, 244, 248, 0.3) 0%, transparent 40%);
        animation: lightning-flash 0.8s ease-out forwards;
    }
    .lightning-svg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    .lightning-svg path {
        fill: none;
        stroke: url(#lightning-gradient);
        stroke-width: 3;
        stroke-linecap: round;
        stroke-dasharray: 2000;
        stroke-dashoffset: 2000;
        animation: bolt-draw 0.9s ease-out forwards, glow-pulse 0.3s ease-in-out 3;
    }
    .lightning-svg .main-bolt { stroke-width: 4; animation-delay: 0s; }
    .lightning-svg .fork-1 { stroke-width: 3; animation-delay: 0.05s; }
    .lightning-svg .fork-2 { stroke-width: 2.5; animation-delay: 0.1s; }
    .lightning-svg .fork-3 { stroke-width: 2; animation-delay: 0.08s; }
    .lightning-svg .fork-4 { stroke-width: 2; animation-delay: 0.12s; }
    .lightning-svg .fork-5 { stroke-width: 1.5; animation-delay: 0.15s; }
    </style>
    <div class="lightning-container">
        <div class="lightning-overlay"></div>
        <svg class="lightning-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
                <linearGradient id="lightning-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#E8F4F8;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#4A90D9;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#E8F4F8;stop-opacity:1" />
                </linearGradient>
            </defs>
            <!-- Main bolt: top-left to bottom-right with jagged path -->
            <path class="main-bolt" d="M5,2 L12,15 L8,16 L18,32 L14,33 L28,52 L22,53 L38,72 L32,73 L50,95" />
            <!-- Fork 1: branches right-up from 20% -->
            <path class="fork-1" d="M12,15 L22,12 L28,22 L38,18" />
            <!-- Fork 2: branches right from 35% -->
            <path class="fork-2" d="M18,32 L32,28 L38,38 L52,35 L58,45" />
            <!-- Fork 3: branches down-right from 50% -->
            <path class="fork-3" d="M28,52 L45,48 L52,58 L68,55 L75,68" />
            <!-- Fork 4: small branch -->
            <path class="fork-4" d="M38,72 L55,68 L62,78 L78,75" />
            <!-- Fork 5: thin tendril -->
            <path class="fork-5" d="M22,53 L35,58 L42,52" />
        </svg>
    </div>
    """, unsafe_allow_html=True)

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
        profile.spending_profile = "f2p"
        profile.priority_focus = "balanced_growth"
        profile.alliance_role = "filler"
        db.commit()
        st.success("Priorities and optimizer settings reset to defaults!")
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
