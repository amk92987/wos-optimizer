# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Whiteout Survival Optimizer - A comprehensive web-based tool to help Whiteout Survival players track their heroes, analyze resources, and get personalized upgrade recommendations optimized for SvS (State vs State) and combat.

**Key Stats:**
- 37 Next.js pages (static export) with serverless API backend
- 56 hero portraits downloaded from wiki
- 67 JSON data files covering all game systems
- DynamoDB with 3 tables (main, admin, reference) per environment
- 10 Lambda functions behind API Gateway + CloudFront
- 9 Claude Code skills for domain-specific tasks

## Development Environment

- Python 3.13+ (backend Lambda functions)
- Node.js / Next.js 14 (frontend static export)
- Virtual environment: `.venv/` (for local scripts)
- Infrastructure: AWS SAM (CloudFormation)
- Database: DynamoDB (serverless)
- Auth: AWS Cognito (email-based)
- AI: OpenAI API (gpt-4o-mini) for AI-powered recommendations
- Secrets: AWS Secrets Manager

## Environments (IMPORTANT)

| Name | Stack | URL | Database | Purpose |
|------|-------|-----|----------|---------|
| **Local** | Your machine (localhost:3000) | N/A | N/A | Frontend dev |
| **Dev** | SAM `wos-dev` | wosdev.randomchaoslabs.com | DynamoDB (dev tables) | Testing changes |
| **Live** | SAM `wos-live` | wos.randomchaoslabs.com | DynamoDB (live tables) | Production users |

**Naming Convention:**
- "Local" = your development machine
- "Dev" = AWS serverless dev stack for testing
- "Live" = AWS serverless production stack (also called "production" or "prod")

**Deployment Commands:**
```bash
# Deploy to Dev (backend + frontend)
cd infra && sam build && sam deploy --no-confirm-changeset
cd ../frontend && npm run build && aws s3 sync out s3://wos-frontend-dev-561893854848 --delete
aws cloudfront create-invalidation --distribution-id EWE2LGBUHCEI1 --paths "/*"

# Deploy to Live (be careful!)
cd infra && sam build && sam deploy --config-env live --no-confirm-changeset
cd ../frontend && npm run build && aws s3 sync out s3://wos-frontend-live-561893854848 --delete
aws cloudfront create-invalidation --distribution-id E1AJ7LCWTU8ZMH --paths "/*"
```

**Email Configuration:**
- SES configured (sandbox mode - verified emails only)
- SPF record includes amazonses.com

## Commands

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Set AI API key for AI recommendations (choose one)
set ANTHROPIC_API_KEY=your-key-here  # Windows (Claude - preferred)
set OPENAI_API_KEY=your-key-here     # Windows (OpenAI - fallback)
export ANTHROPIC_API_KEY=your-key-here  # Unix (Claude)
export OPENAI_API_KEY=your-key-here     # Unix (OpenAI)

# Run the application
streamlit run app.py

# Download hero images from wiki
py scripts/download_hero_images.py

# Build upgrade edge data
py scripts/build_war_academy_edges.py
py scripts/build_buildings_fc_edges.py
py scripts/build_chief_gear_edges.py

