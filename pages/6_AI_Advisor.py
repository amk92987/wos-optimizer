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
from database.models import UserHero, UserInventory, UserChiefGear, UserChiefCharm
from engine import RecommendationEngine, AIRecommender, HeroRecommender
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

# Get user chief gear and charms for power optimizer (handle schema mismatches gracefully)
try:
    user_gear = db.query(UserChiefGear).filter(UserChiefGear.profile_id == profile.id).all()
except Exception:
    user_gear = []

try:
    user_charms = db.query(UserChiefCharm).filter(UserChiefCharm.profile_id == profile.id).all()
except Exception:
    user_charms = []

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


def get_tier_color(tier: str) -> str:
    """Get color for tier badge."""
    colors = {
        "S+": "#FF4444",
        "S": "#FF8C00",
        "A": "#9932CC",
        "B": "#4169E1",
        "C": "#32CD32",
        "D": "#808080"
    }
    return colors.get(tier, "#808080")


def get_class_color(hero_class: str) -> str:
    """Get color for class badge."""
    colors = {
        "Infantry": "#E74C3C",
        "Marksman": "#3498DB",
        "Lancer": "#2ECC71"
    }
    return colors.get(hero_class, "#808080")


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
tab1, tab2, tab3, tab4 = st.tabs(["Recommendations", "Hero Investment", "Lineups", "Ask a Question"])

