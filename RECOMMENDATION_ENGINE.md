# Rule-Based Recommendation Engine

This document describes the architecture and implementation of the WoS Optimizer's recommendation engine. The engine uses curated game knowledge to provide instant, accurate recommendations without requiring AI API calls for most cases.

## Philosophy

**Core Principle:** We have extensive, accurate game knowledge in our data files. Use it directly rather than asking an AI to "figure it out."

**AI Role:** Fallback for complex questions, edge cases, and conversational follow-ups - not the primary recommendation source.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Request                                │
│              "What should I upgrade next?"                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Request Classifier                            │
│                                                                  │
│  Determines if request can be answered by rules or needs AI:    │
│  - "upgrade priority" → RULES                                   │
│  - "best rally team" → RULES                                    │
│  - "should I buy this pack?" → AI (complex/contextual)          │
│  - "what if I swap X for Y" → AI (hypothetical)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌──────────────────────┐        ┌──────────────────────┐
│   Rule Engine        │        │   AI Fallback        │
│                      │        │                      │
│ - Hero Analyzer      │        │ - Claude API         │
│ - Gear Advisor       │        │ - OpenAI API         │
│ - Lineup Builder     │        │ - Full context       │
│ - Progression Tracker│        │ - Conversational     │
└──────────────────────┘        └──────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Response Formatter                               │
│         Consistent output regardless of source                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Status

### Completed Modules

| Module | Location | Status |
|--------|----------|--------|
| Request Classifier | `engine/analyzers/request_classifier.py` | ✅ Complete |
| Hero Analyzer | `engine/analyzers/hero_analyzer.py` | ✅ Complete |
| Gear Advisor | `engine/analyzers/gear_advisor.py` | ✅ Complete |
| Lineup Builder | `engine/analyzers/lineup_builder.py` | ✅ Complete |
| Progression Tracker | `engine/analyzers/progression_tracker.py` | ✅ Complete |
| Main Engine | `engine/recommendation_engine.py` | ✅ Complete |
| AI Fallback | `engine/ai_recommender.py` | ✅ Complete (Claude + OpenAI) |
| UI Integration | `pages/5_AI_Advisor.py` | ✅ Complete |

---

## Module Details

### 1. Request Classifier (`engine/analyzers/request_classifier.py`)

**Purpose:** Determine if a request can be handled by rules or needs AI.

**Classification Types:**
- `RULES` - Can be fully answered with game rules
- `AI` - Needs contextual AI analysis
- `HYBRID` - Try rules first, enhance with AI if needed

**Rule Patterns (routed to rules engine):**
```python
- "what should i upgrade/level/focus" → hero_analyzer
- "best lineup/team/composition" → lineup_builder
- "bear trap/crazy joe/rally" → lineup_builder
- "chief/hero gear" → gear_advisor
- "jessie/sergey" → hero_analyzer (joiner heroes)
- "early/mid/late game" → progression_tracker
```

**AI Patterns (routed to AI):**
```python
- "what if" → hypothetical questions
- "should i buy/spend/invest" → spending decisions
- "compare X vs Y" → comparisons
- "explain/why" → explanations
- "is it worth" → value judgments
```

---

### 2. Hero Analyzer (`engine/analyzers/hero_analyzer.py`)

**Purpose:** Analyze user's heroes and recommend upgrades based on level gaps, skill gaps, and generation relevance.

**Rules Implemented:**

| Rule ID | Condition | Recommendation |
|---------|-----------|----------------|
| `level_main_three` | < 3 heroes at level 40+ | Focus on leveling main 3 heroes first |
| `unlock_jessie` | Rally priority ≥ 3, Jessie not owned | Unlock Jessie (best attack joiner) |
| `level_jessie_skill` | Jessie owned, expedition skill < 5 | Max Jessie's Stand of Arms skill |
| `unlock_sergey` | Castle priority ≥ 3, Sergey not owned | Unlock Sergey (best defense joiner) |
| `level_sergey_skill` | Sergey owned, expedition skill < 5 | Max Sergey's Defenders' Edge skill |
| `acquire_genX` | No heroes from current/recent gen | Acquire generation-appropriate heroes |
| `upgrade_expedition_skill` | Rally priority ≥ 3, skill < 5 | Upgrade expedition skills for PvP |
| `upgrade_exploration_skill` | PvE priority ≥ 3, skill < 5 | Upgrade exploration skills for PvE |
| `ascend_stars` | High-tier hero, stars < 5, level ≥ 40 | Ascend hero for stat boost |

