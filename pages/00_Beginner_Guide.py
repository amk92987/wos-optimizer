"""
Beginner's Guide - Essential knowledge for new players.
"""

import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load CSS
css_file = PROJECT_ROOT / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.markdown("# Beginner's Guide")
st.markdown("*Everything you need to know for your first 30+ days in Whiteout Survival.*")
st.markdown("*Welcome, Chief. Stay warm out there.*")

st.markdown("---")

# =============================================================================
# STATIC TOP SECTION - Key Advice
# =============================================================================
st.markdown("## 💡 The Most Important Advice")
st.markdown("""
This game rewards **patience and planning**. The players who get ahead aren't the ones who spend
the most - they're the ones who spend **smart**. Save your resources for events, focus on heroes
over troops, and stay active in your alliance. Almost everything you do can earn extra rewards
if you do it during the right event.
""")

st.markdown("---")

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Getting Started",
    "Progression",
    "First 30 Days",
    "Resources",
    "Game Systems",
    "Tips & Checklist"
])

# =============================================================================
# TAB 1: GETTING STARTED
# =============================================================================
with tab1:
    st.markdown("## The Golden Rule")
    st.markdown("""
    **Save your resources for events.** Don't spend gems, speedups, or upgrade materials the moment
    you get them just to clear red notification dots. Almost everything you do in this game can earn
    you extra rewards if you do it during the right event. This one habit will put you weeks ahead
    of other players.
    """)

    st.markdown("---")

    st.markdown("## What Matters Most")

    st.markdown("### 1. Hero Power (Your #1 Priority)")
    st.markdown("""
    Heroes are the foundation of everything in this game. A strong hero lineup beats a large army every time.

    **Why heroes matter:**
    - Heroes multiply troop effectiveness - A max-skilled hero can make your troops 2-3x more effective
    - Heroes are permanent - Troops die, heroes don't
    - Heroes unlock content - Exploration stages, expedition battles, and events all require hero power
    - SvS is won by heroes - Hero skills and gear matter more than raw troop count

    **Early hero priorities:**
    - Focus on 5-6 heroes maximum (one main lineup)
    - Level them evenly rather than maxing one
    - Prioritize expedition skills over exploration skills for combat
    - Legendary heroes > Epic heroes for long-term investment
    """)

    st.markdown("### 2. Furnace Level (Your Progress Gate)")
    st.markdown("""
    Your Furnace level gates everything else. Each level unlocks new features, higher troop tiers,
    and better rewards. Rush your Furnace as your secondary priority after daily hero investments.
    """)

    st.markdown("### 3. Troops (Important but Replaceable)")
    st.markdown("""
    You need troops to fight, gather, and fill rallies. But troops die and need to be rebuilt.
    Don't over-invest in troops early - build what you need, focus the rest on heroes and Furnace.
    """)

# =============================================================================
# TAB 2: PROGRESSION
# =============================================================================
with tab2:
    st.markdown("## Furnace Level Milestones")

    st.markdown("""
    - **1-10 (Tutorial Phase)** - Basic buildings, T1-T3 troops, initial heroes. Just follow the guide.
    - **11-14 (Early Game)** - More building slots, T4 troops unlock, Alliance features. Join an active alliance ASAP.
    - **15 (Hero Gear Unlocks)** - You can now equip gear on heroes. Start collecting gear materials.
    - **16-18 (Mid Progression)** - T5 troops, more research. Events become more important.
    - **19 (Daybreak Island)** - Unlocks island for combat buffs. Don't rush this - focus on Furnace first.
    - **20-24 (Tier 6 Era)** - T6 troops unlock. You're now a real contributor in alliance battles.
    - **25 (Labyrinth & Glowstones)** - New resource system. Great source of mythic shards and gear.
    - **26-29 (Late Game Prep)** - T7-T8 troops. Focus heavily on hero gear and skills now.
    - **30 (FC Unlocks!)** - Fire Crystal system begins. This is the real endgame. T9 troops available.
    - **FC1-FC10 (Fire Crystal Era)** - New upgrade currency (Fire Crystals). Much slower progression but huge power gains.
    - **RFC1+ (Refined FC Era)** - Requires Refined Fire Crystals. You're now a veteran player.
    """)

    st.markdown("---")

    st.markdown("### How FC Building Upgrades Work")
    st.markdown("""
    Once you reach Furnace 30 (FC), building upgrades change from single upgrades to a **5-phase incremental system**:

    - Each FC level (FC1, FC2, etc.) has **5 upgrade phases** per building
    - You must complete all 5 phases to fully upgrade a building at that FC level
    - Each phase costs Fire Crystals instead of regular resources
    - Your Furnace must reach the next FC level before buildings can advance to their next FC tier
    - Example: To fully upgrade a building at FC3, you complete phases FC3-1, FC3-2, FC3-3, FC3-4, FC3-5
    """)

