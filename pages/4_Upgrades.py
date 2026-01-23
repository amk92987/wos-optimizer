"""
Recommendations Page - Get personalized upgrade recommendations.
"""

import streamlit as st
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from database.models import UserHero
from engine.recommender import RecommendationEngine, UpgradeType

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load hero data
heroes_file = PROJECT_ROOT / "data" / "heroes.json"
with open(heroes_file, encoding='utf-8') as f:
    HERO_DATA = json.load(f)

# Get user heroes
user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile.id).all()


def get_tier_color(tier: str) -> str:
    """Get color for tier badge."""
    colors = {
        "S+": "#FF4444",
        "S": "#FF8C00",
        "A": "#9932CC",
        "B": "#4169E1",
        "C": "#32CD32",
        "D": "#808080"
    }
    return colors.get(tier, "#808080")


def get_class_color(hero_class: str) -> str:
    """Get color for class badge."""
    colors = {
        "Infantry": "#E74C3C",
        "Marksman": "#3498DB",
        "Lancer": "#2ECC71"
    }
    return colors.get(hero_class, "#808080")


def get_upgrade_icon(upgrade_type: UpgradeType) -> str:
    """Get icon for upgrade type."""
    icons = {
        UpgradeType.LEVEL: "📊",
        UpgradeType.STARS: "⭐",
        UpgradeType.EXPLORATION_SKILL: "🗺️",
        UpgradeType.EXPEDITION_SKILL: "⚔️",
        UpgradeType.GEAR: "🛡️"
    }
    return icons.get(upgrade_type, "📋")


