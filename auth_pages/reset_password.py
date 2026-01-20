"""
Reset Password Page - Enter new password using reset token.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db
from database.auth import validate_password_reset_token, reset_password_with_token


def render_reset_password():
    """Render the reset password page."""

    # Get token from query params
    token = st.query_params.get("token", "")

    # Full page styling (same as login)
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

    /* Style button */
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

    /* Hide "Press Enter to Apply" hint */
    .stTextInput div[data-testid="InputInstructions"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px; margin-top: 20px;">
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

    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Check if password was successfully reset
        if st.session_state.get("password_reset_success"):
            st.markdown("""
            <h2 style="text-align: center; color: #E0F7FF; margin-bottom: 8px; font-size: 28px;">Password Reset!</h2>
            """, unsafe_allow_html=True)
            st.success("Your password has been reset successfully.")
            if st.button("Sign In", use_container_width=True):
                st.session_state.pop("password_reset_success", None)
                st.query_params.clear()
                st.query_params["page"] = "login"
                st.rerun()
            return

        # Validate token first
        if not token:
            st.markdown("""
            <h2 style="text-align: center; color: #E0F7FF; margin-bottom: 8px; font-size: 28px;">Invalid Link</h2>
            """, unsafe_allow_html=True)
            st.error("No reset token provided. Please request a new password reset.")
            if st.button("Request New Reset", use_container_width=True):
                st.query_params.clear()
                st.query_params["page"] = "forgot-password"
                st.rerun()
            return

        db = get_db()
        valid, message, user_id = validate_password_reset_token(db, token)
        db.close()

        if not valid:
            st.markdown("""
            <h2 style="text-align: center; color: #E0F7FF; margin-bottom: 8px; font-size: 28px;">Invalid Link</h2>
            """, unsafe_allow_html=True)
            st.error(message)
            if st.button("Request New Reset", use_container_width=True):
                st.query_params.clear()
                st.query_params["page"] = "forgot-password"
                st.rerun()
            return

        # Valid token - show reset form
        st.markdown("""
        <h2 style="text-align: center; color: #E0F7FF; margin-bottom: 8px; font-size: 28px;">Set New Password</h2>
        <p style="text-align: center; color: #93C5E0; margin-bottom: 30px; font-size: 15px;">
            Enter your new password below
        </p>
        """, unsafe_allow_html=True)

        # Form container
        form_container = st.empty()

        with form_container.container():
            # Error message
            if st.session_state.get("reset_error"):
                st.error(st.session_state["reset_error"])
                st.session_state.pop("reset_error", None)

            # Form
            with st.form("reset_password_form"):
                new_password = st.text_input("New Password", type="password", placeholder="Enter new password (min 6 characters)")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
                submitted = st.form_submit_button("Reset Password", use_container_width=True)

                if submitted:
                    if not new_password or not confirm_password:
                        st.warning("Please fill in both password fields")
                    elif new_password != confirm_password:
                        st.session_state["reset_error"] = "Passwords do not match"
                        st.rerun()
                    elif len(new_password) < 6:
                        st.session_state["reset_error"] = "Password must be at least 6 characters"
                        st.rerun()
                    else:
                        # Show loading state
                        form_container.empty()
                        with form_container.container():
                            st.markdown("""
                            <div style="text-align: center; padding: 40px;">
                                <p style="color: #93C5E0; font-size: 16px;">Resetting password...</p>
                            </div>
                            """, unsafe_allow_html=True)

                        db = get_db()
                        success, message = reset_password_with_token(db, token, new_password)
                        db.close()

                        if success:
                            st.session_state["password_reset_success"] = True
                        else:
                            st.session_state["reset_error"] = message

                        st.rerun()

    # Footer
    st.markdown("""
    <div style="margin-top: 50px; text-align: center;">
        <p style="font-size: 11px; color: #5AADD6;">
            <a href="https://www.randomchaoslabs.com">Random Chaos Labs</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_reset_password()
