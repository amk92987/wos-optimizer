# Bear's Den - TODO List

## Active TODO

### Content / Research
- [ ] **State Transfer Guide** - Add to Quick Tips or new section
  - Individual state transfers and full alliance transfers
  - How many transfer passes needed (reportedly 4?)
  - Requirements, cooldowns, restrictions
  - Research and verify mechanics before adding

- [ ] **Century Games Announcements / Timeline Tracker** - Track upcoming events and state milestones
  - State transfer opening dates and requirements
  - Upcoming events and release schedule
  - What opens at which state age / server milestone
  - Sources: official announcements, patch notes, World Chat intel
  - May need new data sources beyond existing research skill registry

### UI / Frontend
- [ ] **Legendary Gear Level Logic on Hero Tracker** - Rethink gear editing UX
  - Gear must be at level 100 before it can be upgraded to Legendary quality
  - Once Legendary, levels reset and go up from there (Legendary level progression)
  - Current UI doesn't enforce this — selecting Legendary should handle the level transition correctly
  - Research data in `data/raw/gear_enhancement.research.json`

- [ ] **Gear Power Contribution to Lineups** - Incorporate gear stats into lineup scoring
  - Understand how gear adds power/stats to heroes
  - Factor gear quality + level into lineup recommendations
  - Currently lineup engine only considers hero level/stars/skills, not gear

### Repo Cleanup
- [ ] **Remove Legacy Streamlit Code** - Dead code from pre-serverless era
  - **Phase 1 (Quick wins)**: Delete clearly dead directories/files
    - `app.py`, `config.py`, `requirements.txt`, `nul` (root files)
    - `pages/` (32 old Streamlit pages, ~230KB)
    - `auth_pages/` (old auth pages, ~8KB)
    - `styles/` (Streamlit CSS, ~50KB)
    - `.streamlit/` (Streamlit config)
    - `deploy/` (old Lightsail Docker/Nginx, ~20KB)
    - `static/` (old landing page, ~5KB)
  - **Phase 2 (Deeper cleanup)**: Remove replaced code
    - `engine/` (replaced by `backend/engine/`, ~60KB)
    - `database/` (replaced by `backend/common/`, ~50KB)
    - `api/` (abandoned React FastAPI prototype, ~80KB)
    - `ocr/` (disabled feature, ~2KB)
    - `utils/` (Streamlit helpers — keep `email.py` if needed, ~30KB)
    - `export_data/` (one-time migration artifacts, ~330KB)
  - **Phase 3 (Optional)**: IDE/media cleanup
    - `.idea/` (PyCharm config)
    - `Screenshots/` (old Streamlit screenshots, ~1.5MB)
  - **Scripts to remove** (in `scripts/`):
    - `add_ai_limit_column.py`, `export_data.py`, `export_postgres.py`
    - `import_data.py`, `migrate_data.py`, `migrate_dynamodb.py`, `migrate_to_dynamodb.py`
    - `setup_cognito_users.py`, `compare_engine_to_ai.py`, `update_claude_answers.py`
    - `prompt_test_results.json`, `start_frontend.bat`
  - **Scripts to keep**: `download_hero_images.py`, `build_*_edges.py`, `compute_gem_costs.py`,
    `run_data_audit.py`, `run_qa_check.py`, `seed_reference_data.py`, `tag_hero_effects.py`,
    `test_ai_comprehensive.py`, `test_lineups.py`, `create_admin.py`
  - Total cleanup: ~2.5MB of dead code

## Recently Completed

### Feb 2026 - Upgrade Calculators & Data Fixes
- [x] Build Unified Upgrade Calculators tab with 6 calculators (Enhancement, Legendary, Mastery, Chief Gear, Charms, War Academy)
- [x] Chief Gear + Charms calculators show stat bonus % gains
- [x] War Academy calculator with FC prereqs, build times, power gains, milestone breakdown
- [x] Fix charm bonus percentages in Chief Tracker (14 of 16 values were wrong)
- [x] Add 4 missing Pink T4 chief gear tiers (43-46) to Chief Tracker
- [x] Fix admin dashboard trend charts (field name mismatch: `historical` not `data_points`)
- [x] Fix underscore display in recommendation Resources text
- [x] Enhance Crazy Joe Battle Tactics page: fix 21→20 waves, add no-troop-loss note, shields/teleport/training warnings, rewards section
- [x] Crazy Joe research saved to `data/raw/crazy_joe.research.json`
- [x] Verify combat priority system (3/4 priorities confirmed working in rules engine)
- [x] Update research data: hero gear XP table (73,320 total), charm power values for L12-16

### Feb 2026 - UI Polish & Fixes
- [x] Combat priorities refactor: 5 → 4 (PvP Attack, Defense, PvE, Economy) with arctic-themed sliders and consistent ice-blue Playstyle buttons
- [x] Frost/arctic theme enhancements (ice shield avatar, sidebar glow, frost dividers, card hover, page title glow, frosted dropdown, snowflake visibility)
- [x] Hero info popout button on My Heroes tab (reuses HeroDetailModal)
- [x] Fix event type underscores on Events page (alliance_pve → Alliance Pve)
- [x] Fix Crazy Joe data (20 phases not 21, biweekly not daily, 2 battles per occurrence)
- [x] Fix loading screen bear paw box-shadow artifact
- [x] Code review pass: removed dead CSS, fixed hero info guard, added useGamePhase error logging, reverted card hover

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
