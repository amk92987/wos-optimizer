# Bear's Den - TODO List

## High Priority

- [x] **Build power optimization into AI Advisor** - Use collected hero stats, troop data, and combat formulas to provide upgrade recommendations

- [x] **Fix Advisor screen** - Fixed: Path handling, FC level parsing, ORM object handling in PowerOptimizer

- [x] **Fix Upgrade Priority page** - Verified working. Requires users to add heroes via Heroes page first (expected behavior)

## UI/UX Improvements

- [x] **Chief gear images are static at Gold T2 3★** - Created 432 color-tinted variations (6 slots x 6 colors x 3 tiers x 4 stars). Images: `assets/chief_gear/tiers/`. Generator: `scripts/generate_gear_images.py`

- [x] **Consider 3 selectors for gear (color, tier, star) vs 1 dropdown** - Implemented 3 cascading selectors with dynamic options based on selection

- [x] **Rename sidebar items to be more precise** - Renamed: Beginner Guide, Hero Tracker, Chief Tracker, AI Advisor, Save Load, Quick Tips, Battle Tactics, Daybreak Island

- [x] **Rename app from "WoS Optimizer" to something fun** - Renamed to "Bear's Den"

- [x] **Get proper backpack images** - Fixed 4 typos (glowstones, marks_of_valor, explosive_arrowheads, legendary_hero_shard). Added emoji fallbacks for 4 missing event currencies (gem_of_enigma, thorns_of_enigma, rocket_v2, fuel_supply_chest)

- [x] **UI improvements** - Added bear paw logo with gradient, content card utilities (.content-card, .info-card, .warning-card, .success-card, .stats-card), improved typography (h1/h2/h3 sizing, h2 bottom border), spacing utilities, table hover effects

## Infrastructure/Deployment

- [x] **Create admin page for usernames/passwords** - User model with bcrypt hashing, Admin page at pages/15_Admin.py, login/logout in sidebar. Default admin: admin/admin123

- [x] **Complete Admin Dashboard System** - Full admin interface with 10 dedicated pages:
  - **Dashboard** (0_Admin_Home.py) - System overview with key metrics
  - **Users** (15_Admin.py) - User management with inline editing, suspend/activate, impersonation
  - **Announcements** (1_Admin_Announcements.py) - System-wide notifications
  - **Audit Log** (2_Admin_Audit_Log.py) - User action tracking
  - **Feature Flags** (3_Admin_Feature_Flags.py) - Toggle features on/off (8 default flags)
  - **Database** (4_Admin_Database.py) - Database browser and management
  - **Feedback** (5_Admin_Feedback.py) - User feedback collection
  - **Game Data** (6_Admin_Game_Data.py) - Game data management
  - **Data Integrity** (7_Admin_Data_Integrity.py) - Data validation tools
  - **Usage Reports** (8_Admin_Usage_Reports.py) - Analytics and metrics
  - **Export** (9_Admin_Export.py) - Data export (CSV/Excel/JSON)

- [x] **User Authentication System** - Complete auth flow:
  - Landing page with login/register links
  - Login page with "Remember me" option
  - Registration page with email validation
  - Session management with impersonation support
  - Password change in user popover menu
  - Role-based navigation (admin vs user views)

- [x] **Admin Impersonation** - "Login as User" feature with:
  - Red banner showing impersonation status
  - "Switch Back" button in banner and user menu
  - Preserves original admin session for return

- [x] **AI Advisor System** - Complete AI integration:
  - Admin toggle: Off / On (rate limited) / Unlimited modes
  - Rate limiting: daily limits, cooldown between requests
  - Conversation logging for training data collection
  - User feedback: thumbs up/down, star ratings
  - Admin curation: mark good/bad examples
  - Training data export (JSONL for fine-tuning, CSV)
  - Jailbreak protection (only answers WoS questions)
  - Game-specific personality: addresses user as "Chief", uses WoS terminology

- [x] **State Number Tracking** - Track players across states:
  - State number field in Settings page
  - State column in Admin Users page with filtering
  - State distribution analytics in Usage Reports
  - State included in User Summary and Content Statistics exports
  - Unique states metric in admin dashboard

- [ ] **Add CAPTCHA or login attempt protection** - Security enhancement

- [x] **Add Donate button** - Ko-fi integration in user menu and homepage. URL: `https://ko-fi.com/randomchaoslabs`

- [x] **Add Feedback System** - Inline feedback form in user menu, detailed form on AI Advisor with "Report Bad Recommendation" option

- [x] **AI Advisor Chat History** - Messages persist within session, "New Chat" button, "Past Chats" section to load previous conversations

- [ ] **Mobile Optimization** - Responsive design, touch-friendly UI, PWA "Save to Home Screen"

- [ ] **Favorite/Bookmark AI Responses** - Let users save helpful answers for quick reference

- [ ] **Conversation Threading** - Group follow-up questions together in Past Chats

- [ ] **Consider moving off Streamlit to AWS** - Major architecture decision for scaling

## Completed