# =============================================================================
# TAB 3: FIRST 30 DAYS
# =============================================================================
with tab3:
    st.markdown("## Your First 30 Days")

    st.markdown("### Days 1-7: Foundation")
    st.markdown("""
    - Complete the tutorial and initial quests
    - **Join the best alliance that will accept you** - Top alliances kill stronger beasts, win more events, and their members will teach you
    - Focus on Furnace upgrades above all else
    - Collect your free heroes from events and exploration
    - Don't spend gems yet - save them
    """)

    st.markdown("### Days 8-14: Building Momentum")
    st.markdown("""
    - Keep pushing Furnace level (aim for F15+ by day 14)
    - Start leveling your best 5-6 heroes evenly
    - Participate in every event, even if you can't complete them
    - Learn which events are worth spending resources on
    - Build troops to meet alliance rally requirements
    """)

    st.markdown("### Days 15-21: Event Cycling")
    st.markdown("""
    - You'll start seeing event patterns repeat
    - Save speedups for construction/research events
    - Save hero materials for hero upgrade events
    - Join alliance rallies to earn rewards and learn mechanics
    - Start working on hero gear (unlocked at F15)
    """)

    st.markdown("### Days 22-30: Optimization")
    st.markdown("""
    - You should be approaching F20 if you've been efficient
    - Focus shifts more toward hero skills and gear
    - Learn SvS basics and prepare for your first one
    - Identify your main troop type (Infantry, Lancer, or Marksman)
    - Specialize your hero lineup around that troop type
    """)

# =============================================================================
# TAB 4: RESOURCES
# =============================================================================
with tab4:
    st.markdown("## Resource Management")

    st.markdown("### What to Save (Don't Spend Randomly)")
    st.markdown("""
    - **Gems** - Save for Lucky Wheel during hero events, VIP shop refreshes
    - **Speedups** - Save for construction/research events (2x+ rewards)
    - **Hero Shards** - Save for hero upgrade events
    - **Hero XP items** - Save for hero leveling events
    - **Skill Books** - Save for skill upgrade events
    """)

    st.markdown("### What to Spend Freely")
    st.markdown("""
    - **Basic resources** (meat, wood, coal, iron) - These accumulate fast, use them
    - **Stamina** - Use it daily or it's wasted (caps at a maximum)
    - **Alliance tokens** - Spend daily, they reset
    """)

    st.markdown("### Event Timing")
    st.markdown("""
    Most events run on predictable cycles:
    - **Hero events** - Usually every 1-2 weeks
    - **Construction events** - Very frequent, save your building speedups
    - **Power events** - Reward overall power gains, good time to do everything
    - **Spend events** - Sometimes spending gems/speedups gives bonus rewards

    When in doubt, wait. If an event is coming in 1-2 days, save your resources.
    """)

    st.markdown("---")

    st.markdown("## What to Prioritize Acquiring")

    st.markdown("### High Priority")
    st.markdown("""
    - **Legendary Hero Shards** - Any source. These are gold.
    - **Expedition Skill Books** (Mythic/Epic) - Combat power
    - **Hero Gear Materials** - For your main heroes
    - **VIP Points** - Permanent bonuses, very valuable long-term
    """)

    st.markdown("### Medium Priority")
    st.markdown("""
    - **Speedups** - Always useful, especially construction
    - **Fire Crystal Shards** - You'll need mountains of these later
    - **Chief Gear Materials** - Steady improvement over time
    - **Pet Materials** - Pets add up over time
    """)

    st.markdown("### Lower Priority")
    st.markdown("""
    - **Basic Resources** - You'll get plenty from gathering
    - **Exploration Skill Books** - Nice but not critical
    - **Random hero shards** - Focus on specific heroes instead
    - **Cosmetics** - Zero gameplay value
    """)

    st.markdown("### Where to Get Good Stuff")
    st.markdown("""
    - **Lucky Wheel** - Best source of legendary shards (save gems for hero events)
    - **Alliance Shop** - Teleports, some materials
    - **VIP Shop** - Skill books, shards (refresh with gems during events)
    - **Arena Shop** - Chief gear materials, stamina
    - **Events** - Best value for most items
    """)

