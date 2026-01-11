"""
AI Advisor Page - Get intelligent recommendations powered by rules and AI fallback.
Uses rule-based analysis first, with AI (Claude or OpenAI) for complex questions.
"""

import streamlit as st
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero, UserInventory
from engine import RecommendationEngine, AIRecommender
from engine.ai_recommender import format_data_preview

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

# Initialize recommendation engine and AI recommender
engine = RecommendationEngine(PROJECT_ROOT / "data")
ai_recommender = AIRecommender()

# Page content
st.markdown("# AI Advisor")
st.markdown("Get personalized recommendations powered by rules and AI.")

st.info("""
**How it works:** The advisor uses a **rule-based engine** with curated game knowledge for most questions.
For complex, contextual questions, it falls back to AI (Claude or OpenAI) with verified game mechanics.
This gives you **instant, accurate answers** for common questions, with AI power when needed.
""")

st.markdown("---")

# AI Provider status
col_status1, col_status2 = st.columns(2)

with col_status1:
    st.markdown("**Rules Engine:** Active")

with col_status2:
    if ai_recommender.is_available():
        provider = ai_recommender.get_provider_name()
        st.success(f"**AI Fallback:** {provider.title()} available")
    else:
        st.warning("""
        **AI Fallback:** Not configured

        Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment variable for AI features.
        """)

