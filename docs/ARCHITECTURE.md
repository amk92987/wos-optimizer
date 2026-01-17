# WoS Optimizer Architecture

This document describes the architecture and data flow of the Bear's Den (Whiteout Survival Optimizer) application.

## System Overview

```
+------------------+     +------------------+     +------------------+
|   Streamlit UI   |---->|  Recommendation  |---->|   AI Provider    |
|   (pages/*.py)   |     |  Engine (engine/)|     | (OpenAI/Claude)  |
+------------------+     +------------------+     +------------------+
         |                       |
         v                       v
+------------------+     +------------------+
|  SQLite Database |<----|   Game Data      |
|  (wos.db)        |     |  (data/*.json)   |
+------------------+     +------------------+
```

## Core Components

### 1. Streamlit Application (`app.py`)

Entry point that handles:
- User authentication (login/register/logout)
- Page routing based on user role (admin vs user)
- Session management
- Navigation menus

### 2. Pages (`pages/*.py`)

| Category | Pages | Purpose |
|----------|-------|---------|
| **User Pages** | 0_Home, 00_Beginner_Guide | Welcome and onboarding |
| **Tracker Pages** | 1_Hero_Tracker, 2_Chief_Tracker, 3_Backpack | Game state tracking |
| **Analysis Pages** | 5_Lineups, 6_AI_Advisor | Recommendations and advice |
| **Reference Pages** | 10_Combat, 11_Quick_Tips, 12_Battle_Tactics | Game guides |
| **Settings Pages** | 7_Save_Load, 13_Settings | Profile management |
| **Admin Pages** | 0_Admin_Home through 15_Admin | System management |

### 3. Database Layer (`database/`)

```
database/
├── db.py          # Connection, session management
├── models.py      # SQLAlchemy ORM models
└── auth.py        # Authentication functions
```

**Key Models:**
- `User` - Authentication, roles, rate limiting
- `UserProfile` - Game account settings (furnace, state, priorities)
- `Hero` - Static hero reference data (from heroes.json)
- `UserHero` - User's hero levels, skills, gear
- `UserInventory` - Backpack items
- `AIConversation` - AI Q&A logging for training data

### 4. Recommendation Engine (`engine/`)

```
engine/
├── recommendation_engine.py  # Main orchestrator
├── recommender.py            # Rule-based recommendations
├── ai_recommender.py         # AI-powered recommendations
└── analyzers/
    ├── hero_analyzer.py      # Hero upgrade logic
    ├── gear_advisor.py       # Chief/hero gear priorities
    ├── lineup_builder.py     # Event lineup builder
    ├── progression_tracker.py # Game phase detection
    └── request_classifier.py  # Routes questions to rules vs AI
```

**Data Flow for Recommendations:**

```
User Question
     |
     v
+-------------------+
| Request Classifier|---> Simple question? --> Rules Engine --> Response
+-------------------+                              |
     |                                             v
     | Complex question                     Hero Analyzer
     v                                      Gear Advisor
+-------------------+                       Lineup Builder
|   AI Recommender  |
+-------------------+
     |
     v
+-------------------+
| OpenAI / Claude   |
| (with verified    |
|  game mechanics)  |
+-------------------+
     |
     v
  AI Response
```

### 5. Game Data (`data/`)

**Authoritative Source Files:**

| File | Purpose | Priority |
|------|---------|----------|
| `heroes.json` | Hero stats, generations, skills | **CRITICAL** - always reference for hero data |
| `chief_gear.json` | Chief gear progression | High |
| `events.json` | Event calendar and mechanics | High |
| `guides/quick_tips.json` | Player tips by category | Medium |

**Data Structure:**

```
data/
├── heroes.json              # Hero reference (AUTHORITATIVE)
├── chief_gear.json          # Gear stats
├── events.json              # Event data
├── guides/                  # Strategy guides
│   ├── quick_tips.json      # 15 categories, 79 tips
│   └── hero_lineup_reasoning.json
├── optimizer/               # Decision rules
│   ├── progression_phases.json
│   └── decision_rules.json
├── upgrades/                # Cost data (920+ edges)
│   ├── buildings.edges.json
│   └── war_academy.steps.json
└── ai/                      # AI training data
    └── openai_wos_knowledge.json
```

## Data Flow Diagrams

