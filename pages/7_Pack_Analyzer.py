"""
Pack Analyzer - Evaluate real value of in-game purchase packs.
Cuts through inflated % values to show what you're actually paying for.
"""

import streamlit as st
from pathlib import Path
import sys
import json
import base64

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load resource hierarchy
HIERARCHY_PATH = PROJECT_ROOT / "data" / "conversions" / "resource_value_hierarchy.json"
if HIERARCHY_PATH.exists():
    with open(HIERARCHY_PATH) as f:
        RESOURCE_HIERARCHY = json.load(f)
else:
    RESOURCE_HIERARCHY = {"resources": {}, "value_tiers": {}}

# Item images directory
ITEMS_DIR = PROJECT_ROOT / "assets" / "items"

# Price tiers (added lower tiers)
PRICE_TIERS = [0.99, 1.99, 2.99, 4.99, 9.99, 19.99, 49.99, 99.99]

# Speedup durations in minutes
SPEEDUP_DURATIONS = {
    "1min": 1,
    "5min": 5,
    "1hr": 60,
    "3hr": 180,
    "8hr": 480,
    "24hr": 1440,
}

# Item configurations for quick-add buttons
QUICK_ITEMS = {
    "valuable": [
        {"id": "essence_stone", "label": "Essence", "image": "essence_stone.png", "emoji": "💎"},
        {"id": "legendary_hero_shard", "label": "Leg Shard", "image": "legendary_hero_shard.png", "emoji": "⭐"},
        {"id": "gems", "label": "Gems", "image": "gems.png", "emoji": "💠"},
        {"id": "stamina", "label": "Stamina", "image": "stamina.png", "emoji": "⚡"},
        {"id": "vip_points", "label": "VIP Pts", "image": "vip_points.png", "emoji": "👑"},
        {"id": "fire_crystal", "label": "Fire Crystal", "image": "fire_crystal.png", "emoji": "🔥"},
    ],
    "speedups": [
        {"id": "speedup_general", "label": "General", "emoji": "⏱️", "durations": ["1min", "5min", "1hr", "3hr", "8hr", "24hr"]},
        {"id": "speedup_construction", "label": "Build", "emoji": "🏗️", "durations": ["1min", "5min", "1hr"]},
        {"id": "speedup_training", "label": "Train", "emoji": "⚔️", "durations": ["1min", "5min", "1hr"]},
        {"id": "speedup_research", "label": "Research", "emoji": "🔬", "durations": ["1min", "5min", "1hr"]},
        {"id": "speedup_healing", "label": "Healing", "emoji": "💚", "durations": ["1min", "5min", "1hr"]},
    ],
    "filler": [
        {"id": "meat", "label": "Meat", "image": "meat.png", "emoji": "🍖"},
        {"id": "wood", "label": "Wood", "image": "wood.png", "emoji": "🪵"},
        {"id": "coal", "label": "Coal", "image": "coal.png", "emoji": "�ite"},
        {"id": "iron", "label": "Iron", "image": "iron.png", "emoji": "🔩"},
    ]
}


