"""
Backpack Page - Track your inventory via screenshots or manual entry.
"""

import streamlit as st
from pathlib import Path
import sys
from PIL import Image
import io

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import Item, UserInventory

st.set_page_config(page_title="Backpack - WoS Optimizer", page_icon="🎒", layout="wide")

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Try to import OCR
try:
    from ocr.screenshot_parser import ScreenshotParser
    ocr_parser = ScreenshotParser()
    OCR_AVAILABLE = ocr_parser.is_available()
except ImportError:
    OCR_AVAILABLE = False
    ocr_parser = None

# Common items in WoS
ITEM_CATEGORIES = {
    "Hero Shards": [
        "Jeronimo Shard", "Natalia Shard", "Molly Shard", "Flint Shard",
        "Philly Shard", "Alonso Shard", "Logan Shard", "Mia Shard",
        "Epic General Shard", "Legendary General Shard"
    ],
    "Hero EXP": [
        "Basic Combat Manual", "Combat Manual", "Advanced Combat Manual",
        "Elite Combat Manual", "Hero EXP Pack (Small)", "Hero EXP Pack (Medium)",
        "Hero EXP Pack (Large)"
    ],
    "Skill Books": [
        "Exploration Skill Book I", "Exploration Skill Book II",
        "Exploration Skill Book III", "Expedition Skill Book I",
        "Expedition Skill Book II", "Expedition Skill Book III"
    ],
    "Gear Materials": [
        "Iron Ore", "Refined Iron", "Steel Ingot", "Frost Steel",
        "Gear Material Box", "Hero Gear Blueprint"
    ],
    "Speedups": [
        "1 Minute Speedup", "5 Minute Speedup", "15 Minute Speedup",
        "1 Hour Speedup", "3 Hour Speedup", "8 Hour Speedup",
        "Research Speedup", "Training Speedup", "Building Speedup"
    ],
    "Resources": [
        "Food Pack", "Wood Pack", "Coal Pack", "Iron Pack",
        "Food", "Wood", "Coal", "Iron"
    ]
}


def get_or_create_item(name: str, category: str) -> Item:
    """Get or create an item in the database."""
    item = db.query(Item).filter(Item.name == name).first()
    if not item:
        item = Item(name=name, category=category)
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


def save_inventory_item(item_name: str, category: str, quantity: int):
    """Save an inventory item."""
    item = get_or_create_item(item_name, category)

    inv = db.query(UserInventory).filter(
        UserInventory.profile_id == profile.id,
        UserInventory.item_id == item.id
    ).first()

    if inv:
        inv.quantity = quantity
    else:
        inv = UserInventory(
            profile_id=profile.id,
            item_id=item.id,
            quantity=quantity
        )
        db.add(inv)

    db.commit()


def get_inventory() -> dict:
    """Get all inventory items grouped by category."""
    inventory = db.query(UserInventory).filter(
        UserInventory.profile_id == profile.id
    ).all()

    grouped = {}
    for inv in inventory:
        cat = inv.item.category
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append({
            'name': inv.item.name,
            'quantity': inv.quantity,
            'id': inv.id
        })

    return grouped


# Page content
st.markdown("# 🎒 Backpack Manager")
st.markdown("Track your resources and items for better upgrade recommendations.")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📸 Screenshot Upload", "✏️ Manual Entry", "📋 My Inventory"])

