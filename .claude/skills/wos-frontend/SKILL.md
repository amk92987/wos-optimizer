---
name: wos-frontend
description: Build and modify Next.js/React/TypeScript frontend pages and components. Covers app router, component patterns, auto-save hooks, API client, auth, Tailwind, and the Arctic Night theme.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(npm:*, npx:*, node:*)
---

# WoS Frontend Development - Next.js / React / TypeScript

## Purpose
Assists with building new pages, creating components, modifying existing UI, and following established frontend patterns for the WoS Optimizer Next.js application.

## When to Use
- Building new pages in `frontend/app/`
- Creating or modifying React components
- Working with the API client or auth system
- Adding hooks or utilities
- Modifying styles, layout, or navigation
- Fixing frontend bugs

## Project Structure

```
frontend/
├── app/                          # Next.js 14 App Router pages
│   ├── layout.tsx                # Root layout (AuthProvider, AppShell)
│   ├── page.tsx                  # Home page
│   ├── globals.css               # Arctic Night theme + Tailwind
│   ├── (auth)/                   # Auth group (login, register, forgot-password)
│   ├── admin/                    # Admin pages (dashboard, users, flags, etc.)
│   ├── heroes/page.tsx           # Hero tracker
│   ├── chief/page.tsx            # Chief gear & charms
│   ├── lineups/page.tsx          # Lineup builder
│   ├── advisor/page.tsx          # AI advisor
│   ├── profiles/page.tsx         # Profile management
│   ├── upgrades/page.tsx         # Upgrade calculators
│   ├── settings/page.tsx         # User settings
│   ├── combat/page.tsx           # Combat guide
│   ├── quick-tips/page.tsx       # Quick reference
│   ├── research/page.tsx         # Research & buffs
│   ├── events/page.tsx           # Event calendar
│   ├── packs/page.tsx            # Pack analyzer
│   ├── daybreak/page.tsx         # Daybreak Island
│   ├── battle-tactics/page.tsx   # Battle tactics
│   ├── beginner-guide/page.tsx   # New player guide
│   ├── backpack/page.tsx         # Inventory tracking
│   └── inbox/page.tsx            # User notifications
├── components/                   # Shared components
│   ├── AppShell.tsx              # Layout wrapper with sidebar
│   ├── Sidebar.tsx               # Navigation sidebar
│   ├── PageLayout.tsx            # Standard page wrapper
│   ├── Expander.tsx              # Collapsible sections
│   ├── HeroCard.tsx              # Hero card with auto-save
│   ├── HeroDetailModal.tsx       # Hero detail modal view
│   ├── HeroRoleBadges.tsx        # Role indicator badges
│   ├── InstallPrompt.tsx         # PWA install prompt
│   ├── ServiceWorkerProvider.tsx # SW registration
│   ├── hero/                     # Hero-specific components
│   │   ├── GearSlotEditor.tsx    # Gear quality/level/mastery
│   │   ├── MythicGearEditor.tsx  # Exclusive gear editor
│   │   ├── NumberStepper.tsx     # [-] value [+] control
│   │   ├── SaveIndicator.tsx     # Auto-save status display
│   │   ├── SkillPips.tsx         # Clickable skill circles
│   │   └── StarRating.tsx        # Stars + ascension pips
│   └── ui/                       # Generic UI components
│       ├── Badge.tsx
│       ├── DataTable.tsx
│       ├── MetricCard.tsx
│       ├── Modal.tsx
│       ├── ProgressBar.tsx
│       ├── Skeleton.tsx
│       ├── Tabs.tsx
│       ├── Toast.tsx
│       ├── Toggle.tsx
│       ├── Tooltip.tsx
│       └── index.ts              # Re-exports all UI components
├── hooks/
│   └── useAutoSave.ts            # Debounced auto-save hook
├── lib/
│   ├── api.ts                    # API client (fetch wrapper + Cognito auth)
│   ├── auth.tsx                  # AuthContext provider + hooks
│   ├── heroRoles.ts              # Hero role tag logic
│   └── useServiceWorker.ts       # Service worker hook
├── e2e/                          # Playwright E2E tests
│   ├── playwright.config.ts
│   ├── global-setup.ts
│   ├── fixtures/
│   ├── helpers/
│   ├── page-objects/
│   └── tests/
├── public/                       # Static assets
├── next.config.js                # Next.js config (static export)
├── tailwind.config.ts            # Tailwind configuration
├── tsconfig.json                 # TypeScript config
└── package.json                  # Dependencies and scripts
```

## Key Patterns

### 1. Page Structure

Every page follows this pattern:

```tsx
'use client';

import { useAuth } from '@/lib/auth';
import PageLayout from '@/components/PageLayout';
import { Tabs } from '@/components/ui';

export default function MyPage() {
  const { user, token } = useAuth();

  return (
    <PageLayout title="Page Title" description="Optional subtitle">
      {/* Page content */}
    </PageLayout>
  );
}
```

### 2. API Client Pattern

The API client in `frontend/lib/api.ts` wraps `fetch` with Cognito token auth:

```typescript
import { API_BASE, getStoredToken } from '@/lib/api';

// Making authenticated API calls
const response = await fetch(`${API_BASE}/heroes`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
});

// The api.ts file also exports typed API helpers:
// authApi.login(), authApi.register(), authApi.me()
// heroesApi.getAll(), heroesApi.update(), etc.
```

Environment variable: `NEXT_PUBLIC_API_URL` sets the API base URL.

### 3. Auth Context

The `AuthProvider` in `frontend/lib/auth.tsx` provides:

