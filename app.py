"""
Bear's Den - Whiteout Survival Companion
A tool to track heroes, analyze screenshots, and get upgrade recommendations.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Bear's Den",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar visible for authenticated users
)

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DEV_AUTO_LOGIN, ENV
from database.db import init_db, get_db, get_or_create_profile, get_user_profiles, set_default_profile
from database.auth import (
    init_session_state, is_authenticated, is_admin, login_user, logout_user,
    authenticate_user, ensure_admin_exists, get_current_username, is_impersonating,
    get_current_user_id, update_user_password, get_user_email, update_user_email
)
from database.models import Feedback

# Initialize database and auth
init_db()
db = get_db()
init_session_state()

# Ensure admin exists before auto-login attempt
ensure_admin_exists(db)

# DEV MODE: Auto-login for local development
# Controlled by ENVIRONMENT and DEV_AUTO_LOGIN env vars (see config.py)
DEV_AUTO_LOGIN_USER = "admin"  # Which user to auto-login as

if DEV_AUTO_LOGIN and not is_authenticated():
    from database.auth import get_user_by_username
    dev_user = get_user_by_username(db, DEV_AUTO_LOGIN_USER)
    if dev_user:
        st.session_state.authenticated = True
        st.session_state.user_id = dev_user.id
        st.session_state.username = dev_user.username
        st.session_state.user_role = dev_user.role

# Load Arctic Night theme CSS
def load_theme_css():
    """Load the Arctic Night theme CSS."""
    if not is_authenticated():
        return

    css_file = PROJECT_ROOT / "styles" / "custom.css"
    if css_file.exists():
        with open(css_file, encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_theme_css()

# Check which page we're on based on query params
current_page = st.query_params.get("page", "home")

# Hide sidebar and Streamlit chrome for unauthenticated users
if not is_authenticated():
    st.markdown("""
    <style>
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Hide the sidebar toggle button */
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Hide the hamburger menu */
    [data-testid="stHeader"] {
        display: none !important;
    }

    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Remove top padding since we're hiding the header */
    .stApp > div:first-child {
        padding-top: 0 !important;
    }

    /* Hide the main menu button */
    #MainMenu {
        display: none !important;
    }

    /* Hide footer */
    footer {
        display: none !important;
    }

    /* Ensure full width for landing page */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Route to appropriate page for non-authenticated users
    if current_page == "login":
        from auth_pages.auth_login import render_login
        render_login()
    elif current_page == "register":
        from auth_pages.auth_register import render_register
        render_register()
    else:
        from auth_pages.landing import render_landing
        render_landing()

    db.close()
    st.stop()

# ============================================
# AUTHENTICATED USER FLOW (has sidebar)
# ============================================

# Show impersonation banner if admin is viewing as another user
if is_impersonating():
    original_admin = st.session_state.get('original_admin_username', 'Admin')
    current_user = get_current_username()

    # Banner with inline switch back button
    banner_cols = st.columns([4, 1])
    with banner_cols[0]:
        st.markdown(f"""
        <div style="background: #E74C3C; color: white; padding: 8px 16px; border-radius: 6px;">
            <strong>Viewing as: {current_user}</strong>
        </div>
        """, unsafe_allow_html=True)
    with banner_cols[1]:
        if st.button("Switch Back", key="switch_back_banner"):
            logout_user()
            st.rerun()

profile = get_or_create_profile(db)

# Ensure assets directory exists
(PROJECT_ROOT / "assets").mkdir(exist_ok=True)
logo_path = PROJECT_ROOT / "assets" / "logo.svg"

# Always regenerate logo - all white text
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
  <!-- Text - all white -->
  <text x="48" y="32" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#E8F4F8">Bear&#39;s Den</text>
  <!-- Snowflake accent -->
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
# Check if admin (not impersonating) to show different navigation
is_admin_view = is_admin() and not is_impersonating()

