# Bear's Den - Whiteout Survival Optimizer

A comprehensive web app to help Whiteout Survival players track heroes, manage resources, and get personalized upgrade recommendations optimized for SvS and combat.

**Live**: [wos.randomchaoslabs.com](https://wos.randomchaoslabs.com)
**Dev**: [wosdev.randomchaoslabs.com](https://wosdev.randomchaoslabs.com)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| **Backend** | Python 3.13, AWS Lambda (10 functions) |
| **Database** | Amazon DynamoDB (3 tables) |
| **Auth** | Amazon Cognito |
| **Infra** | AWS SAM (CloudFormation), API Gateway HTTP API |
| **CDN** | CloudFront + S3 (static hosting) |
| **AI** | OpenAI / Claude API (optional, for AI Advisor) |
| **IaC** | `infra/template.yaml` (SAM template) |

## Project Structure

```
wos-optimizer/
├── frontend/                 # Next.js application
│   ├── app/                  # Pages (App Router)
│   │   ├── heroes/           # Hero Tracker
│   │   ├── chief/            # Chief Gear & Charms Tracker
│   │   ├── upgrades/         # Upgrade Recommendations & Gear Calculator
│   │   ├── advisor/          # AI Advisor chat
│   │   ├── lineups/          # Lineup Builder
│   │   ├── admin/            # Admin panel (10+ pages)
│   │   └── ...               # Other pages
│   ├── components/           # Shared React components
│   │   ├── hero/             # Hero card sub-components
│   │   ├── AppShell.tsx      # Layout shell with header/sidebar
│   │   ├── HeroCard.tsx      # Expandable hero card
│   │   ├── Sidebar.tsx       # Navigation sidebar
│   │   └── ...
│   ├── hooks/                # Custom React hooks
│   │   └── useAutoSave.ts    # Debounced auto-save hook
│   └── lib/                  # Utilities
│       ├── api.ts            # API client (all backend calls)
│       └── auth.tsx          # Auth context (Cognito)
│
├── backend/                  # Lambda function code
│   ├── handlers/             # Lambda entry points
│   │   ├── auth.py           # Login, register, password reset
│   │   ├── heroes.py         # Hero CRUD, roster management
│   │   ├── profiles.py       # Profile CRUD, settings
│   │   ├── chief.py          # Chief gear & charms
│   │   ├── recommendations.py # Upgrade recommendations
│   │   ├── advisor.py        # AI Advisor (rules + AI)
│   │   ├── admin.py          # Admin panel (users, flags, audit, etc.)
│   │   ├── general.py        # Announcements, inbox, search, unread count
│   │   ├── cleanup.py        # Scheduled cleanup (expired sessions, etc.)
│   │   └── user_migration.py # Cognito post-confirmation trigger
│   ├── common/               # Shared backend code
│   │   ├── dynamo_repo.py    # DynamoDB data access layer
│   │   ├── admin_repo.py     # Admin-specific data access
│   │   ├── ai_repo.py        # AI conversation logging
│   │   ├── auth.py           # JWT/Cognito auth utilities
│   │   └── config.py         # Environment config
│   └── engine/               # Recommendation engine
│       ├── recommendation_engine.py  # Main orchestrator
│       ├── ai_recommender.py         # AI provider integration
│       └── analyzers/                # Specialized analyzers
│           ├── hero_analyzer.py      # Hero upgrade logic
│           ├── gear_advisor.py       # Gear priority logic
│           ├── lineup_builder.py     # Event lineup builder
│           ├── progression_tracker.py # Game phase detection
│           └── request_classifier.py  # Routes questions to rules vs AI
│
├── infra/                    # Infrastructure as Code
│   ├── template.yaml         # SAM template (all AWS resources)
│   ├── samconfig.toml        # SAM deploy config (dev/live profiles)
│   └── url-rewrite.js        # CloudFront URL rewrite function
│
├── data/                     # Game data (JSON files)
│   ├── heroes.json           # Hero reference data (AUTHORITATIVE)
│   ├── chief_gear.json       # Chief gear progression
│   ├── guides/               # Strategy guide data
│   ├── optimizer/            # Decision engine config
│   ├── upgrades/             # Upgrade cost edge graphs (920+ edges)
│   └── ai/                   # AI knowledge base
│
├── scripts/                  # Build & deploy scripts
│   ├── deploy_dev.ps1        # Deploy to dev environment
│   ├── deploy_live.ps1       # Deploy to production
│   ├── download_hero_images.py
│   └── build_*.py            # Data building scripts
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md       # System architecture
│   ├── SAM_DEPLOYMENT.md     # AWS deployment guide
│   └── ...
│
│── # Legacy (Streamlit era - kept for reference)
├── app.py                    # Old Streamlit entry point
├── pages/                    # Old Streamlit pages
├── database/                 # Old SQLAlchemy models
├── engine/                   # Old recommendation engine (root copy)
├── config.py                 # Old Streamlit config
└── requirements.txt          # Old Python dependencies
```

## Features

### Player Tools
- **Hero Tracker** - Track all 56+ heroes (Gen 1-14) with inline editing for level, stars, skills, gear
- **Chief Tracker** - Chief gear and charms progression tracking
- **Upgrade Recommendations** - Personalized upgrade priorities based on spending profile and game phase
- **Gear Cost Calculator** - Exact material costs for hero gear upgrades
- **AI Advisor** - Chat-based advisor using rules engine (92%+) with AI fallback
- **Lineup Builder** - Optimal lineups for Bear Trap, Crazy Joe, Garrison, SvS, and more
- **Profiles** - Multiple game profiles with auto-save

### Strategy Guides
- Beginner Guide, Combat Optimization, Quick Tips, Battle Tactics, Daybreak Island, Events

### Admin Panel
- User management with impersonation
- Feature flags, announcements, audit log
- Data browser, integrity checks, usage reports
- Error tracking with in-app badge notifications
- AI conversation review and training data curation

## Development

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.13+ (backend)
- AWS CLI + SAM CLI (deployment)

### Local Frontend Development
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

### Deploy to Dev
```powershell
# Full deploy (backend + frontend)
.\scripts\deploy_dev.ps1

# Backend only
.\scripts\deploy_dev.ps1 -BackendOnly

# Frontend only
.\scripts\deploy_dev.ps1 -FrontendOnly
```

### Key Configuration
- SAM config: `infra/samconfig.toml` (profiles: default=dev, live=live)
- Frontend env: `frontend/.env.local` (API URL, Cognito pool)
- Backend config: Environment variables set in SAM template

## Architecture

```
User Browser
     |
     v
CloudFront (CDN + SPA routing)
     |
     +---> S3 Bucket (Next.js static export)
     |
     +---> API Gateway HTTP API (/api/*)
               |
               v
          10 Lambda Functions
               |
               v
          DynamoDB (3 tables)
               |
               +---> wos-main-{env}      (users, profiles, heroes, AI conversations)
               +---> wos-admin-{env}     (flags, feedback, errors, audit log)
               +---> wos-reference-{env} (game data cache)
```

## Data Sources

- [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/) - Hero data, game mechanics
- [WhiteoutSurvival.app](https://whiteoutsurvival.app/) - FC building costs
- [WhiteoutData](https://whiteoutdata.com/) - Building costs L1-L30
- [Quackulator](https://www.quackulator.com/) - Chief gear costs
- [AllClash](https://www.allclash.com/) - Community tier lists

## License

MIT License
