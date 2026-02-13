# Feature Matrix: Streamlit vs Pre-Serverless React vs Serverless React

Comparison of all three versions to identify gaps in the serverless migration.

**Legend:** OK = feature present | MISSING = feature absent | PARTIAL = partially implemented | N/A = not applicable | ENHANCED = improved over source

---

## USER PAGES

### 1. Home / Dashboard

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Welcome message with username | Yes | Yes | Yes | OK |
| Quick Start guide (4 steps) | Yes | Yes | Yes | OK |
| Stats cards (heroes, profiles, etc.) | Yes (from DB) | Yes (from API) | Yes (from API) | OK |
| Donate message (Ko-fi) | Yes | Yes | Yes | OK |
| Feedback form (inline) | Yes | Yes (via AppShell) | Yes (via AppShell) | OK |
| API endpoint | N/A | `/api/dashboard/stats` (hardcoded) | `/api/dashboard` (centralized) | OK |

### 2. Hero Tracker

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| My Heroes / All Heroes tabs | Yes | Yes | Yes | OK |
| Search filter | Yes | Yes | Yes | OK |
| Sort (generation/name/level/tier) | Yes | Yes | Yes | OK |
| Class filter buttons | Yes | Yes | Yes | OK |
| Generation filter dropdown | Yes | Yes | Yes | OK |
| Tier filter dropdown | Yes | Yes | Yes | OK |
| Clear filters | Yes | Yes | Yes | OK |
| Hero portraits (80x80) | Yes | Yes | Yes | OK |
| Tier badge with tooltip | Yes | Yes | Yes | OK |
| Rarity border colors | Yes | Yes | Yes | OK |
| Generation section headers | Yes | No | Yes | ENHANCED |
| Star rating (clickable) | Yes | Yes | Yes | OK |
| Ascension pips | Yes | Yes | Yes | OK |
| Level stepper [-/+] | Yes | Yes | Yes | OK |
| Skill pips (green exploration) | Yes | Yes | Yes | OK |
| Skill pips (orange expedition) | Yes | Yes | Yes | OK |
| Gear slots (4) with quality/level/mastery | Yes | Yes | Yes | OK |
| Exclusive/Mythic gear editor | Yes | Yes | Yes | OK |
| Remove from collection | Yes | Yes | Yes | OK |
| Auto-save (debounced 300ms) | Yes (Streamlit rerun) | Yes (useAutoSave) | Yes (useAutoSave) | OK |
| Save indicator | Yes (toast) | Yes (component) | Yes (component) | OK |
| Summary metrics (Avg Level, Total Stars) | Yes | Yes | Yes | OK |
| Non-owned hero detail (skills, best use) | Yes (expanded) | Yes (modal) | Yes (modal) | OK |
| Auto-update profile gen on hero add | Yes | Yes | Yes | OK |
| Hero Database stats | No | Yes | Yes | OK |
| Role badges on hero cards | No | Yes | Yes | OK |

### 3. Chief Tracker

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 3 tabs: Gear, Charms, Upgrade Priority | Yes | Yes (2 tabs: Gear + Charms) | Yes (2 tabs: Gear + Charms) | PARTIAL |
| **Chief Gear tab** | | | | |
| 42-tier progression system | Yes | Yes | Yes | OK |
| Grouped by troop type (6 gear slots) | Yes | Yes | Yes | OK |
| Gear tier images | Yes | Yes | Yes | OK |
| 3 cascading selectors (color/subtier/stars) | Yes | Yes | Yes | OK |
| Auto-save | Yes | Yes | Yes | OK |
| **Chief Charms tab** | | | | |
| 18 charm slots (3 per gear piece) | Yes | Yes | Yes | OK |
| Triangular layout | Yes | Yes | Yes | OK |
| Level with sub-levels (4-1, 4-2, etc.) | Yes | Yes | Yes | OK |
| Summary by charm type | Yes | Yes | Yes | OK |
| **Upgrade Priority tab** | Yes (static) | No | No | **MISSING** |
| Stage-based guidance (3 stages) | Yes | No | No | **MISSING** |
| Gear upgrade order | Yes | No | No | **MISSING** |
| Key tips | Yes | No | No | **MISSING** |

### 4. Backpack / Item Guide

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Search filter | Yes | Yes | Yes | OK |
| Category tabs (8) | Yes | Yes | Yes | OK |
| Item table (image, name, desc, sources, uses) | Yes | Yes | Yes | OK |
| Static data (no API) | Yes (hardcoded) | Yes (hardcoded) | Yes (hardcoded) | OK |

