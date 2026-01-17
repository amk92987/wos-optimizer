"""
Admin Database Tools - Database management and maintenance.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin
from database.models import (
    User, UserProfile, UserHero, UserInventory, Hero, Item,
    AdminMetrics, AuditLog, Announcement, Feedback
)
from sqlalchemy import text

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 🗄️ Database Tools")
st.caption("Database management and maintenance")

db = get_db()

# Database file info
db_path = PROJECT_ROOT / "wos.db"
db_exists = db_path.exists()

if db_exists:
    db_size = db_path.stat().st_size
    db_modified = datetime.fromtimestamp(db_path.stat().st_mtime)

    col1, col2, col3 = st.columns(3)
    with col1:
        size_mb = db_size / (1024 * 1024)
        st.metric("Database Size", f"{size_mb:.2f} MB")
    with col2:
        st.metric("Last Modified", db_modified.strftime("%m/%d/%y %I:%M %p"))
    with col3:
        st.metric("Status", "🟢 Healthy")
else:
    st.error("Database file not found!")

st.markdown("---")

# Tabs
tab_tables, tab_backup, tab_cleanup, tab_query = st.tabs(["📊 Tables", "💾 Backup", "🧹 Cleanup", "🔍 Query"])

with tab_tables:
    st.markdown("### Table Statistics")

    # Get counts for all tables
    from sqlalchemy import inspect
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()

    table_data = []
    for table in tables:
        try:
            # Try to get count
            count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            table_data.append({"Table": table, "Rows": count})
        except Exception:
            table_data.append({"Table": table, "Rows": "Error"})

    # Display as grid
    for i in range(0, len(table_data), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(table_data):
                item = table_data[i + j]
                with col:
                    st.markdown(f"""
                    <div style="background: rgba(74, 144, 217, 0.1); padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #3498DB;">{item['Rows']}</div>
                        <div style="font-size: 12px; color: #888; margin-top: 4px;">{item['Table']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")

    # Table browser
    st.markdown("### Browse Table Data")
    st.caption("View raw database records (read-only). Use this to inspect data or debug issues.")

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_table = st.selectbox("Select a table to view its records", tables)
    with col2:
        rows_per_page = st.selectbox("Rows", [10, 25, 50], index=1, key="rows_per_page")

    if selected_table:
        try:
            # Get total count
            total_count = db.execute(text(f"SELECT COUNT(*) FROM {selected_table}")).scalar()

            if total_count > 0:
                # Pagination
                total_pages = (total_count + rows_per_page - 1) // rows_per_page

                # Initialize page in session state
                page_key = f"page_{selected_table}"
                if page_key not in st.session_state:
                    st.session_state[page_key] = 1

                # Page navigation
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                with col1:
                    if st.button("⏮️", key="first_page", disabled=st.session_state[page_key] == 1):
                        st.session_state[page_key] = 1
                        st.rerun()
                with col2:
                    if st.button("◀️", key="prev_page", disabled=st.session_state[page_key] == 1):
                        st.session_state[page_key] -= 1
                        st.rerun()
                with col3:
                    st.markdown(f"<div style='text-align:center;padding-top:8px;'>Page {st.session_state[page_key]} of {total_pages}</div>", unsafe_allow_html=True)
                with col4:
                    if st.button("▶️", key="next_page", disabled=st.session_state[page_key] == total_pages):
                        st.session_state[page_key] += 1
                        st.rerun()
                with col5:
                    if st.button("⏭️", key="last_page", disabled=st.session_state[page_key] == total_pages):
                        st.session_state[page_key] = total_pages
                        st.rerun()

                # Calculate offset
                offset = (st.session_state[page_key] - 1) * rows_per_page

                # Get paginated results
                result = db.execute(text(f"SELECT * FROM {selected_table} LIMIT {rows_per_page} OFFSET {offset}")).fetchall()

                # Get column names
                columns = db.execute(text(f"PRAGMA table_info({selected_table})")).fetchall()
                col_names = [col[1] for col in columns]

                import pandas as pd
                df = pd.DataFrame(result, columns=col_names)
                st.dataframe(df, width="stretch", hide_index=True, height=400)

                start_row = offset + 1
                end_row = min(offset + rows_per_page, total_count)
                st.caption(f"Showing rows {start_row}-{end_row} of {total_count} in {selected_table}")
            else:
                st.info("Table is empty")
        except Exception as e:
            st.error(f"Error reading table: {e}")

with tab_backup:
    st.markdown("### Database Backup")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background: rgba(46, 204, 113, 0.1); padding: 20px; border-radius: 8px;">
            <h4 style="margin: 0 0 12px 0;">💾 Create Backup</h4>
            <p style="color: #888; font-size: 13px;">Download a copy of the database file.</p>
        </div>
        """, unsafe_allow_html=True)

        if db_exists:
            with open(db_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Database",
                    data=f.read(),
                    file_name=f"wos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                    mime="application/x-sqlite3",
                    width="stretch"
                )

    with col2:
        st.markdown("""
        <div style="background: rgba(241, 196, 15, 0.1); padding: 20px; border-radius: 8px;">
            <h4 style="margin: 0 0 12px 0;">📤 Export Data</h4>
            <p style="color: #888; font-size: 13px;">Export tables as CSV files.</p>
        </div>
        """, unsafe_allow_html=True)

        export_table = st.selectbox("Table to Export", tables, key="export_select")
        if st.button("📥 Export as CSV", width="stretch"):
            try:
                result = db.execute(text(f"SELECT * FROM {export_table}")).fetchall()
                columns = db.execute(text(f"PRAGMA table_info({export_table})")).fetchall()
                col_names = [col[1] for col in columns]

                import pandas as pd
                df = pd.DataFrame(result, columns=col_names)
                csv = df.to_csv(index=False)

                st.download_button(
                    label=f"⬇️ Download {export_table}.csv",
                    data=csv,
                    file_name=f"{export_table}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error exporting: {e}")

with tab_cleanup:
    st.markdown("### Database Cleanup")

    st.warning("⚠️ These operations cannot be undone. Create a backup first!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Clear Old Data")

        # Old metrics
        old_metrics = db.query(AdminMetrics).filter(
            AdminMetrics.date < datetime.now() - timedelta(days=90)
        ).count()
        st.markdown(f"📊 Old metrics (90+ days): **{old_metrics}** records")

        if st.button("🗑️ Delete Old Metrics", disabled=old_metrics == 0):
            db.query(AdminMetrics).filter(
                AdminMetrics.date < datetime.now() - timedelta(days=90)
            ).delete()
            db.commit()
            st.success(f"Deleted {old_metrics} old metrics records")
            st.rerun()

        # Old audit logs
        old_logs = db.query(AuditLog).filter(
            AuditLog.created_at < datetime.now() - timedelta(days=180)
        ).count()
        st.markdown(f"📜 Old audit logs (180+ days): **{old_logs}** records")

        if st.button("🗑️ Delete Old Audit Logs", disabled=old_logs == 0):
            db.query(AuditLog).filter(
                AuditLog.created_at < datetime.now() - timedelta(days=180)
            ).delete()
            db.commit()
            st.success(f"Deleted {old_logs} old audit log records")
            st.rerun()

    with col2:
        st.markdown("#### Danger Zone")

        st.markdown("""
        <div style="background: rgba(231, 76, 60, 0.1); padding: 16px; border-radius: 8px; border: 1px solid rgba(231, 76, 60, 0.3);">
            <p style="color: #E74C3C; font-size: 13px; margin: 0;">These actions are destructive!</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Clear all feedback
        feedback_count = db.query(Feedback).count()
        st.markdown(f"📝 Feedback entries: **{feedback_count}**")
        if st.button("🗑️ Clear All Feedback", disabled=feedback_count == 0):
            if st.session_state.get("confirm_clear_feedback"):
                db.query(Feedback).delete()
                db.commit()
                st.session_state["confirm_clear_feedback"] = False
                st.success("All feedback cleared")
                st.rerun()
            else:
                st.session_state["confirm_clear_feedback"] = True
                st.warning("Click again to confirm")

        # Vacuum database
        st.markdown("")
        if st.button("🧹 Vacuum Database", help="Reclaim unused space"):
            try:
                db.execute(text("VACUUM"))
                st.success("Database vacuumed successfully")
            except Exception as e:
                st.error(f"Error: {e}")

with tab_query:
    st.markdown("### SQL Query")
    st.warning("⚠️ Be careful with UPDATE/DELETE queries!")

    query = st.text_area("SQL Query", placeholder="SELECT * FROM users LIMIT 10", height=100)

    if st.button("▶️ Execute Query"):
        if query:
            try:
                # Safety check - prevent destructive queries without confirmation
                lower_query = query.lower().strip()
                if any(kw in lower_query for kw in ["drop", "delete", "update", "truncate", "alter"]):
                    if not st.session_state.get("confirm_dangerous_query"):
                        st.session_state["confirm_dangerous_query"] = True
                        st.warning("This is a potentially destructive query. Click Execute again to confirm.")
                    else:
                        result = db.execute(text(query))
                        db.commit()
                        st.success(f"Query executed. Rows affected: {result.rowcount}")
                        st.session_state["confirm_dangerous_query"] = False
                else:
                    result = db.execute(text(query)).fetchall()
                    if result:
                        import pandas as pd
                        df = pd.DataFrame(result)
                        st.dataframe(df, width="stretch")
                        st.caption(f"{len(result)} rows returned")
                    else:
                        st.info("Query returned no results")

            except Exception as e:
                st.error(f"Query error: {e}")
        else:
            st.warning("Enter a query first")

db.close()
