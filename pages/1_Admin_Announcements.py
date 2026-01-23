"""
Admin Announcements - Create and manage system-wide announcements.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin, get_current_user_id
from database.models import Announcement
from database.messaging_service import create_notification_for_users

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 📢 Announcements")
st.caption("Create and manage system-wide announcements for users")

db = get_db()

# Ensure table exists
from sqlalchemy import inspect, or_
inspector = inspect(db.get_bind())
if 'announcements' not in inspector.get_table_names():
    Announcement.__table__.create(db.get_bind(), checkfirst=True)

# Current Banner Status - show what users currently see
current_banner = db.query(Announcement).filter(
    Announcement.is_active == True,
    or_(
        Announcement.display_type == 'banner',
        Announcement.display_type == 'both',
        Announcement.display_type.is_(None)
    )
).order_by(Announcement.created_at.desc()).first()

st.markdown("### Current Banner")
if current_banner:
    # Calculate days remaining if show_until is set
    days_remaining = None
    expiry_text = "No expiration"
    if current_banner.show_until:
        from datetime import datetime
        now = datetime.utcnow()
        if current_banner.show_until > now:
            delta = current_banner.show_until - now
            days_remaining = delta.days
            if days_remaining == 0:
                hours_remaining = delta.seconds // 3600
                expiry_text = f"Expires in {hours_remaining} hours" if hours_remaining > 0 else "Expires soon"
            elif days_remaining == 1:
                expiry_text = "Expires tomorrow"
            else:
                expiry_text = f"{days_remaining} days remaining"
        else:
            expiry_text = "Expired (still showing)"

    type_icons = {"info": "ℹ️", "warning": "⚠️", "success": "✅", "error": "🚨"}
    icon = type_icons.get(current_banner.type, "ℹ️")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="background: rgba(52, 152, 219, 0.15); padding: 16px; border-radius: 8px; border-left: 4px solid #3498DB;">
            <div style="font-weight: bold; font-size: 16px;">{icon} {current_banner.title}</div>
            <div style="color: #ccc; margin-top: 6px; font-size: 14px;">{current_banner.message[:100]}{'...' if len(current_banner.message) > 100 else ''}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.metric("Status", expiry_text)
        st.caption(f"Created: {current_banner.created_at.strftime('%b %d, %Y')}")
else:
    st.info("No banner currently showing to users.")

st.markdown("---")

# Tabs
tab_active, tab_create, tab_archive = st.tabs(["📋 Active", "➕ Create New", "📦 Archive"])

with tab_active:
    # Get active announcements
    active = db.query(Announcement).filter(Announcement.is_active == True).order_by(Announcement.created_at.desc()).all()

    if not active:
        st.info("No active announcements. Create one in the 'Create New' tab.")
    else:
        for ann in active:
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

            with st.container():
                # Display type badge
                display_type = getattr(ann, 'display_type', 'banner') or 'banner'
                display_badges = {
                    "banner": ("📺", "Banner"),
                    "inbox": ("📬", "Inbox"),
                    "both": ("📢", "Both")
                }
                d_icon, d_label = display_badges.get(display_type, ("📺", "Banner"))

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2), rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1));
                            padding: 16px; border-radius: 8px; margin-bottom: 12px;
                            border-left: 4px solid {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 16px; font-weight: bold;">{icon} {ann.title}</div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 11px;">{d_icon} {d_label}</span>
                            <span style="font-size: 11px; color: #888;">{ann.created_at.strftime('%m/%d/%y %I:%M %p')}</span>
                        </div>
                    </div>
                    <div style="margin-top: 8px; color: #ccc;">{ann.message}</div>
                </div>
                """, unsafe_allow_html=True)

                cols = st.columns([1, 1, 1, 5])
                with cols[0]:
                    if st.button("✏️ Edit", key=f"edit_{ann.id}"):
                        st.session_state[f"editing_ann_{ann.id}"] = True
                with cols[1]:
                    if st.button("📦 Archive", key=f"archive_{ann.id}"):
                        ann.is_active = False
                        db.commit()
                        st.rerun()
                with cols[2]:
                    if st.button("🗑️ Delete", key=f"del_{ann.id}"):
                        st.session_state[f"confirm_del_ann_{ann.id}"] = True

                # Edit form
                if st.session_state.get(f"editing_ann_{ann.id}"):
                    with st.form(f"edit_form_{ann.id}"):
                        new_title = st.text_input("Title", value=ann.title)
                        new_message = st.text_area("Message", value=ann.message)
                        new_type = st.selectbox("Type", ["info", "warning", "success", "error"],
                                               index=["info", "warning", "success", "error"].index(ann.type))

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save"):
                                ann.title = new_title
                                ann.message = new_message
                                ann.type = new_type
                                ann.updated_at = datetime.utcnow()
                                db.commit()
                                st.session_state[f"editing_ann_{ann.id}"] = False
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"editing_ann_{ann.id}"] = False
                                st.rerun()

                # Delete confirmation
                if st.session_state.get(f"confirm_del_ann_{ann.id}"):
                    st.warning(f"Delete '{ann.title}'? This cannot be undone!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Yes, Delete", key=f"confirm_delete_{ann.id}"):
                            db.delete(ann)
                            db.commit()
                            st.session_state[f"confirm_del_ann_{ann.id}"] = False
                            st.rerun()
                    with col2:
                        if st.button("Cancel", key=f"cancel_del_{ann.id}"):
                            st.session_state[f"confirm_del_ann_{ann.id}"] = False
                            st.rerun()

                st.markdown("---")

