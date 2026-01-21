"""
Admin Dashboard - System overview and analytics for administrators.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, date
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin, get_all_users, login_as_user
from database.models import User, UserProfile, UserHero, UserInventory, AdminMetrics, AuditLog, Announcement, Base, ErrorLog
from utils.error_logger import get_error_summary

# Ensure tables exist
init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Require admin access
require_admin()

db = get_db()

# Create new tables if they don't exist
from sqlalchemy import inspect
inspector = inspect(db.get_bind())
existing_tables = inspector.get_table_names()
if 'admin_metrics' not in existing_tables:
    AdminMetrics.__table__.create(db.get_bind(), checkfirst=True)
if 'audit_log' not in existing_tables:
    AuditLog.__table__.create(db.get_bind(), checkfirst=True)
if 'announcements' not in existing_tables:
    Announcement.__table__.create(db.get_bind(), checkfirst=True)


def record_daily_metrics():
    """Record today's metrics snapshot (excludes test accounts)."""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    # Check if we already have today's metrics
    existing = db.query(AdminMetrics).filter(AdminMetrics.date == today_start).first()
    if existing:
        return  # Already recorded

    all_users = get_all_users(db)
    # Exclude admins and test accounts from metrics
    regular_users = [u for u in all_users if u.role != 'admin' and not u.is_test_account]
    test_and_admin_ids = [u.id for u in all_users if u.role == 'admin' or u.is_test_account]

    # Calculate metrics (excluding test accounts)
    total_users = len(regular_users)
    new_users = len([u for u in regular_users if u.created_at and u.created_at >= today_start])
    active_users = len([u for u in regular_users if u.last_login and u.last_login >= today_start])

    # Exclude test account data from content stats
    if test_and_admin_ids:
        total_profiles = db.query(UserProfile).filter(~UserProfile.user_id.in_(test_and_admin_ids)).count()
        total_heroes = db.query(UserHero).join(UserProfile).filter(~UserProfile.user_id.in_(test_and_admin_ids)).count()
        total_inventory = db.query(UserInventory).join(UserProfile).filter(~UserProfile.user_id.in_(test_and_admin_ids)).count()
    else:
        total_profiles = db.query(UserProfile).count()
        total_heroes = db.query(UserHero).count()
        total_inventory = db.query(UserInventory).count()

    # Create metrics record
    metrics = AdminMetrics(
        date=today_start,
        total_users=total_users,
        new_users=new_users,
        active_users=active_users,
        total_profiles=total_profiles,
        total_heroes_tracked=total_heroes,
        total_inventory_items=total_inventory,
        total_logins=active_users  # Simplified
    )
    db.add(metrics)
    db.commit()


def get_historical_metrics(days: int = 30) -> pd.DataFrame:
    """Get historical metrics for charting."""
    cutoff = datetime.now() - timedelta(days=days)
    metrics = db.query(AdminMetrics).filter(AdminMetrics.date >= cutoff).order_by(AdminMetrics.date).all()

    if not metrics:
        return pd.DataFrame()

    data = []
    for m in metrics:
        data.append({
            'Date': m.date.strftime('%m/%d'),
            'Users': m.total_users,
            'Active': m.active_users,
            'New': m.new_users,
            'Heroes': m.total_heroes_tracked,
        })

    return pd.DataFrame(data)


# Record today's metrics
record_daily_metrics()

# ============================================
# Header
# ============================================