def get_image_base64(image_name):
    """Get base64 encoded image for inline display."""
    image_path = ITEMS_DIR / image_name
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def render_item_button(item, price, quantity_key, add_key, size=40):
    """Render an item button with image or emoji."""
    image_b64 = None
    if "image" in item:
        image_b64 = get_image_base64(item["image"])

    if image_b64:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:4px;">
            <img src="data:image/png;base64,{image_b64}" width="{size}" height="{size}"
                 style="border-radius:4px;" title="{item['label']}">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:center;font-size:{size-10}px;margin-bottom:4px;">
            {item.get('emoji', '📦')}
        </div>
        """, unsafe_allow_html=True)


def get_resource_info(resource_id):
    """Get resource tier and value info."""
    resources = RESOURCE_HIERARCHY.get("resources", {})
    return resources.get(resource_id, {})


def get_tier_info(tier):
    """Get tier display info."""
    tiers = RESOURCE_HIERARCHY.get("value_tiers", {})
    return tiers.get(tier, {"name": tier, "color": "#666", "utility_multiplier": 0.5})


def calculate_pack_value(items, player_profile="mid_game"):
    """Calculate real value of pack items."""
    total_value = 0
    useful_value = 0
    breakdown = []

    profiles = RESOURCE_HIERARCHY.get("player_need_profiles", {})
    profile_boosts = profiles.get(player_profile, {}).get("boost_tiers", {})
    profile_reduces = profiles.get(player_profile, {}).get("reduce_tiers", {})

    for item in items:
        resource_id = item.get("resource_id")
        quantity = item.get("quantity", 0)

        if not resource_id or quantity <= 0:
            continue

        info = get_resource_info(resource_id)
        if not info:
            continue

        gem_value = info.get("gem_value_estimate", 0)
        tier = info.get("tier", "C")
        tier_info = get_tier_info(tier)
        utility_mult = tier_info.get("utility_multiplier", 0.5)

        # Apply player profile adjustments
        if resource_id in profile_boosts:
            utility_mult *= profile_boosts[resource_id]
        if resource_id in profile_reduces:
            utility_mult *= profile_reduces[resource_id]

        raw_value = quantity * gem_value
        adjusted_value = raw_value * utility_mult

        total_value += raw_value
        useful_value += adjusted_value

        breakdown.append({
            "resource_id": resource_id,
            "display_name": info.get("display_name", resource_id),
            "quantity": quantity,
            "tier": tier,
            "tier_color": tier_info.get("color", "#666"),
            "gem_value_each": gem_value,
            "raw_value": raw_value,
            "utility_mult": utility_mult,
            "adjusted_value": adjusted_value,
            "is_filler": tier == "D"
        })

    return total_value, useful_value, breakdown


def render_pack_analyzer():
    """Render the pack analyzer page."""
    st.markdown("# Pack Value Analyzer")
    st.markdown("Cut through inflated % values. See what you're *actually* paying for.")

    # Info box
    with st.expander("How it works", expanded=False):
        st.markdown("""
        1. Select a price tier tab
        2. Click item images to add them to the pack
        3. Enter quantities for each item
        4. Compare value across tiers

        **Key insight:** Packs show "500% value!" but most of that is basic resources
        (wood, meat) that you can farm for free. This tool filters those out.
        """)

    st.markdown("---")

    # Player profile selection
    col1, col2 = st.columns([1, 2])
    with col1:
        player_profile = st.selectbox(
            "Your Profile",
            options=["early_game", "mid_game", "late_game", "svs_focused"],
            format_func=lambda x: {
                "early_game": "Early Game (FC 1-20)",
                "mid_game": "Mid Game (FC 20-30)",
                "late_game": "Late Game (FC 30+)",
                "svs_focused": "SvS Focused"
            }.get(x, x),
            index=1
        )
    with col2:
        profile_info = RESOURCE_HIERARCHY.get("player_need_profiles", {}).get(player_profile, {})
        st.caption(profile_info.get("notes", ""))

    st.markdown("---")

    # Pack name
    pack_name = st.text_input("Pack Name", placeholder="e.g., Craftsman's Treasure")

    # Initialize session state
    if "pack_items" not in st.session_state:
        st.session_state.pack_items = {price: [] for price in PRICE_TIERS}

    # Tabs for each price tier
    tabs = st.tabs([f"${price:.2f}" for price in PRICE_TIERS])

    for tab_idx, (tab, price) in enumerate(zip(tabs, PRICE_TIERS)):
        with tab:
            # Valuable items section
            st.markdown("**Valuable Items**")
            cols = st.columns(len(QUICK_ITEMS["valuable"]))
            for col, item in zip(cols, QUICK_ITEMS["valuable"]):
                with col:
                    render_item_button(item, price, f"qty_{item['id']}_{price}", f"add_{item['id']}_{price}")
                    qty = st.number_input(
                        item["label"],
                        min_value=0,
                        value=0,
                        key=f"qty_{item['id']}_{price}",
                        label_visibility="collapsed"
                    )
                    if st.button("Add", key=f"add_{item['id']}_{price}", use_container_width=True):
                        if qty > 0:
                            st.session_state.pack_items[price].append({
                                "resource_id": item["id"],
                                "quantity": qty
                            })
                            st.rerun()

            # Speedups section
            st.markdown("**Speedups** (enter quantity, select duration)")
            speedup_cols = st.columns(len(QUICK_ITEMS["speedups"]))
            for col, item in zip(speedup_cols, QUICK_ITEMS["speedups"]):
                with col:
                    st.markdown(f"<div style='text-align:center;font-size:24px;'>{item['emoji']}</div>", unsafe_allow_html=True)
                    st.caption(item["label"])
                    qty = st.number_input(
                        "Qty",
                        min_value=0,
                        value=0,
                        key=f"spd_qty_{item['id']}_{price}",
                        label_visibility="collapsed"
                    )
                    duration = st.selectbox(
                        "Dur",
                        options=item["durations"],
                        key=f"spd_dur_{item['id']}_{price}",
                        label_visibility="collapsed"
                    )
                    if st.button("+", key=f"spd_add_{item['id']}_{price}", use_container_width=True):
                        if qty > 0:
                            minutes = SPEEDUP_DURATIONS.get(duration, 1) * qty
                            st.session_state.pack_items[price].append({
                                "resource_id": item["id"],
                                "quantity": minutes,
                                "display_override": f"{item['label']} {duration} x{qty}"
                            })
                            st.rerun()

            # Filler items section
            st.markdown("**Filler Items** (inflates %)")
            filler_cols = st.columns(len(QUICK_ITEMS["filler"]))
            for col, item in zip(filler_cols, QUICK_ITEMS["filler"]):
                with col:
                    render_item_button(item, price, f"fqty_{item['id']}_{price}", f"fadd_{item['id']}_{price}", size=32)
                    qty = st.number_input(
                        item["label"],
                        min_value=0,
                        value=0,
                        step=100000,
                        key=f"fqty_{item['id']}_{price}",
                        label_visibility="collapsed"
                    )
                    if st.button("Add", key=f"fadd_{item['id']}_{price}", use_container_width=True):
                        if qty > 0:
                            st.session_state.pack_items[price].append({
                                "resource_id": item["id"],
                                "quantity": qty
                            })
                            st.rerun()

            # Show current items
            items = st.session_state.pack_items[price]
            if items:
                st.markdown("---")
                st.markdown("**Items in this tier:**")
                for j, item in enumerate(items):
                    info = get_resource_info(item["resource_id"])
                    tier = info.get("tier", "C")
                    tier_info = get_tier_info(tier)
                    display_name = item.get("display_override", info.get("display_name", item["resource_id"]))

                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(
                            f"<span style='color:{tier_info['color']}'>[{tier}]</span> {display_name}",
                            unsafe_allow_html=True
                        )
                    with col2:
                        if "display_override" not in item:
                            st.write(f"x{item['quantity']:,}")
                    with col3:
                        if st.button("✕", key=f"remove_{price}_{j}"):
                            st.session_state.pack_items[price].pop(j)
                            st.rerun()
            else:
                st.caption("No items added. Click items above to add them.")

    st.markdown("---")

    # Analysis section
    st.markdown("## Analysis")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Analyze Pack Value", type="primary", use_container_width=True):
            results = []

            for price in PRICE_TIERS:
                items = st.session_state.pack_items[price]
                if items:
                    total, useful, breakdown = calculate_pack_value(items, player_profile)
                    results.append({
                        "price": price,
                        "total_gem_value": total,
                        "useful_gem_value": useful,
                        "breakdown": breakdown,
                        "value_per_dollar": useful / price if price > 0 else 0,
                        "filler_percent": sum(b["raw_value"] for b in breakdown if b["is_filler"]) / total * 100 if total > 0 else 0
                    })

            if results:
                st.session_state.analysis_results = results

    with col2:
        if st.button("Clear All Items", use_container_width=True):
            st.session_state.pack_items = {price: [] for price in PRICE_TIERS}
            if "analysis_results" in st.session_state:
                del st.session_state.analysis_results
            st.rerun()

    # Display results
    if "analysis_results" in st.session_state and st.session_state.analysis_results:
        results = st.session_state.analysis_results
        best_tier = max(results, key=lambda x: x["value_per_dollar"])

        st.markdown("### Value Comparison")

        # Result cards
        cols = st.columns(len(results))
        for col, r in zip(cols, results):
            with col:
                is_best = r == best_tier
                border = "3px solid #FFD700" if is_best else "1px solid #444"

                st.markdown(f"""
                <div style="background:rgba(74,144,217,0.1);padding:12px;border-radius:8px;border:{border};text-align:center;">
                    <div style="font-size:18px;font-weight:bold;">${r['price']:.2f}</div>
                    <hr style="margin:8px 0;border-color:#444;">
                    <div style="font-size:20px;color:#4A90D9;">{r['useful_gem_value']:,.0f}</div>
                    <div style="font-size:11px;color:#888;">Useful Gems</div>
                    <div style="font-size:12px;color:#FF6B35;margin-top:6px;">{r['filler_percent']:.0f}% filler</div>
                    <div style="font-size:14px;color:#2ECC71;margin-top:4px;">{r['value_per_dollar']:.0f} gems/$</div>
                    {"<div style='color:#FFD700;font-weight:bold;margin-top:6px;'>BEST</div>" if is_best else ""}
                </div>
                """, unsafe_allow_html=True)

        # Best tier breakdown
        st.markdown("---")
        st.markdown(f"### Breakdown: ${best_tier['price']:.2f} (Best Value)")

        for item in sorted(best_tier["breakdown"], key=lambda x: -x["adjusted_value"]):
            pct = item["adjusted_value"] / best_tier["useful_gem_value"] * 100 if best_tier["useful_gem_value"] > 0 else 0

            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                filler_tag = " <span style='color:#FF6B35'>(FILLER)</span>" if item["is_filler"] else ""
                st.markdown(
                    f"<span style='color:{item['tier_color']}'>[{item['tier']}]</span> {item['display_name']}{filler_tag}",
                    unsafe_allow_html=True
                )
            with col2:
                st.write(f"x{item['quantity']:,}")
            with col3:
                st.write(f"{item['adjusted_value']:,.0f}")
            with col4:
                st.write(f"{pct:.1f}%")

        # Recommendations
        st.markdown("---")
        st.markdown("### Verdict")

        if best_tier["filler_percent"] > 50:
            st.warning(f"⚠️ {best_tier['filler_percent']:.0f}% filler - heavily inflated value")

        valuable = [b for b in best_tier["breakdown"] if b["tier"] in ["S", "A"]]
        if valuable:
            st.success(f"✓ Good items: {', '.join(b['display_name'] for b in valuable[:3])}")
        else:
            st.error("✗ No high-value items (S/A tier). Consider skipping.")


# Main
render_pack_analyzer()

# Close database session
db.close()
