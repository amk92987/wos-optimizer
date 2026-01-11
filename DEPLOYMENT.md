# Deployment Planning

This document tracks architectural decisions and requirements for deploying the WoS Optimizer to AWS for public use.

## Current State (Local Development)

- **Database**: SQLite (single file, local storage)
- **Auth**: None (single user assumed)
- **Profiles**: Stored locally, no user isolation
- **Sessions**: Streamlit's built-in session state

---

## Landing Page / Login Experience

**First-time visitor flow:**
```
1. User visits site → Landing page (not logged in)
2. See app description, features preview
3. "Login with Discord" button prominently displayed
4. Donation callout visible
5. After login → redirect to main app
```

**Donation Section** (visible on landing/login page):
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Random Chaos Labs relies on donations to continue         │
│   creating content. Please consider donating to the cause.  │
│                                                             │
│   [ Ko-fi ]  [ PayPal ]  [ Patreon ]                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Tasks**:
- [ ] Create landing page component (shown when not logged in)
- [ ] Add donation button/links (Ko-fi, PayPal, Patreon - pick one or more)
- [ ] Add brief feature overview / screenshots
- [ ] Add "Login with Discord" button
- [ ] Optional: Show limited features without login, full features require login

**Donation Platform Options**:
| Platform | Pros | Cons |
|----------|------|------|
| Ko-fi | Simple, no fees on donations | Less features |
| Patreon | Recurring support, tiers | Takes percentage |
| PayPal | Universal, trusted | Fees on transactions |
| Buy Me a Coffee | Gaming-friendly | Takes percentage |
| GitHub Sponsors | Developer-focused | Requires approval |

---

## Pre-Deployment Requirements

### 1. Database Migration (SQLite → PostgreSQL)

**Why**: SQLite doesn't handle concurrent writes well. Multiple users hitting the app simultaneously will cause issues.

**Tasks**:
- [ ] Set up PostgreSQL on AWS RDS (or same EC2 instance to start)
- [ ] Update SQLAlchemy connection string to support both SQLite (dev) and PostgreSQL (prod)
- [ ] Add environment variable for database URL (`DATABASE_URL`)
- [ ] Test migration scripts
- [ ] Add connection pooling for production

**Schema changes needed**:
- [ ] Add `User` table (id, email, discord_id, created_at, last_login, is_admin)
- [ ] Add `user_id` foreign key to `UserProfile` table
- [ ] Add index on `user_id` for profile queries

---

### 2. Authentication System

**Recommended**: Discord OAuth (WoS community lives on Discord)

**Alternative**: Google OAuth or email/password

**User Flow**:
```
1. User visits site → sees landing page with "Login with Discord" button
2. User clicks → redirected to Discord OAuth
3. User authorizes → redirected back with auth token
4. App creates/updates User record → creates session
5. User can now create/manage their profiles
```

**Tasks**:
- [ ] Register Discord application at https://discord.com/developers/applications
- [ ] Add OAuth callback URL configuration
- [ ] Implement login/logout endpoints
- [ ] Add session management (database-backed sessions)
- [ ] Add "Login with Discord" button to UI
- [ ] Protect profile routes - require login
- [ ] Store Discord user ID, username, avatar

**Libraries to consider**:
- `Authlib` for OAuth
- `streamlit-authenticator` (simpler but less flexible)
- Custom implementation with Discord API

---

### 3. User & Admin System

**User Hierarchy**:
```
Admin (role: admin)
├── Can view all profiles (read-only by default)
├── Can impersonate users for debugging
├── Access to admin dashboard
├── Audit log of admin actions
└── Can promote/demote users

Regular Users (role: user)
├── Own their profiles (1 or more cities)
├── Can only see their own data
├── Self-service account management
└── Can delete their own account
```

**Database Schema**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) UNIQUE,
    discord_username VARCHAR(100),
    discord_avatar VARCHAR(255),
    email VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',  -- 'user', 'admin', 'moderator'
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100),
    server_age_days INTEGER,
    furnace_level INTEGER,
    -- ... existing profile fields ...
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER REFERENCES users(id),
    action VARCHAR(50),  -- 'view_profile', 'impersonate', 'edit_user', etc.
    target_user_id INTEGER REFERENCES users(id),
    target_profile_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Admin Features**:
- [ ] Admin dashboard page (protected)
- [ ] User list with search/filter
- [ ] View user profiles (read-only, logged)
- [ ] Impersonate user (for debugging, logged)
- [ ] User statistics and analytics
- [ ] Ability to disable problematic accounts

**Tasks**:
- [ ] Add `role` field to User model
- [ ] Create admin check decorator/function
- [ ] Build admin dashboard page
- [ ] Implement audit logging
- [ ] Add your Discord ID as initial admin (hardcoded or env var)

---

### 4. Security Considerations

