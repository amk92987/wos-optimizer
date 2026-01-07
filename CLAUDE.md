# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Whiteout Survival Optimizer - A web-based tool to help players track their heroes, analyze backpack screenshots via OCR, and get personalized upgrade recommendations optimized for SvS and combat.

## Development Environment

- Python 3.13+
- Virtual environment: `.venv/`
- Framework: Streamlit
- Database: SQLite with SQLAlchemy ORM
- OCR: EasyOCR (optional, for screenshot parsing)

## Commands

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key for AI recommendations
set OPENAI_API_KEY=your-key-here  # Windows
export OPENAI_API_KEY=your-key-here  # Unix

# Run the application
streamlit run app.py

# Download hero images (optional)
python utils/image_downloader.py
```

## Architecture

### Directory Structure
```
WoS/
├── app.py                    # Main Streamlit entry point
├── database/
│   ├── models.py             # SQLAlchemy models (UserProfile, Hero, UserHero, etc.)
│   └── db.py                 # Database connection and session management
├── data/
│   └── heroes.json           # Static hero data (all generations, tiers, skills, gear)
├── assets/heroes/            # Hero portrait images
├── ocr/
│   └── screenshot_parser.py  # EasyOCR integration for backpack screenshots
├── engine/
│   ├── recommender.py        # Recommendation engine with priority-weighted scoring
│   └── ai_recommender.py     # OpenAI-powered AI advisor
├── pages/
│   ├── 1_Heroes.py           # Hero management with inline editing
│   ├── 2_Backpack.py         # Inventory tracking via OCR or manual entry
│   ├── 3_Recommendations.py  # Personalized upgrade recommendations
│   ├── 4_Settings.py         # User profile and priority configuration
│   └── 5_AI_Advisor.py       # AI-powered recommendations
├── styles/
│   └── custom.css            # Winter/frost theme styling
└── utils/
    └── image_downloader.py   # Script to fetch hero images from wiki
```

### Database Models (`database/models.py`)

**UserProfile**:
- Server age, furnace level, priority settings (SvS, Rally, etc.)
- SvS tracking (wins, losses, last date)

**Hero**:
- Static reference data (name, generation, class, tier ratings)
- Skills: exploration_skill_1/2, expedition_skill_1/2
- Image filename reference

**UserHero**:
- User's owned heroes with levels (1-80)
- Stars (0-5) and ascension tier (0-5, where 6 = next star)
- Skill levels (1-5 for each of 4 skills)
- Hero gear: 4 slots with quality (0-6) and level
- Mythic gear: unlocked status, quality, level

**UserInventory**:
- Backpack items and quantities

### Hero Card Features

Each hero card displays:
- **Tier badge** with hover tooltip explaining tier meaning (S+ through D)
- **Rarity border** color-coded (Blue=Rare, Purple=Epic, Gold=Legendary)
- **Class symbol** as default image (Shield/Bow/Swords)
- **Generation badge** for non-Gen 1 heroes
- **Star rating** with partial ascension progress (e.g., "3/5" toward next star)
- **Best use blurb** explaining optimal hero usage
- **Gear widgets** showing 4 gear slots with quality colors
- **Mythic gear** indicator for heroes with exclusive gear (e.g., Dawnbreak)

### Inline Hero Editor

Expand any hero card to edit:
- Level (1-80 slider)
- Stars (0-5 dropdown)
- Ascension (0-5 dropdown, disabled at 5 stars)
- Exploration skills 1 & 2 (1-5 sliders)
- Expedition skills 1 & 2 (1-5 sliders)
- 4 gear slots with quality (None/Gray/Green/Blue/Purple/Orange/Mythic) and level
- Mythic gear (if applicable): unlocked checkbox, quality, level

### Gear Quality System

Quality levels with max gear levels:
| Quality | Color | Max Level |
|---------|-------|-----------|
| None | Gray | 0 |
| Gray | #9E9E9E | 20 |
| Green | #4CAF50 | 40 |
| Blue | #2196F3 | 60 |
| Purple | #9C27B0 | 80 |
| Orange | #FF9800 | 100 |
| Mythic | #E91E63 | 120 |

### Star/Ascension System

- **Stars**: 0-5 (heroes start at 0 stars)
- **Ascension**: 0-5 tiers within each star level
- When ascension reaches 6, hero gains next star and ascension resets to 0
- At 5 stars, ascension is disabled (max reached)
- Display: `★★★✦☆ 3/5` shows 3 full stars + partial progress

### Hero Tiers

- **S+**: Meta-defining heroes, top priority for investment
- **S**: Excellent heroes, core team choices
- **A**: Strong heroes, reliable performers
- **B**: Good heroes, situationally useful
- **C**: Average heroes, early game viable
- **D**: Below average, not recommended for investment

### Hero Classes
- **Infantry**: Frontline tanks (Symbol: Shield) - Chief Gear: Coat, Pants
- **Marksman**: Ranged damage (Symbol: Bow) - Chief Gear: Belt, Shortstaff
- **Lancer**: Balanced fighters (Symbol: Swords) - Chief Gear: Hat, Watch

### Hero Skill System

Each hero has two types of skills, visible on separate sides of the skill screen:

**Exploration Skills (Left Side)**
- Upgraded with **Exploration Manuals**
- Used for PvE content (exploration, events)
- Levels 1-5, equal % increase per level

**Expedition Skills (Right Side)**
- Upgraded with **Expedition Manuals**
- Used for PvP content (rallies, garrison, SvS)
- Levels 1-5, equal % increase per level
- **Top-right skill** is specifically used when joining rallies

**Manual Costs**: Increasing amount of manuals required per level upgrade.

### Priority System

Users set priorities (1-5 scale) for:
- SvS / State vs State
- Rally Attacks (Bear Hunt, Crazy Joe)
- Castle Battles
- Exploration / PvE
- Resource Gathering

The recommendation engine weights upgrades based on these priorities.

### Rally Joiner Mechanics

**Critical mechanic**: When joining a rally, only the **leftmost hero's top-right expedition skill** is used.
- **Leftmost hero**: First hero in your march lineup (slot 1)
- **Top-right skill**: The expedition skill in top-right position on hero skill screen

**Skill level determines priority**: Only the top 4 highest LEVEL expedition skills from all joiners apply to the rally. This is based on skill level, not player power.

**Risk of wrong skills**: A high-level wrong skill (like Sergey's defensive skill at level 5) can bump out a lower-level valuable skill (like Jessie's damage skill at level 3).

**Best Attack Joiner Heroes** (for Bear Trap, Castle Attacks):
| Hero | Gen | Top-Right Skill | Effect per Level (1-5) |
|------|-----|-----------------|------------------------|
| Jessie | 5 | Stand of Arms | +5/10/15/20/25% DMG dealt |
| Jeronimo | 1 | Infantry ATK buff | Scales with level |

**Best Garrison Joiner Heroes** (for defense):
| Hero | Gen | Top-Right Skill | Effect per Level (1-5) |
|------|-----|-----------------|------------------------|
| Sergey | 1 | Defenders' Edge | -4/8/12/16/20% DMG taken |

**If you don't have the right joiner heroes**: Join with troops only (no heroes) to avoid bumping out someone else's valuable skill.

Heroes with `rally_joiner_role` field in heroes.json: "attack" or "garrison"

## Important Notes

### UTF-8 Encoding
All file operations with `heroes.json` must use `encoding='utf-8'` due to emoji characters (class symbols).

### Database Recreation
If database schema changes (new columns added), delete `wos.db` to force recreation:
```bash
del wos.db  # Windows
rm wos.db   # Unix
```

### Streamlit Running
```bash
# Windows (from project root)
.venv\Scripts\streamlit.exe run app.py