### 5. Lineups

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 4 tabs | Yes (Rally Leader, Joiner, Exploration, Reference) | Yes (Optimal, Joiner, Exploration, Quick Ref) | Yes (Optimal, Joiner, Exploration, Quick Ref) | OK |
| PvE vs PvP explanation | Yes | Yes | Yes | OK |
| Default troop ratio callout | Yes | Yes | Yes | OK |
| Generation selector | Yes | Yes | Yes | OK |
| **Optimal Lineups / Rally Leader tab** | | | | |
| Personalized lineup (from engine) | Yes | Yes (6 event buttons) | Yes (6 event buttons) | OK |
| General lineup (no auth) | Yes | Yes | Yes | OK |
| Event-specific troop ratios | Yes | Yes | Yes | OK |
| Troop ratio visual bar | Yes | Yes | Yes | OK |
| "Why This Lineup" explanations | Yes | Yes | Yes | OK |
| "Recommended to Get" section | Yes | Yes | Yes | OK |
| **Rally Joiner tab** | | | | |
| Attack joiner recommendations | Yes | Yes | Yes | OK |
| Defense joiner recommendations | Yes | Yes | Yes | OK |
| Jessie/Sergey critical cards | Yes | Yes | Yes | OK |
| Joiner investment priority table | Yes | Yes | Yes | OK |
| Common mistakes | Yes | Yes | Yes | OK |
| **Exploration tab** | | | | |
| 5-hero PvE lineup | Yes | Yes | Yes | OK |
| Key PvE heroes | Yes | Yes | Yes | OK |
| Double infantry explanation | Yes | Yes | Yes | OK |
| **Quick Reference tab** | | | | |
| Troop ratio quick reference table | Yes | Yes | Yes | OK |
| Generation advice | Yes | Yes | Yes | OK |
| Spending-level investment tabs | Yes | Yes | Yes | OK |
| Joiner mechanics table | Yes | Yes | Yes | OK |
| Login prompt for non-auth users | No | Yes | Yes | OK |

### 6. AI Advisor

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Chat interface (bubbles) | Yes | Yes | Yes | OK |
| Bear paw avatar for assistant | No | Yes | Yes | OK |
| AI status banner (mode, limits) | Yes | Yes | Yes | OK |
| New Chat button | Yes | Yes | Yes | OK |
| Chat history (last 10/30) | Yes (10) | Yes (30) | Yes (30) | OK |
| Thread grouping | Yes | Yes | Yes | OK |
| Favorites section | Yes | Yes | Yes | OK |
| Favorite toggle per message | Yes | Yes | Yes | OK |
| Suggested questions (4 preset) | No | Yes | Yes | ENHANCED |
| Rate limit warning | Yes | Yes | Yes | OK |
| Thumbs up/down rating | Yes | Yes | Yes | OK |
| Feedback form on thumbs down | Yes | Yes | Yes | OK |
| Source labels (Rules/AI) | Yes | Yes | Yes | OK |
| Donate message | Yes | Yes | Yes | OK |
| Feedback form (Report Bad Rec) | Yes (in menu) | Yes (header button) | Yes (header button) | OK |
| localStorage persistence | No | Yes | Yes | ENHANCED |
| Append to current chat (+) | No | Yes | Yes | ENHANCED |

### 7. Profiles (Save/Load)

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Current Profile Summary (5 cards) | Yes | Yes | Yes | OK |
| Profile list | Yes | Yes | Yes | OK |
| Switch profile button | Yes | Yes | Yes | OK |
| Preview button/panel | Yes | Yes | Yes | OK |
| Farm toggle button | Yes | Yes | Yes | OK |
| Edit button (name + state) | Yes | Yes | Yes | OK |
| Duplicate button | Yes | Yes | Yes | OK |
| Delete button (soft delete) | Yes | Yes | Yes | OK |
| Create new profile | Yes | Yes | Yes | OK |
| Farm account linking | Yes | Yes | Yes | OK |
| Recently Deleted section | Yes | Yes | Yes | OK |
| Restore deleted profile | Yes | Yes | Yes | OK |
| Permanent delete | Yes | Yes | Yes | OK |
| 30-day retention display | Yes | Yes | Yes | OK |
| "This is a farm account" checkbox on create | No | Yes | Yes | OK |
| Farm profile disclaimer | Yes | Yes | Yes | OK |
| FARM badge | Yes | Yes | Yes | OK |

