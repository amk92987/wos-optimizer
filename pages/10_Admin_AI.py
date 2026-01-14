"""
Admin AI Management - Control AI settings, view conversations, curate training data.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin, get_current_user_id
from database.models import AIConversation, AISettings
from database.ai_service import (
    get_ai_settings, set_ai_mode, get_ai_stats,
    curate_conversation, get_training_data
)

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# AI Management")

db = get_db()
stats = get_ai_stats(db)
settings = get_ai_settings(db)

# Mode selector with visual indicator
st.markdown("### AI Mode")

mode_colors = {
    'off': '#E74C3C',
    'on': '#2ECC71',
    'unlimited': '#9B59B6'
}
mode_icons = {
    'off': '🔴',
    'on': '🟢',
    'unlimited': '🟣'
}

current_mode = stats['mode']
st.markdown(f"""
<div style="background: {mode_colors[current_mode]}22; border: 2px solid {mode_colors[current_mode]};
            border-radius: 12px; padding: 20px; margin-bottom: 20px;">
    <div style="font-size: 24px; font-weight: bold; color: {mode_colors[current_mode]};">
        {mode_icons[current_mode]} AI is {current_mode.upper()}
    </div>
    <div style="color: #B8D4E8; margin-top: 8px;">
        {
            'AI features are completely disabled for all users.' if current_mode == 'off' else
            f'AI is enabled with rate limits ({stats["daily_limit_free"]} requests/day for users).' if current_mode == 'on' else
            'AI is enabled with no rate limits (use with caution).'
        }
    </div>
