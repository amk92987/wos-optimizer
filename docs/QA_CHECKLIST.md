# Comprehensive QA Checklist

Last Updated: 2026-01-12

## Areas Checked

### 1. HTML/Markdown Rendering
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| Self-closing img tags | 1_Hero_Tracker.py | FIXED | Line 340 - added `/>` |
| Self-closing br/hr tags | 7_Save_Load.py, 15_Admin.py | OK | Working, low priority |
| Split div tags | 15_Admin.py | OK | Lines 349/377 - fragile but functional |
| Proper HTML escaping | All pages | OK | unsafe_allow_html used appropriately |

### 2. AI Advisor Error Handling
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| Error message sanitization | 6_AI_Advisor.py | FIXED | Line 322-331 - hides API details |
| API exception handling | recommendation_engine.py | FIXED | Lines 444-459 - user-friendly messages |
| JSON parsing safety | ai_recommender.py | FIXED | Lines 478-504 - no raw content exposure |
| Rate limit handling | 6_AI_Advisor.py | OK | Proper limits and cooldowns |
| Conversation logging | 6_AI_Advisor.py | OK | Logs properly for training data |

### 3. Lineup Recommender
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| Database attribute names | 5_Lineups.py | FIXED | Lines 88-91 - stars, skill levels |
| Null checks for profile data | 5_Lineups.py | OK | server_age_days handled |
| Hero availability checks | 5_Lineups.py | OK | get_best_available_hero() working |
| 3-hero vs 5-hero structure | 5_Lineups.py | OK | Different dict keys but handled |
| Hardcoded hero names | 5_Lineups.py | MONITOR | Works but should verify heroes.json sync |

### 4. Power Multipliers
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| Chief gear tier mapping | power_optimizer.py | REVIEW | Tier 35 max vs 42 max in data |
| Chief charm levels | power_optimizer.py | OK | 1-16 levels, 9-100% bonus |
| Hero power formula | power_optimizer.py | DOCUMENTED | Estimated, not game data |
| Troop power values | troop_data.json | OK | Verified T1-T11 values |
| War Academy power | war_academy.steps.json | OK | Exact values from game |

### 5. Dynamic Hero/Gear/Charm Displays
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| Hero skill descriptions | 1_Hero_Tracker.py | OK | Fallback to "coming soon" |
| Gear tier lookup | 2_Chief_Tracker.py | FIXED | Line 246 - null check added |
| Charm bonus display | 2_Chief_Tracker.py | OK | Defaults to 9.0% if missing |
| Hero image loading | 1_Hero_Tracker.py | OK | Fallback to class symbol |
| Mythic gear attributes | 1_Hero_Tracker.py | OK | Safe getattr with defaults |

### 6. Recommendation Engine
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| Hero name validation | hero_analyzer.py | OK | Lookup fallback to empty dict |
| Error handling | recommendation_engine.py | FIXED | User-friendly error messages |
| Hardcoded hero references | Multiple files | MONITOR | Should sync with heroes.json |
| Special character handling | All analyzers | OK | No issues found |

## Issues Fixed This Session

### Critical (Blocking)
1. **Unclosed `<img>` tag** - 1_Hero_Tracker.py:340
   - Problem: HTML rendering could break
   - Fix: Added self-closing `/>` to img tag

2. **Wrong database attributes** - 5_Lineups.py:88-91
   - Problem: `star_rank` and `exploration_skill_level` don't exist
   - Fix: Changed to `stars`, `exploration_skill_1_level`, `expedition_skill_1_level`

### High Priority
3. **Raw API errors shown to users** - 6_AI_Advisor.py:322-323
   - Problem: Technical error messages visible to users
   - Fix: Added error categorization with user-friendly messages

4. **Null check missing** - 2_Chief_Tracker.py:246
   - Problem: AttributeError if gear_data is None
   - Fix: Added `if gear_data else 1` check

5. **JSON parsing crash** - ai_recommender.py:491-492
   - Problem: `content` variable undefined in except block, raw content exposed
   - Fix: Initialized content to None, removed raw content from errors

6. **AI exception exposure** - recommendation_engine.py:444-449
   - Problem: Raw exception strings shown to users
   - Fix: Categorized errors with sanitized messages

## Comprehensive System Review (Phase 2)

### 7. Session State Management
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| AI Advisor chat_messages access | 6_AI_Advisor.py | FIXED | Lines 708-757 - now uses .get() |
| Dynamic state cleanup | Admin pages | MONITOR | Keys accumulate, low priority |
| Auth state initialization | database/auth.py | OK | Centralized in init_session_state() |
| Profile state access | 7_Save_Load.py | OK | Safe patterns used |