### User Profile Flow

```
User Logs In
     |
     v
Load UserProfile from DB
     |
     +--> No profile? --> Create default profile
     |
     v
Load UserHeroes (owned heroes with levels)
     |
     v
Load Heroes.json (static hero data)
     |
     v
Merge: UserHero + Hero = Complete hero context
     |
     v
Display in Hero Tracker / Pass to AI Advisor
```

### AI Recommendation Flow

```
User asks question in AI Advisor
     |
     v
Request Classifier analyzes question
     |
     +-- Simple pattern match --> Rules Engine
     |                               |
     |                               v
     |                          Format response
     |                               |
     +-- Complex/unknown -----> AI Recommender
                                    |
                                    v
                              Build user context:
                              - Profile (furnace, spending)
                              - Owned heroes + levels
                              - Priorities (SvS, Rally, etc)
                                    |
                                    v
                              Add VERIFIED_MECHANICS:
                              - HERO_GENERATION_REFERENCE
                              - Rally mechanics
                              - Chief gear rules
                                    |
                                    v
                              Call OpenAI/Claude API
                                    |
                                    v
                              Log to AIConversation table
                                    |
                                    v
                              Return response to user
```

### Lineup Builder Flow

```
User selects event type (Bear Trap, Garrison, etc)
     |
     v
Load user's owned heroes + levels
     |
     v
Load LINEUP_TEMPLATES for event type
     |
     v
For each slot:
  1. Get preferred heroes from template
  2. Filter by user's roster
  3. Rank by: level > stars > gear quality
  4. Select best available
     |
     v
Calculate troop ratios from template
     |
     v
Generate "Why This Lineup" explanations
     |
     v
Display lineup recommendation
```

## Key Architectural Decisions

### 1. Rules Engine First, AI Fallback

92.3% of questions are handled by the rules engine (request_classifier.py). This:
- Reduces API costs
- Provides faster responses
- Ensures consistent answers for common questions

### 2. Verified Mechanics in AI Prompts

The AI prompts include `VERIFIED_MECHANICS` and `HERO_GENERATION_REFERENCE` constants that:
- Prevent hallucination of incorrect data
- Ensure Jessie is always Gen 1 (not Gen 5)
- Provide correct rally joining mechanics

### 3. Single Source of Truth

`data/heroes.json` is the ONLY authoritative source for hero data. All components read from it:
- Hero Tracker displays
- AI Recommender context
- Lineup Builder logic

### 4. Profile Isolation

Each `UserProfile` is independent:
- Users can have multiple profiles (main + farm accounts)
- Profiles can be in different states (servers)
- Farm accounts get different recommendations

## Security Considerations

### Authentication
- Passwords hashed with bcrypt
- Session-based login
- Admin impersonation with tracking

### AI Jailbreak Protection
- Only answers Whiteout Survival questions
- Rejects off-topic requests
- No code generation

### Database
- SQLAlchemy ORM (SQL injection protection)
- Prepared statements only

## Performance Optimizations

### Caching
- Hero images loaded as base64 once per session
- Static data cached in session state

### Database
- Lazy loading for related objects
- Indexed foreign keys

### AI
- Rules engine reduces API calls by 92%
- Response caching for identical questions

## Testing

### Test Profiles
6 test users with 9 profiles covering:
- Different spending profiles (F2P to Whale)
- Different game phases (new player to FC30)
- Farm accounts
- Rally leaders vs fillers

Run tests:
```bash
.venv/Scripts/python.exe scripts/test_ai_comprehensive.py
```

### QA Checks
```bash
.venv/Scripts/python.exe scripts/run_qa_check.py
```

## Deployment

See `deploy/AWS_DEPLOYMENT_CHECKLIST.md` for production deployment guide covering:
- AWS EC2 setup
- RDS database migration
- SSL/HTTPS configuration
- Environment variables

## File Quick Reference

| Need to... | Look in... |
|------------|------------|
| Add a new page | `pages/` - create new file |
| Add a hero | `data/heroes.json` - add to heroes array |
| Change AI behavior | `engine/ai_recommender.py` - update prompts |
| Add recommendation rule | `engine/analyzers/` - modify relevant analyzer |
| Add database model | `database/models.py` - add SQLAlchemy class |
| Add Claude skill | `.claude/skills/` - create new skill folder |