# Run QA and data audits
py scripts/run_qa_check.py      # Automated QA validation
py scripts/run_data_audit.py    # Data integrity audit
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
├── DATA_AUDIT.md             # Data file inventory with sources and confidence
├── QA_CHECKLIST.md           # QA process documentation
│
├── database/                 # Database layer
│   ├── models.py             # SQLAlchemy models (UserProfile, Hero, UserHero, etc.)
│   └── db.py                 # Database connection and session management
│
├── data/                     # Game data (67 JSON files)
│   ├── heroes.json           # All heroes Gen 1-14 with tiers, skills, image refs (43KB)
│   ├── chief_gear.json       # Chief gear stats and progression
│   ├── events.json           # Event calendar and mechanics
│   ├── vip_system.json       # VIP levels and buffs
│   ├── wos_schema.json       # Comprehensive hero mechanics schema
│   ├── WOS_REFERENCE.md      # Game mechanics documentation
│   │
│   ├── guides/               # Strategy guides (7 files)
│   │   ├── quick_tips.json           # Cheat sheet - 15 categories, 79 tips
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
├── pages/                    # Streamlit multi-page app
│   │   # User Pages (game-focused)
│   ├── 0_Home.py             # Welcome, quick start
│   ├── 00_Beginner_Guide.py  # New player guide
│   ├── 1_Hero_Tracker.py     # Hero management with portraits
│   ├── 2_Chief_Tracker.py    # Chief gear and charms
│   ├── 3_Backpack.py         # Inventory tracking, OCR
│   ├── 5_Lineups.py          # Hero lineup builder
│   ├── 6_AI_Advisor.py       # AI-powered advice
│   ├── 7_Save_Load.py        # Profile management
│   ├── 8_Packs.py            # Pack analyzer
│   ├── 9_Events.py           # Event calendar
│   ├── 10_Combat.py          # Combat optimization guide
│   ├── 11_Quick_Tips.py      # Quick reference
│   ├── 12_Battle_Tactics.py  # Battle tactics guide
│   ├── 13_Settings.py        # User settings
│   ├── 14_Daybreak_Island.py # Daybreak Island guide
│   │   # Admin Pages (system management)
│   ├── 0_Admin_Home.py       # Admin dashboard
│   ├── 1_Admin_Announcements.py # System announcements
│   ├── 2_Admin_Audit_Log.py  # User action tracking
│   ├── 3_Admin_Feature_Flags.py # Toggle features
│   ├── 4_Admin_Database.py   # Database browser
│   ├── 5_Admin_Feedback.py   # User feedback
│   ├── 6_Admin_Game_Data.py  # Game data management
│   ├── 7_Admin_Data_Integrity.py # Data validation
│   ├── 8_Admin_Usage_Reports.py # Analytics
│   ├── 9_Admin_Export.py     # Data export (CSV/Excel/JSON)
│   └── 15_Admin.py           # User management
│
├── auth_pages/               # Authentication pages (unauthenticated users)
│   ├── landing.py            # Public landing page
│   ├── auth_login.py         # Login form
│   └── auth_register.py      # Registration form
│
├── engine/                   # Recommendation engines
│   ├── recommendation_engine.py  # Main engine orchestrator
│   ├── recommender.py            # Legacy rule-based recommendations
│   ├── ai_recommender.py         # Claude/OpenAI fallback integration
│   └── analyzers/                # Specialized analyzers
│       ├── hero_analyzer.py      # Hero upgrade recommendations
│       ├── gear_advisor.py       # Chief/hero gear priorities
│       ├── lineup_builder.py     # Game mode lineup builder
│       ├── progression_tracker.py # Game phase detection
│       └── request_classifier.py  # Routes questions to rules vs AI
│
├── ocr/                      # Screenshot parsing
│   └── screenshot_parser.py  # EasyOCR integration
│
├── scripts/                  # Data building and QA utilities
│   ├── download_hero_images.py       # Fetch hero portraits from wiki
│   ├── build_war_academy_edges.py    # War Academy progression
│   ├── build_buildings_fc_edges.py   # FC building costs
│   ├── build_chief_gear_edges.py     # Chief gear upgrades
│   ├── compute_gem_costs.py          # Gem shadow pricing
│   ├── run_qa_check.py               # Automated QA validation
│   └── run_data_audit.py             # Data integrity audit
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
    └── skills/               # 8 custom skills
        ├── wos-joiner/       # Rally joiner hero selection
        ├── wos-lineup/       # Hero lineup optimization
        ├── wos-research/     # Research prioritization
        ├── wos-recommend/    # General recommendations
        ├── wos-upgrades/     # Upgrade path optimization
        ├── wos-test-ai/      # AI system testing
        ├── wos-data-audit/   # Data validation and integrity
        ├── wos-qa-review/    # Web app QA checks
        └── wos-feedback/     # Review pending feedback for development
