"""
Admin - User Management with database-style interface.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db
from database.auth import (
    require_admin, get_all_users, create_user,
    update_user_password, update_user_role, delete_user,
    login_as_user, get_current_user_id
)
from database.models import User

# Load Arctic Night theme CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Compact styling for user management
st.markdown("""
<style>
.status-active { color: #2ECC71; }
.status-suspended { color: #E74C3C; }
.status-inactive { color: #95A5A6; }
.usage-high { color: #2ECC71; }
.usage-medium { color: #F1C40F; }
.usage-low { color: #E74C3C; }

/* Tight vertical spacing */
[data-testid="stVerticalBlock"] > div {
    gap: 0.2rem !important;
}

/* Compact columns */
[data-testid="column"] {
    padding: 0 0.1rem !important;
}

/* Compact metrics row */
[data-testid="stMetric"] {
    padding: 6px !important;
}
[data-testid="stMetric"] label {
    font-size: 11px !important;
}

/* Very small action buttons */
.stButton > button {
    padding: 2px 6px !important;
    min-height: 24px !important;
    font-size: 10px !important;
    border-radius: 4px !important;
    white-space: nowrap !important;
    background: linear-gradient(135deg, #1A3A5C, #2E5A8C) !important;
    border: 1px solid #4A90D9 !important;
    color: #E8F4F8 !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2E5A8C, #3A7ABF) !important;
    border-color: #7DD3FC !important;
}

/* Primary buttons (Delete, Save) - red/orange */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8B2500, #C0392B) !important;
    border-color: #E74C3C !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #C0392B, #E74C3C) !important;
}

/* Reduce text margins */
p, .stMarkdown p {
    margin-bottom: 0.15rem !important;
    line-height: 1.3 !important;
}

/* Compact captions */
.stCaption, [data-testid="stCaptionContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 12px !important;
}

/* Align items vertically in columns */
[data-testid="column"] > div {
    display: flex;
    align-items: center;
    min-height: 28px;
}
</style>
""", unsafe_allow_html=True)

require_admin()

st.markdown("# 👥 User Management")


db = get_db()
current_user_id = get_current_user_id()

# Get all users
all_users = get_all_users(db)
regular_users = [u for u in all_users if u.role != 'admin']
admin_users = [u for u in all_users if u.role == 'admin']

# Calculate usage stats (days active in last 7 days)
def get_usage_stat(user) -> tuple:
    """Returns (days_active, label, css_class)"""
    if not user.last_login:
        return (0, "0/7", "usage-low")

    now = datetime.now()
    # For simplicity, we'll estimate based on last_login
    # In production, you'd track daily logins in a separate table
    days_since = (now - user.last_login).days

    if days_since == 0:
        days_active = 7  # Assume active user
    elif days_since <= 1:
        days_active = 5
    elif days_since <= 3:
        days_active = 3
    elif days_since <= 7:
        days_active = 1
    else:
        days_active = 0

    css = "usage-high" if days_active >= 5 else "usage-medium" if days_active >= 2 else "usage-low"
    return (days_active, f"{days_active}/7", css)

# Top stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Users", len(regular_users))
with col2:
    st.metric("Admins", len(admin_users))
with col3:
    active_7d = len([u for u in regular_users if u.last_login and (datetime.now() - u.last_login).days <= 7])
    st.metric("Active (7d)", active_7d)
with col4:
    suspended = len([u for u in all_users if not u.is_active])
    st.metric("Suspended", suspended)

st.markdown("---")

# Tabs
tab_users, tab_create = st.tabs(["📋 User Database", "➕ Create User"])

with tab_users:
    # Search and filters
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search = st.text_input("🔍 Search", placeholder="Username or email...", label_visibility="collapsed")
    with col_filter:
        filter_status = st.selectbox("Status", ["All", "Active", "Suspended", "Inactive (30d+)"], label_visibility="collapsed")

    # Filter users
    filtered_users = all_users.copy()

    if search:
        search_lower = search.lower()
        filtered_users = [u for u in filtered_users if
                        search_lower in u.username.lower() or
                        (u.email and search_lower in u.email.lower())]

    if filter_status == "Active":
        filtered_users = [u for u in filtered_users if u.is_active]
    elif filter_status == "Suspended":
        filtered_users = [u for u in filtered_users if not u.is_active]
    elif filter_status == "Inactive (30d+)":
        cutoff = datetime.now() - timedelta(days=30)
        filtered_users = [u for u in filtered_users if not u.last_login or u.last_login < cutoff]

    # Sort by last login (most recent first)
    filtered_users = sorted(filtered_users, key=lambda x: x.last_login or datetime.min, reverse=True)

    st.caption(f"Showing {len(filtered_users)} users")

    # Header row (matches data row: 10 columns)
    header_cols = st.columns([0.3, 1.4, 1.6, 0.7, 0.5, 0.6, 0.6, 0.6, 0.7, 0.6])
    with header_cols[0]:
        st.caption("Role")
    with header_cols[1]:
        st.caption("Username")
    with header_cols[2]:
        st.caption("Email")
    with header_cols[3]:
        st.caption("Status")
    with header_cols[4]:
        st.caption("Usage")
    with header_cols[5]:
        st.caption("Last")
    with header_cols[6]:
        st.caption("Actions")

    st.markdown("<hr style='margin: 2px 0 8px 0; border-color: rgba(74, 144, 217, 0.4);'>", unsafe_allow_html=True)

    # User rows
    for user in filtered_users:
        # Calculate stats
        usage_days, usage_label, usage_css = get_usage_stat(user)

        # Status
        if not user.is_active:
            status_label = "Suspended"
            status_css = "status-suspended"
        elif user.last_login and (datetime.now() - user.last_login).days > 30:
            status_label = "Inactive"
            status_css = "status-inactive"
        else:
            status_label = "Active"
            status_css = "status-active"

        # Last login
        if user.last_login:
            days_ago = (datetime.now() - user.last_login).days
            if days_ago == 0:
                last_login = "Today"
            elif days_ago == 1:
                last_login = "Yesterday"
            elif days_ago < 7:
                last_login = f"{days_ago}d ago"
            else:
                last_login = user.last_login.strftime("%m/%d/%y")
        else:
            last_login = "Never"

        # Role icon
        role_icon = "👑" if user.role == 'admin' else "🛡️"
        is_self = user.id == current_user_id

        # User row with inline actions
        row_cols = st.columns([0.3, 1.4, 1.6, 0.7, 0.5, 0.6, 0.6, 0.6, 0.7, 0.6])

        with row_cols[0]:
            st.markdown(role_icon)

        with row_cols[1]:
            label = f"**{user.username}**" + (" _(you)_" if is_self else "")
            st.markdown(label)

        with row_cols[2]:
            st.caption(user.email or "—")

        with row_cols[3]:
            st.markdown(f"<span class='{status_css}'>{status_label}</span>", unsafe_allow_html=True)

        with row_cols[4]:
            st.markdown(f"<span class='{usage_css}'>{usage_label}</span>", unsafe_allow_html=True)

        with row_cols[5]:
            st.caption(last_login)

        # Action buttons inline (no help param, no emoji issues)
        with row_cols[6]:
            if st.button("Edit", key=f"edit_{user.id}"):
                st.session_state[f"editing_{user.id}"] = True
                st.rerun()

        with row_cols[7]:
            if not is_self:
                if st.button("Login", key=f"impersonate_{user.id}"):
                    login_as_user(user)
                    st.rerun()

        with row_cols[8]:
            if not is_self:
                if user.is_active:
                    if st.button("Suspend", key=f"suspend_{user.id}"):
                        user.is_active = False
                        db.commit()
                        st.rerun()
                else:
                    if st.button("Activate", key=f"activate_{user.id}"):
                        user.is_active = True
                        db.commit()
                        st.rerun()

        with row_cols[9]:
            if not is_self:
                if st.button("Delete", key=f"del_{user.id}", type="primary"):
                    st.session_state[f"confirm_del_{user.id}"] = True
                    st.rerun()

        # Edit form appears BELOW the row when editing
        if st.session_state.get(f"editing_{user.id}"):
            with st.container():
                st.markdown(f"<div style='background: rgba(26, 58, 92, 0.3); padding: 8px 12px; border-radius: 6px; margin: 4px 0;'>", unsafe_allow_html=True)
                edit_cols = st.columns([2, 2, 1, 0.5, 0.5])
                with edit_cols[0]:
                    new_email = st.text_input("Email", value=user.email or "", key=f"email_{user.id}", label_visibility="collapsed", placeholder="Email")
                with edit_cols[1]:
                    new_pass = st.text_input("Password", type="password", key=f"pass_{user.id}", label_visibility="collapsed", placeholder="New password")
                with edit_cols[2]:
                    new_role = st.selectbox("Role", ["user", "admin"], index=0 if user.role == "user" else 1, key=f"role_{user.id}", label_visibility="collapsed")
                with edit_cols[3]:
                    if st.button("Save", key=f"save_{user.id}"):
                        if new_email != user.email:
                            user.email = new_email if new_email else None
                        if new_pass:
                            update_user_password(db, user.id, new_pass)
                        if new_role != user.role:
                            update_user_role(db, user.id, new_role)
                        db.commit()
                        st.session_state[f"editing_{user.id}"] = False
                        st.rerun()
                with edit_cols[4]:
                    if st.button("Cancel", key=f"cancel_{user.id}"):
                        st.session_state[f"editing_{user.id}"] = False
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # Delete confirmation appears BELOW the row
        if st.session_state.get(f"confirm_del_{user.id}"):
            del_cols = st.columns([4, 1, 1])
            with del_cols[0]:
                st.warning(f"Delete **{user.username}**? This cannot be undone!")
            with del_cols[1]:
                if st.button("Yes", key=f"confirm_delete_{user.id}", type="primary"):
                    delete_user(db, user.id)
                    st.session_state[f"confirm_del_{user.id}"] = False
                    st.rerun()
            with del_cols[2]:
                if st.button("No", key=f"cancel_delete_{user.id}"):
                    st.session_state[f"confirm_del_{user.id}"] = False
                    st.rerun()

with tab_create:
    st.markdown("### Create New User")

    with st.form("create_user"):
        form_cols = st.columns(2)

        with form_cols[0]:
            new_username = st.text_input("Username *")
            new_password = st.text_input("Password *", type="password")

        with form_cols[1]:
            new_email = st.text_input("Email")
            new_role = st.selectbox("Role", ["user", "admin"])

        submitted = st.form_submit_button("➕ Create User", use_container_width=True)

        if submitted:
            if not new_username:
                st.error("Username required")
            elif not new_password:
                st.error("Password required")
            elif len(new_password) < 6:
                st.error("Password must be 6+ characters")
            else:
                user = create_user(db, new_username, new_password,
                                  email=new_email if new_email else None,
                                  role=new_role)
                if user:
                    st.success(f"✅ Created user: {new_username}")
                else:
                    st.error("Username or email already exists")

db.close()
