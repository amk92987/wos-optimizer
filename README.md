# Whiteout Survival Optimizer

A comprehensive web-based tool to help Whiteout Survival players track their heroes, manage resources, and get personalized upgrade recommendations optimized for SvS (State vs State) and combat.

## Features

### Hero Management
- Track all 56+ heroes from Gen 1-14 with detailed stats
- **Actual hero portrait images** from the game
- Visual hero cards with tier badges (S+ through D), rarity borders, and generation badges
- Inline editing for level (1-80), stars (0-5), ascension, skills, and gear
- Hero gear tracking (4 slots + mythic gear per hero)
- Tier descriptions explaining hero value

### Strategy Guides
- **Combat Optimization** - All hidden stat sources (Research, Daybreak decorations, Chief Gear, Charms, Pets)
- **Quick Tips** - 13 categories of consolidated game knowledge with priority ratings
- **Events Guide** - Event calendar and point optimization strategies
- **Daybreak Island** - Battle enhancer decorations and Tree of Life priorities

### Recommendations
- **Rule-based recommendation engine** with curated game knowledge (instant responses)
- **Power Optimizer** - Upgrade recommendations backed by actual power calculations:
  - Chief Gear: 42 tiers with exact % bonuses (9.35% → 187%)
  - Chief Charms: 16 levels with exact % bonuses (9% → 100%)
  - War Academy: Exact power_gain values per level (6,888 → 8,784)
  - Troop Tiers: Exact power per unit (T11 lancers/marksmen = 80 power!)
  - Hero upgrades: Level, star, and skill power estimates
- AI-powered fallback (Claude or OpenAI) for complex questions
- Priority-based upgrade recommendations (SvS, Rally, Castle Battle, PvE, Gathering)
- Combat-focused analysis for SvS optimization
- Rally joiner hero selection with verified game mechanics

### Lineup Builder
- Hero lineup optimization for different content types
- March composition builder
- Expedition vs Exploration skill tracking

### Resource Management
- Backpack inventory tracking
- OCR screenshot parsing (EasyOCR)
- **Pack Analyzer** with Frost Star valuation system (1 FS = $0.01)
  - 100+ items with researched values across 12 categories
  - Speedup and resource grids for quick entry
  - Efficiency ratings and filler detection
  - "Farmer Mode" to zero-out farmable resources

### User Profiles
- Multiple profile support
- Server age and generation tracking
- Spending profile selection (F2P to Whale)
- Priority focus configuration
- Alliance role settings

### Admin Dashboard
- **User Management** - Create, edit, suspend/activate users with role-based access
- **Admin Impersonation** - "Login as User" to see exactly what users see
- **Feature Flags** - Toggle features on/off without code changes
- **Announcements** - System-wide notification management
- **Audit Log** - Track user actions and system events
- **Usage Reports** - Analytics and metrics dashboard
- **Data Export** - Export data to CSV, Excel, or JSON
- **Database Browser** - Direct database inspection and management

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/wos-optimizer.git
cd wos-optimizer
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Unix/macOS
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Download hero images:
```bash
py scripts/download_hero_images.py
```

5. (Optional) Set AI API key for AI recommendations (choose one):
```bash
# Claude (preferred) - Windows
set ANTHROPIC_API_KEY=your-key-here
# Claude - Unix/macOS
export ANTHROPIC_API_KEY=your-key-here

# OpenAI (fallback) - Windows
set OPENAI_API_KEY=your-key-here
# OpenAI - Unix/macOS
export OPENAI_API_KEY=your-key-here
```

6. Run the application:
```bash
streamlit run app.py
```

7. Open http://localhost:8501 in your browser

## Application Pages

### User Pages (Game-Focused)
| Page | Description |
|------|-------------|
| **Home** | Welcome, quick start guide, generation calculator |
| **Beginner Guide** | New player onboarding guide |
| **Hero Tracker** | Hero management with portraits, inline editing |
| **Chief Tracker** | Chief gear and charms tracking |
| **Backpack** | Inventory tracking via OCR or manual entry |
| **AI Advisor** | AI-powered personalized recommendations |
| **Lineups** | Hero lineup builder for rallies and events |
| **Save/Load** | Multi-profile management |
| **Packs** | Pack value analysis with Frost Star valuation |
| **Events** | Event calendar and optimization |
| **Combat** | SvS/combat stat source guide |
| **Quick Tips** | Consolidated cheat sheet of key game knowledge |
| **Battle Tactics** | Advanced battle strategies |
| **Daybreak Island** | Tree of Life and decoration priorities |
| **Settings** | User profile and priority configuration |

### Admin Pages (System Management)
| Page | Description |
|------|-------------|
| **Dashboard** | System overview with key metrics |
| **Users** | User CRUD, suspend/activate, impersonation |
| **Announcements** | System-wide notification management |
| **Feature Flags** | Toggle features on/off (8 default flags) |
| **Database** | Database browser and table management |
| **Feedback** | User feedback collection inbox |
| **Game Data** | Game data file management |
| **Data Integrity** | Data validation and consistency checks |
| **Usage Reports** | Analytics and user engagement metrics |
| **Export** | Data export (CSV, Excel, JSON formats) |

## Key Game Mechanics

### Rally Joiner System
When joining a rally, only the **leftmost hero's top-right expedition skill** applies. The top 4 highest LEVEL skills from all joiners are used.

**Best Attack Joiners**: Jessie (+25% DMG), Jeronimo (Infantry ATK)
**Best Defense Joiners**: Sergey (-20% DMG taken)

### Daybreak Island
Combat stats come from **Battle Enhancer Decorations**, not just Tree of Life:
- Mythic decorations: 10 levels × 1% = **10% max** (Floating Market, Snow Castle, etc.)
- Epic decorations: 5 levels × 0.5% = **2.5% max**

### SvS Prep Phase
**SPEEDUPS ONLY GIVE POINTS ON DAY 1, 2, AND 5**
- Fire Crystals: 2,000 pts each (Day 1)
- Lucky Wheel: 8,000 pts per spin (Day 2/3)
- Mithril: 40,000 pts each (Day 4)

## Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: Claude (Anthropic) or OpenAI API (optional)
- **OCR**: EasyOCR (optional)
- **Data**: 59 JSON files covering all game systems

## Project Structure

```
WoS/
├── app.py                    # Main entry point
├── pages/                    # 12 Streamlit pages (5,100+ lines)
├── database/                 # SQLAlchemy models and DB management
├── data/                     # 59 JSON data files
│   ├── heroes.json           # All hero data
│   ├── guides/               # Strategy guides
│   ├── optimizer/            # Decision engine config
│   └── upgrades/             # Upgrade edge graphs (920+ edges)
├── assets/heroes/            # 56 hero portrait images
├── engine/                   # Recommendation engines
│   ├── recommendation_engine.py  # Main orchestrator
│   └── analyzers/            # HeroAnalyzer, GearAdvisor, PowerOptimizer, etc.
├── scripts/                  # Data building utilities
├── styles/                   # CSS styling
└── .claude/skills/           # 5 Claude Code skills
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/) - Hero data and images
- [WhiteoutData](https://whiteoutdata.com/) - Game mechanics
- [WhiteoutSurvival.app](https://whiteoutsurvival.app/) - FC building data
- [Quackulator](https://www.quackulator.com/) - Cost calculators
- [AllClash](https://www.allclash.com/) - Tier list information
