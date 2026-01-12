"""
Admin Usage Reports - Detailed usage analytics and reports.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin, get_all_users
from database.models import (
    User, UserProfile, UserHero, UserInventory, Hero,
    AdminMetrics, AuditLog
)

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 📈 Usage Reports")
st.caption("Detailed usage analytics and reports")

db = get_db()

# Time range selector
col1, col2 = st.columns([1, 3])
with col1:
    time_range = st.selectbox("Time Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])

# Calculate date range
now = datetime.now()
if time_range == "Last 7 Days":
    start_date = now - timedelta(days=7)
elif time_range == "Last 30 Days":
    start_date = now - timedelta(days=30)
elif time_range == "Last 90 Days":
    start_date = now - timedelta(days=90)
else:
    start_date = datetime.min

# Get all users
all_users = get_all_users(db)
regular_users = [u for u in all_users if u.role != 'admin']

st.markdown("---")

# Tabs
tab_overview, tab_users, tab_content, tab_trends = st.tabs(["📊 Overview", "👥 User Activity", "📦 Content Usage", "📈 Trends"])

with tab_overview:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = len(regular_users)
        st.markdown(f"""
        <div style="background: rgba(52, 152, 219, 0.15); padding: 20px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; font-weight: bold; color: #3498DB;">{total}</div>
            <div style="font-size: 12px; color: #888;">Total Users</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        active = len([u for u in regular_users if u.last_login and u.last_login >= start_date])
        st.markdown(f"""
        <div style="background: rgba(46, 204, 113, 0.15); padding: 20px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; font-weight: bold; color: #2ECC71;">{active}</div>
            <div style="font-size: 12px; color: #888;">Active Users</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        new = len([u for u in regular_users if u.created_at and u.created_at >= start_date])
        st.markdown(f"""
        <div style="background: rgba(155, 89, 182, 0.15); padding: 20px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; font-weight: bold; color: #9B59B6;">{new}</div>
            <div style="font-size: 12px; color: #888;">New Users</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        if total > 0:
            activity_rate = (active / total) * 100
        else:
            activity_rate = 0
        rate_color = "#2ECC71" if activity_rate >= 50 else "#F1C40F" if activity_rate >= 25 else "#E74C3C"
        st.markdown(f"""
        <div style="background: rgba(241, 196, 15, 0.15); padding: 20px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; font-weight: bold; color: {rate_color};">{activity_rate:.0f}%</div>
            <div style="font-size: 12px; color: #888;">Activity Rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Activity breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Activity Breakdown")

        # Calculate activity tiers
        very_active = len([u for u in regular_users if u.last_login and (now - u.last_login).days <= 1])
        active_weekly = len([u for u in regular_users if u.last_login and 1 < (now - u.last_login).days <= 7])
        active_monthly = len([u for u in regular_users if u.last_login and 7 < (now - u.last_login).days <= 30])
        inactive = len([u for u in regular_users if not u.last_login or (now - u.last_login).days > 30])

        st.markdown(f"""
        <div style="background: rgba(74, 144, 217, 0.1); padding: 16px; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span>🟢 Very Active (daily)</span>
                <strong style="color: #2ECC71;">{very_active}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span>🔵 Active (weekly)</span>
                <strong style="color: #3498DB;">{active_weekly}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span>🟡 Occasional (monthly)</span>
                <strong style="color: #F1C40F;">{active_monthly}</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>🔴 Inactive (30d+)</span>
                <strong style="color: #E74C3C;">{inactive}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Content Created")

        total_profiles = db.query(UserProfile).count()
        total_heroes = db.query(UserHero).count()
        total_inventory = db.query(UserInventory).count()

        st.markdown(f"""
        <div style="background: rgba(74, 144, 217, 0.1); padding: 16px; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span>👤 Profiles Created</span>
                <strong>{total_profiles}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span>🦸 Heroes Tracked</span>
                <strong>{total_heroes}</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>🎒 Inventory Items</span>
                <strong>{total_inventory}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_users:
    st.markdown("### User Activity Details")

    # Sort options
    sort_by = st.selectbox("Sort By", ["Last Active", "Most Heroes", "Most Items", "Newest", "Oldest"])

    # Get user data with metrics
    user_data = []
    for user in regular_users:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        hero_count = db.query(UserHero).filter(UserHero.profile_id == profile.id).count() if profile else 0
        inventory_count = db.query(UserInventory).filter(UserInventory.profile_id == profile.id).count() if profile else 0

        # Activity score (days active estimation)
        if user.last_login:
            days_since = (now - user.last_login).days
            if days_since == 0:
                activity_score = 7
            elif days_since <= 1:
                activity_score = 5
            elif days_since <= 7:
                activity_score = 3
            else:
                activity_score = 0
        else:
            activity_score = 0

        user_data.append({
            "user": user,
            "profile": profile,
            "heroes": hero_count,
            "items": inventory_count,
            "activity_score": activity_score,
            "last_login": user.last_login
        })

    # Sort
    if sort_by == "Last Active":
        user_data.sort(key=lambda x: x["last_login"] or datetime.min, reverse=True)
    elif sort_by == "Most Heroes":
        user_data.sort(key=lambda x: x["heroes"], reverse=True)
    elif sort_by == "Most Items":
        user_data.sort(key=lambda x: x["items"], reverse=True)
    elif sort_by == "Newest":
        user_data.sort(key=lambda x: x["user"].created_at or datetime.min, reverse=True)
    else:
        user_data.sort(key=lambda x: x["user"].created_at or datetime.min)

    # Display table header
    st.markdown("""
    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; padding: 8px 12px;
                background: rgba(74, 144, 217, 0.2); border-radius: 6px; font-size: 12px;
                font-weight: bold; color: #7DD3FC; text-transform: uppercase;">
        <div>User</div>
        <div>Heroes</div>
        <div>Items</div>
        <div>Activity</div>
        <div>Last Active</div>
    </div>
    """, unsafe_allow_html=True)

    for data in user_data[:50]:  # Show top 50
        user = data["user"]
        last_active = "Never"
        if user.last_login:
            days = (now - user.last_login).days
            if days == 0:
                last_active = "Today"
            elif days == 1:
                last_active = "Yesterday"
            elif days < 7:
                last_active = f"{days}d ago"
            else:
                last_active = user.last_login.strftime("%m/%d/%y")

        activity_color = "#2ECC71" if data["activity_score"] >= 5 else "#F1C40F" if data["activity_score"] >= 2 else "#E74C3C"

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; padding: 10px 12px;
                    border-bottom: 1px solid rgba(74, 144, 217, 0.15); font-size: 13px; align-items: center;">
            <div><strong>{user.username}</strong></div>
            <div>{data['heroes']}</div>
            <div>{data['items']}</div>
            <div style="color: {activity_color};">{data['activity_score']}/7</div>
            <div style="color: #888;">{last_active}</div>
        </div>
        """, unsafe_allow_html=True)

    if len(user_data) > 50:
        st.caption(f"Showing 50 of {len(user_data)} users")

with tab_content:
    st.markdown("### Content Usage Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Most Popular Heroes")

        # Count hero usage
        from sqlalchemy import func
        hero_counts = db.query(
            Hero.name, func.count(UserHero.id).label('count')
        ).join(UserHero).group_by(Hero.id).order_by(func.count(UserHero.id).desc()).limit(10).all()

        if hero_counts:
            max_count = hero_counts[0][1] if hero_counts else 1
            for hero_name, count in hero_counts:
                pct = (count / max_count) * 100
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>{hero_name}</span>
                        <strong>{count}</strong>
                    </div>
                    <div style="background: rgba(74, 144, 217, 0.2); border-radius: 4px; height: 8px;">
                        <div style="background: #3498DB; width: {pct}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hero data yet")

    with col2:
        st.markdown("#### Hero Class Distribution")

        class_counts = db.query(
            Hero.hero_class, func.count(UserHero.id).label('count')
        ).join(UserHero).group_by(Hero.hero_class).all()

        if class_counts:
            total = sum(c[1] for c in class_counts)
            class_icons = {"Infantry": "🛡️", "Marksman": "🏹", "Lancer": "🗡️"}
            class_colors = {"Infantry": "#E74C3C", "Marksman": "#2ECC71", "Lancer": "#3498DB"}

            for hero_class, count in class_counts:
                pct = (count / total) * 100 if total > 0 else 0
                icon = class_icons.get(hero_class, "❓")
                color = class_colors.get(hero_class, "#888")

                st.markdown(f"""
                <div style="background: rgba(74, 144, 217, 0.1); padding: 16px; border-radius: 8px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 20px;">{icon}</span>
                            <strong style="margin-left: 8px;">{hero_class}</strong>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 18px; font-weight: bold; color: {color};">{count}</div>
                            <div style="font-size: 11px; color: #888;">{pct:.1f}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hero data yet")

    st.markdown("---")

    st.markdown("#### Profile Settings Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # Spending profiles
        spending_counts = db.query(
            UserProfile.spending_profile, func.count(UserProfile.id).label('count')
        ).group_by(UserProfile.spending_profile).all()

        if spending_counts:
            st.markdown("**Spending Profile**")
            for profile, count in spending_counts:
                st.markdown(f"- {profile or 'Not set'}: **{count}**")
        else:
            st.info("No profile data")

    with col2:
        # Alliance roles
        role_counts = db.query(
            UserProfile.alliance_role, func.count(UserProfile.id).label('count')
        ).group_by(UserProfile.alliance_role).all()

        if role_counts:
            st.markdown("**Alliance Role**")
            for role, count in role_counts:
                st.markdown(f"- {role or 'Not set'}: **{count}**")
        else:
            st.info("No profile data")

    st.markdown("---")

    # State Distribution
    st.markdown("#### State Distribution")

    state_counts = db.query(
        UserProfile.state_number, func.count(UserProfile.id).label('count')
    ).filter(UserProfile.state_number != None).group_by(UserProfile.state_number).order_by(func.count(UserProfile.id).desc()).all()

    if state_counts:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Users by State**")
            total_with_state = sum(c[1] for c in state_counts)
            max_count = state_counts[0][1] if state_counts else 1

            for state, count in state_counts[:15]:  # Show top 15 states
                pct = (count / max_count) * 100
                st.markdown(f"""
                <div style="margin-bottom: 6px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                        <span>State {state}</span>
                        <strong>{count}</strong>
                    </div>
                    <div style="background: rgba(74, 144, 217, 0.2); border-radius: 4px; height: 6px;">
                        <div style="background: #9B59B6; width: {pct}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if len(state_counts) > 15:
                st.caption(f"Showing top 15 of {len(state_counts)} states")

        with col2:
            st.markdown("**State Summary**")
            profiles_without_state = db.query(UserProfile).filter(
                (UserProfile.state_number == None) | (UserProfile.state_number == 0)
            ).count()

            st.markdown(f"""
            <div style="background: rgba(74, 144, 217, 0.1); padding: 16px; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span>🌍 Unique States</span>
                    <strong style="color: #9B59B6;">{len(state_counts)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span>👥 Users with State</span>
                    <strong style="color: #2ECC71;">{total_with_state}</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>❓ No State Set</span>
                    <strong style="color: #E74C3C;">{profiles_without_state}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No state data yet. Users can set their state in Settings.")

with tab_trends:
    st.markdown("### Historical Trends")

    # Get historical metrics
    import pandas as pd

    metrics = db.query(AdminMetrics).order_by(AdminMetrics.date.desc()).limit(90).all()

    if metrics:
        data = []
        for m in reversed(metrics):
            data.append({
                'Date': m.date.strftime('%m/%d'),
                'Total Users': m.total_users,
                'Active Users': m.active_users,
                'New Users': m.new_users,
                'Heroes': m.total_heroes_tracked or 0
            })

        df = pd.DataFrame(data)

        # User growth chart
        st.markdown("#### User Growth")
        st.line_chart(df.set_index('Date')[['Total Users']], color=["#3498DB"])

        # Active users chart
        st.markdown("#### Active Users")
        st.bar_chart(df.set_index('Date')[['Active Users']], color=["#2ECC71"])

        # New users chart
        st.markdown("#### New Registrations")
        st.bar_chart(df.set_index('Date')[['New Users']], color=["#9B59B6"])

    else:
        st.info("Not enough historical data yet. Charts will appear after a few days of data collection.")

db.close()