if is_admin_view:
    # Admin navigation - focused on system management
    admin_home = st.Page("pages/0_Admin_Home.py", title="Dashboard", icon="📊", default=True)
    admin_users = st.Page("pages/15_Admin.py", title="Users", icon="👥")
    admin_announcements = st.Page("pages/1_Admin_Announcements.py", title="Announcements", icon="📢")
    admin_audit = st.Page("pages/2_Admin_Audit_Log.py", title="Audit Log", icon="📜")
    admin_flags = st.Page("pages/3_Admin_Feature_Flags.py", title="Feature Flags", icon="🚩")
    admin_ai = st.Page("pages/10_Admin_AI.py", title="AI Settings", icon="🤖")
    admin_feedback = st.Page("pages/5_Admin_Feedback.py", title="Feedback", icon="📬")
    admin_database = st.Page("pages/4_Admin_Database.py", title="Database", icon="🗄️")
    admin_game_data = st.Page("pages/6_Admin_Game_Data.py", title="Game Data", icon="🎮")
    admin_integrity = st.Page("pages/7_Admin_Data_Integrity.py", title="Data Integrity", icon="🔍")
    admin_reports = st.Page("pages/8_Admin_Usage_Reports.py", title="Usage Reports", icon="📈")
    admin_export = st.Page("pages/9_Admin_Export.py", title="Export", icon="📤")

    pg = st.navigation({
        "Overview": [admin_home, admin_users],
        "Communication": [admin_announcements, admin_feedback],
        "System": [admin_flags, admin_ai, admin_audit, admin_database, admin_integrity],
        "Data": [admin_game_data, admin_reports, admin_export],
    }, expanded=True)

else:
    # Regular user navigation - game focused
    home_page = st.Page("pages/0_Home.py", title="Home", icon="🏠", default=True)
    beginners_page = st.Page("pages/00_Beginner_Guide.py", title="Beginner Guide", icon="🔥")

    # Tracker section - tracking current status
    heroes_page = st.Page("pages/1_Hero_Tracker.py", title="Hero Tracker", icon="🦸")
    chief_page = st.Page("pages/2_Chief_Tracker.py", title="Chief Tracker", icon="👑")

    # Analysis section
    lineups_page = st.Page("pages/5_Lineups.py", title="Lineups", icon="⚔️")
    packs_page = st.Page("pages/8_Packs.py", title="Packs", icon="📦")
    ai_advisor_page = st.Page("pages/6_AI_Advisor.py", title="AI Advisor", icon="🧠")

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

    # Navigation with grouped sections
    pg = st.navigation({
        "": [home_page, beginners_page],
        "Tracker": [heroes_page, chief_page],
        "Analysis": [ai_advisor_page, lineups_page, packs_page],
        "Guides": [items_page, events_page, combat_page, tips_page, tactics_page, daybreak_page],
        "Account": [profiles_page, settings_page],
    }, expanded=True)

# Top-right user menu - styling is in theme CSS files

