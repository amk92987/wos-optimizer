---
name: wos-joiner
description: Identify best rally joiner heroes from user's roster. Use when user asks about joining rallies, garrison defense, or which hero to put first when joining. Explains expedition skill mechanics.
allowed-tools: Read, Glob
---

# WoS Joiner Hero Analyzer

## Purpose
Helps users understand rally joiner mechanics and identify their best joiner heroes.

## Critical Mechanic

**When joining a rally, only your LEFTMOST hero's expedition skill is used!**

- Your other 2 heroes contribute NOTHING to rally buffs
- Only the **top 4 highest SKILL LEVEL** expedition skills from all joiners apply
- This is based on **skill level**, not player power
- Member skills CAN stack if they're the same effect

**IMPORTANT**: A high-level wrong skill can bump out a lower-level right skill. Example: A level 5 Sergey (defensive) would bump out a level 3 Jessie (+25% damage) - even though Jessie's skill is far more valuable for attacks.

## Best Attack/Rally Joiner Heroes

Heroes with expedition skills that buff rally damage:

| Hero | Gen | Skill Effect |
|------|-----|--------------|
| **Jeronimo** | 1 | Infantry ATK multiplier |
| **Jessie** | 5 | +25% DMG dealt (all troops) |
| **Jasser** | 7 | Rally damage buff |
| **Seo-yoon** | 8 | Rally damage buff |

**Why Jessie is top tier**: Her "damage dealt" buff affects ALL damage types:
- Normal attacks
- Hero skills
- Pet abilities
- Teammate buffs

## Best Garrison/Defense Joiner Heroes

Heroes with expedition skills that reduce damage taken:

| Hero | Gen | Skill Effect |
|------|-----|--------------|
| **Sergey** | 1 | -20% DMG taken (all troops) |

## When to Join with TROOPS ONLY (No Heroes)

If you don't have one of the attack joiner heroes above, **join with troops only**:
- Don't put any heroes in the march
- This prevents your leveled-up wrong skill from bumping out a valuable damage multiplier
- Your troops still contribute to rally damage

## Instructions

When analyzing joiner heroes:

1. **Check user's generation** to see which joiner heroes are available
2. **For attack joining**: Only use Jeronimo, Jessie, Jasser, or Seo-yoon
3. **For garrison joining**: Sergey is the best option
4. **If they don't have these heroes**: Recommend joining with troops only

## Common Mistakes to Correct

### Mistake 1: "I put my strongest heroes when joining"
**Correction**: Only the LEFTMOST hero's expedition skill matters. Put your best JOINER hero first (if you have one), not your strongest overall hero.

### Mistake 2: "All my joiner heroes' skills apply"
**Correction**: Only 1 skill per joiner contributes. Your 2nd and 3rd heroes are just carrying troops.

### Mistake 3: "I'll just use any hero when joining"
**Correction**: If your hero has a high-level skill that's wrong for the situation, it could bump out someone else's valuable skill. Better to join with troops only.

## Investment Priority for Joiners

Joiner heroes should have:
- ✅ Functional gear (legendary okay)
- ✅ Appropriate levels
- ✅ HIGH expedition skill levels (this determines if your skill gets used!)
- ❌ NOT mythic gear
- ❌ NOT premium resources (Essence Stones, Mithril)
- ❌ NOT priority over main heroes

## Output Format

```
## Your Best Joiner Heroes

### For Attack Rallies (Bear Trap, Castle Attack):
1. **Jessie** - +25% DMG dealt (all troops)
   - Current Skill Level: 3/5
   - Recommendation: Upgrade to 5 for maximum rally contribution

### For Garrison Defense:
1. **Sergey** - -20% DMG taken (all troops)
   - Current Skill Level: 2/5
   - Recommendation: Upgrade for better defensive contribution

### If You Don't Have Jessie/Jeronimo/Jasser/Seo-yoon:
Join with TROOPS ONLY (no heroes) to avoid bumping out someone else's valuable damage skill.
```
