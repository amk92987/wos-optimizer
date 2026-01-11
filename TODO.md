# WoS Optimizer - TODO List

## High Priority

- [ ] **Build power optimization into AI Advisor** - Use collected hero stats, troop data, and combat formulas to provide upgrade recommendations

- [ ] **Fix Advisor screen** - Currently not working, needs debugging

- [ ] **Fix Upgrade Priority page** - Currently not working, needs debugging

## UI/UX Improvements

- [ ] **Chief gear images are static at Gold T2 3★** - Either accept current images or find/create images for other tier levels

- [ ] **Consider 3 selectors for gear (color, tier, star) vs 1 dropdown** - Current single dropdown has 42 options, might be cleaner with 3 separate selectors

- [ ] **Rename sidebar items to be more precise** - Current names may be unclear

- [ ] **Rename app from "WoS Optimizer" to something fun** - Brainstorm creative names

- [ ] **Get proper backpack images** - Need images for Deal Event Currencies, Glowstones, and other items

- [ ] **Consider gradient background for main pages** - Design enhancement

## Infrastructure/Deployment

- [ ] **Create admin page for usernames/passwords** - Required for AWS deployment with user accounts

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

## Notes

- Database schema was updated - users may need to delete `wos_optimizer.db` if they see errors
- Hero role data is in `pages/1_Heroes.py` in the `HERO_ROLES` dict
- Game data files are in `data/` folder (hero_stats_database.json, troop_data.json, chief_equipment_data.json, hero_power_data.json)
