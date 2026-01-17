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
    with open(TIPS_PATH, encoding='utf-8') as f:
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
        "shield": "🛡️",
        "upgrade": "📈"
    }
    return icons.get(icon, "📌")


def render_tip_card(title, detail, border_color, badge_text=None, badge_color=None):
    """Render a single tip card with consistent styling across all tabs.

    Args:
        title: Main tip text (bold)
        detail: Supporting detail text
        border_color: Color for left border accent
        badge_text: Optional badge text (e.g., priority label or category)
        badge_color: Color for badge background (uses border_color if not specified)
    """
    badge_bg = badge_color or border_color
    badge_html = ""
    if badge_text:
        badge_html = f'<span style="background: {badge_bg}; padding: 3px 10px; border-radius: 4px; font-size: 11px; white-space: nowrap; color: #fff;">{badge_text}</span>'

    html = f'''<div style="background: rgba(74, 144, 217, 0.1); border-left: 4px solid {border_color}; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
<div style="flex: 1;">
<div style="font-weight: bold; color: #E8F4F8; font-size: 15px; margin-bottom: 6px;">{title}</div>
<div style="color: #B8D4E8; font-size: 13px; line-height: 1.5;">{detail}</div>
</div>
{badge_html}
</div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)


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

            render_tip_card(
                title=tip.get('tip', ''),
                detail=tip.get('detail', ''),
                border_color=priority_color,
                badge_text=priority_label,
                badge_color=priority_color
            )


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

    st.markdown("### Critical Tips")
    st.markdown("The most impactful knowledge. Get these wrong and you'll fall behind.")

    for tip in critical_tips:
        render_tip_card(
            title=tip['tip'],
            detail=tip['detail'],
            border_color="#E74C3C",
            badge_text=f"{tip['icon']} {tip['category']}",
            badge_color="#555"
        )


def render_common_mistakes():
    """Render common mistakes section."""
    mistakes = QUICK_TIPS.get("most_common_mistakes", [])

    st.markdown("### Common Mistakes")
    st.markdown("Things players do wrong that cost them progress or battles.")

    for mistake in mistakes:
        category = mistake.get("category", "")
        categories = QUICK_TIPS.get("categories", {})
        cat_data = categories.get(category, {})
        icon = get_category_icon(cat_data.get("icon", ""))
        cat_name = cat_data.get("name", category)

        render_tip_card(
            title=mistake.get('mistake', ''),
            detail=f"Do this: {mistake.get('correction', '')}",
            border_color="#E74C3C",
            badge_text=f"{icon} {cat_name}",
            badge_color="#555"
        )


def get_current_generation(server_age_days: int) -> int:
    """Calculate current hero generation based on server age."""
    gen_thresholds = [40, 120, 200, 280, 360, 440, 520, 600, 680, 760, 840, 920, 1000]
    for i, threshold in enumerate(gen_thresholds):
        if server_age_days < threshold:
            return i + 1
    return 14


def get_investment_color(investment: str) -> str:
    """Get color for investment level."""
    investment_upper = investment.upper()
    if "MAX" in investment_upper:
        return "#E74C3C"  # Red - critical
    elif "HIGH" in investment_upper:
        return "#F39C12"  # Orange - high priority
    elif "MEDIUM" in investment_upper:
        return "#3498DB"  # Blue - medium
    elif "LOW" in investment_upper:
        return "#95A5A6"  # Gray - low
    elif "SKIP" in investment_upper:
        return "#7F8C8D"  # Dark gray - skip
    return "#666"


def get_tier_color(tier: str) -> str:
    """Get color for tier badge."""
    tier_colors = {
        "S+": "#E74C3C",  # Red
        "S": "#F39C12",   # Orange
        "A": "#3498DB",   # Blue
        "B": "#2ECC71",   # Green
        "C": "#95A5A6",   # Gray
        "D": "#7F8C8D"    # Dark gray
    }
    return tier_colors.get(tier, "#666")


def get_class_icon(hero_class: str) -> str:
    """Get emoji for hero class."""
    icons = {
        "Infantry": "🛡️",
        "Lancer": "🔱",
        "Marksman": "🎯"
    }
    return icons.get(hero_class, "⚔️")


def get_rarity_color(rarity: str) -> str:
    """Get color for rarity badge."""
    rarity_colors = {
        "Legendary": "#FFD700",  # Gold
        "Epic": "#9B59B6",       # Purple
        "Rare": "#3498DB"        # Blue
    }
    return rarity_colors.get(rarity, "#666")


def render_hero_card(hero: dict):
    """Render a single hero investment card."""
    name = hero.get("name", "Unknown")
    hero_class = hero.get("class", "")
    tier = hero.get("tier", "C")
    tier_exp = hero.get("tier_expedition", tier)
    rarity = hero.get("rarity", "")
    has_mythic = hero.get("mythic", False)
    investment = hero.get("investment", "MEDIUM")
    why = hero.get("why", "")
    skills = hero.get("skills", "")
    longevity = hero.get("longevity", "")

    tier_color = get_tier_color(tier)
    investment_color = get_investment_color(investment)
    class_icon = get_class_icon(hero_class)

    # Show expedition tier if different from overall
    tier_display = tier
    if tier_exp and tier_exp != tier:
        tier_display = f"{tier} (Exp: {tier_exp})"

    # Build badges
    badges_html = f'<span style="background: {tier_color}; padding: 2px 8px; border-radius: 4px; font-size: 11px; color: #fff;">{tier_display}</span>'

    # Add mythic gear badge if applicable
    if has_mythic:
        badges_html += ' <span style="background: linear-gradient(135deg, #FFD700, #FFA500); padding: 2px 8px; border-radius: 4px; font-size: 10px; color: #000; font-weight: bold;">MYTHIC GEAR</span>'

    html = f'''<div style="background: rgba(74, 144, 217, 0.08); border-left: 4px solid {investment_color}; padding: 14px; border-radius: 8px; margin-bottom: 10px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
