"""
Profiles Page - Manage your game profiles.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile, get_user_profiles
from database.models import UserHero, Hero, UserProfile

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

from database.auth import get_current_user_id
user_id = get_current_user_id()


def switch_to_profile(profile_id: int):
    """Switch to a different profile."""
    st.session_state.profile_id = profile_id
    st.rerun()


def delete_profile(profile_id: int, hard_delete: bool = False) -> tuple[bool, str]:
    """Delete a profile. Soft delete by default (30 day recovery), or hard delete for test accounts."""
    from datetime import datetime
    from database.models import User
    try:
        p = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not p:
            return False, "Profile not found"

        # Check if this is a test account - hard delete those
        user = db.query(User).filter(User.id == p.user_id).first()
        is_test = user and user.is_test_account

        if hard_delete or is_test:
            # Permanent delete
            db.query(UserHero).filter(UserHero.profile_id == profile_id).delete()
            db.query(UserProfile).filter(UserProfile.id == profile_id).delete()
            db.commit()
            return True, "Profile permanently deleted"
        else:
            # Soft delete
            p.deleted_at = datetime.utcnow()
            db.commit()
            return True, "Profile deleted"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_deleted_profiles(uid: int):
    """Get soft-deleted profiles for a user."""
    return db.query(UserProfile).filter(
        UserProfile.user_id == uid,
        UserProfile.deleted_at.isnot(None)
    ).order_by(UserProfile.deleted_at.desc()).all()


def restore_profile(profile_id: int) -> tuple[bool, str]:
    """Restore a soft-deleted profile."""
    try:
        p = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.deleted_at.isnot(None)
        ).first()
        if p:
            p.deleted_at = None
            db.commit()
            return True, "Profile restored"
        return False, "Profile not found or not deleted"
    except Exception as e:
        return False, f"Error: {str(e)}"


def update_profile(profile_id: int, new_name: str, state_number: int = None) -> tuple[bool, str]:
    """Update a profile's name and state number."""
    try:
        p = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if p:
            p.name = new_name
            p.state_number = state_number
            db.commit()
            return True, "Profile updated"
        return False, "Profile not found"
    except Exception as e:
        return False, f"Error: {str(e)}"