with tab_create:
    st.markdown("### New Announcement")

    with st.form("create_announcement"):
        title = st.text_input("Title *", placeholder="Announcement title...")
        message = st.text_area("Message *", placeholder="Announcement message (shown in banner)...", height=100)

        col1, col2 = st.columns(2)
        with col1:
            ann_type = st.selectbox("Type", ["info", "warning", "success", "error"])
        with col2:
            display_type = st.radio(
                "Display",
                ["banner", "inbox", "both"],
                horizontal=True,
                help="Banner: top of page | Inbox: user inbox only | Both: everywhere"
            )

        # Expiration settings (for banners)
        if display_type in ["banner", "both"]:
            st.markdown("**Expiration**")
            exp_col1, exp_col2 = st.columns([1, 2])
            with exp_col1:
                set_expiration = st.checkbox("Set expiration", value=False)
            with exp_col2:
                expiration_days = st.number_input(
                    "Days until expiration",
                    min_value=1,
                    max_value=365,
                    value=7,
                    help="Banner will auto-hide after this many days (only used if checkbox is checked)"
                )
        else:
            set_expiration = False
            expiration_days = None

        # Show inbox content field when inbox delivery is selected
        inbox_content = None
        if display_type in ["inbox", "both"]:
            inbox_content = st.text_area(
                "Inbox Content (optional)",
                placeholder="Optional longer message for inbox. Leave blank to use the banner message.",
                height=100,
                help="If provided, this longer message will appear in user inboxes instead of the banner message."
            )

        preview_types = {"info": "ℹ️ Info", "warning": "⚠️ Warning", "success": "✅ Success", "error": "🚨 Error"}
        st.caption(f"Preview: {preview_types[ann_type]}")

        submitted = st.form_submit_button("📢 Publish Announcement", use_container_width=True)

        if submitted:
            if not title:
                st.error("Title is required")
            elif not message:
                st.error("Message is required")
            else:
                # Calculate show_until if expiration is set
                show_until = None
                if set_expiration and expiration_days:
                    show_until = datetime.utcnow() + timedelta(days=expiration_days)

                new_ann = Announcement(
                    title=title,
                    message=message,
                    type=ann_type,
                    display_type=display_type,
                    inbox_content=inbox_content if inbox_content else None,
                    show_until=show_until,
                    is_active=True,
                    created_by=get_current_user_id()
                )
                db.add(new_ann)
                db.commit()
                db.refresh(new_ann)

                # Create notifications for users if inbox delivery is enabled
                if display_type in ["inbox", "both"]:
                    notif_count = create_notification_for_users(db, new_ann.id)
                    st.session_state['announcement_created'] = True
                    st.session_state['notification_count'] = notif_count
                else:
                    st.session_state['announcement_created'] = True
                    st.session_state['notification_count'] = 0

                st.rerun()

    # Show success message after rerun
    if st.session_state.get('announcement_created'):
        notif_count = st.session_state.get('notification_count', 0)
        if notif_count > 0:
            st.success(f"Announcement published! Delivered to {notif_count} user inboxes.")
        else:
            st.success("Announcement published! View it in the 'Active' tab.")
        st.session_state['announcement_created'] = False
        st.session_state['notification_count'] = 0

with tab_archive:
    # Get archived announcements
    archived = db.query(Announcement).filter(Announcement.is_active == False).order_by(Announcement.created_at.desc()).all()

    if not archived:
        st.info("No archived announcements.")
    else:
        for ann in archived:
            with st.container():
                st.markdown(f"""
                <div style="background: rgba(100, 100, 100, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between;">
                        <div style="font-weight: bold; color: #888;">{ann.title}</div>
                        <div style="font-size: 11px; color: #666;">{ann.created_at.strftime('%m/%d/%y')}</div>
                    </div>
                    <div style="color: #666; font-size: 13px; margin-top: 4px;">{ann.message[:100]}...</div>
                </div>
                """, unsafe_allow_html=True)

                cols = st.columns([1, 1, 6])
                with cols[0]:
                    if st.button("🔄 Restore", key=f"restore_{ann.id}"):
                        ann.is_active = True
                        db.commit()
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️", key=f"del_arch_{ann.id}"):
                        db.delete(ann)
                        db.commit()
                        st.rerun()

db.close()
