# React Migration Audit: Missing Features

Comprehensive comparison of Streamlit (live) vs React (local) migration.

**Audit Date:** January 26, 2026
**Method:** 12 parallel audit agents analyzing each page
**Status:** UI enhancements in React are OK. Focus is on MISSING FUNCTIONALITY.

---

## Executive Summary

| Section | Critical Missing | High Priority | Medium | Total Issues |
|---------|------------------|---------------|--------|--------------|
| Admin Pages | 28 | 15 | 12 | 55 |
| User Pages | 35 | 20 | 18 | 73 |
| **Total** | **63** | **35** | **30** | **128** |

**Most Critical Gaps:**
1. Hero Tracker - Missing gear system, skill editing, filters
2. Admin Database - 6 API endpoints not implemented (page non-functional)
3. AI Advisor - Missing favorites, threading, feedback form, rate limits
4. Lineups - No personalization, no database integration
5. Guide Pages - 68% content reduction, missing interactive features

---

# PART 1: ADMIN PAGES

## 1.1 Admin Users Page

### Status: NEARLY COMPLETE (1 critical issue)

**Missing:**
- Impersonation - "Login" button shows alert instead of working

**React Enhancements (keep these):**
- AI Access Level toggle in edit modal
- Custom daily limit field
- Visual usage bars instead of X/7 text

---

## 1.2 Admin Announcements Page

### Status: PARTIAL - 6 critical features missing

| Feature | Streamlit | React | Status |
|---------|-----------|-------|--------|
| Current Banner status section | Yes | No | MISSING |
| Announcement Type (info/warning/success/error) | Yes | No | MISSING |
| Type colors and icons | Yes | No | MISSING |
| Expiration settings (days) | Yes | No | MISSING |
| Inbox Content field | Yes | No | MISSING |
| Create user notifications | Yes | No | MISSING |
| Days remaining display | Yes | No | MISSING |
| Priority field | No | Yes | React enhancement |

---

## 1.3 Admin Database Page

### Status: NON-FUNCTIONAL - 6 API endpoints missing

**Critical:** React calls 6 endpoints that DO NOT EXIST in the backend.

| Endpoint | Purpose | Status |
|----------|---------|--------|
| `GET /api/admin/database/tables` | List tables | MISSING |
| `GET /api/admin/database/tables/{name}` | Get table data | MISSING |
| `GET /api/admin/database/backups` | List backups | MISSING |
| `POST /api/admin/database/backup` | Create backup | MISSING |
| `POST /api/admin/database/cleanup/{id}` | Run cleanup | MISSING |
| `POST /api/admin/database/query` | Execute SQL | MISSING |

**Missing Functionality:**
- Cannot view any table data
- No pagination (limited to 50 rows, no controls)
- No backup/download functionality
- No CSV export
- No cleanup operations work
- No SQL query execution
- No database metrics (size, last modified)

---

## 1.4 Admin Inbox/Feedback Page

### Status: PARTIAL - Conversations completely missing

**Feedback Tab Missing:**
- 5-status system (only has 3 statuses)
- 6 organized tabs with live counts
- Statistics dashboard
- Archive All Completed bulk action
- Empty Archive bulk delete
- Delete individual items
- Restore from archive

**Errors Tab Missing:**
- 4-status system (only has resolved boolean)
- Admin review tracking (who/when reviewed)
- Fix notes field
- Environment badge (production/staging)
- Extra context JSON display
- Reopen functionality
- Delete operations

**Conversations Tab:**
- COMPLETELY UNIMPLEMENTED (just a placeholder)
- No new message creation
- No conversation list
- No reply functionality
- No read/unread tracking

---

## 1.5 Admin Feature Flags Page

### Status: MINIMAL - 19 features missing

**React Only Has:**
- List flags
- Toggle on/off

**Missing:**
- Search flags by name
- Filter by status (Enabled/Disabled)
- Statistics dashboard (Total/Enabled/Disabled counts)
- Create new flags
- Edit flag name/description
- Delete flags
- Expandable "What's included" details
- Flag metadata (icons, categories)
- Enable All bulk action
- Disable All bulk action
- Reset to Defaults
- Name validation
- Duplicate detection
- Auto-seed defaults on empty table
- Delete confirmation dialogs
- Success/error messages

