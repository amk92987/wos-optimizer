"""
Whiteout Survival Optimizer
A tool to track heroes, analyze screenshots, and get upgrade recommendations.
"""

import streamlit as st
from pathlib import Path
import sys

# Page config must be first Streamlit command
st.set_page_config(
    page_title="WoS Optimizer",
    page_icon="❄️",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Ensure assets directory exists
(PROJECT_ROOT / "assets").mkdir(exist_ok=True)
logo_path = PROJECT_ROOT / "assets" / "logo.svg"

if not logo_path.exists():
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 50">
  <text x="5" y="35" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#E8F4F8">WoS Optimizer</text>
</svg>'''
    logo_path.write_text(svg_content, encoding='utf-8')

st.logo(image=str(logo_path), size="large", icon_image=str(logo_path))


def update_priority(priority_name: str, value: int):
    """Update a priority value in the database."""
    if priority_name == "SvS":
        profile.priority_svs = value
    elif priority_name == "Rally":
        profile.priority_rally = value
    elif priority_name == "Castle":
        profile.priority_castle_battle = value
    elif priority_name == "PvE":
        profile.priority_exploration = value
    elif priority_name == "Gather":
        profile.priority_gathering = value
    db.commit()


# Render global sidebar with priorities
with st.sidebar:
    st.markdown("**Priorities**")

    priorities = [
        ("SvS", profile.priority_svs),
        ("Rally", profile.priority_rally),
        ("Castle", profile.priority_castle_battle),
        ("PvE", profile.priority_exploration),
        ("Gather", profile.priority_gathering),
    ]

    for name, value in priorities:
        stars = "★" * value + "☆" * (5 - value)
        col1, col2, col3, col4, col5, col6 = st.columns([1.2, 0.6, 0.6, 0.6, 0.6, 0.6])
        col1.markdown(f"<small>{name}</small>", unsafe_allow_html=True)
        for i, col in enumerate([col2, col3, col4, col5, col6], 1):
            with col:
                if st.button("★" if i <= value else "☆", key=f"s_{name}_{i}"):
                    update_priority(name, i)
                    st.rerun()

# Define pages
home_page = st.Page("pages/0_Home.py", title="Home", icon="🏠", default=True)
heroes_page = st.Page("pages/1_Heroes.py", title="Heroes", icon="🦸")
backpack_page = st.Page("pages/2_Backpack.py", title="Backpack", icon="🎒")
recommendations_page = st.Page("pages/3_Recommendations.py", title="Recommendations", icon="📈")
settings_page = st.Page("pages/4_Settings.py", title="Settings", icon="⚙️")
ai_advisor_page = st.Page("pages/5_AI_Advisor.py", title="AI Advisor", icon="🤖")
profiles_page = st.Page("pages/6_Profiles.py", title="Profiles", icon="👤")
lineups_page = st.Page("pages/7_Lineups.py", title="Lineups", icon="⚔️")

pg = st.navigation([home_page, heroes_page, backpack_page, recommendations_page, lineups_page, settings_page, ai_advisor_page, profiles_page])
pg.run()

# Close database
db.close()
