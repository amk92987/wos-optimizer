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
    elif priority_name == "Explore":
        profile.priority_exploration = value
    elif priority_name == "Gather":
        profile.priority_gathering = value
    db.commit()


# Define pages with shorter names
# Home section
home_page = st.Page("pages/0_Home.py", title="Home", icon="🏠", default=True)
beginners_page = st.Page("pages/00_Beginners.py", title="Beginners", icon="📖")

# Tracker section - tracking current status
heroes_page = st.Page("pages/1_Heroes.py", title="Heroes", icon="🦸")
chief_page = st.Page("pages/2_Chief.py", title="Chief", icon="👑")

# Analysis section
upgrades_page = st.Page("pages/4_Upgrades.py", title="Upgrades", icon="📈")
lineups_page = st.Page("pages/5_Lineups.py", title="Lineups", icon="⚔️")
packs_page = st.Page("pages/8_Packs.py", title="Packs", icon="📦")
ai_advisor_page = st.Page("pages/6_Advisor.py", title="Advisor", icon="🤖")

# Guides section
items_page = st.Page("pages/3_Backpack.py", title="Items", icon="🎒")
events_page = st.Page("pages/9_Events.py", title="Events", icon="📅")
combat_page = st.Page("pages/10_Combat.py", title="Combat", icon="⚡")
tips_page = st.Page("pages/11_Tips.py", title="Tips", icon="💡")
tactics_page = st.Page("pages/12_Tactics.py", title="Tactics", icon="🎯")
daybreak_page = st.Page("pages/14_Daybreak.py", title="Daybreak", icon="🏝️")

# Account section
profiles_page = st.Page("pages/7_Profiles.py", title="Profiles", icon="👤")
settings_page = st.Page("pages/13_Settings.py", title="Settings", icon="⚙️")

# Navigation with grouped sections
pg = st.navigation({
    "": [home_page, beginners_page],
    "Tracker": [heroes_page, chief_page],
    "Analysis": [upgrades_page, lineups_page, packs_page, ai_advisor_page],
    "Guides": [items_page, events_page, combat_page, tips_page, tactics_page, daybreak_page],
    "Account": [profiles_page, settings_page],
}, expanded=True)

# Render priorities in sidebar
with st.sidebar:
    st.markdown("##### Priorities")

    priorities = [
        ("SvS", profile.priority_svs),
        ("Rally", profile.priority_rally),
        ("Castle", profile.priority_castle_battle),
        ("Explore", profile.priority_exploration),
        ("Gather", profile.priority_gathering),
    ]

    for name, value in priorities:
        col1, col2, col3, col4, col5, col6 = st.columns([1.2, 0.6, 0.6, 0.6, 0.6, 0.6])
        col1.markdown(f"<small>{name}</small>", unsafe_allow_html=True)
        for i, col in enumerate([col2, col3, col4, col5, col6], 1):
            with col:
                if st.button("★" if i <= value else "☆", key=f"s_{name}_{i}"):
                    update_priority(name, i)
                    st.rerun()

    # Branding at bottom
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;color:#666;font-size:11px;padding:8px 0;">'
        '🎲 <span style="font-weight:bold;">Random Chaos Labs</span>'
        '</div>',
        unsafe_allow_html=True
    )

pg.run()

# Close database
db.close()
