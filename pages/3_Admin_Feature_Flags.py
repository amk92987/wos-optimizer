"""
Admin Feature Flags - Control app features with toggles.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin
from database.models import FeatureFlag

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Compact styling
st.markdown("""
<style>
.flag-row {
    display: grid;
    grid-template-columns: 60px 200px 1fr 80px;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(74, 144, 217, 0.15);
}
.flag-row:hover {
    background: rgba(74, 144, 217, 0.08);
}
.flag-header {
    background: rgba(74, 144, 217, 0.2);
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
    color: #7DD3FC;
    border-radius: 6px 6px 0 0;
    padding: 10px 16px;
}
</style>
""", unsafe_allow_html=True)

require_admin()

st.markdown("# 🚩 Feature Flags")

db = get_db()

# Ensure table exists
from sqlalchemy import inspect
inspector = inspect(db.bind)
if 'feature_flags' not in inspector.get_table_names():
    FeatureFlag.__table__.create(db.bind, checkfirst=True)

# Feature flag metadata - display names and detailed descriptions
FLAG_METADATA = {
    "hero_recommendations": {
        "display_name": "Hero Recommendations",
        "icon": "🤖",
        "category": "AI Features",
        "description": "AI-powered hero upgrade recommendations",
        "details": [
            "AI Advisor page recommendations",
            "Hero priority scoring",
            "Upgrade path suggestions",
            "Resource optimization tips"
        ]
    },
    "inventory_ocr": {
        "display_name": "Inventory OCR",
        "icon": "📷",
        "category": "Scanning",
        "description": "Screenshot scanning for inventory",
        "details": [
            "Backpack screenshot scanning",
            "Auto-detection of item quantities",
            "Batch import from screenshots",
            "OCR error correction UI"
        ]
    },
    "alliance_features": {
        "display_name": "Alliance Tools",
        "icon": "🏰",
        "category": "Social",
        "description": "Alliance management and coordination",
        "details": [
            "Alliance member tracking",
            "Rally coordination tools",
            "Shared lineup planning",
            "Alliance event tracking"
        ]
    },
    "beta_features": {
        "display_name": "Beta Features",
        "icon": "🧪",
        "category": "Experimental",
        "description": "Experimental features in testing",
        "details": [
            "Unreleased functionality",
            "Features under development",
            "May contain bugs or change",
            "Early access for testing"
        ]
    },
    "maintenance_mode": {
        "display_name": "Maintenance Mode",
        "icon": "🔧",
        "category": "System",
        "description": "Show maintenance notice to users",
        "details": [
            "Displays maintenance banner",
            "Blocks new data submissions",
            "Allows read-only access",
            "Admin access unaffected"
        ]
    },
    "new_user_onboarding": {
        "display_name": "User Onboarding",
        "icon": "👋",
        "category": "UX",
        "description": "Guided setup for new users",
        "details": [
            "Welcome tour on first login",
            "Profile setup wizard",
            "Feature highlights",
            "Quick start guide prompts"
        ]
    },
    "dark_theme_only": {
        "display_name": "Force Dark Theme",
        "icon": "🌙",
        "category": "Display",
        "description": "Override user theme preference",
        "details": [
            "Forces Arctic Night theme",
            "Ignores user settings",
            "Useful for screenshots/demos",
            "Affects all users"
        ]
    },
    "analytics_tracking": {
        "display_name": "Analytics Tracking",
        "icon": "📊",
        "category": "Data",
        "description": "Detailed usage analytics collection",
        "details": [
            "Page view tracking",
            "Feature usage metrics",
            "User engagement data",
            "Admin dashboard charts"
        ]
    },
}

# Default feature flags
DEFAULT_FLAGS = [
    {"name": "hero_recommendations", "description": "AI-powered hero upgrade recommendations", "is_enabled": True},
    {"name": "inventory_ocr", "description": "Screenshot scanning for inventory", "is_enabled": False},
    {"name": "alliance_features", "description": "Alliance management and coordination", "is_enabled": False},
    {"name": "beta_features", "description": "Experimental features in testing", "is_enabled": False},
    {"name": "maintenance_mode", "description": "Show maintenance notice to users", "is_enabled": False},
    {"name": "new_user_onboarding", "description": "Guided setup for new users", "is_enabled": True},
    {"name": "dark_theme_only", "description": "Override user theme preference", "is_enabled": False},
    {"name": "analytics_tracking", "description": "Detailed usage analytics collection", "is_enabled": True},
]

# Seed defaults if empty
existing_count = db.query(FeatureFlag).count()
if existing_count == 0:
    for flag_data in DEFAULT_FLAGS:
        flag = FeatureFlag(**flag_data)
        db.add(flag)
    db.commit()
    st.rerun()

# Get flags
flags = db.query(FeatureFlag).order_by(FeatureFlag.name).all()
enabled_count = len([f for f in flags if f.is_enabled])

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total", len(flags))
with col2:
    st.metric("Enabled", enabled_count)
with col3:
    st.metric("Disabled", len(flags) - enabled_count)
with col4:
    categories = set(FLAG_METADATA.get(f.name, {}).get("category", "Other") for f in flags)
    st.metric("Categories", len(categories))

st.markdown("---")

# Filter
col1, col2 = st.columns([2, 1])
with col1:
    search = st.text_input("🔍 Search", placeholder="Search flags...", label_visibility="collapsed")
with col2:
    show_filter = st.selectbox("Show", ["All", "Enabled", "Disabled"], label_visibility="collapsed")

# Filter flags
filtered_flags = flags.copy()
if search:
    search_lower = search.lower()
    filtered_flags = [f for f in filtered_flags if
                     search_lower in f.name.lower() or
                     search_lower in FLAG_METADATA.get(f.name, {}).get("display_name", "").lower() or
                     search_lower in (f.description or "").lower()]

if show_filter == "Enabled":
    filtered_flags = [f for f in filtered_flags if f.is_enabled]
elif show_filter == "Disabled":
    filtered_flags = [f for f in filtered_flags if not f.is_enabled]

st.caption(f"Showing {len(filtered_flags)} flags")

# Table header
st.markdown("""
<div class="flag-header" style="display: grid; grid-template-columns: 60px 200px 1fr 80px;">
    <div>Status</div>
    <div>Feature</div>
    <div>Description</div>
    <div>Actions</div>