<span style="font-size: 18px;">{class_icon}</span>
<span style="font-weight: bold; color: #E8F4F8; font-size: 16px;">{name}</span>
{badges_html}
</div>
<span style="background: {investment_color}; padding: 3px 10px; border-radius: 4px; font-size: 11px; white-space: nowrap; color: #fff;">{investment}</span>
</div>
<div style="color: #B8D4E8; font-size: 13px; line-height: 1.6;">
<div style="margin-bottom: 6px;"><strong>Why:</strong> {why}</div>
<div style="margin-bottom: 6px;"><strong>Skills:</strong> {skills}</div>
<div><strong>Longevity:</strong> {longevity}</div>
</div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def render_hero_investment():
    """Render hero investment by generation with expanders."""
    categories = QUICK_TIPS.get("categories", {})
    investment_data = categories.get("hero_investment_by_gen", {})
    generations = investment_data.get("generations", {})
    spending_advice = investment_data.get("spending_advice", {})

    st.markdown("### Hero Investment by Generation")
    st.markdown("Which heroes to prioritize when unlocking each generation. Expand a generation to see detailed hero recommendations.")

    if not generations:
        st.info("No hero investment data available.")
        return

    # Get user's current generation from profile
    current_gen = get_current_generation(profile.server_age_days)

    # Show current generation info
    st.markdown(f"**Your current generation:** Gen {current_gen} (based on {profile.server_age_days} server days)")

    # Show spending profile advice if available
    spending = profile.spending_profile or "f2p"
    if spending in spending_advice:
        st.info(f"**{spending.upper()} Tip:** {spending_advice[spending]}")

    st.markdown("---")

    # Render each generation as an expander
    for gen_num in range(1, 15):
        gen_key = str(gen_num)
        if gen_key not in generations:
            continue

        gen_data = generations[gen_key]
        summary = gen_data.get("summary", f"Generation {gen_num}")
        heroes = gen_data.get("heroes", [])

        # Auto-expand prior, current, and next generation
        is_expanded = (gen_num >= current_gen - 1) and (gen_num <= current_gen + 1)

        # Add visual indicator for current gen
        if gen_num == current_gen:
            gen_label = f"⭐ Gen {gen_num}: {summary} (CURRENT)"
        elif gen_num == current_gen - 1:
            gen_label = f"Gen {gen_num}: {summary} (Previous)"
        elif gen_num == current_gen + 1:
            gen_label = f"Gen {gen_num}: {summary} (Next)"
        else:
            gen_label = f"Gen {gen_num}: {summary}"

        with st.expander(gen_label, expanded=is_expanded):
            # Count investment levels for quick summary
            max_count = sum(1 for h in heroes if "MAX" in h.get("investment", "").upper())
            high_count = sum(1 for h in heroes if "HIGH" in h.get("investment", "").upper() and "MAX" not in h.get("investment", "").upper())
            skip_count = sum(1 for h in heroes if "SKIP" in h.get("investment", "").upper())

            # Quick summary
            summary_parts = []
            if max_count > 0:
                summary_parts.append(f"**{max_count} MAX**")
            if high_count > 0:
                summary_parts.append(f"{high_count} HIGH")
            if skip_count > 0:
                summary_parts.append(f"{skip_count} SKIP")

            if summary_parts:
                st.markdown(f"Investment summary: {', '.join(summary_parts)}")

            # Render each hero card
            for hero in heroes:
                render_hero_card(hero)


