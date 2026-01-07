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

### Priority System

Users set priorities (1-5 scale) for:
- SvS / State vs State
- Rally Attacks (Bear Hunt, Crazy Joe)
- Castle Battles
- Exploration / PvE
- Resource Gathering

The recommendation engine weights upgrades based on these priorities.

### Rally Joiner Mechanics

**Critical mechanic**: When joining a rally, only the **leftmost hero's expedition skill** is used.

**Skill level determines priority**: Only the top 4 highest LEVEL expedition skills from all joiners apply to the rally. This is based on skill level, not player power.

**Risk of wrong skills**: A high-level wrong skill (like Sergey's defensive skill at level 5) can bump out a lower-level valuable skill (like Jessie's +25% damage at level 3).

**Best Attack Joiner Heroes** (for Bear Trap, Castle Attacks):
| Hero | Gen | Skill Effect |
|------|-----|--------------|
| Jeronimo | 1 | Infantry ATK multiplier |
| Jessie | 5 | +25% DMG dealt (all troops) |

**Best Garrison Joiner Heroes** (for defense):
| Hero | Gen | Skill Effect |
|------|-----|--------------|
| Sergey | 1 | -20% DMG taken (all troops) |

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

## Game Data References

Hero tier rankings and game mechanics sourced from:
- [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/)
- [AllClash Tier List](https://www.allclash.com/best-heroes-in-whiteout-survival-tier-list/)
- [WhiteoutData](https://whiteoutdata.com/)

## Future Enhancements

Planned features not yet implemented:
- Pet tracking and recommendations
- Chief gear and charm tracking
- Event calendar with SvS reminders
- Power calculators
- Alliance coordination features
- Actual hero portrait images (currently using class symbols)
