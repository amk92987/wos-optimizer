"""
Admin Feedback Inbox - Review and manage user feedback.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys
import html

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin
from database.models import Feedback, User

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 📬 Feedback Inbox")

db = get_db()

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
                    if st.button("🔧 To Fix", key=f"tofix_{k}", width="stretch"):
                        item.status = 'pending_fix'
                        db.commit()
                        st.rerun()
                else:
                    if st.button("📝 To Update", key=f"toupdate_{k}", width="stretch"):
                        item.status = 'pending_update'
                        db.commit()
                        st.rerun()
            with cols[1]:
                if st.button("📦 Archive", key=f"archive_{k}", width="stretch"):
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
                if st.button("📦 Archive", key=f"archive_{k}", width="stretch"):
                    item.status = 'archive'
                    db.commit()
                    st.rerun()
            with cols[1]:
                if st.button("🗑️", key=f"del_{k}"):
                    st.session_state[f"confirm_del_{k}"] = True

        elif item.status == 'completed':
            cols = st.columns([1, 1, 6])
            with cols[0]:
                if st.button("📦 Archive", key=f"archive_{k}", width="stretch"):
                    item.status = 'archive'
                    db.commit()
                    st.rerun()
            with cols[1]:
                if st.button("🗑️", key=f"del_{k}"):
                    st.session_state[f"confirm_del_{k}"] = True

        elif item.status == 'archive':
            cols = st.columns([1, 1, 6])
            with cols[0]:
                if st.button("🔄 Restore", key=f"restore_{k}", width="stretch"):
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
        if st.button("📦 Archive All Completed", width="content"):
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
        if st.button("🗑️ Empty Archive (Delete All)", type="secondary"):
            st.session_state.confirm_empty_archive = True

        if st.session_state.get('confirm_empty_archive'):
            st.warning("This will permanently delete all archived feedback!")
            cols = st.columns([1, 1, 4])
            with cols[0]:
                if st.button("Yes, Delete All", type="primary"):
                    db.query(Feedback).filter(Feedback.status == 'archive').delete()
                    db.commit()
                    st.session_state.confirm_empty_archive = False
                    st.rerun()
            with cols[1]:
                if st.button("Cancel"):
                    st.session_state.confirm_empty_archive = False
                    st.rerun()

        for item in archived:
            render_feedback_item(item, show_category=True, key_prefix="arch")


db.close()
