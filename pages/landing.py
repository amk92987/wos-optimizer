"""
Landing Page - Marketing page for non-authenticated users.
Pure marketing - no app functionality shown.
"""

import streamlit as st
from pathlib import Path


def render_landing():
    """Render the landing page."""
    PROJECT_ROOT = Path(__file__).parent.parent

    # Get the logo SVG content
    logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50" style="height: 40px;">
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

    # Antarctic glacier theme styles
    st.markdown("""
    <style>
    /* Antarctic glacier background - dark above, light glacial blue below */
    .stApp {
        background: linear-gradient(180deg,
            #0A1628 0%,
            #0F2847 15%,
            #1A4B6E 35%,
            #2E7DA8 55%,
            #5AADD6 75%,
            #7DD3FC 90%,
            #B8EAFF 100%) !important;
        background-attachment: fixed !important;
    }

    /* Glowing button styles */
    .glow-btn {
        padding: 12px 28px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 15px;
        text-decoration: none;
        display: inline-block;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
    }

    .glow-btn-signin {
        background: rgba(125, 211, 252, 0.15);
        color: #B8EAFF;
        border: 2px solid rgba(125, 211, 252, 0.5);
        box-shadow: 0 0 15px rgba(125, 211, 252, 0.3), inset 0 0 20px rgba(125, 211, 252, 0.1);
    }

    .glow-btn-signin:hover {
        box-shadow: 0 0 25px rgba(125, 211, 252, 0.6), 0 0 40px rgba(125, 211, 252, 0.3), inset 0 0 25px rgba(125, 211, 252, 0.2);
        border-color: #B8EAFF;
        color: #FFFFFF;
        background: rgba(125, 211, 252, 0.25);
    }

    .glow-btn-register {
        background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 100%);
        color: white;
        border: none;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.5), 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .glow-btn-register:hover {
        box-shadow: 0 0 35px rgba(56, 189, 248, 0.7), 0 0 50px rgba(125, 211, 252, 0.4), 0 6px 20px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
        background: linear-gradient(135deg, #7DD3FC 0%, #38BDF8 100%);
    }

    /* Landing header - deep glacier */
    .landing-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 40px;
        background: linear-gradient(180deg, rgba(10, 22, 40, 0.98) 0%, rgba(15, 40, 71, 0.95) 100%);
        border-bottom: 1px solid rgba(125, 211, 252, 0.2);
        position: sticky;
        top: 0;
        z-index: 1000;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    }

    .header-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .header-buttons {
        display: flex;
        gap: 16px;
        align-items: center;
    }

    /* Glacier ice card styling */
    .ice-card {
        background: linear-gradient(180deg, rgba(15, 40, 71, 0.85) 0%, rgba(26, 75, 110, 0.9) 50%, rgba(46, 125, 168, 0.85) 100%);
        border: 1px solid rgba(125, 211, 252, 0.25);
        border-radius: 16px;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(184, 234, 255, 0.1),
            0 0 60px rgba(125, 211, 252, 0.08);
        backdrop-filter: blur(10px);
    }

    /* Deep water card - for contrast */
    .deep-card {
        background: linear-gradient(180deg, rgba(10, 22, 40, 0.95) 0%, rgba(15, 40, 71, 0.9) 100%);
        border: 1px solid rgba(125, 211, 252, 0.15);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    /* Snowflake decorations */
    .snowflake {
        color: rgba(184, 234, 255, 0.5);
        font-size: 24px;
        animation: drift 8s ease-in-out infinite;
    }

    @keyframes drift {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.5; }
        50% { transform: translateY(-10px) rotate(180deg); opacity: 0.8; }
    }

    /* Glacial ice text glow */
    .ice-glow {
        color: #7DD3FC;
        text-shadow: 0 0 30px rgba(125, 211, 252, 0.6), 0 0 60px rgba(125, 211, 252, 0.3);
    }

    /* Aurora/ice accent line */
    .ice-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, #38BDF8, #7DD3FC, #B8EAFF, #7DD3FC, #38BDF8, transparent);
        border-radius: 2px;
        box-shadow: 0 0 15px rgba(125, 211, 252, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="landing-header">
        <div class="header-logo">
            {logo_svg}
        </div>
        <div class="header-buttons">
            <a href="?page=login" class="glow-btn glow-btn-signin">Sign In</a>
            <a href="?page=register" class="glow-btn glow-btn-register">Get Started Free</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # HERO SECTION
    st.markdown("""
    <div style="text-align: center; padding: 100px 20px 80px 20px; position: relative;">
        <div style="position: absolute; top: 20px; left: 10%; opacity: 0.4;" class="snowflake">&#10052;</div>
        <div style="position: absolute; top: 60px; right: 15%; opacity: 0.3;" class="snowflake">&#10053;</div>
        <div style="position: absolute; bottom: 40px; left: 20%; opacity: 0.35;" class="snowflake">&#10054;</div>

        <h1 style="font-size: 58px; margin-bottom: 24px; font-weight: 700; line-height: 1.15;">
            <span style="color: #E0F7FF;">Stop Guessing.</span><br/>
            <span class="ice-glow">Start Dominating.</span>
        </h1>
        <p style="font-size: 22px; color: #93C5E0; max-width: 650px; margin: 0 auto 45px auto; line-height: 1.7;">
            Bear's Den gives Whiteout Survival players the data-driven insights they need to make smarter decisions and grow faster.
        </p>
        <a href="?page=register" class="glow-btn glow-btn-register" style="font-size: 18px; padding: 18px 45px;">
            Start Your Journey
        </a>

        <div class="ice-line" style="max-width: 400px; margin: 60px auto 0 auto;"></div>
    </div>
    """, unsafe_allow_html=True)

    # PROBLEM SECTION
    st.markdown("""
    <div class="ice-card" style="padding: 50px; margin: 20px auto 60px auto; max-width: 1000px;">
        <h2 style="text-align: center; color: #7DD3FC; margin-bottom: 40px; font-size: 32px;">
            <span style="margin-right: 10px;">&#10052;</span>Sound Familiar?<span style="margin-left: 10px;">&#10052;</span>
        </h2>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px;">
            <div style="text-align: center; padding: 25px; background: rgba(125, 211, 252, 0.08); border-radius: 12px; border: 1px solid rgba(125, 211, 252, 0.15);">
                <div style="font-size: 42px; margin-bottom: 16px;">&#128176;</div>
                <p style="color: #E0F7FF; font-size: 16px; line-height: 1.6;">"I keep spending but I'm not getting any stronger."</p>
            </div>
            <div style="text-align: center; padding: 25px; background: rgba(125, 211, 252, 0.08); border-radius: 12px; border: 1px solid rgba(125, 211, 252, 0.15);">
                <div style="font-size: 42px; margin-bottom: 16px;">&#128565;</div>
                <p style="color: #E0F7FF; font-size: 16px; line-height: 1.6;">"I have 20 heroes and no idea which to upgrade next."</p>
            </div>
            <div style="text-align: center; padding: 25px; background: rgba(125, 211, 252, 0.08); border-radius: 12px; border: 1px solid rgba(125, 211, 252, 0.15);">
                <div style="font-size: 42px; margin-bottom: 16px;">&#128548;</div>
                <p style="color: #E0F7FF; font-size: 16px; line-height: 1.6;">"My rally got destroyed. What lineup should I use?"</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SOLUTION STATEMENT
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px 70px 20px;">
        <h2 style="font-size: 40px; color: #E0F7FF; margin-bottom: 20px; line-height: 1.3;">
            What if you had a <span class="ice-glow">strategic advisor</span> in your pocket?
        </h2>
        <p style="font-size: 20px; color: #93C5E0; max-width: 750px; margin: 0 auto;">
            Bear's Den analyzes your account, tracks your progress, and tells you exactly what to do next.
            <strong style="color: #B8EAFF;">No more guessing. No more wasted resources.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # FEATURES SECTION HEADER
    st.markdown("""
    <div style="text-align: center; margin-bottom: 50px;">
        <div class="ice-line" style="max-width: 200px; margin: 0 auto 30px auto;"></div>
        <h2 style="color: #E0F7FF; font-size: 38px;">Everything You Need to Win</h2>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards using columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="ice-card" style="padding: 35px; height: 100%; min-height: 400px;">
            <div style="font-size: 52px; margin-bottom: 20px; text-align: center;">&#129302;</div>
            <h3 style="color: #7DD3FC; font-size: 24px; margin-bottom: 18px; text-align: center; text-shadow: 0 0 20px rgba(125, 211, 252, 0.3);">AI-Powered Advisor</h3>
            <p style="color: #93C5E0; font-size: 15px; line-height: 1.7; margin-bottom: 22px; text-align: center;">Get personalized upgrade recommendations ranked by priority. Stop asking Discord - let data guide your growth.</p>
            <ul style="color: #E0F7FF; font-size: 14px; line-height: 2.2; padding-left: 20px;">
                <li>Prioritized upgrade paths</li>
                <li>Resource-efficient strategies</li>
                <li>Adapts to your spending level</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="ice-card" style="padding: 35px; height: 100%; min-height: 400px;">
            <div style="font-size: 52px; margin-bottom: 20px; text-align: center;">&#128230;</div>
            <h3 style="color: #B8EAFF; font-size: 24px; margin-bottom: 18px; text-align: center; text-shadow: 0 0 20px rgba(184, 234, 255, 0.3);">Pack Value Analyzer</h3>
            <p style="color: #93C5E0; font-size: 15px; line-height: 1.7; margin-bottom: 22px; text-align: center;">Know the real value of every pack before you buy. Cut through marketing to see what's actually worth your money.</p>
            <ul style="color: #E0F7FF; font-size: 14px; line-height: 2.2; padding-left: 20px;">
                <li>True value per dollar</li>
                <li>Compare packs instantly</li>
                <li>Spot overpriced traps</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="ice-card" style="padding: 35px; height: 100%; min-height: 400px;">
            <div style="font-size: 52px; margin-bottom: 20px; text-align: center;">&#9876;&#65039;</div>
            <h3 style="color: #38BDF8; font-size: 24px; margin-bottom: 18px; text-align: center; text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);">Hero Tracker & Lineups</h3>
            <p style="color: #93C5E0; font-size: 15px; line-height: 1.7; margin-bottom: 22px; text-align: center;">Track all your heroes and get battle-tested lineup suggestions for rallies, garrison, and SvS battles.</p>
            <ul style="color: #E0F7FF; font-size: 14px; line-height: 2.2; padding-left: 20px;">
                <li>Full hero database</li>
                <li>Skill priority guides</li>
                <li>Optimal lineup builder</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # MORE FEATURES
    st.markdown("<div style='height: 70px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="deep-card" style="padding: 28px; text-align: center;">
            <div style="font-size: 40px; margin-bottom: 14px;">&#128081;</div>
            <h4 style="color: #B8EAFF; margin-bottom: 10px; font-size: 18px;">Chief Gear Tracker</h4>
            <p style="color: #93C5E0; font-size: 14px; line-height: 1.5;">Track all 6 gear slots and 18 charms with tier progression.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="deep-card" style="padding: 28px; text-align: center;">
            <div style="font-size: 40px; margin-bottom: 14px;">&#128218;</div>
            <h4 style="color: #B8EAFF; margin-bottom: 10px; font-size: 18px;">Strategy Guides</h4>
            <p style="color: #93C5E0; font-size: 14px; line-height: 1.5;">Battle tactics, event tips, and resource management.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="deep-card" style="padding: 28px; text-align: center;">
            <div style="font-size: 40px; margin-bottom: 14px;">&#128200;</div>
            <h4 style="color: #B8EAFF; margin-bottom: 10px; font-size: 18px;">Progress Tracking</h4>
            <p style="color: #93C5E0; font-size: 14px; line-height: 1.5;">Visual charts and milestone tracking over time.</p>
        </div>
        """, unsafe_allow_html=True)

    # SOCIAL PROOF
    st.markdown("""
    <div class="ice-card" style="text-align: center; padding: 55px 30px; margin: 70px auto; max-width: 900px;">
        <h3 style="color: #7DD3FC; font-size: 14px; margin-bottom: 35px; letter-spacing: 3px; text-transform: uppercase;">Trusted By Players From</h3>
        <div style="display: flex; justify-content: center; gap: 80px; flex-wrap: wrap;">
            <div>
                <div style="font-size: 48px; font-weight: bold; color: #B8EAFF; text-shadow: 0 0 30px rgba(184, 234, 255, 0.5);">500+</div>
                <div style="color: #93C5E0; font-size: 15px; margin-top: 5px;">States</div>
            </div>
            <div>
                <div style="font-size: 48px; font-weight: bold; color: #7DD3FC; text-shadow: 0 0 30px rgba(125, 211, 252, 0.5);">100+</div>
                <div style="color: #93C5E0; font-size: 15px; margin-top: 5px;">Alliances</div>
            </div>
            <div>
                <div style="font-size: 48px; font-weight: bold; color: #38BDF8; text-shadow: 0 0 30px rgba(56, 189, 248, 0.5);">Gen 1-14</div>
                <div style="color: #93C5E0; font-size: 15px; margin-top: 5px;">All Generations</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FINAL CTA
    st.markdown("""
    <div style="text-align: center; padding: 70px 20px; position: relative;">
        <div style="position: absolute; top: 10px; right: 20%; opacity: 0.3;" class="snowflake">&#10052;</div>
        <div style="position: absolute; bottom: 20px; left: 15%; opacity: 0.25;" class="snowflake">&#10053;</div>

        <h2 style="font-size: 44px; color: #E0F7FF; margin-bottom: 18px;">Ready to Level Up?</h2>
        <p style="font-size: 20px; color: #93C5E0; margin-bottom: 45px;">
            Create your free account and start making smarter decisions today.
        </p>
        <a href="?page=register" class="glow-btn glow-btn-register" style="font-size: 20px; padding: 20px 55px; margin-right: 20px;">
            Get Started Free
        </a>
        <a href="?page=login" class="glow-btn glow-btn-signin" style="font-size: 18px; padding: 18px 40px;">
            Sign In
        </a>
    </div>
    """, unsafe_allow_html=True)

    # FOOTER WITH LEGAL DISCLAIMER
    st.markdown("""
    <div class="deep-card" style="margin-top: 60px; padding: 50px 30px 30px 30px; border-radius: 0;">
        <div style="text-align: center; margin-bottom: 40px;">
            <span style="font-size: 28px; color: #38BDF8;">&#127922;</span>
            <p style="color: #E0F7FF; font-weight: 600; margin: 10px 0 5px 0;">Random Chaos Labs</p>
            <p style="font-size: 13px; color: #6B9AB8;">wos.randomchaoslabs.com</p>
        </div>

        <div style="max-width: 800px; margin: 0 auto; padding: 25px 30px; background: rgba(10, 22, 40, 0.6); border-radius: 12px; border: 1px solid rgba(125, 211, 252, 0.1);">
            <p style="font-size: 11px; color: #6B9AB8; text-align: center; line-height: 1.8; margin: 0;">
                <strong style="color: #93C5E0;">Disclaimer:</strong> Bear's Den and Random Chaos Labs are not affiliated with, endorsed by, or sponsored by Century Games, Whiteout Survival, or any related entities.
                All game content, names, and trademarks are property of their respective owners.<br/><br/>
                The information provided on this platform is for entertainment and informational purposes only.
                <strong style="color: #93C5E0;">Random Chaos Labs makes no guarantees regarding the accuracy, completeness, or timeliness of any data presented.</strong>
                Users are solely responsible for their own gameplay decisions, including any in-game purchases or resource allocation.
                By using this service, you acknowledge that Random Chaos Labs shall not be held liable for any losses, damages, or dissatisfaction
                arising from decisions made based on information provided herein. Use this tool at your own discretion and risk.
            </p>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <p style="font-size: 11px; color: #4A7A98;">
                &copy; 2025 Random Chaos Labs. All rights reserved.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Run if called directly
if __name__ == "__main__":
    render_landing()
