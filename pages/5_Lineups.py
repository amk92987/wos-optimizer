"""
Lineups Page - Simplified hero lineups and troop compositions.
"""

import streamlit as st
from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_db, get_or_create_profile
from engine.analyzers.lineup_builder import LineupBuilder, LINEUP_TEMPLATES

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database and get user profile
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load hero data
heroes_file = PROJECT_ROOT / "data" / "heroes.json"
with open(heroes_file, encoding='utf-8') as f:
    HERO_DATA = json.load(f)

HEROES_BY_NAME = {h["name"]: h for h in HERO_DATA.get("heroes", [])}
HEROES_BY_GEN = {}
for h in HERO_DATA.get("heroes", []):
    gen = h.get("generation", 1)
    if gen not in HEROES_BY_GEN:
        HEROES_BY_GEN[gen] = []
    HEROES_BY_GEN[gen].append(h)


def get_current_generation(server_age_days: int) -> int:
    """Calculate current hero generation based on server age."""
    if server_age_days < 40:
        return 1
    elif server_age_days < 120:
        return 2
    elif server_age_days < 200:
        return 3
    elif server_age_days < 280:
        return 4
    elif server_age_days < 360:
        return 5
    elif server_age_days < 440:
        return 6
    elif server_age_days < 520:
        return 7
    else:
        return min(8 + ((server_age_days - 520) // 80), 14)


def get_user_heroes(db, profile_id: int) -> dict:
    """Get user's owned heroes with their stats."""
    from database.models import UserHero, Hero
    user_heroes = db.query(UserHero).filter(UserHero.profile_id == profile_id).all()
    heroes_dict = {}
    for uh in user_heroes:
        hero = db.query(Hero).filter(Hero.id == uh.hero_id).first()
        if hero:
            heroes_dict[hero.name] = {
                "level": uh.level or 1,
                "stars": uh.stars or 0,
                "gear_avg": (
                    (uh.gear_slot1_quality or 0) + (uh.gear_slot2_quality or 0) +
                    (uh.gear_slot3_quality or 0) + (uh.gear_slot4_quality or 0)
                ) / 4,
                "owned": True
            }
    return heroes_dict


def get_best_hero_by_class(user_heroes: dict, hero_class: str, prefer_sustain: bool = False) -> tuple:
    """Get user's best hero of a given class based on level and gear."""
    # Sustain heroes for defense
    sustain_heroes = {
        "Infantry": ["Natalia", "Logan", "Flint"],
        "Lancer": ["Philly", "Molly", "Norah"],
        "Marksman": ["Alonso", "Zinman", "Greg"]
    }

    candidates = []
    for hero_name, stats in user_heroes.items():
        hero_data = HEROES_BY_NAME.get(hero_name, {})
        if hero_data.get("hero_class") == hero_class:
            # Calculate a power score
            power = stats["level"] * 10 + stats["stars"] * 5 + stats["gear_avg"] * 3
            # Boost sustain heroes for defense
            if prefer_sustain and hero_name in sustain_heroes.get(hero_class, []):
                power *= 1.2
            candidates.append((hero_name, power, stats))

    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        best = candidates[0]
        return (best[0], f"Lv.{best[2]['level']}, {best[2]['stars']}★")
    return (None, None)


def get_class_icon(hero_class: str) -> str:
    """Get icon for class."""
    return {"Infantry": "🛡️", "Lancer": "⚔️", "Marksman": "🏹"}.get(hero_class, "?")


def render_hero_card(hero_name: str, note: str = "", is_critical: bool = False):
    """Render a hero card."""
    hero = HEROES_BY_NAME.get(hero_name, {})
    hero_class = hero.get("hero_class", "Unknown")
    gen = hero.get("generation", "?")
    tier = hero.get("tier_overall", "?")
    icon = get_class_icon(hero_class)

    border_color = "#FFD700" if is_critical else "#2E5A8C"
    bg_color = "rgba(255,215,0,0.1)" if is_critical else "rgba(46,90,140,0.3)"

    note_html = f'<span style="color:#2ECC71;font-size:11px;margin-left:8px;">✓ {note}</span>' if note else ""
    critical_badge = '<span style="background:#FFD700;color:black;padding:1px 6px;border-radius:3px;font-size:10px;margin-left:8px;">CRITICAL</span>' if is_critical else ""

    st.markdown(f'''
    <div style="background:{bg_color};border:1px solid {border_color};border-radius:8px;padding:12px;margin:6px 0;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:24px;">{icon}</span>
            <div>
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <span style="color:#E8F4F8;font-weight:bold;font-size:16px;">{hero_name}</span>
                    <span style="color:#808080;font-size:11px;">Gen {gen} • {tier}-tier • {hero_class}</span>
                    {note_html}{critical_badge}
                </div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_troop_ratio(infantry: int, lancer: int, marksman: int, note: str = ""):
    """Render troop ratio display."""
    st.markdown(f"""
    <div style="background:rgba(255,107,53,0.15);border:1px solid #FF6B35;border-radius:8px;padding:12px;margin:12px 0;">
        <div style="font-weight:bold;color:#FF6B35;margin-bottom:8px;">Troop Ratio</div>
        <div style="display:flex;gap:24px;flex-wrap:wrap;">
            <div><span style="color:#E74C3C;font-weight:bold;font-size:18px;">{infantry}%</span> Infantry</div>
            <div><span style="color:#2ECC71;font-weight:bold;font-size:18px;">{lancer}%</span> Lancer</div>
            <div><span style="color:#3498DB;font-weight:bold;font-size:18px;">{marksman}%</span> Marksman</div>
        </div>
        {f'<div style="color:#B8D4E8;font-size:12px;margin-top:8px;">{note}</div>' if note else ''}
    </div>
    """, unsafe_allow_html=True)


def get_generation_advice(current_gen: int) -> dict:
    """Get dynamic advice based on current generation."""
    next_gen = current_gen + 1 if current_gen < 14 else None

    # Key heroes that stay relevant
    evergreen_heroes = {
        "Infantry": ["Natalia"],  # Always good tank
        "Lancer": ["Molly"],      # Always good healer
        "Marksman": []            # Marksmen get replaced more often
    }

    # Notable heroes by generation
    notable_heroes = {
        2: {"highlight": "Flint", "reason": "Strong garrison defender, stays relevant for Arena"},
        3: {"highlight": "Logan", "reason": "Best defensive tank, essential for garrison"},
        4: {"highlight": "Ahmose", "reason": "Solid Infantry option"},
        5: {"highlight": "Hector", "reason": "F2P rally leader, replaces Flint for Bear Trap"},
        6: {"highlight": "Wu Ming", "reason": "Sustain Infantry, great for extended fights"},
        7: {"highlight": "Gordon", "reason": "Strong Lancer with poison abilities"},
        8: {"highlight": "Hendrik", "reason": "Top Marksman for rallies"},
        9: {"highlight": "Xura", "reason": "Excellent burst Marksman"},
        10: {"highlight": "Blanchette", "reason": "Best F2P Marksman damage dealer"},
        11: {"highlight": "Eleonora", "reason": "Strong Infantry option"},
        12: {"highlight": "Hervor", "reason": "Top-tier Infantry"},
        13: {"highlight": "Gisela", "reason": "Latest Infantry powerhouse"},
        14: {"highlight": "Elif", "reason": "Newest Infantry hero"},
    }

    advice = {
        "current_gen": current_gen,
        "next_gen": next_gen,
        "next_heroes": [],
        "save_for": None,
        "still_strong": ["Natalia", "Molly"],
    }

    if next_gen and next_gen in HEROES_BY_GEN:
        next_heroes = HEROES_BY_GEN[next_gen]
        legendary = [h for h in next_heroes if h.get("rarity") == "Legendary"]
        advice["next_heroes"] = legendary

        if next_gen in notable_heroes:
            advice["save_for"] = notable_heroes[next_gen]

    return advice


# Get user's current generation
USER_GEN = get_current_generation(profile.server_age_days)
USER_HEROES = get_user_heroes(db, profile.id)

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown("# ⚔️ Hero Lineups")

# Generation selector
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("Optimal hero and troop setups for every game mode")
with col2:
    selected_gen = st.selectbox("Your Generation:", options=list(range(1, 15)), index=min(USER_GEN - 1, 13))

# =============================================================================
# MAIN TABS
# =============================================================================
tab_rally_lead, tab_rally_join, tab_labyrinth, tab_exploration, tab_reference = st.tabs([
    "🏰 Rally Leader", "🤝 Rally Joiner", "🏛️ Labyrinth", "🗺️ Exploration", "📚 Reference"
])

# =============================================================================
# RALLY LEADER TAB
# =============================================================================
with tab_rally_lead:
    st.markdown("## Rally Leader Setup")
    st.markdown("When **you lead** a rally, all 3 of your heroes contribute their expedition skills.")

    st.info("""
    **The Simple Rule:** Use your **3 strongest heroes** - one Infantry, one Lancer, one Marksman.

    Hero slot position doesn't matter for rally leaders - all 3 contribute equally.
    """)

    # Attack vs Defense sub-tabs
    attack_tab, defense_tab = st.tabs(["⚔️ Attack (Rallies, Bear Trap, Crazy Joe)", "🛡️ Defense (Garrison)"])

    with attack_tab:
        st.markdown("### Attack Rally Leader")
        st.markdown("*For Bear Trap, Crazy Joe, Castle Attacks - prioritize damage output*")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Your Best Heroes:**")
            if USER_HEROES:
                for hero_class in ["Infantry", "Lancer", "Marksman"]:
                    best, note = get_best_hero_by_class(USER_HEROES, hero_class, prefer_sustain=False)
                    if best:
                        render_hero_card(best, note)
                    else:
                        st.warning(f"No {hero_class} hero found - add heroes in Hero Tracker!")
            else:
                st.warning("Add your heroes in the Hero Tracker page to see personalized recommendations.")
                st.markdown("**General recommendation:** Jeronimo (I) + Molly (L) + Alonso (M)")

        with col2:
            st.markdown("**Troop Ratios by Event:**")

            event_ratios = st.selectbox("Select event:",
                ["Bear Trap", "Crazy Joe", "Castle Attack", "General Rally"],
                key="attack_event")

            if event_ratios == "Bear Trap":
                render_troop_ratio(0, 10, 90, "Bear is slow - maximize Marksman DPS window")
            elif event_ratios == "Crazy Joe":
                render_troop_ratio(90, 10, 0, "Infantry kills before Joe's backline attacks hit")
            elif event_ratios == "Castle Attack":
                render_troop_ratio(50, 20, 30, "Balanced for sustained castle fights")
            else:
                render_troop_ratio(50, 20, 30, "Standard balanced ratio")

    with defense_tab:
        st.markdown("### Garrison Leader")
        st.markdown("*For defending your castle - prioritize sustain and damage reduction*")

        st.success("**Defense priorities:** Natalia/Logan/Flint (sustain Infantry), Philly/Molly (healing Lancer)")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Your Best Defensive Heroes:**")
            if USER_HEROES:
                for hero_class in ["Infantry", "Lancer", "Marksman"]:
                    best, note = get_best_hero_by_class(USER_HEROES, hero_class, prefer_sustain=True)
                    if best:
                        render_hero_card(best, note)
                    else:
                        st.warning(f"No {hero_class} hero found")
            else:
                st.warning("Add your heroes in the Hero Tracker page.")
                st.markdown("**General recommendation:** Natalia (I) + Philly (L) + Alonso (M)")

        with col2:
            st.markdown("**Why Sustain Matters:**")
            st.markdown("""
            - Garrison fights are **attrition battles**
            - The side whose Infantry survives longest wins
            - Healing and damage reduction > burst damage

            **Key Sustain Heroes:**
            - **Natalia** - Shields and self-healing
            - **Logan** - 25% troop health boost, damage reduction
            - **Flint** - +15% defender attack (with Dragonbane gear)
            - **Philly** - Team healing, garrison troop health boost
            """)

            render_troop_ratio(50, 30, 20, "Infantry-heavy for survival")

# =============================================================================
# RALLY JOINER TAB
# =============================================================================
with tab_rally_join:
    st.markdown("## Rally Joiner Setup")

    st.error("""
    **CRITICAL:** When joining a rally, **ONLY your leftmost hero's expedition skill matters!**

    Your 2nd and 3rd heroes contribute NOTHING except troop capacity. Choose slot 1 wisely.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚔️ Attack Joiner")
        st.markdown("*For Bear Trap, Crazy Joe, Castle Attacks*")

        render_hero_card("Jessie", "Stand of Arms: +25% DMG dealt at max level", is_critical=True)

        st.markdown("""
        **Why Jessie:**
        - Her expedition skill boosts ALL damage (attacks, skills, pets)
        - Affects the ENTIRE rally, not just your troops
        - Skill level matters more than her stats/gear

        **If you don't have Jessie:** Send troops WITHOUT heroes rather than using a hero with an unhelpful skill.
        """)

        render_troop_ratio(30, 20, 50, "Match rally leader's damage-focused composition")

    with col2:
        st.markdown("### 🛡️ Defense Joiner")
        st.markdown("*For garrison reinforcement*")

        render_hero_card("Sergey", "Defenders' Edge: -20% DMG taken at max level", is_critical=True)

        st.markdown("""
        **Why Sergey:**
        - His expedition skill reduces damage for ENTIRE garrison
        - Universal damage reduction (all sources)
        - Skill level matters more than his stats/gear

        **If you don't have Sergey:** Send troops WITHOUT heroes.
        """)

        render_troop_ratio(50, 30, 20, "Match garrison's defensive composition")

    st.markdown("---")
    st.markdown("### Joiner Investment Priority")
    st.markdown("""
    | Priority | What to Do |
    |----------|-----------|
    | ✅ HIGH | Level up Jessie/Sergey's **expedition skill** (right side) |
    | ✅ Medium | Get them to functional gear (Legendary is fine) |
    | ❌ LOW | Don't waste premium resources (Mithril, Stones) on joiners |

    **Only the skill level determines their contribution.** Their hero level, stars, and gear don't affect the rally buff.
    """)

# =============================================================================
# LABYRINTH TAB
# =============================================================================
with tab_labyrinth:
    st.markdown("## The Labyrinth")
    st.markdown("Weekly competitive PvP with 6 zones - each tests different parts of your account!")

    st.info("""
    **Key Mechanics:**
    - Most zones provide **Lv.10 troops** (your troop tier doesn't matter)
    - **Gaia Heart** (Sunday) uses YOUR actual troops
    - 5 daily attempts per zone
    """)

    # Zone overview table
    st.markdown("### Zone Summary")
    st.markdown("""
    | Zone | Days | Format | Stats That Matter | Floor 1-9 Ratio | Floor 10 Ratio |
    |------|------|--------|-------------------|-----------------|----------------|
    | **Land of the Brave** | Mon-Tue | 3v3 | Heroes, Hero Gear, Exclusive Gear | 50/20/30 | 40/15/45 |
    | **Cave of Monsters** | Wed-Thu | 2v2 | Pets, Pet Skills | 52/13/35 | 40/15/45 |
    | **Glowstone Mine** | Wed-Thu | 2v2 | Chief Charms (FC25+) | 52/13/35 | 40/15/45 |
    | **Earthlab** | Fri-Sat | 2v2 | Research, War Academy | 52/13/35 | 40/15/45 |
    | **Dark Forge** | Fri-Sat | 2v2 | Chief Gear (FC22+) | 52/13/35 | 40/15/45 |
    | **Gaia Heart** | Sunday | 3v3 | ALL stats + YOUR troops | 50/20/30 | 40/15/45 |
    """)

    st.markdown("""
    **Floor 10 Strategy:** AI switches from 33/33/33 to **53/27/20** (Infantry-heavy) on Floor 10.
    Counter with more Marksmen (40/15/45) to exploit their Infantry focus.
    """)

    # Detailed zone tabs
    with st.expander("📋 Detailed Zone Strategies"):
        zone_tabs = st.tabs(["Land of Brave", "Cave of Monsters", "Glowstone Mine", "Earthlab", "Dark Forge", "Gaia Heart"])

        with zone_tabs[0]:
            st.markdown("**Land of the Brave** (Mon-Tue)")
            st.markdown("Format: 3v3 with up to 9 heroes")
            st.success("Stats: Heroes, Hero Gear, Hero Exclusive Gear")
            st.markdown("Strategy: Focus on exclusive gear upgrades, pick heroes with AoE/CC")

        with zone_tabs[1]:
            st.markdown("**Cave of Monsters** (Wed-Thu)")
            st.markdown("Format: 2v2 squad battles")
            st.success("Stats: Pets, Pet Skills only")
            st.markdown("Strategy: Pair tank heroes with healing pets. Turn order is random.")

        with zone_tabs[2]:
            st.markdown("**Glowstone Mine** (Wed-Thu)")
            st.markdown("Format: 2v2 squad battles | Unlocks: FC25")
            st.success("Stats: Chief Charms only")
            st.markdown("Strategy: Balance offensive and defensive charms")

        with zone_tabs[3]:
            st.markdown("**Earthlab** (Fri-Sat)")
            st.markdown("Format: 2v2 squad battles")
            st.success("Stats: Research Center Tech, War Academy Tech")
            st.markdown("Strategy: Max your tech levels - long-term investment")

        with zone_tabs[4]:
            st.markdown("**Dark Forge** (Fri-Sat)")
            st.markdown("Format: 2v2 squad battles | Unlocks: FC22")
            st.success("Stats: Chief Gear only")
            st.markdown("Strategy: Balance all gear slots, don't neglect any piece")

        with zone_tabs[5]:
            st.markdown("**Gaia Heart** (Sunday)")
            st.markdown("Format: 3v3 with YOUR troops")
            st.warning("This is the ONLY zone where your troop tier matters!")
            st.success("Stats: ALL stats combined")
            st.markdown("Strategy: Use your best Fire Crystal/Helios troops")

# =============================================================================
# EXPLORATION TAB
# =============================================================================
with tab_exploration:
    st.markdown("## Exploration (5-Hero Lineup)")
    st.markdown("This is the **only common mode** that uses 5 heroes.")

    st.info("**EXPLORATION skills** (left side) apply in PvE, not Expedition skills!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Recommended Lineup")
        st.markdown("""
        | Slot | Class | Role |
        |------|-------|------|
        | 1 | Infantry | Primary Tank |
        | 2 | Infantry | Secondary Tank |
        | 3 | Lancer | Healer |
        | 4 | Marksman | Main DPS |
        | 5 | Marksman/Lancer | Support |
        """)

        st.markdown("**Why 2 Infantry:** Double frontline survives longer in multi-wave PvE content.")

    with col2:
        st.markdown("### Key Heroes for PvE")
        st.markdown("""
        - **Natalia** - Essential tank with self-sustain
        - **Flint** - Good secondary tank
        - **Molly** - Primary healer
        - **Alonso** - Strong sustained DPS

        **For difficult stages:** Use double healer (Molly + Philly)
        """)

        render_troop_ratio(40, 30, 30, "Balanced for multi-wave survival")

# =============================================================================
# REFERENCE TAB
# =============================================================================
with tab_reference:
    st.markdown("## Quick Reference")

    # Dynamic generation advice
    advice = get_generation_advice(selected_gen)

    st.markdown("### 📈 Generation Advice")
    st.markdown(f"**Your current generation:** Gen {selected_gen}")

    if advice["next_gen"]:
        st.markdown(f"**Next generation (Gen {advice['next_gen']}) brings:**")
        if advice["next_heroes"]:
            for hero in advice["next_heroes"]:
                st.markdown(f"- **{hero['name']}** ({hero['hero_class']}) - {hero.get('tier_overall', '?')}-tier")

        if advice["save_for"]:
            st.success(f"**Worth saving for:** {advice['save_for']['highlight']} - {advice['save_for']['reason']}")
    else:
        st.markdown("You're at the latest generation!")

    st.markdown(f"**Heroes that stay strong:** {', '.join(advice['still_strong'])}")

    # Troop ratio reference
    st.markdown("---")
    st.markdown("### 📊 Troop Ratio Quick Reference")
    st.markdown("""
    | Situation | Infantry | Lancer | Marksman | Notes |
    |-----------|----------|--------|----------|-------|
    | **Default / Balanced** | 50% | 20% | 30% | Safe for unknown matchups |
    | **Bear Trap** | 0% | 10% | 90% | Maximize ranged DPS |
    | **Crazy Joe** | 90% | 10% | 0% | Infantry kills before backline attacks |
    | **Garrison Defense** | 50% | 30% | 20% | Survival focus |
    | **Labyrinth 3v3** | 50% | 20% | 30% | Standard |
    | **Labyrinth 2v2** | 52% | 13% | 35% | Multi-round survival |
    | **Labyrinth Floor 10** | 40% | 15% | 45% | Counter Infantry-heavy AI |
    """)

    # Joiner mechanics
    st.markdown("---")
    st.markdown("### 🤝 Joiner Mechanics")
    st.markdown("""
    **When joining rallies/garrisons:**
    - Only **slot 1 hero's expedition skill** matters
    - Up to **4 joiner skills** can stack on a rally
    - Skills ranked by **level**, not player power

    | Role | Best Hero | Skill Effect |
    |------|-----------|--------------|
    | Attack Joiner | **Jessie** | +5/10/15/20/25% DMG dealt |
    | Defense Joiner | **Sergey** | -4/8/12/16/20% DMG taken |

    **No Jessie/Sergey?** Send troops WITHOUT heroes - wrong skills can hurt the rally!
    """)

    # Spending advice
    st.markdown("---")
    st.markdown("### 💰 Investment Priority by Spending Level")

    spend_tab1, spend_tab2, spend_tab3 = st.tabs(["F2P / Low Spender", "Medium Spender", "Heavy Spender"])

    with spend_tab1:
        st.markdown("""
        **Focus on 3-4 heroes maximum:**
        - **Natalia** - Your everything hero, max first
        - **Alonso** - Primary damage dealer
        - **Molly** - Essential healer
        - **Jessie** - Expedition skill only (minimal investment)

        **Strategy:** Join rallies, don't lead them. One strong lineup beats multiple weak ones.
        """)

    with spend_tab2:
        st.markdown("""
        **Develop 6-9 heroes:**
        - Core 3: Natalia, Alonso, Molly
        - Add: Flint (Arena), Jeronimo (rallies), Philly (healing)
        - Joiners: Jessie, Sergey (skill level only)

        **Strategy:** Can lead rallies occasionally. Build roster depth for Alliance Championship.
        """)

    with spend_tab3:
        st.markdown("""
        **Develop 12+ heroes:**
        - Full mythic gear on top 6
        - Flint becomes core for Arena
        - Roster depth for Championship
        - Latest gen heroes for competitive edge

        **Strategy:** Lead rallies, compete in all modes. Hero diversity wins Championships.
        """)

# Close database connection
db.close()
