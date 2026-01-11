"""
Home Page - Welcome and overview.
"""

import streamlit as st
from pathlib import Path
import sys

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


def get_current_generation(server_age_days: int) -> int:
    """Calculate current hero generation based on server age."""
    # Gen 1-10 have specific day ranges, Gen 11+ follows 80-day pattern
    gen_thresholds = [
        (40, 1), (120, 2), (200, 3), (280, 4), (360, 5),
        (440, 6), (520, 7), (600, 8), (680, 9), (760, 10),
        (840, 11), (920, 12), (1000, 13), (1080, 14)
    ]
    for threshold, gen in gen_thresholds:
        if server_age_days < threshold:
            return gen
    # Beyond Gen 14, continue 80-day pattern
    return 14 + ((server_age_days - 1080) // 80)


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
        - **Track chief equipment** - Monitor chief gear and charms
        - **Get recommendations** - Know exactly what to upgrade next
        - **Optimize for SvS** - Focus on what matters for combat

        ### Getting Started
        1. Go to **⚙️ Settings** to set your server age and spending profile
        2. Visit **🦸 Heroes** to add your owned heroes and their levels
        3. Visit **👑 Chief** to track your chief gear and charms
        4. Check **📈 Upgrades** for your personalized upgrade path
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

        # Display furnace level properly (including FC levels)
        if profile.furnace_level >= 30 and profile.furnace_fc_level:
            furnace_display = profile.furnace_fc_level
        else:
            furnace_display = str(profile.furnace_level)

        st.markdown(f"""
        <div style="background: rgba(255, 215, 0, 0.2); padding: 20px; border-radius: 12px;">
            <div style="font-size: 14px; color: #B8D4E8;">Furnace Level</div>
            <div style="font-size: 32px; font-weight: bold; color: #FFD700;">{furnace_display}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Generation Timeline
    st.markdown("### 📅 Generation Timeline")
    st.markdown("Know what heroes are coming and when to prepare.")

    gen = get_current_generation(profile.server_age_days)
    timeline_data = [
        ("Gen 1", "0-40", "Jeronimo, Natalia, Jessie, Sergey", gen == 1),
        ("Gen 2", "40-120", "Flint, Philly, Alonso", gen == 2),
        ("Gen 3", "120-200", "Logan, Mia, Greg", gen == 3),
        ("Gen 4", "200-280", "Ahmose, Reina, Lynn", gen == 4),
        ("Gen 5", "280-360", "Hector, Norah, Gwen", gen == 5),
        ("Gen 6", "360-440", "Wu Ming, Renee, Wayne", gen == 6),
        ("Gen 7", "440-520", "Gordon, Edith, Bradley", gen == 7),
        ("Gen 8", "520-600", "Gatot, Hendrik, Sonya", gen == 8),
        ("Gen 9", "600-680", "Magnus, Fred, Xura", gen == 9),
        ("Gen 10", "680-760", "Blanchette, Gregory, Freya", gen == 10),
        ("Gen 11", "760-840", "Eleonora, Lloyd, Rufus", gen == 11),
        ("Gen 12", "840-920", "Hervor, Karol, Ligeia", gen == 12),
        ("Gen 13", "920-1000", "Gisela, Flora, Vulcanus", gen == 13),
        ("Gen 14", "1000+", "Elif, Dominic, Cara", gen >= 14),
    ]

    # Display in rows of 4
    cols = st.columns(4)
    for i, (gen_name, days, heroes, is_current) in enumerate(timeline_data):
        with cols[i % 4]:
            bg_color = "rgba(255, 107, 53, 0.3)" if is_current else "rgba(74, 144, 217, 0.2)"
            border = "2px solid #FF6B35" if is_current else "1px solid rgba(74, 144, 217, 0.3)"
            st.markdown(f"""
            <div style="background: {bg_color}; border: {border}; padding: 16px; border-radius: 8px; margin-bottom: 12px; min-height: 100px;">
                <div style="font-weight: bold; color: #E8F4F8; font-size: 16px;">{gen_name}</div>
                <div style="color: #B8D4E8; font-size: 12px; margin-bottom: 8px;">{days}</div>
                <div style="color: #E8F4F8; font-size: 13px;">{heroes}</div>
            </div>
            """, unsafe_allow_html=True)


# Main
render_home()

# Close database session
db.close()