st.markdown("# 📊 Admin Dashboard")
st.caption(f"System overview • {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

# ============================================
# Calculate current metrics
# ============================================

all_users = get_all_users(db)
now = datetime.now()

# Separate admins from regular users, exclude test accounts from metrics
admin_users = [u for u in all_users if u.role == 'admin']
test_users = [u for u in all_users if u.is_test_account]
regular_users = [u for u in all_users if u.role != 'admin' and not u.is_test_account]

# Active users calculations (regular users only)
def count_active_users(users: list, days: int) -> int:
    cutoff = now - timedelta(days=days)
    return len([u for u in users if u.last_login and u.last_login >= cutoff])

dau = count_active_users(regular_users, 1)
wau = count_active_users(regular_users, 7)
mau = count_active_users(regular_users, 30)

# New users (regular users only)
new_today = len([u for u in regular_users if u.created_at and u.created_at >= now - timedelta(days=1)])
new_this_week = len([u for u in regular_users if u.created_at and u.created_at >= now - timedelta(days=7)])
new_this_month = len([u for u in regular_users if u.created_at and u.created_at >= now - timedelta(days=30)])

# Content stats (exclude test account data)
test_user_ids = [u.id for u in test_users]
admin_user_ids = [u.id for u in admin_users]
excluded_user_ids = test_user_ids + admin_user_ids

if excluded_user_ids:
    total_profiles = db.query(UserProfile).filter(~UserProfile.user_id.in_(excluded_user_ids)).count()
    total_heroes_tracked = db.query(UserHero).join(UserProfile).filter(~UserProfile.user_id.in_(excluded_user_ids)).count()
    total_inventory_items = db.query(UserInventory).join(UserProfile).filter(~UserProfile.user_id.in_(excluded_user_ids)).count()
    # Count unique states
    from sqlalchemy import func
    unique_states = db.query(func.count(func.distinct(UserProfile.state_number))).filter(
        ~UserProfile.user_id.in_(excluded_user_ids),
        UserProfile.state_number.isnot(None)
    ).scalar() or 0
else:
    total_profiles = db.query(UserProfile).count()
    total_heroes_tracked = db.query(UserHero).count()
    total_inventory_items = db.query(UserInventory).count()
    from sqlalchemy import func
    unique_states = db.query(func.count(func.distinct(UserProfile.state_number))).filter(
        UserProfile.state_number.isnot(None)
    ).scalar() or 0

# Inactive users (30+ days)
inactive_30d = len([u for u in regular_users if not u.last_login or u.last_login < now - timedelta(days=30)])

# ============================================
# Top KPI Cards
# ============================================

st.markdown("### Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(52, 152, 219, 0.2), rgba(52, 152, 219, 0.1));
                padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(52, 152, 219, 0.3);">
        <div style="font-size: 32px; font-weight: bold; color: #3498DB;">{len(regular_users)}</div>
        <div style="font-size: 12px; color: #888; margin-top: 4px;">Total Users</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    delta_color = "#2ECC71" if new_this_week > 0 else "#888"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.2), rgba(46, 204, 113, 0.1));
                padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(46, 204, 113, 0.3);">
        <div style="font-size: 32px; font-weight: bold; color: #2ECC71;">{dau}</div>
        <div style="font-size: 12px; color: #888; margin-top: 4px;">Active Today</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(155, 89, 182, 0.2), rgba(155, 89, 182, 0.1));
                padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(155, 89, 182, 0.3);">
        <div style="font-size: 32px; font-weight: bold; color: #9B59B6;">{wau}</div>
        <div style="font-size: 12px; color: #888; margin-top: 4px;">Active This Week</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(241, 196, 15, 0.2), rgba(241, 196, 15, 0.1));
                padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(241, 196, 15, 0.3);">
        <div style="font-size: 32px; font-weight: bold; color: #F1C40F;">{total_profiles}</div>
        <div style="font-size: 12px; color: #888; margin-top: 4px;">Chiefs Created</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(230, 126, 34, 0.2), rgba(230, 126, 34, 0.1));
                padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(230, 126, 34, 0.3);">
        <div style="font-size: 32px; font-weight: bold; color: #E67E22;">{unique_states}</div>
        <div style="font-size: 12px; color: #888; margin-top: 4px;">States Represented</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# Charts Section
# ============================================

st.markdown("### Trends")

# Time period filter
time_options = {
    "1 Week": 7,
    "1 Month": 30,
    "3 Months": 90,
    "Custom": -1
}

col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 4])
with col_filter1:
    time_selection = st.selectbox("Time Period", list(time_options.keys()), index=1, key="chart_time_period")

# Handle custom date range
if time_selection == "Custom":
    with col_filter2:
        start_date = st.date_input("Start", value=date.today() - timedelta(days=30), key="chart_start")
    with col_filter3:
        end_date = st.date_input("End", value=date.today(), key="chart_end")
    days_to_show = (end_date - start_date).days
else:
    days_to_show = time_options[time_selection]

# Get historical data
historical_df = get_historical_metrics(days_to_show)

