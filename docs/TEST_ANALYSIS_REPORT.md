# AI & Recommendation System Test Analysis Report

**Date:** January 12, 2026
**Test Profiles:** 5 profiles across 3 users
**Questions Tested:** 39 across 3 main profiles

---

## Executive Summary

The test suite validated the recommendation engine, lineup builder, and AI question routing across different player archetypes. The system is functional with **92.3% of questions handled by rules** (saving AI costs), but several issues were identified that need attention.

### Overall Health
| Component | Status | Notes |
|-----------|--------|-------|
| Recommendation Engine | ⚠️ Needs Work | Skill detection bugs, gear quality issues |
| Lineup Builder | ⚠️ Needs Work | Rally joiner confidence always "low" |
| AI Question Routing | ✅ Good | 92.3% rules, only complex questions go to AI |
| AI Response Quality | ✅ Good | WoS terminology used correctly |

---

## Test Profiles Created

| Profile | Generation | Spending | Furnace | Heroes | Has Farm |
|---------|------------|----------|---------|--------|----------|
| FrostKnight_560 | Gen 10 | Dolphin | FC30 | 28 | Yes |
| FrostKnight_Farm | Gen 10 | F2P | 25 | 4 | - |
| IceWarrior_240 | Gen 4 | F2P | 27 | 13 | No |
| ArcticKing_80 | Gen 2 | Whale | 25 | 15 | Yes |
| ArcticKing_Farm | Gen 2 | F2P | 18 | 4 | - |

---

## Issues Identified

### 🔴 Critical Issues

#### 1. Hero Skill Level Detection Bug
**Location:** `engine/analyzers/hero_analyzer.py`

**Problem:** Recommendations show "currently Lv1" for skills that are actually maxed.

**Evidence:**
```
Gen 10 Dolphin has Jessie with expedition_skills=(5,5,5)
Recommendation: "Max Jessie's expedition skill (currently Lv1)"
```

**Impact:** Users see incorrect skill levels, recommendations are misleading.

**Fix:** The skill level retrieval in `_check_joiner_skills()` likely uses wrong attribute names or doesn't access UserHero skills correctly.

---

#### 2. Chief Gear Quality Not Recognized
**Location:** `engine/analyzers/gear_advisor.py`

**Problem:** Recommends upgrading Ring to Legendary even when user has Mythic.

**Evidence:**
```
Gen 10 Dolphin has ring_quality=7 (Mythic), ring_level=50
Recommendation: "Focus on upgrading Ring to Legendary"
```

**Impact:** Irrelevant recommendations for advanced players.

**Fix:** Gear advisor needs to check for Mythic quality (7) not just Legendary (6).

---

#### 3. Rally Joiner Confidence Always "Low"
**Location:** `engine/lineup_builder.py` or `engine/recommendation_engine.py`

**Problem:** Even with optimal joiner heroes (Jessie, Sergey) at high levels, confidence is "low".

**Evidence:**
```
Gen 10 Dolphin (owns Jessie Lv70 5★, Sergey Lv80 5★)
rally_joiner_attack: low confidence
rally_joiner_defense: low confidence
```

**Expected:** Should be "high" when user owns the correct joiner hero.

**Fix:** The lineup confidence calculation needs to check if user actually owns the recommended joiner.

---

### 🟡 Medium Issues

#### 4. Recommendation Diversity for Main Accounts
**Problem:** Main accounts get 9/10 hero recommendations, only 1 gear.

**Evidence:**
```
Gen 10 Dolphin (Main): {'hero': 9, 'gear': 1}
Gen 4 F2P: {'hero': 9, 'gear': 1}
Gen 2 Whale (Main): {'hero': 9, 'gear': 1}
```

**Impact:** Limited actionable advice beyond hero upgrades.

**Suggestion:** Add diversity weighting to ensure mix of categories:
- At least 1 gear recommendation
- At least 1 progression recommendation for mid-game
- Chief charms for players at FC25+

---

#### 5. Spending Profile Not Affecting Recommendations
**Problem:** Whale and F2P accounts get very similar recommendations.

**Evidence:**
```
Gen 2 Whale: Same hero skill upgrade recommendations as F2P
No whale-specific advice like "Push all heroes to max" or "Invest in multiple lineups"
```

**Suggestion:** Add spending-profile-aware logic:
- F2P: Focus on 1-2 heroes, efficiency matters
- Dolphin: Can spread investment across 3-4 heroes
- Whale: Max everything, gear all core heroes

---

#### 6. Farm Account Detection Not Used
**Problem:** Farm accounts marked with `is_farm_account=True` but recommendations don't adjust.

