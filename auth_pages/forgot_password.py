"""
Forgot Password Page - Request password reset email.
"""

import streamlit as st
from pathlib import Path
import sys
import os

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db
from database.auth import create_password_reset_token
from utils.email import send_password_reset_email


def get_base_url():
    """Get the base URL for the current environment."""
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'production':
        return "https://www.randomchaoslabs.com"
    elif env == 'sandbox':
        return "https://dev.randomchaoslabs.com"
    else:
        return "http://localhost:8501"


def render_forgot_password():
    """Render the forgot password page."""

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

    /* Success/Error message styling */
    .stAlert[data-baseweb="notification"] {
        border-radius: 8px !important;
    }

    /* Hide "Press Enter to Apply" hint */
    .stTextInput div[data-testid="InputInstructions"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Style tertiary buttons as plain text links
    st.markdown("""
    <style>
    button[kind="tertiary"] {
        background: none !important;
        border: none !important;
        color: #7DD3FC !important;
        font-size: 14px !important;
        font-weight: normal !important;
        box-shadow: none !important;
        padding: 5px 0 !important;
    }
    button[kind="tertiary"]:hover {
        color: #B8EAFF !important;
        text-decoration: underline !important;
        background: none !important;
    }
    button[kind="tertiary"]:focus {
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Back link
    if st.button("← Back to Login", key="back_to_login", type="tertiary"):
        st.query_params["page"] = "login"
        st.rerun()

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
    <h2 style="text-align: center; color: #E0F7FF; margin-bottom: 8px; font-size: 28px;">Reset Password</h2>
    <p style="text-align: center; color: #93C5E0; margin-bottom: 30px; font-size: 15px;">
        Enter your email and we'll send you a reset link
    </p>
    """, unsafe_allow_html=True)

    # Center the form using columns
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Check if we already sent an email (success state)
        if st.session_state.get("reset_email_sent"):
            st.success("Check your email for the reset link. It may take a few minutes to arrive.")
            st.markdown("""
            <div style="text-align: center; margin-top: 20px; color: #93C5E0; font-size: 14px;">
                Didn't receive it? Check your spam folder or <a href="?page=forgot-password">try again</a>
            </div>
            """, unsafe_allow_html=True)
            # Clear the flag after showing
            if st.button("Back to Login", use_container_width=True):
                st.session_state.pop("reset_email_sent", None)
                st.query_params["page"] = "login"
                st.rerun()
            return

        # Form container
        form_container = st.empty()

        with form_container.container():
            # Error message
            if st.session_state.get("forgot_error"):
                st.error(st.session_state["forgot_error"])
                st.session_state.pop("forgot_error", None)

            # Form
            with st.form("forgot_password_form"):
                email = st.text_input("Email", placeholder="Enter your email address")
                submitted = st.form_submit_button("Send Reset Link", use_container_width=True)

                if submitted:
                    if email:
                        # Show loading state
                        form_container.empty()
                        with form_container.container():
                            st.markdown("""
                            <div style="text-align: center; padding: 40px;">
                                <p style="color: #93C5E0; font-size: 16px;">Sending reset link...</p>
                            </div>
                            """, unsafe_allow_html=True)

                        db = get_db()
                        success, message, token = create_password_reset_token(db, email)

                        if success and token:
                            # Send email
                            base_url = get_base_url()
                            email_success, email_msg = send_password_reset_email(email, token, base_url)

                            if email_success:
                                st.session_state["reset_email_sent"] = True
                            else:
                                st.session_state["forgot_error"] = f"Failed to send email. Please try again."

                        db.close()
                        st.rerun()
                    else:
                        st.warning("Please enter your email address")

    # Login link (using button to prevent page reload flash)
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Remember your password? Sign in", key="login_link", type="tertiary", use_container_width=True):
            st.query_params["page"] = "login"
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
    render_forgot_password()
