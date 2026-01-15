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
    elif server_age_days < 600:
        return 8
    elif server_age_days < 680:
        return 9
    elif server_age_days < 760:
        return 10
    elif server_age_days < 840:
        return 11
    elif server_age_days < 920:
        return 12
    elif server_age_days < 1000:
        return 13
    else:
        return 14


def get_game_phase(furnace_level, fc_level):
    """Determine game phase based on furnace progression."""
    if furnace_level < 19:
        return ("early_game", "Early Game", "Rush to F19 for Daybreak Island")
    elif furnace_level < 30:
        return ("mid_game", "Mid Game", "Rush to F30 for Fire Crystal era")
    elif fc_level and any(fc_level.startswith(f"FC{i}") for i in range(5, 11)):
        return ("endgame", "Endgame", "FC10 completion, max everything")
    else:
        return ("late_game", "Late Game", "FC progression, War Academy, Mastery")


# Page content
st.markdown("# ⚙️ Settings")

# Current profile summary
state_display = f"State {profile.state_number}" if profile.state_number else "State N/A"
fc_display = profile.furnace_fc_level if profile.furnace_fc_level else f"Lv.{profile.furnace_level}"
st.info(f"**{profile.name or 'Chief'}** · {state_display} · {fc_display} · Day {profile.server_age_days}")
st.caption("Edit profile name and state on the **Profiles** page")

st.markdown("---")

# =============================================================================
# SERVER & PROGRESSION
# =============================================================================
st.markdown("## 📅 Server & Progression")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Server Age")

    # Generation options - Gen 1 through Gen 14
    gen_options = [
        ("Gen 1", 1, 20, "Jeronimo, Natalia, Molly, Zinman, Jessie"),
        ("Gen 2", 2, 80, "Flint, Philly, Alonso"),
        ("Gen 3", 3, 160, "Logan, Mia, Greg"),
        ("Gen 4", 4, 240, "Ahmose, Reina, Lynn"),
        ("Gen 5", 5, 320, "Wu Ming, Hector"),
        ("Gen 6", 6, 400, "Norah, Wayne"),
        ("Gen 7", 7, 480, "Gordon, Renee"),
        ("Gen 8", 8, 560, "Edith, Gatot"),
        ("Gen 9", 9, 640, "Henrik, Gwen"),
        ("Gen 10", 10, 720, "Tristan, Ling"),
        ("Gen 11", 11, 800, "Kazuki, Sofia"),
        ("Gen 12", 12, 880, "Bjorn, Yuki"),
        ("Gen 13", 13, 960, "Magnus, Chen"),
        ("Gen 14", 14, 1040, "Latest heroes"),
    ]

    # Find current gen based on server age
    current_gen = get_current_generation(profile.server_age_days)
    current_gen_idx = min(current_gen - 1, len(gen_options) - 1)

    selected_gen = st.selectbox(
        "Newest hero generation on your server",
        options=range(len(gen_options)),
        index=current_gen_idx,
        format_func=lambda i: f"{gen_options[i][0]} ({gen_options[i][3][:30]}...)" if len(gen_options[i][3]) > 30 else f"{gen_options[i][0]} ({gen_options[i][3]})",
        help="Select based on which heroes are available in your state"
    )

    # Calculate estimated days from selection
    estimated_days = gen_options[selected_gen][2]

    # Manual override option
    use_manual = st.checkbox("Enter exact day count", value=False)
    if use_manual:
        server_days = st.number_input(
            "Days since server started",
            min_value=0,
            max_value=2000,
            value=profile.server_age_days,
        )
    else:
        server_days = estimated_days

    # Show current generation info
    gen = get_current_generation(server_days)
    if server_days != profile.server_age_days:
        if st.button("Update Server Age", type="primary"):
            profile.server_age_days = server_days
            db.commit()
            st.toast("Saved")
            st.rerun()

    # Calculate days until next gen
    gen_day_thresholds = [0, 40, 120, 200, 280, 360, 440, 520, 600, 680, 760, 840, 920, 1000, 9999]
    current_gen = get_current_generation(profile.server_age_days)
    if current_gen < 14:
        next_gen_day = gen_day_thresholds[current_gen]  # Threshold for next gen
        days_until_next = next_gen_day - profile.server_age_days
        st.caption(f"Current: **Gen {current_gen}** (Day {profile.server_age_days}) · {days_until_next} days until Gen {current_gen + 1}")
    else:
        st.caption(f"Current: **Gen {current_gen}** (Day {profile.server_age_days}) · Latest generation")

