"""
AI Advisor Page - ChatGPT-style chat interface for WoS recommendations.
"""

import streamlit as st
import json
import html
from pathlib import Path
import sys
import time
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero, User, AIConversation
from database.auth import get_current_user_id
from database.ai_service import (
    get_ai_mode, check_rate_limit, record_ai_request,
    log_ai_conversation, rate_conversation, get_ai_settings,
    toggle_favorite, get_favorite_conversations,
    create_thread_id, generate_thread_title, get_user_threads,
    get_thread_conversations, get_standalone_conversations
)
from engine import RecommendationEngine, AIRecommender
from utils.toolbar import render_donate_message

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

# Get current user for rate limiting
current_user_id = get_current_user_id()
current_user = db.query(User).filter(User.id == current_user_id).first() if current_user_id else None

# AI settings
ai_mode = get_ai_mode(db)
ai_settings = get_ai_settings(db)

# Check rate limit status
if current_user:
    can_use_ai, rate_message, remaining = check_rate_limit(db, current_user)
else:
    can_use_ai, rate_message, remaining = False, "Please log in to use AI features", 0

# Initialize recommendation engine and AI recommender
engine = RecommendationEngine(PROJECT_ROOT / "data")
ai_recommender = AIRecommender()

# Page header
st.markdown("# AI Advisor")
st.markdown("Get personalized recommendations powered by AI.")

render_donate_message()

# Show AI access status
if current_user:
    user_ai_level = getattr(current_user, 'ai_access_level', None) or 'limited'

    if user_ai_level == 'off':
        st.error("**AI Access: Disabled** - AI features have been turned off for your account. Contact support if you believe this is an error.")
    elif user_ai_level == 'unlimited':
        st.success("**AI Access: Unlimited** - You have unlimited AI queries.")
    else:  # limited
        daily_limit = ai_settings.daily_limit_admin if current_user.role == 'admin' else ai_settings.daily_limit_free
        st.info(f"**AI Access: Limited** - AI queries are expensive to run, so we limit free accounts to {daily_limit} questions per day. {rate_message}")

st.markdown("---")

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'current_thread_id' not in st.session_state:
    st.session_state.current_thread_id = None
if 'feedback_message_id' not in st.session_state:
    st.session_state.feedback_message_id = None
if 'show_feedback_input' not in st.session_state:
    st.session_state.show_feedback_input = False
if 'favorites_expanded' not in st.session_state:
    st.session_state.favorites_expanded = False
if 'past_chats_expanded' not in st.session_state:
    st.session_state.past_chats_expanded = False
if 'rated_messages' not in st.session_state:
    st.session_state.rated_messages = set()

# ============================================
# FAVORITES & PAST CHATS EXPANDERS
# ============================================

# Get user's conversations
favorites = []
threads = []
standalone = []

if current_user_id:
    favorites = get_favorite_conversations(db, current_user_id, limit=20)
    threads = get_user_threads(db, current_user_id, limit=15)
    standalone = get_standalone_conversations(db, current_user_id, limit=10)

