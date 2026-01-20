"""
Admin Inbox - Unified view for Feedback, Errors, and future Conversations.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys
import html

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin, get_current_user_id
from database.models import Feedback, User, ErrorLog, MessageThread, Message
from database.messaging_service import (
    get_admin_conversations, create_message_thread, add_message_to_thread,
    has_unread_user_replies, mark_user_replies_read, get_thread_messages,
    close_thread, reopen_thread, get_admin_unread_count,
    mark_message_unread, mark_message_read
)

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 📬 Inbox")

db = get_db()

# Get unread counts for tab labels
admin_unread_convos = get_admin_unread_count(db)
convo_badge = f" ({admin_unread_convos})" if admin_unread_convos > 0 else ""

# Use session state to preserve tab selection across reruns
if 'admin_inbox_tab' not in st.session_state:
    st.session_state.admin_inbox_tab = "Feedback"

# Tab options
tab_options = ["Feedback", "Errors", "Conversations"]
tab_labels = {
    "Feedback": "💬 Feedback",
    "Errors": "🚨 Errors",
    "Conversations": f"📨 Conversations{convo_badge}"
}

# Tab selection using radio buttons (preserves state on rerun)
selected_admin_tab = st.radio(
    "Select tab",
    tab_options,
    format_func=lambda x: tab_labels[x],
    horizontal=True,
    label_visibility="collapsed",
    key="admin_inbox_tab_selector",
    index=tab_options.index(st.session_state.admin_inbox_tab)
)
st.session_state.admin_inbox_tab = selected_admin_tab

st.markdown("---")

# ============================================
# FEEDBACK TAB
# ============================================
if selected_admin_tab == "Feedback":
    # Stats row
    total = db.query(Feedback).count()
    new_count = db.query(Feedback).filter(Feedback.status == 'new').count()
    pending_fix = db.query(Feedback).filter(Feedback.status == 'pending_fix').count()
    pending_update = db.query(Feedback).filter(Feedback.status == 'pending_update').count()
    completed = db.query(Feedback).filter(Feedback.status == 'completed').count()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("New", new_count)
    with col2:
        st.metric("Pending Fix", pending_fix)
    with col3:
        st.metric("Pending Update", pending_update)
    with col4:
        st.metric("Completed", completed)
    with col5:
        st.metric("Total", total)

    st.markdown("---")

    # Tabs for different views
    tab_bugs, tab_features, tab_pending_fix, tab_pending_update, tab_completed, tab_archive = st.tabs([
        f"🐛 New Bugs ({db.query(Feedback).filter(Feedback.category == 'bug', Feedback.status == 'new').count()})",
        f"✨ New Features ({db.query(Feedback).filter(Feedback.category == 'feature', Feedback.status == 'new').count()})",
        f"🔧 Pending Fix ({pending_fix})",
        f"📝 Pending Update ({pending_update})",
        f"✅ Completed ({completed})",
        f"📦 Archive ({db.query(Feedback).filter(Feedback.status == 'archive').count()})"
    ])

    # Status styles
    status_styles = {
        "new": ("🆕", "#3498DB"),
        "pending_fix": ("🔧", "#E74C3C"),
        "pending_update": ("📝", "#9B59B6"),
        "completed": ("✅", "#2ECC71"),
        "archive": ("📦", "#95A5A6"),
    }


    def render_feedback_item(item, show_category=True, key_prefix=""):
        """Render a single feedback item with actions."""
        user = db.query(User).filter(User.id == item.user_id).first() if item.user_id else None
        k = f"{key_prefix}_{item.id}"  # Unique key prefix for this context
        username = html.escape(user.username if user else "Anonymous")
        description = html.escape(item.description or "")
        time_str = item.created_at.strftime("%m/%d/%y %I:%M %p")

        stat_icon, stat_color = status_styles.get(item.status, ("❓", "#888"))

        # Category colors
        cat_colors = {"bug": "#E74C3C", "feature": "#9B59B6", "data_error": "#F1C40F", "other": "#3498DB"}
        cat_color = cat_colors.get(item.category, "#888")
        cat_icons = {"bug": "🐛", "feature": "✨", "data_error": "📊", "other": "💬"}
        cat_icon = cat_icons.get(item.category, "💬")

        with st.container():
            # Header row
            header_col1, header_col2 = st.columns([4, 1])
            with header_col1:
                cat_display = f"{cat_icon} **{item.category.title()}**" if show_category else ""
                page_display = f" · {item.page}" if item.page else ""
                st.markdown(f"{cat_display}{page_display}")
            with header_col2:
                st.markdown(f"<span style='background: {stat_color}22; color: {stat_color}; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{stat_icon} {item.status.replace('_', ' ').title()}</span>", unsafe_allow_html=True)

            # Description
            st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 4px; border-left: 3px solid {cat_color}; margin: 8px 0;'>{description}</div>", unsafe_allow_html=True)

            # Footer
            st.caption(f"From: {username} · {time_str}")

            # Action buttons based on current status
            if item.status == 'new':
                cols = st.columns([1, 1, 1, 1, 4])
                with cols[0]:
                    if item.category == 'bug':
                        if st.button("🔧 To Fix", key=f"tofix_{k}", use_container_width=True):
                            item.status = 'pending_fix'
                            db.commit()
                            st.rerun()
                    else:
                        if st.button("📝 To Update", key=f"toupdate_{k}", use_container_width=True):
                            item.status = 'pending_update'
                            db.commit()
                            st.rerun()
                with cols[1]:
                    if st.button("📦 Archive", key=f"archive_{k}", use_container_width=True):
                        item.status = 'archive'
                        db.commit()
                        st.rerun()
                with cols[2]:
                    if st.button("🗑️", key=f"del_{k}"):
                        st.session_state[f"confirm_del_{k}"] = True

            elif item.status in ['pending_fix', 'pending_update']:
                # No Complete button - Claude marks as completed via /wos-feedback skill
                cols = st.columns([1, 1, 6])
                with cols[0]:
                    if st.button("📦 Archive", key=f"archive_{k}", use_container_width=True):
                        item.status = 'archive'
                        db.commit()
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️", key=f"del_{k}"):
                        st.session_state[f"confirm_del_{k}"] = True

            elif item.status == 'completed':
                cols = st.columns([1, 1, 6])
                with cols[0]:
                    if st.button("📦 Archive", key=f"archive_{k}", use_container_width=True):
                        item.status = 'archive'
                        db.commit()
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️", key=f"del_{k}"):
                        st.session_state[f"confirm_del_{k}"] = True

            elif item.status == 'archive':
                cols = st.columns([1, 1, 6])
                with cols[0]:
                    if st.button("🔄 Restore", key=f"restore_{k}", use_container_width=True):
                        item.status = 'new'
                        db.commit()
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️", key=f"del_{k}"):
                        st.session_state[f"confirm_del_{k}"] = True

            # Delete confirmation
            if st.session_state.get(f"confirm_del_{k}"):
                st.warning("Permanently delete this feedback?")
                del_cols = st.columns([1, 1, 4])
                with del_cols[0]:
                    if st.button("Yes, Delete", key=f"confirm_delete_{k}", type="primary"):
                        db.delete(item)
                        db.commit()
                        st.session_state[f"confirm_del_{k}"] = False
                        st.rerun()
                with del_cols[1]:
                    if st.button("Cancel", key=f"cancel_del_{k}"):
                        st.session_state[f"confirm_del_{k}"] = False
                        st.rerun()

            st.markdown("---")


    # New Bugs tab
    with tab_bugs:
        new_bugs = db.query(Feedback).filter(
            Feedback.category == 'bug',
            Feedback.status == 'new'
        ).order_by(Feedback.created_at.desc()).all()

        if not new_bugs:
            st.info("No new bugs to review.")
        else:
            for item in new_bugs:
                render_feedback_item(item, show_category=False, key_prefix="bugs")


    # New Features tab
    with tab_features:
        new_features = db.query(Feedback).filter(
            Feedback.category == 'feature',
            Feedback.status == 'new'
        ).order_by(Feedback.created_at.desc()).all()

        if not new_features:
            st.info("No new feature requests to review.")
        else:
            for item in new_features:
                render_feedback_item(item, show_category=False, key_prefix="feat")


    # Pending Fix tab
    with tab_pending_fix:
        pending_fix_items = db.query(Feedback).filter(
            Feedback.status == 'pending_fix'
        ).order_by(Feedback.created_at.desc()).all()

        if not pending_fix_items:
            st.info("No bugs pending fix.")
        else:
            st.caption("Run `/wos-feedback` to review and implement fixes")
            for item in pending_fix_items:
                render_feedback_item(item, show_category=True, key_prefix="pfix")


    # Pending Update tab
    with tab_pending_update:
        pending_update_items = db.query(Feedback).filter(
            Feedback.status == 'pending_update'
        ).order_by(Feedback.created_at.desc()).all()

        if not pending_update_items:
            st.info("No features pending update.")
        else:
            st.caption("Run `/wos-feedback` to review and implement features")
            for item in pending_update_items:
                render_feedback_item(item, show_category=True, key_prefix="pupd")


    # Completed tab
    with tab_completed:
        completed_items = db.query(Feedback).filter(
            Feedback.status == 'completed'
        ).order_by(Feedback.created_at.desc()).all()

        if not completed_items:
            st.info("No completed items.")
        else:
            if st.button("📦 Archive All Completed", key="archive_all_feedback"):
                db.query(Feedback).filter(Feedback.status == 'completed').update({'status': 'archive'})
                db.commit()
                st.rerun()

            for item in completed_items:
                render_feedback_item(item, show_category=True, key_prefix="done")


    # Archive tab
    with tab_archive:
        archived = db.query(Feedback).filter(
            Feedback.status == 'archive'
        ).order_by(Feedback.created_at.desc()).all()

        if not archived:
            st.info("Archive is empty.")
        else:
            if st.button("🗑️ Empty Archive (Delete All)", type="secondary", key="empty_feedback_archive"):
                st.session_state.confirm_empty_feedback_archive = True

            if st.session_state.get('confirm_empty_feedback_archive'):
                st.warning("This will permanently delete all archived feedback!")
                cols = st.columns([1, 1, 4])
                with cols[0]:
                    if st.button("Yes, Delete All", type="primary", key="confirm_empty_feedback"):
                        db.query(Feedback).filter(Feedback.status == 'archive').delete()
                        db.commit()
                        st.session_state.confirm_empty_feedback_archive = False
                        st.rerun()
                with cols[1]:
                    if st.button("Cancel", key="cancel_empty_feedback"):
                        st.session_state.confirm_empty_feedback_archive = False
                        st.rerun()

            for item in archived:
                render_feedback_item(item, show_category=True, key_prefix="arch")


# ============================================
# ERRORS TAB
# ============================================
if selected_admin_tab == "Errors":
    # Stats row
    yesterday = datetime.utcnow() - timedelta(hours=24)
    error_new = db.query(ErrorLog).filter(ErrorLog.status == 'new').count()
    error_reviewed = db.query(ErrorLog).filter(ErrorLog.status == 'reviewed').count()
    error_fixed = db.query(ErrorLog).filter(ErrorLog.status == 'fixed').count()
    error_ignored = db.query(ErrorLog).filter(ErrorLog.status == 'ignored').count()
    error_last_24h = db.query(ErrorLog).filter(ErrorLog.created_at >= yesterday).count()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("New", error_new)
    with col2:
        st.metric("Reviewed", error_reviewed)
    with col3:
        st.metric("Fixed", error_fixed)
    with col4:
        st.metric("Ignored", error_ignored)
    with col5:
        st.metric("Last 24h", error_last_24h)

    st.markdown("---")

    # Error status styles
    error_status_styles = {
        "new": ("🆕", "#E74C3C"),
        "reviewed": ("👁️", "#F39C12"),
        "fixed": ("✅", "#2ECC71"),
        "ignored": ("🙈", "#95A5A6"),
    }

    # Sub-tabs for error statuses
    err_tab_new, err_tab_reviewed, err_tab_fixed, err_tab_ignored = st.tabs([
        f"🆕 New ({error_new})",
        f"👁️ Reviewed ({error_reviewed})",
        f"✅ Fixed ({error_fixed})",
        f"🙈 Ignored ({error_ignored})"
    ])

    def render_error_item(error, key_prefix=""):
        """Render a single error item with actions."""
        k = f"{key_prefix}_{error.id}"
        user = db.query(User).filter(User.id == error.user_id).first() if error.user_id else None
        username = html.escape(user.username if user else "Anonymous")
        time_str = error.created_at.strftime("%m/%d/%y %I:%M %p")

        stat_icon, stat_color = error_status_styles.get(error.status, ("❓", "#888"))

        with st.container():
            # Header row
            header_col1, header_col2 = st.columns([4, 1])
            with header_col1:
                st.markdown(f"**{error.error_type}** · {error.page or 'Unknown page'}")
            with header_col2:
                st.markdown(f"<span style='background: {stat_color}22; color: {stat_color}; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{stat_icon} {error.status.title()}</span>", unsafe_allow_html=True)

            # Error message
            error_msg = html.escape(error.error_message or "")[:500]
            st.markdown(f"<div style='background: rgba(231, 76, 60, 0.1); padding: 12px; border-radius: 4px; border-left: 3px solid #E74C3C; margin: 8px 0; font-family: monospace; font-size: 13px;'>{error_msg}</div>", unsafe_allow_html=True)

            # Stack trace in expander
            with st.expander("View Stack Trace"):
                st.code(error.stack_trace or "No stack trace available", language="python")

                if error.extra_context:
                    st.markdown("**Extra Context:**")
                    st.json(error.extra_context)

            # Footer
            env_badge = f"<span style='background: {'#2ECC71' if error.environment == 'production' else '#3498DB'}22; color: {'#2ECC71' if error.environment == 'production' else '#3498DB'}; padding: 1px 6px; border-radius: 3px; font-size: 11px;'>{error.environment}</span>"
            st.caption(f"User: {username} · {time_str} · {env_badge}", unsafe_allow_html=True)

            # Fix notes if present
            if error.fix_notes:
                st.info(f"**Fix Notes:** {error.fix_notes}")

            # Action buttons based on current status
            if error.status == 'new':
                cols = st.columns([1, 1, 1, 5])
                with cols[0]:
                    if st.button("👁️ Reviewed", key=f"reviewed_{k}", use_container_width=True):
                        error.status = 'reviewed'
                        error.reviewed_by = get_current_user_id()
                        error.reviewed_at = datetime.utcnow()
                        db.commit()
                        st.rerun()
                with cols[1]:
                    if st.button("✅ Fixed", key=f"fixed_{k}", use_container_width=True):
                        error.status = 'fixed'
                        error.reviewed_by = get_current_user_id()
                        error.reviewed_at = datetime.utcnow()
                        db.commit()
                        st.rerun()
                with cols[2]:
                    if st.button("🙈 Ignore", key=f"ignore_{k}", use_container_width=True):
                        error.status = 'ignored'
                        error.reviewed_by = get_current_user_id()
                        error.reviewed_at = datetime.utcnow()
                        db.commit()
                        st.rerun()

            elif error.status == 'reviewed':
                cols = st.columns([1, 1, 1, 5])
                with cols[0]:
                    if st.button("✅ Fixed", key=f"fixed_{k}", use_container_width=True):
                        error.status = 'fixed'
                        error.reviewed_by = get_current_user_id()
                        error.reviewed_at = datetime.utcnow()
                        db.commit()
                        st.rerun()
                with cols[1]:
                    if st.button("🙈 Ignore", key=f"ignore_{k}", use_container_width=True):
                        error.status = 'ignored'
                        error.reviewed_by = get_current_user_id()
                        error.reviewed_at = datetime.utcnow()
                        db.commit()
                        st.rerun()
                with cols[2]:
                    if st.button("🔄 Reopen", key=f"reopen_{k}", use_container_width=True):
                        error.status = 'new'
                        db.commit()
                        st.rerun()

            elif error.status in ['fixed', 'ignored']:
                cols = st.columns([1, 1, 6])
                with cols[0]:
                    if st.button("🔄 Reopen", key=f"reopen_{k}", use_container_width=True):
                        error.status = 'new'
                        db.commit()
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️", key=f"del_err_{k}"):
                        st.session_state[f"confirm_del_err_{k}"] = True

            # Delete confirmation
            if st.session_state.get(f"confirm_del_err_{k}"):
                st.warning("Permanently delete this error?")
                del_cols = st.columns([1, 1, 4])
                with del_cols[0]:
                    if st.button("Yes, Delete", key=f"confirm_delete_err_{k}", type="primary"):
                        db.delete(error)
                        db.commit()
                        st.session_state[f"confirm_del_err_{k}"] = False
                        st.rerun()
                with del_cols[1]:
                    if st.button("Cancel", key=f"cancel_del_err_{k}"):
                        st.session_state[f"confirm_del_err_{k}"] = False
                        st.rerun()

            st.markdown("---")


    # New errors tab
    with err_tab_new:
        new_errors = db.query(ErrorLog).filter(
            ErrorLog.status == 'new'
        ).order_by(ErrorLog.created_at.desc()).limit(50).all()

        if not new_errors:
            st.info("No new errors. The system is running smoothly!")
        else:
            st.caption("Run `/wos-errors` to analyze and fix errors with Claude")
            for error in new_errors:
                render_error_item(error, key_prefix="new")


    # Reviewed errors tab
    with err_tab_reviewed:
        reviewed_errors = db.query(ErrorLog).filter(
            ErrorLog.status == 'reviewed'
        ).order_by(ErrorLog.created_at.desc()).limit(50).all()

        if not reviewed_errors:
            st.info("No errors awaiting fix.")
        else:
            st.caption("These errors have been reviewed but not yet fixed")
            for error in reviewed_errors:
                render_error_item(error, key_prefix="reviewed")


    # Fixed errors tab
    with err_tab_fixed:
        fixed_errors = db.query(ErrorLog).filter(
            ErrorLog.status == 'fixed'
        ).order_by(ErrorLog.created_at.desc()).limit(50).all()

        if not fixed_errors:
            st.info("No fixed errors.")
        else:
            for error in fixed_errors:
                render_error_item(error, key_prefix="fixed")


    # Ignored errors tab
    with err_tab_ignored:
        ignored_errors = db.query(ErrorLog).filter(
            ErrorLog.status == 'ignored'
        ).order_by(ErrorLog.created_at.desc()).limit(50).all()

        if not ignored_errors:
            st.info("No ignored errors.")
        else:
            if st.button("🗑️ Delete All Ignored", type="secondary", key="delete_all_ignored"):
                st.session_state.confirm_delete_ignored = True

            if st.session_state.get('confirm_delete_ignored'):
                st.warning("This will permanently delete all ignored errors!")
                cols = st.columns([1, 1, 4])
                with cols[0]:
                    if st.button("Yes, Delete All", type="primary", key="confirm_del_ignored"):
                        db.query(ErrorLog).filter(ErrorLog.status == 'ignored').delete()
                        db.commit()
                        st.session_state.confirm_delete_ignored = False
                        st.rerun()
                with cols[1]:
                    if st.button("Cancel", key="cancel_del_ignored"):
                        st.session_state.confirm_delete_ignored = False
                        st.rerun()

            for error in ignored_errors:
                render_error_item(error, key_prefix="ignored")


# ============================================
# CONVERSATIONS TAB
# ============================================
if selected_admin_tab == "Conversations":
    # New Message button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("➕ New Message", key="new_convo_btn"):
            st.session_state.show_new_convo_form = True

    # New conversation form
    if st.session_state.get('show_new_convo_form'):
        st.markdown("---")
        st.markdown("### New Conversation")

        # Get list of users to message
        users = db.query(User).filter(
            User.is_active == True,
            User.role != 'admin'
        ).order_by(User.username).all()

        if not users:
            st.warning("No users available to message.")
        else:
            with st.form(key="new_conversation_form"):
                user_options = {f"{u.username} ({u.email})": u.id for u in users}
                selected_user = st.selectbox("Select User", list(user_options.keys()))
                subject = st.text_input("Subject *", placeholder="Conversation subject...")
                message_text = st.text_area("Message *", placeholder="Your message...", height=150)

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.form_submit_button("📨 Send Message", use_container_width=True, type="primary"):
                        if not subject:
                            st.error("Subject is required")
                        elif not message_text:
                            st.error("Message is required")
                        else:
                            user_id = user_options[selected_user]
                            create_message_thread(
                                db,
                                user_id=user_id,
                                subject=subject,
                                admin_id=get_current_user_id(),
                                initial_message=message_text
                            )
                            st.session_state.show_new_convo_form = False
                            st.success("Message sent!")
                            st.rerun()
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_new_convo_form = False
                        st.rerun()

        st.markdown("---")

    # List all conversations
    threads = get_admin_conversations(db, limit=50)

    if not threads:
        st.info("No conversations yet. Click 'New Message' to start one.")
    else:
        # Track which thread is expanded
        if 'admin_expanded_thread' not in st.session_state:
            st.session_state.admin_expanded_thread = None

        for thread in threads:
            user = thread.user
            has_unread = has_unread_user_replies(db, thread.id)

            unread_badge = " 🔵" if has_unread else ""
            closed_badge = " (Closed)" if thread.is_closed else ""
            username = html.escape(user.username if user else "Unknown")
            subject = html.escape(thread.subject)

            with st.container():
                col1, col2, col3, col4 = st.columns([5.3, 0.7, 1, 0.5])
                with col1:
                    time_str = thread.updated_at.strftime("%b %d, %Y %I:%M %p")
                    st.markdown(f"""
                    <div style="font-weight: bold; font-size: 15px;">
                        {subject}{unread_badge}{closed_badge}
                    </div>
                    <div style="font-size: 12px; color: #888;">
                        To: {username} · Last activity: {time_str}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    is_expanded = st.session_state.admin_expanded_thread == thread.id
                    btn_label = "Close" if is_expanded else "View"
                    if st.button(btn_label, key=f"admin_toggle_{thread.id}"):
                        if is_expanded:
                            st.session_state.admin_expanded_thread = None
                        else:
                            st.session_state.admin_expanded_thread = thread.id
                            # Mark user replies as read
                            mark_user_replies_read(db, thread.id)
                        st.rerun()
                with col3:
                    # Thread-level read/unread toggle
                    if has_unread:
                        if st.button("Mark Read", key=f"admin_mark_read_{thread.id}"):
                            mark_user_replies_read(db, thread.id)
                            st.rerun()
                    else:
                        if st.button("Mark Unread", key=f"admin_mark_unread_{thread.id}"):
                            # Mark the most recent user message as unread
                            for msg in reversed(thread.messages):
                                if not msg.is_from_admin:
                                    mark_message_unread(db, msg.id)
                                    break
                            st.rerun()
                with col4:
                    if thread.is_closed:
                        if st.button("Reopen", key=f"reopen_{thread.id}"):
                            reopen_thread(db, thread.id)
                            st.rerun()
                    else:
                        if st.button("End", key=f"close_{thread.id}"):
                            close_thread(db, thread.id)
                            st.rerun()

                # Show messages if expanded
                if st.session_state.admin_expanded_thread == thread.id:
                    messages = get_thread_messages(db, thread.id)

                    st.markdown("---")

                    for msg in messages:
                        sender = db.query(User).filter(User.id == msg.sender_id).first()
                        sender_name = "You (Admin)" if msg.is_from_admin else (sender.username if sender else "User")
                        msg_time = msg.created_at.strftime("%b %d %I:%M %p")
                        content = html.escape(msg.content)

                        if msg.is_from_admin:
                            # Admin message - right aligned
                            st.markdown(f"""
                            <div style="background: rgba(52, 152, 219, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 8px; margin-left: 40px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                    <span style="font-weight: bold; color: #3498DB;">{sender_name}</span>
                                    <span style="font-size: 11px; color: #888;">{msg_time}</span>
                                </div>
                                <div style="white-space: pre-wrap;">{content}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # User message - left aligned
                            unread_indicator = " 🔵" if not msg.is_read else ""
                            st.markdown(f"""
                            <div style="background: rgba(46, 204, 113, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 8px; margin-right: 40px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                    <span style="font-weight: bold; color: #2ECC71;">{sender_name}{unread_indicator}</span>
                                    <span style="font-size: 11px; color: #888;">{msg_time}</span>
                                </div>
                                <div style="white-space: pre-wrap;">{content}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Reply form if thread is not closed
                    if not thread.is_closed:
                        st.markdown("---")
                        with st.form(key=f"admin_reply_{thread.id}", clear_on_submit=True):
                            reply_text = st.text_area(
                                "Your reply",
                                placeholder="Type your reply...",
                                height=100,
                                key=f"admin_reply_text_{thread.id}",
                                label_visibility="collapsed"
                            )
                            if st.form_submit_button("Send Reply", use_container_width=True, type="primary"):
                                if reply_text and len(reply_text.strip()) >= 2:
                                    add_message_to_thread(
                                        db,
                                        thread_id=thread.id,
                                        sender_id=get_current_user_id(),
                                        content=reply_text.strip(),
                                        is_from_admin=True
                                    )
                                    st.rerun()
                                else:
                                    st.warning("Please enter a message")
                    else:
                        st.caption("This conversation is closed. Reopen to reply.")

                st.markdown("---")


db.close()