---

## 1.6 Admin Usage Reports Page

### Status: PARTIAL - 11 features missing

**Missing:**
- "All Time" date range option
- Activity Rate % metric
- Total Users metric
- New Users metric
- Activity Breakdown (Very Active/Weekly/Monthly/Inactive)
- Content Created (Profiles/Heroes/Items counts)
- User Activity Table (Top 50 users with sorting)
- Hero Class Distribution
- Spending Profile Distribution
- State Distribution Analytics
- Historical Trends (90-day growth charts)

**React Has That Streamlit Doesn't:**
- Page Views tracking
- User Retention circular charts
- AI Usage (Rules vs API) breakdown

---

## 1.7 Admin AI Page

### Status: NEEDS VERIFICATION

---

# PART 2: USER PAGES

## 2.1 Hero Tracker Page

### Status: CRITICAL - Missing core gameplay systems

**Missing Filters:**
- Generation filter (1-14)
- Tier filter (S+ through D)
- Status filter (Owned/Not Owned)

**Missing Hero Editor Features:**
- Skill level editing (1-5 for all 6 skills) - CANNOT CHANGE SKILLS
- Skill names (shows generic "Skill 1/2/3" instead)
- Skill descriptions/tooltips
- Ascension tier editing

**Missing Gear System (CRITICAL):**
- Entire 4-slot gear system missing
- No quality tracking (None/Gray/Green/Blue/Purple/Gold/Legendary)
- No gear level tracking (0-100)
- No gear mastery tracking (0-20)
- No mythic/exclusive gear

**Missing Display Features:**
- Hero role badges (Rally Leader, Garrison Joiner, etc.)
- Level display on list view
- Star display on list view
- Tier tooltip descriptions
- Multi-level sorting (rarity → tier → name)
- Generation-based grouping

**Missing UX:**
- Auto-save (requires manual save button)
- Toast notifications

---

## 2.2 Chief Tracker Page

### Status: PARTIAL - 12+ features missing

**Gear System Missing:**
- 42-tier progression (React only has 8 quality levels)
- Star progression (0-3★)
- Sub-tiers (T1, T2, T3)
- Cascading selector UI
- Tiered gear images
- Set bonus information

**Charms Missing:**
- Charm bonus display (percentage)
- Shape symbols (△◇□⬠⬡●)
- Charm statistics summary tab
- Charm level statistics with bonus %
- Auto-save on change

**Other Missing:**
- Game-specific gear names
- Error handling/recovery
- Furnace 22 unlock info

---

## 2.3 AI Advisor Page

### Status: PARTIAL - 12 major features missing

| Feature | Streamlit | React | Status |
|---------|-----------|-------|--------|
| Report Bad Recommendation form | Yes | No | MISSING |
| Chat history load functionality | Yes | Buttons don't work | BROKEN |
| Favorites system (star/unstar) | Yes | No | MISSING |
| Threaded conversations | Yes | No | MISSING |
| AI access status display | Yes | No | MISSING |
| Rate limit display | Yes | No | MISSING |
| Donate message | Yes | Yes | OK |
| Conversation logging to database | Yes | No | MISSING |
| User context logging | Yes | No | MISSING |
| Error logging with IDs | Yes | No | MISSING |
| Prevent duplicate ratings | Yes | No | MISSING |
| Toast confirmations | Yes | No | MISSING |
| Suggested questions | No | Yes | React enhancement |

**Critical Bug:** Chat history buttons have no onClick handler - users cannot load past conversations.

---

## 2.4 Profiles/Save-Load Page

### Status: PARTIAL - 8 features missing

**Missing:**
- Current Profile Summary section (metrics at top)
- Preview Profile details (expandable view with hero list)
- Edit Profile (name + state after creation)
- Duplicate Profile
- Soft Delete / 30-Day Recovery
- Link Farm to Main Account (via linked_main_profile_id)
- Alliance Role display
- State Number editing (only at creation)

