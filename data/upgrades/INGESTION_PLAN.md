# Upgrade Data Ingestion Plan

## Order of Implementation
1. **Chief Gear** (static table - easiest, most reliable) - COMPLETE
2. **War Academy** (static table + prereqs - also clean) - COMPLETE
3. **Troops** (calculator output - generate own table) - COMPLETE
4. **Buildings** (calculator output - generate own table) - COMPLETE
5. **Hero Gear** (mastery forging + enhancement) - COMPLETE
6. **Chief Charms** (charm upgrades L1-L16) - COMPLETE
7. **Pets** (advancement milestones) - COMPLETE
8. **Research** (Growth/Economy/Battle trees) - PARTIAL (structure only, costs in calculators)
9. **Daybreak Island** (Tree of Life upgrades) - COMPLETE

## Progress Summary
| System | Raw File | Edges File | Report | Status |
|--------|----------|------------|--------|--------|
| Chief Gear | `raw/chief_gear.table.json` | `upgrades/chief_gear.steps.json` | `validation/chief_gear.report.json` | OK (84 rows, 83 edges) |
| War Academy | `raw/war_academy.table.json` | `upgrades/war_academy.steps.json` | `validation/war_academy.report.json` | OK (46 rows, 45 edges) |
| Troops (train) | `raw/troops.train.samples.json` | `upgrades/troops.train.edges.json` | `validation/troops.report.json` | OK (90 edges) |
| Troops (promote) | `raw/troops.promote.samples.json` | `upgrades/troops.promote.edges.json` | `validation/troops.report.json` | OK (75 edges) |
| Buildings | `dictionaries/buildings.catalog.json` | `upgrades/buildings.edges.json` | `validation/buildings.report.json` | OK (261 edges, 9 buildings) |
| Buildings (FC) | - | `upgrades/buildings.fc.edges.json` | `validation/buildings.fc.report.json` | OK (313 edges, 7 buildings) |
| Hero Gear (Mastery) | `raw/hero_gear.research.json` | `upgrades/hero_gear.mastery.edges.json` | - | OK (20 edges) |
| Chief Charms | `raw/chief_charms.research.json` | `upgrades/chief_charms.edges.json` | - | OK (16 edges) |
| Pets | `raw/pets.research.json` | `upgrades/pets.advancement.edges.json` | - | OK (10 edges) |
| Research | `raw/research.research.json` | - | - | PARTIAL (structure, totals only) |
| Daybreak Island | `raw/daybreak_island.research.json` | `upgrades/daybreak_island.tree_of_life.edges.json` | - | OK (9 edges) |

---

## 1) Chief Gear Ingestion

### A) Target JSON Structure
File: `upgrades/chief_gear.steps.json`

```json
{
  "system": "chief_gear",
  "unit": "step",
  "currencies": ["hardened_alloy", "polishing_solution", "design_plan", "lunar_amber"],
  "edges": [
    {
      "upgrade_id": "chief_gear:red-0:step1->step2",
      "from": { "tier": "red-0", "step": 1 },
      "to": { "tier": "red-0", "step": 2 },
      "cost": {
        "hardened_alloy": 12500,
        "polishing_solution": 132,
        "design_plan": 21,
        "lunar_amber": 2
      },
      "source_ids": ["SRC_WIKI_CHIEF_GEAR"],
      "evidence": { "source_row_key": "red-0_step1" },
      "confidence": { "grade": "A", "reason": "direct table row" }
    }
  ]
}
```

### B) Pipeline Steps

#### Step 1: Store Raw Rows
File: `raw/chief_gear.table.json`

```json
{
  "source_id": "SRC_WIKI_CHIEF_GEAR",
  "retrieved_at": "2026-01-07T00:00:00Z",
  "rows": [
    {
      "tier": "red-0",
      "step": 1,
      "hardened_alloy": 12500,
      "polishing_solution": 132,
      "design_plan": 21,
      "lunar_amber": 2,
      "row_key": "red-0_step1"
    }
  ]
}
```

**Why:** Preserves "what the source said" separately from computed edges. Enables diffing if data changes.

#### Step 2: Convert Rows → Edges

**Rules:**
- Within a tier: step 1→2, 2→3, 3→4
- Tier transitions: tier X step 4 → tier (next) step 1

**Tier ordering list:**
```json
["green", "blue", "purple", "red-0", "red-1", "red-2", ...]
```

### C) Validations

#### 1. Continuity Validation
- Every tier must have steps 1-4
- Every row produces exactly one edge (except last tier step 4)
- No missing rows
- No duplicate (tier, step)
- All costs are non-negative integers

#### 2. Edge Integrity Validation
- Max one outgoing edge per node (tier, step)
- No cycles (straight path only)

#### 3. Cross-Check Totals (Optional)
Use Quackulator Chief Gear calculator:
- Choose start and end node
- Compare sum of edges vs calculator total
- Detects: scrape errors, table updates, parsing mistakes

### D) Benefit Handling
For now: `benefit: null`

Later add when stats source available:
```json
"benefit": { "troop_attack_pct": 0.20 }
```

Optimizer can still work without benefits using:
- Cost-only budgeting ("can I afford this?")
- Proxy value weights (Ring > Amulet > ...)

---

## 2) War Academy - COMPLETE

### Implementation Details
- **Raw file**: `raw/war_academy.table.json` (46 rows, FC1-0 through FC10-0)
- **Edges file**: `upgrades/war_academy.steps.json` (45 edges)
- **Build script**: `scripts/build_war_academy_edges.py`