**Generation Relevance Scoring:**
```python
gen_diff = current_gen - hero_gen
if gen_diff <= 0: return 1.0   # Current/future gen
elif gen_diff == 1: return 0.9  # Still very relevant
elif gen_diff == 2: return 0.7  # Moderately relevant
elif gen_diff == 3: return 0.5  # Getting outdated
else: return 0.3                # Very old
```

**Joiner Heroes (Verified Mechanics):**
```python
JOINER_HEROES = {
    "attack": {
        "hero": "Jessie",
        "skill": "Stand of Arms",
        "effect_per_level": [5, 10, 15, 20, 25],  # % DMG dealt
    },
    "defense": {
        "hero": "Sergey",
        "skill": "Defenders' Edge",
        "effect_per_level": [4, 8, 12, 16, 20],   # % DMG reduction
    }
}
```

---

### 3. Gear Advisor (`engine/analyzers/gear_advisor.py`)

**Purpose:** Recommend chief gear and hero gear upgrades using spender-aware rules.

**Chief Gear Priority Order:**
| Priority | Slot | Stat | Reason |
|----------|------|------|--------|
| 1 | Ring | Troop Attack (All) | Universal attack buff for ALL troops |
| 2 | Amulet | Lethality/Damage | PvP decisive - affects kill rates |
| 3 | Gloves | Marksman Attack | Boosts marksman heroes |
| 4 | Boots | Lancer Attack | Boosts lancer heroes |
| 5 | Helmet | Infantry Defense | Defensive - less impactful |
| 6 | Armor | Infantry Health | Defensive - least priority |

**Hero Gear Limits by Spender Type:**
```python
HERO_GEAR_LIMITS = {
    "f2p": {
        "allowed_count": 1,
        "targets": ["Molly", "Alonso"],
        "avoid": ["Jessie", "Sergey", "any joiner hero"]
    },
    "low_spender": {
        "allowed_count": 2,
        "targets": ["Alonso", "Jeronimo", "Molly"],
    },
    "medium_spender": {
        "allowed_count": 4,
        "targets": ["Jeronimo", "Alonso", "Molly", "situational"],
    },
    "whale": {
        "allowed_count": 999,  # No limit
        "targets": ["all core heroes"],
    }
}
```

**Common Mistake Detection:**
- Hero gear before Ring/Amulet at Legendary
- Gearing joiner heroes (Jessie/Sergey)
- Upgrading defensive gear before attack gear

---

### 4. Lineup Builder (`engine/analyzers/lineup_builder.py`)

**Purpose:** Recommend optimal lineups based on owned heroes for each game mode.

**Supported Game Modes:**
| Mode Key | Description |
|----------|-------------|
| `rally_joiner_attack` | Joining attack rallies |
| `rally_joiner_defense` | Reinforcing garrison |
| `bear_trap` | Bear Trap boss rally |
| `crazy_joe` | Crazy Joe boss rally |
| `garrison` | Castle defense |
| `exploration` | PvE/Frozen Stages |
| `svs_march` | SvS field combat |

**Lineup Structure:**
```python
{
    "mode": "Bear Trap Rally",
    "heroes": [
        {"slot": "Lead", "hero": "Jeronimo", "role": "DPS Lead", "your_status": "Lv45"},
        {"slot": "Slot 2", "hero": "Molly", "role": "AOE DPS", "your_status": "Lv40"},
        {"slot": "Slot 3", "hero": "Alonso", "role": "DPS Support", "your_status": "Not owned"}
    ],
    "troop_ratio": {"infantry": 0, "lancer": 10, "marksman": 90},
    "notes": "Bear is slow. Maximize marksman DPS. Infantry not needed.",
    "confidence": "medium"  # Based on hero availability
}
```

**Joiner Recommendation Logic:**
```python
def get_joiner_recommendation(user_heroes, attack=True):
    # For attack: Jessie > Jeronimo
    # For defense: Sergey > Natalia
    # If no good joiner: "Remove all heroes, send troops only"
```

---

### 5. Progression Tracker (`engine/analyzers/progression_tracker.py`)

**Purpose:** Identify player's current game phase and provide phase-specific tips.

