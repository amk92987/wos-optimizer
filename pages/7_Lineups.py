"""
Lineups Page - Best hero lineups and troop compositions for different events.
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
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database and get user profile
init_db()
db = get_db()
profile = get_or_create_profile(db)

# Load hero data for reference
heroes_file = PROJECT_ROOT / "data" / "heroes.json"
with open(heroes_file, encoding='utf-8') as f:
    HERO_DATA = json.load(f)

HEROES_BY_NAME = {h["name"]: h for h in HERO_DATA.get("heroes", [])}


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
        return 8 + ((server_age_days - 520) // 80)


def hero_available(hero_name: str, max_gen: int) -> bool:
    """Check if a hero is available based on current generation."""
    hero = HEROES_BY_NAME.get(hero_name)
    if not hero:
        return False
    return hero.get("generation", 1) <= max_gen


def get_available_hero(preferred: str, fallback: str, hero_class: str, max_gen: int) -> str:
    """Get the best available hero, falling back if preferred isn't unlocked."""
    if hero_available(preferred, max_gen):
        return preferred
    if hero_available(fallback, max_gen):
        return fallback
    # Find any available hero of this class
    for hero in HERO_DATA.get("heroes", []):
        if hero.get("hero_class") == hero_class and hero.get("generation", 1) <= max_gen:
            return hero["name"]
    return preferred  # Return preferred anyway as placeholder


# Get user's current generation
USER_GEN = get_current_generation(profile.server_age_days)


def get_class_symbol(hero_class: str) -> str:
    """Get symbol for class."""
    symbols = {
        "Infantry": "🛡️",
        "Marksman": "🏹",
        "Lancer": "⚔️"
    }
    return symbols.get(hero_class, "?")


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


