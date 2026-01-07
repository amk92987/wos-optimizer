# WoS Optimizer Guides Index

## Purpose
These guides provide detailed reasoning and explanations for optimizer recommendations. Each guide is structured to answer "why" not just "what".

## Available Guides

### Hero Lineups (`hero_lineup_reasoning.json`)
**Use when:** Selecting heroes for rallies, SvS, exploration, or any combat

**Key sections:**
- Critical concepts (exploration vs expedition skills, rally joiner mechanic)
- Rally attack joiner (Jessie, Jeronimo best - avoid Sergey)
- Rally defense joiner (Sergey best)
- Rally lead and SvS march hero selection
- Exploration/PvE team building
- Common mistakes (wrong hero in slot 1, spreading manuals thin)

**Critical rule:** When joining rallies, only leftmost hero's top-right expedition skill matters. If you don't have a good joiner, send troops only.

---

### Daybreak Island (`daybreak_island_priorities.json`)
**Use when:** Planning Life Essence investment, Tree of Life upgrades, decoration strategy

**Key sections:**
- Tree of Life buff progression (L6 = first combat buff)
- Decoration efficiency comparison (Mythic best)
- Priorities by spending profile
- Common mistakes (building decorations beyond gates)

**Critical rule:** Tree of Life is the goal - decorations are just means to unlock it. Rush L6 for Troops Health +5%.

---

### Research Priorities (`research_priorities.json`)
**Use when:** Deciding what to research, using speedups, planning research path

**Key sections:**
- Tree overview (Growth, Economy, Battle)
- Tool Enhancement priority (CRITICAL - must max VII first)
- Priorities by game phase
- Priorities by spending profile
- Priorities by alliance role
- Common mistakes (Economy tree early, spreading speedups)

**Critical rule:** Tool Enhancement VII reduces ALL future research by 35%. This is THE mid-game milestone.

---

### Recommendation Reasons (`../optimizer/recommendation_reasons.json`)
**Use when:** Displaying "why" explanations for optimizer suggestions

**Key sections:**
- System reasons (why each upgrade system matters)
- Recommendation templates (unlock gates, efficiency milestones, power gains)
- Hero lineup reasons (quick reference for scenarios)
- "Why not" reasons (explaining why something isn't recommended)

---

## Guide Structure

Each guide follows this structure:
1. **Overview** - What the system is, when it unlocks
2. **Key concepts** - Critical rules and mechanics
3. **Priorities by profile** - Recommendations for F2P, minnow, dolphin, whale
4. **Priorities by role** - Rally lead vs filler vs farmer
5. **Common mistakes** - What to avoid and why
6. **Quick reference** - TL;DR summary

## Integration with Optimizer

The optimizer should:
1. Load relevant guide based on recommendation type
2. Include `reason` field in each recommendation
3. Reference specific guide sections for detailed explanations
4. Adjust recommendations based on `spending_profile` and `alliance_role`

## Adding New Guides

When creating a new guide:
1. Use JSON format with clear section structure
2. Include `priorities_by_spending_profile` section
3. Include `priorities_by_alliance_role` if relevant
4. Include `common_mistakes` section
5. Add entry to this INDEX.md