# Favorites section (only show if there are favorites)
if favorites:
    with st.expander(f"★ Favorites ({len(favorites)})", expanded=st.session_state.favorites_expanded):
        for fav in favorites:
            time_ago = ""
            if fav.created_at:
                delta = datetime.now() - fav.created_at
                if delta.days > 0:
                    time_ago = f"{delta.days}d ago"
                elif delta.seconds > 3600:
                    time_ago = f"{delta.seconds // 3600}h ago"
                else:
                    time_ago = f"{delta.seconds // 60}m ago"

            q_preview = fav.question[:50] + "..." if len(fav.question) > 50 else fav.question

            col_info, col_load, col_star = st.columns([5, 1, 1])
            with col_info:
                st.caption(f"{q_preview} • {time_ago}")
            with col_load:
                if st.button("Load", key=f"load_fav_{fav.id}"):
                    st.session_state.favorites_expanded = True
                    if fav.thread_id:
                        thread_convos = get_thread_conversations(db, fav.thread_id, current_user_id)
                        st.session_state.chat_messages = []
                        for conv in thread_convos:
                            st.session_state.chat_messages.append({"role": "user", "content": conv.question, "id": conv.id})
                            st.session_state.chat_messages.append({"role": "assistant", "content": conv.answer, "id": conv.id})
                        st.session_state.current_thread_id = fav.thread_id
                    else:
                        st.session_state.chat_messages = [
                            {"role": "user", "content": fav.question, "id": fav.id},
                            {"role": "assistant", "content": fav.answer, "id": fav.id}
                        ]
                        st.session_state.current_thread_id = None
                    st.rerun()
            with col_star:
                if st.button("★", key=f"unstar_{fav.id}", type="primary"):
                    st.session_state.favorites_expanded = True
                    toggle_favorite(db, fav.id, current_user_id)
                    st.rerun()

# Past Chats expander
total_past = len(threads) + len(standalone)
if total_past > 0:
    with st.expander(f"Past Chats ({total_past})", expanded=st.session_state.past_chats_expanded):
        # Threaded conversations
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

            title_preview = thread['title'][:40] + "..." if len(thread['title']) > 40 else thread['title']
            msg_count = thread['message_count']

            # Get first conversation in thread to check favorite status
            thread_convos = get_thread_conversations(db, thread['thread_id'], current_user_id)
            first_conv = thread_convos[0] if thread_convos else None
            is_fav = first_conv.is_favorite if first_conv else False

            col_info, col_load, col_star = st.columns([5, 1, 1])
            with col_info:
                st.caption(f"{title_preview} ({msg_count} msgs) • {time_ago}")
            with col_load:
                if st.button("Load", key=f"load_thread_{thread['thread_id']}"):
                    st.session_state.past_chats_expanded = True
                    st.session_state.chat_messages = []
                    for conv in thread_convos:
                        st.session_state.chat_messages.append({"role": "user", "content": conv.question, "id": conv.id})
                        st.session_state.chat_messages.append({"role": "assistant", "content": conv.answer, "id": conv.id})
                    st.session_state.current_thread_id = thread['thread_id']
                    st.rerun()
            with col_star:
                if first_conv:
                    star_label = "★" if is_fav else "☆"
                    btn_type = "primary" if is_fav else "secondary"
                    if st.button(star_label, key=f"star_thread_{thread['thread_id']}", type=btn_type):
                        st.session_state.past_chats_expanded = True
                        toggle_favorite(db, first_conv.id, current_user_id)
                        st.rerun()

        # Standalone conversations
        if standalone:
            if threads:
                st.markdown("---")
            for conv in standalone:
                time_ago = ""
                if conv.created_at:
                    delta = datetime.now() - conv.created_at
                    if delta.days > 0:
                        time_ago = f"{delta.days}d ago"
                    elif delta.seconds > 3600:
                        time_ago = f"{delta.seconds // 3600}h ago"
                    else:
                        time_ago = f"{delta.seconds // 60}m ago"

                q_preview = conv.question[:40] + "..." if len(conv.question) > 40 else conv.question

                # Query fresh from DB to get current favorite status
                fresh_conv = db.query(AIConversation).filter(AIConversation.id == conv.id).first()
                is_fav = fresh_conv.is_favorite if fresh_conv else False

                col_info, col_load, col_star = st.columns([5, 1, 1])
                with col_info:
                    st.caption(f"{q_preview} • {time_ago}")
                with col_load:
                    if st.button("Load", key=f"load_standalone_{conv.id}"):
                        st.session_state.past_chats_expanded = True
                        st.session_state.chat_messages = [
                            {"role": "user", "content": conv.question, "id": conv.id},
                            {"role": "assistant", "content": conv.answer, "id": conv.id}
                        ]
                        st.session_state.current_thread_id = None
                        st.rerun()
                with col_star:
                    star_label = "★" if is_fav else "☆"
                    btn_type = "primary" if is_fav else "secondary"
                    if st.button(star_label, key=f"star_standalone_{conv.id}", type=btn_type):
                        st.session_state.past_chats_expanded = True
                        toggle_favorite(db, conv.id, current_user_id)
                        st.rerun()

