"""
Admin Data Integrity - Check and fix data issues.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin
from database.models import (
    User, UserProfile, UserHero, UserInventory, Hero, Item,
    UserChiefGear, UserChiefCharm, Feedback, UpgradeHistory
)

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 🔍 Data Integrity")
st.caption("Check and fix data issues")

db = get_db()


def run_integrity_checks():
    """Run all integrity checks and return results."""
    results = []

    # 1. Check for orphaned profiles (no user)
    orphan_profiles = db.query(UserProfile).filter(
        UserProfile.user_id.isnot(None),
        ~UserProfile.user_id.in_(db.query(User.id))
    ).all()
    results.append({
        "name": "Orphaned Profiles",
        "description": "Profiles with deleted user accounts",
        "count": len(orphan_profiles),
        "severity": "warning" if orphan_profiles else "ok",
        "fix_action": "delete_orphan_profiles",
        "items": [f"Profile ID {p.id}: {p.name}" for p in orphan_profiles[:5]]
    })

    # 2. Check for orphaned user heroes (no profile)
    orphan_heroes = db.query(UserHero).filter(
        ~UserHero.profile_id.in_(db.query(UserProfile.id))
    ).all()
    results.append({
        "name": "Orphaned User Heroes",
        "description": "Hero records with deleted profiles",
        "count": len(orphan_heroes),
        "severity": "warning" if orphan_heroes else "ok",
        "fix_action": "delete_orphan_heroes",
        "items": [f"UserHero ID {h.id}" for h in orphan_heroes[:5]]
    })

    # 3. Check for orphaned inventory (no profile)
    orphan_inv = db.query(UserInventory).filter(
        ~UserInventory.profile_id.in_(db.query(UserProfile.id))
    ).all()
    results.append({
        "name": "Orphaned Inventory",
        "description": "Inventory records with deleted profiles",
        "count": len(orphan_inv),
        "severity": "warning" if orphan_inv else "ok",
        "fix_action": "delete_orphan_inventory",
        "items": [f"Inventory ID {i.id}" for i in orphan_inv[:5]]
    })

    # 4. Check for user heroes referencing non-existent heroes
    invalid_hero_refs = db.query(UserHero).filter(
        ~UserHero.hero_id.in_(db.query(Hero.id))
    ).all()
    results.append({
        "name": "Invalid Hero References",
        "description": "User heroes referencing deleted hero templates",
        "count": len(invalid_hero_refs),
        "severity": "error" if invalid_hero_refs else "ok",
        "fix_action": "delete_invalid_hero_refs",
        "items": [f"UserHero ID {h.id} -> Hero ID {h.hero_id}" for h in invalid_hero_refs[:5]]
    })

    # 5. Check for inventory referencing non-existent items
    invalid_item_refs = db.query(UserInventory).filter(
        ~UserInventory.item_id.in_(db.query(Item.id))
    ).all()
    results.append({
        "name": "Invalid Item References",
        "description": "Inventory referencing deleted item templates",
        "count": len(invalid_item_refs),
        "severity": "error" if invalid_item_refs else "ok",
        "fix_action": "delete_invalid_item_refs",
        "items": [f"Inventory ID {i.id} -> Item ID {i.item_id}" for i in invalid_item_refs[:5]]
    })

    # 6. Check for duplicate user profiles per user
    from sqlalchemy import func
    duplicate_profiles = db.query(
        UserProfile.user_id, func.count(UserProfile.id).label('count')
    ).filter(UserProfile.user_id.isnot(None)).group_by(UserProfile.user_id).having(func.count(UserProfile.id) > 1).all()
    results.append({
        "name": "Duplicate Profiles",
        "description": "Users with multiple profiles",
        "count": len(duplicate_profiles),
        "severity": "info" if duplicate_profiles else "ok",
        "fix_action": None,
        "items": [f"User ID {d[0]} has {d[1]} profiles" for d in duplicate_profiles[:5]]
    })

    # 7. Check for users without profiles
    users_no_profile = db.query(User).filter(
        User.role == 'user',
        ~User.id.in_(db.query(UserProfile.user_id).filter(UserProfile.user_id.isnot(None)))
    ).all()
    results.append({
        "name": "Users Without Profiles",
        "description": "User accounts without a game profile",
        "count": len(users_no_profile),
        "severity": "info" if users_no_profile else "ok",
        "fix_action": "create_missing_profiles",
        "items": [f"{u.username} (ID {u.id})" for u in users_no_profile[:5]]
    })

    # 8. Check for out-of-range hero levels
    invalid_hero_levels = db.query(UserHero).filter(
        (UserHero.level < 1) | (UserHero.level > 80)
    ).all()
    results.append({
        "name": "Invalid Hero Levels",
        "description": "Heroes with level < 1 or > 80",
        "count": len(invalid_hero_levels),
        "severity": "warning" if invalid_hero_levels else "ok",
        "fix_action": "fix_hero_levels",
        "items": [f"UserHero ID {h.id}: Level {h.level}" for h in invalid_hero_levels[:5]]
    })

    # 9. Check for negative inventory quantities
    negative_inv = db.query(UserInventory).filter(UserInventory.quantity < 0).all()
    results.append({
        "name": "Negative Inventory",
        "description": "Items with negative quantity",
        "count": len(negative_inv),
        "severity": "error" if negative_inv else "ok",
        "fix_action": "fix_negative_inventory",
        "items": [f"Inventory ID {i.id}: Qty {i.quantity}" for i in negative_inv[:5]]
    })

    # 10. Check for null/empty usernames
    null_usernames = db.query(User).filter(
        (User.username.is_(None)) | (User.username == '')
    ).all()
    results.append({
        "name": "Null/Empty Usernames",
        "description": "Users with no username",
        "count": len(null_usernames),
        "severity": "error" if null_usernames else "ok",
        "fix_action": None,
        "items": [f"User ID {u.id}" for u in null_usernames[:5]]
    })

    return results


# Run checks
if st.button("🔄 Run Integrity Checks", width="stretch"):
    st.session_state["integrity_results"] = run_integrity_checks()

# Display results
if "integrity_results" in st.session_state:
    results = st.session_state["integrity_results"]

    # Summary
    issues = sum(1 for r in results if r["severity"] in ["warning", "error"])
    ok = sum(1 for r in results if r["severity"] == "ok")
    info = sum(1 for r in results if r["severity"] == "info")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Checks", len(results))
    with col2:
        st.metric("Passed", ok)
    with col3:
        st.metric("Issues", issues)
    with col4:
        st.metric("Info", info)

    st.markdown("---")

    # Detailed results
    for result in results:
        severity_styles = {
            "ok": ("✅", "#2ECC71", "rgba(46, 204, 113, 0.1)"),
            "info": ("ℹ️", "#3498DB", "rgba(52, 152, 219, 0.1)"),
            "warning": ("⚠️", "#F1C40F", "rgba(241, 196, 15, 0.1)"),
            "error": ("🚨", "#E74C3C", "rgba(231, 76, 60, 0.1)")
        }

        icon, color, bg = severity_styles.get(result["severity"], ("❓", "#888", "rgba(0,0,0,0.1)"))

        with st.container():
            st.markdown(f"""
            <div style="background: {bg}; padding: 16px; border-radius: 8px; margin-bottom: 8px;
                        border-left: 3px solid {color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 16px;">{icon}</span>
                        <strong style="margin-left: 8px;">{result['name']}</strong>
                    </div>
                    <div style="font-size: 20px; font-weight: bold; color: {color};">{result['count']}</div>
                </div>
                <div style="color: #888; font-size: 13px; margin-top: 4px;">{result['description']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Show items if any
            if result["items"]:
                with st.expander("View Details"):
                    for item in result["items"]:
                        st.caption(f"• {item}")
                    if result["count"] > 5:
                        st.caption(f"... and {result['count'] - 5} more")

            # Fix button
            if result["fix_action"] and result["count"] > 0:
                if st.button(f"🔧 Fix {result['name']}", key=f"fix_{result['fix_action']}"):
                    action = result["fix_action"]

                    if action == "delete_orphan_profiles":
                        db.query(UserProfile).filter(
                            UserProfile.user_id.isnot(None),
                            ~UserProfile.user_id.in_(db.query(User.id))
                        ).delete(synchronize_session=False)
                        db.commit()
                        st.success(f"Deleted {result['count']} orphaned profiles")

                    elif action == "delete_orphan_heroes":
                        db.query(UserHero).filter(
                            ~UserHero.profile_id.in_(db.query(UserProfile.id))
                        ).delete(synchronize_session=False)
                        db.commit()
                        st.success(f"Deleted {result['count']} orphaned user heroes")

                    elif action == "delete_orphan_inventory":
                        db.query(UserInventory).filter(
                            ~UserInventory.profile_id.in_(db.query(UserProfile.id))
                        ).delete(synchronize_session=False)
                        db.commit()
                        st.success(f"Deleted {result['count']} orphaned inventory records")

                    elif action == "delete_invalid_hero_refs":
                        db.query(UserHero).filter(
                            ~UserHero.hero_id.in_(db.query(Hero.id))
                        ).delete(synchronize_session=False)
                        db.commit()
                        st.success(f"Deleted {result['count']} invalid hero references")

                    elif action == "delete_invalid_item_refs":
                        db.query(UserInventory).filter(
                            ~UserInventory.item_id.in_(db.query(Item.id))
                        ).delete(synchronize_session=False)
                        db.commit()
                        st.success(f"Deleted {result['count']} invalid item references")

                    elif action == "create_missing_profiles":
                        users = db.query(User).filter(
                            User.role == 'user',
                            ~User.id.in_(db.query(UserProfile.user_id).filter(UserProfile.user_id.isnot(None)))
                        ).all()
                        for user in users:
                            profile = UserProfile(user_id=user.id, name=user.username)
                            db.add(profile)
                        db.commit()
                        st.success(f"Created {len(users)} missing profiles")

                    elif action == "fix_hero_levels":
                        # Clamp levels to valid range
                        db.query(UserHero).filter(UserHero.level < 1).update({"level": 1})
                        db.query(UserHero).filter(UserHero.level > 80).update({"level": 80})
                        db.commit()
                        st.success("Fixed invalid hero levels")

                    elif action == "fix_negative_inventory":
                        db.query(UserInventory).filter(UserInventory.quantity < 0).update({"quantity": 0})
                        db.commit()
                        st.success("Fixed negative inventory quantities")

                    # Re-run checks
                    st.session_state["integrity_results"] = run_integrity_checks()
                    st.rerun()

else:
    st.info("Click 'Run Integrity Checks' to scan the database for issues.")

st.markdown("---")

# Quick actions
st.markdown("### Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔧 Fix All Safe Issues", width="stretch",
                help="Fix orphaned records and invalid references"):
        # Run all safe fixes
        fixed = 0

        # Delete orphaned profiles
        count = db.query(UserProfile).filter(
            UserProfile.user_id.isnot(None),
            ~UserProfile.user_id.in_(db.query(User.id))
        ).delete(synchronize_session=False)
        fixed += count

        # Delete orphaned heroes
        count = db.query(UserHero).filter(
            ~UserHero.profile_id.in_(db.query(UserProfile.id))
        ).delete(synchronize_session=False)
        fixed += count

        # Delete orphaned inventory
        count = db.query(UserInventory).filter(
            ~UserInventory.profile_id.in_(db.query(UserProfile.id))
        ).delete(synchronize_session=False)
        fixed += count

        # Delete invalid references
        count = db.query(UserHero).filter(
            ~UserHero.hero_id.in_(db.query(Hero.id))
        ).delete(synchronize_session=False)
        fixed += count

        count = db.query(UserInventory).filter(
            ~UserInventory.item_id.in_(db.query(Item.id))
        ).delete(synchronize_session=False)
        fixed += count

        db.commit()
        st.success(f"Fixed {fixed} issues")

        # Re-run checks
        st.session_state["integrity_results"] = run_integrity_checks()
        st.rerun()

with col2:
    if st.button("📊 Refresh Checks", width="stretch"):
        st.session_state["integrity_results"] = run_integrity_checks()
        st.rerun()

db.close()
