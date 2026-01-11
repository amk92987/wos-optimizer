"""
Bear's Den - Whiteout Survival Companion
A tool to track heroes, analyze screenshots, and get upgrade recommendations.
"""

import streamlit as st
from pathlib import Path
import sys

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Bear's Den",
    page_icon="❄️",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.auth import (
    init_session_state, is_authenticated, is_admin, login_user, logout_user,
    authenticate_user, ensure_admin_exists, get_current_username
)

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database and auth
init_db()
db = get_db()
init_session_state()

# Ensure at least one admin exists (default: admin/admin123)
if ensure_admin_exists(db):
    st.toast("Default admin created: admin / admin123", icon="🔐")

profile = get_or_create_profile(db)

# Ensure assets directory exists
(PROJECT_ROOT / "assets").mkdir(exist_ok=True)
logo_path = PROJECT_ROOT / "assets" / "logo.svg"

# Always regenerate logo with current name
svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50">
  <defs>
    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4A90D9"/>
      <stop offset="100%" style="stop-color:#E8F4F8"/>
    </linearGradient>
  </defs>
  <!-- Bear paw icon -->
  <circle cx="22" cy="20" r="8" fill="url(#logoGrad)"/>
  <circle cx="12" cy="10" r="4" fill="url(#logoGrad)"/>
  <circle cx="22" cy="6" r="4" fill="url(#logoGrad)"/>
  <circle cx="32" cy="10" r="4" fill="url(#logoGrad)"/>
  <!-- Text -->
  <text x="48" y="32" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#E8F4F8">Bear&#39;s Den</text>
  <!-- Snowflake accent (SVG path) -->
  <g transform="translate(178, 18)" fill="#4A90D9">
    <line x1="0" y1="-8" x2="0" y2="8" stroke="#4A90D9" stroke-width="2"/>
    <line x1="-7" y1="-4" x2="7" y2="4" stroke="#4A90D9" stroke-width="2"/>
    <line x1="-7" y1="4" x2="7" y2="-4" stroke="#4A90D9" stroke-width="2"/>
  </g>
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


# Define pages with full names as requested
# Home section
home_page = st.Page("pages/0_Home.py", title="Home", icon="🏠", default=True)
beginners_page = st.Page("pages/00_Beginner_Guide.py", title="Beginner Guide", icon="📖")

# Tracker section - tracking current status
heroes_page = st.Page("pages/1_Hero_Tracker.py", title="Hero Tracker", icon="🦸")
chief_page = st.Page("pages/2_Chief_Tracker.py", title="Chief Tracker", icon="👑")

# Analysis section
lineups_page = st.Page("pages/5_Lineups.py", title="Lineups", icon="⚔️")
packs_page = st.Page("pages/8_Packs.py", title="Packs", icon="📦")
ai_advisor_page = st.Page("pages/6_AI_Advisor.py", title="AI Advisor", icon="🤖")

# Guides section
items_page = st.Page("pages/3_Backpack.py", title="Backpack", icon="🎒")
events_page = st.Page("pages/9_Events.py", title="Events", icon="📅")
combat_page = st.Page("pages/10_Combat.py", title="Combat", icon="⚡")
tips_page = st.Page("pages/11_Quick_Tips.py", title="Quick Tips", icon="💡")
tactics_page = st.Page("pages/12_Battle_Tactics.py", title="Battle Tactics", icon="🎯")
daybreak_page = st.Page("pages/14_Daybreak_Island.py", title="Daybreak Island", icon="🏝️")

# Account section
profiles_page = st.Page("pages/7_Save_Load.py", title="Save/Load", icon="👤")
settings_page = st.Page("pages/13_Settings.py", title="Settings", icon="⚙️")
admin_page = st.Page("pages/15_Admin.py", title="Admin", icon="🔐")

# Build navigation - Admin page only visible to admins
account_pages = [profiles_page, settings_page]
if is_admin():
    account_pages.append(admin_page)

# Navigation with grouped sections
pg = st.navigation({
    "": [home_page, beginners_page],
    "Tracker": [heroes_page, chief_page],
    "Analysis": [ai_advisor_page, lineups_page, packs_page],
    "Guides": [items_page, events_page, combat_page, tips_page, tactics_page, daybreak_page],
    "Account": account_pages,
}, expanded=True)

# Top-right login/logout using popover
login_container = st.container()
with login_container:
    # Create columns for top-right positioning
    spacer, login_col = st.columns([6, 1])
    with login_col:
        if is_authenticated():
            username = get_current_username()
            role_badge = "👑" if is_admin() else "👤"
            with st.popover(f"{role_badge} {username}"):
                st.caption(f"Logged in as **{username}**")
                if st.button("Logout", key="logout_btn", use_container_width=True):
                    logout_user()
                    st.rerun()
        else:
            with st.popover("🔐 Login"):
                login_username = st.text_input("Username", key="login_user")
                login_password = st.text_input("Password", type="password", key="login_pass")
                if st.button("Login", key="login_btn", use_container_width=True):
                    user = authenticate_user(db, login_username, login_password)
                    if user:
                        login_user(user)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

# Render sidebar content
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
