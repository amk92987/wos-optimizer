# WoS Research Questions for ChatGPT (Web Search)

Track progress on gathering verified game data.

**Last Updated:** 2026-01-07

---

## Current Status Summary

| Topic | Status | Data Files |
|-------|--------|------------|
| Q1: Chief Gear | COMPLETE | `chief_gear.json`, `synergy_model.json` |
| Explanation System | COMPLETE | `explanation_system.json`, `explanation_builder.json` |
| Confidence Scoring | COMPLETE | `confidence_scoring.json` |
| Upgrade Costs/Benefits | IN PROGRESS | (next priority) |
| Q2: Hero Gear | COMPLETE | `raw/hero_gear.research.json` |
| Q3: Chief Gear Charms | COMPLETE | `raw/chief_charms.research.json` |
| Q4: Pets | COMPLETE | `raw/pets.research.json` |
| Q5: Research Priorities | COMPLETE | `guides/research_priorities.json` |
| Q6: Daybreak Island | COMPLETE | `raw/daybreak_island.research.json` |
| Shop Items & Currencies | PARTIAL | `shops.json` (needs verification) |
| Chest Types | PARTIAL | `chests.json` (needs verification) |
| Hero Skill Descriptions | PARTIAL | `heroes.json` (14 heroes done, Gen 4-14 pending) |

---

## NEW: Upgrade Costs & Benefits Data

**Status:** IN PROGRESS (next priority)

Systems to document with level-by-level costs and stat gains:
- [ ] Hero Levels (1-80) - XP costs, stat gains
- [ ] Hero Stars/Ascension - shard costs, stat multipliers
- [ ] Hero Skills (1-5) - manual costs, % gains per level
- [ ] Chief Gear Quality Tiers - materials, stat progression
- [ ] Hero Gear Levels - XP costs, stat progression
- [ ] Pets - level costs, skill unlocks

**Purpose:** Enable ROI calculations, resource planning, "what do I need to reach X?" queries

---

## Question 1: Chief Gear
**Status:** COMPLETE

```
In Whiteout Survival, explain Chief Gear:
- What are the 6 gear pieces and which hero class benefits from each?
- How does gear quality work (Common → Mythic)?
- What stats does each piece provide?
- What's the recommended upgrade priority?
Please cite sources (WoS Wiki, guides, etc.)
```

**Response:** PROCESSED - Data saved to:
- `data/chief_gear.json` (structured data with ROI, spender paths)
- `data/synergy_model.json` (combat synergy model)
- `data/WOS_REFERENCE.md` (Chief Gear section, Spender Paths, Combat Synergy)
- `engine/ai_recommender.py` (AI knowledge updated with full mechanics)

**Additional specs completed:**
- Explanation System (`explanation_system.json`)
- Explanation Builder with 10 examples (`explanation_builder.json`)
- Confidence Scoring System (`confidence_scoring.json`)

---

## Question 2: Hero Gear
**Status:** PENDING (after upgrade costs)

```
In Whiteout Survival, explain Hero Gear:
- What are the gear quality tiers (Common → Legendary → Mythic)?
- How does Hero Gear XP work? What are the sources?
- How does forging work with Essence Stones?
- What is Mastery Forging and what does it add?
- What's the full upgrade progression path?
- Which heroes should get gear priority?
Please cite sources (WoS Wiki, guides, etc.)
```

**Response:** (paste here)

---

## Question 3: Chief Gear Charms
**Status:** PENDING

```
In Whiteout Survival, explain Chief Gear Charms:
- How do charms work? How do you attach them?
- What types of charms exist and what stats do they provide?
- What's the best charm setup for SvS/combat focused players?
- How do you obtain and upgrade charms?
Please cite sources.
```

**Response:** (paste here)

---

## Question 4: Pets
**Status:** PENDING

```
In Whiteout Survival, explain the Pet system:
- What pets exist and what are their skills/abilities?
- How do you obtain, level, and upgrade pets?
- Which pets are best for PvP vs PvE?
- How do pet skills work in rallies?
Please cite sources.
```

**Response:** (paste here)

---

## Question 5: Research Priorities
**Status:** PENDING

```
In Whiteout Survival, explain Research priorities:
- What are the main research trees (Growth, Economy, Battle)?
- What's the recommended research order for combat-focused players?
- What's the recommended order for F2P vs spenders?
- Any research that's commonly overlooked but important?
Please cite sources.
```

**Response:** (paste here)

---

## Question 6: Daybreak Island
**Status:** PENDING

```
In Whiteout Survival, explain Daybreak Island:
- What is it and when does it unlock?
- How does the gameplay work?
- What rewards does it provide?
- Any tips for optimal play?
Please cite sources.
```

**Response:** (paste here)

---

## Backpack & UI Research
**Status:** PARTIAL - Data files created 2026-01-10

### Shop Items & Currencies
- [x] Research all shop types and their currencies (Glowstones, etc.) - Created `data/shops.json`
- [x] Mystery Shop items and costs
- [x] Arena Shop items
- [x] Alliance Shop items
- [x] SvS Shop items
- [x] Event-specific shops
- [ ] NEEDS VERIFICATION: Actual in-game costs and exact item lists

### Missing Chest Types
- [x] Fishing event chests (Ice Fishing rewards) - Created `data/chests.json`
- [x] Labyrinth chests and rewards
- [x] Other event-specific chests
- [ ] NEEDS VERIFICATION: Exact drop rates and item lists from in-game

### Hero Skill Descriptions
- [x] Research hero skill descriptions for tooltip hovers - Added to `data/heroes.json`
- [x] Exploration skills (what each skill does at each level)
- [x] Expedition skills (what each skill does at each level)
- [x] Document in heroes.json using `_desc` suffix fields
- **Heroes with descriptions added:** Sergey, Jessie, Jeronimo, Natalia, Bahiti, Patrick, Molly, Flint, Philly, Alonso, Gina, Mia, Greg
- [ ] TODO: Add descriptions for remaining heroes (Gen 4-14)

---

## Data Files Reference

### Core Schema
- `wos_schema.json` - Master schema (heroes, gear, rules, contexts)

### Mechanics & Rules
- `chief_gear.json` - Chief gear pieces, ROI, spender paths
- `synergy_model.json` - Combat context weights, hero roles
- `WOS_REFERENCE.md` - Human-readable reference guide

### Recommendation Engine
- `explanation_system.json` - Reason types, claims, templates
- `explanation_builder.json` - Input/output spec, 10 examples
- `confidence_scoring.json` - Scoring formula, grade mapping, guardrails

### Hero Data
- `heroes.json` - Basic hero data
- `wos_schema.json` (entities.heroes) - Detailed hero skills

---

## Implementation Checklist

After gathering all research:

- [x] Chief Gear - Data + ROI model complete
- [x] Explanation System - Builder + examples complete
- [x] Confidence Scoring - Formula + guardrails complete
- [ ] Upgrade Costs/Benefits - Level-by-level progression data
- [ ] Hero Gear - Full mechanics + tracking
- [ ] Chief Gear Charms - Data + tracking
- [ ] Pets - Data + tracking page
- [ ] Research - Recommendations page/section
- [ ] Daybreak Island - Guidance page/section
- [ ] Build recommendation engine with all specs
- [ ] Update AI Advisor with new mechanics