# Unix
streamlit run app.py
```

## Optimizer Decision System

The optimizer recommends upgrades based on player state, spending profile, and goals.

### Player Settings (`data/optimizer/player_settings_schema.json`)

**Required Inputs:**
- `furnace_level` (1-30) - Determines game phase and unlocked systems
- `furnace_fc_level` (optional) - FC progression like "FC3-0"
- `state_age_days` - Unlocks time-gated content (pets at 55 days)
- `spending_profile` - Affects efficiency thresholds and recommendations
- `priority_focus` - svs_combat, balanced_growth, or economy_focus
- `alliance_role` - rally_lead, filler, farmer, or casual

**Spending Profiles:**
| Profile | Monthly USD | Efficiency Threshold | Skip Whale Content |
|---------|-------------|---------------------|-------------------|
| f2p | $0 | 0.8 | Yes |
| minnow | $5-30 | 0.7 | Yes |
| dolphin | $30-100 | 0.5 | No |
| orca | $100-500 | 0.3 | No |
| whale | $500+ | 0.0 | No |

### Game Phases (`data/optimizer/progression_phases.json`)

| Phase | Furnace | Focus |
|-------|---------|-------|
| early_game | 1-18 | Rush to F19 for Daybreak, unlock Research |
| mid_game | 19-29 | Rush to F30 for FC, Tool Enhancement VII, Charms L11 |
| late_game | 30/FC1-FC4 | FC progression, War Academy, Hero Gear Mastery |
| endgame | FC5+ | FC10 completion, Mastery L20, Charms L12-16 |

### System Unlocks (`data/optimizer/system_unlocks.json`)

| Furnace | Systems Unlocked |
|---------|-----------------|
| 1 | buildings, troops, chief_gear |
| 9 | research |
| 18 | pets (also needs 55 days state age) |
| 19 | daybreak_island |
| 25 | chief_charms |
| 30 | buildings_fc, war_academy, hero_gear_mastery |

### Decision Rules (`data/optimizer/decision_rules.json`)

Priority weights by focus:
- **svs_combat**: Troops (1.0), War Academy (0.95), Hero Gear (0.85)
- **balanced_growth**: Buildings (0.9), Research (0.85), Troops (0.7)
- **economy_focus**: Buildings (1.0), Research (0.95), Pets (0.6)

### Optimizer Documentation

Full decision flow and logic: `data/optimizer/OPTIMIZER_LOGIC.md`

### Strategy Guides (`data/guides/`)

Detailed reasoning and explanations for recommendations:

| Guide | File | Purpose |
|-------|------|---------|
| Hero Lineups | `hero_lineup_reasoning.json` | Rally joiner selection, slot 1 hero choice, expedition vs exploration |
| Daybreak Island | `daybreak_island_priorities.json` | Tree of Life priorities, decoration strategy by spender type |
| Research | `research_priorities.json` | Research tree order, Tool Enhancement VII priority, by profile |
| Recommendation Reasons | `../optimizer/recommendation_reasons.json` | "Why" explanations for all suggestion types |

**Key Guide Features:**
- Priorities by spending profile (F2P → whale)
- Priorities by alliance role (rally lead, filler, farmer)
- Common mistakes with explanations
- Quick reference summaries

### Recommendation Reasons

Every recommendation should include a `reason` field explaining "why":
- **Unlock gates**: "Unlocking X at Y opens Z"
- **Efficiency milestones**: "X provides Y% efficiency - critical milestone"
- **Power gains**: "X gives Y power for Z cost - high efficiency"
- **Spending gates**: "X is whale territory for F2P - consider Y instead"

## Upgrade Data System

The optimizer uses a tables-first data model with 920+ upgrade edges for cost-aware recommendations.

### Data Files (`data/upgrades/`)

| System | File | Edges | Currencies |
|--------|------|-------|------------|
| Chief Gear | `chief_gear.steps.json` | 83 | hardened_alloy, polishing_solution, design_plan, lunar_amber |
| War Academy | `war_academy.steps.json` | 45 | fire_crystal_shards, refined_fire_crystals, meat, wood, coal, iron |
| Troops (train) | `troops.train.edges.json` | 90 | meat, wood, coal, iron |
| Troops (promote) | `troops.promote.edges.json` | 75 | meat, wood, coal, iron |
| Buildings (L1-30) | `buildings.edges.json` | 261 | wood, meat, coal, iron, fire_crystal |
| Buildings (FC) | `buildings.fc.edges.json` | 313 | wood, meat, coal, iron, fire_crystal, refined_fire_crystal |
| Hero Gear Mastery | `hero_gear.mastery.edges.json` | 20 | essence_stone, mythic_gear |
| Chief Charms | `chief_charms.edges.json` | 16 | charm_guide, charm_design, jewel_secrets |
| Pets | `pets.advancement.edges.json` | 10 | pet_food, taming_manual, energizing_potion, strengthening_serum |
| Daybreak Island | `daybreak_island.tree_of_life.edges.json` | 9 | life_essence |

### Build Scripts (`scripts/`)

```bash
# Regenerate edges from raw data
py scripts/build_war_academy_edges.py
py scripts/build_buildings_edges.py
py scripts/build_buildings_fc_edges.py

