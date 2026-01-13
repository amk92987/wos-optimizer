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
from database.models import UserHero, UserInventory, UserChiefGear, UserChiefCharm, User
from database.auth import get_current_user_id, is_authenticated
from database.ai_service import (
    get_ai_mode, check_rate_limit, record_ai_request,
    log_ai_conversation, rate_conversation, get_ai_settings,
    get_recent_conversations, toggle_favorite, get_favorite_conversations,
    create_thread_id, generate_thread_title, get_user_threads,
    get_thread_conversations, get_standalone_conversations
)
from engine import RecommendationEngine, AIRecommender, HeroRecommender
from engine.ai_recommender import format_data_preview
from utils.toolbar import render_donate_message, render_feedback_form
from datetime import datetime
import time

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

# Donate message
render_donate_message()

st.markdown("---")

# Get current user for rate limiting
current_user_id = get_current_user_id()
current_user = db.query(User).filter(User.id == current_user_id).first() if current_user_id else None

# AI Mode and status
ai_mode = get_ai_mode(db)
ai_settings = get_ai_settings(db)

# Check rate limit status
if current_user:
    can_use_ai, rate_message, remaining = check_rate_limit(db, current_user)
else:
    can_use_ai, rate_message, remaining = False, "Please log in to use AI features", 0

# AI Provider status
col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    st.markdown("**Rules Engine:** Active")

with col_status2:
    if ai_mode == 'off':
        st.error("**AI:** Disabled")
    elif ai_recommender.is_available():
        provider = ai_recommender.get_provider_name()
        st.success(f"**AI:** {provider.title()}")
    else:
        st.warning("**AI:** Not configured")

