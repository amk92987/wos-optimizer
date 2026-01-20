"""
Register Page - Native Streamlit components with custom styling.
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

    # Full page styling
    st.markdown("""
    <style>
    /* Full page gradient background */
    .stApp {
        background: linear-gradient(180deg,
            #0A1628 0%,
            #0A1628 20%,
            #0F2847 45%,
            #1A4B6E 70%,
            #2E7DA8 88%,
            #5AADD6 96%,
            #7DD3FC 100%) !important;
        background-attachment: fixed !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header, [data-testid="stHeader"],
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Center content */
    .main .block-container {
        max-width: 400px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Style all text inputs */
    .stTextInput > div > div > input {
        background: rgba(10, 22, 40, 0.6) !important;
        border: 1px solid rgba(125, 211, 252, 0.3) !important;
        border-radius: 8px !important;
        color: #E0F7FF !important;
        padding: 12px 14px !important;
        font-size: 15px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #7DD3FC !important;
        box-shadow: 0 0 10px rgba(125, 211, 252, 0.3) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #5AADD6 !important;
    }

    /* Style labels */
    .stTextInput > label {
        color: #93C5E0 !important;
        font-size: 14px !important;
    }

    /* Style button (both regular and form submit) */
    .stButton > button,
    .stFormSubmitButton > button {
        width: 100% !important;
        padding: 14px !important;
        background: linear-gradient(135deg, #38BDF8, #0EA5E9) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
        cursor: pointer !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.6) !important;
        background: linear-gradient(135deg, #7DD3FC, #38BDF8) !important;
    }

    /* Remove default streamlit element spacing */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Style links */
    a {
        color: #7DD3FC !important;
        text-decoration: none !important;
    }
    a:hover {
        color: #B8EAFF !important;
    }

    /* Error message styling */
    .stAlert {
        background: rgba(220, 38, 38, 0.2) !important;
        border: 1px solid rgba(220, 38, 38, 0.5) !important;
        color: #FCA5A5 !important;
    }

    /* Hide "Press Enter to Apply" hint */
    .stTextInput div[data-testid="InputInstructions"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Back link - goes to static landing page
    st.markdown("""
    <a href="https://wos.randomchaoslabs.com" style="color: #7DD3FC; text-decoration: none; font-size: 14px;">
        ← Back to Home
    </a>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    # Logo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50" style="height: 70px;">
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
            <text x="48" y="32" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#E0F7FF">Bear's Den</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("""
    <h2 style="text-align: center; color: #E0F7FF; margin-bottom: 8px; font-size: 28px;">Create Your Account</h2>
    <p style="text-align: center; color: #93C5E0; margin-bottom: 20px; font-size: 15px;">Join Bear's Den - it's free!</p>
    """, unsafe_allow_html=True)

    # Center the form using columns
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Benefits
        st.markdown("""
        <div style="background: rgba(125, 211, 252, 0.08); border: 1px solid rgba(125, 211, 252, 0.15);
                    border-radius: 10px; padding: 15px 20px; margin-bottom: 25px;">
            <ul style="margin: 0; padding-left: 20px; color: #93C5E0; font-size: 13px; line-height: 1.7;">
                <li>Track your heroes, gear, and progress</li>
                <li>Get AI-powered upgrade recommendations</li>
                <li>Analyze pack values before buying</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Use placeholder so we can clear it on successful registration
        form_container = st.empty()

        with form_container.container():
            # Error message (stored in session state to persist across form submission)
            if st.session_state.get("register_error"):
                st.error(st.session_state["register_error"])
                st.session_state.pop("register_error", None)

            # Form using st.form for reliable submission
            with st.form("register_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                password2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)

                if submitted:
                    error = None
                    if not email or not password:
                        error = "Email and password are required"
                    elif '@' not in email or '.' not in email:
                        error = "Please enter a valid email address"
                    elif len(password) < 6:
                        error = "Password must be at least 6 characters"
                    elif password != password2:
                        error = "Passwords don't match"
                    else:
                        # Clear form and show loading state
                        form_container.empty()
                        with form_container.container():
                            st.markdown("""
                            <div style="text-align: center; padding: 40px;">
                                <p style="color: #93C5E0; font-size: 16px;">Creating your account...</p>
                            </div>
                            """, unsafe_allow_html=True)

                        db = get_db()
                        user = create_user(db, email, password)

                        if user:
                            login_user(user)
                            db.close()
                            st.rerun()
                        else:
                            db.close()
                            error = "Email already registered"

                    if error:
                        st.session_state["register_error"] = error
                        st.rerun()

    # Login link using Streamlit button (prevents page reload flash)
    st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)

    link_col1, link_col2, link_col3 = st.columns([1, 2, 1])
    with link_col2:
        st.markdown("<p style='text-align: center; color: #93C5E0; font-size: 14px; margin: 5px 0;'>Already have an account?</p>", unsafe_allow_html=True)

        if st.button("Sign in", key="login_link", use_container_width=True, type="tertiary"):
            st.query_params["page"] = "login"
            st.rerun()

    # Footer
    st.markdown("""
    <div style="margin-top: 40px; text-align: center;">
        <div style="font-size: 24px;">&#127922;</div>
        <p style="font-size: 11px; color: #5AADD6; margin-top: 5px;">
            <a href="https://www.randomchaoslabs.com">Random Chaos Labs</a>
        </p>
        <div style="margin-top: 15px; padding: 15px; background: rgba(125, 211, 252, 0.08);
                    border: 1px solid rgba(125, 211, 252, 0.15); border-radius: 8px;
                    font-size: 10px; color: #93C5E0; line-height: 1.6;">
            Bear's Den is not affiliated with Century Games or Whiteout Survival.
            All trademarks are property of their respective owners. Use at your own risk.
        </div>
        <p style="margin-top: 15px; font-size: 11px; color: #7DD3FC;">© 2025 Random Chaos Labs</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_register()