st.markdown("---")

# ============================================
# CHAT CONTAINER - Single scrollable box
# ============================================

# Check if current chat is favorited (used for favorite button)
current_is_fav = False
current_conv_id = None
if st.session_state.chat_messages and current_user_id:
    # Find the first assistant message with an ID
    for msg in st.session_state.chat_messages:
        if msg.get("role") == "assistant" and msg.get("id"):
            current_conv_id = msg.get("id")
            # Re-query the database to get current favorite status
            conv_check = db.query(AIConversation).filter(AIConversation.id == current_conv_id).first()
            if conv_check:
                current_is_fav = conv_check.is_favorite or False
            break

# New Chat and Favorite buttons (left-aligned)
col_new, col_fav, col_spacer = st.columns([1, 2, 5])
with col_new:
    if st.button("New Chat"):
        st.session_state.chat_messages = []
        st.session_state.current_thread_id = None
        st.session_state.show_feedback_input = False
        st.session_state.feedback_message_id = None
        st.session_state.rated_messages = set()
        st.rerun()
with col_fav:
    star_label = "★ Favorited" if current_is_fav else "☆ Mark as Favorite"
    star_disabled = current_conv_id is None
    btn_type = "primary" if current_is_fav else "secondary"
    if st.button(star_label, disabled=star_disabled, key="star_current_chat", type=btn_type):
        if current_conv_id:
            toggle_favorite(db, current_conv_id, current_user_id)
            st.rerun()

# Custom CSS for chat avatars and star buttons
st.markdown("""
    <style>
    /* Remove border from chat avatars */
    [data-testid="stChatMessageAvatarCustom"],
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    .stChatMessage > div:first-child {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Gold border for primary (starred) buttons */
    .stButton > button[kind="primary"] {
        border: 2px solid #FFD700 !important;
        box-shadow: 0 0 5px rgba(255, 215, 0, 0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Chat messages container
chat_container = st.container(height=400)

with chat_container:
    if not st.session_state.chat_messages and 'pending_question' not in st.session_state:
        # Empty state
        st.markdown("""
            <div style="text-align:center;padding:60px 20px;color:#888;">
                <div style="font-size:18px;margin-bottom:8px;">Ask me anything about Whiteout Survival</div>
                <div style="font-size:14px;">Lineups, hero upgrades, SvS prep, gear priorities, and more</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Render each message using Streamlit's chat components
        for i, msg in enumerate(st.session_state.chat_messages):
            msg_content = msg.get('content', '')
            msg_id = msg.get('id')
            msg_source = msg.get('source', '')

            if msg["role"] == "user":
                with st.chat_message("user", avatar="👨‍✈️"):
                    st.write(msg_content)
            else:
                with st.chat_message("assistant", avatar=str(PROJECT_ROOT / "assets" / "bear_paw.png")):
                    st.write(msg_content)
                    # Per-message feedback using st.feedback
                    if msg_id:
                        feedback = st.feedback("thumbs", key=f"feedback_{msg_id}")
                        if feedback is not None and msg_id not in st.session_state.rated_messages:
                            st.session_state.rated_messages.add(msg_id)
                            if feedback == 1:  # thumbs up
                                rate_conversation(db, msg_id, is_helpful=True)
                                st.toast("Thanks, Chief!")
                            elif feedback == 0:  # thumbs down
                                st.session_state.show_feedback_input = True
                                st.session_state.feedback_message_id = msg_id
                                st.rerun()

# Feedback input for thumbs down
if st.session_state.show_feedback_input and st.session_state.feedback_message_id:
    st.markdown("**Chief, what went wrong?**")
    feedback_text = st.text_area(
        "Your feedback helps us improve:",
        placeholder="Please be specific so we can improve the Furnace! e.g., 'The hero tier was wrong' or 'Didn't account for my FC level'",
        key="feedback_text_input",
        height=80,
        label_visibility="collapsed"
    )
    col_submit, col_cancel, col_space = st.columns([1, 1, 3])
    with col_submit:
        if st.button("Submit", type="primary"):
            if feedback_text:
                rate_conversation(db, st.session_state.feedback_message_id, is_helpful=False, user_feedback=feedback_text)
                st.session_state.show_feedback_input = False
                st.session_state.feedback_message_id = None
                st.toast("Thanks Chief, feedback logged!")
                st.rerun()
            else:
                st.warning("Please enter some feedback")
    with col_cancel:
        if st.button("Cancel"):
            st.session_state.show_feedback_input = False
            st.session_state.feedback_message_id = None
            st.rerun()

# ============================================
# MESSAGE INPUT
# ============================================

# Use a form for the input
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Message",
            placeholder="Ask about lineups, upgrades, SvS prep...",
            label_visibility="collapsed",
            key="chat_input_field"
        )
    with col_send:
        send_clicked = st.form_submit_button("Send", type="primary", )