if not historical_df.empty and len(historical_df) > 1:
    import altair as alt

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("##### User Growth")
        # Create Altair line chart
        user_chart = alt.Chart(historical_df).mark_line(
            strokeWidth=3,
            color='#3498DB'
        ).encode(
            x=alt.X('Date:N', axis=alt.Axis(labelAngle=-45, title=None)),
            y=alt.Y('Users:Q', axis=alt.Axis(title='Total Users')),
            tooltip=['Date', 'Users']
        ).properties(height=250)

        # Add points
        points = alt.Chart(historical_df).mark_circle(
            size=60,
            color='#3498DB'
        ).encode(
            x='Date:N',
            y='Users:Q',
            tooltip=['Date', 'Users']
        )

        st.altair_chart(user_chart + points, width="stretch")

    with chart_col2:
        st.markdown("##### Daily Active Users")
        # Create Altair bar chart
        active_chart = alt.Chart(historical_df).mark_bar(
            color='#2ECC71',
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4
        ).encode(
            x=alt.X('Date:N', axis=alt.Axis(labelAngle=-45, title=None)),
            y=alt.Y('Active:Q', axis=alt.Axis(title='Active Users')),
            tooltip=['Date', 'Active']
        ).properties(height=250)

        st.altair_chart(active_chart, width="stretch")

else:
    st.info("📈 Charts will appear after a few days of data collection. Check back soon!")

    # Show sample/placeholder
    st.markdown("""
    <div style="background: rgba(74, 144, 217, 0.1); padding: 40px; border-radius: 12px; text-align: center; border: 1px dashed rgba(74, 144, 217, 0.3);">
        <div style="font-size: 48px; margin-bottom: 12px;">📊</div>
        <div style="color: #888;">Historical data is being collected.</div>
        <div style="color: #666; font-size: 12px; margin-top: 8px;">Daily snapshots are recorded automatically.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# Two column layout for detailed stats
# ============================================

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### New Registrations")

    reg_col1, reg_col2, reg_col3 = st.columns(3)
    with reg_col1:
        st.markdown(f"""
        <div style="background: rgba(46, 204, 113, 0.15); padding: 20px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; font-weight: bold; color: #2ECC71;">{new_today}</div>
            <div style="font-size: 11px; color: #888;">Today</div>
        </div>
        """, unsafe_allow_html=True)
    with reg_col2:
        st.markdown(f"""
        <div style="background: rgba(52, 152, 219, 0.15); padding: 20px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; font-weight: bold; color: #3498DB;">{new_this_week}</div>
            <div style="font-size: 11px; color: #888;">This Week</div>
        </div>
        """, unsafe_allow_html=True)
    with reg_col3:
        st.markdown(f"""
        <div style="background: rgba(155, 89, 182, 0.15); padding: 20px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; font-weight: bold; color: #9B59B6;">{new_this_month}</div>
            <div style="font-size: 11px; color: #888;">This Month</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### User Health")

    # Retention indicator
    if len(regular_users) > 0:
        retention_rate = ((len(regular_users) - inactive_30d) / len(regular_users)) * 100
    else:
        retention_rate = 0

    retention_color = "#2ECC71" if retention_rate >= 70 else "#F1C40F" if retention_rate >= 40 else "#E74C3C"

    st.markdown(f"""
    <div style="background: rgba(74, 144, 217, 0.1); padding: 16px; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <span>Active Users (30d)</span>
            <strong style="color: #2ECC71;">{len(regular_users) - inactive_30d}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <span>Inactive Users (30d+)</span>
            <strong style="color: #E74C3C;">{inactive_30d}</strong>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Retention Rate</span>
            <strong style="color: {retention_color};">{retention_rate:.0f}%</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### Content Statistics")

    st.markdown(f"""
    <div style="background: rgba(74, 144, 217, 0.1); padding: 20px; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
            <span>👤 Chiefs/Profiles</span>
            <strong style="font-size: 18px;">{total_profiles}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
            <span>🦸 Heroes Tracked</span>
            <strong style="font-size: 18px;">{total_heroes_tracked}</strong>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>🎒 Inventory Items</span>
            <strong style="font-size: 18px;">{total_inventory_items}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### System Status")

    db_path = PROJECT_ROOT / "wos.db"
    db_size = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0

    # Get error summary
    error_summary = get_error_summary()
    new_errors = error_summary.get('new', 0)
    errors_24h = error_summary.get('last_24h', 0)

    # Determine status based on errors
    if new_errors > 5:
        status_color = "#E74C3C"
        status_text = "Needs Attention"
        status_icon = "🔴"
    elif new_errors > 0:
        status_color = "#F1C40F"
        status_text = "Has New Errors"
        status_icon = "🟡"
    else:
        status_color = "#2ECC71"
        status_text = "Healthy"
        status_icon = "🟢"

    st.markdown(f"""
    <div style="background: rgba(46, 204, 113, 0.1); padding: 16px; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <span>💾 Database Size</span>
            <strong>{db_size:.2f} MB</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <span>👑 Admin Accounts</span>
            <strong>{len(admin_users)}</strong>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>{status_icon} Status</span>
            <strong style="color: {status_color};">{status_text}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Error metrics
    st.markdown("")
    st.markdown("### Error Tracking")

    error_color = "#E74C3C" if new_errors > 0 else "#2ECC71"
    st.markdown(f"""
    <div style="background: rgba(231, 76, 60, 0.1); padding: 16px; border-radius: 8px; border: 1px solid rgba(231, 76, 60, 0.2);">
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <span>🆕 New Errors</span>
            <strong style="color: {error_color};">{new_errors}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <span>📊 Last 24 Hours</span>
            <strong>{errors_24h}</strong>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>✅ Fixed</span>
            <strong style="color: #2ECC71;">{error_summary.get('fixed', 0)}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if new_errors > 0:
        if st.button("View Errors", key="view_errors_btn", use_container_width=True):
            st.switch_page("pages/5_Admin_Inbox.py")

st.markdown("---")

# ============================================
# Recent Activity
# ============================================

st.markdown("### Recent User Activity")

# Get recent logins (regular users only, last 10)
recent_users = sorted(
    [u for u in regular_users if u.last_login],
    key=lambda x: x.last_login,
    reverse=True
)[:8]

if recent_users:
    for user in recent_users:
        time_ago = now - user.last_login
        if time_ago.days > 0:
            time_str = f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600}h ago"
        elif time_ago.seconds > 60:
            time_str = f"{time_ago.seconds // 60}m ago"
        else:
            time_str = "Just now"

        col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])

        with col1:
            st.markdown(f"🛡️ **{user.username}**")

        with col2:
            st.caption(user.email or "No email")

        with col3:
            st.caption(time_str)

        with col4:
            if st.button("👁️", key=f"view_{user.id}", help=f"View as {user.username}"):
                login_as_user(user)
                st.rerun()