def render_hero_slot(hero_name: str, hero_class: str, role: str = "", is_lead: bool = False):
    """Render a single hero slot in the lineup."""
    hero = HEROES_BY_NAME.get(hero_name, {})

    if hero:
        tier = hero.get("tier_overall", "?")
        tier_color = get_tier_color(tier)
        generation = hero.get("generation", 1)
        actual_class = hero.get("hero_class", hero_class)
    else:
        tier = "?"
        tier_color = "#808080"
        generation = "?"
        actual_class = hero_class

    class_symbol = get_class_symbol(actual_class)

    # Position styling
    if is_lead:
        pos_label = "👑 LEAD"
        pos_color = "#FFD700"
    else:
        pos_label = actual_class
        pos_color = "#B8D4E8"

    role_text = f" - {role}" if role else ""

    st.markdown(f"""
    <div style="background:rgba(46,90,140,0.3);border-radius:8px;padding:10px;margin:4px 0;display:flex;align-items:center;gap:12px;">
        <div style="font-size:24px;">{class_symbol}</div>
        <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <span style="color:{pos_color};font-weight:bold;font-size:12px;">{pos_label}</span>
                <span style="background:{tier_color};color:white;padding:1px 6px;border-radius:3px;font-size:11px;">{tier}</span>
                <span style="color:#E8F4F8;font-weight:bold;">{hero_name}</span>
                <span style="color:#808080;font-size:11px;">Gen {generation}</span>
            </div>
            <div style="color:#B8D4E8;font-size:12px;">{role_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_troop_ratio(infantry: int, lancer: int, marksman: int, note: str = ""):
    """Render troop ratio display."""
    st.markdown(f"""
    <div style="background:rgba(255,107,53,0.2);border:1px solid #FF6B35;border-radius:8px;padding:12px;margin:8px 0;">
        <div style="font-weight:bold;color:#FF6B35;margin-bottom:8px;">⚔️ Troop Ratio</div>
        <div style="display:flex;gap:20px;flex-wrap:wrap;">
            <div><span style="color:#E74C3C;font-weight:bold;">{infantry}%</span> Infantry</div>
            <div><span style="color:#2ECC71;font-weight:bold;">{lancer}%</span> Lancer</div>
            <div><span style="color:#3498DB;font-weight:bold;">{marksman}%</span> Marksman</div>
        </div>
        {f'<div style="color:#B8D4E8;font-size:12px;margin-top:8px;">{note}</div>' if note else ''}
    </div>
    """, unsafe_allow_html=True)


def render_3hero_lineup(infantry: dict, lancer: dict, marksman: dict, title: str = "", description: str = ""):
    """Render a standard 3-hero world march lineup."""
    if title:
        st.markdown(f"**{title}**")
    if description:
        st.markdown(f"*{description}*")

    render_hero_slot(infantry["name"], "Infantry", infantry.get("role", ""), infantry.get("lead", False))
    render_hero_slot(lancer["name"], "Lancer", lancer.get("role", ""), lancer.get("lead", False))
    render_hero_slot(marksman["name"], "Marksman", marksman.get("role", ""), marksman.get("lead", False))


def render_5hero_lineup(heroes: list, title: str = "", description: str = ""):
    """Render a 5-hero Arena/Championship lineup."""
    if title:
        st.markdown(f"**{title}**")
    if description:
        st.markdown(f"*{description}*")

    for i, hero in enumerate(heroes):
        is_lead = (i == 0) or hero.get("lead", False)
        hero_class = hero.get("class", "Unknown")
        render_hero_slot(hero["name"], hero_class, hero.get("role", ""), is_lead)


# Page content
st.markdown("# ⚔️ Best Lineups & Compositions")
st.markdown("Optimal hero and troop setups for every game mode")

st.markdown("---")

# Critical game mechanics
st.info("""
**📌 Rally Skill Mechanics**

**Rally Joiner:** Only your **leftmost hero's expedition skill** contributes to the rally!
- Up to **4 member skills** contribute total and can stack
- This is why specific "joiner heroes" matter (Jessie, Sergey)
- Your other 2 heroes and their skills DON'T contribute when joining
""")

st.markdown("---")

# Event selector
st.markdown("## Select Game Mode")

event_categories = {
    "PvP / SvS": ["World March (Default)", "SvS Castle Attack", "SvS Castle Defense", "SvS Field Battle"],
    "Rallies": ["Bear Trap Rally", "Crazy Joe Rally", "Rally Joiner Setup"],
    "Competitive": ["Arena (5 Heroes)", "Alliance Championship"],
    "PvE": ["Exploration / Frozen Stages", "Gathering"],
    "Alliance Events": ["Polar Terror", "Reservoir Raid"]
}

category = st.selectbox("Category:", list(event_categories.keys()))
event_type = st.selectbox("Game Mode:", event_categories[category])

st.markdown("---")

# =============================================================================
# WORLD MARCH (DEFAULT)
# =============================================================================
if event_type == "World March (Default)":
    st.markdown("## 🗡️ Default World March")
    st.markdown("Standard 3-hero composition for attacks, rally joins, and general PvP")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Main March (Recommended)")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Primary tank, sustain", "lead": True},
            lancer={"name": "Molly", "role": "DPS + healing support"},
            marksman={"name": "Alonso", "role": "Main damage dealer"}
        )
        render_troop_ratio(50, 20, 30, "Balanced default - community consensus")

        with st.expander("📝 Strategy Notes"):
            st.markdown("""
            - **Natalia lead** provides tankiness and sustain
            - This lineup works for most content
            - Alonso scales well in longer fights
            - Adjust troop ratio based on enemy composition
            """)

    with col2:
        st.markdown("### Alternative Compositions")

        st.markdown("**Burst Damage Focus:**")
        render_3hero_lineup(
            infantry={"name": "Jeronimo", "role": "ATK multiplier", "lead": True},
            lancer={"name": "Molly", "role": "DPS"},
            marksman={"name": "Alonso", "role": "Burst damage"}
        )
        st.caption("Use when you need fast kills, not sustain")

        st.markdown("**Marksman Heavy:**")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Tank", "lead": True},
            lancer={"name": "Zinman", "role": "Lancer support"},
            marksman={"name": "Philly", "role": "Ranged focus"}
        )
        st.caption("Good against slower infantry comps")

# =============================================================================
# SvS CASTLE ATTACK
# =============================================================================
elif event_type == "SvS Castle Attack":
    st.markdown("## 🏰 SvS Castle Attack")
    st.markdown("Rally or march composition for taking enemy castles")

    st.warning("Castle attacks are **attrition fights**. The side whose infantry survives longest usually wins.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Rally Leader")
        st.markdown("*When YOU are leading the castle rally*")
        render_3hero_lineup(
            infantry={"name": "Jeronimo", "role": "ATK boost to entire rally", "lead": True},
            lancer={"name": "Molly", "role": "Healing + damage"},
            marksman={"name": "Alonso", "role": "Main DPS"}
        )
        render_troop_ratio(50, 20, 30, "Standard attack ratio")

        with st.expander("📝 When to use Jeronimo vs Natalia lead"):
            st.markdown("""
            **Use Jeronimo lead when:**
            - Your rally is well-coordinated
            - Infantry gear is strong enough to survive
            - You need maximum damage output

            **Use Natalia lead when:**
            - Infantry dies too quickly
            - Enemy garrison is very strong
            - You need sustained pressure over burst
            """)

    with col2:
        st.markdown("### Rally Joiner")
        st.markdown("*When joining someone else's rally*")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Survivability", "lead": True},
            lancer={"name": "Molly", "role": "Support"},
            marksman={"name": "Alonso", "role": "Damage"}
        )
        render_troop_ratio(60, 15, 25, "Tankier - keep troops alive")

        st.markdown("---")
        st.markdown("**Best Joiners (Expedition Skills):**")
        st.markdown("""
        - **Jessie** - ATK buffs for the rally
        - Use your strongest geared heroes
        - Dead troops = zero contribution
        """)

# =============================================================================
# SvS CASTLE DEFENSE
# =============================================================================
elif event_type == "SvS Castle Defense":
    st.markdown("## 🛡️ SvS Castle Defense (Garrison)")
    st.markdown("Defending YOUR castle from enemy rallies")

    st.warning("Defense is about **surviving the rally timer**. Healing and tankiness > burst damage.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Garrison Leader")
        st.markdown("*If you are the garrison leader*")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Maximum survivability", "lead": True},
            lancer={"name": "Molly", "role": "Healing defenders"},
            marksman={"name": "Alonso", "role": "Counter damage"}
        )
        render_troop_ratio(60, 15, 25, "Heavy infantry for defense")

    with col2:
        st.markdown("### Garrison Joiner")
        st.markdown("*Reinforcing alliance garrison*")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Tank"},
            lancer={"name": "Molly", "role": "Healing"},
            marksman={"name": "Alonso", "role": "Support"}
        )
        render_troop_ratio(60, 20, 20, "Match garrison leader's strategy")

        st.markdown("---")
        st.markdown("**Best Garrison Joiners:**")
        st.markdown("""
        - **Sergey** - Expedition skills reduce damage taken
        - **Bahiti** - Sustain support
        - Prioritize heroes with defensive expedition skills
        """)

# =============================================================================
# SvS FIELD BATTLE
# =============================================================================
elif event_type == "SvS Field Battle":
    st.markdown("## ⚔️ SvS Field Battle")
    st.markdown("Open field PvP during State vs State events")

    st.warning("Field fights are **fast and chaotic**. Burst damage and positioning matter more than sustained fights.")

    tab1, tab2, tab3 = st.tabs(["Infantry Rush", "Marksman Kite", "Balanced/Safe"])

    with tab1:
        st.markdown("### Infantry Rush")
        st.markdown("*All-in Infantry damage for quick kills*")
        render_3hero_lineup(
            infantry={"name": "Jeronimo", "role": "Infantry ATK steroid", "lead": True},
            lancer={"name": "Molly", "role": "Burst support"},
            marksman={"name": "Alonso", "role": "Follow-up damage"}
        )
        render_troop_ratio(60, 15, 25, "Heavy infantry for rush")

        st.markdown("""
        **When to use:**
        - Enemy has weak frontline
        - You need fast eliminations
        - Coordinated alliance pushes
        """)

    with tab2:
        st.markdown("### Marksman Kite")
        st.markdown("*Ranged damage composition*")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Tank while kiting", "lead": True},
            lancer={"name": "Zinman", "role": "Lancer support"},
            marksman={"name": "Philly", "role": "Ranged burst"}
        )
        render_troop_ratio(40, 15, 45, "Heavy marksman for range")

        st.markdown("""
        **When to use:**
        - Against slower Infantry comps
        - When you can maintain distance
        - Hit-and-run tactics
        """)

    with tab3:
        st.markdown("### Balanced / Safe")
        st.markdown("*Well-rounded for unknown matchups*")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Tank", "lead": True},
            lancer={"name": "Molly", "role": "Healing"},
            marksman={"name": "Alonso", "role": "Damage"}
        )
        render_troop_ratio(50, 20, 30, "Standard balanced ratio")

        st.markdown("""
        **When to use:**
        - Unknown enemy composition
        - General field presence
        - Not optimal but rarely hard-countered
        """)

# =============================================================================
# BEAR TRAP RALLY
# =============================================================================
elif event_type == "Bear Trap Rally":
    st.markdown("## 🐻 Bear Trap Rally")
    st.markdown("Alliance rally against Bear Trap boss")

    st.caption(f"*Showing heroes for your server: Generation {USER_GEN}*")

    st.info("""
    **📌 Rally Joiner Mechanics**

    Only the **top 4 highest level** expedition skills from joiners apply to the rally.

    This is based on **skill level**, not player power. A level 5 Sergey skill would bump out a level 3 Jessie
    skill - even though Jessie's +25% damage is far more valuable for attacks.
    """)

    tab_rally, tab_joins = st.tabs(["Rally Squad (Leader)", "Joining Strategy"])

    with tab_rally:
        st.markdown("### Rally Leader Setup")
        st.markdown("*When YOU are leading the rally - all 3 of your heroes' expedition skills apply*")

        # Use generation-appropriate heroes
        infantry_hero = get_available_hero("Jeronimo", "Natalia", "Infantry", USER_GEN)
        lancer_hero = get_available_hero("Molly", "Zinman", "Lancer", USER_GEN)
        marksman_hero = get_available_hero("Alonso", "Philly", "Marksman", USER_GEN)

        render_3hero_lineup(
            infantry={"name": infantry_hero, "role": "ATK boost to rally", "lead": True},
            lancer={"name": lancer_hero, "role": "Healing support"},
            marksman={"name": marksman_hero, "role": "Main damage dealer"}
        )
        render_troop_ratio(20, 20, 60, "Heavy Marksman for maximum damage")

        with st.expander("📝 Rally Leader Strategy"):
            st.markdown("""
            **Why Jeronimo lead is crucial:**
            - His expedition skill provides massive Infantry ATK boost
            - This buff applies to the ENTIRE rally, not just your troops

            **When to use Natalia lead instead:**
            - If infantry melts before fight ends
            - Early game / undergeared rallies
            - Survival > damage scenarios

            **Troop ratio explanation:**
            - 20% Infantry = just enough to survive
            - 60% Marksman = maximum damage output
            - This is aggressive - adjust if troops die too fast
            """)

    with tab_joins:
        st.markdown("### Joining Strategy")

        st.warning("""
        **⚠️ IMPORTANT: Should you use heroes when joining?**

        Only the **top 4 highest level** expedition skills apply. If your hero has a high-level skill that's
        not useful for attacks (like Sergey's defensive skill), it could bump out someone's lower-level
        Jessie - which has a much better damage multiplier.
        """)

        # Show valuable joiner heroes that are available
        st.markdown("### Heroes Worth Using as Joiner")
        st.markdown("*Only use these heroes in your leftmost slot - they have valuable rally expedition skills:*")

        valuable_joiners = [
            ("Jeronimo", "Infantry", "Infantry ATK multiplier", 1),
            ("Jessie", "Marksman", "+25% DMG dealt (all troops)", 1),
            ("Jasser", "Marksman", "Rally damage buff", 1),
            ("Seo-yoon", "Marksman", "Rally damage buff", 1),
        ]

        available_joiners = []
        for name, hero_class, skill, gen in valuable_joiners:
            if gen <= USER_GEN:
                available_joiners.append((name, hero_class, skill))
                render_hero_slot(name, hero_class, skill, False)

        if not available_joiners:
            st.markdown("*No valuable joiner heroes available at Gen 1 - join with troops only*")

        st.markdown("---")

        st.markdown("### If You DON'T Have These Heroes")
        st.success("""
        **Join with TROOPS ONLY (no heroes)**

        - Send your troops to contribute damage
        - Don't put any heroes in the march
        - This prevents your leveled-up but wrong skill (like Sergey) from bumping out a valuable damage multiplier
        - Your troops still contribute to the rally damage!
        """)

        st.markdown("---")
        st.markdown("### Troop Recommendations")
        render_troop_ratio(20, 20, 60, "Match the rally leader's marksman-heavy strategy")

# =============================================================================
# CRAZY JOE RALLY
# =============================================================================
elif event_type == "Crazy Joe Rally":
    st.markdown("## 🤪 Crazy Joe Rally")
    st.markdown("Alliance rally against Crazy Joe boss - heavy AoE damage")

    st.warning("Crazy Joe deals **massive AoE damage**. Healing and sustain are MORE important than Bear Trap!")

    tab_rally, tab_joins = st.tabs(["Rally Squad (Leader)", "Your 6 Joining Marches"])

    with tab_rally:
        st.markdown("### Rally Squad")
        st.markdown("*Healing focus - Joe's AoE requires sustained survival*")

        render_3hero_lineup(
            infantry={"name": "Jeronimo", "role": "ATK multiplier", "lead": True},
            lancer={"name": "Molly", "role": "CRITICAL - Team healing"},
            marksman={"name": "Alonso", "role": "Sustained DPS"}
        )
        render_troop_ratio(90, 10, 0, "Infantry-heavy - infantry kills before others engage")

        st.markdown("""
        **Joe-specific mechanics:**
        - Infantry engages FIRST in combat order
        - If infantry stats are high enough, they defeat all bandits before Lancers/Marksmen attack
        - This is why 90/10/0 works - back row never gets to fight
        - Molly's healing still valuable for survival
        """)

    with tab_joins:
        st.markdown("### Your 6 Joining Marches")
        st.markdown("*Survival matters even more for joiners against Joe*")

        st.markdown("Same 90/10/0 infantry-heavy approach:")
        st.markdown("""
        - Infantry engages and kills before other troops attack
        - Send Infantry when reinforcing cities for max kill participation
        - Heroes with healing/sustain still valuable for survival
        """)
        render_troop_ratio(90, 10, 0, "Match the infantry-heavy strategy")

# =============================================================================
# RALLY JOINER SETUP
# =============================================================================
elif event_type == "Rally Joiner Setup":
    st.markdown("## 🤝 Rally Joiner Best Practices")
    st.markdown("Optimizing your contribution when joining someone else's rally")

    st.info("""
    **⚠️ CRITICAL JOINER MECHANIC**

    When joining a rally, only your **leftmost hero's expedition skill** is used!
    - Your other 2 heroes contribute NOTHING to rally buffs
    - Up to **4 member skills** total contribute to a rally
    - Member skills CAN stack if they're the same effect
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Best Joiner Heroes")

        st.markdown("**🔥 Attack/Rally Joiners:**")
        st.markdown("""
        Heroes whose **expedition skill** buffs damage:
        """)
        render_hero_slot("Jessie", "Marksman", "Stand of Arms: +25% DMG dealt (all troops)", False)
        st.caption("Best attack joiner - affects ALL damage types including skills, pets, teammates")

        st.markdown("**🛡️ Garrison Joiners:**")
        st.markdown("""
        Heroes whose **expedition skill** reduces damage:
        """)
        render_hero_slot("Sergey", "Infantry", "Defenders' Edge: -20% DMG taken (all troops)", False)
        st.caption("Best garrison joiner - universal damage reduction")

    with col2:
        st.markdown("### Joiner Priorities")

        st.info("""
        **Key Understanding:**

        Only ONE skill per joiner matters (leftmost hero's expedition skill).

        What matters most:
        1. **Leftmost hero selection** - choose for their expedition skill
        2. **Troop survival** - dead troops = zero contribution
        3. **Troop tier** - T9/T10 significantly outperform lower tiers
        """)

        st.markdown("### Joiner Investment Priority")
        st.markdown("""
        Joiner heroes (Jessie, Sergey, etc.) should:
        - ✅ Have functional gear (legendary is fine)
        - ✅ Be leveled appropriately
        - ❌ NOT get premium resources (Stones, Mithril)
        - ❌ NOT be prioritized over main heroes

        They are **support**, not core investments.
        """)

# =============================================================================
# ARENA (5 HEROES)
# =============================================================================
elif event_type == "Arena (5 Heroes)":
    st.markdown("## 🏟️ Arena (5-Hero Lineup)")
    st.markdown("1v1 PvP arena battles - this is the ONLY common mode with 5 heroes")

    st.info("Arena is **asynchronous** - you fight AI-controlled enemy teams. Frontline survival wins.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Arena Offense")
        st.markdown("*Attacking enemy defense teams*")

        render_5hero_lineup([
            {"name": "Natalia", "class": "Infantry", "role": "Primary tank", "lead": True},
            {"name": "Flint", "class": "Infantry", "role": "Secondary tank / time buyer"},
            {"name": "Alonso", "class": "Marksman", "role": "Main DPS"},
            {"name": "Molly", "class": "Lancer", "role": "Healing + damage"},
            {"name": "Philly", "class": "Marksman", "role": "Ranged burst"},
        ])

        st.markdown("""
        **Why 2 Infantry frontline:**
        - Arena rewards frontline durability
        - Flint buys time for Alonso to ramp up
        - Natalia + Flint = strongest Gen2 frontline
        """)

    with col2:
        st.markdown("### Arena Defense")
        st.markdown("*Team others will fight (AI controlled)*")

        render_5hero_lineup([
            {"name": "Natalia", "class": "Infantry", "role": "Hard to kill", "lead": True},
            {"name": "Flint", "class": "Infantry", "role": "Absorb burst"},
            {"name": "Molly", "class": "Lancer", "role": "Healing frustrates attackers"},
            {"name": "Alonso", "class": "Marksman", "role": "Counter threat"},
            {"name": "Bahiti", "class": "Lancer", "role": "Sustain"},
        ])

        st.markdown("""
        **Defense philosophy:**
        - AI controls your team
        - Tankiness + healing = long fights
        - Goal: timeout or discourage attacks
        """)

    st.markdown("---")
    st.markdown("### Arena Investment Note")
    st.warning("""
    **Flint is NOT optional for Arena.**

    Many guides undervalue Flint, but at competitive levels:
    - Flint's survivability and control scale extremely well
    - He is a **mode specialist**, not "extra infantry"
    - If you're serious about Arena, invest in Flint
    """)

# =============================================================================
# ALLIANCE CHAMPIONSHIP
# =============================================================================
elif event_type == "Alliance Championship":
    st.markdown("## 🏆 Alliance Championship")
    st.markdown("Alliance vs Alliance tournament - multiple rounds with hero restrictions")

    st.error("""
    **Heroes can only be used ONCE per Championship!**

    You need **multiple developed teams** to compete effectively.
    Plan your lineup usage across all battles.
    """)

    tab1, tab2, tab3 = st.tabs(["Team 1 (Strongest)", "Team 2 (Secondary)", "Team 3+ (Depth)"])

    with tab1:
        st.markdown("### Team 1 - Main Squad")
        st.markdown("*Use your absolute best heroes first*")

        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Best tank", "lead": True},
            lancer={"name": "Molly", "role": "Best lancer"},
            marksman={"name": "Alonso", "role": "Best damage"}
        )

        st.markdown("""
        **Philosophy:**
        - Don't save best heroes for "later"
        - Win early rounds to build momentum
        - Team 1 should be your most invested heroes
        """)

    with tab2:
        st.markdown("### Team 2 - Secondary")
        st.markdown("*Second-best lineup after main heroes used*")

        render_3hero_lineup(
            infantry={"name": "Flint", "role": "Secondary infantry", "lead": True},
            lancer={"name": "Zinman", "role": "Lancer damage"},
            marksman={"name": "Philly", "role": "Ranged support"}
        )

        st.markdown("""
        **Tips:**
        - Use different class focus than Team 1
        - Opponent may have countered your first strategy
        - Flint often anchors Team 2 effectively
        """)

    with tab3:
        st.markdown("### Team 3+ - Roster Depth")
        st.markdown("*Fill with remaining developed heroes*")

        render_3hero_lineup(
            infantry={"name": "Jeronimo", "role": "Infantry option"},
            lancer={"name": "Bahiti", "role": "Sustain"},
            marksman={"name": "Logan", "role": "Fill"}
        )

        st.info("""
        **Roster Depth Matters!**

        For full Championship participation, you need:
        - **9+ developed heroes** minimum (3 teams)
        - **15+ heroes** for competitive depth
        - Even "B-tier" heroes matter here

        This is why you shouldn't over-focus on just 3 heroes.
        """)

# =============================================================================
# EXPLORATION / PVE
# =============================================================================
elif event_type == "Exploration / Frozen Stages":
    st.markdown("## 🗺️ Exploration / Frozen Stages")
    st.markdown("PvE campaign content and frozen wasteland exploration")

    st.info("""
    **EXPLORATION Skills apply in PvE, not Expedition Skills!**

    Check your heroes' exploration skill descriptions - they're different from expedition (PvP) skills.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Standard PvE Clear")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Tank for hard stages", "lead": True},
            lancer={"name": "Molly", "role": "Healing sustain"},
            marksman={"name": "Alonso", "role": "Damage dealer"}
        )

        st.markdown("Works for most exploration content")

    with col2:
        st.markdown("### Hard Stage Push")
        render_3hero_lineup(
            infantry={"name": "Natalia", "role": "Survive waves", "lead": True},
            lancer={"name": "Bahiti", "role": "Secondary healing"},
            marksman={"name": "Alonso", "role": "Boss damage"}
        )

        st.markdown("""
        **For difficult stages:**
        - Double healer (Molly + Bahiti)
        - Prioritize survival over speed
        - Retreat and retry with better gear
        """)

# =============================================================================
# GATHERING
# =============================================================================
elif event_type == "Gathering":
    st.markdown("## 📦 Gathering")
    st.markdown("Resource gathering on the world map")

    st.info("**Exploration skills** matter here - some heroes have gathering speed/load bonuses!")

    render_3hero_lineup(
        infantry={"name": "Sergey", "role": "Gathering support"},
        lancer={"name": "Bahiti", "role": "Load capacity"},
        marksman={"name": "Jessie", "role": "Gathering speed bonus", "lead": True}
    )

    st.markdown("""
    **Gathering Tips:**
    - **Jessie's** exploration skill boosts gathering speed
    - Load capacity = more resources per trip
    - Gathering heroes are **low priority** for combat upgrades
    - Check hero exploration skills for gathering bonuses
    """)

# =============================================================================
# POLAR TERROR
# =============================================================================
elif event_type == "Polar Terror":
    st.markdown("## ❄️ Polar Terror")
    st.markdown("Alliance boss event - all alliance members attack the same boss")

    st.info("Your damage accumulates. Focus on dealing **maximum damage** before heroes die.")

    render_3hero_lineup(
        infantry={"name": "Jeronimo", "role": "ATK multiplier", "lead": True},
        lancer={"name": "Molly", "role": "Some sustain"},
        marksman={"name": "Alonso", "role": "Main damage"}
    )
    render_troop_ratio(25, 15, 60, "Heavy damage focus")

    st.markdown("""
    **Polar Terror Tips:**
    - Boss has very high DEF
    - DEF reduction heroes are valuable
    - Damage dealt = points for rewards
    - Multiple attempts allowed - experiment!
    """)

# =============================================================================
# RESERVOIR RAID
# =============================================================================
elif event_type == "Reservoir Raid":
    st.markdown("## 💧 Reservoir Raid")
    st.markdown("Timed challenge event - clear waves as fast as possible")

    st.warning("**Speed is everything.** AoE damage and fast wave clear wins.")

    render_3hero_lineup(
        infantry={"name": "Jeronimo", "role": "AoE damage", "lead": True},
        lancer={"name": "Molly", "role": "AoE support"},
        marksman={"name": "Philly", "role": "Ranged AoE"}
    )

    st.markdown("""
    **Speed Clear Tips:**
    - Every second matters for leaderboard
    - AoE > single target for wave content
    - Overkill doesn't matter - just kill fast
    - DEF reduction helps clear faster
    """)

# =============================================================================
# FOOTER - REFERENCE SECTIONS
# =============================================================================
st.markdown("---")

with st.expander("📊 Troop Ratio Quick Reference"):
    st.markdown("""
    | Situation | Infantry | Lancer | Marksman | Notes |
    |-----------|----------|--------|----------|-------|
    | **Default Formation** | 50% | 20% | 30% | Balanced default |
    | **Castle Battle** | 50% | 20% | 30% | Standard PvP |
    | **Labyrinth** | 60% | 15% | 25% | Tanky for PvE |
    | **Bear Hunt** | 0% | 10% | 90% | Maximum DPS |
    | **Crazy Joe** | 90% | 10% | 0% | Infantry kills first |
    | **Alliance Championship** | 45% | 25% | 35% | Balanced competitive |

    **Combat Order:** Infantry → Lancers → Marksmen
    **Class Counters:** Infantry > Lancer > Marksman > Infantry
    """)

with st.expander("🦸 Joiner Role Quick Reference"):
    st.markdown("""
    ### CRITICAL: Only leftmost hero's expedition skill matters!

    ### Best Attack/Rally Joiners
    | Hero | Expedition Skill | Effect |
    |------|------------------|--------|
    | **Jessie** | Stand of Arms | +25% DMG dealt (all troops) |

    Jessie's buff affects ALL damage types: normal attacks, hero skills, pet abilities, teammate buffs.

    ### Best Garrison Joiners
    | Hero | Expedition Skill | Effect |
    |------|------------------|--------|
    | **Sergey** | Defenders' Edge | -20% DMG taken (all troops) |

    ### Investment Rule
    Joiners should have:
    - ✅ Functional gear (legendary okay)
    - ✅ Appropriate levels
    - ❌ NOT premium resources (Stones/Mithril)
    - ❌ NOT priority over core heroes

    Only 1 skill per joiner contributes. Other heroes/skills don't matter.
    """)

with st.expander("💰 Spender-Specific Advice"):
    st.markdown("""
    ### Heavy Spender (Top 10-50 in state)
    - **Flint becomes core** for Arena & Championship
    - Full mythic on Natalia → Alonso → Flint → Molly → Jeronimo
    - Roster depth matters - develop 15+ heroes
    - SvS prep timing is crucial (save upgrades for scoring)

    ### Medium Spender
    - Focus on **Natalia + Alonso + Molly** first
    - Jeronimo for rallies only
    - Flint if Arena matters to you
    - 9-12 developed heroes is target

    ### Low Spender / F2P
    - **Natalia is everything** - max her first
    - One strong hero per class
    - Join rallies, don't lead them
    - Focus on ONE game mode strength

    ### Universal Rules
    1. Natalia is safe investment at any spend level
    2. Jeronimo is situational, not core
    3. Joiners (Jessie/Sergey) don't need premium resources
    4. Save Stone spending for SvS prep phases
    """)

with st.expander("⏰ S3 Transition Notes"):
    st.markdown("""
    ### What carries into S3?
    - **Natalia** - Remains top-tier tank
    - **Alonso** - Holds value better than most DPS
    - **Flint** - Still strong for Arena

    ### What gets power-crept?
    - **Jeronimo** - Most affected, becomes niche
    - **Pure DPS heroes** - Burst heroes lose relative value
    - Some S2 marksmen depending on S3 meta

    ### Investment Strategy
    - **Safe to max:** Natalia
    - **Finish strong, then pause:** Alonso, Flint
    - **Hold where they are:** Jeronimo, Molly
    - **Wait for S3:** New hero investments

    ### Timeline
    - S3 is typically ~4-6 weeks after S2 stabilizes
    - First SvS → Multiple SvS cycles → S3 signals
    - Don't panic-freeze, but don't over-invest
    """)

# Close database connection
db.close()