### 8. Packs (Pack Value Analyzer)

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Farmer Mode checkbox | Yes | Static page | Static page | **MISSING** |
| Price selector | Yes | Static page | Static page | **MISSING** |
| 9 item category tabs with inputs | Yes (full calculator) | Static page | Static page | **MISSING** |
| Pack analysis (value, efficiency, verdict) | Yes (full calculator) | Static page | Static page | **MISSING** |
| Category breakdown bar | Yes | Static page | Static page | **MISSING** |
| Item breakdown table | Yes | Static page | Static page | **MISSING** |
| S/A/B/C/D tier verdict | Yes | Static page | Static page | **MISSING** |

**Note:** The Packs page was a full interactive calculator in Streamlit. In both React versions it's static reference content only. This was already a gap in pre-serverless React -- not a regression from the serverless migration.

### 9. Events Guide

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Priority legend (S/A/B/C/D) | Yes | Yes | Yes | OK |
| Resource Saving Guide table | Yes | Yes | Yes | OK |
| Category tabs (5) | Yes | Yes | Yes | OK |
| F2P Only filter | No | Yes | Yes | ENHANCED |
| Priority filter | No | Yes | Yes | ENHANCED |
| Event count display | No | Yes | Yes | ENHANCED |
| Event cards with priority borders | Yes | Yes | Yes | OK |
| Event detail modal/expander | Yes | Yes | Yes | OK |
| Rewards section | Yes | Yes | Yes | OK |
| Preparation section | Yes | Yes | Yes | OK |
| Troop ratios (simple/leader+joiner) | Yes | Yes | Yes | OK |
| Wave mechanics | Yes | Yes | Yes | OK |
| SvS day-by-day phases | Yes | Yes | Yes | OK |
| Battle mechanics | Yes | Yes | Yes | OK |
| Intel strategy timeline | Yes | Yes | Yes | OK |
| Spending priority | Yes | Yes | Yes | OK |
| Phase strategy | Yes | Yes | Yes | OK |
| Scoring system | Yes | Yes | Yes | OK |
| Fuel management | Yes | Yes | Yes | OK |
| Daily stages | Yes | Yes | Yes | OK |
| Victory points | Yes | Yes | Yes | OK |
| Star system | Yes | Yes | Yes | OK |
| Tundra trade route | Yes | Yes | Yes | OK |
| Medal system | Yes | Yes | Yes | OK |
| F2P strategy | Yes | Yes | Yes | OK |
| Cost categories explained | Yes | Yes | Yes | OK |
| Recommended heroes (personalized) | Yes | Yes | Yes | OK |
| Ranking tiers | No | Yes | Yes | ENHANCED |
| Stat bonuses | No | Yes | Yes | ENHANCED |
| Stamina costs | No | Yes | Yes | ENHANCED |
| Zones | No | Yes | Yes | ENHANCED |

### 10. Combat Optimization Guide

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 4 tabs (Quick Audit, All Stats, Blind Spots, Phase Priorities) | Yes | Static page | Static page | **MISSING** |
| Milestone tracker by phase | Yes | Static page | Static page | **MISSING** |
| Stat Stacking Comparison (Player A vs B) | Yes | Static page | Static page | **MISSING** |
| Stat source cards sorted by impact | Yes | Static page | Static page | **MISSING** |
| Daybreak decoration details | Yes | Static page | Static page | **MISSING** |
| Blind spots cards with severity | Yes | Static page | Static page | **MISSING** |
| Phase priority tabs (4 phases) | Yes | Static page | Static page | **MISSING** |

**Note:** Like Packs, Combat was rich in Streamlit but is static in both React versions. Not a serverless regression.

### 11. Quick Tips & Cheat Sheet

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 5 tabs | Yes | Static page | Static page | **MISSING** |
| Critical Tips aggregation | Yes | Static page | Static page | **MISSING** |
| Hero Investment (gen-by-gen cards) | Yes | Static page | Static page | **MISSING** |
| Niche badges (~20 heroes) | Yes | Static page | Static page | **MISSING** |
| Investment level per hero | Yes | Static page | Static page | **MISSING** |
| Alliance (R4/R5) tips | Yes | Static page | Static page | **MISSING** |
| Common Mistakes aggregation | Yes | Static page | Static page | **MISSING** |
| By Category (14 expanders) | Yes | Static page | Static page | **MISSING** |

**Note:** Same pattern -- static in both React versions. Not a serverless regression.