**Must Have**:
- [ ] HTTPS only (AWS Certificate Manager + Load Balancer or Let's Encrypt)
- [ ] Environment variables for secrets (never commit to git)
- [ ] SQL injection protection (SQLAlchemy handles this)
- [ ] Session security (secure cookies, expiration)
- [ ] Rate limiting on auth endpoints
- [ ] CORS configuration if API endpoints added later

**Secrets to manage**:
```
DATABASE_URL=postgresql://user:pass@host:5432/wos_optimizer
DISCORD_CLIENT_ID=xxx
DISCORD_CLIENT_SECRET=xxx
SECRET_KEY=xxx  # For session signing
ADMIN_DISCORD_IDS=your_discord_id,other_admin_id
```

**Nice to Have**:
- [ ] Content Security Policy headers
- [ ] Request logging for debugging
- [ ] Automated security updates

---

### 5. Hosting Architecture

**Simple Start (Recommended)**:
```
┌─────────────────────────────────────────────────────────┐
│                        AWS                               │
│  ┌─────────────────┐      ┌─────────────────────────┐   │
│  │   EC2 Instance  │      │     RDS PostgreSQL      │   │
│  │                 │      │                         │   │
│  │  - Streamlit    │ ───► │  - User data            │   │
│  │  - Nginx        │      │  - Profiles             │   │
│  │  - SSL/HTTPS    │      │  - Audit logs           │   │
│  └─────────────────┘      └─────────────────────────┘   │
│           │                                              │
│           ▼                                              │
│  ┌─────────────────┐                                    │
│  │  Route 53 DNS   │  ← wos-optimizer.yourdomain.com    │
│  └─────────────────┘                                    │
└─────────────────────────────────────────────────────────┘
```

**EC2 Instance**:
- t3.small or t3.medium to start ($15-30/month)
- Ubuntu 22.04 LTS
- Nginx as reverse proxy
- Let's Encrypt for SSL
- systemd service for Streamlit

**RDS PostgreSQL**:
- db.t3.micro for free tier (first year)
- db.t3.small after (~$15/month)
- Enable automated backups

**Alternative (Serverless)**:
- AWS App Runner or ECS Fargate
- More complex but auto-scales
- Consider later if traffic grows

---

### 6. Environment Configuration

**Development** (current):
```python
# .env.development
DATABASE_URL=sqlite:///./wos_optimizer.db
DEBUG=True
```

**Production**:
```python
# .env.production (NEVER COMMIT)
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/wos_optimizer
DISCORD_CLIENT_ID=xxx
DISCORD_CLIENT_SECRET=xxx
SECRET_KEY=generate-a-long-random-string
ADMIN_DISCORD_IDS=your_discord_id
DEBUG=False
```

**Config loader** (to implement):
```python
import os
from dotenv import load_dotenv

ENV = os.getenv("ENVIRONMENT", "development")
load_dotenv(f".env.{ENV}")

DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
# etc.
```

---

### 7. Deployment Checklist

**Before First Deploy**:
- [ ] PostgreSQL migration complete and tested
- [ ] Discord OAuth working locally
- [ ] Admin account system implemented
- [ ] Environment variable configuration
- [ ] All secrets out of codebase
- [ ] Basic error handling/logging

**Deploy Steps**:
- [ ] Set up EC2 instance
- [ ] Set up RDS PostgreSQL
- [ ] Configure security groups
- [ ] Install dependencies on EC2
- [ ] Set up Nginx reverse proxy
- [ ] Configure SSL with Let's Encrypt
- [ ] Set up systemd service for Streamlit
- [ ] Configure Route 53 DNS
- [ ] Run database migrations
- [ ] Deploy application code
- [ ] Verify admin account works
- [ ] Test user registration flow

**Post-Deploy**:
- [ ] Set up monitoring (CloudWatch)
- [ ] Configure automated backups
- [ ] Set up error alerting
- [ ] Document recovery procedures

---

## Feature Flags for Gradual Rollout

Consider implementing feature flags to enable features gradually:

```python
FEATURES = {
    "profiles": True,           # Multi-profile support
    "ai_advisor": False,        # AI features (cost $)
    "social_sharing": False,    # Share lineups publicly
    "alliance_features": False, # Alliance-wide tracking
}
```

---

## Cost Estimates

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| EC2 | t3.small | ~$15 |
| RDS PostgreSQL | db.t3.micro | Free (year 1), then ~$15 |
| Route 53 | Hosted zone | ~$0.50 |
| Data Transfer | Light usage | ~$5 |
| **Total** | | **~$20-35/month** |

---

## Timeline Suggestion

1. **Phase 1 - Core Features** (current): Build all features locally
2. **Phase 2 - Auth & Database**: Implement PostgreSQL + Discord OAuth
3. **Phase 3 - Admin System**: Build admin dashboard and audit logging
4. **Phase 4 - Deploy**: Set up AWS infrastructure and deploy
5. **Phase 5 - Monitor**: Watch for issues, gather feedback, iterate

---

## Notes & Decisions

*Add notes here as decisions are made:*

- **2026-01-10**: Created deployment planning document
- **Decision**: Use Discord OAuth (community is on Discord)
- **Decision**: Start with single EC2 + RDS, scale later if needed
- **Decision**: Admin account will have read access to all profiles with audit logging
- **Branding**: "Random Chaos Labs" - use this name on landing page and donation callouts
- **Decision**: Landing page will include donation message: "Random Chaos Labs relies on donations to continue creating content. Please consider donating to the cause."

---

## Planned Features (Pre-Deployment)

### Rule-Based Recommendation Engine
See `RECOMMENDATION_ENGINE.md` for full design.

**Summary:** Replace AI-first recommendations with a rule-based engine that uses our curated game data. AI becomes a fallback for complex questions only.

**Benefits:**
- Instant responses (no API latency)
- Zero cost for 80%+ of queries
- Uses accurate, curated data
- AI available for edge cases

**Status:** Design complete, implementation pending

---

## Questions to Resolve

- [ ] Domain name for the app?
- [ ] Will you need email notifications? (password reset, etc.)
- [ ] Any plans for mobile app later? (would need API endpoints)
- [ ] Budget constraints for hosting?
- [ ] Expected user count at launch?
