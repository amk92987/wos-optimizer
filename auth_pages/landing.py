"""
Landing Page - Streamlit version shown after logout or for local development.
In production, nginx serves static/landing.html for the initial visit.
"""

import streamlit as st


def render_landing():
    """Render the landing page."""

    # Clear any stale query params
    stale_params = ['login_submit', 'register_submit', 'error', 'username', 'email', 'password', 'password2', 'page']
    has_stale = any(param in st.query_params for param in stale_params)

    if has_stale:
        st.query_params.clear()
        st.rerun()

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
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header, [data-testid="stHeader"],
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Center content */
    .main .block-container {
        max-width: 600px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Style buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        padding: 14px !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo and title
    st.markdown("""
    <div style="text-align: center; padding-top: 40px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50" style="height: 80px;">
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

    # Tagline
    st.markdown("""
    <div style="text-align: center; margin: 20px 0 40px;">
        <p style="color: #93C5E0; font-size: 20px; margin: 0;">
            Your Whiteout Survival Companion
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sign In", key="landing_login", use_container_width=True):
            st.query_params["page"] = "login"
            st.rerun()

        if st.button("Create Free Account", key="landing_register", use_container_width=True, type="primary"):
            st.query_params["page"] = "register"
            st.rerun()

    # Sound Familiar section - 3 boxes across
    st.markdown("""
    <div style="text-align: center; margin: 30px 0 20px;">
        <div style="color: #E0F7FF; font-size: 18px; font-weight: 600;">
            ❄️ Sound Familiar? ❄️
        </div>
    </div>
    """, unsafe_allow_html=True)

    box_style = """
        background: rgba(125, 211, 252, 0.08);
        border: 1px solid rgba(125, 211, 252, 0.15);
        border-radius: 8px;
        padding: 16px 12px;
        text-align: center;
        height: 100%;
    """

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style="{box_style}">
            <div style="font-size: 28px; margin-bottom: 8px;">💰</div>
            <div style="color: #B8D4E8; font-size: 12px;">"I keep spending but I'm not getting any stronger."</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="{box_style}">
            <div style="font-size: 28px; margin-bottom: 8px;">😵</div>
            <div style="color: #B8D4E8; font-size: 12px;">"I have 20 heroes and no idea which to upgrade next."</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style="{box_style}">
            <div style="font-size: 28px; margin-bottom: 8px;">😤</div>
            <div style="color: #B8D4E8; font-size: 12px;">"My rally got destroyed. What lineup should I use?"</div>
        </div>
        """, unsafe_allow_html=True)

    # Features - centered box with centered text
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="margin: 30px 0; padding: 25px 30px;
                    background: rgba(125, 211, 252, 0.08);
                    border: 1px solid rgba(125, 211, 252, 0.15);
                    border-radius: 12px; text-align: center;">
            <div style="color: #E0F7FF; font-size: 16px; font-weight: 600; margin-bottom: 16px;">
                What You Get
            </div>
            <div style="color: #B8D4E8; font-size: 14px; line-height: 2.2;">
                Track your heroes, gear, and progression<br/>
                Get AI-powered upgrade recommendations<br/>
                Build optimal lineups for every event<br/>
                Analyze pack values before buying<br/>
                Access quick tips and strategy guides
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top: 40px; text-align: center;">
        <div style="font-size: 24px;">🎲</div>
        <p style="font-size: 11px; color: #5AADD6; margin-top: 5px;">
            <a href="https://www.randomchaoslabs.com" style="color: #7DD3FC; text-decoration: none;">Random Chaos Labs</a>
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
    render_landing()