### 12. Battle Tactics

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 6 tabs (Castle, Bear Trap, Canyon, Foundry, Frostfire, Labyrinth) | Yes | Static page | Static page | **MISSING** |
| Castle Battles (attack/defense tactics, checklists) | Yes | Static page | Static page | **MISSING** |
| Bear Trap (7-rally allocation, joiner priority) | Yes | Static page | Static page | **MISSING** |
| Canyon Clash (phases, fuel, 3-team strategy) | Yes | Static page | Static page | **MISSING** |
| Foundry (building values, double rally, Discord scripts) | Yes | Static page | Static page | **MISSING** |
| Frostfire Mine (minute-by-minute, smelter analysis) | Yes | Static page | Static page | **MISSING** |
| Labyrinth (6 zone tabs, per-zone detail) | Yes | Static page | Static page | **MISSING** |

**Note:** Same pattern -- static in both React versions.

### 13. Daybreak Island Guide

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 4 tabs | Yes | Static page | Static page | **MISSING** |
| "Don't Chase Prosperity" warning | Yes | Static page | Static page | **MISSING** |
| Battle Decorations (mythic + epic tables) | Yes | Static page | Static page | **MISSING** |
| Tree of Life progression (L1-L10) | Yes | Static page | Static page | **MISSING** |
| Spending-level strategy tabs | Yes | Static page | Static page | **MISSING** |

**Note:** Same pattern -- static in both React versions.

### 14. Settings

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Profile summary banner | Yes | Yes | Yes | OK |
| Account section (email, role) | No | Yes | Yes | OK |
| Generation selector (1-14) | Yes | Yes | Yes | OK |
| Manual day override checkbox | Yes | No | Yes | OK (serverless adds it) |
| Days-until-next-gen display | Yes | No | Yes | OK (serverless adds it) |
| State Number input | Yes | Yes | Yes | OK |
| Furnace Level selector (with FC sub-levels) | Yes | Yes | Yes | OK |
| Game Phase indicator | Yes | No | Yes | OK (serverless adds it) |
| Milestone Unlocks badges | No | No | Yes | ENHANCED |
| Spending Profile buttons | Yes | Yes | Yes | OK |
| Priority Focus buttons | Yes | Yes | Yes | OK |
| Alliance Role buttons | Yes | Yes | Yes | OK |
| Combat Priorities (5 sliders) | Yes | Yes | Yes | OK |
| Security section (change password) | No | No | Yes | ENHANCED |
| Change Email form | No | No | Yes | ENHANCED |
| Reset Priorities button | Yes | No | Yes | OK (serverless adds it) |
| Clear All Hero Data button | Yes | No | Yes | OK (serverless adds it) |
| Save indicator (bottom-right) | Yes (toast) | Yes | Yes | OK |

### 15. Inbox

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Notification tab | N/A (via announcements) | Yes | Yes | OK |
| Messages/Threads tab | N/A | Yes | Yes | OK |
| Unread count badges | N/A | Yes | Yes | OK |
| Notification detail modal | N/A | Yes | Yes | OK |
| Thread modal with message history | N/A | Yes | Yes | OK |
| Reply form | N/A | Yes | Yes | OK |

### 16. Upgrades (Recommendations)

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 3 tabs: Recommendations, Hero Investments, Analysis | Yes | Yes | Yes | OK |
| Category filter | Yes | Yes | Yes | OK |
| Priority filter | Yes | Yes | Yes | OK |
| Recommendation cards | Yes | Yes | Yes | OK |
| Hero Investment ranked list | Yes | Yes | Yes | OK |
| Priority Settings display (star ratings) | Yes | Yes | Yes | OK |
| Recommendation Logic explanation | Yes | Yes | Yes | OK |

### 17. Beginner Guide

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Full guide content | Yes | Static page | Static page | OK |
| No API needed | Correct | Correct | Correct | OK |

---

## AUTH PAGES

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Landing page | Yes | Yes | Yes | OK |
| Login (email + password) | Yes | Yes | Yes | OK |
| Register (email + password) | Yes | Yes | Yes | OK |
| Forgot Password page | No | No | Yes | ENHANCED |
| Reset Password page | No | No | Yes | ENHANCED |
| "Forgot your password?" link | No | No | Yes | ENHANCED |

---

## ADMIN PAGES