# Show current phase
phase_info = engine.get_phase_info(profile)
st.markdown(f"""
<div style="background:rgba(74,144,217,0.15);border-radius:8px;padding:12px;margin:16px 0;">
    <span style="font-weight:bold;color:#4A90D9;">Current Phase:</span>
    <span style="color:#E8F4F8;margin-left:8px;">{phase_info['phase_name']}</span>
    <span style="color:#888;margin-left:16px;">Next milestone: {phase_info['next_milestone']['name']}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["Recommendations", "Lineups", "Ask a Question", "Data Preview"])

with tab1:
    st.markdown("### Your Top Priorities")

    if not user_heroes:
        st.info("Add some heroes first in the Heroes page to get personalized recommendations.")
    else:
        # Get rule-based recommendations
        recommendations = engine.get_recommendations(profile, user_heroes, limit=10)

        if recommendations:
            for rec in recommendations:
                priority = rec.priority
                action = rec.action
                hero = rec.hero or ""
                reason = rec.reason
                resources = rec.resources
                category = rec.category
                source = rec.source

                # Priority colors
                if priority == 1:
                    border_color = "#FF4444"
                    bg_color = "rgba(255, 68, 68, 0.15)"
                    label = "DO FIRST"
                elif priority == 2:
                    border_color = "#FF8C00"
                    bg_color = "rgba(255, 140, 0, 0.15)"
                    label = "HIGH"
                elif priority <= 4:
                    border_color = "#FFD700"
                    bg_color = "rgba(255, 215, 0, 0.1)"
                    label = "MEDIUM"
                else:
                    border_color = "#4A90D9"
                    bg_color = "rgba(74, 144, 217, 0.1)"
                    label = "LOW"

                # Category badge
                cat_colors = {
                    "hero": "#9B59B6",
                    "gear": "#E67E22",
                    "progression": "#3498DB",
                    "lineup": "#27AE60"
                }
                cat_color = cat_colors.get(category, "#888")

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
                            <span style="
                                background: {cat_color};
                                color: white;
                                padding: 2px 6px;
                                border-radius: 4px;
                                font-size: 10px;
                                margin-left: 6px;
                            ">{category.upper()}</span>
                            {f'<span style="color:#B8D4E8;font-size:12px;margin-left:8px;">{hero}</span>' if hero else ''}
                        </div>
                    </div>
                    <div style="font-size: 16px; font-weight: bold; color: #E8F4F8; margin: 8px 0;">
                        {action}
                    </div>
                    <div style="color: #B8D4E8; font-size: 13px; margin-bottom: 4px;">
                        {reason}
                    </div>
                    {f'<div style="color:#808080;font-size:12px;">Resources: {resources}</div>' if resources else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recommendations available. Add more heroes or update your profile.")

        # Option to get AI recommendations
        st.markdown("---")
        st.markdown("### Want AI Analysis?")

        if ai_recommender.is_available():
            if st.button("Get AI-Powered Recommendations", type="secondary"):
                with st.spinner("Analyzing with AI..."):
                    ai_recs = ai_recommender.get_recommendations(
                        profile, user_heroes, HERO_DATA, inventory
                    )

                if ai_recs and 'error' not in ai_recs[0]:
                    st.success(f"AI generated {len(ai_recs)} additional recommendations")
                    for rec in ai_recs:
                        st.markdown(f"""
                        <div style="
                            background: rgba(155, 89, 182, 0.15);
                            border-left: 4px solid #9B59B6;
                            border-radius: 8px;
                            padding: 12px;
                            margin-bottom: 8px;
                        ">
                            <div style="font-weight:bold;color:#E8F4F8;">{rec.get('action', 'Action')}</div>
                            <div style="color:#B8D4E8;font-size:13px;">{rec.get('reason', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    error = ai_recs[0].get('error', 'Unknown error') if ai_recs else 'No response'
                    st.error(f"AI error: {error}")
        else:
            st.info("Set up an AI provider (Claude or OpenAI) for additional analysis.")

with tab2:
    st.markdown("### Lineup Recommendations")

    # Mode selector
    mode_options = {
        "rally_joiner_attack": "Rally Joiner (Attack)",
        "rally_joiner_defense": "Rally Joiner (Defense)",
        "bear_trap": "Bear Trap Rally",
        "crazy_joe": "Crazy Joe Rally",
        "garrison": "Castle Garrison",
        "exploration": "Exploration/PvE",
        "svs_march": "SvS Field March"
    }

    selected_mode = st.selectbox(
        "Select Game Mode",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x]
    )

    if user_heroes:
        lineup = engine.get_lineup(selected_mode, user_heroes, profile)

        # Show lineup
        st.markdown(f"**{lineup['mode']}**")

        # Confidence indicator
        conf_colors = {"high": "#27AE60", "medium": "#F1C40F", "low": "#E74C3C"}
        conf_color = conf_colors.get(lineup['confidence'], "#888")
        st.markdown(f"""
        <span style="background:{conf_color};color:white;padding:2px 8px;border-radius:4px;font-size:11px;">
            {lineup['confidence'].upper()} CONFIDENCE
        </span>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Heroes table
        cols = st.columns([1, 2, 2, 2])
        with cols[0]:
            st.markdown("**Slot**")
        with cols[1]:
            st.markdown("**Hero**")
        with cols[2]:
            st.markdown("**Role**")
        with cols[3]:
            st.markdown("**Your Status**")

        for hero_info in lineup['heroes']:
            cols = st.columns([1, 2, 2, 2])
            with cols[0]:
                st.markdown(hero_info['slot'])
            with cols[1]:
                st.markdown(f"**{hero_info['hero']}**")
            with cols[2]:
                st.markdown(hero_info['role'])
            with cols[3]:
                status = hero_info['your_status']
                color = "#27AE60" if "Lv" in status else "#E74C3C"
                st.markdown(f"<span style='color:{color}'>{status}</span>", unsafe_allow_html=True)

        # Troop ratio
        st.markdown("---")
        st.markdown("**Recommended Troop Ratio:**")
        ratio = lineup['troop_ratio']
        cols = st.columns(3)
        with cols[0]:
            st.metric("Infantry", f"{ratio.get('infantry', 0)}%")
        with cols[1]:
            st.metric("Lancer", f"{ratio.get('lancer', 0)}%")
        with cols[2]:
            st.metric("Marksman", f"{ratio.get('marksman', 0)}%")

        # Notes
        st.info(lineup['notes'])

        # Joiner recommendation
        if "joiner" in selected_mode:
            st.markdown("---")
            attack = "attack" in selected_mode
            joiner_rec = engine.get_joiner_recommendation(user_heroes, attack)

            if joiner_rec.get('status') == 'owned':
                st.success(f"""
                **Joiner Recommendation:** {joiner_rec['recommendation']}

                {joiner_rec.get('action', '')}
                """)
            else:
                st.warning(f"""
                **No good joiner hero!** {joiner_rec['action']}

                {joiner_rec['critical_note']}
                """)
    else:
        st.info("Add heroes to see personalized lineup recommendations.")

with tab3:
    st.markdown("### Ask the Advisor")

    # Quick question buttons
    st.markdown("**Quick Questions:**")
    col1, col2 = st.columns(2)

    quick_questions = [
        ("Best rally joiner?", "What hero should I use when joining attack rallies?"),
        ("SvS prep?", "How should I prepare for the next SvS?"),
        ("Who to level?", "Which hero should I level next?"),
        ("Gear priority?", "What's my chief gear upgrade priority?"),
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
        placeholder="e.g., What's my best Bear Trap lineup?",
        height=80
    )

    force_ai = st.checkbox("Force AI response (skip rules)", value=False)

    if st.button("Ask", type="primary"):
        if not custom_q:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                result = engine.ask(
                    profile, user_heroes, custom_q,
                    force_ai=force_ai
                )

            # Show source
            source = result.get('source', 'unknown')
            if source == 'rules':
                st.success("Answered using game rules (instant)")
            elif source == 'ai':
                st.info(f"Answered using AI ({ai_recommender.get_provider_name()})")
            elif source == 'error':
                st.error("Could not process request")

            # Show answer
            if 'answer' in result:
                st.markdown(f"""
                <div style="
                    background: rgba(74, 144, 217, 0.15);
                    border: 1px solid rgba(74, 144, 217, 0.3);
                    border-radius: 12px;
                    padding: 20px;
                ">
                    <div style="color: #E8F4F8; font-size: 15px; line-height: 1.6;">
                        {result['answer']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Show lineup if present
            if 'lineup' in result:
                lineup = result['lineup']
                st.markdown(f"**Lineup for {lineup['mode']}:**")
                for h in lineup['heroes']:
                    st.markdown(f"- **{h['slot']}:** {h['hero']} ({h['role']})")

            # Show recommendations if present
            if result.get('recommendations'):
                st.markdown("**Related recommendations:**")
                for rec in result['recommendations'][:3]:
                    action = rec.get('action', '')
                    reason = rec.get('reason', '')
                    st.markdown(f"- {action}: {reason}")

with tab4:
    st.markdown("### Data Preview")
    st.markdown("This is what gets sent to AI when using AI features:")

    data_preview = format_data_preview(profile, user_heroes, HERO_DATA)
    st.code(data_preview, language="text")

    st.markdown("---")
    st.markdown("""
    **Format breakdown:**

    - **PROFILE:** Generation, server age, furnace level
    - **PRIORITIES:** Your focus areas (1=low, 5=critical)
    - **MY HEROES:** Name [Tier|Class|Gen] Level Stars Skills
    - **INVENTORY:** Resources you have (if included)
    """)

# Close database
db.close()