### 8. Database Integrity
| Check | Files | Status | Notes |
|-------|-------|--------|-------|
| Cascade deletes User→Profiles | models.py | POST-LAUNCH | Will orphan data if user deleted |
| Cascade deletes Profile→Children | models.py | POST-LAUNCH | Same issue for profile deletion |
| Foreign key validation | models.py | OK | Constraints in place |
| Session management | db.py | OK | Works for expected traffic |
| Enum validation (role, spending) | models.py | POST-LAUNCH | String columns, no constraints |

### 9. System Features Verified
| Feature | Pages | Status | Edge Cases Noted |
|---------|-------|--------|------------------|
| User Registration | auth_register.py | OK | No email verification (documented) |
| User Login | auth_login.py | OK | Bcrypt works correctly |
| Hero Tracker | 1_Hero_Tracker.py | OK | 42 heroes, all have images |
| Chief Gear/Charms | 2_Chief_Tracker.py | OK | 42 tiers, 16 charm levels |
| Lineups | 5_Lineups.py | OK | Generation-aware recommendations |
| AI Advisor | 6_AI_Advisor.py | OK | Rate limiting, error handling |
| Admin Dashboard | Admin pages (10) | OK | CRUD, impersonation working |
| Settings | 13_Settings.py | OK | All profile fields saved |

## Known Issues (Not Blocking)

### Medium Priority
1. **Split div tags in Admin** - 15_Admin.py:349/377
   - Pattern is fragile but works in practice
   - Consider refactoring to single markdown call

2. **Hero power formula is estimated** - power_optimizer.py:324-325
   - Uses arbitrary coefficients (500 base, +20/level)
   - Should be documented as estimate, not exact

3. **Chief gear tier mapping** - power_optimizer.py:146
   - Mythic quality maps to tier 35, but data shows tier 42 max
   - Needs verification against game data

4. **Missing cascade deletes** - models.py
   - User deletion leaves orphaned profiles, heroes, inventory
   - Recommend adding cascade='all, delete-orphan' post-launch

5. **Dynamic session state accumulation** - Admin pages
   - Keys like `editing_{id}` accumulate without cleanup
   - Low impact, monitor for memory issues

### Low Priority
1. **Skill description fallbacks** - 1_Hero_Tracker.py
   - Shows "Skill description coming soon" for missing data
   - All Gen 1-14 heroes now have descriptions

2. **Hardcoded hero names** - Multiple files
   - Works as long as heroes.json is in sync
   - Consider dynamic lookup validation

3. **No password reset flow**
   - Admin can reset via Admin → Users page
   - Email setup planned post-launch

4. **Rate limit uses UTC midnight**
   - User sees reset at different local times
   - Acceptable for initial launch

## Recommended Future Checks

### Before Each Release
- [ ] Run app locally and test all pages
- [ ] Check AI Advisor with valid and invalid API keys
- [ ] Test lineup recommendations with empty/partial hero roster
- [ ] Verify new heroes are in heroes.json with skill descriptions
- [ ] Check chief gear/charm displays at various tiers

### Quarterly Review
- [ ] Verify power multiplier formulas against game updates
- [ ] Check for deprecated heroes or renamed heroes
- [ ] Review error message handling for new API behaviors
- [ ] Audit hardcoded hero references

### After Game Updates
- [ ] Update heroes.json with new heroes/skill descriptions
- [ ] Verify tier lists are current
- [ ] Check if gear tier system changed
- [ ] Update troop power values if rebalanced

## Files Modified This Session

| File | Lines Changed | Type |
|------|---------------|------|
| pages/1_Hero_Tracker.py | 340 | Fix - self-closing img tag |
| pages/5_Lineups.py | 88-91 | Fix - correct DB attributes |
| pages/6_AI_Advisor.py | 322-331, 708-757 | Fix - error handling, session state |
| pages/2_Chief_Tracker.py | 246-247 | Fix - null check |
| engine/recommendation_engine.py | 444-459 | Fix - error sanitization |
| engine/ai_recommender.py | 478-504 | Fix - JSON parsing safety |
| deploy/AWS_DEPLOYMENT_CHECKLIST.md | 497-529 | Add - email setup section |
| docs/QA_CHECKLIST.md | All | Add - comprehensive checklist |

## Testing Commands

```bash
# Run the app
streamlit run app.py

# Test specific pages
# Navigate to: Hero Tracker, Chief Tracker, Lineups, AI Advisor

# Check for Python errors
python -c "from pages import *"  # Basic import check
```