else:
    st.info("No recent user activity.")

st.markdown("---")

# ============================================
# Admin Tools
# ============================================

st.markdown("### Admin Tools")

tool_col1, tool_col2, tool_col3 = st.columns(3)

with tool_col1:
    st.markdown("""
    <div style="background: rgba(155, 89, 182, 0.1); padding: 16px; border-radius: 8px; border: 1px solid rgba(155, 89, 182, 0.3);">
        <div style="font-size: 14px; font-weight: bold; margin-bottom: 8px;">Test Accounts</div>
        <div style="font-size: 12px; color: #888; margin-bottom: 12px;">Create/reset test users for QA testing</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Create Test Accounts", key="create_test_accounts", use_container_width=True):
        with st.spinner("Creating test accounts..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "test_ai_comprehensive.py"), "--create-only"],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0:
                st.success("Test accounts created successfully!")
                st.code(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
            else:
                st.error("Failed to create test accounts")
                st.code(result.stderr[-500:] if result.stderr else "No error output")

with tool_col2:
    st.markdown("""
    <div style="background: rgba(52, 152, 219, 0.1); padding: 16px; border-radius: 8px; border: 1px solid rgba(52, 152, 219, 0.3);">
        <div style="font-size: 14px; font-weight: bold; margin-bottom: 8px;">Data Audit</div>
        <div style="font-size: 12px; color: #888; margin-bottom: 12px;">Validate game data files</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Run Data Audit", key="run_data_audit", use_container_width=True):
        with st.spinner("Running data audit..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "run_data_audit.py")],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0:
                st.success("Data audit completed!")
                st.code(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            else:
                st.warning("Data audit found issues")
                st.code(result.stdout[-1500:] if result.stdout else result.stderr[-500:])

with tool_col3:
    st.markdown("""
    <div style="background: rgba(46, 204, 113, 0.1); padding: 16px; border-radius: 8px; border: 1px solid rgba(46, 204, 113, 0.3);">
        <div style="font-size: 14px; font-weight: bold; margin-bottom: 8px;">QA Check</div>
        <div style="font-size: 12px; color: #888; margin-bottom: 12px;">Run web app QA validation</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Run QA Check", key="run_qa_check", use_container_width=True):
        with st.spinner("Running QA check..."):
            import subprocess
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "run_qa_check.py")],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0:
                st.success("QA check passed!")
                st.code(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            else:
                st.warning("QA check found issues")
                st.code(result.stdout[-1500:] if result.stdout else result.stderr[-500:])

db.close()