with tab1:
    st.markdown("### Upload Backpack Screenshot")

    if not OCR_AVAILABLE:
        st.warning("""
        ⚠️ **OCR not available**

        To enable screenshot parsing, install EasyOCR:
        ```
        pip install easyocr
        ```

        This requires additional dependencies and may take a while to download.
        You can still use Manual Entry in the meantime.
        """)
    else:
        st.info("📸 Upload a screenshot of your backpack to automatically detect items.")

        uploaded_file = st.file_uploader(
            "Choose a screenshot",
            type=['png', 'jpg', 'jpeg'],
            help="Take a screenshot of your backpack in-game"
        )

        if uploaded_file is not None:
            # Display the image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Screenshot", use_container_width=True)

            if st.button("🔍 Analyze Screenshot", type="primary"):
                with st.spinner("Analyzing screenshot with OCR..."):
                    # Parse the screenshot
                    results = ocr_parser.parse_from_pil_image(image)

                    if results and 'error' not in results[0]:
                        st.success(f"Found {len(results)} items!")

                        # Display results for confirmation
                        st.markdown("### Detected Items")
                        st.markdown("Review and confirm the detected items:")

                        # Store in session state for confirmation
                        if 'ocr_results' not in st.session_state:
                            st.session_state.ocr_results = []

                        st.session_state.ocr_results = results

                        for i, item in enumerate(results):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.text(f"{item['type']}")
                            with col2:
                                qty = st.number_input(
                                    "Qty",
                                    value=item.get('quantity', 1) or 1,
                                    key=f"qty_{i}",
                                    min_value=0
                                )
                                st.session_state.ocr_results[i]['quantity'] = qty
                            with col3:
                                conf = item.get('confidence', 0) * 100
                                st.caption(f"Conf: {conf:.0f}%")

                        if st.button("✅ Save All to Inventory"):
                            for item in st.session_state.ocr_results:
                                if item.get('quantity', 0) > 0:
                                    save_inventory_item(
                                        item['type'],
                                        "OCR Detected",
                                        item['quantity']
                                    )
                            st.success("Items saved to inventory!")
                            st.session_state.ocr_results = []
                            st.rerun()

                    else:
                        error_msg = results[0].get('error', 'Unknown error') if results else 'No results'
                        st.error(f"Could not analyze screenshot: {error_msg}")

with tab2:
    st.markdown("### Manual Item Entry")
    st.info("Add items to your inventory manually.")

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox("Category", list(ITEM_CATEGORIES.keys()))

    with col2:
        items_in_category = ITEM_CATEGORIES.get(category, [])
        item_name = st.selectbox("Item", items_in_category + ["Other (Custom)"])

    if item_name == "Other (Custom)":
        item_name = st.text_input("Custom Item Name")

    quantity = st.number_input("Quantity", min_value=0, value=1)

    if st.button("➕ Add to Inventory", type="primary"):
        if item_name and quantity > 0:
            save_inventory_item(item_name, category, quantity)
            st.success(f"Added {quantity}x {item_name} to inventory!")
            st.rerun()
        else:
            st.warning("Please enter an item name and quantity.")

    # Quick add section
    st.markdown("---")
    st.markdown("### Quick Add Common Items")

    quick_items = [
        ("Epic General Shard", "Hero Shards"),
        ("Legendary General Shard", "Hero Shards"),
        ("Combat Manual", "Hero EXP"),
        ("1 Hour Speedup", "Speedups"),
    ]

    cols = st.columns(len(quick_items))
    for i, (item, cat) in enumerate(quick_items):
        with cols[i]:
            qty = st.number_input(item, min_value=0, value=0, key=f"quick_{i}")
            if st.button(f"Add", key=f"quick_btn_{i}"):
                if qty > 0:
                    save_inventory_item(item, cat, qty)
                    st.success(f"Added {qty}x!")
                    st.rerun()

with tab3:
    st.markdown("### My Inventory")

    inventory = get_inventory()

    if not inventory:
        st.info("Your inventory is empty. Add items using Screenshot Upload or Manual Entry.")
    else:
        # Summary
        total_items = sum(len(items) for items in inventory.values())
        total_quantity = sum(item['quantity'] for items in inventory.values() for item in items)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Unique Items", total_items)
        with col2:
            st.metric("Total Quantity", f"{total_quantity:,}")

        st.markdown("---")

        # Display by category
        for category, items in inventory.items():
            with st.expander(f"📦 {category} ({len(items)} items)", expanded=True):
                for item in items:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(item['name'])
                    with col2:
                        new_qty = st.number_input(
                            "Qty",
                            value=item['quantity'],
                            key=f"inv_{item['id']}",
                            min_value=0,
                            label_visibility="collapsed"
                        )
                        if new_qty != item['quantity']:
                            inv_item = db.query(UserInventory).get(item['id'])
                            if inv_item:
                                inv_item.quantity = new_qty
                                db.commit()
                    with col3:
                        if st.button("🗑️", key=f"del_{item['id']}"):
                            inv_item = db.query(UserInventory).get(item['id'])
                            if inv_item:
                                db.delete(inv_item)
                                db.commit()
                                st.rerun()

        # Clear all button
        st.markdown("---")
        if st.button("⚠️ Clear All Inventory", type="secondary"):
            db.query(UserInventory).filter(
                UserInventory.profile_id == profile.id
            ).delete()
            db.commit()
            st.warning("Inventory cleared!")
            st.rerun()

# Close database
db.close()
