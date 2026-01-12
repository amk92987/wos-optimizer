"""
Landing Page - Simple Streamlit version for local development.
In production, nginx serves static/landing.html instead.
"""

import streamlit as st


def render_landing():
    """Render a simple landing page for local development."""

    # Clear any stale query params
    stale_params = ['login_submit', 'register_submit', 'error', 'username', 'email', 'password', 'password2', 'page']
    has_stale = any(param in st.query_params for param in stale_params)

    if has_stale:
        st.query_params.clear()
        st.rerun()

    # Styling
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0A1628 0%, #0F2847 50%, #1A4B6E 100%) !important;
    }
    #MainMenu, footer, header, [data-testid="stHeader"],
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    .main .block-container {
        max-width: 800px !important;
        padding-top: 3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Simple content
    st.markdown("""
    <div style="text-align: center; padding: 50px 20px;">
        <h1 style="color: #E0F7FF; font-size: 48px; margin-bottom: 20px;">Bear's Den</h1>
        <p style="color: #93C5E0; font-size: 20px; margin-bottom: 40px;">
            Whiteout Survival Companion
        </p>
        <p style="color: #7DD3FC; font-size: 14px; margin-bottom: 30px;">
            Local Development Mode<br/>
            In production, nginx serves the full landing page.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sign In", key="landing_login", use_container_width=True):
            st.query_params["page"] = "login"
            st.rerun()

        if st.button("Create Account", key="landing_register", use_container_width=True, type="primary"):
            st.query_params["page"] = "register"
            st.rerun()

    st.markdown("""
    <div style="text-align: center; margin-top: 60px; color: #5AADD6; font-size: 12px;">
        <p>© 2025 Random Chaos Labs</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_landing()
