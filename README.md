# Whiteout Survival Optimizer

A web-based tool to help Whiteout Survival players track their heroes, manage inventory, and get personalized upgrade recommendations optimized for SvS and combat.

## Features

### Hero Management
- Track all heroes from Gen 1-10 with detailed stats
- Visual hero cards with tier badges, rarity borders, and class symbols
- Inline editing for level, stars, ascension, skills, and gear
- Partial star progress tracking (ascension tiers)
- Hero gear tracking (4 slots + mythic gear)

### Gear System
- Track 4 gear slots per hero (Weapon, Armor, Helmet, Boots)
- Quality levels: Gray, Green, Blue, Purple, Orange, Mythic
- Mythic hero gear support (e.g., Jeronimo's Dawnbreak)
- Quality-based max level caps

### Recommendations
- Priority-based upgrade recommendations
- AI-powered advisor (requires OpenAI API key)
- Combat-focused analysis for SvS optimization

### User Profile
- Server age and generation tracking
- Priority settings for SvS, Rally, Castle Battle, PvE, Gathering
- Furnace level tracking

## Screenshots

*Coming soon*

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

4. (Optional) Set OpenAI API key for AI recommendations:
```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Unix/macOS
export OPENAI_API_KEY=your-key-here
```

5. Run the application:
```bash
streamlit run app.py
```

6. Open http://localhost:8501 in your browser

## Usage

### Heroes Page
1. Browse all heroes by generation
2. Filter by generation, class, or tier
3. Click "Edit" to expand the inline editor
4. Set level, stars, ascension, skills, and gear
5. Click "Save" to store your hero data

### Star/Ascension System
- Stars: 0-5 (heroes start with 0 stars)
- Ascension: 0-5 tiers within each star
- When you'd reach ascension 6, you gain the next star instead
- At 5 stars, ascension is maxed out

### Gear Quality
| Quality | Color | Max Level |
|---------|-------|-----------|
| Gray | Silver | 20 |
| Green | Green | 40 |
| Blue | Blue | 60 |
| Purple | Purple | 80 |
| Orange | Orange | 100 |
| Mythic | Pink | 120 |

### Settings Page
Configure your priorities to get personalized recommendations:
- SvS priority (1-5)
- Rally priority (1-5)
- Castle Battle priority (1-5)
- Exploration/PvE priority (1-5)
- Gathering priority (1-5)

## Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: OpenAI API (optional)
- **OCR**: EasyOCR (optional, for screenshot parsing)

## Project Structure

```
WoS/
├── app.py                    # Main entry point
├── database/
│   ├── models.py             # SQLAlchemy models
│   └── db.py                 # Database management
├── data/
│   └── heroes.json           # Hero data (tiers, skills, etc.)
├── engine/
│   ├── recommender.py        # Recommendation engine
│   └── ai_recommender.py     # AI-powered recommendations
├── pages/
│   ├── 1_Heroes.py           # Hero management
│   ├── 2_Backpack.py         # Inventory tracking
│   ├── 3_Recommendations.py  # Upgrade recommendations
│   ├── 4_Settings.py         # User settings
│   └── 5_AI_Advisor.py       # AI advisor
├── styles/
│   └── custom.css            # Custom styling
└── utils/
    └── image_downloader.py   # Hero image downloader
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/) for game data
- [AllClash](https://www.allclash.com/) for tier list information
- [WhiteoutData](https://whiteoutdata.com/) for additional resources
