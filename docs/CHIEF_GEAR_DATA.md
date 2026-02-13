# Chief Gear Data Locations

This document lists all files in the codebase that contain Chief Gear data or references.
Use this as a guide when updating Chief Gear mechanics.

## Core Data Files

| File | Purpose | Data Type |
|------|---------|-----------|
| `data/chief_gear.json` | Primary Chief Gear data | Slots, stats, upgrade materials |
| `data/wos_schema.json` | Schema definitions | Chief Gear structure, set bonuses |
| `data/WOS_REFERENCE.md` | Game mechanics reference | Priority strategy, set bonuses |

## Engine Files

| File | Purpose | Functions |
|------|---------|-----------|
| `engine/analyzers/gear_advisor.py` | Gear recommendations | `CHIEF_GEAR_ORDER`, `_analyze_chief_gear()` |
| `engine/ai_recommender.py` | AI knowledge base | Hardcoded Chief Gear rules |

## Guide Files

| File | Purpose | Sections |
|------|---------|----------|
| `data/guides/quick_tips.json` | Quick tips | Chief Gear tips, common mistakes |
| `data/guides/combat_optimization_audit.json` | Combat guide | Chief Gear section, stat examples |
| `data/explanation_builder.json` | Explanation templates | Chief Gear explanations |
| `data/explanation_system.json` | Explanation system | Claims, templates |

## Page Files

| File | Purpose | Sections |
|------|---------|----------|
| `pages/00_Beginner_Guide.py` | Beginner guide | Chief Gear intro |
| `pages/10_Combat.py` | Combat page | Stat comparison UI |

## Documentation Files

| File | Purpose | Sections |
|------|---------|----------|
| `RECOMMENDATION_ENGINE.md` | Engine documentation | Gear Advisor section |
| `.claude/skills/wos-upgrades/SKILL.md` | Upgrade skill docs | Example output format |
| `CLAUDE.md` | Project guide | Quick reference |

---

## Chief Gear Data Model

### The 6 Slots

| Slot | Troop Type | Stats |
|------|------------|-------|
| coat | Infantry | Attack/Defense |
| pants | Infantry | Attack/Defense |
| belt | Marksman | Attack/Defense |
| weapon | Marksman | Attack/Defense |
| cap | Lancer | Attack/Defense |
| watch | Lancer | Attack/Defense |

### Set Bonuses

- **3-piece bonus:** Defense boost for ALL troop types
- **6-piece bonus:** Attack boost for ALL troop types

### Upgrade Priority Strategy

**CRITICAL:** Keep all 6 pieces at SAME TIER for set bonuses!

When pushing to next tier:
1. Infantry (Coat/Pants) - Frontline, engage first
2. Marksman (Belt/Weapon) - Key damage dealers
3. Lancer (Cap/Watch) - Mid-line support, lowest priority

---

## Historical Notes

**January 2026:** Major data correction - previous incorrect slot names (Ring, Amulet, Gloves, Boots, Helmet, Armor) were replaced with correct names (Coat, Pants, Belt, Weapon, Cap, Watch). All files in this document were updated to reflect the correct data.
