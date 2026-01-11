"""
Profiles Page - Save and load profiles for use across computers.
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero, Hero, UserInventory


# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Profiles directory
PROFILES_DIR = PROJECT_ROOT / "data" / "profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)


def get_saved_profiles():
    """Get list of saved profile files."""
    profiles = []
    for f in PROFILES_DIR.glob("*.json"):
        try:
            with open(f, encoding='utf-8') as file:
                data = json.load(file)
                profiles.append({
                    "filename": f.name,
                    "path": f,
                    "name": data.get("profile", {}).get("name", "Unknown"),
                    "hero_count": len(data.get("heroes", [])),
                    "export_date": data.get("export_date", "Unknown"),
                    "server_age": data.get("profile", {}).get("server_age_days", 0),
                })
        except:
            pass
    return sorted(profiles, key=lambda x: x.get("export_date", ""), reverse=True)


def export_current_profile():
    """Export current profile to JSON dict."""
    user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()

    heroes_data = []
    for uh in user_heroes:
        hero_ref = db.query(Hero).filter(Hero.id == uh.hero_id).first()
        if hero_ref:
            heroes_data.append({
                "hero_name": hero_ref.name,
                "level": uh.level,
                "stars": uh.stars,
                "ascension_tier": uh.ascension_tier,
                "exploration_skill_1_level": uh.exploration_skill_1_level,
                "exploration_skill_2_level": uh.exploration_skill_2_level,
                "expedition_skill_1_level": uh.expedition_skill_1_level,
                "expedition_skill_2_level": uh.expedition_skill_2_level,
                "gear_slot1_quality": uh.gear_slot1_quality,
                "gear_slot1_level": uh.gear_slot1_level,
                "gear_slot2_quality": uh.gear_slot2_quality,
                "gear_slot2_level": uh.gear_slot2_level,
                "gear_slot3_quality": uh.gear_slot3_quality,
                "gear_slot3_level": uh.gear_slot3_level,
                "gear_slot4_quality": uh.gear_slot4_quality,
                "gear_slot4_level": uh.gear_slot4_level,
                "mythic_gear_unlocked": uh.mythic_gear_unlocked,
                "mythic_gear_quality": uh.mythic_gear_quality,
                "mythic_gear_level": uh.mythic_gear_level,
            })

    return {
        "export_version": "1.0",
        "export_date": datetime.now().isoformat(),
        "profile": {
            "name": profile.name,
            "server_age_days": profile.server_age_days,
            "furnace_level": profile.furnace_level,
            "priority_svs": profile.priority_svs,
            "priority_rally": profile.priority_rally,
            "priority_castle_battle": profile.priority_castle_battle,
            "priority_exploration": profile.priority_exploration,
            "priority_gathering": profile.priority_gathering,
            "svs_wins": profile.svs_wins,
            "svs_losses": profile.svs_losses,
            "last_svs_date": profile.last_svs_date.isoformat() if profile.last_svs_date else None,
        },
        "heroes": heroes_data
    }


def save_profile_to_file(profile_name: str):
    """Save current profile to a file."""
    data = export_current_profile()

    # Create safe filename
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in profile_name)
    filename = f"{safe_name}.json"
    filepath = PROFILES_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    return filepath


def load_profile_from_file(filepath: Path):
    """Load profile from a file."""
    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        # Track loaded profile file
        st.session_state["loaded_profile_path"] = str(filepath)
        st.session_state["loaded_profile_filename"] = filepath.name

        # Import profile settings
        if "profile" in data:
            p = data["profile"]
            profile.name = p.get("name", profile.name)
            profile.server_age_days = p.get("server_age_days", profile.server_age_days)
            profile.furnace_level = p.get("furnace_level", profile.furnace_level)
            profile.priority_svs = p.get("priority_svs", profile.priority_svs)
            profile.priority_rally = p.get("priority_rally", profile.priority_rally)
            profile.priority_castle_battle = p.get("priority_castle_battle", profile.priority_castle_battle)
            profile.priority_exploration = p.get("priority_exploration", profile.priority_exploration)
            profile.priority_gathering = p.get("priority_gathering", profile.priority_gathering)
            profile.svs_wins = p.get("svs_wins", profile.svs_wins)
            profile.svs_losses = p.get("svs_losses", profile.svs_losses)
            if p.get("last_svs_date"):
                profile.last_svs_date = datetime.fromisoformat(p["last_svs_date"])

        # Clear existing heroes first
        db.query(UserHero).filter(UserHero.profile_id == profile.id).delete()
        db.commit()

        # Import heroes
        if "heroes" in data:
            heroes_file = PROJECT_ROOT / "data" / "heroes.json"
            with open(heroes_file, encoding='utf-8') as f:
                hero_data = json.load(f)

            heroes_by_name = {h["name"]: h for h in hero_data.get("heroes", [])}

            imported_count = 0
            for hero_import in data["heroes"]:
                hero_name = hero_import.get("hero_name")
                if not hero_name or hero_name not in heroes_by_name:
                    continue

                # Get or create hero reference
                hero_ref = db.query(Hero).filter(Hero.name == hero_name).first()
                if not hero_ref:
                    h = heroes_by_name[hero_name]
                    hero_ref = Hero(
                        name=h["name"],
                        generation=h["generation"],
                        hero_class=h["hero_class"],
                        rarity=h["rarity"],
                        tier_overall=h["tier_overall"],
                        tier_expedition=h["tier_expedition"],
                        tier_exploration=h["tier_exploration"],
                        image_filename=h.get("image_filename", "")
                    )
                    db.add(hero_ref)
                    db.commit()
                    db.refresh(hero_ref)

                # Create user hero
                user_hero = UserHero(
                    profile_id=profile.id,
                    hero_id=hero_ref.id,
                    level=hero_import.get("level", 1),
                    stars=hero_import.get("stars", 0),
                    ascension_tier=hero_import.get("ascension_tier", 0),
                    exploration_skill_1_level=hero_import.get("exploration_skill_1_level", 1),
                    exploration_skill_2_level=hero_import.get("exploration_skill_2_level", 1),
                    expedition_skill_1_level=hero_import.get("expedition_skill_1_level", 1),
                    expedition_skill_2_level=hero_import.get("expedition_skill_2_level", 1),
                    gear_slot1_quality=hero_import.get("gear_slot1_quality", 0),
                    gear_slot1_level=hero_import.get("gear_slot1_level", 0),
                    gear_slot2_quality=hero_import.get("gear_slot2_quality", 0),
                    gear_slot2_level=hero_import.get("gear_slot2_level", 0),
                    gear_slot3_quality=hero_import.get("gear_slot3_quality", 0),
                    gear_slot3_level=hero_import.get("gear_slot3_level", 0),
                    gear_slot4_quality=hero_import.get("gear_slot4_quality", 0),
                    gear_slot4_level=hero_import.get("gear_slot4_level", 0),
                    mythic_gear_unlocked=hero_import.get("mythic_gear_unlocked", False),
                    mythic_gear_quality=hero_import.get("mythic_gear_quality", 0),
                    mythic_gear_level=hero_import.get("mythic_gear_level", 0),
                )
                db.add(user_hero)
                imported_count += 1

            db.commit()
            return True, f"Loaded profile with {imported_count} heroes!"

        db.commit()
        return True, "Profile settings loaded!"

    except Exception as e:
        return False, f"Error loading profile: {str(e)}"


def delete_profile_file(filepath: Path):
    """Delete a profile file."""
    try:
        filepath.unlink()
        return True
    except:
        return False


def update_loaded_profile():
    """Update the currently loaded profile file with current data."""
    if "loaded_profile_path" not in st.session_state:
        return False, "No profile loaded to update"

    filepath = Path(st.session_state["loaded_profile_path"])
    if not filepath.exists():
        return False, "Profile file no longer exists"

    data = export_current_profile()

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    return True, f"Updated profile: {filepath.name}"


def rename_profile_file(new_name: str):
    """Rename the currently loaded profile file."""
    if "loaded_profile_path" not in st.session_state:
        return False, "No profile loaded to rename"

    old_path = Path(st.session_state["loaded_profile_path"])
    if not old_path.exists():
        return False, "Profile file no longer exists"

    # Create safe filename
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in new_name)
    new_filename = f"{safe_name}.json"
    new_path = PROFILES_DIR / new_filename

    # Rename file
    old_path.rename(new_path)

    # Update session state
    st.session_state["loaded_profile_path"] = str(new_path)
    st.session_state["loaded_profile_filename"] = new_filename

    return True, f"Renamed to: {new_filename}"


# Page content
st.markdown("# 👤 Profiles")
st.markdown("Save and load profiles to sync your data across computers via git.")

st.markdown("---")

# Current profile summary
st.markdown("## 📊 Current Profile")

# Show loaded profile status
loaded_file = st.session_state.get("loaded_profile_filename")
if loaded_file:
    st.success(f"📂 **Loaded from:** `{loaded_file}`")
else:
    st.info("💡 No profile file loaded. Load a saved profile or save a new one below.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Chief Name", profile.name or "Chief")
with col2:
    st.metric("Server Age", f"Day {profile.server_age_days}")
with col3:
    hero_count = db.query(UserHero).filter(UserHero.profile_id == profile.id).count()
    st.metric("Heroes Saved", hero_count)
with col4:
    st.metric("Furnace Level", profile.furnace_level)

# Edit profile name and update loaded profile
if loaded_file:
    st.markdown("### ✏️ Edit Loaded Profile")

    edit_col1, edit_col2, edit_col3 = st.columns([3, 1, 1])

    with edit_col1:
        new_name = st.text_input(
            "Chief Name",
            value=profile.name or "Chief",
            key="edit_profile_name",
            help="Update your chief name"
        )

    with edit_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Rename File", use_container_width=True):
            if new_name and new_name != profile.name:
                profile.name = new_name
                db.commit()
            success, message = rename_profile_file(new_name)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with edit_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Update Profile", type="primary", use_container_width=True):
            # Save name change first
            if new_name and new_name != profile.name:
                profile.name = new_name
                db.commit()
            success, message = update_loaded_profile()
            if success:
                st.success(message)
            else:
                st.error(message)

st.markdown("---")

# Save as new profile
st.markdown("## 💾 Save As New Profile")

save_col1, save_col2 = st.columns([3, 1])

with save_col1:
    save_name = st.text_input(
        "New Profile Name",
        value=profile.name or "My Profile",
        key="save_new_profile_name",
        help="Name for the new saved profile"
    )

with save_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Save As New", type="primary", use_container_width=True):
        if save_name:
            # Update profile name if different
            if save_name != profile.name:
                profile.name = save_name
                db.commit()
            filepath = save_profile_to_file(save_name)
            # Track the newly saved file as loaded
            st.session_state["loaded_profile_path"] = str(filepath)
            st.session_state["loaded_profile_filename"] = filepath.name
            st.success(f"Profile saved to: `data/profiles/{filepath.name}`")
            st.info("Commit and push to git to sync across computers!")
            st.rerun()
        else:
            st.error("Please enter a profile name")

st.markdown("---")

# Saved profiles
st.markdown("## 📁 Saved Profiles")

saved_profiles = get_saved_profiles()

if not saved_profiles:
    st.info("No saved profiles yet. Save your current profile above!")
else:
    st.markdown(f"*Found {len(saved_profiles)} saved profile(s)*")

    for prof in saved_profiles:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                # Parse date for display
                try:
                    export_dt = datetime.fromisoformat(prof["export_date"])
                    date_str = export_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    date_str = "Unknown date"

                st.markdown(f"""
                **{prof['name']}**
                📅 {date_str} | 🦸 {prof['hero_count']} heroes | 📍 Day {prof['server_age']}
                """)

            with col2:
                if st.button("📂 Load", key=f"load_{prof['filename']}", use_container_width=True):
                    success, message = load_profile_from_file(prof["path"])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

            with col3:
                # Preview button
                if st.button("👁️ Preview", key=f"preview_{prof['filename']}", use_container_width=True):
                    st.session_state[f"show_preview_{prof['filename']}"] = not st.session_state.get(f"show_preview_{prof['filename']}", False)

            with col4:
                if st.button("🗑️ Delete", key=f"delete_{prof['filename']}", use_container_width=True):
                    if delete_profile_file(prof["path"]):
                        st.success("Profile deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete")

            # Show preview if expanded
            if st.session_state.get(f"show_preview_{prof['filename']}", False):
                with open(prof["path"], encoding='utf-8') as f:
                    data = json.load(f)

                preview_col1, preview_col2 = st.columns(2)

                with preview_col1:
                    st.markdown("**Profile Settings:**")
                    p = data.get("profile", {})
                    st.markdown(f"""
                    - Name: {p.get('name', 'N/A')}
                    - Server Age: Day {p.get('server_age_days', 0)}
                    - Furnace: Lv.{p.get('furnace_level', 1)}
                    - SvS Priority: {p.get('priority_svs', 5)}/5
                    """)

                with preview_col2:
                    st.markdown("**Heroes:**")
                    heroes = data.get("heroes", [])
                    if heroes:
                        for h in heroes[:5]:  # Show first 5
                            st.markdown(f"- {h['hero_name']} (Lv.{h['level']}, ★{h['stars']})")
                        if len(heroes) > 5:
                            st.markdown(f"*...and {len(heroes) - 5} more*")
                    else:
                        st.markdown("*No heroes saved*")

            st.markdown("---")

st.markdown("---")

# Git instructions
with st.expander("📖 How to sync profiles across computers"):
    st.markdown("""
    ### Syncing Profiles via Git

    **On this computer (after saving a profile):**
    ```bash
    cd WoS
    git add data/profiles/
    git commit -m "Save profile: YourProfileName"
    git push
    ```

    **On another computer:**
    ```bash
    cd WoS
    git pull
    ```
    Then open the Profiles page and click "Load" on your saved profile.

    ### Tips:
    - Save your profile before switching computers
    - Always `git pull` before loading on a new machine
    - Profile files are small JSON files in `data/profiles/`
    """)

# Close database
db.close()
