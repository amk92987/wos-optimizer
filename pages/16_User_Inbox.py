"""
User Inbox - View notifications and messages from admin.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys
import html

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import get_current_user_id, is_authenticated
from database.messaging_service import (
    get_user_notifications, mark_notification_read, mark_notification_unread,
    mark_all_notifications_read, get_user_threads, get_thread_messages,
    mark_thread_messages_read, add_message_to_thread, get_unread_notification_count,
    get_unread_message_count, mark_message_unread, mark_message_read
)

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Require login - redirect to login page if not authenticated
if not is_authenticated():
    st.query_params["page"] = "login"
    st.rerun()

user_id = get_current_user_id()
db = get_db()

st.markdown("# Inbox")

# Get unread counts for tab labels
notification_unread = get_unread_notification_count(db, user_id)
message_unread = get_unread_message_count(db, user_id)

notification_label = f"Notifications ({notification_unread})" if notification_unread > 0 else "Notifications"
messages_label = f"Messages ({message_unread})" if message_unread > 0 else "Messages"

# Use session state to preserve tab selection across reruns
if 'inbox_tab' not in st.session_state:
    st.session_state.inbox_tab = "Notifications"

# Tab selection using radio buttons (preserves state on rerun)
selected_tab = st.radio(
    "Select tab",
    ["Notifications", "Messages"],
    horizontal=True,
    label_visibility="collapsed",
    key="inbox_tab_selector",
    index=0 if st.session_state.inbox_tab == "Notifications" else 1
)
st.session_state.inbox_tab = selected_tab

# Show unread badges next to tab names
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if notification_unread > 0:
        st.caption(f"📬 {notification_unread} unread")
with col2:
    if message_unread > 0 and selected_tab == "Notifications":
        st.caption(f"💬 {message_unread} unread messages")

st.markdown("---")

# ============================================
# NOTIFICATIONS TAB
# ============================================
if selected_tab == "Notifications":
    # Get all notifications (not just unread)
    notifications = get_user_notifications(db, user_id, unread_only=False, limit=50)

    if not notifications:
        st.info("No notifications yet.")
    else:
        # Mark all as read button
        if notification_unread > 0:
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Mark All Read", key="mark_all_notif_read"):
                    mark_all_notifications_read(db, user_id)
                    st.rerun()

        st.markdown("---")

        for notif in notifications:
            ann = notif.announcement
            if not ann:
                continue

            # Type styling
            type_colors = {
                "info": "#3498DB",
                "warning": "#F1C40F",
                "success": "#2ECC71",
                "error": "#E74C3C"
            }
            type_icons = {
                "info": "ℹ️",
                "warning": "⚠️",
                "success": "✅",
                "error": "🚨"
            }
            color = type_colors.get(ann.type, "#3498DB")
            icon = type_icons.get(ann.type, "ℹ️")

            # Unread indicator
            unread_style = "border-left: 4px solid #3498DB;" if not notif.is_read else "border-left: 4px solid transparent;"
            unread_dot = "🔵 " if not notif.is_read else ""

            # Use inbox_content if available, otherwise use message
            content = html.escape(ann.inbox_content or ann.message)
            title = html.escape(ann.title)
            time_str = notif.created_at.strftime("%b %d, %Y %I:%M %p")

            with st.container():
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15), rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.08));
                            padding: 16px; border-radius: 8px; margin-bottom: 12px;
                            {unread_style}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 16px; font-weight: bold;">{unread_dot}{icon} {title}</div>
                        <div style="font-size: 11px; color: #888;">{time_str}</div>
                    </div>
                    <div style="margin-top: 10px; color: #ccc; white-space: pre-wrap;">{content}</div>
                </div>
                """, unsafe_allow_html=True)

                # Toggle read/unread status
                if not notif.is_read:
                    if st.button("Mark as Read", key=f"read_notif_{notif.id}"):
                        mark_notification_read(db, notif.id, user_id)
                        st.rerun()
                else:
                    if st.button("Mark as Unread", key=f"unread_notif_{notif.id}"):
                        mark_notification_unread(db, notif.id, user_id)
                        st.rerun()

                st.markdown("")  # Spacing

