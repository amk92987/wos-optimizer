"""
Pack Analyzer - Evaluate real value of in-game purchase packs.
Cuts through inflated % values to show what you're actually paying for.
"""

import streamlit as st
from pathlib import Path
import sys
import json

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

# Constants
PRICE_TIERS = [4.99, 9.99, 19.99, 49.99, 99.99]
GEMS_PER_USD = 500  # Base conversion rate


def get_resource_list():
    """Get list of resources for selection."""
    resources = RESOURCE_HIERARCHY.get("resources", {})
    return [(k, v.get("display_name", k)) for k, v in resources.items()]


def get_resource_info(resource_id):
    """Get resource tier and value info."""
    resources = RESOURCE_HIERARCHY.get("resources", {})
    return resources.get(resource_id, {})


def get_tier_info(tier):
    """Get tier display info."""
    tiers = RESOURCE_HIERARCHY.get("value_tiers", {})
    return tiers.get(tier, {"name": tier, "color": "#666", "utility_multiplier": 0.5})


def calculate_pack_value(items, player_profile="mid_game"):
    """
    Calculate real value of pack items.
    Returns: (total_gem_value, useful_gem_value, breakdown)
    """
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
    st.info("""
    **How it works:**
    1. Enter the items in each pack tier
    2. See the real gem-equivalent value (not inflated by wood/meat)
    3. Compare $/value across tiers to find the best deal

    **Key insight:** Packs often show "500% value!" but most of that is basic resources
    (wood, meat, iron, coal) that you can farm for free. This tool filters those out.
    """)

    st.markdown("---")

    # Player profile selection
    col1, col2 = st.columns([1, 2])
    with col1:
        player_profile = st.selectbox(
            "Your Player Profile",
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
    pack_name = st.text_input("Pack Name (for reference)", placeholder="e.g., Craftsman's Treasure")

    # Tabs for each price tier
    tabs = st.tabs([f"${price:.2f}" for price in PRICE_TIERS])

    # Store items for each tier
    if "pack_items" not in st.session_state:
        st.session_state.pack_items = {price: [] for price in PRICE_TIERS}

    resource_options = get_resource_list()
    resource_dict = {k: v for k, v in resource_options}

    for i, (tab, price) in enumerate(zip(tabs, PRICE_TIERS)):
        with tab:
            st.markdown(f"### ${price:.2f} Tier")

            # Quick add valuable items
            st.markdown("**Valuable Items:**")
            quick_cols = st.columns(6)
            quick_items = [
                ("essence_stone", "Essence"),
                ("speedup_general", "Speedups (min)"),
                ("legendary_hero_shard", "Leg Shards"),
                ("gems", "Gems"),
                ("stamina", "Stamina"),
                ("vip_points", "VIP Pts")
            ]
            for qcol, (res_id, label) in zip(quick_cols, quick_items):
                with qcol:
                    qty = st.number_input(label, min_value=0, value=0, key=f"quick_{res_id}_{price}", label_visibility="collapsed")
                    if st.button(f"+{label[:6]}", key=f"qbtn_{res_id}_{price}", use_container_width=True):
                        if qty > 0:
                            st.session_state.pack_items[price].append({
                                "resource_id": res_id,
                                "quantity": qty
                            })
                            st.rerun()

            # Quick add filler items (to show inflation)
            st.markdown("**Filler Items (inflates %):**")
            filler_cols = st.columns(4)
            filler_items = [
                ("meat", "Meat"),
                ("wood", "Wood"),
                ("coal", "Coal"),
                ("iron", "Iron")
            ]
            for fcol, (res_id, label) in zip(filler_cols, filler_items):
                with fcol:
                    fqty = st.number_input(label, min_value=0, value=0, key=f"filler_{res_id}_{price}", label_visibility="collapsed")
                    if st.button(f"+{label}", key=f"fbtn_{res_id}_{price}", use_container_width=True):
                        if fqty > 0:
                            st.session_state.pack_items[price].append({
                                "resource_id": res_id,
                                "quantity": fqty
                            })
                            st.rerun()

            # Add item form (for other resources)
            with st.expander("Add Other Resources"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    selected_resource = st.selectbox(
                        "Resource",
                        options=[k for k, v in resource_options],
                        format_func=lambda x: resource_dict.get(x, x),
                        key=f"resource_{price}"
                    )

                with col2:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=0,
                        value=0,
                        key=f"quantity_{price}"
                    )

                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Add", key=f"add_{price}"):
                        if quantity > 0:
                            st.session_state.pack_items[price].append({
                                "resource_id": selected_resource,
                                "quantity": quantity
                            })
                            st.rerun()

            # Show current items
            items = st.session_state.pack_items[price]
            if items:
                st.markdown("**Items in this tier:**")
                for j, item in enumerate(items):
                    info = get_resource_info(item["resource_id"])
                    tier = info.get("tier", "C")
                    tier_info = get_tier_info(tier)

                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(
                            f"<span style='color:{tier_info['color']}'>[{tier}]</span> "
                            f"{info.get('display_name', item['resource_id'])}",
                            unsafe_allow_html=True
                        )
                    with col2:
                        st.write(f"x{item['quantity']:,}")
                    with col3:
                        if st.button("X", key=f"remove_{price}_{j}"):
                            st.session_state.pack_items[price].pop(j)
                            st.rerun()
            else:
                st.caption("No items added yet. Add items above.")

    st.markdown("---")

    # Analysis section
    st.markdown("## Analysis")

    if st.button("Analyze Pack Value", type="primary"):
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
            # Summary table
            st.markdown("### Value Comparison")

            # Find best value
            best_tier = max(results, key=lambda x: x["value_per_dollar"]) if results else None

            cols = st.columns(len(results))
            for col, r in zip(cols, results):
                with col:
                    is_best = r == best_tier
                    border_style = "3px solid #FFD700" if is_best else "1px solid #444"

                    st.markdown(f"""
                    <div style="background: rgba(74, 144, 217, 0.1); padding: 16px;
                                border-radius: 8px; border: {border_style}; text-align: center;">
                        <div style="font-size: 20px; font-weight: bold;">${r['price']:.2f}</div>
                        <div style="font-size: 12px; color: #888;">Price</div>
                        <hr style="margin: 10px 0; border-color: #444;">
                        <div style="font-size: 24px; color: #4A90D9;">{r['useful_gem_value']:,.0f}</div>
                        <div style="font-size: 12px; color: #888;">Useful Gems</div>
                        <div style="font-size: 14px; color: #FF6B35; margin-top: 8px;">
                            {r['filler_percent']:.0f}% filler
                        </div>
                        <div style="font-size: 16px; color: #2ECC71; margin-top: 8px;">
                            {r['value_per_dollar']:.0f} gems/$
                        </div>
                        {"<div style='color: #FFD700; margin-top: 8px;'>BEST VALUE</div>" if is_best else ""}
                    </div>
                    """, unsafe_allow_html=True)

            # Detailed breakdown for best tier
            st.markdown("---")
            st.markdown(f"### Detailed Breakdown: ${best_tier['price']:.2f} (Best Value)")

            for item in sorted(best_tier["breakdown"], key=lambda x: -x["adjusted_value"]):
                pct_of_value = item["adjusted_value"] / best_tier["useful_gem_value"] * 100 if best_tier["useful_gem_value"] > 0 else 0

                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(
                        f"<span style='color:{item['tier_color']}'>[{item['tier']}]</span> "
                        f"{item['display_name']}" +
                        (" <span style='color:#FF6B35'>(FILLER)</span>" if item["is_filler"] else ""),
                        unsafe_allow_html=True
                    )
                with col2:
                    st.write(f"x{item['quantity']:,}")
                with col3:
                    st.write(f"{item['adjusted_value']:,.0f} gems")
                with col4:
                    st.write(f"{pct_of_value:.1f}%")

            # Recommendations
            st.markdown("---")
            st.markdown("### Recommendations")

            if best_tier["filler_percent"] > 50:
                st.warning(f"This pack is {best_tier['filler_percent']:.0f}% filler (basic resources). "
                          f"The advertised value is heavily inflated.")

            # Check for key valuable items
            valuable_items = [b for b in best_tier["breakdown"] if b["tier"] in ["S", "A"]]
            if valuable_items:
                st.success(f"Good items found: {', '.join(b['display_name'] for b in valuable_items[:3])}")
            else:
                st.error("No high-value items (S/A tier) found in this pack. Consider skipping.")

            # Efficiency comparison
            if len(results) > 1:
                st.markdown("**Efficiency across tiers:**")
                for r in sorted(results, key=lambda x: -x["value_per_dollar"]):
                    efficiency_bar = min(r["value_per_dollar"] / best_tier["value_per_dollar"] * 100, 100)
                    st.markdown(
                        f"${r['price']:.2f}: "
                        f"<span style='color:#4A90D9'>{r['value_per_dollar']:.0f} gems/$</span> "
                        f"({efficiency_bar:.0f}% of best)",
                        unsafe_allow_html=True
                    )
        else:
            st.warning("Add items to at least one tier to analyze.")

    # Clear button
    if st.button("Clear All Items"):
        st.session_state.pack_items = {price: [] for price in PRICE_TIERS}
        st.rerun()

    st.markdown("---")

    # Reference: Value tiers
    with st.expander("Reference: Resource Value Tiers"):
        st.markdown("""
        | Tier | Category | Examples | Real Value |
        |------|----------|----------|------------|
        | **S** | Critical | Essence Stones, Legendary Shards | High |
        | **A** | High Value | Speedups, Stamina, VIP Points | Medium-High |
        | **B** | Medium | Gems, Fire Crystals, Pet Items | Medium |
        | **C** | Low | Alliance Coins, Teleports | Low |
        | **D** | Filler | Wood, Meat, Iron, Coal | ~Zero |

        **Key insight:** Tier D resources inflate the "% value" shown in-game but are
        essentially free through normal gameplay. This tool filters them out.
        """)


# Main
render_pack_analyzer()

# Close database session
db.close()