with col2:
    st.markdown("#### Furnace Level")

    # Build furnace level options: (display_label, furnace_level, fc_level_stored)
    furnace_options = []
    for i in range(1, 31):
        furnace_options.append((str(i), i, None))
    # FC sub-levels - store as "FC5-0" format consistently
    for fc in range(1, 11):
        for sub in range(5):
            display = f"FC{fc}" if sub == 0 else f"FC{fc}-{sub}"
            stored = f"FC{fc}-{sub}"
            furnace_options.append((display, 30, stored))

    # Find current index - handle both "FC5" and "FC5-0" formats
    current_furnace_idx = 29  # Default to level 30
    if profile.furnace_level < 30:
        current_furnace_idx = profile.furnace_level - 1
    elif profile.furnace_fc_level:
        fc_to_find = profile.furnace_fc_level
        # Normalize: "FC5" -> "FC5-0"
        if fc_to_find and not "-" in fc_to_find:
            fc_to_find = fc_to_find + "-0"
        for i, (label, lvl, fc) in enumerate(furnace_options):
            if fc == fc_to_find:
                current_furnace_idx = i
                break

    selected_furnace_idx = st.selectbox(
        "Current Furnace Level",
        options=range(len(furnace_options)),
        index=current_furnace_idx,
        format_func=lambda i: furnace_options[i][0],
        help="Your main building level (1-30, then FC progression)"
    )

    selected_furnace = furnace_options[selected_furnace_idx]
    new_furnace_level = selected_furnace[1]
    new_fc_level = selected_furnace[2]

    # Normalize stored FC level for comparison
    current_fc_normalized = profile.furnace_fc_level
    if current_fc_normalized and "-" not in current_fc_normalized:
        current_fc_normalized = current_fc_normalized + "-0"

    # Only save if user actually changed something (not on initial load)
    if new_furnace_level != profile.furnace_level or new_fc_level != current_fc_normalized:
        profile.furnace_level = new_furnace_level
        profile.furnace_fc_level = new_fc_level
        db.commit()
        st.toast("Saved")
        st.rerun()

    # Game phase indicator
    phase_id, phase_name, phase_focus = get_game_phase(profile.furnace_level, profile.furnace_fc_level)
    phase_colors = {
        "early_game": "#4CAF50",
        "mid_game": "#2196F3",
        "late_game": "#FF9800",
        "endgame": "#E91E63"
    }
    st.markdown(f"""
    <div style="background: {phase_colors.get(phase_id, '#808080')}22;
                border-left: 4px solid {phase_colors.get(phase_id, '#808080')};
                padding: 8px 12px; border-radius: 4px; margin-top: 8px;">
        <strong>{phase_name}</strong><br>
        <small style="opacity: 0.8;">{phase_focus}</small>
    </div>
    """, unsafe_allow_html=True)

    # Key milestones
    st.caption("Key unlocks: F18 Pets · F19 Daybreak · F25 Charms · F30 FC")

st.markdown("---")

# =============================================================================
# PLAYSTYLE
# =============================================================================
st.markdown("## 🎮 Playstyle")

col1, col2, col3 = st.columns(3)