def duplicate_profile(profile_id: int, new_name: str) -> tuple[bool, str, int]:
    """Duplicate a profile with all its heroes."""
    try:
        original = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not original:
            return False, "Profile not found", None

        # Create new profile with same settings
        new_profile = UserProfile(
            user_id=original.user_id,
            name=new_name,
            state_number=original.state_number,
            server_age_days=original.server_age_days,
            furnace_level=original.furnace_level,
            furnace_fc_level=original.furnace_fc_level,
            spending_profile=original.spending_profile,
            priority_focus=original.priority_focus,
            alliance_role=original.alliance_role,
            is_farm_account=False,  # Don't copy farm status
            priority_svs=original.priority_svs,
            priority_rally=original.priority_rally,
            priority_castle_battle=original.priority_castle_battle,
            priority_exploration=original.priority_exploration,
            priority_gathering=original.priority_gathering,
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        # Copy all heroes
        original_heroes = db.query(UserHero).filter(UserHero.profile_id == profile_id).all()
        for hero in original_heroes:
            new_hero = UserHero(
                profile_id=new_profile.id,
                hero_id=hero.hero_id,
                level=hero.level,
                stars=hero.stars,
                ascension_tier=hero.ascension_tier,
                exploration_skill_1_level=hero.exploration_skill_1_level,
                exploration_skill_2_level=hero.exploration_skill_2_level,
                exploration_skill_3_level=hero.exploration_skill_3_level,
                expedition_skill_1_level=hero.expedition_skill_1_level,
                expedition_skill_2_level=hero.expedition_skill_2_level,
                expedition_skill_3_level=hero.expedition_skill_3_level,
                gear_slot1_quality=hero.gear_slot1_quality,
                gear_slot1_level=hero.gear_slot1_level,
                gear_slot1_mastery=hero.gear_slot1_mastery,
                gear_slot2_quality=hero.gear_slot2_quality,
                gear_slot2_level=hero.gear_slot2_level,
                gear_slot2_mastery=hero.gear_slot2_mastery,
                gear_slot3_quality=hero.gear_slot3_quality,
                gear_slot3_level=hero.gear_slot3_level,
                gear_slot3_mastery=hero.gear_slot3_mastery,
                gear_slot4_quality=hero.gear_slot4_quality,
                gear_slot4_level=hero.gear_slot4_level,
                gear_slot4_mastery=hero.gear_slot4_mastery,
                mythic_gear_unlocked=hero.mythic_gear_unlocked,
                mythic_gear_quality=hero.mythic_gear_quality,
                mythic_gear_level=hero.mythic_gear_level,
                mythic_gear_mastery=hero.mythic_gear_mastery,
            )
            db.add(new_hero)

        db.commit()
        return True, f"Duplicated with {len(original_heroes)} heroes", new_profile.id
    except Exception as e:
        return False, f"Error: {str(e)}", None


# Page content
st.markdown("# 👤 Profiles")

st.info("Your profile data is **automatically saved** as you make changes. Use this page to manage multiple profiles (main account, farms, etc).")

st.markdown("---")

# Current profile summary
st.markdown("## 📊 Current Profile")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Chief Name", profile.name or "Chief")
with col2:
    state_num = profile.state_number if hasattr(profile, 'state_number') and profile.state_number else "N/A"
    st.metric("State #", state_num)
with col3:
    st.metric("Server Age", f"Day {profile.server_age_days}")
with col4:
    hero_count = db.query(UserHero).filter(UserHero.profile_id == profile.id).count()
    st.metric("Heroes Saved", hero_count)
with col5:
    fc_display = profile.furnace_fc_level if profile.furnace_fc_level else f"Lv.{profile.furnace_level}"
    st.metric("Furnace", fc_display)

st.markdown("---")

# Your Profiles section
st.markdown("## 👥 Your Profiles")

if user_id:
    all_user_profiles = get_user_profiles(db, user_id)

    if len(all_user_profiles) == 0:
        st.info("No profiles found. Create one below.")
    else:
        st.caption(f"You have {len(all_user_profiles)} profile(s).")

        for p in all_user_profiles:
            is_current = p.id == profile.id
            farm_badge = " 🌾" if p.is_farm_account else ""
            fc_text = p.furnace_fc_level if p.furnace_fc_level else f"Lv.{p.furnace_level}"
            hero_count_p = db.query(UserHero).filter(UserHero.profile_id == p.id).count()

            # Profile row with buttons
            with st.container():
                # Check for pending actions on this profile
                edit_key = f"editing_{p.id}"
                delete_key = f"confirm_delete_{p.id}"
                preview_key = f"show_preview_{p.id}"
                duplicate_key = f"duplicating_{p.id}"

                # Main row
                prof_col1, prof_col2, prof_col3, prof_col4, prof_col5, prof_col6, prof_col7 = st.columns([2.5, 1, 1, 1.2, 1, 1.3, 0.5])

                with prof_col1:
                    if is_current:
                        st.markdown(f"**✓ {p.name}**{farm_badge}")
                    else:
                        st.markdown(f"{p.name}{farm_badge}")
                    st.caption(f"State {p.state_number or 'N/A'} | {fc_text} | {hero_count_p} heroes")

                with prof_col2:
                    if not is_current:
                        if st.button("Switch", key=f"switch_{p.id}", width="stretch"):
                            switch_to_profile(p.id)
                    else:
                        st.caption("(current)")

                with prof_col3:
                    if st.button("Preview", key=f"preview_btn_{p.id}", width="stretch"):
                        st.session_state[preview_key] = not st.session_state.get(preview_key, False)

                with prof_col4:
                    if p.is_farm_account:
                        # Show as selected/active farm
                        if st.button("🌾 Farm", key=f"farm_{p.id}", width="stretch", type="primary"):
                            p.is_farm_account = False
                            db.commit()
                            st.rerun()
                    else:
                        if st.button("Mark Farm", key=f"farm_{p.id}", width="stretch"):
                            p.is_farm_account = True
                            db.commit()
                            st.rerun()

                with prof_col5:
                    # Edit button (name + state)
                    if st.button("Edit", key=f"edit_btn_{p.id}", width="stretch"):
                        st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                        # Close other dialogs
                        st.session_state[delete_key] = False
                        st.session_state[duplicate_key] = False

                with prof_col6:
                    # Duplicate button
                    if st.button("Duplicate", key=f"dup_btn_{p.id}", width="stretch"):
                        st.session_state[duplicate_key] = not st.session_state.get(duplicate_key, False)
                        # Close other dialogs
                        st.session_state[edit_key] = False
                        st.session_state[delete_key] = False

                with prof_col7:
                    # Delete button (trash icon)
                    if st.button("🗑️", key=f"delete_btn_{p.id}", width="stretch"):
                        st.session_state[delete_key] = not st.session_state.get(delete_key, False)
                        # Close other dialogs
                        st.session_state[edit_key] = False
                        st.session_state[duplicate_key] = False

                # Edit dialog (using form so Enter key works)
                if st.session_state.get(edit_key, False):
                    with st.form(key=f"edit_form_{p.id}"):
                        edit_col1, edit_col2, edit_col3, edit_col4 = st.columns([2, 1, 1, 1])
                        with edit_col1:
                            new_name = st.text_input(
                                "Profile Name",
                                value=p.name,
                                key=f"edit_name_{p.id}",
                                placeholder="Profile name"
                            )
                        with edit_col2:
                            new_state = st.number_input(
                                "State #",
                                min_value=1,
                                max_value=9999,
                                value=p.state_number if p.state_number else 1,
                                key=f"edit_state_{p.id}"
                            )
                        with edit_col3:
                            st.markdown("<br>", unsafe_allow_html=True)
                            save_clicked = st.form_submit_button("Save", type="primary", width="stretch")
                        with edit_col4:
                            st.markdown("<br>", unsafe_allow_html=True)
                            cancel_clicked = st.form_submit_button("Cancel", width="stretch")

                    if save_clicked:
                        if new_name and new_name.strip():
                            success, msg = update_profile(p.id, new_name.strip(), new_state)
                            if success:
                                st.session_state[edit_key] = False
                                st.toast("Profile updated")
                                st.rerun()
                            else:
                                st.error(msg)
                    if cancel_clicked:
                        st.session_state[edit_key] = False
                        st.rerun()

                # Duplicate dialog
                if st.session_state.get(duplicate_key, False):
                    with st.form(key=f"dup_form_{p.id}"):
                        dup_col1, dup_col2, dup_col3 = st.columns([3, 1, 1])
                        with dup_col1:
                            dup_name = st.text_input(
                                "New profile name",
                                value=f"{p.name}_copy",
                                key=f"dup_name_{p.id}",
                                placeholder="Name for the copy"
                            )
                        with dup_col2:
                            st.markdown("<br>", unsafe_allow_html=True)
                            dup_clicked = st.form_submit_button("Duplicate", type="primary", width="stretch")
                        with dup_col3:
                            st.markdown("<br>", unsafe_allow_html=True)
                            dup_cancel = st.form_submit_button("Cancel", width="stretch")

                    if dup_clicked:
                        if dup_name and dup_name.strip():
                            success, msg, new_id = duplicate_profile(p.id, dup_name.strip())
                            if success:
                                st.session_state[duplicate_key] = False
                                st.toast(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    if dup_cancel:
                        st.session_state[duplicate_key] = False
                        st.rerun()

                # Delete confirmation dialog
                if st.session_state.get(delete_key, False):
                    if is_current:
                        st.warning("Cannot delete your current profile. Switch to another profile first.")
                        if st.button("OK", key=f"delete_ok_{p.id}"):
                            st.session_state[delete_key] = False
                            st.rerun()
                    else:
                        st.warning(f"Are you sure you want to delete **{p.name}**? This cannot be undone.")
                        del_col1, del_col2, del_col3 = st.columns([2, 1, 1])
                        with del_col2:
                            if st.button("Yes, Delete", key=f"delete_confirm_{p.id}", type="primary", width="stretch"):
                                success, msg = delete_profile(p.id)
                                if success:
                                    st.session_state[delete_key] = False
                                    st.success("Profile deleted!")
                                    st.rerun()
                                else:
                                    st.error(msg)
                        with del_col3:
                            if st.button("Cancel", key=f"delete_cancel_{p.id}", width="stretch"):
                                st.session_state[delete_key] = False
                                st.rerun()

                # Preview panel
                if st.session_state.get(preview_key, False):
                    with st.expander("Profile Details", expanded=True):
                        prev_col1, prev_col2 = st.columns(2)

                        with prev_col1:
                            st.markdown("**Profile Settings:**")
                            farm_status = "Yes" if p.is_farm_account else "No"
                            st.markdown(f"""
                            - Name: {p.name}
                            - State: {p.state_number or 'N/A'}
                            - Server Age: Day {p.server_age_days}
                            - Furnace: {fc_text}
                            - Farm Account: {farm_status}
                            - Spending: {p.spending_profile}
                            - Alliance Role: {p.alliance_role}
                            """)

                        with prev_col2:
                            st.markdown("**Heroes:**")
                            heroes = db.query(UserHero).filter(UserHero.profile_id == p.id).all()
                            if heroes:
                                for uh in heroes[:5]:
                                    hero_ref = db.query(Hero).filter(Hero.id == uh.hero_id).first()
                                    if hero_ref:
                                        st.markdown(f"- {hero_ref.name} (Lv.{uh.level}, ★{uh.stars})")
                                if len(heroes) > 5:
                                    st.markdown(f"*...and {len(heroes) - 5} more*")
                            else:
                                st.markdown("*No heroes saved*")

                st.markdown("---")

    # Create New Profile section
    st.markdown("### ➕ Create New Profile")
    with st.form(key="create_profile_form"):
        create_col1, create_col2, create_col3 = st.columns([2, 1, 1])
        with create_col1:
            new_profile_name = st.text_input(
                "Profile Name",
                placeholder="e.g., MyFarm_city2",
                key="create_new_profile_name"
            )
        with create_col2:
            new_profile_state = st.number_input(
                "State #",
                min_value=1,
                max_value=9999,
                value=profile.state_number if profile.state_number else 1,
                key="create_new_profile_state",
                help="Your state/server number"
            )
        with create_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            create_clicked = st.form_submit_button("Create", width="stretch")

    if create_clicked:
        if new_profile_name and new_profile_name.strip():
            # Create a new blank profile
            new_profile = UserProfile(
                user_id=user_id,
                name=new_profile_name.strip(),
                state_number=new_profile_state,
                furnace_level=1,
                server_age_days=0,
                spending_profile="f2p",
                alliance_role="filler"
            )
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            # Switch to the new profile
            st.session_state.profile_id = new_profile.id
            st.toast(f"Created {new_profile_name}")
            st.rerun()
        else:
            st.error("Please enter a profile name")

    st.markdown("---")

    # Farm account linking (for current profile)
    if profile.is_farm_account:
        st.markdown("### 🔗 Link Farm to Main Account")
        st.caption("Link this farm to your main account for coordinated recommendations")

        # Get main profiles to link
        main_profiles = [p for p in all_user_profiles if p.id != profile.id and not p.is_farm_account]

        if main_profiles:
            profile_options = {0: "-- Not linked --"}
            profile_options.update({p.id: f"{p.name} (State {p.state_number or '?'})" for p in main_profiles})

            current_linked = profile.linked_main_profile_id if hasattr(profile, 'linked_main_profile_id') else None
            default_idx = 0
            if current_linked and current_linked in profile_options:
                default_idx = list(profile_options.keys()).index(current_linked)

            linked_id = st.selectbox(
                "Link to main account",
                options=list(profile_options.keys()),
                format_func=lambda x: profile_options[x],
                index=default_idx,
                key="linked_main_select",
            )

            if linked_id != (current_linked or 0):
                profile.linked_main_profile_id = linked_id if linked_id != 0 else None
                db.commit()
                st.success("Link updated!")
                st.rerun()
        else:
            st.caption("No main accounts available to link to. Create a non-farm profile first.")

    # Recently Deleted Profiles section
    deleted_profiles = get_deleted_profiles(user_id)
    if deleted_profiles:
        st.markdown("### 🗑️ Recently Deleted")
        st.caption("Deleted profiles can be restored within 30 days.")

        from datetime import datetime, timedelta

        for dp in deleted_profiles:
            # Calculate days remaining
            delete_date = dp.deleted_at
            expiry_date = delete_date + timedelta(days=30)
            days_left = (expiry_date - datetime.utcnow()).days

            if days_left < 0:
                days_left = 0

            with st.container():
                del_col1, del_col2, del_col3 = st.columns([3, 1, 1])

                with del_col1:
                    st.markdown(f"~~{dp.name}~~")
                    if days_left > 0:
                        st.caption(f"⏱️ {days_left} days left to restore")
                    else:
                        st.caption("⚠️ Will be permanently deleted soon")

                with del_col2:
                    if st.button("Restore", key=f"restore_{dp.id}", width="stretch"):
                        success, msg = restore_profile(dp.id)
                        if success:
                            st.success("Profile restored!")
                            st.rerun()
                        else:
                            st.error(msg)

                with del_col3:
                    if st.button("🗑️ Delete Now", key=f"perm_delete_{dp.id}", width="stretch"):
                        st.session_state[f"confirm_perm_delete_{dp.id}"] = True

                # Permanent delete confirmation
                if st.session_state.get(f"confirm_perm_delete_{dp.id}", False):
                    st.warning(f"Permanently delete **{dp.name}**? This cannot be undone.")
                    conf_col1, conf_col2, conf_col3 = st.columns([2, 1, 1])
                    with conf_col2:
                        if st.button("Yes, Delete Forever", key=f"perm_confirm_{dp.id}", width="stretch"):
                            success, msg = delete_profile(dp.id, hard_delete=True)
                            if success:
                                st.session_state[f"confirm_perm_delete_{dp.id}"] = False
                                st.rerun()
                            else:
                                st.error(msg)
                    with conf_col3:
                        if st.button("Cancel", key=f"perm_cancel_{dp.id}", width="stretch"):
                            st.session_state[f"confirm_perm_delete_{dp.id}"] = False
                            st.rerun()

        st.markdown("---")

    # Farm profile disclaimer
    st.caption("🌾 **Farm Profiles:** Mark your farm account to receive specialized recommendations focused on resource gathering and support heroes rather than combat upgrades.")

else:
    st.warning("Please log in to manage your profiles.")

# Close database
db.close()