**Phases:**
| Phase | Furnace | Server Age | Focus |
|-------|---------|------------|-------|
| Early Game | 1-18 | 0-54 days | Rush Furnace to L19, unlock Research Center |
| Mid Game | 19-29 | 55-199 days | Push to L30, develop pets/charms |
| Late Game | 30 (FC1-FC5) | 200-400 days | FC progression, War Academy |
| Endgame | FC5+ | 400+ days | Optimization, FC10 completion |

**Phase Detection:**
```python
def detect_phase(profile):
    if furnace_level < 19:
        return "early_game"
    elif furnace_level < 30:
        return "mid_game"
    elif fc_level < 5:
        return "late_game"
    else:
        return "endgame"
```

**Milestone Tracking:**
```python
milestones = [
    {"level": 9, "name": "Research Center"},
    {"level": 18, "name": "Pets Prep"},
    {"level": 19, "name": "Daybreak Island"},
    {"level": 25, "name": "Chief Charms"},
    {"level": 30, "name": "Fire Crystal Era"},
]
```

---

### 6. Main Engine (`engine/recommendation_engine.py`)

**Purpose:** Orchestrate all analyzers and provide unified API.

**Key Methods:**

```python
class RecommendationEngine:
    def get_recommendations(profile, user_heroes, user_gear=None, limit=10):
        """Get prioritized recommendations from all analyzers."""

    def get_lineup(game_mode, user_heroes, profile=None):
        """Build optimal lineup for a game mode."""

    def get_joiner_recommendation(user_heroes, attack=True):
        """Get specific joiner hero recommendation."""

    def ask(profile, user_heroes, question, force_ai=False):
        """Answer a question using rules or AI."""

    def get_phase_info(profile):
        """Get current progression phase information."""
```

**Usage Example:**
```python
from engine import RecommendationEngine

engine = RecommendationEngine()

# Get recommendations
recs = engine.get_recommendations(profile, user_heroes)

# Get lineup
lineup = engine.get_lineup("bear_trap", user_heroes)

# Ask a question
result = engine.ask(profile, user_heroes, "What should I upgrade next?")
```

---

### 7. AI Fallback (`engine/ai_recommender.py`)

**Supported Providers:**
- **Claude (Anthropic)** - Preferred when available
- **OpenAI (GPT-4o-mini)** - Fallback option

**Auto-Detection:**
```python
# Checks environment variables:
# ANTHROPIC_API_KEY - for Claude
# OPENAI_API_KEY - for OpenAI

recommender = AIRecommender(provider="auto")  # Uses first available
```

**When AI is Used:**
- "What if" hypothetical questions
- "Should I buy/spend" spending decisions
- "Compare X vs Y" comparisons
- "Explain why" requests
- Complex contextual questions

---

## Data Sources

| File | Used By | Contains |
|------|---------|----------|
| `data/heroes.json` | HeroAnalyzer, LineupBuilder | Hero tiers, generations, skills |
| `data/chief_gear.json` | GearAdvisor | Gear priorities, spender paths |
| `data/optimizer/progression_phases.json` | ProgressionTracker | Phase definitions, milestones |
| `data/guides/hero_lineup_reasoning.json` | LineupBuilder | Lineup templates, joiner rules |

---

## UI Integration

The **AI Advisor** page (`pages/5_AI_Advisor.py`) provides:

1. **Recommendations Tab** - Rule-based priorities with category badges
2. **Lineups Tab** - Mode-specific lineup builder with confidence indicator
3. **Ask a Question Tab** - Natural language interface (rules first, AI fallback)
4. **Data Preview Tab** - Shows what gets sent to AI

**Features:**
- Shows current progression phase and next milestone
- Displays whether answer came from rules (instant) or AI
- Category badges (HERO, GEAR, PROGRESSION)
- Confidence indicators for lineups (HIGH/MEDIUM/LOW)

---

## Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Rule response time | < 100ms | ✅ Instant |
| AI response time | 1-3s | ✅ Expected |
| Rule coverage | 80%+ of queries | ✅ Common questions covered |
| Accuracy | Match verified mechanics | ✅ Uses curated data |

---

## Future Enhancements

- [ ] Shop Advisor - "What to buy" recommendations
- [ ] Event Prioritizer - Event-specific guidance
- [ ] Resource Calculator - Upgrade cost estimates
- [ ] A/B testing for rule variations
- [ ] Rule analytics (track which rules fire most)

---

## Notes

- Rules are implemented in code but could be externalized to JSON
- Each rule includes an explanation for transparency
- The system gracefully degrades if AI is unavailable
- Recommendations are deduplicated to avoid repeating similar advice
