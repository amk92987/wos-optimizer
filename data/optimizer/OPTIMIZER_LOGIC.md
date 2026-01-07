# WoS Optimizer Decision Logic

## Overview

The optimizer recommends upgrade paths based on three key inputs:
1. **Player State** - Where are they in the game?
2. **Spending Profile** - What resources are scarce for them?
3. **Priority Focus** - What do they want to optimize for?

## Input Files

| File | Purpose |
|------|---------|
| `progression_phases.json` | Defines game phases by Furnace level |
| `system_unlocks.json` | Maps when each system becomes available |
| `decision_rules.json` | Priority weights and phase-specific rules |
| `player_settings_schema.json` | Player profile structure and spending tiers |

## Decision Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     PLAYER INPUTS                               │
├─────────────────────────────────────────────────────────────────┤
│  Furnace Level → Determines PHASE                               │
│  Spending Profile → Determines SCARCITY weights                 │
│  Priority Focus → Determines SYSTEM weights                     │
│  Alliance Role → Applies ROLE boosts                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PHASE DETECTION                                │
├─────────────────────────────────────────────────────────────────┤
│  F1-F18  → early_game                                           │
│  F19-F29 → mid_game                                             │
│  F30/FC1-FC4 → late_game                                        │
│  FC5+ → endgame                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               AVAILABLE SYSTEMS FILTER                          │
├─────────────────────────────────────────────────────────────────┤
│  Only consider systems player has UNLOCKED                      │
│  Check: furnace_level, state_age_days, state_generation         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               PRIORITY CALCULATION                              │
├─────────────────────────────────────────────────────────────────┤
│  base_weight = priority_focus_weight[system]                    │
│  role_boost = alliance_role_boost[system]                       │
│  scarcity_penalty = spending_profile_scarcity[currency]         │
│                                                                 │
│  final_score = (base_weight + role_boost) * scarcity_factor     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              RECOMMENDATION OUTPUT                              │
├─────────────────────────────────────────────────────────────────┤
│  Ranked list of upgrade actions by final_score                  │
│  Filtered by efficiency_threshold for spending profile          │
│  Annotated with milestone targets for current phase             │
└─────────────────────────────────────────────────────────────────┘
```

## Spending Profile Impact

### F2P Players
- **Skip**: Chief Gear beyond Red-1, Charms L12+, Pets beyond L60
- **Focus**: Event efficiency, milestone unlocks, bottleneck resources
- **Rule**: Only recommend upgrades with efficiency > 0.8

### Minnow/Low Spender
- **Skip**: Whale-tier upgrades (max mastery, L16 charms)
- **Focus**: Strategic pack purchases, event participation
- **Rule**: Efficiency threshold 0.7

### Dolphin/Mid Spender
- **Skip**: Nothing automatically (all systems accessible)
- **Focus**: Balanced progression, event optimization
- **Rule**: Efficiency threshold 0.5

### Orca/Heavy Spender
- **Focus**: Speed of progression, power milestones
- **Rule**: Efficiency threshold 0.3

### Whale
- **Focus**: Marginal optimization, completionism
- **Rule**: No efficiency gate, optimize for time

## Phase-Specific Priorities

### Early Game (F1-F18)
| Priority | Action | Why |
|----------|--------|-----|
| 1 | Furnace to L19 | Unlocks Daybreak Island |
| 2 | Research Center + Tool Enhancement | Speed up everything |
| 3 | Troop training capacity | Foundation for power |

### Mid Game (F19-F29)
| Priority | Action | Why |
|----------|--------|-----|
| 1 | Furnace to L30 | FC unlock is game-changing |
| 2 | Tool Enhancement VII | Max research speed |
| 3 | Chief Charms to L11 | Max before Gen 7 gate |
| 4 | Pets to L50-60 | Combat and utility skills |
| 5 | Daybreak Tree of Life L6+ | Combat buffs |

### Late Game (FC Era)
| Priority | Action | Why |
|----------|--------|-----|
| 1 | FC Furnace progression | Unlocks everything else |
| 2 | War Academy | Massive troop efficiency |
| 3 | Hero Gear Mastery | Combat stats |
| 4 | T10 troops | Power tier milestone |

### Endgame (FC5+)
| Priority | Action | Why |
|----------|--------|-----|
| 1 | FC10 completion | Max buildings |
| 2 | Mastery L20 | Max hero stats |
| 3 | Charms L12-16 | Gen 7+ content |
| 4 | T11 dominance | Top tier troops |

## Resource Allocation Rules

### Speedups
- **Primary**: Furnace pushes, Research, War Academy
- **F2P Rule**: Hoard for Furnace events
- **Spender Rule**: Use freely, buy more

### Fire Crystals
- **Priority Order**: FC Furnace > War Academy > Other FC buildings
- **F2P Rule**: Never waste on secondary buildings until Furnace capped
- **Spender Rule**: Parallel progression acceptable

### Essence Stones
- **Rule**: Focus one hero at a time for Mastery
- **Why**: Partial mastery across heroes gives less value than maxing one

### Charm Materials
- **Rule**: Level all 6 slots evenly
- **Why**: Each slot gives independent stats

### Pet Materials
- **Rule**: SSR pets first (Snow Ape, Cave Lion)
- **F2P Rule**: Don't push past L60 unless SSR
- **Why**: SSR skill value + level cap

## Efficiency Thresholds

The optimizer filters recommendations based on spending profile:

| Profile | Threshold | Meaning |
|---------|-----------|---------|
| F2P | 0.8 | Only high-efficiency upgrades |
| Minnow | 0.7 | Skip whale-only content |
| Dolphin | 0.5 | Most content accessible |
| Orca | 0.3 | Almost everything viable |
| Whale | 0.0 | No filtering |

Efficiency is calculated as:
```
efficiency = power_gain / gem_equivalent_cost
```

Using shadow prices from `conversions/gem_shadow_prices.json`.

## Integration Points

### Edge Files Used
- `upgrades/buildings.edges.json` - Building L1-30
- `upgrades/buildings.fc.edges.json` - Building FC levels
- `upgrades/war_academy.steps.json` - War Academy
- `upgrades/chief_gear.steps.json` - Chief Gear
- `upgrades/hero_gear.mastery.edges.json` - Hero Gear Mastery
- `upgrades/chief_charms.edges.json` - Chief Charms
- `upgrades/pets.advancement.edges.json` - Pet advancement
- `upgrades/troops.train.edges.json` - Troop training
- `upgrades/troops.promote.edges.json` - Troop promotion
- `upgrades/daybreak_island.tree_of_life.edges.json` - Daybreak Island

### Conversion Files Used
- `conversions/gem_shadow_prices.json` - Resource → gem values
- `conversions/scarcity_profiles.json` - Player-specific multipliers

## Future Enhancements

1. **Event Optimization**: Factor in active events for timing recommendations
2. **Power Calculator**: Integrate power gain per upgrade for ROI
3. **Goal Pathfinding**: "How do I get to X?" shortest path calculation
4. **Inventory Awareness**: Recommend based on what player actually has