### 18. Admin Dashboard

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 8 stat cards | Yes | Yes (8 cards) | Yes (8 cards) | OK |
| SVG bar charts (User Growth, DAU) | Yes (st.bar_chart) | No | Yes | ENHANCED |
| Time range toggle (1W/1M/3M) | No | No | Yes | ENHANCED |
| New Registrations (Today/Week/Month) | Yes | No | Yes | OK |
| User Health (Active/Inactive/Retention) | Yes | No | Yes | OK |
| Quick Actions (6 links) | Yes | Yes | Yes | OK |
| Recent Users with impersonate | Yes | No | Yes | OK |
| System Status (DB/AI/Email) | Yes | No | Yes | OK |
| Error Tracking section | Yes | No | Yes | OK |
| Admin Tools (Test Accounts, Data Audit, QA) | Yes | No | Yes | OK |
| Content Statistics | Yes | No | No | **MISSING** |

**Note:** Content Statistics (profiles, heroes tracked, inventory items) from Streamlit are not in the serverless dashboard stat cards. The stat cards show "Heroes Tracked" and "Total Profiles" which partially covers this.

### 19. Admin Users

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 6 stat cards | Yes | Yes | Yes | OK |
| User Database / Create User tabs | Yes | Yes | Yes | OK |
| Search filter | Yes | Yes | Yes | OK |
| Status filter (All/Active/Suspended/Inactive) | Yes | Yes | Yes | OK |
| State filter | Yes | Yes | Yes | OK |
| Test Only checkbox | Yes | Yes | Yes | OK |
| User table with actions | Yes | Yes | Yes | OK |
| TEST badge | Yes | Yes | Yes | OK |
| 7-day usage bar chart per user | No | Yes | Yes | ENHANCED |
| AI access cycle button | Yes | Yes | Yes | OK |
| Edit user modal | Yes | Yes | Yes | OK |
| Impersonate button | Yes | Yes | Yes | OK |
| Suspend/Activate toggle | Yes | Yes | Yes | OK |
| Delete user button | Yes | Yes | Yes | OK |
| Create user form | Yes | Yes | Yes | OK |
| Test Account checkbox on create | Yes | Yes | Yes | OK |

### 20. Admin Announcements

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Current Banner Preview | Yes | Yes | Yes | OK |
| Active Announcements list | Yes | Yes | Yes | OK |
| Create announcement form | Yes | Yes (modal) | Yes (modal) | OK |
| Edit announcement | Yes | Yes | Yes | OK |
| Archive/Deactivate toggle | Yes | Yes | Yes | OK |
| Delete announcement | Yes | Yes | Yes | OK |
| Type selector (info/warning/success/error) | Yes | Yes | Yes | OK |
| Display type (banner/inbox/both) | Yes | Yes | Yes | OK |
| Expiration (days) | Yes | Yes | Yes | OK |
| Inbox content textarea | Yes | Yes | Yes | OK |
| Inactive/Archive list | Yes | Yes | Yes | OK |
| Restore from archive | Yes | Yes | Yes | OK |

### 21. Admin Feature Flags

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 4 stat cards | Yes | Yes | Yes | OK |
| 8 default flags with metadata | Yes | Yes | Yes | OK |
| Search filter | Yes | Yes | Yes | OK |
| Status filter (All/Enabled/Disabled) | Yes | Yes | Yes | OK |
| Toggle switch per flag | Yes | Yes | Yes | OK |
| Expand details (bullets) | Yes | Yes | Yes | OK |
| Edit flag (inline) | Yes | Yes | Yes | OK |
| Delete flag with confirmation | Yes | Yes | Yes | OK |
| Create new flag | Yes | Yes | Yes | OK |
| Quick Actions (Enable All/Disable All/Reset) | Yes | Yes | Yes | OK |
| Caution warning | No | Yes | Yes | OK |
| Category badges | Yes | Yes | Yes | OK |

### 22. Admin AI Settings

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| AI Mode toggle (Off/On/Unlimited) | Yes | Yes | Yes | OK |
| 8 stat metrics | Yes | Yes (5 in pre-serverless) | Yes (8) | OK |
| 4 tabs: Settings, Conversations, Training, Export | Yes | Yes | Yes | OK |
| Provider settings (primary/fallback) | Yes | Yes | Yes | OK |
| Rate limit settings | Yes | Yes | Yes | OK |
| Conversation list with filters | Yes | Yes | Yes | OK |
| Conversation detail modal | Yes | Yes | Yes | OK |
| Mark Good/Bad buttons | Yes | Yes | Yes | OK |
| Admin notes | Yes | Yes | Yes | OK |
| Training Data preview | Yes | Yes | Yes | OK |
| Export JSONL/CSV | Yes | Yes | Yes | OK |
| Fine-tuning guide | Yes | No | No | **MISSING** |