# Process new message submission
if send_clicked and user_input:
    # Add user message immediately and set pending flag
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    st.session_state.pending_question = user_input
    st.rerun()  # Rerun to show the question immediately

# Process pending question (after rerun shows the question)
if st.session_state.get('pending_question'):
    pending_q = st.session_state.pending_question
    del st.session_state.pending_question  # Clear before processing

    start_time = time.time()

    with st.spinner("Thinking..."):
        try:
            # Call the engine (AI only)
            result = engine.ask(
                profile, user_heroes, pending_q,
                force_ai=True  # Always use AI, skip rules engine
            )

            response_time_ms = int((time.time() - start_time) * 1000)
            source = result.get('source', 'unknown')
            answer_text = result.get('answer', 'Sorry, I could not process that request.')

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            source = 'error'
            answer_text = "Sorry, an error occurred. Please try again."
            # Log error to database and send email notification
            from utils.error_logger import log_error
            error_id = log_error(
                e,
                page="AI Advisor",
                function="engine.ask",
                extra_context={"question": pending_q[:200]}
            )
            if error_id:
                answer_text += f" (Error #{error_id})"

    # Thread management
    is_new_thread = st.session_state.current_thread_id is None
    if is_new_thread:
        st.session_state.current_thread_id = create_thread_id()

    thread_title = generate_thread_title(pending_q) if is_new_thread else None

    # Log the conversation
    conversation_id = None
    if current_user:
        context_summary = f"FC{profile.furnace_level}, {len(user_heroes)} heroes, {profile.spending_profile}"

        if source == 'ai':
            record_ai_request(db, current_user)

        conversation = log_ai_conversation(
            db=db,
            user_id=current_user.id,
            question=pending_q,
            answer=answer_text,
            provider=ai_recommender.get_provider_name() if source == 'ai' else 'rules',
            model=ai_settings.openai_model if source == 'ai' and ai_recommender.get_provider_name() == 'openai' else 'rules_engine',
            context_summary=context_summary,
            response_time_ms=response_time_ms,
            source_page='ai_advisor',
            question_type='custom',
            routed_to=source,
            thread_id=st.session_state.current_thread_id,
            thread_title=thread_title
        )
        conversation_id = conversation.id

    # Add assistant message to chat with ID and source for feedback
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": answer_text,
        "id": conversation_id,
        "source": source
    })

    st.rerun()

# ============================================
# FOOTER
# ============================================

# Rate limit warning (subtle, at the bottom)
if ai_mode == 'on' and remaining is not None and remaining >= 0 and remaining < 5:
    st.caption(f"Note: {remaining} AI requests remaining today")

# Close database
db.close()
