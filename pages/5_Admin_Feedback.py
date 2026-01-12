"""
Admin Feedback Inbox - Review and manage user feedback.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin
from database.models import Feedback, User

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 📬 Feedback Inbox")
st.caption("Review and manage user feedback")

db = get_db()

# Stats
total = db.query(Feedback).count()
new_count = db.query(Feedback).filter(Feedback.status == 'new').count()
reviewed = db.query(Feedback).filter(Feedback.status == 'reviewed').count()
implemented = db.query(Feedback).filter(Feedback.status == 'implemented').count()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total", total)
with col2:
    st.metric("New", new_count)
with col3:
    st.metric("Reviewed", reviewed)
with col4:
    st.metric("Implemented", implemented)

st.markdown("---")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox("Status", ["All", "new", "reviewed", "implemented", "wont_fix"])

with col2:
    category_filter = st.selectbox("Category", ["All", "bug", "feature", "data_error", "other"])

with col3:
    sort_order = st.selectbox("Sort", ["Newest First", "Oldest First"])

# Build query
query = db.query(Feedback)

if status_filter != "All":
    query = query.filter(Feedback.status == status_filter)

if category_filter != "All":
    query = query.filter(Feedback.category == category_filter)

if sort_order == "Newest First":
    query = query.order_by(Feedback.created_at.desc())
else:
    query = query.order_by(Feedback.created_at.asc())

feedback_items = query.all()

st.markdown("---")

# Category icons and colors
category_styles = {
    "bug": ("🐛", "#E74C3C"),
    "feature": ("✨", "#9B59B6"),
    "data_error": ("📊", "#F1C40F"),
    "other": ("💬", "#3498DB"),
}

status_styles = {
    "new": ("🆕", "#3498DB"),
    "reviewed": ("👀", "#F1C40F"),
    "implemented": ("✅", "#2ECC71"),
    "wont_fix": ("❌", "#95A5A6"),
}

if not feedback_items:
    st.info("No feedback found matching your filters.")
else:
    st.caption(f"Showing {len(feedback_items)} items")

    for item in feedback_items:
        # Get user info
        user = db.query(User).filter(User.id == item.user_id).first() if item.user_id else None
        username = user.username if user else "Anonymous"

        cat_icon, cat_color = category_styles.get(item.category, ("💬", "#888"))
        stat_icon, stat_color = status_styles.get(item.status, ("❓", "#888"))

        # Time formatting
        time_str = item.created_at.strftime("%m/%d/%y %I:%M %p")

        with st.container():
            st.markdown(f"""
            <div style="background: rgba(74, 144, 217, 0.05); padding: 16px; border-radius: 8px;
                        margin-bottom: 8px; border-left: 3px solid {cat_color};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="font-size: 14px;">{cat_icon}</span>
                        <strong style="margin-left: 8px;">{item.category.title()}</strong>
                        {f'<span style="color: #888; margin-left: 8px;">• {item.page}</span>' if item.page else ''}
                    </div>
                    <div style="text-align: right;">
                        <span style="background: rgba({int(stat_color[1:3], 16)}, {int(stat_color[3:5], 16)}, {int(stat_color[5:7], 16)}, 0.2);
                                     color: {stat_color}; padding: 2px 8px; border-radius: 4px; font-size: 11px;">
                            {stat_icon} {item.status.upper()}
                        </span>
                    </div>
                </div>
                <div style="margin-top: 12px; color: #ccc; white-space: pre-wrap;">{item.description}</div>
                <div style="margin-top: 12px; display: flex; justify-content: space-between; color: #666; font-size: 12px;">
                    <span>From: {username}</span>
                    <span>{time_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Actions
            cols = st.columns([1, 1, 1, 1, 4])

            with cols[0]:
                if item.status != "reviewed":
                    if st.button("👀", key=f"review_{item.id}", help="Mark as Reviewed"):
                        item.status = "reviewed"
                        db.commit()
                        st.rerun()

            with cols[1]:
                if item.status != "implemented":
                    if st.button("✅", key=f"impl_{item.id}", help="Mark as Implemented"):
                        item.status = "implemented"
                        db.commit()
                        st.rerun()

            with cols[2]:
                if item.status != "wont_fix":
                    if st.button("❌", key=f"wont_{item.id}", help="Won't Fix"):
                        item.status = "wont_fix"
                        db.commit()
                        st.rerun()

            with cols[3]:
                if st.button("🗑️", key=f"del_{item.id}", help="Delete"):
                    st.session_state[f"confirm_del_fb_{item.id}"] = True

            # Delete confirmation
            if st.session_state.get(f"confirm_del_fb_{item.id}"):
                st.warning("Delete this feedback?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Yes", key=f"confirm_delete_{item.id}"):
                        db.delete(item)
                        db.commit()
                        st.session_state[f"confirm_del_fb_{item.id}"] = False
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_del_{item.id}"):
                        st.session_state[f"confirm_del_fb_{item.id}"] = False
                        st.rerun()

            st.markdown("---")

# Quick actions
st.markdown("### Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👀 Mark All as Reviewed", use_container_width=True):
        db.query(Feedback).filter(Feedback.status == "new").update({"status": "reviewed"})
        db.commit()
        st.rerun()

with col2:
    if st.button("🗑️ Delete Resolved", use_container_width=True, help="Delete implemented and won't fix"):
        db.query(Feedback).filter(Feedback.status.in_(["implemented", "wont_fix"])).delete()
        db.commit()
        st.rerun()

with col3:
    # Export
    if st.button("📥 Export All", use_container_width=True):
        import pandas as pd
        all_fb = db.query(Feedback).all()
        data = []
        for fb in all_fb:
            user = db.query(User).filter(User.id == fb.user_id).first() if fb.user_id else None
            data.append({
                "Date": fb.created_at.strftime("%Y-%m-%d %H:%M"),
                "Category": fb.category,
                "Page": fb.page or "",
                "Description": fb.description,
                "Status": fb.status,
                "User": user.username if user else "Anonymous"
            })
        if data:
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"feedback_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

db.close()