with col_status3:
    if ai_mode == 'off':
        st.markdown("**Requests:** AI disabled")
    elif ai_mode == 'unlimited':
        st.markdown("**Requests:** Unlimited")
    elif remaining == -1:
        st.markdown("**Requests:** Unlimited")
    elif remaining > 0:
        st.markdown(f"**Requests:** {remaining} remaining today")
    else:
        st.warning("**Requests:** Daily limit reached")

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Recommendations", "Hero Investment", "Lineups", "Ask a Question", "⭐ Favorites"])

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
                    # Sanitize error message for user display
                    raw_error = ai_recs[0].get('error', 'Unknown error') if ai_recs else 'No response'
                    # Hide technical details from users
                    if 'API' in str(raw_error) or 'key' in str(raw_error).lower() or 'rate' in str(raw_error).lower():
                        user_error = "AI service is temporarily unavailable. Please try again later."
                    elif 'timeout' in str(raw_error).lower() or 'connection' in str(raw_error).lower():
                        user_error = "Could not connect to AI service. Please check your internet connection."
                    else:
                        user_error = "Unable to get AI recommendations at this time."
                    st.error(user_error)
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

    # Initialize chat history and thread tracking in session state
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'current_thread_id' not in st.session_state:
        st.session_state.current_thread_id = None

    # Top controls: New Chat + Past Chats
    col_new, col_past = st.columns([1, 2])

    with col_new:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.current_thread_id = None  # Will be created on first message
            if 'last_ai_conversation_id' in st.session_state:
                del st.session_state['last_ai_conversation_id']
            st.rerun()

    with col_past:
        # Get threads and standalone conversations
        threads = []
        standalone = []
        if current_user_id:
            threads = get_user_threads(db, current_user_id, limit=10)
            standalone = get_standalone_conversations(db, current_user_id, limit=5)

        total_count = len(threads) + len(standalone)

        if total_count > 0:
            with st.expander(f"📜 Past Chats ({total_count})"):
                # Show threaded conversations first
                if threads:
                    st.markdown("**Conversations:**")
                    for thread in threads:
                        time_ago = ""
                        if thread['last_message']:
                            delta = datetime.now() - thread['last_message']
                            if delta.days > 0:
                                time_ago = f"{delta.days}d ago"
                            elif delta.seconds > 3600:
                                time_ago = f"{delta.seconds // 3600}h ago"
                            else:
                                time_ago = f"{delta.seconds // 60}m ago"

                        msg_count = thread['message_count']
                        title_preview = thread['title'][:45] + "..." if len(thread['title']) > 45 else thread['title']

                        col_q, col_load = st.columns([3, 1])
                        with col_q:
                            st.caption(f"💬 {title_preview} ({msg_count} msgs) • {time_ago}")
                        with col_load:
                            if st.button("Load", key=f"load_thread_{thread['thread_id']}"):
                                # Load entire thread into chat
                                thread_convos = get_thread_conversations(db, thread['thread_id'], current_user_id)
                                st.session_state.chat_messages = []
                                for conv in thread_convos:
                                    st.session_state.chat_messages.append({"role": "user", "content": conv.question})
                                    st.session_state.chat_messages.append({
                                        "role": "assistant",
                                        "content": conv.answer,
                                        "source": conv.routed_to or "unknown"
                                    })
                                st.session_state.current_thread_id = thread['thread_id']
                                if thread_convos:
                                    st.session_state['last_ai_conversation_id'] = thread_convos[-1].id
                                st.rerun()

                # Show standalone conversations
                if standalone:
                    if threads:
                        st.markdown("---")
                        st.markdown("**Single Q&A:**")
                    for conv in standalone:
                        q_preview = conv.question[:40] + "..." if len(conv.question) > 40 else conv.question
                        time_ago = ""
                        if conv.created_at:
                            delta = datetime.now() - conv.created_at
                            if delta.days > 0:
                                time_ago = f"{delta.days}d ago"
                            elif delta.seconds > 3600:
                                time_ago = f"{delta.seconds // 3600}h ago"
                            else:
                                time_ago = f"{delta.seconds // 60}m ago"

                        col_q, col_load = st.columns([3, 1])
                        with col_q:
                            st.caption(f"{q_preview} • {time_ago}")
                        with col_load:
                            if st.button("Load", key=f"load_conv_{conv.id}"):
                                # Load single conversation - create a new thread for follow-ups
                                st.session_state.chat_messages = [
                                    {"role": "user", "content": conv.question},
                                    {"role": "assistant", "content": conv.answer, "source": conv.routed_to or "unknown"}
                                ]
                                st.session_state.current_thread_id = None  # No thread yet
                                st.session_state['last_ai_conversation_id'] = conv.id
                                st.rerun()

    st.markdown("---")

    # Show thread indicator if there's an active conversation
    if st.session_state.chat_messages:
        msg_count = len([m for m in st.session_state.chat_messages if m['role'] == 'user'])
        if msg_count > 1:
            st.caption(f"💬 Conversation with {msg_count} messages • Follow-up questions will be added to this thread")
        elif msg_count == 1:
            st.caption("💬 New conversation • Ask follow-up questions to continue")

    # Display chat history
    if st.session_state.chat_messages:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="
                    background: rgba(255, 107, 53, 0.15);
                    border-left: 3px solid #FF6B35;
                    border-radius: 0 8px 8px 0;
                    padding: 12px 16px;
                    margin: 8px 0;
                ">
                    <div style="font-size: 11px; color: #FF6B35; margin-bottom: 4px;">You asked:</div>
                    <div style="color: #E8F4F8;">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                source_label = "Rules" if msg.get('source') == 'rules' else "AI" if msg.get('source') == 'ai' else ""
                source_color = "#2ECC71" if msg.get('source') == 'rules' else "#9B59B6"
                st.markdown(f"""
                <div style="
                    background: rgba(74, 144, 217, 0.15);
                    border-left: 3px solid #4A90D9;
                    border-radius: 0 8px 8px 0;
                    padding: 12px 16px;
                    margin: 8px 0;
                ">
                    <div style="font-size: 11px; color: #4A90D9; margin-bottom: 4px;">
                        Advisor {f'<span style="color:{source_color};">({source_label})</span>' if source_label else ''}:
                    </div>
                    <div style="color: #E8F4F8; line-height: 1.5;">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

        # Rating and bookmark buttons for the last message
        if (st.session_state.chat_messages and
            st.session_state.chat_messages[-1].get('role') == 'assistant' and
            'last_ai_conversation_id' in st.session_state):
            col_rate1, col_rate2, col_bookmark, col_spacer = st.columns([1, 1, 1, 3])

            # Only show rating for AI responses
            if st.session_state.chat_messages[-1].get('source') == 'ai':
                with col_rate1:
                    if st.button("👍 Helpful", key="rate_helpful"):
                        rate_conversation(db, st.session_state['last_ai_conversation_id'], is_helpful=True)
                        st.success("Thanks!")
                with col_rate2:
                    if st.button("👎 Not helpful", key="rate_not_helpful"):
                        rate_conversation(db, st.session_state['last_ai_conversation_id'], is_helpful=False)
                        st.info("Thanks for the feedback!")

            # Bookmark button for all responses
            with col_bookmark:
                if st.button("⭐ Save", key="bookmark_conv"):
                    new_status = toggle_favorite(db, st.session_state['last_ai_conversation_id'], current_user_id)
                    if new_status:
                        st.success("Saved to favorites!")
                    else:
                        st.info("Removed from favorites")

        st.markdown("---")

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
        if st.button(quick_questions[0][0], use_container_width=True, key="quick_q_0"):
            selected_question = quick_questions[0][1]
        if st.button(quick_questions[2][0], use_container_width=True, key="quick_q_2"):
            selected_question = quick_questions[2][1]

    with col2:
        if st.button(quick_questions[1][0], use_container_width=True, key="quick_q_1"):
            selected_question = quick_questions[1][1]
        if st.button(quick_questions[3][0], use_container_width=True, key="quick_q_3"):
            selected_question = quick_questions[3][1]

    # Custom question
    custom_q = st.text_area(
        "Or ask your own question:",
        value=selected_question or "",
        placeholder="e.g., What's my best Bear Trap lineup?",
        height=80,
        key="custom_question_input"
    )

    col_ask, col_force = st.columns([2, 1])
    with col_force:
        force_ai = st.checkbox("Force AI", value=False, help="Skip rules engine and use AI directly")

    # Show AI availability for forced AI
    if force_ai:
        if ai_mode == 'off':
            st.error("AI features are currently disabled by administrator.")
        elif not can_use_ai:
            st.warning(rate_message)

    with col_ask:
        ask_clicked = st.button("Ask", type="primary", use_container_width=True)

    if ask_clicked:
        if not custom_q:
            st.warning("Chief, please enter a question!")
        else:
            # Add user message to chat
            st.session_state.chat_messages.append({"role": "user", "content": custom_q})

            # Check if forcing AI and if rate limited
            use_ai = force_ai
            if use_ai:
                if ai_mode == 'off':
                    st.error("AI features are currently disabled.")
                    use_ai = False
                elif not can_use_ai:
                    st.warning(rate_message)
                    use_ai = False

            start_time = time.time()

            with st.spinner("Thinking..."):
                result = engine.ask(
                    profile, user_heroes, custom_q,
                    force_ai=use_ai
                )

            response_time_ms = int((time.time() - start_time) * 1000)

            source = result.get('source', 'unknown')
            answer_text = result.get('answer', 'Sorry, I could not process that request.')

            # Add assistant message to chat
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": answer_text,
                "source": source
            })

            # Threading logic: create a new thread for first message, continue existing thread for follow-ups
            is_new_thread = st.session_state.current_thread_id is None
            if is_new_thread:
                # Start a new thread with this conversation
                st.session_state.current_thread_id = create_thread_id()

            thread_title = generate_thread_title(custom_q) if is_new_thread else None

            # Log AI responses
            if source == 'ai' and current_user:
                record_ai_request(db, current_user)

                context_summary = f"FC{profile.furnace_level}, {len(user_heroes)} heroes, {profile.spending_profile}"
                conversation = log_ai_conversation(
                    db=db,
                    user_id=current_user.id,
                    question=custom_q,
                    answer=answer_text,
                    provider=ai_recommender.get_provider_name(),
                    model=ai_settings.openai_model if ai_recommender.get_provider_name() == 'openai' else ai_settings.anthropic_model,
                    context_summary=context_summary,
                    response_time_ms=response_time_ms,
                    source_page='ai_advisor',
                    question_type='custom' if not selected_question else 'quick',
                    routed_to=source,
                    thread_id=st.session_state.current_thread_id,
                    thread_title=thread_title
                )
                st.session_state['last_ai_conversation_id'] = conversation.id
            elif source == 'rules' and current_user:
                # Also log rules-based answers
                context_summary = f"FC{profile.furnace_level}, {len(user_heroes)} heroes, {profile.spending_profile}"
                conversation = log_ai_conversation(
                    db=db,
                    user_id=current_user.id,
                    question=custom_q,
                    answer=answer_text,
                    provider='rules',
                    model='rules_engine',
                    context_summary=context_summary,
                    response_time_ms=response_time_ms,
                    source_page='ai_advisor',
                    question_type='custom' if not selected_question else 'quick',
                    routed_to='rules',
                    thread_id=st.session_state.current_thread_id,
                    thread_title=thread_title
                )
                st.session_state['last_ai_conversation_id'] = conversation.id

            st.rerun()

# ============================================
# TAB 5: FAVORITES
# ============================================
with tab5:
    st.markdown("### Your Saved Conversations")
    st.markdown("Quick access to your bookmarked Q&A pairs.")

    # Get favorites
    favorites = []
    if current_user_id:
        favorites = get_favorite_conversations(db, current_user_id, limit=20)

    if favorites:
        for fav in favorites:
            # Time ago
            time_ago = ""
            if fav.created_at:
                delta = datetime.now() - fav.created_at
                if delta.days > 0:
                    time_ago = f"{delta.days}d ago"
                elif delta.seconds > 3600:
                    time_ago = f"{delta.seconds // 3600}h ago"
                else:
                    time_ago = f"{delta.seconds // 60}m ago"

            source_label = "Rules" if fav.routed_to == 'rules' else "AI" if fav.routed_to == 'ai' else ""

            with st.container():
                # Header with question preview and actions
                col_q, col_actions = st.columns([4, 1])
                with col_q:
                    q_preview = fav.question[:80] + "..." if len(fav.question) > 80 else fav.question
                    st.markdown(f"**Q:** {q_preview}")
                    st.caption(f"{time_ago} • {source_label}")

                with col_actions:
                    col_load, col_unfav = st.columns(2)
                    with col_load:
                        if st.button("Load", key=f"load_fav_{fav.id}"):
                            # If favorite has a thread, load the whole thread
                            if fav.thread_id:
                                thread_convos = get_thread_conversations(db, fav.thread_id, current_user_id)
                                st.session_state.chat_messages = []
                                for conv in thread_convos:
                                    st.session_state.chat_messages.append({"role": "user", "content": conv.question})
                                    st.session_state.chat_messages.append({
                                        "role": "assistant",
                                        "content": conv.answer,
                                        "source": conv.routed_to or "unknown"
                                    })
                                st.session_state.current_thread_id = fav.thread_id
                            else:
                                # Single conversation
                                st.session_state.chat_messages = [
                                    {"role": "user", "content": fav.question},
                                    {"role": "assistant", "content": fav.answer, "source": fav.routed_to or "unknown"}
                                ]
                                st.session_state.current_thread_id = None
                            st.session_state['last_ai_conversation_id'] = fav.id
                            # Switch to Ask tab
                            st.rerun()
                    with col_unfav:
                        if st.button("🗑️", key=f"unfav_{fav.id}", help="Remove from favorites"):
                            toggle_favorite(db, fav.id, current_user_id)
                            st.rerun()

                # Answer preview (expandable)
                with st.expander("View answer", expanded=False):
                    st.markdown(fav.answer)

                st.markdown("---")
    else:
        st.info("No saved conversations yet. Use the ⭐ Save button after getting an answer to bookmark it here.")

# ============================================
# FEEDBACK SECTION
# ============================================
st.markdown("---")
st.markdown("### Report an Issue or Request a Feature")

with st.expander("Send Feedback", expanded=False):
    # Get recent conversations for "bad recommendation" reporting
    recent_convos = []
    if current_user_id:
        recent_convos = get_recent_conversations(db, current_user_id, limit=5)

    render_feedback_form(db, current_user_id, recent_conversations=recent_convos)

# Close database
db.close()
