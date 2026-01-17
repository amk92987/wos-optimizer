"""
Admin Export Analytics - Export data in various formats.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys
import json
import io

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin, get_all_users
from database.models import (
    User, UserProfile, UserHero, UserInventory, Hero, Item,
    AdminMetrics, AuditLog, Announcement, Feedback
)

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 📤 Export Analytics")
st.caption("Export data in various formats")

db = get_db()

st.markdown("---")

# Tabs
tab_reports, tab_data, tab_backup = st.tabs(["📊 Reports", "📁 Data Export", "💾 Full Backup"])

with tab_reports:
    st.markdown("### Generate Reports")

    import pandas as pd

    report_type = st.selectbox("Report Type", [
        "User Summary",
        "Activity Report",
        "Content Statistics",
        "Hero Usage",
        "Growth Metrics"
    ])

    # Time range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())

    if st.button("📊 Generate Report", width="stretch"):
        report_data = None
        report_name = ""

        if report_type == "User Summary":
            users = get_all_users(db)
            data = []
            for user in users:
                profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                hero_count = db.query(UserHero).filter(UserHero.profile_id == profile.id).count() if profile else 0

                data.append({
                    "Username": user.username,
                    "Email": user.email or "",
                    "Role": user.role,
                    "State": profile.state_number if profile and profile.state_number else "",
                    "Is Active": user.is_active,
                    "Created": user.created_at.strftime("%Y-%m-%d") if user.created_at else "",
                    "Last Login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never",
                    "Profile Name": profile.name if profile else "",
                    "Heroes Tracked": hero_count
                })

            report_data = pd.DataFrame(data)
            report_name = "user_summary"

        elif report_type == "Activity Report":
            users = get_all_users(db)
            regular = [u for u in users if u.role != 'admin']

            now = datetime.now()
            data = []
            for user in regular:
                if user.last_login:
                    days_since = (now - user.last_login).days
                    if days_since == 0:
                        status = "Active Today"
                    elif days_since <= 7:
                        status = "Active This Week"
                    elif days_since <= 30:
                        status = "Active This Month"
                    else:
                        status = "Inactive"
                else:
                    status = "Never Logged In"

                data.append({
                    "Username": user.username,
                    "Status": status,
                    "Last Login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never",
                    "Days Since Login": days_since if user.last_login else None,
                    "Account Created": user.created_at.strftime("%Y-%m-%d") if user.created_at else ""
                })

            report_data = pd.DataFrame(data)
            report_name = "activity_report"

        elif report_type == "Content Statistics":
            profiles = db.query(UserProfile).all()
            data = []
            for profile in profiles:
                user = db.query(User).filter(User.id == profile.user_id).first()
                hero_count = db.query(UserHero).filter(UserHero.profile_id == profile.id).count()
                inv_count = db.query(UserInventory).filter(UserInventory.profile_id == profile.id).count()

                data.append({
                    "Profile Name": profile.name,
                    "Username": user.username if user else "Unknown",
                    "State": profile.state_number or "",
                    "Server Age (Days)": profile.server_age_days,
                    "Furnace Level": profile.furnace_level,
                    "Spending Profile": profile.spending_profile,
                    "Alliance Role": profile.alliance_role,
                    "Heroes Tracked": hero_count,
                    "Inventory Items": inv_count
                })

            report_data = pd.DataFrame(data)
            report_name = "content_stats"

        elif report_type == "Hero Usage":
            from sqlalchemy import func

            hero_usage = db.query(
                Hero.name, Hero.hero_class, Hero.rarity, Hero.generation,
                func.count(UserHero.id).label('users')
            ).outerjoin(UserHero).group_by(Hero.id).order_by(func.count(UserHero.id).desc()).all()

            data = []
            for name, hero_class, rarity, gen, users in hero_usage:
                data.append({
                    "Hero": name,
                    "Class": hero_class,
                    "Rarity": rarity,
                    "Generation": gen,
                    "Users Tracking": users
                })

            report_data = pd.DataFrame(data)
            report_name = "hero_usage"

        elif report_type == "Growth Metrics":
            metrics = db.query(AdminMetrics).filter(
                AdminMetrics.date >= datetime.combine(start_date, datetime.min.time()),
                AdminMetrics.date <= datetime.combine(end_date, datetime.max.time())
            ).order_by(AdminMetrics.date).all()

            data = []
            for m in metrics:
                data.append({
                    "Date": m.date.strftime("%Y-%m-%d"),
                    "Total Users": m.total_users,
                    "New Users": m.new_users,
                    "Active Users": m.active_users,
                    "Total Profiles": m.total_profiles,
                    "Heroes Tracked": m.total_heroes_tracked,
                    "Inventory Items": m.total_inventory_items
                })

            report_data = pd.DataFrame(data)
            report_name = "growth_metrics"

        if report_data is not None and not report_data.empty:
            st.success(f"Report generated with {len(report_data)} rows")

            # Preview
            st.dataframe(report_data, width="stretch")

            # Download options
            col1, col2 = st.columns(2)

            with col1:
                csv = report_data.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"{report_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    width="stretch"
                )

            with col2:
                # Excel export
                buffer = io.BytesIO()
                report_data.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)
                st.download_button(
                    label="⬇️ Download Excel",
                    data=buffer,
                    file_name=f"{report_name}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch"
                )
        else:
            st.warning("No data found for this report")

with tab_data:
    st.markdown("### Export Raw Data")

    st.caption("Export individual tables as CSV or JSON")

    tables = {
        "Users": (User, ["id", "username", "email", "role", "is_active", "created_at", "last_login"]),
        "Profiles": (UserProfile, ["id", "user_id", "name", "state_number", "server_age_days", "furnace_level", "spending_profile", "alliance_role"]),
        "User Heroes": (UserHero, ["id", "profile_id", "hero_id", "level", "stars", "owned"]),
        "Heroes (Reference)": (Hero, ["id", "name", "generation", "hero_class", "rarity", "tier_overall"]),
        "Items (Reference)": (Item, ["id", "name", "category", "subcategory", "rarity"]),
        "Feedback": (Feedback, ["id", "user_id", "category", "page", "description", "status", "created_at"]),
        "Audit Log": (AuditLog, ["id", "admin_username", "action", "target_name", "details", "created_at"]),
        "Admin Metrics": (AdminMetrics, ["id", "date", "total_users", "new_users", "active_users"]),
        "Announcements": (Announcement, ["id", "title", "message", "type", "is_active", "created_at"])
    }

    selected_table = st.selectbox("Select Table", list(tables.keys()))

    if selected_table:
        model, columns = tables[selected_table]

        # Get count
        count = db.query(model).count()
        st.caption(f"{count} records")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Export as CSV", width="stretch"):
                import pandas as pd

                records = db.query(model).all()
                data = []
                for record in records:
                    row = {}
                    for col in columns:
                        val = getattr(record, col, None)
                        if isinstance(val, datetime):
                            val = val.strftime("%Y-%m-%d %H:%M:%S")
                        row[col] = val
                    data.append(row)

                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)

                st.download_button(
                    label=f"⬇️ Download {selected_table}.csv",
                    data=csv,
                    file_name=f"{selected_table.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("📥 Export as JSON", width="stretch"):
                records = db.query(model).all()
                data = []
                for record in records:
                    row = {}
                    for col in columns:
                        val = getattr(record, col, None)
                        if isinstance(val, datetime):
                            val = val.isoformat()
                        row[col] = val
                    data.append(row)

                json_str = json.dumps(data, indent=2)

                st.download_button(
                    label=f"⬇️ Download {selected_table}.json",
                    data=json_str,
                    file_name=f"{selected_table.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )

with tab_backup:
    st.markdown("### Full System Backup")

    st.markdown("""
    <div style="background: rgba(52, 152, 219, 0.1); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h4 style="margin: 0 0 12px 0;">💾 Database Backup</h4>
        <p style="color: #888; font-size: 13px;">Download a complete copy of the SQLite database file.</p>
    </div>
    """, unsafe_allow_html=True)

    db_path = PROJECT_ROOT / "wos.db"

    if db_path.exists():
        db_size = db_path.stat().st_size / (1024 * 1024)
        st.caption(f"Database size: {db_size:.2f} MB")

        with open(db_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Full Database",
                data=f.read(),
                file_name=f"wos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                mime="application/x-sqlite3",
                width="stretch"
            )

    st.markdown("---")

    st.markdown("""
    <div style="background: rgba(155, 89, 182, 0.1); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h4 style="margin: 0 0 12px 0;">📦 Export All Data</h4>
        <p style="color: #888; font-size: 13px;">Export all tables as a ZIP file containing CSV files.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📦 Generate Full Export", width="stretch"):
        import zipfile

        # Create zip in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for table_name, (model, columns) in tables.items():
                try:
                    records = db.query(model).all()
                    data = []
                    for record in records:
                        row = {}
                        for col in columns:
                            val = getattr(record, col, None)
                            if isinstance(val, datetime):
                                val = val.strftime("%Y-%m-%d %H:%M:%S")
                            row[col] = val
                        data.append(row)

                    import pandas as pd
                    df = pd.DataFrame(data)
                    csv_content = df.to_csv(index=False)

                    filename = f"{table_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}.csv"
                    zip_file.writestr(filename, csv_content)
                except Exception as e:
                    st.warning(f"Could not export {table_name}: {e}")

        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Download ZIP Archive",
            data=zip_buffer.getvalue(),
            file_name=f"wos_full_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            width="stretch"
        )

        st.success("Export package ready!")

db.close()
