# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Whiteout Survival Optimizer - A comprehensive web-based tool to help Whiteout Survival players track their heroes, analyze resources, and get personalized upgrade recommendations optimized for SvS (State vs State) and combat.

**Key Stats:**
- 12 Streamlit pages with 5,100+ lines of application code
- 56 hero portraits downloaded from wiki
- 59 JSON data files covering all game systems
- SQLite database with 6 primary tables
- 5 Claude Code skills for domain-specific tasks

## Development Environment

- Python 3.13+
- Virtual environment: `.venv/`
- Framework: Streamlit
- Database: SQLite with SQLAlchemy ORM
- AI: OpenAI API for AI-powered recommendations
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

# Download hero images from wiki
py scripts/download_hero_images.py

# Build upgrade edge data
py scripts/build_war_academy_edges.py
py scripts/build_buildings_fc_edges.py
py scripts/build_chief_gear_edges.py
```

## Architecture

### Directory Structure
```
WoS/
├── app.py                    # Main Streamlit entry point (98 lines)
├── requirements.txt          # Dependencies
├── wos.db                    # SQLite database (36KB)
├── CLAUDE.md                 # This file - developer guide
├── README.md                 # User-facing documentation
│
├── database/                 # Database layer
│   ├── models.py             # SQLAlchemy models (UserProfile, Hero, UserHero, etc.)
│   └── db.py                 # Database connection and session management
│
├── data/                     # Game data (59 JSON files)
│   ├── heroes.json           # All heroes Gen 1-14 with tiers, skills, image refs (43KB)
│   ├── chief_gear.json       # Chief gear stats and progression
│   ├── events.json           # Event calendar and mechanics
│   ├── vip_system.json       # VIP levels and buffs
│   ├── wos_schema.json       # Comprehensive hero mechanics schema
│   ├── WOS_REFERENCE.md      # Game mechanics documentation
│   │
│   ├── guides/               # Strategy guides (7 files)
│   │   ├── quick_tips.json           # Cheat sheet - 13 categories of tips
│   │   ├── combat_optimization_audit.json  # Combat stat sources
│   │   ├── daybreak_island_priorities.json # Tree of Life & decorations
│   │   ├── research_priorities.json  # Research tree order
│   │   ├── combat_formulas.json      # Damage calculations
│   │   └── hero_lineup_reasoning.json # Rally/lineup selection
│   │
│   ├── optimizer/            # Decision engine config (8 files)
│   │   ├── progression_phases.json   # Game phases by furnace level
│   │   ├── system_unlocks.json       # When systems become available
│   │   ├── decision_rules.json       # Priority weights
│   │   └── recommendation_reasons.json # "Why" explanations
│   │
│   ├── upgrades/             # Upgrade edge graphs (12 files, 920+ edges)
│   │   ├── buildings.edges.json      # L1-30 buildings (261 edges)
│   │   ├── buildings.fc.edges.json   # FC buildings (313 edges)
│   │   ├── troops.train.edges.json   # Troop training (90 edges)
│   │   ├── chief_gear.steps.json     # Chief gear (83 edges)
│   │   └── war_academy.steps.json    # War Academy (45 edges)
│   │
│   ├── conversions/          # Resource valuation
│   │   ├── gem_shadow_prices.json    # Gem-equivalent costs
│   │   └── resource_value_hierarchy.json
│   │
│   ├── ai/                   # AI training data
│   │   ├── openai_wos_knowledge.json # Game knowledge base
│   │   └── openai_wos_followup.json  # Follow-up handling
│   │
│   └── raw/                  # Raw data samples
│
├── assets/                   # Static assets
│   └── heroes/               # Hero portrait images (56 files, PNG/JPG)
│
├── pages/                    # Streamlit multi-page app (12 pages, 5,129 lines)
│   ├── 0_Home.py             # Welcome, quick start (136 lines)
│   ├── 1_Heroes.py           # Hero management with portraits (564 lines)
│   ├── 2_Backpack.py         # Inventory tracking, OCR (317 lines)
│   ├── 3_Recommendations.py  # Priority-weighted suggestions (401 lines)
│   ├── 4_Settings.py         # User profile config (520 lines)
│   ├── 5_AI_Advisor.py       # OpenAI-powered advice (315 lines)
│   ├── 6_Profiles.py         # Multi-profile management (477 lines)
│   ├── 7_Lineups.py          # Hero lineup builder (963 lines)
│   ├── 8_Pack_Analyzer.py    # Backpack analysis (397 lines)
│   ├── 9_Events_Guide.py     # Event calendar (306 lines)
│   ├── 10_Combat_Optimization.py # SvS/combat guide (450 lines)
│   └── 11_Quick_Tips.py      # Quick reference (283 lines)
│
├── engine/                   # Recommendation engines
│   ├── recommender.py        # Rule-based recommendations (532 lines)
│   └── ai_recommender.py     # OpenAI integration (368 lines)
│
├── ocr/                      # Screenshot parsing
│   └── screenshot_parser.py  # EasyOCR integration
│
├── scripts/                  # Data building utilities
│   ├── download_hero_images.py       # Fetch hero portraits from wiki
│   ├── build_war_academy_edges.py    # War Academy progression
│   ├── build_buildings_fc_edges.py   # FC building costs
│   ├── build_chief_gear_edges.py     # Chief gear upgrades
│   └── compute_gem_costs.py          # Gem shadow pricing
│
├── styles/
│   └── custom.css            # Winter/frost theme styling
│
├── utils/
│   ├── ask_openai.py         # OpenAI API wrapper
│   ├── sidebar.py            # Shared sidebar components
│   └── image_downloader.py   # Legacy image downloader
│
└── .claude/                  # Claude Code configuration
    ├── settings.local.json   # Local settings
    └── skills/               # 5 custom skills
        ├── wos-joiner/       # Rally joiner hero selection
        ├── wos-lineup/       # Hero lineup optimization
        ├── wos-research/     # Research prioritization
        ├── wos-recommend/    # General recommendations
        └── wos-upgrades/     # Upgrade path optimization