def render_alliance_management():
    """Render alliance management tips for R4/R5."""
    categories = QUICK_TIPS.get("categories", {})
    alliance_data = categories.get("alliance_management", {})

    st.markdown("### Alliance Management (R4/R5)")
    st.markdown("Essential knowledge for alliance officers and leaders.")

    tips = alliance_data.get("tips", [])
    if not tips:
        st.info("No alliance management tips available.")
        return

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_tips = sorted(tips, key=lambda x: priority_order.get(x.get("priority", "medium"), 2))

    for tip in sorted_tips:
        priority = tip.get("priority", "medium")
        priority_color = get_priority_color(priority)
        priority_label = get_priority_label(priority)

        render_tip_card(
            title=tip.get('tip', ''),
            detail=tip.get('detail', ''),
            border_color=priority_color,
            badge_text=priority_label,
            badge_color=priority_color
        )

    # Show related common mistakes
    mistakes = QUICK_TIPS.get("most_common_mistakes", [])
    alliance_mistakes = [m for m in mistakes if m.get("category") == "alliance_management"]

    if alliance_mistakes:
        st.markdown("---")
        st.markdown("### Common Mistakes")
        for mistake in alliance_mistakes:
            render_tip_card(
                title=f"Mistake: {mistake.get('mistake', '')}",
                detail=f"Fix: {mistake.get('correction', '')}",
                border_color="#E74C3C",
                badge_text="Avoid",
                badge_color="#E74C3C"
            )


def render_quick_tips():
    """Render the quick tips page."""
    st.markdown("# Quick Tips & Cheat Sheet")
    st.markdown("Key game knowledge in one place. The stuff most players get wrong.")

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Critical Tips",
        "Hero Investment",
        "Alliance (R4/R5)",
        "Common Mistakes",
        "By Category"
    ])

    with tab1:
        render_critical_tips()

    with tab2:
        render_hero_investment()

    with tab3:
        render_alliance_management()

    with tab4:
        render_common_mistakes()

    with tab5:
        st.markdown("### All Tips by Category")
        st.markdown("Browse all tips organized by topic. Expand each category to explore.")

        categories = QUICK_TIPS.get("categories", {})

        # Define display order (alliance_management and hero_investment_by_gen have their own tabs)
        category_order = [
            "new_player", "upgrade_priorities", "heroes",
            "svs_prep", "svs_battle", "daybreak_island", "research", "combat",
            "chief_gear", "chief_charms", "pets", "events", "packs", "farm_accounts"
        ]

        for cat_id in category_order:
            if cat_id in categories:
                render_category_tips(cat_id, categories[cat_id])

        # Any remaining categories not in order (except those with their own tabs)
        excluded_from_category_tab = {"alliance_management", "hero_investment_by_gen"}
        for cat_id, cat_data in categories.items():
            if cat_id not in category_order and cat_id not in excluded_from_category_tab:
                render_category_tips(cat_id, cat_data)

    # Footer with tip count
    categories = QUICK_TIPS.get("categories", {})
    total_tips = sum(len(cat.get("tips", [])) for cat in categories.values())
    st.markdown("---")
    st.caption(f"Total: {total_tips} tips across {len(categories)} categories")


# Main
render_quick_tips()

# Close database session
db.close()
