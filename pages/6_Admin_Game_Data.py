"""
Admin Game Data Editor - Edit heroes, items, and game reference data.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import require_admin
from database.models import Hero, Item

init_db()

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

require_admin()

st.markdown("# 🎮 Game Data Editor")
st.caption("Edit heroes, items, and game reference data")

db = get_db()

# Stats
hero_count = db.query(Hero).count()
item_count = db.query(Item).count()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Heroes", hero_count)
with col2:
    st.metric("Items", item_count)
with col3:
    # Count JSON files
    data_path = PROJECT_ROOT / "data"
    json_count = len(list(data_path.glob("**/*.json"))) if data_path.exists() else 0
    st.metric("Data Files", json_count)

st.markdown("---")

# Tabs
tab_heroes, tab_items, tab_json = st.tabs(["🦸 Heroes", "🎒 Items", "📁 JSON Files"])

with tab_heroes:
    # Search
    search = st.text_input("🔍 Search Heroes", placeholder="Name, class, or rarity...")

    heroes = db.query(Hero).order_by(Hero.generation, Hero.name).all()

    if search:
        search_lower = search.lower()
        heroes = [h for h in heroes if
                 search_lower in h.name.lower() or
                 search_lower in (h.hero_class or "").lower() or
                 search_lower in (h.rarity or "").lower()]

    st.caption(f"Showing {len(heroes)} heroes")

    # Add new hero button
    if st.button("➕ Add New Hero"):
        st.session_state["adding_hero"] = True

    if st.session_state.get("adding_hero"):
        with st.expander("New Hero", expanded=True):
            with st.form("new_hero"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Name *")
                    hero_class = st.selectbox("Class", ["Infantry", "Marksman", "Lancer"])
                    rarity = st.selectbox("Rarity", ["Epic", "Legendary"])
                with col2:
                    generation = st.number_input("Generation", min_value=1, max_value=20, value=1)
                    tier_overall = st.selectbox("Overall Tier", ["S+", "S", "A", "B", "C", "D"])

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Create Hero"):
                        if not name:
                            st.error("Name is required")
                        elif db.query(Hero).filter(Hero.name == name).first():
                            st.error("Hero with this name already exists")
                        else:
                            new_hero = Hero(
                                name=name,
                                hero_class=hero_class,
                                rarity=rarity,
                                generation=generation,
                                tier_overall=tier_overall
                            )
                            db.add(new_hero)
                            db.commit()
                            st.session_state["adding_hero"] = False
                            st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state["adding_hero"] = False
                        st.rerun()

    st.markdown("---")

    # Hero list
    for hero in heroes:
        cols = st.columns([0.5, 2, 1.5, 1, 1, 1.5])

        with cols[0]:
            class_icons = {"Infantry": "🛡️", "Marksman": "🏹", "Lancer": "🗡️"}
            st.markdown(class_icons.get(hero.hero_class, "❓"))

        with cols[1]:
            rarity_color = "#9B59B6" if hero.rarity == "Legendary" else "#3498DB"
            st.markdown(f"**{hero.name}**")

        with cols[2]:
            st.caption(f"Gen {hero.generation} • {hero.hero_class}")

        with cols[3]:
            tier_colors = {"S+": "#FFD700", "S": "#C0C0C0", "A": "#CD7F32", "B": "#2ECC71", "C": "#F1C40F", "D": "#E74C3C"}
            tier = hero.tier_overall or "?"
            color = tier_colors.get(tier, "#888")
            st.markdown(f"<span style='color: {color}; font-weight: bold;'>{tier}</span>", unsafe_allow_html=True)

        with cols[4]:
            if st.button("✏️", key=f"edit_hero_{hero.id}", help="Edit"):
                st.session_state[f"editing_hero_{hero.id}"] = True

        with cols[5]:
            if st.button("🗑️", key=f"del_hero_{hero.id}", help="Delete"):
                st.session_state[f"confirm_del_hero_{hero.id}"] = True

        # Edit form
        if st.session_state.get(f"editing_hero_{hero.id}"):
            with st.expander(f"Edit {hero.name}", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    new_name = st.text_input("Name", value=hero.name, key=f"name_{hero.id}")
                    new_class = st.selectbox("Class", ["Infantry", "Marksman", "Lancer"],
                                            index=["Infantry", "Marksman", "Lancer"].index(hero.hero_class) if hero.hero_class else 0,
                                            key=f"class_{hero.id}")

                with col2:
                    new_rarity = st.selectbox("Rarity", ["Epic", "Legendary"],
                                             index=["Epic", "Legendary"].index(hero.rarity) if hero.rarity else 0,
                                             key=f"rarity_{hero.id}")
                    new_gen = st.number_input("Generation", min_value=1, max_value=20, value=hero.generation,
                                             key=f"gen_{hero.id}")

                with col3:
                    tiers = ["S+", "S", "A", "B", "C", "D"]
                    current_tier_idx = tiers.index(hero.tier_overall) if hero.tier_overall in tiers else 2
                    new_tier = st.selectbox("Overall Tier", tiers, index=current_tier_idx, key=f"tier_{hero.id}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save", key=f"save_hero_{hero.id}"):
                        hero.name = new_name
                        hero.hero_class = new_class
                        hero.rarity = new_rarity
                        hero.generation = new_gen
                        hero.tier_overall = new_tier
                        db.commit()
                        st.session_state[f"editing_hero_{hero.id}"] = False
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_hero_{hero.id}"):
                        st.session_state[f"editing_hero_{hero.id}"] = False
                        st.rerun()

        # Delete confirmation
        if st.session_state.get(f"confirm_del_hero_{hero.id}"):
            st.warning(f"Delete {hero.name}? This will also delete user hero data!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Yes", key=f"confirm_delete_hero_{hero.id}"):
                    db.delete(hero)
                    db.commit()
                    st.session_state[f"confirm_del_hero_{hero.id}"] = False
                    st.rerun()
            with col2:
                if st.button("Cancel", key=f"cancel_del_hero_{hero.id}"):
                    st.session_state[f"confirm_del_hero_{hero.id}"] = False
                    st.rerun()

with tab_items:
    st.info("Items are used for backpack/inventory tracking (OCR feature). Add items here to enable inventory scanning.")

    # Search
    search = st.text_input("🔍 Search Items", placeholder="Name or category...", key="item_search")

    items = db.query(Item).order_by(Item.category, Item.name).all()

    if search:
        search_lower = search.lower()
        items = [i for i in items if
                search_lower in i.name.lower() or
                search_lower in (i.category or "").lower()]

    st.caption(f"Showing {len(items)} items")

    # Add new item
    if st.button("➕ Add New Item"):
        st.session_state["adding_item"] = True

    if st.session_state.get("adding_item"):
        with st.expander("New Item", expanded=True):
            with st.form("new_item"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Name *")
                    category = st.text_input("Category", placeholder="e.g., Shard, XP, Material")
                with col2:
                    subcategory = st.text_input("Subcategory", placeholder="Optional")
                    rarity = st.selectbox("Rarity", ["Common", "Rare", "Epic", "Legendary"])

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Create Item"):
                        if not name:
                            st.error("Name is required")
                        else:
                            new_item = Item(
                                name=name,
                                category=category,
                                subcategory=subcategory,
                                rarity=rarity
                            )
                            db.add(new_item)
                            db.commit()
                            st.session_state["adding_item"] = False
                            st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state["adding_item"] = False
                        st.rerun()

    st.markdown("---")

    # Group by category
    categories = {}
    for item in items:
        cat = item.category or "Uncategorized"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    for category, cat_items in categories.items():
        with st.expander(f"📦 {category} ({len(cat_items)} items)"):
            for item in cat_items:
                cols = st.columns([3, 1.5, 1, 1])

                with cols[0]:
                    st.markdown(f"**{item.name}**")

                with cols[1]:
                    rarity_colors = {"Common": "#888", "Rare": "#3498DB", "Epic": "#9B59B6", "Legendary": "#F1C40F"}
                    color = rarity_colors.get(item.rarity, "#888")
                    st.markdown(f"<span style='color: {color};'>{item.rarity or 'Unknown'}</span>", unsafe_allow_html=True)

                with cols[2]:
                    if st.button("✏️", key=f"edit_item_{item.id}"):
                        st.session_state[f"editing_item_{item.id}"] = True

                with cols[3]:
                    if st.button("🗑️", key=f"del_item_{item.id}"):
                        db.delete(item)
                        db.commit()
                        st.rerun()

                if st.session_state.get(f"editing_item_{item.id}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_name = st.text_input("Name", value=item.name, key=f"iname_{item.id}")
                    with col2:
                        new_cat = st.text_input("Category", value=item.category or "", key=f"icat_{item.id}")
                    with col3:
                        new_rarity = st.selectbox("Rarity", ["Common", "Rare", "Epic", "Legendary"],
                                                 index=["Common", "Rare", "Epic", "Legendary"].index(item.rarity) if item.rarity else 0,
                                                 key=f"irar_{item.id}")

                    if st.button("💾 Save", key=f"save_item_{item.id}"):
                        item.name = new_name
                        item.category = new_cat
                        item.rarity = new_rarity
                        db.commit()
                        st.session_state[f"editing_item_{item.id}"] = False
                        st.rerun()

with tab_json:
    st.markdown("### JSON Data Files")
    st.caption("View and edit raw game data files")

    data_path = PROJECT_ROOT / "data"

    if data_path.exists():
        # List all JSON files
        json_files = list(data_path.glob("**/*.json"))
        json_files.sort(key=lambda x: str(x))

        if json_files:
            # Group by directory
            file_groups = {}
            for f in json_files:
                rel_path = f.relative_to(data_path)
                if len(rel_path.parts) > 1:
                    group = rel_path.parts[0]
                else:
                    group = "Root"
                if group not in file_groups:
                    file_groups[group] = []
                file_groups[group].append(f)

            selected_file = st.selectbox(
                "Select File",
                json_files,
                format_func=lambda x: str(x.relative_to(data_path))
            )

            if selected_file:
                st.markdown(f"**File:** `{selected_file.relative_to(data_path)}`")
                st.caption(f"Size: {selected_file.stat().st_size / 1024:.1f} KB")

                try:
                    with open(selected_file, "r", encoding="utf-8") as f:
                        content = json.load(f)

                    # Display as expandable JSON
                    if isinstance(content, list):
                        st.caption(f"{len(content)} items")
                        st.json(content[:20] if len(content) > 20 else content)
                        if len(content) > 20:
                            st.info(f"Showing first 20 of {len(content)} items")
                    else:
                        st.json(content)

                    # Edit mode
                    if st.checkbox("Enable Editing", key=f"edit_json_{selected_file.name}"):
                        st.warning("Be careful when editing JSON files!")
                        edited_content = st.text_area(
                            "JSON Content",
                            value=json.dumps(content, indent=2),
                            height=400,
                            key=f"json_content_{selected_file.name}"
                        )

                        if st.button("💾 Save Changes"):
                            try:
                                parsed = json.loads(edited_content)
                                with open(selected_file, "w", encoding="utf-8") as f:
                                    json.dump(parsed, f, indent=2)
                                st.success("File saved!")
                            except json.JSONDecodeError as e:
                                st.error(f"Invalid JSON: {e}")

                except json.JSONDecodeError as e:
                    st.error(f"Error parsing JSON: {e}")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        else:
            st.info("No JSON files found in data directory")
    else:
        st.warning("Data directory not found")

db.close()