```

### Database Models (`database/models.py`)

**UserProfile**:
- Server age, furnace level (1-30+FC), priority settings
- Spending profile: f2p, minnow, dolphin, orca, whale
- Priority focus: svs_combat, balanced_growth, economy_focus
- Alliance role: rally_lead, filler, farmer, casual
- Priority levels (1-5 scale): SvS, Rally, Castle Battle, PvE, Gathering
- SvS tracking (wins, losses, last date)

**Hero**:
- Static reference data (name, generation 1-14, class, tier ratings)
- Skills: exploration_skill_1/2/3, expedition_skill_1/2/3 (with optional _desc fields for tooltips)
- Image filename reference (points to assets/heroes/)

**UserHero**:
- User's owned heroes with levels (1-80)
- Stars (0-5) and ascension tier (0-5)
- Skill levels (1-5 for each of 6 skills: 3 exploration + 3 expedition)
- Hero gear: 4 slots with quality (0=None through 6=Legendary), level (0-100), mastery (0-20 for Gold+)
- Exclusive gear: unlocked status, quality, level, mastery

**UserInventory**: Backpack items and quantities

**Item**: Backpack item definitions with OCR aliases

**UpgradeHistory**: Analytics tracking for upgrades

### Hero Card Features

Each hero row displays:
- **Hero portrait** - Actual hero image from assets/heroes/ (80x80px)
- **Tier badge** with hover tooltip (S+ through D)
- **Rarity border** color-coded (Blue=Rare, Purple=Epic, Gold=Legendary)
- **Generation** column
- **Star rating** with purple ascension pips (shown when not at max stars)
- **Level** display
- **Owned checkbox** - auto-expands editor when checked

Hero editor (expander) includes:
- **Level/Stars/Ascension** row with visual pips
- **Skills** side-by-side with hoverable names showing descriptions
- **Gear** 4 slots with quality dropdown, level (0-100), mastery (0-20 for Gold+)
- **Exclusive gear** section for heroes with mythic gear

### Hero Classes
- **Infantry**: Frontline tanks - Chief Gear: Coat, Pants
- **Marksman**: Ranged damage - Chief Gear: Belt, Shortstaff
- **Lancer**: Balanced fighters - Chief Gear: Hat, Watch

### Hero Skill System

Each hero has two types of skills (up to 3 each):

**Exploration Skills (Left Side)**
- Upgraded with Exploration Manuals
- Used for PvE content (exploration, events)
- Levels 1-5
- Skill descriptions available via hover tooltips (populated from `_desc` fields in heroes.json)

**Expedition Skills (Right Side)**
- Upgraded with Expedition Manuals
- Used for PvP content (rallies, garrison, SvS)
- Levels 1-5
- **Top-right skill** applies when joining rallies
- Skill descriptions available via hover tooltips

### Rally Joiner Mechanics

**Critical mechanic**: When joining a rally, only the **leftmost hero's top-right expedition skill** is used.

**Skill level priority**: Only the top 4 highest LEVEL expedition skills from all joiners apply to the rally.

**Best Attack Joiners** (Bear Trap, Castle Attacks):
| Hero | Gen | Top-Right Skill | Effect |
|------|-----|-----------------|--------|
| Jessie | 5 | Stand of Arms | +5-25% DMG dealt |
| Jeronimo | 1 | Infantry ATK buff | Scales with level |

**Best Garrison Joiners** (Defense):
| Hero | Gen | Top-Right Skill | Effect |
|------|-----|-----------------|--------|
| Sergey | 1 | Defenders' Edge | -4-20% DMG taken |

## Key Game Systems

### Daybreak Island - Battle Enhancer Decorations

**CRITICAL**: Combat stats come from **decorations**, not just Tree of Life!

**Mythic Decorations (10 levels × 1% = 10% max each)**:
| Troop Type | Attack Decoration | Defense Decoration |
|------------|-------------------|-------------------|
| Infantry | Floating Market | Snow Castle |
| Lancer | Amphitheatre | Elegant Villa |
| Marksman | Observation Deck | Art Gallery |

**Epic Decorations**: 5 levels × 0.5% = 2.5% max each

**Tree of Life Universal Buffs**:
- L4: +5% Defense
- L6: +5% Attack
- L9: +5% Health
- L10: +5% Lethality

### SvS Prep Phase Points

**SPEEDUPS ONLY GIVE POINTS ON DAY 1, 2, AND 5**

Key point values:
- Fire Crystals: 2,000 pts each (Day 1)
- Lucky Wheel: 8,000 pts per spin (Day 2/3)
- Mithril: 40,000 pts each (Day 4)
- Troop Promotion beats Speedups on Day 4

### SvS Battle Phase

- Enemies can teleport and attack unshielded cities
- Attacking drops shield for 30 minutes
- Losing = enemy becomes Supreme President of BOTH states
- Field Triage: 30-90% troop recovery after SvS

## Optimizer Decision System

### Spending Profiles
| Profile | Monthly USD | Description |
|---------|-------------|-------------|
| f2p | $0 | Free to play |
| minnow | $5-30 | Light spender |
| dolphin | $30-100 | Medium spender |
| orca | $100-500 | Heavy spender |
| whale | $500+ | Maximum investment |

### Game Phases
| Phase | Furnace | Focus |
|-------|---------|-------|
| early_game | 1-18 | Rush to F19 for Daybreak |
| mid_game | 19-29 | Rush to F30 for FC |
| late_game | 30/FC1-FC4 | FC progression |
| endgame | FC5+ | FC10 completion |

### System Unlocks
| Furnace | Systems Unlocked |
|---------|-----------------|
| 9 | Research |
| 18 | Pets (also needs 55 days) |
| 19 | Daybreak Island |
| 25 | Chief Charms |
| 30 | FC, War Academy, Hero Gear Mastery |

## Claude Skills

Located in `.claude/skills/`:

- `/wos-joiner` - Rally joiner hero selection
- `/wos-lineup` - Event lineup builder
- `/wos-research` - Tiered source lookup with confidence grades
- `/wos-recommend` - Upgrade recommendations
- `/wos-upgrades` - Cost data access

## Important Notes

### UTF-8 Encoding
All file operations with JSON files must use `encoding='utf-8'` due to special characters.

### Database Recreation
If database schema changes, delete `wos.db` to force recreation:
```bash
del wos.db  # Windows
rm wos.db   # Unix
```

### Hero Images
Hero portraits are stored in `assets/heroes/` with filenames matching `image_filename` in heroes.json. Images are loaded as base64 and embedded in hero cards.

To re-download images:
```bash
py scripts/download_hero_images.py
```

## Data Sources

- [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/) - Hero data, images
- [WhiteoutData](https://whiteoutdata.com/) - Game mechanics
- [WhiteoutSurvival.app](https://whiteoutsurvival.app/) - FC building data
- [Quackulator](https://www.quackulator.com/) - Cost calculators
- [AllClash](https://www.allclash.com/) - Tier list information

## Future Enhancements

- Gem shadow prices (needs in-game screenshots)
- Research tree granular costs
- Goal pathfinding ("How do I reach X milestone?")
- Power calculators (per-upgrade power gain)
- Alliance coordination features