```

### Database Models (`database/models.py`)

**User**:
- Authentication (username, email, password_hash)
- Role: 'admin' or 'user'
- Account status: is_active, is_verified, is_test_account
- AI rate limiting: ai_requests_today, last_ai_request
- Has many UserProfiles (one user can have multiple game accounts)

**UserProfile**:
- State number (server/state identifier for cross-state tracking)
- Server age, furnace level (1-30+FC), priority settings
- Spending profile: f2p, minnow, dolphin, orca, whale
- Priority focus: svs_combat, balanced_growth, economy_focus
- Alliance role: rally_lead, filler, farmer, casual
- Priority levels (1-5 scale): PvP Attack, Defense, PvE, Economy
- Farm account: is_farm_account, linked_main_profile_id
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
- Exclusive gear: unlocked status, quality, level, mastery, exclusive_gear_skill_level (0-10)

**UserInventory**: Backpack items and quantities

**Item**: Backpack item definitions with OCR aliases

**UpgradeHistory**: Analytics tracking for upgrades

### Authentication & Admin System

**User Model** (`database/models.py`):
- id, username (unique), email, password_hash (bcrypt)
- role: 'admin' or 'user'
- is_active: boolean for suspend/activate
- created_at, last_login timestamps

**Auth Functions** (`database/auth.py`):
- `authenticate_user(db, username, password)` - Verify credentials
- `login_user(user)` / `logout_user()` - Session management
- `login_as_user(user)` - Admin impersonation (preserves original session)
- `is_impersonating()` - Check impersonation status
- `require_admin()` - Page-level access control decorator
- `ensure_admin_exists(db)` - Creates default admin (admin/admin123)

**Page Routing** (`app.py`):
- Unauthenticated users see: Landing → Login/Register
- Admin users see: Admin navigation with 10 management pages
- Regular users see: Game navigation with tracker/advisor pages
- Impersonation shows: User view + red banner with "Switch Back"

**Admin Pages** (10 pages):
| Page | Purpose |
|------|---------|
| Dashboard | Key metrics overview |
| Users | CRUD, suspend/activate, impersonation, test account management |
| Announcements | System-wide notifications |
| Feature Flags | Toggle features (8 defaults) |
| Database | Browse/manage tables |
| Feedback | User feedback inbox |
| Game Data | Game data management |
| Data Integrity | Validation tools |
| Usage Reports | Analytics |
| Export | CSV/Excel/JSON export |

**Test Account Management** (Admin → Users):
- "Test Accts" metric shows count of test accounts
- "Test Only" checkbox filters to show only test accounts
- `TEST` badge displayed next to test account usernames
- Create User: "Test Account" checkbox to mark new users
- Edit User: "Test" checkbox to toggle test status

**Feature Flags** (defaults):
- `hero_recommendations`, `new_user_onboarding`, `analytics_tracking` - enabled
- `inventory_ocr`, `alliance_features`, `beta_features`, `maintenance_mode`, `dark_theme_only` - disabled

**Known Streamlit Quirk**: Buttons with emoji characters don't render in certain column/loop contexts. Use plain text labels.

### AI System (`database/ai_service.py`, `engine/ai_recommender.py`)

**AI Settings Model** (`database/models.py`):
- `AISettings` - Global singleton for AI configuration
- Mode: 'off', 'on' (rate limited), 'unlimited'
- Rate limits: daily_limit_free (10), daily_limit_admin (1000), cooldown_seconds (30)
- Provider settings: primary_provider, fallback_provider, model names

**AI Conversation Logging**:
- `AIConversation` - Logs all Q&A for training data
- Fields: question, answer, provider, model, tokens, response_time
- User feedback: rating (1-5), is_helpful (thumbs up/down), user_feedback
- Admin curation: is_good_example, is_bad_example, admin_notes

**Rate Limiting**:
- Per-user daily limits reset at midnight UTC
- Cooldown between requests (configurable)
- Admin toggle: Off (disabled), On (limited), Unlimited

**AI Personality & Syntax** (`engine/ai_recommender.py`):
- Address users as "Chief" (game terminology)
- Use WoS vocabulary: Settlement, Furnace, Accelerators, Supplies, etc.
- Soft trigger keywords adapt tone: optimize, SvS, furnace, gems, farm
- "Pause & Ask" pattern: one clarifying question max when uncertain
- Jailbreak protection: only answers WoS questions

**Admin AI Page** (`pages/10_Admin_AI.py`):
- Mode toggle (Off/On/Unlimited) with visual indicators
- Usage statistics and rate limit configuration
- Conversation browser with filtering
- Training data curation (mark good/bad examples)
- Export for fine-tuning (JSONL, CSV)

### Hero Card Features (Always-Interactive UI)

Each hero card is an expandable row. The collapsed header shows:
- **Hero portrait** - Actual hero image from assets/heroes/ (80x80px)
- **Tier badge** with hover tooltip (S+ through D)
- **Rarity border** color-coded (Blue=Rare, Purple=Epic, Gold=Legendary)
- **Generation** column
- **Star rating** with purple ascension pips (shown when not at max stars)
- **Level** display
- **Save indicator** - shows saving/saved/error status next to hero name

The expanded body is **always interactive** (no edit/save/cancel buttons). All changes auto-save via debounced API calls (300ms). Components:
- **Level** - NumberStepper `[-] value [+]`, click number to type directly
- **Stars** - 5 clickable star icons, tap to set, tap current to decrement
- **Ascension pips** - 5 clickable purple circles below stars (hidden at 5 stars), tap to set
- **Skills** - Clickable pip circles (green=exploration, orange=expedition), tap to set level, tap current to decrement
- **Gear** - 4 slots with always-visible quality dropdown + conditional level/mastery steppers
- **Exclusive gear** - Toggle switch, quality/level/mastery editors, plus 10 clickable exclusive skill level pips (1-10)
- **Remove** - "Remove from collection" link (only action button remaining)

**Frontend architecture** (`frontend/components/hero/`):
- `SaveIndicator.tsx` - Save status display
- `StarRating.tsx` - Clickable stars + ascension pips
- `SkillPips.tsx` - Clickable skill level circles
- `NumberStepper.tsx` - Reusable `[-] value [+]` control
- `GearSlotEditor.tsx` - Inline gear slot with quality dropdown + steppers
- `MythicGearEditor.tsx` - Exclusive gear toggle + editors + skill pips

**Auto-save hook** (`frontend/hooks/useAutoSave.ts`):
- Debounces 300ms, merges concurrent changes into single API call
- Optimistic UI updates, reverts on error
- Returns `saveField()`, `saveFields()`, and `saveStatus`

**HeroCard props**: `hero`, `token`, `onSaved?`, `onRemove?` (no `onUpdate`)

### Upgrade Recommendations

**Priority Settings Display:**
- Shows 4 priority categories with arctic-themed sliders (1-5 scale)
- Categories: PvP Attack, Defense, PvE, Economy
- Adjustable on Settings page with ice-blue Playstyle buttons

**Top Recommendations Tab:**
- One recommendation per hero (deduplicated, highest priority shown)
- Filterable by upgrade type and priority level
- Single column list ordered by priority score

**Best Heroes to Invest Tab:**
- Only shows owned heroes
- Investment targets based on spending profile (F2P → Whale)
- Shows current level → target level with star progression
- Generation-aware advice (save vs invest based on hero age)
- Considers upcoming generations for resource planning

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
| Jessie | 1 | Stand of Arms | +5-25% DMG dealt |
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

### Chief Charms System

Unlocks at Furnace 25. Each gear piece has **3 charm slots of the SAME type**:

| Gear Type | Pieces | Charm Type | Troop Buff |
|-----------|--------|------------|------------|
| Lancer | Cap, Watch | Keenness | Lancer stats |
| Infantry | Coat, Pants | Protection | Infantry stats |
| Marksman | Belt, Weapon | Vision | Marksman stats |

**Level Progression:**
- Levels 1-3: Simple progression
- Levels 4-16: Sub-levels like FC construction (4-1 → 4-2 → 4-3 → 5)
- Level 16 requires Gen 7

**Database Model:** `UserChiefCharm` with fields like `cap_slot_1`, `cap_slot_2`, `cap_slot_3` (strings for sub-level support)

**UI Layout:** Triangular arrangement per gear piece - 1 charm on top, 2 below

## Claude Skills

Located in `.claude/skills/`:

- `/wos-joiner` - Rally joiner hero selection
- `/wos-lineup` - Event lineup builder
- `/wos-research` - Tiered source lookup with confidence grades
- `/wos-recommend` - Upgrade recommendations
- `/wos-upgrades` - Cost data access
- `/wos-test-ai` - Run comprehensive AI and recommendation tests
- `/wos-data-audit` - Validate game data against sources
- `/wos-qa-review` - Run QA checks on web application
- `/wos-feedback` - Review pending feedback for development

## Feedback Workflow

User feedback flows through these statuses:
1. **New** - Freshly submitted feedback
2. **Pending Fix** - Bugs marked for development
3. **Pending Update** - Features marked for development
4. **Completed** - Fixed/implemented items
5. **Archive** - Dismissed or no longer needed

**Admin Feedback Page** (Admin → Feedback):
- Tabs: Bugs | Features | All Active | Completed | Archive
- Smart routing: bugs go to "Pending Fix", features go to "Pending Update"
- Bulk actions: Archive all completed, Empty archive

**Development Workflow:**
1. Users submit feedback via menu or AI Advisor page
2. Admin triages in Feedback Inbox (mark for fix/update or archive)
3. Run `/wos-feedback` to get Claude's analysis of pending items
4. Implement fixes/features
5. Mark as Completed in Admin

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

### Verified Hero Data - CRITICAL

**NEVER GUESS HERO GENERATIONS. ALWAYS use `data/heroes.json` as the source of truth.**

#### Complete Hero Generation Reference (AUTHORITATIVE)

| Gen | Server Days | Heroes |
|-----|-------------|--------|
| 1 | 0-40 | Bahiti, Charlie, Cloris, Eugene, Gina, Jasser, **Jeronimo**, **JESSIE**, Ling Xue, Lumak Bokan, **Molly**, **Natalia**, Patrick, Seo-yoon, **SERGEY**, Smith, Zinman |
| 2 | 40-120 | **Alonso**, Flint, Philly |
| 3 | 120-200 | Greg, Logan, Mia |
| 4 | 200-280 | Ahmose, Lynn, Reina |
| 5 | 280-360 | Gwen, Hector, Norah |
| 6 | 360-440 | Renee, Wayne, **Wu Ming** |
| 7 | 440-520 | Bradley, Edith, Gordon |
| 8 | 520-600 | **Gatot**, Hendrik, Sonya |
| 9 | 600-680 | Fred, Magnus, Xura |
| 10 | 680-760 | Blanchette, Freya, Gregory |
| 11 | 760-840 | Eleonora, Lloyd, Rufus |
| 12 | 840-920 | Hervor, Karol, Ligeia |
| 13 | 920-1000 | Flora, Gisela, Vulcanus |
| 14 | 1000+ | Cara, Dominic, Elif |

**KEY HEROES EMPHASIZED:**
- **JESSIE = Gen 1** (NOT Gen 5!) - Best attack joiner, Stand of Arms skill
- **SERGEY = Gen 1** - Best garrison joiner, Defenders' Edge skill
- **Jeronimo = Gen 1** - Top infantry hero
- **Molly = Gen 1** - Top marksman hero
- **Wu Ming = Gen 6** - Strong infantry alternative
- **Hector = Gen 5** - Strong infantry option
- **Gatot = Gen 8** - Top infantry hero

When working with heroes, verify:
- **Generation**: Each hero's `generation` field (1-14) - DO NOT guess generations
- **Hero class**: `hero_class` field (Infantry, Lancer, Marksman)
- **Tier ratings**: `tier_overall`, `tier_expedition`, `tier_exploration` (S+, S, A, B, C, D)
- **Skills**: `exploration_skill_1/2/3`, `expedition_skill_1/2/3` with `_desc` suffixes for descriptions

**Common mistakes to avoid:**
- Jessie is Gen 1 (NOT Gen 5)
- Gwen is Gen 5 (not Gen 4)
- Gen 3 is Logan, Mia, Greg (not Bahiti, Patrick)
- Sergey is B-tier overall but S-tier expedition
- Hector is Gen 5 (not Gen 4 or Gen 6)

**To verify hero data**, run:
```bash
.venv/Scripts/python.exe -c "
import json
with open('data/heroes.json', encoding='utf-8') as f:
    data = json.load(f)
