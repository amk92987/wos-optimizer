"""
Admin Audit Log - Track all admin actions for accountability.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin
from database.models import AuditLog, User

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 📜 Audit Log")
st.caption("Track all administrative actions")

db = get_db()

# Ensure table exists
from sqlalchemy import inspect
inspector = inspect(db.bind)
if 'audit_log' not in inspector.get_table_names():
    AuditLog.__table__.create(db.bind, checkfirst=True)

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    # Get unique admins from audit log
    admins = db.query(AuditLog.admin_username).distinct().all()
    admin_list = ["All Admins"] + [a[0] for a in admins]
    selected_admin = st.selectbox("Admin", admin_list, label_visibility="collapsed")

with col2:
    action_types = ["All Actions", "user_created", "user_deleted", "password_reset",
                   "role_changed", "impersonation_started", "user_suspended", "user_activated"]
    selected_action = st.selectbox("Action", action_types, label_visibility="collapsed")

with col3:
    time_ranges = ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
    selected_range = st.selectbox("Time Range", time_ranges, label_visibility="collapsed")

# Build query
query = db.query(AuditLog)

if selected_admin != "All Admins":
    query = query.filter(AuditLog.admin_username == selected_admin)

if selected_action != "All Actions":
    query = query.filter(AuditLog.action == selected_action)

if selected_range == "Last 24 Hours":
    query = query.filter(AuditLog.created_at >= datetime.now() - timedelta(hours=24))
elif selected_range == "Last 7 Days":
    query = query.filter(AuditLog.created_at >= datetime.now() - timedelta(days=7))
elif selected_range == "Last 30 Days":
    query = query.filter(AuditLog.created_at >= datetime.now() - timedelta(days=30))

logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()

st.markdown("---")

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    today_count = db.query(AuditLog).filter(AuditLog.created_at >= datetime.now() - timedelta(days=1)).count()
    st.metric("Today", today_count)
with col2:
    week_count = db.query(AuditLog).filter(AuditLog.created_at >= datetime.now() - timedelta(days=7)).count()
    st.metric("This Week", week_count)
with col3:
    user_actions = db.query(AuditLog).filter(AuditLog.action.like("user_%")).count()
    st.metric("User Actions", user_actions)
with col4:
    total = db.query(AuditLog).count()
    st.metric("Total Entries", total)

st.markdown("---")

# Action icons and colors
action_styles = {
    "user_created": ("👤", "#2ECC71"),
    "user_deleted": ("🗑️", "#E74C3C"),
    "password_reset": ("🔑", "#F1C40F"),
    "role_changed": ("👑", "#9B59B6"),
    "impersonation_started": ("👁️", "#3498DB"),
    "user_suspended": ("⏸️", "#E74C3C"),
    "user_activated": ("▶️", "#2ECC71"),
}

if not logs:
    st.info("No audit log entries found matching your filters.")
else:
    st.caption(f"Showing {len(logs)} entries")

    for log in logs:
        icon, color = action_styles.get(log.action, ("📋", "#888"))

        # Time formatting
        time_diff = datetime.now() - log.created_at
        if time_diff.days > 0:
            time_str = log.created_at.strftime("%m/%d/%y %I:%M %p")
        elif time_diff.seconds > 3600:
            time_str = f"{time_diff.seconds // 3600}h ago"
        elif time_diff.seconds > 60:
            time_str = f"{time_diff.seconds // 60}m ago"
        else:
            time_str = "Just now"

        # Format action text
        action_text = log.action.replace("_", " ").title()

        st.markdown(f"""
        <div style="background: rgba(74, 144, 217, 0.05); padding: 12px 16px; border-radius: 8px;
                    margin-bottom: 8px; border-left: 3px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 16px;">{icon}</span>
                    <strong style="margin-left: 8px;">{action_text}</strong>
                    {f'<span style="color: #888; margin-left: 8px;">→ {log.target_name}</span>' if log.target_name else ''}
                </div>
                <div style="text-align: right;">
                    <span style="color: #888; font-size: 12px;">{time_str}</span>
                    <br>
                    <span style="color: #666; font-size: 11px;">by {log.admin_username}</span>
                </div>
            </div>
            {f'<div style="color: #888; font-size: 12px; margin-top: 6px;">{log.details}</div>' if log.details else ''}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Export option
if st.button("📥 Export to CSV"):
    import pandas as pd
    data = []
    all_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    for log in all_logs:
        data.append({
            "Timestamp": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Admin": log.admin_username,
            "Action": log.action,
            "Target": log.target_name or "",
            "Details": log.details or ""
        })

    if data:
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

db.close()