with tab1:
    st.markdown("### Your Top Priorities")

    if not user_heroes:
        st.info("Add some heroes first in the Heroes page to get personalized recommendations.")
    else:
        # Get recommendations including power-based analysis
        recommendations = engine.get_recommendations(
            profile, user_heroes,
            user_gear=user_gear,
            user_charms=user_charms,
            limit=10,
            include_power=True
        )

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
                    "lineup": "#27AE60",
                    # Power optimizer categories
                    "chief_gear": "#E67E22",
                    "chief_charm": "#16A085",
                    "hero_level": "#9B59B6",
                    "hero_star": "#9B59B6",
                    "troop_tier": "#E74C3C",
                    "war_academy": "#C0392B",
                    "research": "#2980B9",
                    "pet": "#F39C12",
                    "daybreak": "#8E44AD"
                }
                cat_color = cat_colors.get(category, "#888")

                # Display category names nicely
                cat_display = {
                    "chief_gear": "GEAR",
                    "chief_charm": "CHARM",
                    "hero_level": "HERO",
                    "hero_star": "HERO",
                    "troop_tier": "TROOPS",
                    "war_academy": "WAR ACAD",
                    "research": "RESEARCH",
                    "pet": "PETS",
                    "daybreak": "DAYBREAK"
                }
                cat_label = cat_display.get(category, category.upper())

                # Source indicator for power-based recommendations
                source_badge = ""
                if source == "power":
                    source_badge = '<span style="background:#1ABC9C;color:white;padding:1px 5px;border-radius:3px;font-size:9px;margin-left:6px;">POWER</span>'

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
                            ">{cat_label}</span>
                            {source_badge}
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
    st.markdown("### Hero Investment Analysis")
    st.markdown(f"Based on your priorities, generation, and spending profile ({profile.spending_profile.upper()}):")

    if not user_heroes:
        st.info("Add heroes in the Hero Tracker page to see investment recommendations.")
    else:
        # Use HeroRecommender for hero-specific investment analysis
        hero_engine = HeroRecommender(HERO_DATA, user_heroes, profile)
        top_heroes = hero_engine.get_top_heroes_to_invest(limit=10)

        if not top_heroes:
            st.info("No investment recommendations available yet.")
        else:
            for i, hero in enumerate(top_heroes):
                tier_color = get_tier_color(hero['tier'])
                class_color = get_class_color(hero['class'])

                # Current vs target display
                current_level = hero.get('current_level', 1)
                current_stars = hero.get('current_stars', 0)
                target_level = hero.get('target_level', 50)
                target_stars = hero.get('target_stars', 2)
                advice = hero.get('advice', '')

                # Progress indicator
                level_progress = f"L{current_level} → L{target_level}" if current_level < target_level else f"L{current_level} ✓"
                stars_display = f"{'★' * current_stars}{'☆' * (5-current_stars)}"
                target_stars_display = f"{'★' * target_stars}{'☆' * (5-target_stars)}"

                st.markdown(f"""
                <div style="
                    background: rgba(46, 90, 140, 0.25);
                    border: 1px solid rgba(74, 144, 217, 0.3);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <div style="
                                font-size: 24px;
                                font-weight: bold;
                                color: #4A90D9;
                                width: 40px;
                            ">#{i+1}</div>
                            <div>
                                <div style="font-size: 18px; font-weight: bold; color: #E8F4F8;">
                                    {hero['name']}
                                </div>
                                <div style="display: flex; gap: 8px; margin-top: 4px; align-items: center;">
                                    <span style="
                                        background: {tier_color};
                                        color: white;
                                        padding: 2px 8px;
                                        border-radius: 4px;
                                        font-size: 11px;
                                    ">{hero['tier']}</span>
                                    <span style="
                                        background: rgba(255,255,255,0.1);
                                        border-left: 3px solid {class_color};
                                        padding: 2px 8px;
                                        font-size: 11px;
                                        color: #E8F4F8;
                                    ">{hero['class']}</span>
                                    <span style="color: #B8D4E8; font-size: 11px;">Gen {hero['generation']}</span>
                                </div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #4A90D9; font-size: 14px; font-weight: bold;">{level_progress}</div>
                            <div style="color: #FFD700; font-size: 12px;">{stars_display}</div>
                            <div style="color: #888; font-size: 10px;">Target: {target_stars_display}</div>
                        </div>
                    </div>
                    <div style="color: #4CAF50; font-size: 13px; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(74,144,217,0.2);">
                        {advice}
                    </div>
                    <div style="color: #B8D4E8; font-size: 11px; margin-top: 6px;">
                        {hero.get('notes', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Hero stats summary
        st.markdown("---")
        st.markdown("### Your Hero Stats")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div style="background: rgba(74, 144, 217, 0.2); padding: 20px; border-radius: 12px;">
                <div style="font-size: 14px; color: #B8D4E8;">Total Heroes Owned</div>
                <div style="font-size: 32px; font-weight: bold; color: #4A90D9;">{}</div>
            </div>
            """.format(len(user_heroes)), unsafe_allow_html=True)

        with col2:
            avg_level = sum(h.level for h in user_heroes) / len(user_heroes) if user_heroes else 0
            st.markdown("""
            <div style="background: rgba(255, 107, 53, 0.2); padding: 20px; border-radius: 12px;">
                <div style="font-size: 14px; color: #B8D4E8;">Average Level</div>
                <div style="font-size: 32px; font-weight: bold; color: #FF6B35;">{:.1f}</div>
            </div>
            """.format(avg_level), unsafe_allow_html=True)

        with col3:
            # Count heroes by tier
            tier_counts = {}
            for uh in user_heroes:
                hero_data = next((h for h in HERO_DATA['heroes'] if h['name'] == uh.hero.name), None)
                if hero_data:
                    tier = hero_data.get('tier_overall', '?')
                    tier_counts[tier] = tier_counts.get(tier, 0) + 1

            top_tier_count = tier_counts.get('S+', 0) + tier_counts.get('S', 0)
            st.markdown("""
            <div style="background: rgba(255, 215, 0, 0.2); padding: 20px; border-radius: 12px;">
                <div style="font-size: 14px; color: #B8D4E8;">S+/S Tier Heroes</div>
                <div style="font-size: 32px; font-weight: bold; color: #FFD700;">{}</div>
            </div>
            """.format(top_tier_count), unsafe_allow_html=True)

        # Class distribution
        st.markdown("### Class Distribution")

        class_counts = {"Infantry": 0, "Marksman": 0, "Lancer": 0}
        for uh in user_heroes:
            hero_data = next((h for h in HERO_DATA['heroes'] if h['name'] == uh.hero.name), None)
            if hero_data:
                hero_class = hero_data.get('hero_class', 'Unknown')
                if hero_class in class_counts:
                    class_counts[hero_class] += 1

        cols = st.columns(3)
        for i, (class_name, count) in enumerate(class_counts.items()):
            with cols[i]:
                color = get_class_color(class_name)
                st.markdown(f"""
                <div style="
                    background: rgba(46, 90, 140, 0.3);
                    border-left: 4px solid {color};
                    padding: 16px;
                    border-radius: 8px;
                ">
                    <div style="font-size: 14px; color: #B8D4E8;">{class_name}</div>
                    <div style="font-size: 28px; font-weight: bold; color: {color};">{count}</div>
                </div>
                """, unsafe_allow_html=True)

        # Tier distribution
        st.markdown("### Tier Distribution")

        tier_order = ['S+', 'S', 'A', 'B', 'C', 'D']
        cols = st.columns(len(tier_order))
        for i, tier in enumerate(tier_order):
            with cols[i]:
                count = tier_counts.get(tier, 0)
                color = get_tier_color(tier)
                st.markdown(f"""
                <div style="
                    background: {color}33;
                    border: 2px solid {color};
                    padding: 12px;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <div style="font-weight: bold; color: {color};">{tier}</div>
                    <div style="font-size: 24px; color: #E8F4F8;">{count}</div>
                </div>
                """, unsafe_allow_html=True)

with tab3:
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

with tab4:
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

# Close database
db.close()
