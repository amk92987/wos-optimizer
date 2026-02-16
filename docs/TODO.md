# Bear's Den - TODO List

## Active TODO

### UI / Frontend
- [ ] **Rethink Combat Priority Settings** - SvS, Castle Battle, and Rally are redundant
  - Currently 5 priorities: SvS, Rally, Castle Battle, Exploration, Gathering
  - SvS/Castle/Rally are essentially the same combat activity
  - Need new categories that actually differentiate playstyles
  - Used by: hero_analyzer, gear_advisor, recommender, ai_recommender
  - Discuss approach before implementing

- [ ] **Admin Dashboard Trend Charts** - Charts not showing data

- [ ] **Legendary Gear Level Logic on Hero Tracker** - Rethink gear editing UX
  - Gear must be at level 100 before it can be upgraded to Legendary quality
  - Once Legendary, levels reset and go up from there (Legendary level progression)
  - Current UI doesn't enforce this — selecting Legendary should handle the level transition correctly
  - Research gear enhancement mechanics to get the exact flow right

- [ ] **Gear Power Contribution to Lineups** - Incorporate gear stats into lineup scoring
  - Understand how gear adds power/stats to heroes
  - Factor gear quality + level into lineup recommendations
  - Currently lineup engine only considers hero level/stars/skills, not gear

### Backend / Engine
- [ ] **Full Code Review Pass** - Audit all recent combat/daybreak/estimator changes
  - Check for dead code, type mismatches, edge cases
  - Verify all API endpoints return expected shapes

## Recently Completed

### Feb 2026 - UI Polish & Fixes
- [x] Frost/arctic theme enhancements (ice shield avatar, sidebar glow, frost dividers, card hover, page title glow, frosted dropdown, snowflake visibility)
- [x] Hero info popout button on My Heroes tab (reuses HeroDetailModal)
- [x] Fix event type underscores on Events page (alliance_pve → Alliance Pve)
- [x] Fix Crazy Joe data (20 phases not 21, biweekly not daily, 2 battles per occurrence)
- [x] Fix loading screen bear paw box-shadow artifact

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
