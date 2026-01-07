"""
AI Advisor Page - Get intelligent recommendations powered by OpenAI.
"""

import streamlit as st
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero, UserInventory
from engine.ai_recommender import AIRecommender, format_data_preview

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load hero data
heroes_file = PROJECT_ROOT / "data" / "heroes.json"
with open(heroes_file, encoding='utf-8') as f:
    HERO_DATA = json.load(f)

# Get user heroes
user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()

# Get inventory
def get_inventory_dict():
    inventory = db.query(UserInventory).filter(UserInventory.profile_id == profile.id).all()
    grouped = {}
    for inv in inventory:
        cat = inv.item.category
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append({'name': inv.item.name, 'quantity': inv.quantity})
    return grouped

inventory = get_inventory_dict()

# Initialize recommender (auto-detects API key from Windows env)
recommender = AIRecommender()

# Page content
st.markdown("# 🤖 AI Advisor")
st.markdown("Get intelligent, personalized recommendations powered by AI.")

st.markdown("---")

# API Key status
if not recommender.is_available():
    st.warning("""
    **OpenAI API Key not found!**

    Set your API key as a Windows environment variable:
    ```
    setx OPENAI_API_KEY "your-key-here"
    ```

    Or enter it below (session only):
    """)
    manual_key = st.text_input("OpenAI API Key", type="password", help="Your key is not stored")
    if manual_key:
        recommender = AIRecommender(api_key=manual_key)
else:
    st.success("✅ OpenAI API key detected")

# Show data preview
st.markdown("## 📋 Your Data (What AI Sees)")
st.markdown("This is exactly what gets sent to the AI - compact and clear:")

data_preview = format_data_preview(profile, user_heroes, HERO_DATA)

st.code(data_preview, language="text")

st.markdown("---")

# Tabs for different AI features
tab1, tab2, tab3 = st.tabs(["🎯 Get Recommendations", "❓ Ask a Question", "📊 Data Format"])