# ============================================
# MESSAGES TAB
# ============================================
if selected_tab == "Messages":
    # Get all threads for user
    threads = get_user_threads(db, user_id, limit=20)

    if not threads:
        st.info("No messages yet. Admin may contact you here.")
    else:
        # Track which thread is expanded
        if 'expanded_thread' not in st.session_state:
            st.session_state.expanded_thread = None

        for thread in threads:
            # Check if thread has unread messages
            unread_in_thread = any(
                m.is_from_admin and not m.is_read
                for m in thread.messages
            )

            unread_badge = " 🔵" if unread_in_thread else ""
            closed_badge = " (Closed)" if thread.is_closed else ""

            # Thread header
            with st.container():
                col1, col2, col3 = st.columns([5.3, 0.7, 1])
                with col1:
                    subject = html.escape(thread.subject)
                    time_str = thread.updated_at.strftime("%b %d, %Y")
                    st.markdown(f"""
                    <div style="font-weight: bold; font-size: 15px;">
                        {subject}{unread_badge}{closed_badge}
                    </div>
                    <div style="font-size: 12px; color: #888;">Last activity: {time_str}</div>
                    """, unsafe_allow_html=True)
                with col2:
                    is_expanded = st.session_state.expanded_thread == thread.id
                    btn_label = "Close" if is_expanded else "View"
                    if st.button(btn_label, key=f"toggle_thread_{thread.id}"):
                        if is_expanded:
                            st.session_state.expanded_thread = None
                        else:
                            st.session_state.expanded_thread = thread.id
                            # Mark messages as read when opening
                            mark_thread_messages_read(db, thread.id, user_id)
                        st.rerun()
                with col3:
                    # Thread-level read/unread toggle
                    if unread_in_thread:
                        if st.button("Mark Read", key=f"mark_read_{thread.id}"):
                            mark_thread_messages_read(db, thread.id, user_id)
                            st.rerun()
                    else:
                        if st.button("Mark Unread", key=f"mark_unread_{thread.id}"):
                            # Mark the most recent admin message as unread
                            for msg in reversed(thread.messages):
                                if msg.is_from_admin:
                                    mark_message_unread(db, msg.id)
                                    break
                            st.rerun()

                # Show messages if expanded
                if st.session_state.expanded_thread == thread.id:
                    messages = get_thread_messages(db, thread.id)

                    st.markdown("---")

                    for msg in messages:
                        sender_name = "Admin" if msg.is_from_admin else "You"
                        msg_time = msg.created_at.strftime("%b %d %I:%M %p")
                        content = html.escape(msg.content)

                        if msg.is_from_admin:
                            # Admin message - left aligned, different color
                            unread_indicator = " 🔵" if not msg.is_read else ""
                            st.markdown(f"""
                            <div style="background: rgba(52, 152, 219, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 8px; margin-right: 40px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                    <span style="font-weight: bold; color: #3498DB;">Admin{unread_indicator}</span>
                                    <span style="font-size: 11px; color: #888;">{msg_time}</span>
                                </div>
                                <div style="white-space: pre-wrap;">{content}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # User message - right aligned
                            st.markdown(f"""
                            <div style="background: rgba(46, 204, 113, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 8px; margin-left: 40px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                    <span style="font-weight: bold; color: #2ECC71;">You</span>
                                    <span style="font-size: 11px; color: #888;">{msg_time}</span>
                                </div>
                                <div style="white-space: pre-wrap;">{content}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Reply form if thread is not closed
                    if not thread.is_closed:
                        st.markdown("---")
                        with st.form(key=f"reply_form_{thread.id}", clear_on_submit=True):
                            reply_text = st.text_area(
                                "Your reply",
                                placeholder="Type your reply...",
                                height=100,
                                key=f"reply_text_{thread.id}",
                                label_visibility="collapsed"
                            )
                            if st.form_submit_button("Send Reply", use_container_width=True, type="primary"):
                                if reply_text and len(reply_text.strip()) >= 2:
                                    add_message_to_thread(
                                        db,
                                        thread_id=thread.id,
                                        sender_id=user_id,
                                        content=reply_text.strip(),
                                        is_from_admin=False
                                    )
                                    st.rerun()
                                else:
                                    st.warning("Please enter a message")
                    else:
                        st.caption("This conversation is closed.")

                st.markdown("---")

db.close()