login_container = st.container()
with login_container:
    # Create columns for top-right positioning
    spacer, login_col = st.columns([6, 1])
    with login_col:
        username = get_current_username()
        # Truncate long usernames for button display (full name shown inside popover)
        display_name = username[:12] + "..." if len(username) > 15 else username
        # Crown for admin, helmet/shield for chief (user)
        if is_admin() and not is_impersonating():
            role_badge = "👑"
            role_title = "Admin"
        else:
            role_badge = "🛡️"  # Shield for Chief
            role_title = "Chief"

        with st.popover(f"{role_badge} {display_name}"):
            # Header with role
            st.markdown(f"""
            <div style="text-align: center; padding-bottom: 8px;">
                <div style="font-size: 24px;">{role_badge}</div>
                <div style="font-size: 16px; font-weight: bold; color: #E8F4F8;">{username}</div>
                <div style="font-size: 11px; color: #8F9DB4;">{role_title}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Donate link - deeper orange for contrast, centered text
            st.markdown("""
            <a href="https://ko-fi.com/randomchaoslabs" target="_blank" style="
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 10px 12px;
                background: linear-gradient(135deg, #D35400, #E67E22);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin-bottom: 8px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            ">
                <span>☕</span>
                <span>Support Bear's Den</span>
            </a>
            """, unsafe_allow_html=True)

            # Feedback section - inline form
            with st.expander("💬 Send Feedback"):
                feedback_type = st.selectbox(
                    "Type",
                    ["Feature Request", "Bug Report", "Data Error", "Other"],
                    key="menu_feedback_type",
                    label_visibility="collapsed"
                )
                feedback_text = st.text_area(
                    "Description",
                    placeholder="What's on your mind?",
                    max_chars=500,
                    key="menu_feedback_text",
                    label_visibility="collapsed",
                    height=80
                )
                st.caption("To report a bad AI recommendation, use the feedback form on the AI Advisor page.")
                if st.button("Submit", key="menu_submit_feedback", use_container_width=True):
                    if feedback_text and len(feedback_text.strip()) >= 10:
                        category_map = {
                            "Feature Request": "feature",
                            "Bug Report": "bug",
                            "Data Error": "data_error",
                            "Other": "other"
                        }
                        try:
                            new_feedback = Feedback(
                                user_id=get_current_user_id(),
                                category=category_map.get(feedback_type, "other"),
                                description=feedback_text.strip()
                            )
                            db.add(new_feedback)
                            db.commit()
                            st.success("Thanks, Chief!")
                        except Exception:
                            st.error("Failed to submit")
                            db.rollback()
                    else:
                        st.warning("Please add more detail")

            st.markdown("---")

            # Password change section
            with st.expander("🔑 Change Password"):
                new_pass = st.text_input("New Password", type="password", key="new_pass_input", label_visibility="collapsed", placeholder="New password")
                confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass_input", label_visibility="collapsed", placeholder="Confirm password")
                if st.button("Update", key="update_pass_btn", use_container_width=True):
                    if not new_pass:
                        st.error("Enter a password")
                    elif len(new_pass) < 6:
                        st.error("Min 6 characters")
                    elif new_pass != confirm_pass:
                        st.error("Passwords don't match")
                    else:
                        user_id = get_current_user_id()
                        if update_user_password(db, user_id, new_pass):
                            st.success("Updated!")
                        else:
                            st.error("Failed")

            # Email change section
            with st.expander("📧 Change Email"):
                current_email = get_user_email(db, get_current_user_id())
                if current_email:
                    st.caption(f"Current: {current_email}")
                else:
                    st.caption("No email set")
                new_email = st.text_input("New Email", key="new_email_input", label_visibility="collapsed", placeholder="new@email.com")
                if st.button("Update", key="update_email_btn", use_container_width=True):
                    user_id = get_current_user_id()
                    success, message = update_user_email(db, user_id, new_email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

            # Profile switcher
            user_profiles = get_user_profiles(db)
            if len(user_profiles) > 1:
                st.markdown("---")
                with st.expander("👤 Switch Profile"):
                    current_profile_id = st.session_state.get('profile_id')
                    for p in user_profiles:
                        is_current = p.id == current_profile_id
                        is_default = p.is_default
                        label = f"{'✓ ' if is_current else ''}{p.name}"
                        if is_default:
                            label += " (default)"

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button(label, key=f"switch_profile_{p.id}", use_container_width=True, disabled=is_current):
                                st.session_state.profile_id = p.id
                                st.rerun()
                        with col2:
                            if not is_default:
                                if st.button("★", key=f"set_default_{p.id}", help="Set as default"):
                                    set_default_profile(db, p.id)
                                    st.rerun()

            st.markdown("---")
            if is_impersonating():
                if st.button("Switch Back", key="logout_btn", use_container_width=True):
                    logout_user()
                    st.rerun()
            else:
                if st.button("Logout", key="logout_btn", use_container_width=True):
                    logout_user()
                    st.rerun()

# Render sidebar content
with st.sidebar:
    # Show different sidebar for admin vs regular users
    if is_admin_view:
        # Admin sidebar - minimal, dashboard has the details
        st.markdown("##### Admin Mode")

        st.markdown("""
        <div style="background: rgba(155, 89, 182, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-size: 12px; color: #9B59B6;">
                👑 Logged in as Administrator
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Regular user sidebar - game priorities
        st.markdown("<h5 style='text-align: center; margin-bottom: 8px;'>Priorities</h5>", unsafe_allow_html=True)

        priorities = [
            ("SvS", profile.priority_svs),
            ("Rally", profile.priority_rally),
            ("Castle", profile.priority_castle_battle),
            ("Explore", profile.priority_exploration),
            ("Gather", profile.priority_gathering),
        ]

        for name, value in priorities:
            col1, col2, col3, col4, col5, col6 = st.columns([1.3, 0.7, 0.7, 0.7, 0.7, 0.7])
            col1.markdown(f"<div style='display: flex; align-items: center; height: 36px;'><small>{name}</small></div>", unsafe_allow_html=True)
            for i, col in enumerate([col2, col3, col4, col5, col6], 1):
                with col:
                    is_filled = i <= value
                    # Use emoji star (yellow) vs outline star (gray) for contrast
                    star = "⭐" if is_filled else "✩"
                    if st.button(star, key=f"s_{name}_{i}"):
                        update_priority(name, i)
                        st.rerun()

    # Branding at bottom of sidebar content
    st.markdown("---")
    st.markdown('''
        <div style="text-align:center; padding: 12px 0;">
            <span style="font-size:20px;">🎲</span>
            <div style="
                font-size:16px;
                font-weight:bold;
                background: linear-gradient(90deg, #FFD700, #FFA500, #FF6B35, #FFD700);
                background-size: 200% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: goldShine 3s linear infinite;
            ">Random Chaos Labs</div>
        </div>
        <style>
            @keyframes goldShine {
                0% { background-position: 0% center; }
                100% { background-position: 200% center; }
            }
        </style>
        ''',
        unsafe_allow_html=True
    )

pg.run()

# Close database
db.close()
