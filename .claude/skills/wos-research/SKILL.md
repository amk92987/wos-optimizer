---
name: wos-research
description: Fetch latest Whiteout Survival game data from verified sources (WoS Wiki, BlueStacks guides). Use when updating hero skills, troop ratios, or game mechanics. Updates WOS_REFERENCE.md with cited sources.
allowed-tools: WebFetch, Read, Write, Glob
---

# WoS Research - Fetch Verified Game Data

## Purpose
Fetches current, verified game data from trusted sources and updates the project's reference files.

## Verified Sources (in priority order)
1. **WoS Wiki** - https://www.whiteoutsurvival.wiki/
   - Hero skill pages: `/heroes/{hero-name}/`
   - Server timeline: `/events/server-timeline-server-age/`
   - Rally guide: `/advanced-guide-to-hero-rallies-buff/`

2. **Century Games Help Center** - https://centurygames.helpshift.com/
   - Official mechanics clarifications
   - Skill stacking rules

3. **BlueStacks Guides** - https://www.bluestacks.com/blog/game-guides/white-out-survival/
   - Rally joiner guide
   - Hero combinations
   - Event guides

4. **Community Guides**
   - A Jack Of Everything (troop ratios)
   - One Chilled Gamer (tier lists, event guides)
   - LootBar (rally formation)

## Instructions

When researching WoS data:

1. **Identify what needs updating** - Check user request or look at data/WOS_REFERENCE.md for outdated info

2. **Fetch from verified sources** - Use WebFetch to pull data from sources above
   ```
   WebFetch url="https://www.whiteoutsurvival.wiki/heroes/jessie/"
   prompt="Extract all expedition skills with names, effects, and scaling percentages"
   ```

3. **Cross-reference when possible** - If multiple sources exist, compare them

4. **Update reference files**:
   - `data/WOS_REFERENCE.md` - Main reference document
   - `data/verified_research.json` - Structured data
   - `data/heroes.json` - Hero skill data (if skill info found)

5. **Always cite sources** - Include URLs and access dates

## Output Format

After researching, provide:
- Summary of what was found
- What files were updated
- Any discrepancies between sources
- Confidence level (high/medium/low) based on source quality

## Example Usage

User: "Update Jessie's skill data"

1. Fetch https://www.whiteoutsurvival.wiki/heroes/jessie/
2. Extract expedition skills with percentages
3. Update data/WOS_REFERENCE.md with new data
4. Update data/heroes.json if skill structure exists
5. Report findings with source citation

## Important Notes

- NEVER make up skill percentages or effects
- If data conflicts between sources, note the discrepancy
- Prefer official sources (WoS Wiki, Century Games) over community guides
- Always include source URLs in updates
