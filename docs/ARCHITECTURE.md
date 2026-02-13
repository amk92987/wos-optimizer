# Bear's Den - Architecture

## System Overview

```
                         ┌──────────────────┐
                         │   Route 53 DNS   │
                         │ *.randomchaoslabs │
                         └────────┬─────────┘
                                  │
                         ┌────────v─────────┐
                         │   CloudFront     │
                         │   Distribution   │
                         │ (URL rewrite fn) │
                         └───┬──────────┬───┘
                             │          │
                    /app/*   │          │  /api/*
                             │          │
                   ┌─────────v──┐  ┌────v──────────┐
                   │  S3 Bucket │  │  API Gateway   │
                   │  (Next.js  │  │  (HTTP API)    │
                   │  static)   │  │                │
                   └────────────┘  └───────┬────────┘
                                           │
                              ┌─────────────┼──────────────┐
                              │             │              │
                    ┌─────────v──┐ ┌────────v──┐ ┌────────v──┐
                    │  Auth Fn   │ │ Heroes Fn │ │ Admin Fn  │
                    │  Profiles  │ │ Chief Fn  │ │ General   │
                    │            │ │ Recommend │ │ Cleanup   │
                    └─────┬──────┘ │ Advisor   │ └─────┬─────┘
                          │        └─────┬──────┘      │
                          │              │             │
                    ┌─────v──────────────v─────────────v─────┐
                    │              DynamoDB                   │
                    │  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
                    │  │ MainTable│ │AdminTable│ │ RefTable│ │
                    │  └──────────┘ └──────────┘ └─────────┘ │
                    └────────────────────────────────────────┘
```

## Lambda Functions (10)

| Function | Routes | Purpose |
|----------|--------|---------|
| **AuthFunction** | `/api/auth/*` | Login, register, password change, Cognito integration |
| **HeroesFunction** | `/api/heroes/*` | Hero CRUD, roster management, bulk updates |
| **ProfilesFunction** | `/api/profiles/*` | Profile CRUD, settings, active profile |
| **ChiefFunction** | `/api/chief/*` | Chief gear slots, charms, gear progression |
| **RecommendFunction** | `/api/recommendations/*` | Upgrade recommendations, investments, phase detection |
| **AdvisorFunction** | `/api/advisor/*` | AI Advisor chat, rules engine, AI fallback |
| **AdminFunction** | `/api/admin/*` | Users, feature flags, audit log, database, integrity, errors, AI settings |
| **GeneralFunction** | `/api/general/*` | Announcements, inbox, notifications, search, unread count, game data |
| **CleanupFunction** | (Scheduled) | Periodic cleanup of expired data |
| **UserMigrationFunction** | (Cognito trigger) | Post-confirmation user setup |

## DynamoDB Schema

### MainTable (`wos-main-{env}`)

Stores user data, profiles, heroes, and AI conversations.

| Entity | PK | SK | Key Attributes |
|--------|----|----|----------------|
| User metadata | `USER#{userId}` | `METADATA` | email, role, is_active, created_at |
| User profile | `USER#{userId}` | `PROFILE#{profileId}` | name, furnace_level, spending_profile, priorities |
| User hero | `PROFILE#{profileId}` | `HERO#{heroName}` | level, stars, skills, gear slots |
| AI conversation | `USER#{userId}` | `AICONV#{timestamp}` | question, answer, provider, rating |

**GSI: GSI1** (email lookup)
- GSI1PK: `EMAIL#{email}` / GSI1SK: `USER`

**GSI: GSI2** (Cognito sub lookup)
- GSI2PK: `COGNITO#{sub}` / GSI2SK: `USER`

### AdminTable (`wos-admin-{env}`)

Stores admin-specific data: feature flags, feedback, errors, audit log.

| Entity | PK | SK | Key Attributes |
|--------|----|----|----------------|
| Feature flag | `FLAG` | `{flagName}` | is_enabled, description |
| Feedback | `FEEDBACK` | `{timestamp}#{id}` | category, description, status |
| Error log | `ERRORS` | `{timestamp}#{id}` | error_type, message, stack_trace, handler |
| Audit entry | `AUDIT#{month}` | `{timestamp}#{id}` | action, admin_username, target |
| Announcement | `ANNOUNCEMENT` | `{id}` | title, message, type, is_active |
| AI settings | `SETTINGS` | `AI` | mode, provider, daily_limit |
| Notification | `NOTIFICATION#{userId}` | `{id}` | type, title, message, is_read |

### ReferenceTable (`wos-reference-{env}`)

Caches game reference data loaded from JSON files.

| Entity | PK | SK |
|--------|----|----|
| Game data | `GAMEDATA` | `{dataType}` |

## Frontend Architecture

### Next.js App Router

The frontend is a statically exported Next.js app (`output: 'export'` in next.config.js). All pages are client-side rendered with data fetched from the API.