for h in data['heroes']:
    if h['name'] == 'HERO_NAME':
        print(h)
"
```

When generating AI recommendations or lineup suggestions, always load and reference the actual hero data from `data/heroes.json` rather than relying on memory which may be outdated or incorrect.

## Data Sources

- [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/) - Hero data, images
- [WhiteoutData](https://whiteoutdata.com/) - Game mechanics
- [WhiteoutSurvival.app](https://whiteoutsurvival.app/) - FC building data
- [Quackulator](https://www.quackulator.com/) - Cost calculators
- [AllClash](https://www.allclash.com/) - Tier list information

## Upgrade Calculators (Feb 2026)

The Upgrades page has an **"Upgrade Calculators"** tab with 6 calculators organized by category:

| Category | Calculator | Resources Calculated |
|----------|-----------|---------------------|
| Hero Gear | Enhancement | XP (pre-Legendary, L0-100) |
| Hero Gear | Legendary | XP + Mithril + Legendary Gear (L0-100) |
| Hero Gear | Mastery | Essence Stones + Mythic Gear (L0-20) |
| Chief | Chief Gear | Hardened Alloy + Polishing Solution + Design Plans + Lunar Amber (46 tiers) |
| Chief | Charms | Charm Guides + Charm Designs + Jewel Secrets (16 levels with sub-levels) |
| Buildings | War Academy | Fire Crystal Shards + Refined Fire Crystals + Meat/Wood/Coal/Iron (FC1-FC10) |

Chief Gear and Charms calculators also show stat bonus % gains.

**Troop Ratio Reference (Infantry/Lancer/Marksman):**
| Mode | Ratio | Reasoning |
|------|-------|-----------|
| Bear Trap | 0/10/90 | Bear is slow, maximize marksman DPS |
| Crazy Joe | 90/10/0 | Infantry kills before Joe's backline attacks |
| Garrison | 60/25/15 | Defense - lancers survive better than marksmen |
| SvS March | 40/20/40 | Balanced for field combat |
| Rally Joiner Attack | 30/20/50 | Support rally leader's composition |
| Rally Joiner Defense | 50/30/20 | Infantry-heavy for garrison support |

## Future Enhancements

**Backlog:**
- Legendary Gear Level Logic on Hero Tracker (enforce level 100 before Legendary ascension)
- Gear Power Contribution to Lineups (factor gear quality/level into lineup scoring)
- Remove Legacy Streamlit Code (~2.5MB of dead code, see TODO.md for full breakdown)
- Gem shadow prices (needs in-game screenshots)
- Research tree granular costs
- Goal pathfinding ("How do I reach X milestone?")
- CAPTCHA or login attempt protection
- Email notifications for admin (new feedback alerts)
