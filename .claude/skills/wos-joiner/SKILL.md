---
name: wos-joiner
description: Identify best rally joiner heroes from user's roster. Use when user asks about joining rallies, garrison defense, or which hero to put first when joining. Explains top-right expedition skill mechanics.
allowed-tools: Read, Glob
---

# WoS Joiner Hero Analyzer

## Purpose
Helps users understand rally joiner mechanics and identify their best joiner heroes.

## Critical Mechanic (VERIFIED)

**When joining a rally, only your FIRST hero's TOP-RIGHT expedition skill is used!**

- Your other 2 heroes contribute NOTHING to rally buffs
- Up to 4 member skills total contribute to a rally
- Member skills CAN stack if they're the same effect

Source: Century Games Help Center + BlueStacks Rally Guide

## Best Joiner Heroes (Verified)

### Attack/Rally Joiners
Heroes whose top-right skill buffs damage:

| Hero | Skill Name | Effect at Max |
|------|------------|---------------|
| **Jessie** | Stand of Arms | +25% DMG dealt (all troops) |

**Why Jessie is #1**: Her "damage dealt" buff affects ALL damage types:
- Normal attacks
- Hero skills
- Pet abilities
- Teammate buffs

This is superior to heroes that only boost basic auto-attack damage.

### Garrison/Defense Joiners
Heroes whose top-right skill reduces damage:

| Hero | Skill Name | Effect at Max |
|------|------------|---------------|
| **Sergey** | Defenders' Edge | -20% DMG taken (all troops) |

**Why Sergey is #1**: Universal damage reduction is the most straightforward defensive buff.

## Instructions

When analyzing joiner heroes:

1. **Check if user has Jessie/Sergey**
   - If yes: Recommend leveling their expedition skills
   - If no: Identify alternatives from their roster

2. **For attack joining**, look for heroes with top-right skills that:
   - Increase damage dealt (all troops)
   - Increase attack (all troops)
   - Increase lethality

3. **For garrison joining**, look for heroes with top-right skills that:
   - Reduce damage taken (all troops)
   - Increase defense (all troops)
   - Reduce enemy attack

4. **Read hero skill data** from WOS_REFERENCE.md:
   ```
   Read file_path="data/WOS_REFERENCE.md"
   ```

## Common Mistakes to Correct

### Mistake 1: "I put my strongest heroes when joining"
**Correction**: Only the FIRST hero's top-right skill matters. Put your best JOINER hero first, not your strongest overall hero.

### Mistake 2: "All my joiner heroes' skills apply"
**Correction**: Only 1 skill per joiner contributes. Your 2nd and 3rd heroes are just carrying troops.

### Mistake 3: "I should gear up my joiner heroes"
**Correction**: Joiner hero gear has minimal impact. Their skill level matters most. Don't waste premium resources on joiner heroes.

## Investment Priority for Joiners

Joiner heroes should have:
- ✅ Functional gear (legendary okay)
- ✅ Appropriate levels
- ✅ HIGH expedition skill levels (this is what counts!)
- ❌ NOT mythic gear
- ❌ NOT premium resources (Essence Stones, Mithril)
- ❌ NOT priority over main heroes

## Output Format

```
## Your Best Joiner Heroes

### For Attack Rallies:
1. **Jessie** - Stand of Arms (+25% DMG dealt)
   - Current Skill Level: 3/5
   - Recommendation: Upgrade to 5 for maximum rally contribution

### For Garrison Defense:
1. **Sergey** - Defenders' Edge (-20% DMG taken)
   - Current Skill Level: 2/5
   - Recommendation: Upgrade for better defensive contribution

### What This Means:
When joining a rally, put Jessie in slot 1. Your other 2 heroes don't contribute skills - they just carry troops.
```