### 23. Admin Inbox (Feedback + Errors + Conversations)

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 3 top-level tabs | Yes | Yes | Yes | OK |
| **Feedback tab** | | | | |
| 5 stat cards | Yes | Yes | Yes | OK |
| 6 sub-tabs (Bugs/Features/Pending Fix/Update/Completed/Archive) | Yes | Yes | Yes | OK |
| Feedback items with category colors | Yes | Yes | Yes | OK |
| Smart routing (To Fix/To Update) | Yes | Yes | Yes | OK |
| Archive/Restore actions | Yes | Yes | Yes | OK |
| Delete with confirmation | Yes | Yes | Yes | OK |
| Bulk "Archive All Completed" | Yes | Yes | Yes | OK |
| Bulk "Empty Archive" | Yes | Yes | Yes | OK |
| Feedback Detail Modal | No | Yes | Yes | OK |
| **Errors tab** | | | | |
| 5 stat cards | Yes | Yes | Yes | OK |
| 4 sub-tabs (New/Reviewed/Fixed/Ignored) | Yes | Yes | Yes | OK |
| Error items with type/status | Yes | Yes | Yes | OK |
| Stack trace expander | Yes | Yes | Yes | OK |
| Fix notes input | Yes | Yes | Yes | OK |
| Workflow buttons (Reviewed/Fixed/Ignore/Reopen) | Yes | Yes | Yes | OK |
| Bulk "Delete All Ignored" | Yes | Yes | Yes | OK |
| Environment badge (prod/dev) | Yes | Yes | Yes | OK |
| **Conversations tab** | | | | |
| Stats cards | Yes | Yes (in Streamlit: thread count) | Yes (4 cards) | OK |
| Conversation list with routing badges | No (Streamlit has message threads) | Yes | Yes | OK |
| Curation filters (Rating/Curation/Source) | No | Yes | Yes | ENHANCED |
| Curate modal (Good/Bad/Reset/Notes) | No | Yes | Yes | ENHANCED |
| **Message Threads (Streamlit-only)** | | | | |
| New conversation form (to specific user) | Yes | No | No | **MISSING** |
| Thread list with unread badges | Yes | No | No | **MISSING** |
| Thread message history (admin/user styling) | Yes | No | No | **MISSING** |
| Reply to thread form | Yes | No | No | **MISSING** |
| Mark Read/Unread toggle | Yes | No | No | **MISSING** |
| End/Reopen thread | Yes | No | No | **MISSING** |

**Note:** Streamlit had a full admin-to-user messaging system via threads. Pre-serverless React replaced this with AI conversation curation (different purpose). The user Inbox page has a Messages tab with thread support, but the Admin side doesn't have the ability to create/send messages to users.

### 24. Admin Database Browser

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 4 tabs: Tables, Backup, Cleanup, Query | Yes | Yes | Yes | OK |
| Table list with row counts | Yes | Yes | Yes | OK |
| Table data viewer | Yes (st.dataframe) | Yes (HTML table) | Yes (HTML table) | OK |
| Pagination controls | Yes | No | Yes | OK |
| Rows per page selector | Yes | No | Yes | OK |
| Export CSV button | No | No | Yes | ENHANCED |
| Database info cards | Yes (3) | No | Yes (2) | OK |
| Create Backup / Download DB | Yes | Yes | Yes | OK |
| Table CSV export | Yes | No | No | **PARTIAL** |
| 4 Cleanup actions | Yes | Yes | Yes | OK |
| Danger Zone (Clear Feedback, Vacuum) | Yes | No | No | **MISSING** |
| SQL Query tab | Yes | Yes | Yes | OK |
| Destructive query safety check | Yes | No | No | **MISSING** |

### 25. Admin Game Data

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| 3 stat cards | Yes | Yes | Yes | OK |
| **Heroes tab (CRUD)** | Yes | No | No | **MISSING** |
| Search heroes | Yes | No | No | **MISSING** |
| Add/Edit/Delete hero | Yes | No | No | **MISSING** |
| **Items tab (CRUD)** | Yes | No | No | **MISSING** |
| Add/Edit/Delete item | Yes | No | No | **MISSING** |
| **JSON Files tab** | Yes | Yes | Yes | OK |
| File list with category filter | Yes | Yes | Yes | OK |
| Category filter dropdown | No | No | Yes | ENHANCED |
| JSON content viewer | Yes | Yes | Yes | OK |
| Edit mode toggle | Yes | No (placeholder) | Yes | OK |
| Save JSON changes with validation | Yes | No | Yes | OK |
| Data Sources links | No | Yes | Yes | OK |
| File size display | No | Yes | Yes | OK |