### Jan 2026 - Donate, Feedback, Chat History
- [x] Ko-fi donate button in user menu (deep orange, centered)
- [x] Donate message on Homepage and AI Advisor
- [x] Feedback form in user menu with AI Advisor hint
- [x] "Report Bad Recommendation" option on AI Advisor
- [x] AI Advisor chat history persists within session
- [x] "New Chat" button to clear conversation
- [x] "Past Chats" expander with last 10 conversations
- [x] Load past conversations into current chat
- [x] Log both rules AND AI responses to database
- [x] Fixed popover double-background styling issue
- [x] Fixed popover width for feedback form
- [x] Removed sidebar dead space under logo

### Earlier
- [x] Fix Chief Charms to show 18 charms (6 gear x 3 types)
- [x] Fix layout order: Lancer (cap/watch) top, Infantry (coat/pants) middle, Marksman (belt/weapon) bottom
- [x] Add Random Chaos Labs branding to sidebar
- [x] Add hero role badges (gatherer, joiner, garrison, research, stamina, construction)
- [x] Support multiple role badges per hero
- [x] Add roles for heroes across all generations (1-13+)
- [x] Research and save chief gear tier progression data (42 tiers)
- [x] Research and save chief charm level/shape progression data
- [x] Research and save hero stats database
- [x] Research and save troop power/stats data
- [x] Download chief gear and charm images
- [x] Build power optimization into recommendation engine
  - Created `engine/analyzers/power_optimizer.py` with PowerUpgrade dataclass
  - Analyzes: chief gear (42 tiers, exact % bonuses), chief charms (16 levels, exact % bonuses), hero upgrades, troop tiers (exact power/unit), war academy (exact power_gain values)
  - Qualitative tips for: research, pets, daybreak island (not tracked in DB)
  - Integrated into RecommendationEngine.get_recommendations()
  - Updated Advisor UI to show power-based recommendations with "POWER" badge

## Notes

- Database schema was updated - users may need to delete `wos_optimizer.db` if they see errors
- Hero role data is in `pages/1_Heroes.py` in the `HERO_ROLES` dict
- Game data files are in `data/` folder (hero_stats_database.json, troop_data.json, chief_equipment_data.json, hero_power_data.json)

### Admin System Architecture

**Database Models** (`database/models.py`):
- `User` - id, username, email, password_hash, role (admin/user), is_active, created_at, last_login
- `FeatureFlag` - name, description, is_enabled, created_at, updated_at
- `Announcement`, `AuditLog`, `Feedback` - Supporting models

**Auth System** (`database/auth.py`):
- `authenticate_user()` - Verify credentials with bcrypt
- `login_user()` / `logout_user()` - Session management
- `login_as_user()` - Admin impersonation (preserves original admin session)
- `is_impersonating()` - Check if admin is viewing as another user
- `require_admin()` - Page-level access control
- `ensure_admin_exists()` - Creates default admin on first run

**Page Routing** (`app.py`):
- Unauthenticated: Landing → Login/Register pages
- Authenticated Admin: Admin navigation (Dashboard, Users, etc.)
- Authenticated User: Game navigation (Heroes, Advisor, etc.)
- Impersonation: Shows user view with red banner + Switch Back button

**Feature Flags** (8 defaults):
- `hero_recommendations` - AI-powered recommendations (enabled)
- `inventory_ocr` - Screenshot scanning (disabled)
- `alliance_features` - Alliance tools (disabled)
- `beta_features` - Experimental features (disabled)
- `maintenance_mode` - Show maintenance notice (disabled)
- `new_user_onboarding` - Guided setup (enabled)
- `dark_theme_only` - Force Arctic Night (disabled)
- `analytics_tracking` - Usage analytics (enabled)

**Streamlit Button Quirk**: Buttons with emoji characters don't render in certain column/loop contexts. Use plain text labels (Edit, Delete, Save, etc.).

### Power Optimizer Architecture

The power optimizer (`engine/analyzers/power_optimizer.py`) provides upgrade recommendations backed by actual power calculations.

**Data Sources Used:**
- `data/chief_equipment_data.json` - 42 gear tiers (9.35% → 187% bonus), 16 charm levels (9% → 100% bonus)
- `data/troop_data.json` - Power per unit by tier (T1=3, T11=17-80)
- `data/hero_power_data.json` - XP requirements, shard costs, skill scaling
- `data/upgrades/war_academy.steps.json` - EXACT power_gain values per level (6,888 → 8,784)

**Confidence Levels:**
- `exact` - War Academy, troop tiers (have exact power values from game data)
- `estimated` - Chief gear/charms (calculated from % bonuses), hero upgrades
- `qualitative` - Research, pets, daybreak (not tracked in DB, just tips)

**Integration Points:**
- `RecommendationEngine.get_recommendations()` - Merges power-based with rule-based recommendations
- `RecommendationEngine.get_power_recommendations()` - Power-only recommendations
- `pages/6_Advisor.py` - Shows "POWER" badge on power-based recommendations

**Key Classes:**
- `PowerUpgrade` dataclass: upgrade_type, target, from_level, to_level, power_gain, bonus_gain, efficiency, priority, confidence
- `PowerOptimizer` class: Analyzes user_heroes, user_gear, user_charms and returns sorted recommendations by efficiency
