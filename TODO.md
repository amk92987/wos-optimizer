# Bear's Den - TODO List

## Active TODO

- [ ] **Forgot Password Flow** - Add password reset via email
  - Add "Forgot Password?" link on login page
  - Create password reset request page
  - Generate secure reset tokens
  - Send password reset email
  - Create password reset confirmation page

- [ ] **Email Verification on Signup** - Enforce email verification
  - `is_verified` field exists in User model but not enforced
  - Send verification email on registration
  - Block login until verified (or grace period)

- [ ] **Create App Icons** - PWA icons for mobile
  - manifest.json references icon-192.png and icon-512.png that don't exist
  - Generate from bear logo

## Completed

### Jan 2026 - Events & Battle Tactics Update
- [x] Add Mercenary Prestige, Brother In Arms, Tundra Arms League, Frostdragon Tyrant, Tundra Album, Alliance Championship events
- [x] Fix Alliance Championship mechanics (pick 3 heroes, 50/20/30 ratio)
- [x] Fix Tundra Album as F2P event
- [x] Organize Events page with category tabs (Alliance PvE, PvP/SvS, Growth, Solo/Gacha)
- [x] Move Labyrinth section from Lineups to Battle Tactics
- [x] Combine Castle Attack and SvS Rally into single "Castle / SvS" option
- [x] Add default troop ratio note (50/20/30) at top of Lineups page
- [x] Add error logging system for debugging

### Jan 2026 - Donate, Feedback, Chat History
- [x] Ko-fi donate button in user menu (deep orange, centered)
- [x] Donate message on Homepage and AI Advisor
- [x] Feedback form in user menu with AI Advisor hint
- [x] "Report Bad Recommendation" option on AI Advisor
- [x] AI Advisor chat history persists within session
- [x] "New Chat" button to clear conversation
- [x] "Past Chats" expander with last 10 conversations
- [x] Load past conversations into current chat
- [x] Chat threading - group related conversations by thread_id
- [x] Favorites/bookmarks for AI responses (star icon, shows last 20)
- [x] Log both rules AND AI responses to database
- [x] Full user snapshot in conversation logs for training data

### Jan 2026 - Authentication & User System
- [x] User registration with email-based signup
- [x] User login with bcrypt password hashing
- [x] Session management with Streamlit session state
- [x] Password change (self-service in user menu)
- [x] Email change with 6-digit verification codes (15 min expiry, 3 attempts)
- [x] Admin role with access control
- [x] Admin impersonation ("Login as User" with Switch Back)
- [x] Test account support (is_test_account flag)
- [x] Daily login tracking for analytics
- [x] Default admin auto-creation (admin@bearsden.app)

### Jan 2026 - Notification/Announcement System
- [x] System-wide announcements with admin CRUD
- [x] Announcement types: info, warning, success, error
- [x] Active/archive status management
- [x] Time-based display (show_from, show_until)
- [x] Beautiful styled banners on all pages

### Jan 2026 - Mobile/PWA Support
- [x] PWA manifest.json with app name, display mode, theme colors
- [x] Mobile install banner on homepage ("Add to Home Screen")
- [x] Mobile detection via JavaScript
- [x] Responsive toolbar (hides text on mobile)
- [x] iOS/Android installation instructions

### Jan 2026 - Email System
- [x] Email sending utility (SMTP + debug modes)
- [x] Verification code emails (HTML + plain text)
- [x] Environment configuration for SMTP
- [x] Graceful error handling

### Jan 2026 - Admin System
- [x] Admin Dashboard with key metrics
- [x] User management (CRUD, suspend/activate, impersonation)
- [x] Announcements management
- [x] Audit log for admin actions
- [x] Feature flags (8 defaults)
- [x] Database browser
- [x] Feedback inbox with status workflow
- [x] Game data management
- [x] Data integrity validation
- [x] Usage reports and analytics
- [x] Data export (CSV/Excel/JSON)

### Jan 2026 - AI Advisor System
- [x] Admin toggle: Off / On (rate limited) / Unlimited modes
- [x] Rate limiting: daily limits, cooldown between requests
- [x] Conversation logging for training data
- [x] User feedback: thumbs up/down, star ratings
- [x] Admin curation: mark good/bad examples
- [x] Training data export (JSONL, CSV)
- [x] Jailbreak protection (only answers WoS questions)
- [x] Game-specific personality ("Chief", WoS terminology)
- [x] Source labels: (Rules) or (AI) on responses
- [x] 92%+ questions handled by rules engine

### Earlier Completed
- [x] Chief gear images with color-tinted variations (432 images)
- [x] Three cascading gear selectors (color, tier, star)
- [x] Renamed sidebar items for clarity
- [x] Renamed app from "WoS Optimizer" to "Bear's Den"
- [x] Fixed backpack images and emoji fallbacks
- [x] UI improvements (logo, cards, typography, spacing)
- [x] Chief Charms display (18 charms: 6 gear x 3 types)
- [x] Hero role badges (gatherer, joiner, garrison, etc.)
- [x] Power optimization in recommendation engine
- [x] State number tracking across profiles

## Backlog (Lower Priority)

- [ ] **CAPTCHA / Login Protection** - Security enhancement
  - Rate limiting on login attempts
  - CAPTCHA on registration
  - Brute-force protection

- [ ] **Service Worker** - Offline support
  - Cache static assets
  - Offline-first capability
  - Background sync

- [ ] **Push Notifications** - Server-to-client notifications
  - Firebase Cloud Messaging or similar
  - Notification permission handling

- [ ] **Consider moving off Streamlit to AWS** - Major architecture decision
  - FastAPI backend + React frontend
  - Better scaling and performance

## Infrastructure

### Environments
| Environment | URL | Instance |
|-------------|-----|----------|
| Local Dev | localhost:8501 | N/A |
| Sandbox/Dev | wos-dev (100.52.213.9) | Lightsail nano |
| Production | wos-live-micro (52.55.47.124) | Lightsail micro |

### Deployment
```bash
# Deploy to dev
ssh ubuntu@100.52.213.9
cd ~/wos-app && git pull origin master
sudo systemctl restart streamlit

# Deploy to production
ssh ubuntu@52.55.47.124
cd ~/wos-app && git pull origin master
sudo systemctl restart streamlit
```

## Notes

- Database: SQLite (local), PostgreSQL (AWS)
- Email: Debug mode locally, SMTP ready for production
- AI: OpenAI gpt-4o-mini with rules engine fallback