# =============================================================================
# TAB 5: GAME SYSTEMS
# =============================================================================
with tab5:
    st.markdown("## Game Systems Explained")

    st.markdown("### Heroes")
    st.markdown("""
    Your most important asset. Heroes have:
    - **Level** (1-80) - Increases base stats
    - **Stars** (0-5) - Major power jumps, requires shards
    - **Skills** - Exploration (PvE) and Expedition (PvP/combat)
    - **Gear** - 4 slots per hero, huge stat boosts
    - **Exclusive Gear** - Special mythic gear for top-tier heroes

    Focus on Expedition skills for combat content (SvS, rallies). Exploration skills help with PvE stages.
    """)

    st.markdown("### Troops")
    st.markdown("""
    Three types with a rock-paper-scissors relationship:
    - **Infantry** (red) - Beats Lancer, loses to Marksman
    - **Lancer** (green) - Beats Marksman, loses to Infantry
    - **Marksman** (blue) - Beats Infantry, loses to Lancer

    Pick ONE main type and specialize. Most players choose based on their best heroes.
    """)

    st.markdown("### Chief Gear & Charms")
    st.markdown("""
    Equipment for your chief (separate from hero gear):
    - **Chief Gear** - 6 pieces (2 per troop type). Keep all at SAME TIER for 6-piece Attack set bonus. Infantry first when pushing to next tier.
    - **Chief Charms** - 6 charms, boost specific troop types. Focus on your main type.
    """)

    st.markdown("### Pets")
    st.markdown("""
    Unlocked later, pets provide passive bonuses and active abilities:
    - Level pets with Pet Food
    - Advance pets with Taming Manuals
    - Each pet specializes in different bonuses (combat, economy, etc.)
    """)

    st.markdown("### Daybreak Island (F19+)")
    st.markdown("""
    An island that provides combat buffs:
    - **Tree of Life** - Universal buffs for all troops
    - **Battle Decorations** - Troop-specific buffs (more impactful!)
    - Don't rush this over Furnace progression
    """)

    st.markdown("### Research")
    st.markdown("""
    Three trees: Economy, Combat, Hero.
    - Early game: Balance economy and combat
    - Mid game: Focus on troop stats in combat tree
    - Always research something - dead time is wasted time
    """)

# =============================================================================
# TAB 6: TIPS & CHECKLIST
# =============================================================================
with tab6:
    st.markdown("## Common Beginner Mistakes")

    st.markdown("""
    - **Spreading heroes too thin** - Focus on 5-6 heroes, not 15. A few strong heroes beat many weak ones.
    - **Ignoring events** - Events multiply your progress. Always check what's running before spending resources.
    - **Rushing troops over heroes** - Troops die. Heroes don't. Prioritize hero investment.
    - **Spending gems randomly** - Gems are premium currency. Save for Lucky Wheel and VIP shop refreshes.
    - **Neglecting alliance activities** - Alliance help, rallies, and donations give huge rewards. Participate daily.
    - **Upgrading the wrong skills** - Expedition skills matter for combat. Don't dump all books into exploration skills.
    - **Not joining rallies** - Even if you're weak, join rallies. You get rewards and learn mechanics.
    - **Clearing red dots immediately** - Those notification dots trick you into wasting resources outside events.
    - **Ignoring research** - Always have something researching. The time adds up significantly.
    - **Staying in a weak alliance out of loyalty** - Your alliance determines your growth speed. If your alliance is inactive, thank them and move up.
    """)

    st.markdown("---")

    st.markdown("## Daily Checklist")
    st.markdown("Do these every day for steady progress:")

    st.markdown("""
    1. **Collect free rewards** - Daily login, mail, event freebies
    2. **Use stamina** - Beast hunts or exploration (don't let it cap)
    3. **Alliance help** - Request and give help for free speedups
    4. **Donate to alliance tech** - Earns alliance tokens
    5. **Complete daily missions** - Easy rewards
    6. **Check events** - See what's running, plan your spending
    7. **Join rallies** - Even low participation helps
    8. **Keep buildings/research queued** - No idle time
    9. **Collect Daybreak Island essence** - If unlocked (caps at 12hrs)
    10. **Arena battles** - Use your attempts for tokens
        - *Tip: Do these as close to reset as possible for higher rankings - you'll face opponents who haven't played yet*
    """)