</div>
""", unsafe_allow_html=True)

# Flag rows
for flag in filtered_flags:
    meta = FLAG_METADATA.get(flag.name, {
        "display_name": flag.name.replace("_", " ").title(),
        "icon": "🚩",
        "category": "Custom",
        "description": flag.description or "No description",
        "details": []
    })

    cols = st.columns([0.8, 2.5, 4, 1])

    with cols[0]:
        new_state = st.toggle(
            f"Toggle {flag.name}",
            value=flag.is_enabled,
            key=f"toggle_{flag.id}",
            label_visibility="collapsed"
        )
        if new_state != flag.is_enabled:
            flag.is_enabled = new_state
            flag.updated_at = datetime.utcnow()
            db.commit()
            st.rerun()

    with cols[1]:
        status_color = "#2ECC71" if flag.is_enabled else "#666"
        st.markdown(f"""
        <div style="padding: 4px 0;">
            <span style="font-size: 16px;">{meta['icon']}</span>
            <strong style="margin-left: 6px; color: {status_color};">{meta['display_name']}</strong>
            <div style="font-size: 10px; color: #888; margin-top: 2px;">{meta['category']}</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f"<span style='color: #aaa; font-size: 13px;'>{meta['description']}</span>", unsafe_allow_html=True)
        # Show details on hover/expand
        if meta.get('details'):
            with st.expander("What's included"):
                for detail in meta['details']:
                    st.markdown(f"• {detail}")

    with cols[3]:
        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("✏️", key=f"edit_{flag.id}", help="Edit"):
                st.session_state[f"editing_flag_{flag.id}"] = True
        with btn_cols[1]:
            if st.button("🗑️", key=f"del_{flag.id}", help="Delete"):
                st.session_state[f"confirm_del_flag_{flag.id}"] = True

    # Edit form
    if st.session_state.get(f"editing_flag_{flag.id}"):
        with st.container():
            st.markdown(f"##### Edit: {meta['display_name']}")
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Internal Name", value=flag.name, key=f"name_{flag.id}",
                                        help="Used in code (lowercase, underscores)")
            with col2:
                new_desc = st.text_input("Description", value=flag.description or "", key=f"desc_{flag.id}")

            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("💾 Save", key=f"save_{flag.id}"):
                    flag.name = new_name.lower().replace(" ", "_")
                    flag.description = new_desc
                    flag.updated_at = datetime.utcnow()
                    db.commit()
                    st.session_state[f"editing_flag_{flag.id}"] = False
                    st.rerun()
            with col2:
                if st.button("Cancel", key=f"cancel_{flag.id}"):
                    st.session_state[f"editing_flag_{flag.id}"] = False
                    st.rerun()

    # Delete confirmation
    if st.session_state.get(f"confirm_del_flag_{flag.id}"):
        st.warning(f"Delete **{meta['display_name']}**? This cannot be undone.")
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🗑️ Delete", key=f"confirm_delete_{flag.id}", type="primary"):
                db.delete(flag)
                db.commit()
                st.session_state[f"confirm_del_flag_{flag.id}"] = False
                st.rerun()
        with col2:
            if st.button("Cancel", key=f"cancel_del_{flag.id}"):
                st.session_state[f"confirm_del_flag_{flag.id}"] = False
                st.rerun()

st.markdown("---")

# Create new flag section
with st.expander("➕ Create New Flag"):
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Internal Name", placeholder="feature_name", key="new_flag_name",
                                help="Lowercase with underscores")
    with col2:
        new_desc = st.text_input("Description", placeholder="What does this flag control?", key="new_flag_desc")

    new_enabled = st.checkbox("Enable immediately", key="new_flag_enabled")

    if st.button("🚩 Create Flag", use_container_width=True):
        if not new_name:
            st.error("Name is required")
        elif not new_name.replace("_", "").replace(" ", "").isalnum():
            st.error("Name must be alphanumeric (underscores allowed)")
        else:
            clean_name = new_name.lower().replace(" ", "_")
            if db.query(FeatureFlag).filter(FeatureFlag.name == clean_name).first():
                st.error("Flag with this name already exists")
            else:
                new_flag = FeatureFlag(
                    name=clean_name,
                    description=new_desc,
                    is_enabled=new_enabled
                )
                db.add(new_flag)
                db.commit()
                st.success(f"Created: {clean_name}")
                st.rerun()

# Quick actions
st.markdown("### Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✅ Enable All", use_container_width=True):
        for flag in flags:
            flag.is_enabled = True
        db.commit()
        st.rerun()

with col2:
    if st.button("❌ Disable All", use_container_width=True):
        for flag in flags:
            flag.is_enabled = False
        db.commit()
        st.rerun()

with col3:
    if st.button("🔄 Reset Defaults", use_container_width=True):
        db.query(FeatureFlag).delete()
        for flag_data in DEFAULT_FLAGS:
            flag = FeatureFlag(**flag_data)
            db.add(flag)
        db.commit()
        st.rerun()

db.close()