```
frontend/app/
├── layout.tsx          # Root layout (AppShell wrapper)
├── page.tsx            # Home page
├── heroes/page.tsx     # Hero Tracker
├── chief/page.tsx      # Chief Tracker
├── upgrades/page.tsx   # Recommendations + Gear Calculator
├── advisor/page.tsx    # AI Advisor chat
├── lineups/page.tsx    # Lineup Builder
├── profiles/page.tsx   # Profile management
├── admin/              # Admin panel
│   ├── page.tsx        # Dashboard
│   ├── users/          # User management
│   ├── inbox/          # Notifications + errors
│   ├── announcements/  # System announcements
│   ├── feature-flags/  # Feature toggles
│   ├── database/       # Data browser
│   ├── data-integrity/ # Validation checks
│   ├── usage-reports/  # Analytics
│   └── ...
└── ...
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `AppShell.tsx` | Layout with header, sidebar, mobile nav, impersonation banner |
| `Sidebar.tsx` | Navigation with section groups, notification badges |
| `HeroCard.tsx` | Expandable hero card with inline editing |
| `HeroDetailModal.tsx` | Full hero detail view |
| `UserMenu.tsx` | Top-right user dropdown |

### State Management

- **Auth**: React Context (`lib/auth.tsx`) - user, token, impersonation state
- **API calls**: Direct fetch via `lib/api.ts` (no state library)
- **Auto-save**: `hooks/useAutoSave.ts` - 300ms debounce, optimistic updates
- **Local storage**: Sidebar collapse, dismissed announcements, impersonation state

### API Client (`lib/api.ts`)

All backend communication goes through typed API functions organized by domain:

```typescript
authApi.login(email, password)
heroesApi.getUserHeroes(token)
profilesApi.getProfiles(token)
chiefApi.getGear(token)
recommendApi.getRecommendations(token)
advisorApi.ask(token, question, context)
adminApi.getUsers(token)
generalApi.getAnnouncements(token)
inboxApi.getUnreadCount(token)
```

## Backend Architecture

### Handler Pattern

Each Lambda handler follows the same pattern:

```python
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

app = APIGatewayHttpResolver()
logger = Logger()

@app.get("/api/heroes")
def list_heroes():
    user_id = get_authenticated_user(app)  # JWT validation
    # ... business logic ...
    return {"heroes": [...]}

def handler(event, context):
    return app.resolve(event, context)
```

### Authentication Flow

1. Frontend calls Cognito for login/register (JWT tokens)
2. API Gateway passes JWT in Authorization header
3. Each handler validates JWT via `common/auth.py`
4. Admin routes additionally check `role == 'admin'`
5. Impersonation: admin sends `X-Impersonate-User` header to act as another user

### Recommendation Engine

```
User Request
     │
     ▼
┌─────────────────┐
│ Request          │──→ Pattern match? ──→ Rules Engine ──→ Response
│ Classifier       │                        (hero_analyzer,
└─────────────────┘                         gear_advisor,
     │                                      lineup_builder)
     │ Complex question
     ▼
┌─────────────────┐
│ AI Recommender  │──→ Build context (profile + heroes + mechanics)
└─────────────────┘──→ Call OpenAI/Claude API
                   ──→ Log conversation
                   ──→ Return response
```

The rules engine handles ~92% of questions. AI is the fallback for complex/novel questions.

## Infrastructure

### SAM Template (`infra/template.yaml`)

Defines all AWS resources:
- 10 Lambda functions with API Gateway routes
- 3 DynamoDB tables (PAY_PER_REQUEST)
- Cognito User Pool
- S3 bucket for frontend
- CloudFront distribution with URL rewrite function
- IAM roles with least-privilege permissions

### Deployment

```powershell
# Dev deployment
.\scripts\deploy_dev.ps1

# Runs:
# 1. sam build (Python Lambda packages)
# 2. sam deploy --config-env default (CloudFormation stack)
# 3. npm run build (Next.js static export)
# 4. aws s3 sync (upload to S3)
# 5. aws cloudfront create-invalidation (cache clear)
```

### Environments

| Env | Stack | Domain | API |
|-----|-------|--------|-----|
| Dev | `wos-dev` | wosdev.randomchaoslabs.com | qro6iih6oe.execute-api.us-east-1.amazonaws.com/dev |
| Live | `wos-live` | wos.randomchaoslabs.com | (TBD) |

## Data Flow

### Hero Tracker Save Flow

```
User edits hero level in HeroCard
     │
     ▼
useAutoSave hook debounces (300ms)
     │
     ▼
PATCH /api/heroes/{heroName}
     │
     ▼
HeroesFunction validates + updates DynamoDB
     │
     ▼
SaveIndicator shows ✓ in UI
```

### Impersonation Flow

```
Admin clicks "Login As" on Users page
     │
     ▼
POST /api/admin/impersonate/{userId}
     │
     ▼
Backend returns target user data
     │
     ▼
Frontend stores admin user in localStorage
Sets displayed user to impersonated user
Shows "Viewing as: username" banner
     │
     ▼
All API calls include X-Impersonate-User header
Backend routes to impersonated user's data
     │
     ▼
"Switch Back" restores admin user from localStorage
```

## Security

- **Auth**: Cognito JWT tokens, validated in every Lambda
- **Admin**: Role-based access control on all `/api/admin/*` routes
- **Impersonation**: Logged to audit trail, admin-only
- **CORS**: Configured in API Gateway, restricted to app domain
- **Data isolation**: All queries scoped to authenticated user's PK
- **AI safety**: Jailbreak protection, WoS-only question filtering