```typescript
const { user, token, isLoading, isImpersonating, login, register, logout, impersonate, switchBack } = useAuth();
```

- `user` - Current user object (null if not logged in)
- `token` - Cognito ID token for API calls
- `isLoading` - True during initial auth check
- `isImpersonating` - True when admin is viewing as another user
- Tokens stored in localStorage: `id_token`, `access_token`, `refresh_token`

### 4. Auto-Save Hook

The `useAutoSave` hook in `frontend/hooks/useAutoSave.ts` provides debounced saves:

```typescript
import { useAutoSave } from '@/hooks/useAutoSave';

const { saveField, saveFields, saveStatus } = useAutoSave({
  heroName: hero.hero_name,
  token: token,
  onSaved: () => { /* optional callback */ },
});

// Save a single field (debounced 300ms)
saveField('level', 45);

// Save multiple fields at once
saveFields({ level: 45, stars: 4 });

// saveStatus: 'idle' | 'saving' | 'saved' | 'error'
```

### 5. Component Imports

Use the UI component barrel export:

```typescript
// Import multiple UI components at once
import { Badge, Modal, Tabs, Toggle, Tooltip, Skeleton } from '@/components/ui';

// Import hero-specific components directly
import { NumberStepper } from '@/components/hero/NumberStepper';
import { StarRating } from '@/components/hero/StarRating';
import { SkillPips } from '@/components/hero/SkillPips';
```

### 6. Tailwind + CSS Variables

The project uses Tailwind CSS with custom CSS variables from `globals.css`:

```tsx
// Use CSS variables in Tailwind arbitrary values
<div className="bg-[var(--surface)] text-[var(--text-primary)] border border-[var(--border)]">
  <span className="text-[var(--ice)]">Interactive text</span>
  <span className="text-[var(--text-secondary)]">Secondary text</span>
</div>

// Or use inline styles for dynamic values
<div style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border)' }}>
```

### 7. Tab Navigation

Use the shared Tabs component for consistent tab UX:

```tsx
import { Tabs } from '@/components/ui';

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'details', label: 'Details' },
  { id: 'settings', label: 'Settings' },
];

const [activeTab, setActiveTab] = useState('overview');

<Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
{activeTab === 'overview' && <OverviewContent />}
{activeTab === 'details' && <DetailsContent />}
```

### 8. Admin Page Pattern

Admin pages live under `frontend/app/admin/` and follow:

```tsx
'use client';

import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import PageLayout from '@/components/PageLayout';

export default function AdminSomethingPage() {
  const { user, token } = useAuth();
  const router = useRouter();

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    router.push('/');
    return null;
  }

  return (
    <PageLayout title="Admin: Something">
      {/* Admin content with MetricCard, DataTable, etc. */}
    </PageLayout>
  );
}
```

### 9. Static Export

The app uses `output: 'export'` in `next.config.js` for static S3 hosting:
- No server-side rendering (SSR) or API routes
- All API calls go to the external API Gateway
- Dynamic routes use `generateStaticParams()` if needed
- Images use `next/image` with `unoptimized: true`

### 10. Hero Data Version Tracking

When hero data changes, bump the version to trigger re-fetches on other pages:

```typescript
import { bumpHeroDataVersion, getHeroDataVersion } from '@/lib/api';

// After saving hero changes
bumpHeroDataVersion();

// On page load, check if data is stale
const version = getHeroDataVersion();
```

## Build & Development Commands

```bash
# Install dependencies
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend && npm install

# Development server (localhost:3000)
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend && npm run dev

# Production build (static export to out/)
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend && npm run build

# Lint
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend && npm run lint
```

## Important Conventions

1. **All pages are 'use client'** - Static export means no server components with data fetching
2. **Two hero data copies must stay in sync** - `data/heroes.json` and `backend/data/heroes.json`
3. **No Save/Cancel buttons** on hero data entry - Use auto-save pattern exclusively
4. **Use existing UI components** - Check `components/ui/` before building custom elements
5. **Accessibility matters** - Add ARIA labels, keyboard navigation, semantic HTML
6. **Mobile-first** - All pages must work on mobile (test with Playwright mobile project)
7. **Theme compliance** - Use CSS variables from globals.css, never hardcode colors
8. **Loading states** - Use Skeleton component while fetching data
9. **Error handling** - Use Toast for errors, inline error messages for form validation

## Key Files to Reference Before Building

| Purpose | File |
|---------|------|
| Theme colors & CSS variables | `frontend/app/globals.css` |
| Root layout & providers | `frontend/app/layout.tsx` |
| API client & helpers | `frontend/lib/api.ts` |
| Auth context & hooks | `frontend/lib/auth.tsx` |
| Auto-save hook | `frontend/hooks/useAutoSave.ts` |
| Hero card implementation | `frontend/components/HeroCard.tsx` |
| UI component library | `frontend/components/ui/index.ts` |
| Page layout wrapper | `frontend/components/PageLayout.tsx` |
| Tab component | `frontend/components/ui/Tabs.tsx` |
| Sidebar navigation | `frontend/components/Sidebar.tsx` |

## Workflow

1. **Understand the requirement** - What page/component is being built or modified?
2. **Check existing patterns** - Read similar pages/components for conventions
3. **Use existing components** - Import from `components/ui/` and `components/hero/`
4. **Follow the theme** - CSS variables, dark background, ice-blue accents
5. **Add auto-save** where applicable - No manual save buttons
6. **Ensure responsiveness** - Test mentally against mobile breakpoints
7. **Verify build** - Run `npm run build` to catch TypeScript/Next.js errors
