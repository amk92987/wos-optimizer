# Data Audit - WoS Optimizer

Comprehensive inventory of all game data, sources, confidence levels, and where each is used in the application.

**Last Updated:** 2026-01-13
**Total Data Files:** 67 JSON files (~850KB)

---

## Table of Contents

1. [Core Game Data](#core-game-data)
2. [Strategy Guides](#strategy-guides)
3. [Optimization Engine](#optimization-engine)
4. [Upgrade Edge Graphs](#upgrade-edge-graphs)
5. [Resource & Conversion Data](#resource--conversion-data)
6. [Confidence & Explanation Systems](#confidence--explanation-systems)
7. [AI Training Data](#ai-training-data)
8. [Raw/Reference Data](#rawreference-data)
9. [Validation Reports](#validation-reports)
10. [Verification Status Summary](#verification-status-summary)
11. [High-Priority Verification Items](#high-priority-verification-items)

---

## Confidence Grade Legend

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| **A** | 0.90-1.00 | Official source or verified mechanics |
| **B** | 0.80-0.89 | Calculator output or reputable community |
| **C** | 0.65-0.79 | Community consensus, may vary |
| **D** | 0.50-0.64 | Estimated or partially verified |
| **E** | 0.00-0.49 | Speculative, needs verification |

---

## Core Game Data

### `data/heroes.json` (43 KB)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Master database of all heroes (Gen 1-14+) |
| **Contents** | Name, generation, class, rarity, tier ratings, 6 skills with descriptions, image references |
| **Source** | [Whiteout Survival Wiki](https://www.whiteoutsurvival.wiki/) |
| **Confidence** | **A** - Verified hero mechanics |
| **Last Verified** | 2026-01-07 |
| **Used In** | Hero Tracker page, Lineup Builder, AI Recommender |

**Key Data Points:**
- Hero attributes: name, generation (1-14), class (Infantry/Marksman/Lancer), rarity
- Tier ratings: tier_overall, tier_expedition, tier_exploration (D through S+)
- 6 skill slots: 3 exploration (PvE) + 3 expedition (PvP)
- Skill scaling: levels 1-5 with descriptions

**Verification Checklist:**
- [ ] Cross-check Gen 13-14 heroes against wiki
- [ ] Verify expedition skill percentages for top joiners (Jessie, Sergey)
- [ ] Confirm tier ratings match current meta

---

### `data/troop_data.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Troop stats and power scaling across 11 tiers |
| **Contents** | Power per unit T1-T11, base stats, class counters |
| **Source** | onechilledgamer.com, whiteoutdata.com, wostools.net |
| **Confidence** | **B** - Community sources |
| **Last Verified** | 2025-01-11 |
| **Used In** | Troop recommendations, power calculations |

**Key Data Points:**
- Power per unit by tier and class
- Base stats: defense, lethality, attack, health, load capacity
- Class counters: ~30% bonus damage (Infantry > Lancer > Marksman > Infantry)

**Verification Checklist:**
- [ ] Verify T10-T11 power values against in-game
- [ ] Confirm class counter bonus percentage

---

### `data/chief_gear.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Chief Gear slots, set bonuses, upgrade strategy |
| **Contents** | 6 slots, set bonus mechanics, spender paths |
| **Source** | `chief_equipment_data.json`, user verification |
| **Confidence** | **A** - User verified 2026-01-13 |
| **Last Verified** | 2026-01-13 |
| **Used In** | Gear Advisor, Quick Tips, AI Recommender |

**Key Data Points:**
- 6 Slots: Coat/Pants (Infantry), Belt/Weapon (Marksman), Cap/Watch (Lancer)
- Set Bonuses: 3-piece = Defense ALL, 6-piece = Attack ALL
- Priority: Same tier first, then Infantry > Marksman > Lancer

**Verification Status:** VERIFIED - Corrected from wrong slot names on 2026-01-13

---

### `data/vip_system.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | VIP level progression and benefits (0-15) |
| **Contents** | Points required, speed bonuses, unlocked features |
| **Source** | In-game data |
| **Confidence** | **A** - Static game system |
| **Last Verified** | Not verified |
| **Used In** | Not currently displayed in UI |

**Verification Checklist:**
- [ ] Verify VIP 12-15 bonuses against in-game

---

### `data/events.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Event calendar, scoring mechanics |
| **Contents** | SvS, Hall of Chiefs, Bear Trap, Crazy Joe mechanics |
| **Source** | Verified game mechanics |
| **Confidence** | **A** - Community consensus |
| **Last Verified** | 2026-01-08 |
| **Used In** | Events page, Quick Tips, SvS Prep tips |

**Critical Data Points (High Impact):**
- SvS speedups only give points Days 1, 2, 5 (NOT 3-4)
- Fire Crystal = 2,000 pts (Day 1)
- Mithril = 40,000 pts (Day 4)
- Lucky Wheel = 8,000 pts per spin
- T9→T10 promotion = 0.71 pts/sec (beats speedups on Day 4)

**Verification Checklist:**
- [ ] Verify SvS point values haven't changed in recent patches
- [ ] Confirm troop promotion points calculation

---

### `data/wos_schema.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Comprehensive hero mechanics schema |
| **Contents** | Entity definitions, skill scaling, source tracking |
| **Source** | WoS Wiki, Century Help Center |
| **Confidence** | **A** - Primary sources |
| **Last Verified** | 2026-01-13 |
| **Used In** | Schema validation, cross-reference checks |

---

## Strategy Guides

### `data/guides/quick_tips.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Consolidated cheat sheet - critical game knowledge |
| **Contents** | 13 categories, ~80 tips, common mistakes |
| **Source** | Verified mechanics + community consensus |
| **Confidence** | **A** (critical), **B** (meta-dependent) |
| **Last Verified** | 2026-01-13 |
| **Used In** | Quick Tips page (all 4 tabs) |

**High-Impact Tips to Verify:**
- [ ] Tool Enhancement research speed bonuses (0.4%-2.5% per level)
- [ ] Daybreak decoration percentages (Epic 2.5%, Mythic 10%)
- [ ] Rally joiner skill mechanics
- [ ] SvS point values

---

### `data/guides/combat_formulas.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Combat mechanics and damage calculations |
| **Contents** | Damage formula, class counters, formation ratios |
| **Source** | Derived from game mechanics |
| **Confidence** | **B** - Derived formulas |
| **Last Verified** | Not verified against actual combat |
| **Used In** | Combat page, Battle Tactics |

**Verification Checklist:**
- [ ] Test damage formula against actual combat results
- [ ] Verify class counter bonus (stated as ~30%)

---

### `data/guides/combat_optimization_audit.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Combat stat sources and optimization guide |
| **Contents** | Stat stacking examples, hidden stats checklist |
| **Source** | Verified mechanics |
| **Confidence** | **A** |
| **Last Verified** | 2026-01-13 |
| **Used In** | Combat page |

---

### `data/guides/daybreak_island_priorities.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Tree of Life and decoration priorities |
| **Contents** | Decoration stats, upgrade order |
| **Source** | WoS Wiki |
| **Confidence** | **A** |
| **Last Verified** | 2026-01-08 |
| **Used In** | Daybreak Island page, Quick Tips |

---

### `data/guides/hero_lineup_reasoning.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Rally and lineup selection logic |
| **Contents** | Leader vs joiner mechanics, hero recommendations |
| **Source** | Verified mechanics |
| **Confidence** | **A** |
| **Last Verified** | 2026-01-08 |
| **Used In** | Lineup Builder, AI Recommender |

---

### `data/guides/research_priorities.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Research tree prioritization |
| **Contents** | Tool Enhancement, Battle tree, Growth tree order |
| **Source** | Community consensus |
| **Confidence** | **B** |
| **Last Verified** | Not verified |
| **Used In** | Quick Tips |

---

## Optimization Engine

### `data/optimizer/progression_phases.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Game phase detection (early/mid/late/endgame) |
| **Contents** | Phase definitions by furnace level |
| **Source** | Game structure |
| **Confidence** | **A** |
| **Used In** | Recommendation Engine |

**Phase Definitions:**
- Early: F1-18
- Mid: F19-29
- Late: F30/FC1-5
- Endgame: FC5+

---

### `data/optimizer/system_unlocks.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | When systems become available |
| **Contents** | Furnace/state age requirements |
| **Source** | Verified unlocks |
| **Confidence** | **A** |
| **Used In** | Recommendation Engine |

**Critical Unlocks:**
- F9: Research
- F18 + 55 days: Pets
- F19: Daybreak Island
- F25: Chief Charms
- F30: FC buildings, War Academy, Hero Gear Mastery

---

### `data/optimizer/decision_rules.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Prioritization weights by profile |
| **Contents** | System weights for svs_combat, balanced, economy |
| **Source** | Designed logic |
| **Confidence** | **A** |
| **Used In** | Recommendation Engine |

---

### `data/optimizer/recommendation_reasons.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | User-facing explanations |
| **Contents** | Why upgrades are recommended |
| **Source** | Strategy logic |
| **Confidence** | **A** |
| **Used In** | Recommendation display |

---

## Upgrade Edge Graphs

These files define upgrade progressions as directed acyclic graphs (DAGs) with costs.

### `data/upgrades/buildings.edges.json` (261 edges)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Building upgrades L1-30 |
| **Source** | SRC_BUILDING_CALCULATOR, SRC_WIKI_BUILDINGS |
| **Confidence** | **B** - Calculator output |
| **Used In** | Upgrade cost calculations |

---

### `data/upgrades/buildings.fc.edges.json` (313 edges)

| Attribute | Value |
|-----------|-------|
| **Purpose** | FC building upgrades |
| **Source** | SRC_WIKI_BUILDINGS_FC |
| **Confidence** | **A** - Wiki tables |
| **Used In** | Late-game upgrade calculations |

---

### `data/upgrades/chief_gear.steps.json` (83 edges)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Chief Gear tier progression |
| **Source** | SRC_WIKI_CHIEF_GEAR |
| **Confidence** | **A** - Direct table |
| **Used In** | Gear upgrade recommendations |

---

### `data/upgrades/war_academy.steps.json` (45 edges)

| Attribute | Value |
|-----------|-------|
| **Purpose** | War Academy research |
| **Source** | SRC_WIKI_WAR_ACADEMY |
| **Confidence** | **A** - Direct table |
| **Used In** | War Academy recommendations |

---

### `data/upgrades/troops.train.edges.json` (90 edges)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Troop training T1-T11 |
| **Confidence** | **B** |

---

### `data/upgrades/troops.promote.edges.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Troop tier promotions |
| **Confidence** | **B** |

---

### Other Upgrade Files

| File | Purpose | Confidence |
|------|---------|------------|
| `hero_gear.mastery.edges.json` | Mythic gear mastery | B |
| `chief_charms.edges.json` | Charm L1-16 | B |
| `daybreak_island.tree_of_life.edges.json` | Life Essence | A |
| `pets.advancement.edges.json` | Pet leveling | B |

---

## Resource & Conversion Data

### `data/conversions/resource_value_hierarchy.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Resource tier valuation |
| **Confidence** | **C** - Estimated from packs |
| **Used In** | Pack Analyzer |

---

### `data/conversions/gem_shadow_prices.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Gem-equivalent pricing |
| **Confidence** | **C-D** - Estimation based |
| **Used In** | Pack value calculations |

---

## Confidence & Explanation Systems

### `data/confidence_scoring.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Anti-hallucination framework |
| **Contents** | Grade mapping, claim types, scoring formula |
| **Confidence** | **A** - Self-designed |
| **Used In** | All recommendations |

**Anti-Hallucination Rules:**
1. No evidence = no claim
2. Meta claims labeled and capped at B
3. Stale meta (>60 days) capped at C

---

### `data/explanation_system.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Recommendation explanation UX |
| **Contents** | Reason types, claims registry, evidence linking |
| **Confidence** | **A** |
| **Used In** | Recommendation explanations |

---

### `data/synergy_model.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Power propagation mechanics |
| **Contents** | Chief Gear vs Hero Gear, rally skill mechanics |
| **Confidence** | **A** - Foundational mechanics |
| **Used In** | Gear Advisor, Lineup Builder |

---

## AI Training Data

### `data/openai_wos_knowledge.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Game knowledge for AI Advisor |
| **Confidence** | **A** - Curated |
| **Used In** | AI Advisor page |

---

### `data/openai_wos_followup.json`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Follow-up question handling |
| **Used In** | AI Advisor |

---

## Raw/Reference Data

| File | Purpose | Confidence |
|------|---------|------------|
| `raw/chief_charms.research.json` | Charm research data | B |
| `raw/chief_gear.table.json` | Gear table source | A |
| `raw/daybreak_island.research.json` | Island research | B |
| `raw/hero_gear.research.json` | Hero gear research | B |
| `raw/pets.research.json` | Pet research | B |
| `raw/research.research.json` | Research tree data | B |
| `raw/troops.promote.samples.json` | Promotion samples | B |
| `raw/troops.train.samples.json` | Training samples | B |
| `raw/war_academy.table.json` | War Academy table | A |

---

## Validation Reports

| File | Purpose |
|------|---------|
| `validation/buildings.fc.report.json` | FC building validation |
| `validation/buildings.report.json` | Building validation |
| `validation/chief_gear.report.json` | Chief gear validation |
| `validation/formula_checks.json` | Formula validation |
| `validation/troops.report.json` | Troop validation |
| `validation/war_academy.report.json` | War Academy validation |

---

## Verification Status Summary

### By Confidence Grade

| Grade | Count | Description |
|-------|-------|-------------|
| **A** | ~40 files | Verified/Official sources |
| **B** | ~15 files | Calculator/Community sources |
| **C** | ~8 files | Estimated/Consensus |
| **D-E** | ~4 files | Needs verification |

### Recently Verified (2026-01-13)

- [x] `chief_gear.json` - Slot names corrected
- [x] `wos_schema.json` - Chief gear section updated
- [x] `quick_tips.json` - Tool Enhancement tip fixed
- [x] `combat_optimization_audit.json` - Chief gear examples fixed

### Needs Verification

- [ ] `troop_data.json` - T10-T11 power values
- [ ] `combat_formulas.json` - Damage formula accuracy
- [ ] `gem_shadow_prices.json` - Current pack rates
- [ ] `resource_value_hierarchy.json` - Tier valuations

---

## High-Priority Verification Items

These items have high impact if wrong:

### 1. SvS Point Values
**Location:** `events.json`, `quick_tips.json`
**Impact:** Critical - affects player strategy
**Verify Against:** In-game SvS event

| Item | Stated Value | Verified? |
|------|--------------|-----------|
| Fire Crystal | 2,000 pts | [ ] |
| Mithril | 40,000 pts | [ ] |
| Lucky Wheel | 8,000 pts | [ ] |
| Speedups Day 1/2/5 | Yes | [ ] |
| Speedups Day 3/4 | No | [ ] |

### 2. Tool Enhancement Research Speed
**Location:** `quick_tips.json`
**Impact:** Critical - affects early game strategy
**Stated:** 0.4%-2.5% per level, ~35% cumulative I-VII
**Verify Against:** WoS Wiki Tool Enhancement pages

### 3. Rally Joiner Mechanics
**Location:** `heroes.json`, `wos_schema.json`, `synergy_model.json`
**Impact:** Critical - affects rally strategy
**Stated:** Only leftmost hero's top-right expedition skill applies
**Verify Against:** In-game rally mechanics

### 4. Daybreak Decoration Percentages
**Location:** `quick_tips.json`, `daybreak_island_priorities.json`
**Impact:** High - affects decoration priorities
**Stated:** Epic 2.5% max, Mythic 10% max
**Verify Against:** In-game decoration stats

### 5. Chief Gear Set Bonuses
**Location:** `chief_gear.json`, `wos_schema.json`
**Impact:** Critical - affects gear strategy
**Stated:** 3-piece = Defense ALL, 6-piece = Attack ALL
**Status:** VERIFIED by user 2026-01-13

---

## Data Location Quick Reference

### Where is Chief Gear data?
- `data/chief_gear.json` - Strategy and priorities
- `data/chief_equipment_data.json` - Slot definitions
- `data/wos_schema.json` - Schema with set bonuses
- `data/upgrades/chief_gear.steps.json` - Upgrade costs
- `engine/analyzers/gear_advisor.py` - Recommendation logic

### Where is Hero data?
- `data/heroes.json` - Master hero database
- `data/hero_stats_database.json` - Stat lookups
- `data/hero_power_data.json` - Power calculations
- `engine/analyzers/hero_analyzer.py` - Recommendation logic

### Where is SvS data?
- `data/events.json` - SvS mechanics and points
- `data/guides/quick_tips.json` - SvS Prep/Battle tips
- `data/WOS_REFERENCE.md` - SvS documentation

### Where is Rally data?
- `data/synergy_model.json` - Rally skill mechanics
- `data/guides/hero_lineup_reasoning.json` - Rally strategy
- `data/explanation_system.json` - Rally claims
- `engine/analyzers/lineup_builder.py` - Lineup logic

---

## Appendix: Source Registry

See `data/research_sources.json` for full source definitions.

### Tier-1 Sources (Trust 1.0)
- **wos_wiki**: https://www.whiteoutsurvival.wiki/
- **wos_help**: Official Century Games help center

### Tier-2 Sources (Trust 0.9)
- **whiteoutsurvival.app**: https://whiteoutsurvival.app/
- **whiteoutdata.com**: https://whiteoutdata.com/
- **wostools.net**: https://wostools.net/
- **quackulator.com**: https://www.quackulator.com/

### Community Sources (Trust 0.6-0.75)
- YouTube creators (requires meta label)
- Reddit/Discord (version-sensitive)