def render_recommendation_card(rec, index: int):
    """Render a recommendation card."""
    # Get hero data
    hero_data = next((h for h in HERO_DATA['heroes'] if h['name'] == rec.hero_name), None)

    tier = hero_data.get('tier_overall', '?') if hero_data else '?'
    hero_class = hero_data.get('hero_class', '?') if hero_data else '?'

    tier_color = get_tier_color(tier)
    class_color = get_class_color(hero_class)

    # Priority styling
    priority_colors = {
        'high': ('#FF6B35', 'rgba(255, 107, 53, 0.2)'),
        'medium': ('#FFD700', 'rgba(255, 215, 0, 0.15)'),
        'low': ('#4A90D9', 'rgba(74, 144, 217, 0.15)')
    }
    border_color, bg_color = priority_colors.get(rec.category, ('#4A90D9', 'rgba(74, 144, 217, 0.15)'))

    icon = get_upgrade_icon(rec.upgrade_type)

    st.markdown(f"""
    <div style="
        background: {bg_color};
        border: 2px solid {border_color};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 24px;">{icon}</span>
                <div>
                    <div style="font-size: 18px; font-weight: bold; color: #E8F4F8;">
                        {rec.hero_name}
                    </div>
                    <div style="display: flex; gap: 8px; margin-top: 4px;">
                        <span style="
                            background: {tier_color};
                            color: white;
                            padding: 2px 8px;
                            border-radius: 4px;
                            font-size: 11px;
                            font-weight: bold;
                        ">{tier}</span>
                        <span style="
                            background: rgba(255,255,255,0.1);
                            border-left: 3px solid {class_color};
                            padding: 2px 8px;
                            font-size: 11px;
                            color: #E8F4F8;
                        ">{hero_class}</span>
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="
                    background: {border_color};
                    color: white;
                    padding: 4px 12px;
                    border-radius: 16px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                ">{rec.category} priority</div>
                <div style="color: #B8D4E8; font-size: 12px; margin-top: 4px;">
                    Score: {rec.priority_score:.2f}
                </div>
            </div>
        </div>
        <div style="
            background: rgba(0,0,0,0.2);
            padding: 12px;
            border-radius: 8px;
        ">
            <div style="color: #E8F4F8; font-size: 14px; margin-bottom: 8px;">
                <strong>{rec.upgrade_type.value.replace('_', ' ').title()}</strong>:
                {rec.current_value} → {rec.target_value}
            </div>
            <div style="color: #B8D4E8; font-size: 13px;">
                {rec.reason}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Page content
st.markdown("# 📈 Upgrade Recommendations")
st.markdown("Personalized recommendations based on your heroes and priorities.")

st.markdown("---")

# Check if user has heroes
if not user_heroes:
    st.warning("""
    ## No Heroes Added Yet!

    To get personalized recommendations, you need to add your heroes first.

    1. Go to **🦸 Heroes** page
    2. Add the heroes you own
    3. Set their current levels and skills
    4. Come back here for recommendations!
    """)
else:
    # Priority summary
    st.markdown("### Your Priority Settings")

    priorities = [
        ("SvS Combat", profile.priority_svs),
        ("Rally", profile.priority_rally),
        ("Castle Battle", profile.priority_castle_battle),
        ("Exploration", profile.priority_exploration),
        ("Gathering", profile.priority_gathering),
    ]

    cols = st.columns(5)
    for col, (name, value) in zip(cols, priorities):
        with col:
            filled = "★" * value
            empty = "☆" * (5 - value)
            st.markdown(f"""
            <div style="text-align:center;padding:10px;background:rgba(74,144,217,0.15);border-radius:8px;">
                <div style="font-size:14px;color:#B8D4E8;margin-bottom:6px;">{name}</div>
                <div style="font-size:22px;color:#FFD700;">{filled}<span style="color:#4A5568;">{empty}</span></div>
            </div>
            """, unsafe_allow_html=True)

    st.caption("Adjust priorities on the sidebar to change recommendation focus")

    st.markdown("---")

    # Generate recommendations
    engine = RecommendationEngine(HERO_DATA, user_heroes, profile)

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🎯 Top Recommendations", "🦸 Best Heroes to Invest", "📊 Analysis"])

    with tab1:
        st.markdown("### Top Upgrade Recommendations")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox(
                "Filter by upgrade type",
                ["All", "Level", "Skills", "Stars"]
            )
        with col2:
            filter_priority = st.selectbox(
                "Filter by priority",
                ["All", "High", "Medium", "Low"]
            )

        recommendations = engine.generate_recommendations(limit=30)

        # Apply filters
        if filter_type == "Level":
            recommendations = [r for r in recommendations if r.upgrade_type == UpgradeType.LEVEL]
        elif filter_type == "Skills":
            recommendations = [r for r in recommendations if r.upgrade_type in [UpgradeType.EXPLORATION_SKILL, UpgradeType.EXPEDITION_SKILL]]
        elif filter_type == "Stars":
            recommendations = [r for r in recommendations if r.upgrade_type == UpgradeType.STARS]

        if filter_priority != "All":
            recommendations = [r for r in recommendations if r.category == filter_priority.lower()]

        if recommendations:
            # Show recommendations in a single list, ordered by priority
            for i, rec in enumerate(recommendations[:20]):
                render_recommendation_card(rec, i)
        else:
            st.info("No recommendations match your filters. Try adjusting the filters above.")

    with tab2:
        st.markdown("### Best Heroes to Invest In")
        st.markdown(f"Based on your priorities, generation, and spending profile ({profile.spending_profile.upper()}):")

        top_heroes = engine.get_top_heroes_to_invest(limit=10)

        if not top_heroes:
            st.info("No owned heroes yet. Go to Heroes page to add your heroes first!")
        else:
            for i, hero in enumerate(top_heroes):
                tier_color = get_tier_color(hero['tier'])
                class_color = get_class_color(hero['class'])

                # Current vs target display
                current_level = hero.get('current_level', 1)
                current_stars = hero.get('current_stars', 0)
                target_level = hero.get('target_level', 50)
                target_stars = hero.get('target_stars', 2)
                advice = hero.get('advice', '')

                # Progress indicator
                level_progress = f"L{current_level} → L{target_level}" if current_level < target_level else f"L{current_level} ✓"
                stars_display = f"{'★' * current_stars}{'☆' * (5-current_stars)}"
                target_stars_display = f"{'★' * target_stars}{'☆' * (5-target_stars)}"

                st.markdown(f"""
                <div style="
                    background: rgba(46, 90, 140, 0.25);
                    border: 1px solid rgba(74, 144, 217, 0.3);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <div style="
                                font-size: 24px;
                                font-weight: bold;
                                color: #4A90D9;
                                width: 40px;
                            ">#{i+1}</div>
                            <div>
                                <div style="font-size: 18px; font-weight: bold; color: #E8F4F8;">
                                    {hero['name']}
                                </div>
                                <div style="display: flex; gap: 8px; margin-top: 4px; align-items: center;">
                                    <span style="
                                        background: {tier_color};
                                        color: white;
                                        padding: 2px 8px;
                                        border-radius: 4px;
                                        font-size: 11px;
                                    ">{hero['tier']}</span>
                                    <span style="
                                        background: rgba(255,255,255,0.1);
                                        border-left: 3px solid {class_color};
                                        padding: 2px 8px;
                                        font-size: 11px;
                                        color: #E8F4F8;
                                    ">{hero['class']}</span>
                                    <span style="color: #B8D4E8; font-size: 11px;">Gen {hero['generation']}</span>
                                </div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #4A90D9; font-size: 14px; font-weight: bold;">{level_progress}</div>
                            <div style="color: #FFD700; font-size: 12px;">{stars_display}</div>
                            <div style="color: #888; font-size: 11px;">Target: {target_stars_display}</div>
                        </div>
                    </div>
                    <div style="color: #4CAF50; font-size: 13px; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(74,144,217,0.2);">
                        💡 {advice}
                    </div>
                    <div style="color: #B8D4E8; font-size: 11px; margin-top: 6px;">
                        {hero['notes']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### Hero Analysis")

        # Summary stats
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div style="background: rgba(74, 144, 217, 0.2); padding: 20px; border-radius: 12px;">
                <div style="font-size: 14px; color: #B8D4E8;">Total Heroes Owned</div>
                <div style="font-size: 32px; font-weight: bold; color: #4A90D9;">{}</div>
            </div>
            """.format(len(user_heroes)), unsafe_allow_html=True)

        with col2:
            avg_level = sum(h.level for h in user_heroes) / len(user_heroes) if user_heroes else 0
            st.markdown("""
            <div style="background: rgba(255, 107, 53, 0.2); padding: 20px; border-radius: 12px;">
                <div style="font-size: 14px; color: #B8D4E8;">Average Level</div>
                <div style="font-size: 32px; font-weight: bold; color: #FF6B35;">{:.1f}</div>
            </div>
            """.format(avg_level), unsafe_allow_html=True)

        with col3:
            # Count heroes by tier
            tier_counts = {}
            for uh in user_heroes:
                hero_data = next((h for h in HERO_DATA['heroes'] if h['name'] == uh.hero.name), None)
                if hero_data:
                    tier = hero_data.get('tier_overall', '?')
                    tier_counts[tier] = tier_counts.get(tier, 0) + 1

            top_tier_count = tier_counts.get('S+', 0) + tier_counts.get('S', 0)
            st.markdown("""
            <div style="background: rgba(255, 215, 0, 0.2); padding: 20px; border-radius: 12px;">
                <div style="font-size: 14px; color: #B8D4E8;">S+/S Tier Heroes</div>
                <div style="font-size: 32px; font-weight: bold; color: #FFD700;">{}</div>
            </div>
            """.format(top_tier_count), unsafe_allow_html=True)

        st.markdown("---")

        # Class distribution
        st.markdown("### Hero Class Distribution")

        class_counts = {"Infantry": 0, "Marksman": 0, "Lancer": 0}
        for uh in user_heroes:
            hero_data = next((h for h in HERO_DATA['heroes'] if h['name'] == uh.hero.name), None)
            if hero_data:
                hero_class = hero_data.get('hero_class', 'Unknown')
                if hero_class in class_counts:
                    class_counts[hero_class] += 1

        cols = st.columns(3)
        for i, (class_name, count) in enumerate(class_counts.items()):
            with cols[i]:
                color = get_class_color(class_name)
                st.markdown(f"""
                <div style="
                    background: rgba(46, 90, 140, 0.3);
                    border-left: 4px solid {color};
                    padding: 16px;
                    border-radius: 8px;
                ">
                    <div style="font-size: 14px; color: #B8D4E8;">{class_name}</div>
                    <div style="font-size: 28px; font-weight: bold; color: {color};">{count}</div>
                </div>
                """, unsafe_allow_html=True)

        # Tier distribution
        st.markdown("### Hero Tier Distribution")

        tier_order = ['S+', 'S', 'A', 'B', 'C', 'D']
        cols = st.columns(len(tier_order))
        for i, tier in enumerate(tier_order):
            with cols[i]:
                count = tier_counts.get(tier, 0)
                color = get_tier_color(tier)
                st.markdown(f"""
                <div style="
                    background: {color}33;
                    border: 2px solid {color};
                    padding: 12px;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <div style="font-weight: bold; color: {color};">{tier}</div>
                    <div style="font-size: 24px; color: #E8F4F8;">{count}</div>
                </div>
                """, unsafe_allow_html=True)

# Close database
db.close()