# Check gem shadow prices status
py scripts/compute_gem_costs.py --check-prices
```

### Resource Valuation (`data/conversions/`)

- `gem_shadow_prices.json` - Gem-equivalent costs for all resources (needs screenshots to populate)
- `scarcity_profiles.json` - Player-specific multipliers (F2P, low spender, whale)

### Research Sources (`data/research_sources.json`)

Tiered source registry for data collection:
- **Tier 1** (trust 1.0): WoS Wiki, Official Help
- **Tier 2** (trust 0.85-0.9): whiteoutsurvival.app, whiteoutdata.com, quackulator.com, onechilledgamer.com
- **Tier 3** (trust 0.6): allclash.com (meta only, must label)

### Skills (`.claude/skills/`)

- `/wos-research` - Tiered source lookup with confidence grades
- `/wos-recommend` - Upgrade recommendations
- `/wos-upgrades` - Cost data access
- `/wos-joiner` - Rally joiner hero selection
- `/wos-lineup` - Event lineup builder

## Game Data References

Hero tier rankings and game mechanics sourced from:
- [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/)
- [AllClash Tier List](https://www.allclash.com/best-heroes-in-whiteout-survival-tier-list/)
- [WhiteoutData](https://whiteoutdata.com/)
- [WhiteoutSurvival.app](https://whiteoutsurvival.app/) - FC building data
- [Quackulator](https://www.quackulator.com/) - Cost calculators
- [OneChilledGamer](https://onechilledgamer.com/) - Troop calculators

## Future Enhancements

Planned features not yet implemented:
- Event calendar with SvS reminders
- Power calculators (per-upgrade power gain)
- Alliance coordination features
- Actual hero portrait images (currently using class symbols)
- Gem shadow prices (needs in-game screenshots for resource/speedup pricing)
- Research tree granular costs (currently partial - structure only)
- Goal pathfinding ("How do I reach X milestone?")