**Note:** Streamlit had full Hero/Item CRUD directly on the Game Data page. Pre-serverless React only had JSON file viewing. Serverless React added editing but still doesn't have Hero/Item CRUD. However, Hero/Item data in the serverless version lives in DynamoDB and JSON files, so a DB-level editor may not be needed (heroes are managed via the Hero Tracker page, items via JSON files).

### 26. Admin Data Integrity

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Run Integrity Checks button | Yes | Yes | Yes | OK |
| Summary cards (Passed/Warnings/Failed) | Yes (4) | Yes (3) | Yes (3) | OK |
| 10 integrity checks | Yes | API-dependent | API-dependent | OK |
| Per-check expandable details | Yes | Yes | Yes | OK |
| Affected record IDs display | Yes | Yes | Yes | OK |
| Fix button per check | Yes | No (placeholder) | Yes | OK |
| Fix All Safe Issues button | Yes | No | Yes | OK |
| Quick Actions (Rebuild Indexes, Clean Orphans, Generate Report) | No | Yes | Yes | OK |

### 27. Admin Usage Reports

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Time range selector | Yes | Yes | Yes | OK |
| 4 tabs: Overview, User Activity, Content Usage, Trends | Yes | Yes | Yes | OK |
| Key Metrics (4 cards) | Yes | Yes | Yes | OK |
| Activity Breakdown | Yes | Yes | Yes | OK |
| Content Created | Yes | Yes | Yes | OK |
| DAU bar chart | No | Yes | Yes | ENHANCED |
| User Activity sortable table | Yes | Yes | Yes | OK |
| Most Popular Heroes chart | Yes | Yes | Yes | OK |
| Hero Class Distribution | Yes | Yes | Yes | OK |
| Spending Profile distribution | Yes | Yes | Yes | OK |
| Alliance Role distribution | Yes | Yes | Yes | OK |
| State Distribution (top 15 + summary) | Yes | Yes | Yes | OK |
| Trends charts (Growth, Active, Registrations) | Yes (st.line_chart) | Yes (bar charts) | Yes (bar charts) | OK |
| AI Usage chart (Rules vs AI) | No | Yes | Yes | ENHANCED |

### 28. Admin Export

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| **Reports tab** (5 report types with date range) | Yes | No | No | **MISSING** |
| User Summary report | Yes | No | No | **MISSING** |
| Activity Report | Yes | No | No | **MISSING** |
| Content Statistics report | Yes | No | No | **MISSING** |
| Hero Usage report | Yes | No | No | **MISSING** |
| Growth Metrics report | Yes | No | No | **MISSING** |
| **Data Export tab** | | | | |
| 6 export options (Users, Heroes, AI, Feedback, Audit, Game Data) | Partial (9 tables) | Yes | Yes | OK |
| Format selection (CSV/Excel/JSON/JSONL/ZIP) | Yes | Yes | Yes | OK |
| Format details description | No | Yes | Yes | OK |
| Export download | Yes | Yes | Yes | OK |
| **Bulk Export section** | | | | |
| Export All User Data (ZIP) | Yes (Full DB backup) | Yes (3 buttons) | Yes (3 buttons) | OK |
| Full Database Backup | Yes | Yes | Yes | OK |
| AI Training Data (JSONL) | Yes | Yes | Yes | OK |
| Data Privacy warning | No | Yes | Yes | OK |

### 29. Admin Audit Log

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Filter by admin | Yes | No | Yes | OK |
| Filter by action | Yes | No | Yes | OK |
| Filter by time range | Yes | No | Yes | OK |
| 4 stat cards | Yes | Yes | Yes | OK |
| Log entry list with action icons | Yes | Yes | Yes | OK |
| Action type color coding | Yes | Yes | Yes | OK |
| 23+ action types | ~8 | ~8 | 23+ | ENHANCED |
| Relative time display | No | Yes | Yes | OK |
| IP address display | No | No | Yes | ENHANCED |
| Export CSV button | Yes | No | Yes | OK |
| Entry count limit (100/500) | Yes (100) | Yes (100) | Yes (500) | OK |

---

## APP SHELL / SHARED COMPONENTS