with col1:
    spending_options = {
        "f2p": "Free to Play",
        "minnow": "Minnow ($5-30/mo)",
        "dolphin": "Dolphin ($30-100/mo)",
        "orca": "Orca ($100-500/mo)",
        "whale": "Whale ($500+/mo)"
    }
    spending_keys = list(spending_options.keys())
    current_spending_idx = spending_keys.index(profile.spending_profile) if profile.spending_profile in spending_keys else 0

    selected_spending = st.selectbox(
        "💰 Spending",
        spending_keys,
        index=current_spending_idx,
        format_func=lambda x: spending_options[x],
        help="Affects which upgrades are recommended"
    )
    if selected_spending != profile.spending_profile:
        profile.spending_profile = selected_spending
        db.commit()
        st.toast("Saved")

with col2:
    focus_options = {
        "svs_combat": "SvS Combat",
        "balanced_growth": "Balanced Growth",
        "economy_focus": "Economy Focus"
    }
    focus_keys = list(focus_options.keys())
    current_focus_idx = focus_keys.index(profile.priority_focus) if profile.priority_focus in focus_keys else 1

    selected_focus = st.selectbox(
        "🎯 Focus",
        focus_keys,
        index=current_focus_idx,
        format_func=lambda x: focus_options[x],
        help="Determines recommendation priorities"
    )
    if selected_focus != profile.priority_focus:
        profile.priority_focus = selected_focus
        db.commit()
        st.toast("Saved")

with col3:
    role_options = {
        "rally_lead": "Rally Lead",
        "filler": "Rally Filler",
        "farmer": "Farmer",
        "casual": "Casual"
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
    if selected_role != profile.alliance_role:
        profile.alliance_role = selected_role
        db.commit()
        st.toast("Saved")

st.markdown("---")

# =============================================================================
# COMBAT PRIORITIES
# =============================================================================
st.markdown("## ⚔️ Combat Priorities")
st.caption("Higher values = more weight in recommendations")

col1, col2 = st.columns(2)

with col1:
    new_svs = st.slider("SvS / State vs State", 1, 5, profile.priority_svs, key="pri_svs")
    new_rally = st.slider("Rally Attacks", 1, 5, profile.priority_rally, key="pri_rally")
    new_castle = st.slider("Castle Battles", 1, 5, profile.priority_castle_battle, key="pri_castle")

with col2:
    new_exploration = st.slider("Exploration / PvE", 1, 5, profile.priority_exploration, key="pri_explore")
    new_gathering = st.slider("Resource Gathering", 1, 5, profile.priority_gathering, key="pri_gather")

# Auto-save priority changes
if (new_svs != profile.priority_svs or new_rally != profile.priority_rally or
    new_castle != profile.priority_castle_battle or new_exploration != profile.priority_exploration or
    new_gathering != profile.priority_gathering):
    profile.priority_svs = new_svs
    profile.priority_rally = new_rally
    profile.priority_castle_battle = new_castle
    profile.priority_exploration = new_exploration
    profile.priority_gathering = new_gathering
    db.commit()
    st.toast("Saved")

st.markdown("---")

# =============================================================================
# DATA MANAGEMENT (Collapsed)
# =============================================================================
with st.expander("🔧 Reset Options"):
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Reset Priorities to Default", use_container_width=True):
            profile.priority_svs = 5
            profile.priority_rally = 4
            profile.priority_castle_battle = 4
            profile.priority_exploration = 3
            profile.priority_gathering = 2
            profile.spending_profile = "f2p"
            profile.priority_focus = "balanced_growth"
            profile.alliance_role = "filler"
            db.commit()
            st.toast("Priorities reset")
            st.rerun()

    with col2:
        if st.button("⚠️ Clear All Hero Data", type="secondary", use_container_width=True):
            st.session_state.confirm_reset = True

        if st.session_state.get('confirm_reset'):
            st.warning("This will delete all your saved heroes!")
            if st.button("Yes, Clear Everything", type="primary"):
                db.query(UserHero).filter(UserHero.profile_id == profile.id).delete()
                db.query(UserInventory).filter(UserInventory.profile_id == profile.id).delete()
                db.commit()
                st.session_state.confirm_reset = False
                st.success("Data cleared")
                st.rerun()
            if st.button("Cancel"):
                st.session_state.confirm_reset = False
                st.rerun()

# Close database
db.close()