### Structure
- Levels use FCx-y notation (e.g., FC1-0, FC1-1, FC2-0)
- Each edge includes `prereq.furnace_fc_level` requirement
- Currencies: fire_crystal_shards, refined_fire_crystals, meat, wood, coal, iron
- Includes time_seconds and power_gain per edge

### Sources
- wostools.net/wiki/buildings/war-academy
- whiteoutsurvival.app/buildings/war-academy/

---

## 3) Troops - COMPLETE

### Implementation Details
- **Training**: `raw/troops.train.samples.json` → `upgrades/troops.train.edges.json` (90 edges)
- **Promotion**: `raw/troops.promote.samples.json` → `upgrades/troops.promote.edges.json` (75 edges)
- **Build script**: `scripts/build_troops_edges.py`

### Coverage
- Troop types: infantry, lancer, marksman
- Training tiers: T6, T7, T8, T9, T10, T11
- Promotion tiers: T6→T7, T7→T8, T8→T9, T9→T10, T10→T11
- Quantities: 100, 500, 1000, 5000, 10000

### Data per edge
- Costs: meat, wood, coal, iron (fire_crystal=0 for now)
- time_seconds (base time before buffs)
- power_gained
- event_points: hall_of_chiefs, king_of_icefield, state_of_power

### Validation
- Linearity check: PASSED (costs scale exactly with quantity)
- No missing tiers, no duplicates

### Source
- One Chilled Gamer Troop Calculator: https://onechilledgamer.com/whiteout-survival-troop-cost-calculator/

---

## 4) Buildings - COMPLETE

### Implementation Details
- **Catalog**: `dictionaries/buildings.catalog.json` (27 building types defined)
- **Edges**: `upgrades/buildings.edges.json` (261 edges)
- **Build script**: `scripts/build_buildings_edges.py`

### Coverage
- Level range: L1-L30
- Buildings covered (9 key buildings):
  - furnace, embassy, infantry_camp, lancer_camp, marksman_camp
  - research_center, command_center, infirmary, storehouse
- Each building has 29 edges (L1→L2 through L29→L30)

### Data per edge
- Costs: wood, meat, coal, iron, fire_crystal, refined_fire_crystal
- time_seconds (base time before buffs)
- prereq (Furnace level requirement)

### Source
- whiteoutdata.com building pages

---

## Tier Naming Decision

**Option A: Match Source** (recommended)
- Use exact source naming: "red-0", "red-1", etc.
- Simpler, transparent, traceable

**Option B: Normalize**
- Use numeric tier_index: 17, 18, etc.
- More complex, less readable

**Decision:** Match source (simpler)

---

## 5) Buildings (FC Levels) - COMPLETE

### Implementation Details
- **Edges file**: `upgrades/buildings.fc.edges.json` (313 edges)
- **Build script**: `scripts/build_buildings_fc_edges.py`
- **Validation report**: `validation/buildings.fc.report.json`

### Coverage
- Level range: 30-1 through FC10-0
- Buildings covered (7 FC-capable buildings):
  - furnace (19 edges: 30-1 → FC10-0)
  - embassy (49 edges: 30-1 → FC10-0)
  - command_center (49 edges: 30-1 → FC10-0)
  - infirmary (49 edges: 30-1 → FC10-0)
  - infantry_camp (49 edges: 30-1 → FC10-0)
  - lancer_camp (49 edges: 30-1 → FC10-0)
  - marksman_camp (49 edges: 30-1 → FC10-0)

### Level Structure
- FC levels extend beyond L30 using sub-step notation
- Pattern: `30-1`, `30-2`, `FC1-0`, `FC1-1`, `FC2-0`, ..., `FC10-0`
- Furnace has fewer sub-steps (shorter progression path)
- Other buildings have full 51-level FC progression

### Data per edge
- Costs: wood, meat, coal, iron, fire_crystal, refined_fire_crystal
- time_seconds (base time before buffs)
- prereq.furnace_fc_level (required Furnace FC level)

### Source
- whiteoutsurvival.app building pages

---

## 6) Daybreak Island - COMPLETE

### Implementation Details
- **Raw file**: `raw/daybreak_island.research.json`
- **Edges file**: `upgrades/daybreak_island.tree_of_life.edges.json` (9 edges)

### Coverage
- Tree of Life: L1-L10 upgrades
- Starry Lighthouse (special unlock at L10)

### Key Mechanics
- Primary currency: Life Essence (720 wood = 1 Life Essence)
- Prosperity gates: decorations provide Prosperity to unlock Tree levels
- Combat buffs: Healing Speed, Troops Health/Defense/Lethality

### Data per edge
- Costs: life_essence
- prereq.prosperity (required Prosperity from decorations)
- benefit (combat stat boost)

### Decoration Costs
| Rarity | Life Essence | Prosperity |
|--------|--------------|------------|
| Common | 1,000 | 50 |
| Uncommon | 2,000 | 100 |
| Rare | 3,000 | 200 |
| Epic | 5,000 | 400 |
| Mythic | 10,000 | 1,000 |

### Totals
- Tree of Life L1→L10: 293,500 Life Essence
- Starry Lighthouse: 50,000 Life Essence
- Total: 343,500 Life Essence (247.3M wood equivalent)

### Source
- onechilledgamer.com Daybreak Island guide