| Feature | Streamlit | Pre-Serverless React | Serverless React | Status |
|---------|-----------|---------------------|-----------------|--------|
| Desktop sidebar navigation | Yes | Yes | Yes | OK |
| Mobile bottom navigation | No | Yes | Yes | OK |
| Top header bar with UserMenu | Yes (Streamlit built-in) | Yes | Yes | OK |
| Impersonation banner | Yes | Yes | Yes | OK |
| Announcement banners | Yes | No | Yes | OK |
| Maintenance mode screen | Yes | No | Yes | OK |
| Maintenance admin banner | No | No | Yes | ENHANCED |
| Profile switcher in nav | No | No | Yes | ENHANCED |
| Inbox unread badge in nav | No | No | Yes | ENHANCED |
| Ko-fi donate button | Yes | Yes | Yes | OK |
| Send Feedback (menu) | Yes | Yes | Yes | OK |
| Change Password (menu) | Yes | Link to settings | Link to settings | OK |
| Change Email (menu) | Yes | Link to settings | Link to settings | OK |
| Sign Out button | Yes | Yes | Yes | OK |
| Admin Panel link (admin only) | Yes | Yes | Yes | OK |

---

## SUMMARY OF GAPS

### Gaps: Serverless vs Pre-Serverless React (regressions from the migration)

These are features that existed in the pre-serverless React and are missing/broken in serverless:

| # | Feature | Pre-Serverless | Serverless | Severity |
|---|---------|---------------|-----------|----------|
| 1 | Chief Tracker: Upgrade Priority tab (static guide content) | Missing in both React | Missing | Low (was already missing) |

**Result: Zero regressions from the serverless migration.** The serverless version has everything the pre-serverless React had, plus many enhancements.

### Gaps: Serverless vs Streamlit (features not yet ported)

**CORRECTION (Feb 2026):** Initial audit incorrectly labeled guide pages (Combat, Quick Tips, Battle Tactics, Daybreak, Packs) as "static placeholders." On closer inspection, these pages have **full rich content** (580-1314 lines each) with all the Streamlit features already ported. The Chief Gear page also has its Upgrade Priority tab (line 752). The Admin AI page already has fine-tuning tips (line 997).

Actual remaining gaps (admin features only):

| # | Feature | Page | Severity | Notes |
|---|---------|------|----------|-------|
| 1 | Admin message threads (send messages to users) | Admin Inbox | Medium | Full admin-to-user messaging system |
| 2 | Admin Export: 5 custom report types | Admin Export | Medium | User Summary, Activity, Content, Hero Usage, Growth reports |
| 3 | Admin Game Data: Hero/Item CRUD | Admin Game Data | Medium | Hero and Item management tabs |
| 4 | Admin Database: Destructive query safety | Admin Database | Low | Confirmation for DELETE/UPDATE SQL queries |

### Features ENHANCED in Serverless (not in Streamlit or pre-serverless)

| # | Feature | Page |
|---|---------|------|
| 1 | Forgot Password / Reset Password pages | Auth |
| 2 | Security section (change password/email) | Settings |
| 3 | Milestone Unlocks badges | Settings |
| 4 | Manual day override + days-until-next-gen | Settings |
| 5 | SVG bar charts on dashboard | Admin Dashboard |
| 6 | Recent Users with impersonation on dashboard | Admin Dashboard |
| 7 | Error Tracking on dashboard | Admin Dashboard |
| 8 | 23+ action types in audit log | Admin Audit Log |
| 9 | IP address display in audit log | Admin Audit Log |
| 10 | Announcement banners in app shell | AppShell |
| 11 | Maintenance mode screen | AppShell |
| 12 | Profile switcher in nav | AppShell |
| 13 | Inbox unread badge in nav | AppShell |
| 14 | Data integrity fix buttons | Admin Data Integrity |
| 15 | AI Usage trends chart | Admin Usage Reports |
| 16 | Bear paw avatar for AI | AI Advisor |
| 17 | Suggested questions in AI | AI Advisor |
| 18 | localStorage chat persistence | AI Advisor |
| 19 | Append to current chat (+) | AI Advisor |
| 20 | F2P Only / Priority filters on events | Events Guide |
| 21 | Database pagination controls + CSV export | Admin Database |
| 22 | Game data category filter + inline editing | Admin Game Data |
| 23 | Generation section headers in hero tracker | Hero Tracker |
| 24 | Role badges on hero cards | Hero Tracker |

---

## HARDCODED URL STATUS

The plan file identified ~60 hardcoded `http://localhost:8000` URLs across 16+ pages. The current serverless version has converted most of these to use the centralized `api()` client. However, some pages still need verification that all endpoints are wired up correctly on the backend.

See `/home/adam/.claude/plans/soft-hatching-blanket.md` for the full endpoint mapping plan.
