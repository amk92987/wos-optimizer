"""
Register Page - Standalone decorated registration page.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db
from database.auth import create_user, login_user


def render_register():
    """Render the registration page."""
    db = get_db()

    # Logo SVG
    logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50" style="height: 50px;">
      <defs>
        <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#7DD3FC"/>
          <stop offset="100%" style="stop-color:#E0F7FF"/>
        </linearGradient>
      </defs>
      <circle cx="22" cy="20" r="8" fill="url(#logoGrad)"/>
      <circle cx="12" cy="10" r="4" fill="url(#logoGrad)"/>
      <circle cx="22" cy="6" r="4" fill="url(#logoGrad)"/>
      <circle cx="32" cy="10" r="4" fill="url(#logoGrad)"/>
      <text x="48" y="32" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#E0F7FF">Bear\'s Den</text>
    </svg>'''

    # Page styling - glacier theme
    st.markdown("""
    <style>
    /* Glacier background */
    .stApp {
        background: linear-gradient(180deg,
            #0A1628 0%,
            #0F2847 30%,
            #1A4B6E 60%,
            #2E7DA8 100%) !important;
        background-attachment: fixed !important;
    }

    /* Center the register form */
    .register-container {
        max-width: 420px;
        margin: 0 auto;
        padding: 40px;
    }

    /* Card styling */
    .auth-card {
        background: linear-gradient(180deg, rgba(15, 40, 71, 0.95) 0%, rgba(26, 75, 110, 0.9) 100%);
        border: 1px solid rgba(125, 211, 252, 0.3);
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4), 0 0 60px rgba(125, 211, 252, 0.1);
    }

    /* Logo centering */
    .logo-center {
        text-align: center;
        margin-bottom: 30px;
    }

    /* Back link */
    .back-link {
        color: #7DD3FC;
        text-decoration: none;
        font-size: 14px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 30px;
    }

    .back-link:hover {
        color: #B8EAFF;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(10, 22, 40, 0.8) !important;
        border: 1px solid rgba(125, 211, 252, 0.3) !important;
        color: #E0F7FF !important;
        border-radius: 8px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #7DD3FC !important;
        box-shadow: 0 0 15px rgba(125, 211, 252, 0.3) !important;
    }

    /* Primary button glow */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 100%) !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.6) !important;
    }

    /* Login link styling */
    .login-link {
        text-align: center;
        margin-top: 24px;
        color: #93C5E0;
        font-size: 14px;
    }

    .login-link a {
        color: #7DD3FC;
        text-decoration: none;
        font-weight: 600;
    }

    .login-link a:hover {
        color: #B8EAFF;
        text-decoration: underline;
    }

    /* Benefits list */
    .benefits-list {
        background: rgba(125, 211, 252, 0.08);
        border: 1px solid rgba(125, 211, 252, 0.15);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
    }

    .benefits-list ul {
        margin: 0;
        padding-left: 20px;
        color: #93C5E0;
        font-size: 14px;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

    # Back to home link
    st.markdown("""
    <a href="/" class="back-link">
        <span>&#8592;</span> Back to Home
    </a>
    """, unsafe_allow_html=True)

    # Register card
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    # Logo
    st.markdown(f'<div class="logo-center">{logo_svg}</div>', unsafe_allow_html=True)

    st.markdown("""
    <h2 style="text-align: center; color: #E0F7FF; margin-bottom: 8px; font-size: 28px;">Create Your Account</h2>
    <p style="text-align: center; color: #93C5E0; margin-bottom: 24px; font-size: 15px;">Join Bear's Den - it's free!</p>
    """, unsafe_allow_html=True)

    # Benefits
    st.markdown("""
    <div class="benefits-list">
        <ul>
            <li>Track your heroes, gear, and progress</li>
            <li>Get AI-powered upgrade recommendations</li>
            <li>Analyze pack values before buying</li>
            <li>Access optimal lineup guides</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Register form
    reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username (min 3 characters)")
    reg_email = st.text_input("Email (optional)", key="reg_email", placeholder="For account recovery")
    reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min 6 characters")
    reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2", placeholder="Re-enter password")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if st.button("Create Account", type="primary", use_container_width=True, key="register_btn"):
        if not reg_username or not reg_password:
            st.warning("Username and password are required")
        elif len(reg_username) < 3:
            st.warning("Username must be at least 3 characters")
        elif len(reg_password) < 6:
            st.warning("Password must be at least 6 characters")
        elif reg_password != reg_password2:
            st.error("Passwords don't match")
        else:
            email = reg_email if reg_email else None
            user = create_user(db, reg_username, reg_password, email=email)
            if user:
                login_user(user)
                st.success("Account created! Redirecting...")
                # Clear query params and reload to show the app
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Username or email already exists")

    # Login link
    st.markdown("""
    <div class="login-link">
        Already have an account? <a href="?page=login">Sign in</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #4A7A98; padding: 40px 20px; font-size: 12px; margin-top: 60px;">
        <p>Built by Random Chaos Labs</p>
    </div>
    """, unsafe_allow_html=True)

    db.close()


# Run if called directly
if __name__ == "__main__":
    render_register()