with tab1:
    st.markdown("### Get AI-Powered Recommendations")

    if not user_heroes:
        st.info("Add some heroes first in the 🦸 Heroes page to get personalized recommendations.")
    else:
        col1, col2 = st.columns([2, 1])

        with col1:
            include_inventory = st.checkbox("Include inventory data", value=bool(inventory))

        with col2:
            model_choice = st.selectbox("Model", ["gpt-4o-mini (fast)", "gpt-4o (best)"])

        if st.button("🚀 Get AI Recommendations", type="primary", use_container_width=True):
            if not recommender.is_available():
                st.error("Please provide an OpenAI API key above.")
            else:
                with st.spinner("Analyzing your account..."):
                    inv_data = inventory if include_inventory else None
                    recommendations = recommender.get_recommendations(
                        profile, user_heroes, HERO_DATA, inv_data
                    )

                if recommendations and 'error' not in recommendations[0]:
                    st.success(f"Generated {len(recommendations)} recommendations!")

                    for i, rec in enumerate(recommendations):
                        priority = rec.get('priority', i + 1)
                        action = rec.get('action', 'Unknown action')
                        hero = rec.get('hero', '')
                        reason = rec.get('reason', '')
                        resources = rec.get('resources', '')

                        # Priority colors
                        if priority == 1:
                            border_color = "#FF4444"
                            bg_color = "rgba(255, 68, 68, 0.15)"
                            label = "🔥 DO FIRST"
                        elif priority == 2:
                            border_color = "#FF8C00"
                            bg_color = "rgba(255, 140, 0, 0.15)"
                            label = "⚡ HIGH"
                        elif priority <= 4:
                            border_color = "#FFD700"
                            bg_color = "rgba(255, 215, 0, 0.1)"
                            label = "📌 MEDIUM"
                        else:
                            border_color = "#4A90D9"
                            bg_color = "rgba(74, 144, 217, 0.1)"
                            label = "📋 LOW"

                        st.markdown(f"""
                        <div style="
                            background: {bg_color};
                            border-left: 4px solid {border_color};
                            border-radius: 8px;
                            padding: 16px;
                            margin-bottom: 12px;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <span style="
                                        background: {border_color};
                                        color: white;
                                        padding: 2px 8px;
                                        border-radius: 4px;
                                        font-size: 11px;
                                        font-weight: bold;
                                    ">{label}</span>
                                    <span style="color: #B8D4E8; font-size: 12px; margin-left: 8px;">
                                        {hero}
                                    </span>
                                </div>
                                <span style="color: #4A90D9; font-size: 12px;">#{priority}</span>
                            </div>
                            <div style="font-size: 16px; font-weight: bold; color: #E8F4F8; margin: 8px 0;">
                                {action}
                            </div>
                            <div style="color: #B8D4E8; font-size: 13px; margin-bottom: 4px;">
                                {reason}
                            </div>
                            <div style="color: #808080; font-size: 12px;">
                                📦 Needs: {resources}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    error_msg = recommendations[0].get('error', 'Unknown error') if recommendations else 'No response'
                    st.error(f"Error: {error_msg}")
                    if 'raw' in recommendations[0]:
                        st.code(recommendations[0]['raw'], language="text")

with tab2:
    st.markdown("### Ask the AI Advisor")
    st.markdown("Ask specific questions about your account, strategy, or heroes.")

    # Quick question buttons
    st.markdown("**Quick Questions:**")
    col1, col2 = st.columns(2)

    quick_questions = [
        ("Best rally team?", "What's my best rally attack team composition?"),
        ("SvS prep?", "How should I prepare for the next SvS? What should I focus on this week?"),
        ("Who to ascend?", "Which hero should I ascend next with my general shards?"),
        ("Weakest link?", "What's my biggest weakness and how do I fix it?"),
    ]

    selected_question = None

    with col1:
        if st.button(quick_questions[0][0], use_container_width=True):
            selected_question = quick_questions[0][1]
        if st.button(quick_questions[2][0], use_container_width=True):
            selected_question = quick_questions[2][1]

    with col2:
        if st.button(quick_questions[1][0], use_container_width=True):
            selected_question = quick_questions[1][1]
        if st.button(quick_questions[3][0], use_container_width=True):
            selected_question = quick_questions[3][1]

    # Custom question
    custom_q = st.text_area(
        "Or ask your own question:",
        value=selected_question or "",
        placeholder="e.g., Should I invest in Philly or save for Mia?",
        height=80
    )

    if st.button("🤔 Ask AI", type="primary"):
        if not custom_q:
            st.warning("Please enter a question.")
        elif not recommender.is_available():
            st.error("Please provide an OpenAI API key.")
        else:
            with st.spinner("Thinking..."):
                answer = recommender.ask_question(
                    profile, user_heroes, HERO_DATA, custom_q, inventory
                )

            st.markdown("### Answer")
            st.markdown(f"""
            <div style="
                background: rgba(74, 144, 217, 0.15);
                border: 1px solid rgba(74, 144, 217, 0.3);
                border-radius: 12px;
                padding: 20px;
            ">
                <div style="color: #E8F4F8; font-size: 15px; line-height: 1.6;">
                    {answer}
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("### Data Format Explained")

    st.markdown("""
    The AI receives your data in this compact format:

    ```
    PROFILE: Gen2 (Day 85), Furnace 18
    PRIORITIES: SvS=5, Rally=4, Castle=4, PvE=2, Gather=1

    MY HEROES:
    - Jeronimo [S+|Inf|Gen1] Lv45 ★★★☆☆ Skills: Expl 3/2 Exped 4/3
    - Natalia [A|Inf|Gen1] Lv30 ★★☆☆☆ Skills: Expl 2/2 Exped 2/2

    INVENTORY: 50 Epic Shards, 20 Legendary Shards, 500 Combat Manuals
    ```

    **Format breakdown:**
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **PROFILE Line:**
        - `Gen2` = Your current hero generation
        - `Day 85` = Server age in days
        - `Furnace 18` = Your furnace level

        **PRIORITIES Line:**
        - Scale: 1 (low) to 5 (critical)
        - SvS = State vs State focus
        - Rally = Rally attacks focus
        - Castle = Castle battles
        - PvE = Exploration/stages
        - Gather = Resource gathering
        """)

    with col2:
        st.markdown("""
        **HERO Line Format:**
        ```
        Name [Tier|Class|Gen] Lv## ★★★☆☆ Skills: Expl #/# Exped #/#
        ```

        - `[S+|Inf|Gen1]` = S+ tier, Infantry, Generation 1
        - `Lv45` = Current level
        - `★★★☆☆` = 3 out of 5 stars
        - `Expl 3/2` = Exploration skills at 3 and 2
        - `Exped 4/3` = Expedition skills at 4 and 3
        """)

    st.markdown("---")

    st.markdown("""
    **Why this format?**
    - **Compact**: Fits more data in fewer tokens = faster & cheaper
    - **Clear**: AI can easily parse structured data
    - **Complete**: Contains everything needed for good recommendations
    - **No confusion**: Abbreviations are consistent and explained in system prompt
    """)

# Close database
db.close()
