"""
Admin Page - User management for Bear's Den.
Only accessible to users with admin role.
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db
from database.auth import (
    require_admin, is_admin, get_all_users, create_user,
    update_user_password, update_user_role, delete_user,
    get_user_by_id, init_session_state
)

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Check admin access
require_admin()

st.markdown("# Admin Panel")
st.markdown("Manage user accounts and system settings.")

db = get_db()

# Tabs for different admin functions
tab_users, tab_create, tab_system = st.tabs(["Users", "Create User", "System"])

with tab_users:
    st.markdown("## User Management")

    users = get_all_users(db)

    if not users:
        st.info("No users found.")
    else:
        # User table
        for user in users:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 2, 1.5])

                with col1:
                    role_icon = "👑" if user.role == 'admin' else "👤"
                    status_icon = "✓" if user.is_active else "✗"
                    st.markdown(f"**{role_icon} {user.username}**")

                with col2:
                    st.caption(user.email or "No email")

                with col3:
                    st.caption(f"{'Active' if user.is_active else 'Inactive'}")

                with col4:
                    if user.last_login:
                        st.caption(f"Last: {user.last_login.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.caption("Never logged in")

                with col5:
                    # Actions
                    if st.button("Edit", key=f"edit_{user.id}"):
                        st.session_state[f"editing_user_{user.id}"] = True

                # Edit form (shown when edit button is clicked)
                if st.session_state.get(f"editing_user_{user.id}", False):
                    with st.expander(f"Edit {user.username}", expanded=True):
                        edit_col1, edit_col2 = st.columns(2)

                        with edit_col1:
                            new_password = st.text_input(
                                "New Password",
                                type="password",
                                key=f"new_pass_{user.id}",
                                help="Leave blank to keep current password"
                            )

                        with edit_col2:
                            new_role = st.selectbox(
                                "Role",
                                options=['user', 'admin'],
                                index=0 if user.role == 'user' else 1,
                                key=f"role_{user.id}"
                            )

                        btn_col1, btn_col2, btn_col3 = st.columns(3)

                        with btn_col1:
                            if st.button("Save Changes", key=f"save_{user.id}"):
                                changed = False
                                if new_password:
                                    update_user_password(db, user.id, new_password)
                                    changed = True
                                if new_role != user.role:
                                    update_user_role(db, user.id, new_role)
                                    changed = True
                                if changed:
                                    st.success("User updated!")
                                    st.session_state[f"editing_user_{user.id}"] = False
                                    st.rerun()
                                else:
                                    st.info("No changes made.")

                        with btn_col2:
                            if st.button("Cancel", key=f"cancel_{user.id}"):
                                st.session_state[f"editing_user_{user.id}"] = False
                                st.rerun()

                        with btn_col3:
                            # Don't allow deleting yourself
                            if user.id != st.session_state.user_id:
                                if st.button("Delete User", key=f"delete_{user.id}", type="secondary"):
                                    st.session_state[f"confirm_delete_{user.id}"] = True

                        # Delete confirmation
                        if st.session_state.get(f"confirm_delete_{user.id}", False):
                            st.warning(f"Are you sure you want to delete **{user.username}**?")
                            del_col1, del_col2 = st.columns(2)
                            with del_col1:
                                if st.button("Yes, Delete", key=f"confirm_del_{user.id}", type="primary"):
                                    delete_user(db, user.id)
                                    st.success(f"User {user.username} deleted.")
                                    st.session_state[f"confirm_delete_{user.id}"] = False
                                    st.session_state[f"editing_user_{user.id}"] = False
                                    st.rerun()
                            with del_col2:
                                if st.button("No, Cancel", key=f"cancel_del_{user.id}"):
                                    st.session_state[f"confirm_delete_{user.id}"] = False
                                    st.rerun()

                st.divider()

with tab_create:
    st.markdown("## Create New User")

    with st.form("create_user_form"):
        new_username = st.text_input("Username", max_chars=50)
        new_email = st.text_input("Email (optional)", max_chars=255)
        new_user_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        new_user_role = st.selectbox("Role", options=['user', 'admin'])

        submitted = st.form_submit_button("Create User")

        if submitted:
            if not new_username:
                st.error("Username is required.")
            elif not new_user_password:
                st.error("Password is required.")
            elif new_user_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_user_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                user = create_user(
                    db,
                    username=new_username,
                    password=new_user_password,
                    email=new_email if new_email else None,
                    role=new_user_role
                )
                if user:
                    st.success(f"User **{new_username}** created successfully!")
                else:
                    st.error("Username or email already exists.")

with tab_system:
    st.markdown("## System Information")

    # User stats
    total_users = len(get_all_users(db))
    admin_count = len([u for u in get_all_users(db) if u.role == 'admin'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Admins", admin_count)
    with col3:
        st.metric("Regular Users", total_users - admin_count)

    st.markdown("---")

    st.markdown("### AWS Migration Status")
    st.markdown("""
    <div class="info-card">
        <strong>Current Setup:</strong> Local SQLite database with bcrypt password hashing<br><br>
        <strong>AWS Migration Path:</strong>
        <ul>
            <li>Database → Amazon RDS (PostgreSQL)</li>
            <li>Authentication → AWS Cognito (cognito_sub field ready)</li>
            <li>Email Verification → AWS SES</li>
            <li>Hosting → AWS ECS or Elastic Beanstalk</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Database Info")
    db_path = PROJECT_ROOT / "wos.db"
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        st.caption(f"Database: {db_path.name} ({size_mb:.2f} MB)")
    else:
        st.caption("Database file not found (may be using different location)")

db.close()