**React Has:**
- Updated timestamp on cards (Streamlit doesn't show this)
- Spending profile always visible

---

## 2.5 Lineups Page

### Status: PARTIAL - 10+ features missing

**Critical Missing:**
- User hero database integration (shows generic templates, not user's heroes)
- Personalized recommendations based on owned heroes
- Power score calculation

**Missing Features:**
- "Why This Lineup" explanations with tier system
- Generation selector & advice
- Exploration (5-hero) lineups section
- Attack vs Defense sub-tabs
- Spending profile recommendations
- Hero stats display (level, stars, tier, generation)
- "Coming Soon" hero recommendations
- "My Lineups" creation (says "Coming Soon")

**Data Issue:**
- Natalia vs Jeronimo tab has INCORRECT hero class for Natalia

---

## 2.6 Guide Pages (5 pages)

### Status: SIGNIFICANTLY REDUCED - 68% content cut

**Streamlit:** 3,241 lines across 5 files
**React:** 1,021 lines across 5 files

### Beginner Guide Missing:
- 6 navigation tabs (React has 2 sections)
- Farm account system documentation
- Furnace milestones (30+ levels detailed)
- FC building upgrade explanation
- Dynamic generation detection
- Hero investment by generation
- Daily checklist functionality

### Quick Tips Missing:
- Hero Investment by Generation (Gen 1-14 with detailed cards)
- 5 main tabs (Critical/Hero Investment/Alliance/Mistakes/Category)
- Priority-based filtering
- Skill descriptions and tooltips
- Investment level badges (MAX/HIGH/MEDIUM/LOW/SKIP)
- Niche use badges
- Spending profile advice
- Alliance management (R4/R5) tips

### Combat Missing:
- 4 main tabs
- Quick audit checklist by game phase
- Expandable stat source cards
- Impact severity badges
- Common blind spots section
- Stat stacking example comparison
- Phase-based priority organization

### Battle Tactics Missing:
- 6 event tabs (Castle Battles, Bear Trap, Canyon Clash, Foundry, Frostfire Mine, Labyrinth)
- Team coordination content
- Discord scripts
- Map images
- Minute-by-minute breakdowns
- Skill builds (Frostfire)
- Zone strategies (Labyrinth)

### Daybreak Island Missing:
- 4 navigation tabs
- New Player Tips section
- Spending profile variants (F2P/Low/Medium+)
- Common mistakes section
- Detailed level progression
- Treasure chests section

---

# PART 3: PRIORITY IMPLEMENTATION LIST

## Critical (Blocking Core Functionality)

1. **Admin Database** - Implement 6 missing API endpoints
2. **Hero Tracker Gear System** - Add 4-slot gear with quality/level/mastery
3. **Hero Tracker Skills** - Add skill level editing (1-5)
4. **AI Advisor** - Fix chat history load, add feedback form
5. **Admin Users** - Implement impersonation

## High Priority (Feature Parity)

6. **Hero Tracker Filters** - Add generation, tier, status filters
7. **Admin Announcements** - Add type field, expiration, inbox content
8. **Admin Inbox** - Implement Conversations tab
9. **Lineups** - Add database integration for personalized recommendations
10. **AI Advisor** - Add favorites, threading, rate limit display
11. **Chief Tracker** - Add full 42-tier gear progression
12. **Admin Feature Flags** - Add CRUD operations

## Medium Priority (Enhanced UX)

13. **Profiles** - Add edit, duplicate, soft delete
14. **Quick Tips** - Add hero investment by generation
15. **Battle Tactics** - Add event-specific guides
16. **Admin Usage Reports** - Add historical trends
17. **Hero Tracker** - Add hero role badges

## Low Priority (Polish)

18. Guide pages - Add tab navigation
19. Guide pages - Add expandable sections
20. Toast notifications throughout
21. Auto-save functionality

---

# NEXT STEPS

1. Start with Admin Database API endpoints (page is completely broken)
2. Implement Hero Tracker gear system (core gameplay)
3. Add skill editing to Hero Tracker
4. Fix AI Advisor chat history bug
5. Review this document and prioritize remaining items
