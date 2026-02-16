# Bear's Den - TODO List

## Active TODO

### UI / Frontend
- [ ] **Frost/Arctic Theme Enhancements** - Subtle UI polish across the app
  - Tasteful frost/ice accents where appropriate (not overwhelming)
  - Slight improvements to card borders, hover effects, gradient accents
  - Consider frosted glass effects on key panels

- [ ] **Rethink Combat Priority Settings** - SvS, Castle Battle, and Rally are redundant
  - Currently 5 priorities: SvS, Rally, Castle Battle, Exploration, Gathering
  - SvS/Castle/Rally are essentially the same combat activity
  - Need new categories that actually differentiate playstyles
  - Used by: hero_analyzer, gear_advisor, recommender, ai_recommender
  - Discuss approach before implementing

- [ ] **Admin Dashboard Trend Charts** - Charts not showing data
  - Fix when dev environment is set up

### Backend / Engine
- [ ] **Full Code Review Pass** - Audit all recent combat/daybreak/estimator changes
  - Check for dead code, type mismatches, edge cases
  - Verify all API endpoints return expected shapes

### Infrastructure
- [ ] **Set Up Fresh Dev Environment** - Deploy new `wos-dev` stack
  - New DynamoDB tables, Cognito pool, CloudFront distribution
  - Move `wosdev.randomchaoslabs.com` alias to new distribution
  - Remove `wosdev` alias from current (live) distribution

- [ ] **Create App Icons** - PWA icons for mobile
  - manifest.json references icon-192.png and icon-512.png that don't exist
  - Generate from bear logo

### Auth / Security
- [ ] **Forgot Password Flow** - Add password reset via email
  - Add "Forgot Password?" link on login page
  - Generate secure reset tokens
  - Send password reset email

- [ ] **Email Verification on Signup** - Enforce email verification
  - `is_verified` field exists but not enforced
  - Block login until verified (or grace period)

## Recently Completed

### Feb 2026 - Battle Enhancement Features
- [x] Add "12 Combat Stats" education content (Stats & Sources tab)
- [x] Add stat source breakdown (7 sources mapped to 12 stats)
- [x] Add Daybreak decoration combat stat impact calculator
- [x] Add Tree of Life universal buff summary
- [x] Add stat-balance awareness to gear advisor (weakest-stat prioritization)
- [x] Add `GET /api/recommendations/stat-insights` endpoint
- [x] Build Battle Estimator with stat input, opponent comparison, advantage ratios
- [x] What-If mode with preset bonuses (Mythic Deco, Pet, Tree of Life)
- [x] Real battle data reference panel (158k vs 183k troop example)
- [x] Merge combat page from 6 tabs to 4 (Combat Audit, Stats & Sources, Battle Estimator, Phase Priorities)
- [x] Pre-populate Battle Estimator from stat-insights API (gear/charm data)
- [x] Cross-links between Combat and Daybreak pages
- [x] Auto-expand correct game phase based on user's furnace level
- [x] Fix API shape mismatch in Battle Estimator pre-population
- [x] Fix broken border-l-3 / borderLeftColor CSS in milestone cards
- [x] Fix misleading "Both Mythic Decos" preset (split into honest individual presets)
- [x] Remove dead GEAR_QUALITY_APPROX constant
- [x] Add Alonso to Battle Tactics page
- [x] Add battle mechanics & combat stats to WOS_REFERENCE.md
- [x] Overhaul lineup scoring with pre-tagged hero effects (179 effects, 56 heroes)

### Feb 2026 - AWS Serverless Migration
- [x] Migrate from Streamlit + Lightsail to Next.js + AWS Serverless
- [x] Set up CloudFront + S3 + API Gateway + Lambda + DynamoDB + Cognito
- [x] Promote dev stack to live at wos.randomchaoslabs.com
- [x] Shut down all Lightsail instances
- [x] Merge `feature/aws-serverless` into `master`

### Jan 2026 - Events & Battle Tactics Update
- [x] Add Mercenary Prestige, Brother In Arms, Tundra Arms League, Frostdragon Tyrant, Tundra Album, Alliance Championship events
- [x] Fix Alliance Championship mechanics (pick 3 heroes, 50/20/30 ratio)
- [x] Organize Events page with category tabs
- [x] Move Labyrinth section from Lineups to Battle Tactics
- [x] Add error logging system

### Jan 2026 - Donate, Feedback, Chat History
- [x] Ko-fi donate button in user menu
- [x] Feedback form with AI Advisor hint
- [x] AI Advisor chat history, "New Chat", "Past Chats"
- [x] Chat threading and favorites/bookmarks
- [x] Full user snapshot in conversation logs

### Jan 2026 - Auth, Admin, AI Systems
- [x] User registration, login, password/email change
- [x] Admin system (10 management pages)
- [x] AI Advisor with rules engine (92%+) and OpenAI fallback
- [x] PWA manifest, mobile install banner

## Backlog (Lower Priority)

- [ ] **CAPTCHA / Login Protection** - Rate limiting, brute-force protection
- [ ] **Service Worker** - Offline support, cache static assets
- [ ] **Push Notifications** - Server-to-client notifications

## Infrastructure

### Environments
| Environment | URL | Stack |
|-------------|-----|-------|
| Local Dev | localhost:3000 | Next.js dev server |
| Dev | wosdev.randomchaoslabs.com | SAM `wos-dev` (needs fresh deploy) |
| Live | wos.randomchaoslabs.com | SAM `wos-live` |

### Deployment
```bash
# Deploy to Live (frontend + backend)
cd infra && sam build && sam deploy --config-env live --no-confirm-changeset
cd ../frontend && npm run build && aws s3 sync out s3://wos-frontend-live-561893854848 --delete
aws cloudfront create-invalidation --distribution-id E1AJ7LCWTU8ZMH --paths "/*"

# Or use the deploy script (PowerShell)
./scripts/deploy_dev.ps1  # Dev
./scripts/deploy_dev.ps1 -BackendOnly  # Backend only
```

### Key Resources
- CloudFront (live): `E1AJ7LCWTU8ZMH` -> `wos.randomchaoslabs.com`
- API Gateway (live): `jbz4lfpfm5.execute-api.us-east-1.amazonaws.com/live`
- S3 Frontend (live): `wos-frontend-live-561893854848`
- DynamoDB (live): `wos-main-live`, `wos-admin-live`, `wos-reference-live`
- Cognito (live): `us-east-1_RmBIg1Flh`

## Notes

- Database: DynamoDB (serverless, per-environment tables)
- Auth: AWS Cognito (email-based)
- AI: Claude/OpenAI for AI recommendations, rules engine handles 92%+
- Frontend: Next.js 14 static export + Tailwind CSS
- Backend: Python 3.13 Lambda functions via SAM
