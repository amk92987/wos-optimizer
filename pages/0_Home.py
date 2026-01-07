"""
Home Page - Welcome and overview.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile

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


def render_home():
    """Render the home page."""
    st.markdown("# Welcome to Whiteout Survival Optimizer")

    # Welcome section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ## Welcome, Chief!

        This tool helps you:
        - **Track your heroes** - Record levels, skills, and gear
        - **Analyze your backpack** - Upload screenshots to track resources
        - **Get recommendations** - Know exactly what to upgrade next
        - **Optimize for SvS** - Focus on what matters for combat

        ### Getting Started
        1. Go to **⚙️ Settings** to set your server age and priorities
        2. Visit **🦸 Heroes** to add your owned heroes
        3. Upload backpack screenshots in **🎒 Backpack**
        4. Check **📈 Recommendations** for your personalized upgrade path
        """)

    with col2:
        st.markdown("### Current Status")

        gen = get_current_generation(profile.server_age_days)

        # Status cards
        st.markdown(f"""
        <div style="background: rgba(74, 144, 217, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 16px;">
            <div style="font-size: 14px; color: #B8D4E8;">Generation</div>
            <div style="font-size: 32px; font-weight: bold; color: #4A90D9;">Gen {gen}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(255, 107, 53, 0.2); padding: 20px; border-radius: 12px; margin-bottom: 16px;">
            <div style="font-size: 14px; color: #B8D4E8;">Server Age</div>
            <div style="font-size: 32px; font-weight: bold; color: #FF6B35;">{profile.server_age_days} days</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(255, 215, 0, 0.2); padding: 20px; border-radius: 12px;">
            <div style="font-size: 14px; color: #B8D4E8;">Furnace Level</div>
            <div style="font-size: 32px; font-weight: bold; color: #FFD700;">{profile.furnace_level}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Generation Timeline
    st.markdown("### 📅 Generation Timeline")
    st.markdown("Know what heroes are coming and when to prepare.")

    gen = get_current_generation(profile.server_age_days)
    timeline_data = [
        ("Gen 1", "0-40 days", "Jeronimo, Natalia, Molly, Zinman", gen == 1),
        ("Gen 2", "40-120 days", "Flint, Philly, Alonso", gen == 2),
        ("Gen 3", "120-200 days", "Logan, Mia, Greg", gen == 3),
        ("Gen 4", "200-280 days", "Ahmose, Reina, Lynn", gen == 4),
        ("Gen 5", "280-360 days", "Hector, Wu Ming, Jessie", gen == 5),
        ("Gen 6", "360-440 days", "Patrick, Charlie, Cloris", gen == 6),
        ("Gen 7", "440-520 days", "Gordon, Renee, Eugene", gen == 7),
        ("Gen 8+", "520+ days", "Blanchette, and more...", gen >= 8),
    ]

    cols = st.columns(4)
    for i, (gen_name, days, heroes, is_current) in enumerate(timeline_data):
        with cols[i % 4]:
            bg_color = "rgba(255, 107, 53, 0.3)" if is_current else "rgba(74, 144, 217, 0.2)"
            border = "2px solid #FF6B35" if is_current else "1px solid rgba(74, 144, 217, 0.3)"
            st.markdown(f"""
            <div style="background: {bg_color}; border: {border}; padding: 16px; border-radius: 8px; margin-bottom: 12px; min-height: 120px;">
                <div style="font-weight: bold; color: #E8F4F8; font-size: 16px;">{gen_name}</div>
                <div style="color: #B8D4E8; font-size: 12px; margin-bottom: 8px;">{days}</div>
                <div style="color: #E8F4F8; font-size: 13px;">{heroes}</div>
                {"<div style='color: #FF6B35; font-size: 11px; margin-top: 8px;'>◆ CURRENT</div>" if is_current else ""}
            </div>
            """, unsafe_allow_html=True)


# Main
render_home()

# Close database session
db.close()