**Evidence:**
```
Farm accounts get "Push Furnace to L30 for FC unlock" - not a farm priority
Should see: "Transfer resources to main", "Maximize gathering efficiency"
```

**Suggestion:** Add farm-specific recommendation logic that focuses on:
- Gathering optimization
- Resource transfer timing
- Minimal combat investment

---

### 🟢 Working Well

#### 7. AI Question Routing
**Status:** Excellent

| Metric | Value |
|--------|-------|
| Rules Engine | 36/39 (92.3%) |
| AI Fallback | 3/39 (7.7%) |
| Errors | 0 |

Questions correctly routed to rules:
- Best rally joiner? ✅
- Bear trap lineup? ✅
- What troop ratio for Crazy Joe? ✅
- What should I upgrade next? ✅
- How do I prepare for SvS? ✅

Questions correctly routed to AI:
- "Analyze my account and tell me what I'm doing wrong" ✅

---

#### 8. Lineup Hero Selection
**Status:** Good (when heroes are owned)

| Mode | Heroes | Troop Ratio | Assessment |
|------|--------|-------------|------------|
| Bear Trap | Jeronimo, Molly, Philly | 0/10/90 | ✅ Correct |
| Crazy Joe | Jeronimo, Natalia, Flint | 90/10/0 | ✅ Correct |
| Garrison | Sergey, Natalia, Bahiti | 60/25/15 | ✅ Correct |
| SvS March | Jeronimo, Alonso, Natalia | 40/20/40 | ✅ Correct |

---

#### 9. AI Response Quality
**Status:** Good

Sample AI response (Gen 10 Dolphin):
```
"Chief, your account is in solid shape, but there are a few strategic
adjustments that could greatly enhance your efficiency, especially given
your high priorities for SvS and Rally..."
```

✅ Uses "Chief" terminology
✅ References user's priorities
✅ Provides actionable advice
✅ Doesn't hallucinate hero names

---

## Recommended Fixes (Priority Order)

### Priority 1: Critical Bugs

1. **Fix skill level detection** in `hero_analyzer.py`
   - Check attribute names: `expedition_skill_1_level` vs `expedition_skill`
   - Add debug logging to trace where level detection fails

2. **Fix gear quality check** in `gear_advisor.py`
   - Add Mythic (quality=7) to quality checks
   - Don't recommend upgrading gear that's already at target quality

3. **Fix rally joiner confidence** in lineup builder
   - Check if user owns the recommended hero
   - Set confidence to "high" when joiner is owned with skill level 3+

### Priority 2: Enhancements

4. **Add recommendation diversity**
   - Limit hero recommendations to 5-6 max
   - Force include at least one from each relevant category

5. **Add spending profile logic**
   - Adjust target levels based on spending profile
   - Whale: "Max all S+ heroes"
   - F2P: "Focus on Alonso OR Molly, not both"

6. **Add farm account logic**
   - Detect `is_farm_account=True`
   - Replace combat recommendations with gathering/economy focus

### Priority 3: Nice to Have

7. **Add more AI-routed questions**
   - "What's my biggest weakness?" → AI
   - "How do I maximize power for SvS?" → AI
   - These need contextual analysis beyond rules

8. **Generation-aware hero recommendations**
   - Gen 10 player shouldn't see "Acquire Gen 2 heroes"
   - Focus on current and next generation heroes

---

## Files to Modify

| File | Issue | Change |
|------|-------|--------|
| `engine/analyzers/hero_analyzer.py` | Skill detection | Fix attribute access |
| `engine/analyzers/gear_advisor.py` | Mythic quality | Add quality=7 check |
| `engine/recommendation_engine.py` | Lineup confidence | Check hero ownership |
| `engine/analyzers/hero_analyzer.py` | Diversity | Add category limits |
| `engine/request_classifier.py` | AI routing | Add weakness/analysis patterns |

---

## Test Users Available

The following test users remain in the database for manual testing:

| Username | Password | Profile Type |
|----------|----------|--------------|
| test_gen10_dolphin | test123 | Gen 10 Dolphin + Farm |
| test_gen4_f2p | test123 | Gen 4 F2P |
| test_gen2_whale | test123 | Gen 2 Whale + Farm |

---

## Next Steps

1. Fix critical bugs (skill detection, gear quality, lineup confidence)
2. Run test suite again to verify fixes
3. Add spending profile and farm account logic
4. Expand AI routing for analytical questions
5. Consider adding more test questions for edge cases

---

*Report generated by comprehensive AI test suite*