</div>
""", unsafe_allow_html=True)

# Mode toggle buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔴 Turn OFF", use_container_width=True,
                 disabled=(current_mode == 'off'),
                 help="Disable AI for all users"):
        set_ai_mode(db, 'off', get_current_user_id())
        st.rerun()

with col2:
    if st.button("🟢 Turn ON (Limited)", use_container_width=True,
                 disabled=(current_mode == 'on'),
                 help="Enable AI with rate limits"):
        set_ai_mode(db, 'on', get_current_user_id())
        st.rerun()

with col3:
    if st.button("🟣 UNLIMITED", use_container_width=True,
                 disabled=(current_mode == 'unlimited'),
                 help="Enable AI with no rate limits"):
        set_ai_mode(db, 'unlimited', get_current_user_id())
        st.rerun()

st.markdown("---")

# Stats overview
st.markdown("### Usage Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Requests", stats['total_requests'])
with col2:
    st.metric("Total Tokens", f"{stats['total_tokens']:,}" if stats['total_tokens'] else "0")
with col3:
    st.metric("Conversations", stats['total_conversations'])
with col4:
    st.metric("Avg Rating", stats['average_rating'] or "N/A")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Good Examples", stats['good_examples'])
with col2:
    st.metric("Bad Examples", stats['bad_examples'])
with col3:
    st.metric("Helpful", stats['helpful_count'])
with col4:
    st.metric("Not Helpful", stats['unhelpful_count'])

st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Settings", "Conversations", "Training Data", "Export"])

with tab1:
    st.markdown("### Rate Limit Settings")

    with st.form("rate_limits"):
        col1, col2 = st.columns(2)

        with col1:
            new_daily_limit = st.number_input(
                "Daily Limit (Free Users)",
                min_value=1, max_value=100,
                value=settings.daily_limit_free,
                help="Max AI requests per day for regular users"
            )

            new_cooldown = st.number_input(
                "Cooldown (seconds)",
                min_value=0, max_value=300,
                value=settings.cooldown_seconds,
                help="Minimum seconds between requests"
            )

        with col2:
            new_admin_limit = st.number_input(
                "Daily Limit (Admins)",
                min_value=1, max_value=10000,
                value=settings.daily_limit_admin,
                help="Max AI requests per day for admins"
            )

        st.markdown("### Provider Settings")

        col1, col2 = st.columns(2)

        with col1:
            new_provider = st.selectbox(
                "Primary Provider",
                options=['openai', 'anthropic'],
                index=0 if settings.primary_provider == 'openai' else 1
            )

            new_openai_model = st.text_input(
                "OpenAI Model",
                value=settings.openai_model,
                help="e.g., gpt-4o-mini, gpt-4o"
            )

        with col2:
            new_fallback = st.selectbox(
                "Fallback Provider",
                options=[None, 'openai', 'anthropic'],
                index=0 if not settings.fallback_provider else
                      (1 if settings.fallback_provider == 'openai' else 2)
            )

            new_anthropic_model = st.text_input(
                "Anthropic Model",
                value=settings.anthropic_model,
                help="e.g., claude-sonnet-4-20250514, claude-3-haiku-20240307"
            )

        if st.form_submit_button("Save Settings", use_container_width=True):
            settings.daily_limit_free = new_daily_limit
            settings.daily_limit_admin = new_admin_limit
            settings.cooldown_seconds = new_cooldown
            settings.primary_provider = new_provider
            settings.fallback_provider = new_fallback
            settings.openai_model = new_openai_model
            settings.anthropic_model = new_anthropic_model
            settings.updated_at = datetime.utcnow()
            settings.updated_by = get_current_user_id()
            db.commit()
            st.success("Settings saved!")
            st.rerun()

with tab2:
    st.markdown("### Recent Conversations")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_rating = st.selectbox(
            "Filter by Rating",
            options=["All", "Rated", "Unrated", "Helpful", "Not Helpful"]
        )

    with col2:
        filter_curation = st.selectbox(
            "Filter by Curation",
            options=["All", "Good Examples", "Bad Examples", "Not Curated"]
        )

    with col3:
        limit = st.number_input("Show", min_value=10, max_value=200, value=50)

    # Build query
    query = db.query(AIConversation).order_by(AIConversation.created_at.desc())

    if filter_rating == "Rated":
        query = query.filter(AIConversation.rating != None)
    elif filter_rating == "Unrated":
        query = query.filter(AIConversation.rating == None)
    elif filter_rating == "Helpful":
        query = query.filter(AIConversation.is_helpful == True)
    elif filter_rating == "Not Helpful":
        query = query.filter(AIConversation.is_helpful == False)

    if filter_curation == "Good Examples":
        query = query.filter(AIConversation.is_good_example == True)
    elif filter_curation == "Bad Examples":
        query = query.filter(AIConversation.is_bad_example == True)
    elif filter_curation == "Not Curated":
        query = query.filter(
            AIConversation.is_good_example == False,
            AIConversation.is_bad_example == False
        )

    conversations = query.limit(limit).all()

    st.caption(f"Showing {len(conversations)} conversations")

    for conv in conversations:
        # Determine border color based on curation
        if conv.is_good_example:
            border_color = "#2ECC71"
            badge = "GOOD"
        elif conv.is_bad_example:
            border_color = "#E74C3C"
            badge = "BAD"
        else:
            border_color = "rgba(74, 144, 217, 0.3)"
            badge = None

        with st.expander(
            f"{'✅' if conv.is_good_example else '❌' if conv.is_bad_example else '💬'} "
            f"{conv.question[:60]}{'...' if len(conv.question) > 60 else ''} "
            f"({conv.created_at.strftime('%m/%d %H:%M')})"
        ):
            # Question
            st.markdown("**Question:**")
            st.markdown(f"> {conv.question}")

            # Answer
            st.markdown("**Answer:**")
            st.markdown(conv.answer)

            # Metadata
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                # Source indicator (AI vs Engine)
                source = conv.routed_to or conv.provider
                if source == 'ai':
                    st.caption("Source: 🤖 AI")
                elif source == 'rules':
                    st.caption("Source: ⚙️ Engine")
                else:
                    st.caption(f"Source: {source}")
            with col2:
                st.caption(f"Provider: {conv.provider}")
            with col3:
                st.caption(f"Model: {conv.model}")
            with col4:
                if conv.rating:
                    st.caption(f"Rating: {'⭐' * conv.rating}")
                else:
                    st.caption("Rating: -")
            with col5:
                if conv.is_helpful is True:
                    st.caption("Helpful: 👍")
                elif conv.is_helpful is False:
                    st.caption("Helpful: 👎")
                else:
                    st.caption("Helpful: -")

            # User feedback
            if conv.user_feedback:
                st.markdown(f"**User Feedback:** {conv.user_feedback}")

            # Admin notes
            if conv.admin_notes:
                st.markdown(f"**Admin Notes:** {conv.admin_notes}")

            st.markdown("---")

            # Curation buttons
            st.markdown("**Curate for Training:**")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Good Example", key=f"good_{conv.id}",
                           disabled=conv.is_good_example):
                    curate_conversation(db, conv.id, is_good_example=True, is_bad_example=False)
                    st.rerun()

            with col2:
                if st.button("❌ Bad Example", key=f"bad_{conv.id}",
                           disabled=conv.is_bad_example):
                    curate_conversation(db, conv.id, is_good_example=False, is_bad_example=True)
                    st.rerun()

            with col3:
                if st.button("🔄 Reset", key=f"reset_{conv.id}"):
                    curate_conversation(db, conv.id, is_good_example=False, is_bad_example=False)
                    st.rerun()

            # Admin notes input
            new_notes = st.text_input(
                "Admin Notes",
                value=conv.admin_notes or "",
                key=f"notes_{conv.id}",
                placeholder="Add notes about this conversation..."
            )
            if new_notes != (conv.admin_notes or ""):
                if st.button("Save Notes", key=f"save_notes_{conv.id}"):
                    curate_conversation(db, conv.id, admin_notes=new_notes)
                    st.success("Notes saved!")

with tab3:
    st.markdown("### Training Data Preview")

    st.info("""
    **Good examples** are conversations that can be used to fine-tune an AI model.
    Mark helpful, accurate conversations as good examples in the Conversations tab.
    """)

    # Get training data
    training_data = get_training_data(db, good_only=True)

    st.metric("Good Examples Available", len(training_data))

    if training_data:
        st.markdown("### Sample Training Pairs")

        for i, item in enumerate(training_data[:10]):
            with st.expander(f"Example {i+1}: {item['question'][:50]}..."):
                st.markdown("**Question:**")
                st.code(item['question'], language=None)

                st.markdown("**Answer:**")
                st.code(item['answer'], language=None)

                if item['admin_notes']:
                    st.markdown(f"**Notes:** {item['admin_notes']}")

with tab4:
    st.markdown("### Export Training Data")

    st.markdown("""
    Export your curated training data for fine-tuning AI models.

    **Formats:**
    - **JSON Lines**: Standard format for OpenAI fine-tuning
    - **CSV**: For analysis or custom processing
    """)

    include_context = st.checkbox("Include context summary", value=True)
    include_all = st.checkbox("Include all (not just good examples)", value=False)

    training_data = get_training_data(db, good_only=not include_all)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export as JSONL", use_container_width=True):
            if not training_data:
                st.warning("No training data to export. Mark some conversations as good examples first.")
            else:
                # Format for OpenAI fine-tuning
                jsonl_lines = []
                for item in training_data:
                    entry = {
                        "messages": [
                            {"role": "user", "content": item['question']},
                            {"role": "assistant", "content": item['answer']}
                        ]
                    }
                    jsonl_lines.append(json.dumps(entry))

                jsonl_content = "\n".join(jsonl_lines)

                st.download_button(
                    label="Download JSONL",
                    data=jsonl_content,
                    file_name=f"wos_training_data_{datetime.now().strftime('%Y%m%d')}.jsonl",
                    mime="application/jsonl"
                )
                st.success(f"Prepared {len(training_data)} training examples")

    with col2:
        if st.button("Export as CSV", use_container_width=True):
            if not training_data:
                st.warning("No training data to export. Mark some conversations as good examples first.")
            else:
                import pandas as pd

                df = pd.DataFrame(training_data)
                csv_content = df.to_csv(index=False)

                st.download_button(
                    label="Download CSV",
                    data=csv_content,
                    file_name=f"wos_training_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                st.success(f"Prepared {len(training_data)} training examples")

    st.markdown("---")
    st.markdown("### Fine-Tuning Guide")

    st.markdown("""
    **To fine-tune GPT-4o-mini:**

    1. Export your training data as JSONL
    2. Go to [OpenAI Fine-tuning](https://platform.openai.com/finetune)
    3. Upload your JSONL file
    4. Select `gpt-4o-mini-2024-07-18` as the base model
    5. Start training (~$25 for 500 examples)

    **Recommended:** Wait until you have 500+ good examples for best results.

    **For self-hosted models (Ollama):**

    1. Export as CSV or JSONL
    2. Convert to your model's format
    3. Use tools like `llama.cpp` or `axolotl` for fine-tuning
    """)

db.close()
