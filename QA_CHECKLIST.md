# QA Checklist - WoS Optimizer

Comprehensive quality assurance process for the Whiteout Survival Optimizer web application.

**Last Updated:** 2026-01-13

---

## Table of Contents

1. [Quick Smoke Test](#quick-smoke-test)
2. [Visual/Rendering Checks](#visualrendering-checks)
3. [Functional Testing](#functional-testing)
4. [Data Integrity](#data-integrity)
5. [Error Handling](#error-handling)
6. [Performance](#performance)
7. [Security](#security)
8. [Accessibility](#accessibility)
9. [Browser/Device Compatibility](#browserdevice-compatibility)
10. [Pre-Release Checklist](#pre-release-checklist)

---

## Quick Smoke Test

Run these checks after any significant change (5 minutes):

- [ ] App starts without errors: `streamlit run app.py`
- [ ] All pages load without Python exceptions
- [ ] Database connection works (Hero Tracker shows heroes)
- [ ] No visible HTML tags in rendered content
- [ ] No encoding errors (no `Ã×`, `â€™`, etc.)

---

## Visual/Rendering Checks

### HTML Rendering Issues

Common problems to look for:

| Issue | Example | Where to Check |
|-------|---------|----------------|
| Unclosed tags visible | `</div>` showing in text | All pages with custom HTML |
| HTML entities unescaped | `&amp;` instead of `&` | Tips, descriptions |
| Broken markdown | `**text` without closing | All markdown content |
| CSS not applied | Plain unstyled elements | Hero cards, tip cards |

**Pages with Custom HTML to Verify:**

- [ ] `11_Quick_Tips.py` - All tip cards render correctly
- [ ] `1_Hero_Tracker.py` - Hero cards, tier badges, star ratings
- [ ] `10_Combat.py` - Stat comparisons, tables
- [ ] `00_Beginner_Guide.py` - Guide content, collapsibles
- [ ] `14_Daybreak_Island.py` - Decoration cards

### Encoding Issues

| Check | What to Look For |
|-------|------------------|
| UTF-8 characters | Proper `×`, `→`, `★`, `☆` rendering |
| Hero names | Special characters in names render correctly |
| Game terms | "SvS", "PvE", etc. not garbled |

**Test these specific characters:**
- [ ] Multiplication sign: `×` (not `Ã—`)
- [ ] Arrows: `→`, `←`, `↑`, `↓`
- [ ] Stars: `★`, `☆`
- [ ] Checkmarks: `✓`, `✗`

### Layout Issues

- [ ] Cards don't overflow containers
- [ ] Tables fit on screen (horizontal scroll if needed)
- [ ] Expanders open/close properly
- [ ] Tabs switch without layout shift
- [ ] Sidebar collapses correctly on mobile

---

## Functional Testing

### Core Features

#### Hero Tracker (`1_Hero_Tracker.py`)

| Test | Expected Result | Verified |
|------|-----------------|----------|
| View hero list | All heroes display with images | [ ] |
| Toggle "Owned" checkbox | Hero saves owned status | [ ] |
| Edit hero level | Level persists after page refresh | [ ] |
| Edit star rating | Stars update visually | [ ] |
| Edit skill levels | Skills save correctly | [ ] |
| Edit hero gear | Gear slots save quality/level | [ ] |
| Hero image loading | No broken images | [ ] |
| Filter by generation | Correct heroes shown | [ ] |
| Filter by owned | Only owned heroes shown | [ ] |

#### Chief Tracker (`2_Chief_Tracker.py`)

| Test | Expected Result | Verified |
|------|-----------------|----------|
| Chief gear display | Shows all 6 slots | [ ] |
| Gear tier selection | Tiers save correctly | [ ] |
| Set bonus display | Shows 3pc/6pc bonuses | [ ] |
| Chief charms section | Charms editable | [ ] |

#### Backpack/Inventory (`3_Backpack.py`)

| Test | Expected Result | Verified |
|------|-----------------|----------|
| Item list loads | Items display | [ ] |
| Add item quantity | Quantity saves | [ ] |
| OCR upload (if enabled) | Parses screenshot | [ ] |

#### Lineups (`5_Lineups.py`)

| Test | Expected Result | Verified |
|------|-----------------|----------|
| Game mode selection | Different modes available | [ ] |
| Hero selection | Can pick from owned heroes | [ ] |
| Lineup saves | Lineup persists | [ ] |
| Recommendations work | Suggests heroes | [ ] |

#### AI Advisor (`6_AI_Advisor.py`)

| Test | Expected Result | Verified |
|------|-----------------|----------|
| Question input works | Can type question | [ ] |
| Submit returns answer | Response displays | [ ] |
| Rate limiting works | Shows limit message | [ ] |
| Thumbs up/down works | Feedback saves | [ ] |
| Error handling | Graceful API errors | [ ] |

#### Quick Tips (`11_Quick_Tips.py`)

| Test | Expected Result | Verified |
|------|-----------------|----------|
| All tabs load | 4 tabs display | [ ] |
| Critical Tips shows tips | Tips render | [ ] |
| Alliance tab shows tips | R4/R5 tips display | [ ] |
| Common Mistakes shows | Mistakes render | [ ] |
| By Category expanders work | Categories expand | [ ] |
| Priority badges display | Colors correct | [ ] |

### Authentication & Admin

#### Login/Register

| Test | Expected Result | Verified |
|------|-----------------|----------|
| Login with valid creds | Redirects to home | [ ] |
| Login with invalid creds | Shows error | [ ] |
| Register new user | Account created | [ ] |
| Register duplicate | Shows error | [ ] |
| Logout works | Session ends | [ ] |

#### Admin Pages

| Test | Expected Result | Verified |
|------|-----------------|----------|
| Admin can access admin pages | Pages load | [ ] |
| Non-admin cannot access | Redirects away | [ ] |
| User impersonation works | Sees user view | [ ] |
| Switch back works | Returns to admin | [ ] |
| Feature flags toggle | Features enable/disable | [ ] |
| User suspend/activate | Status changes | [ ] |

---

## Data Integrity

### Cross-Reference Checks

Data displayed should match source files:

| Display Location | Data Source | Check |
|------------------|-------------|-------|
| Hero Tracker hero list | `data/heroes.json` | [ ] Count matches |
| Hero tier badges | `data/heroes.json` tier_overall | [ ] Tiers correct |
| Quick Tips critical | `data/guides/quick_tips.json` | [ ] All critical shown |
| Chief Gear slots | `data/chief_gear.json` | [ ] 6 slots, correct names |
| Event calendar | `data/events.json` | [ ] Dates correct |

### Value Verification

Cross-check these high-impact values against in-game or wiki:

- [ ] Chief Gear slot names (Coat, Pants, Belt, Weapon, Cap, Watch)
- [ ] Chief Gear set bonuses (3pc Defense, 6pc Attack)
- [ ] Tool Enhancement research bonuses (0.4%-2.5% per level)
- [ ] SvS point values (Fire Crystal 2000, Mithril 40000)
- [ ] Rally joiner skill mechanics (leftmost hero's top-right skill)
- [ ] Daybreak decoration max stats (Mythic 10%, Epic 2.5%)

### Database Integrity

- [ ] All foreign keys valid (UserHero.hero_id points to valid Hero)
- [ ] No orphaned records
- [ ] Profile settings save and load correctly
- [ ] Skill levels in valid range (1-5)
- [ ] Star ratings in valid range (0-5)

---

## Error Handling

### Graceful Degradation

| Scenario | Expected Behavior | Verified |
|----------|-------------------|----------|
| Database connection fails | Shows error message | [ ] |
| API key missing | Graceful fallback | [ ] |
| API rate limited | Shows limit message | [ ] |
| JSON file missing | Loads defaults | [ ] |
| Hero image missing | Shows placeholder | [ ] |
| Invalid user input | Shows validation error | [ ] |

### Error Messages

- [ ] Error messages are user-friendly (not stack traces)
- [ ] No Python exceptions exposed to users
- [ ] Error states allow recovery (retry, go back)

---

## Performance

### Load Times

| Page | Target Load Time | Verified |
|------|------------------|----------|
| Home | < 2 seconds | [ ] |
| Hero Tracker | < 3 seconds | [ ] |
| Quick Tips | < 2 seconds | [ ] |
| AI Advisor | < 1 second (before query) | [ ] |

### Memory/Resource Usage

- [ ] No memory leaks on page navigation
- [ ] Large lists paginated or virtualized
- [ ] Images lazy loaded where appropriate
- [ ] Database connections closed properly

---

## Security

### Input Validation

- [ ] SQL injection protected (SQLAlchemy ORM)
- [ ] XSS protected (no raw user input in HTML)
- [ ] CSRF protected (Streamlit handles)
- [ ] File uploads validated (if OCR enabled)

### Authentication

- [ ] Passwords hashed (bcrypt)
- [ ] Sessions expire appropriately
- [ ] Admin routes protected
- [ ] Sensitive data not logged

### Secrets

- [ ] API keys not in code
- [ ] Database file not exposed
- [ ] No secrets in git history

---

## Accessibility

### Basic Checks

- [ ] Text has sufficient contrast
- [ ] Images have alt text (where applicable)
- [ ] Forms have labels
- [ ] Keyboard navigation works
- [ ] Tab order is logical

### Screen Reader

- [ ] Headings properly nested (h1 > h2 > h3)
- [ ] Tables have headers
- [ ] Interactive elements labeled

---

## Browser/Device Compatibility

### Browsers to Test

| Browser | Version | Verified |
|---------|---------|----------|
| Chrome | Latest | [ ] |
| Firefox | Latest | [ ] |
| Safari | Latest | [ ] |
| Edge | Latest | [ ] |

### Devices/Screen Sizes

| Device Type | Width | Verified |
|-------------|-------|----------|
| Desktop | 1920px | [ ] |
| Laptop | 1366px | [ ] |
| Tablet | 768px | [ ] |
| Mobile | 375px | [ ] |

### Responsive Behavior

- [ ] Navigation accessible on mobile
- [ ] Tables scroll horizontally on small screens
- [ ] Cards stack vertically on mobile
- [ ] Text remains readable at all sizes

---

## Pre-Release Checklist

### Before Any Release

- [ ] All smoke tests pass
- [ ] No visible rendering errors
- [ ] No encoding issues
- [ ] Core features functional
- [ ] Data displays correctly
- [ ] Error handling works
- [ ] Performance acceptable

### Before Major Release

All of the above, plus:

- [ ] Full functional test suite passes
- [ ] Data integrity verified against sources
- [ ] Security review completed
- [ ] Browser compatibility tested
- [ ] Documentation updated
- [ ] CHANGELOG updated

---

## Issue Tracking

### Known Issues Template

When documenting issues:

```markdown
## [Page Name] - Issue Title

**Severity:** Critical / High / Medium / Low
**Status:** Open / In Progress / Fixed

**Description:**
What's happening

**Steps to Reproduce:**
1. Go to...
2. Click...
3. Observe...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Screenshots:**
(if applicable)

**Environment:**
- Browser:
- Screen size:
- User type (admin/user):
```

---

## Automated Checks

### Checks That Can Be Automated

These checks should be implemented in `/qa-review` skill:

1. **HTML validation** - Check for unclosed tags in rendered output
2. **Encoding check** - Scan for known bad character sequences
3. **JSON validation** - Verify all JSON files parse correctly
4. **Link checking** - Verify internal navigation works
5. **Data consistency** - Verify counts match across files
6. **Image availability** - Check all referenced images exist

### Manual-Only Checks

These require human verification:

1. Visual layout correctness
2. Subjective UX quality
3. Game data accuracy against in-game
4. Accessibility screen reader testing
5. Performance feel

---

## Running QA

### Quick Review (5 min)

```bash
# Run the /qa-review skill
/qa-review quick
```

### Full Review (30 min)

```bash
# Run comprehensive QA
/qa-review full
```

### Data Audit

```bash
# Run data validation
/data-audit
```

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-13 | 1.0 | Initial comprehensive checklist |
