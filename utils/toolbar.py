"""
Top Toolbar Component - Provides Donate and Feedback buttons in a professional top bar.
Renders at the top-right of pages for consistent access.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def render_toolbar(show_donate: bool = True, show_feedback: bool = True):
    """
    Render the top toolbar with Donate and Feedback buttons.

    Args:
        show_donate: Whether to show the Donate button
        show_feedback: Whether to show the Feedback button
    """
    # Use CSS to position the toolbar in the top-right
    st.markdown("""
    <style>
    /* Toolbar container styling */
    .toolbar-container {
        position: fixed;
        top: 60px;
        right: 20px;
        z-index: 999;
        display: flex;
        gap: 8px;
        align-items: center;
    }

    /* Toolbar button base styling */
    .toolbar-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.2s ease;
        cursor: pointer;
        border: none;
    }

    /* Donate button - warm accent */
    .toolbar-btn-donate {
        background: linear-gradient(135deg, #FF6B35, #FF8C42);
        color: white;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
    }

    .toolbar-btn-donate:hover {
        background: linear-gradient(135deg, #FF8C42, #FFA157);
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
        transform: translateY(-1px);
        color: white;
        text-decoration: none;
    }

    /* Feedback button - ice blue accent */
    .toolbar-btn-feedback {
        background: linear-gradient(135deg, #1A3A5C, #2E5A8C);
        color: #E8F4F8;
        border: 1px solid #4A90D9;
        box-shadow: 0 2px 8px rgba(74, 144, 217, 0.2);
    }

    .toolbar-btn-feedback:hover {
        background: linear-gradient(135deg, #2E5A8C, #3A7ABF);
        border-color: #7DD3FC;
        box-shadow: 0 4px 12px rgba(74, 144, 217, 0.3);
        transform: translateY(-1px);
        color: #E8F4F8;
        text-decoration: none;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .toolbar-container {
            top: auto;
            bottom: 20px;
            right: 16px;
        }

        .toolbar-btn {
            padding: 10px 12px;
            font-size: 12px;
        }

        .toolbar-btn span.btn-text {
            display: none;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Build toolbar HTML
    buttons_html = ""

    if show_donate:
        # Ko-fi link - placeholder URL, user will update
        buttons_html += '''
        <a href="https://ko-fi.com/randomchaoslabs" target="_blank" class="toolbar-btn toolbar-btn-donate" title="Support Bear's Den">
            <span>☕</span>
            <span class="btn-text">Donate</span>
        </a>
        '''

    if show_feedback:
        buttons_html += '''
        <a href="#feedback-section" class="toolbar-btn toolbar-btn-feedback" title="Send Feedback" onclick="document.getElementById('feedback-modal').style.display='block'; return false;">
            <span>💬</span>
            <span class="btn-text">Feedback</span>
        </a>
        '''

    if buttons_html:
        st.markdown(f'''
        <div class="toolbar-container">
            {buttons_html}
        </div>
        ''', unsafe_allow_html=True)


def render_feedback_modal():
    """
    Render the feedback modal that appears when clicking the Feedback button.
    Should be called once per page, typically at the end.
    """
    # Initialize feedback modal state
    if 'show_feedback_modal' not in st.session_state:
        st.session_state.show_feedback_modal = False

    # The actual feedback form is handled via Streamlit's dialog
    # This provides the CSS for the modal appearance
    st.markdown("""
    <style>
    /* Feedback modal overlay styling */
    .feedback-modal-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 1000;
        backdrop-filter: blur(4px);
    }

    .feedback-modal-content {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(180deg, #1A3A5C, #0D1F33);
        border: 1px solid #4A90D9;
        border-radius: 16px;
        padding: 24px;
        width: 90%;
        max-width: 500px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    .feedback-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(74, 144, 217, 0.3);
    }

    .feedback-modal-title {
        font-size: 20px;
        font-weight: bold;
        color: #E8F4F8;
    }

    .feedback-modal-close {
        background: none;
        border: none;
        color: #888;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }

    .feedback-modal-close:hover {
        color: #E8F4F8;
    }
    </style>
    """, unsafe_allow_html=True)


def render_feedback_form(db, current_user_id: int, recent_conversations: list = None):
    """
    Render the feedback submission form.

    Args:
        db: Database session
        current_user_id: Current user's ID
        recent_conversations: List of recent AI conversations for "bad recommendation" reporting
    """
    from database.models import Feedback

    st.markdown("### Send Feedback")
    st.markdown("Help us improve Bear's Den!")

    # Feedback type selection
    feedback_type = st.radio(
        "What type of feedback?",
        ["Feature Request", "Report Issue", "Report Bad Recommendation", "Other"],
        horizontal=True,
        key="toolbar_feedback_type"
    )

    # Category mapping
    category_map = {
        "Feature Request": "feature",
        "Report Issue": "bug",
        "Report Bad Recommendation": "data_error",
        "Other": "other"
    }

    # For bad recommendation, show recent conversations
    selected_conversation_id = None
    if feedback_type == "Report Bad Recommendation":
        st.markdown("---")
        st.markdown("**Which recommendation was wrong?**")

        if recent_conversations and len(recent_conversations) > 0:
            # Show last few conversations to select from
            options = ["Select a recent recommendation..."]
            conv_map = {}

            for conv in recent_conversations[:5]:  # Last 5 conversations
                # Truncate question for display
                q_preview = conv.question[:60] + "..." if len(conv.question) > 60 else conv.question
                option_text = f"{q_preview}"
                options.append(option_text)
                conv_map[option_text] = conv.id

            options.append("Other (describe below)")

            selected_option = st.selectbox(
                "Recent AI responses",
                options,
                key="bad_rec_selector",
                label_visibility="collapsed"
            )

            if selected_option in conv_map:
                selected_conversation_id = conv_map[selected_option]
                # Show the full Q&A for context
                selected_conv = next((c for c in recent_conversations if c.id == selected_conversation_id), None)
                if selected_conv:
                    with st.expander("View full conversation", expanded=True):
                        st.markdown(f"**Your question:** {selected_conv.question}")
                        st.markdown(f"**AI answer:** {selected_conv.answer[:300]}..." if len(selected_conv.answer) > 300 else f"**AI answer:** {selected_conv.answer}")
        else:
            st.info("No recent AI conversations found. Describe the issue below.")

    # Page context (optional)
    page_options = ["Not specific", "Hero Tracker", "Chief Gear", "AI Advisor", "Lineups", "Packs", "Guides", "Settings"]
    selected_page = st.selectbox(
        "Related page (optional)",
        page_options,
        key="toolbar_feedback_page"
    )

    # Description
    placeholder_text = {
        "Feature Request": "Describe the feature you'd like to see...",
        "Report Issue": "Describe what went wrong...",
        "Report Bad Recommendation": "What was wrong with the recommendation? What should it have said?",
        "Other": "What's on your mind?"
    }

    description = st.text_area(
        "Details",
        placeholder=placeholder_text.get(feedback_type, ""),
        max_chars=2000,
        key="toolbar_feedback_desc"
    )

    # Submit button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Submit", type="primary", key="toolbar_submit_feedback", use_container_width=True):
            if description and len(description.strip()) >= 10:
                try:
                    # Build feedback with optional conversation reference
                    new_feedback = Feedback(
                        user_id=current_user_id,
                        category=category_map.get(feedback_type, "other"),
                        page=selected_page if selected_page != "Not specific" else None,
                        description=description.strip()
                    )

                    # If we have a conversation reference, add it to the description
                    if selected_conversation_id:
                        new_feedback.description = f"[AI Conversation #{selected_conversation_id}] {new_feedback.description}"

                    db.add(new_feedback)
                    db.commit()

                    st.success("Thanks for the feedback, Chief! We'll review it soon.")
                    st.balloons()

                except Exception as e:
                    st.error("Failed to submit. Please try again.")
                    db.rollback()
            else:
                st.warning("Please provide more details (at least 10 characters)")


def render_donate_message():
    """
    Render a donate message for the AI Advisor page.
    WoS-themed message encouraging support.
    """
    import base64

    # Load frost star image
    frost_star_path = PROJECT_ROOT / "assets" / "items" / "frost_star.png"
    frost_star_b64 = ""
    if frost_star_path.exists():
        with open(frost_star_path, "rb") as f:
            frost_star_b64 = base64.b64encode(f.read()).decode()

    frost_star_img = f'<img src="data:image/png;base64,{frost_star_b64}" style="width:32px;height:32px;">' if frost_star_b64 else "⭐"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(211, 84, 0, 0.15), rgba(230, 126, 34, 0.1));
        border: 1px solid rgba(211, 84, 0, 0.3);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 16px 0;
        display: flex;
        align-items: center;
        gap: 16px;
    ">
        <div style="font-size: 32px;">{frost_star_img}</div>
        <div style="flex: 1;">
            <div style="color: #E8F4F8; font-size: 14px; font-weight: 500; margin-bottom: 4px;">
                Chief, running this Settlement costs resources!
            </div>
            <div style="color: #B8D4E8; font-size: 13px;">
                If Bear's Den has helped your journey, consider fueling us with some Frost Stars.
                Every donation keeps the fires burning and features coming!
            </div>
        </div>
        <a href="https://ko-fi.com/randomchaoslabs" target="_blank" style="
            background: linear-gradient(135deg, #D35400, #E67E22);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            white-space: nowrap;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        ">
            Support Us
        </a>
    </div>
    """, unsafe_allow_html=True)
