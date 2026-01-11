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

- [ ] **Add Stripe Donate button** - Monetization option

- [ ] **Consider moving off Streamlit to AWS** - Major architecture decision for scaling

## Completed

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
