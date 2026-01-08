"""
Quick Tips - Cheat sheet of key game knowledge.
The stuff most players get wrong, all in one place.
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

# Load quick tips
TIPS_PATH = PROJECT_ROOT / "data" / "guides" / "quick_tips.json"
if TIPS_PATH.exists():
    with open(TIPS_PATH) as f:
        QUICK_TIPS = json.load(f)
else:
    QUICK_TIPS = {"categories": {}, "most_common_mistakes": []}


def get_priority_color(priority):
    """Get color for priority level."""
    colors = {
        "critical": "#E74C3C",
        "high": "#F39C12",
        "medium": "#3498DB",
        "low": "#2ECC71"
    }
    return colors.get(priority, "#666")


def get_priority_label(priority):
    """Get label for priority."""
    labels = {
        "critical": "MUST KNOW",
        "high": "Important",
        "medium": "Good to Know",
        "low": "FYI"
    }
    return labels.get(priority, priority)


def get_category_icon(icon):
    """Get emoji for category icon."""
    icons = {
        "island": "🏝️",
        "battle": "⚔️",
        "research": "🔬",
        "gear": "⚙️",
        "charm": "💎",
        "combat": "🎯",
        "pet": "🐻",
        "event": "📅",
        "pack": "📦",
        "hero": "🦸",
        "alliance": "🏰",
        "newbie": "🆕",
        "shield": "🛡️"
    }
    return icons.get(icon, "📌")


def render_category_tips(category_id, category_data):
    """Render tips for a single category."""
    icon = get_category_icon(category_data.get("icon", ""))
    name = category_data.get("name", category_id)
    tips = category_data.get("tips", [])

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_tips = sorted(tips, key=lambda x: priority_order.get(x.get("priority", "medium"), 2))

    with st.expander(f"{icon} {name} ({len(tips)} tips)", expanded=False):
        for tip in sorted_tips:
            priority = tip.get("priority", "medium")
            priority_color = get_priority_color(priority)
            priority_label = get_priority_label(priority)

            st.markdown(f"""
            <div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid {priority_color};
                        padding: 12px; border-radius: 4px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="font-weight: bold; color: #E8F4F8; font-size: 15px; flex: 1;">
                        {tip.get('tip', '')}
                    </div>
                    <span style="background: {priority_color}; padding: 2px 8px; border-radius: 4px;
                                 font-size: 10px; margin-left: 8px; white-space: nowrap;">
                        {priority_label}
                    </span>
                </div>
                <div style="color: #B8D4E8; font-size: 13px; margin-top: 8px;">
                    {tip.get('detail', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_critical_tips():
    """Render all critical tips across categories."""
    categories = QUICK_TIPS.get("categories", {})
    critical_tips = []

    for cat_id, cat_data in categories.items():
        icon = get_category_icon(cat_data.get("icon", ""))
        name = cat_data.get("name", cat_id)
        for tip in cat_data.get("tips", []):
            if tip.get("priority") == "critical":
                critical_tips.append({
                    "category": name,
                    "icon": icon,
                    "tip": tip.get("tip", ""),
                    "detail": tip.get("detail", "")
                })

    st.markdown("### Critical Tips (Must Know)")
    st.markdown("These are the most impactful pieces of knowledge. Get these wrong and you'll fall behind.")

    for tip in critical_tips:
        st.markdown(f"""
        <div style="background: rgba(231, 76, 60, 0.15); border: 1px solid #E74C3C;
                    padding: 16px; border-radius: 8px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 20px; margin-right: 8px;">{tip['icon']}</span>
                <span style="color: #E74C3C; font-size: 12px; font-weight: bold;">{tip['category']}</span>
            </div>
            <div style="font-weight: bold; color: #E8F4F8; font-size: 16px; margin-bottom: 8px;">
                {tip['tip']}
            </div>
            <div style="color: #B8D4E8; font-size: 14px;">
                {tip['detail']}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_common_mistakes():
    """Render common mistakes section."""
    mistakes = QUICK_TIPS.get("most_common_mistakes", [])

    st.markdown("### Most Common Mistakes")
    st.markdown("Things players do wrong that cost them progress or battles.")

    for mistake in mistakes:
        category = mistake.get("category", "")
        categories = QUICK_TIPS.get("categories", {})
        cat_data = categories.get(category, {})
        icon = get_category_icon(cat_data.get("icon", ""))

        st.markdown(f"""
        <div style="background: rgba(74, 144, 217, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
            <div style="display: flex; align-items: flex-start;">
                <span style="font-size: 18px; margin-right: 12px;">{icon}</span>
                <div style="flex: 1;">
                    <div style="color: #E74C3C; font-weight: bold; margin-bottom: 4px;">
                        ❌ {mistake.get('mistake', '')}
                    </div>
                    <div style="color: #2ECC71;">
                        ✓ {mistake.get('correction', '')}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_search_tips():
    """Render searchable tips section."""
    categories = QUICK_TIPS.get("categories", {})

    # Flatten all tips
    all_tips = []
    for cat_id, cat_data in categories.items():
        icon = get_category_icon(cat_data.get("icon", ""))
        name = cat_data.get("name", cat_id)
        for tip in cat_data.get("tips", []):
            all_tips.append({
                "category": name,
                "icon": icon,
                "tip": tip.get("tip", ""),
                "detail": tip.get("detail", ""),
                "priority": tip.get("priority", "medium"),
                "searchable": f"{tip.get('tip', '')} {tip.get('detail', '')}".lower()
            })

    search = st.text_input("Search tips...", placeholder="e.g., speedup, daybreak, lethality")

    if search:
        search_lower = search.lower()
        filtered = [t for t in all_tips if search_lower in t["searchable"]]

        if filtered:
            st.markdown(f"**Found {len(filtered)} tips:**")
            for tip in filtered:
                priority_color = get_priority_color(tip["priority"])
                st.markdown(f"""
                <div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid {priority_color};
                            padding: 12px; border-radius: 4px; margin-bottom: 8px;">
                    <div style="font-size: 12px; color: #B8D4E8; margin-bottom: 4px;">
                        {tip['icon']} {tip['category']}
                    </div>
                    <div style="font-weight: bold; color: #E8F4F8;">
                        {tip['tip']}
                    </div>
                    <div style="color: #B8D4E8; font-size: 13px; margin-top: 4px;">
                        {tip['detail']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tips found matching your search.")


def render_quick_tips():
    """Render the quick tips page."""
    st.markdown("# Quick Tips & Cheat Sheet")
    st.markdown("Key game knowledge in one place. The stuff most players get wrong.")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Critical Tips",
        "By Category",
        "Common Mistakes",
        "Search"
    ])

    with tab1:
        render_critical_tips()

    with tab2:
        st.markdown("### Tips by Category")
        st.markdown("Expand each category to see all tips.")

        categories = QUICK_TIPS.get("categories", {})

        # Define display order
        category_order = [
            "new_player", "svs_prep", "svs_battle", "daybreak_island", "research", "combat",
            "chief_gear", "chief_charms", "pets", "events",
            "heroes", "alliance", "packs"
        ]

        for cat_id in category_order:
            if cat_id in categories:
                render_category_tips(cat_id, categories[cat_id])

        # Any remaining categories not in order
        for cat_id, cat_data in categories.items():
            if cat_id not in category_order:
                render_category_tips(cat_id, cat_data)

    with tab3:
        render_common_mistakes()

    with tab4:
        render_search_tips()

    # Footer with tip count
    categories = QUICK_TIPS.get("categories", {})
    total_tips = sum(len(cat.get("tips", [])) for cat in categories.values())
    st.markdown("---")
    st.caption(f"Total: {total_tips} tips across {len(categories)} categories")


# Main
render_quick_tips()

# Close database session
db.close()
