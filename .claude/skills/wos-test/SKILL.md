---
name: wos-test
description: Run and manage Playwright E2E tests, QA validation scripts, and data audits. Use to verify changes, run test suites, or validate data integrity.
allowed-tools: Bash, Read, Glob, Grep
---

# WoS Testing Agent - E2E Tests, QA, & Data Validation

## Purpose
Runs and manages the testing infrastructure including Playwright E2E tests against the dev environment, Python QA validation scripts, and data integrity audits.

## When to Use
- Running E2E tests after frontend/backend changes
- Verifying specific feature areas (heroes, auth, admin)
- Running QA checks before deployment
- Validating data file integrity
- Debugging test failures
- Writing or modifying test specs

## Playwright E2E Tests

### Configuration
- **Config file**: `frontend/e2e/playwright.config.ts`
- **Target**: `https://wosdev.randomchaoslabs.com` (dev environment only)
- **Test directory**: `frontend/e2e/tests/`
- **Credentials**: `frontend/e2e/.env.test` (gitignored)
- **Auth**: Global setup logs in via API, fixtures inject tokens into localStorage
- **Browsers**: Chromium (desktop) + Mobile Chrome (for mobile-nav tests only)
- **Workers**: 2 parallel workers
- **Retries**: 1 retry on failure
- **Timeouts**: 60s per test, 10s per action, 15s per navigation, 5s per assertion

### Test Accounts
- Regular user: `e2e-user@test.com` (from .env.test E2E_USER_EMAIL)
- Admin user: `e2e-admin@test.com` (from .env.test E2E_ADMIN_EMAIL)

### Test Structure (113 tests, 29 spec files)

```
frontend/e2e/tests/
├── admin/                        # Admin page tests
│   ├── ai-settings.spec.ts      # AI configuration
│   ├── announcements.spec.ts    # System announcements
│   ├── audit-log.spec.ts        # Audit log viewer
│   ├── dashboard.spec.ts        # Admin dashboard
│   ├── data-integrity.spec.ts   # Data validation tools
│   ├── database.spec.ts         # Database browser
│   ├── feature-flags.spec.ts    # Feature flag toggles
│   ├── impersonation.spec.ts    # User impersonation
│   └── users.spec.ts            # User management
├── auth/                         # Authentication tests
│   ├── forgot-password.spec.ts  # Password reset flow
│   ├── login.spec.ts            # Login flow
│   ├── logout.spec.ts           # Logout flow
│   └── register.spec.ts         # Registration flow
├── user/                         # User-facing page tests
│   ├── advisor.spec.ts          # AI advisor
│   ├── chief.spec.ts            # Chief gear & charms
│   ├── hero-card.spec.ts        # Hero card interactions
│   ├── heroes.spec.ts           # Heroes page
│   ├── home.spec.ts             # Home page
│   ├── inbox.spec.ts            # Notifications inbox
│   ├── lineups.spec.ts          # Lineup builder
│   ├── packs.spec.ts            # Pack analyzer
│   ├── profiles.spec.ts         # Profile management
│   ├── settings.spec.ts         # User settings
│   └── upgrades.spec.ts         # Upgrade calculators
├── smoke/
│   └── static-pages.spec.ts     # Static page accessibility
└── navigation/
    ├── mobile-nav.spec.ts       # Mobile navigation (Pixel 5)
    └── sidebar.spec.ts          # Desktop sidebar navigation
```

### Auth Setup
- `frontend/e2e/global-setup.ts` - Logs in both test accounts via API, saves tokens to `.auth/`
- `frontend/e2e/fixtures/` - Test fixtures inject tokens into browser localStorage
- `frontend/e2e/helpers/auth.helper.ts` - API login helper function

### NPM Test Commands

```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend

# Run all E2E tests (headless, ~2.2 min)
npm run test:e2e

# Run with interactive UI
npm run test:e2e:ui

# Run headed (visible browser)
npm run test:e2e:headed

# Run with debugger
npm run test:e2e:debug

# Run specific test suites
npm run test:e2e:auth     # Auth tests only
npm run test:e2e:user     # User page tests only
npm run test:e2e:admin    # Admin page tests only
npm run test:e2e:heroes   # Hero-specific tests only
```

### Running Individual Spec Files
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend

# Run a single spec file
npx playwright test --config=e2e/playwright.config.ts tests/user/heroes.spec.ts

# Run with grep pattern
npx playwright test --config=e2e/playwright.config.ts --grep "hero card"

# Run in headed mode with specific file
npx playwright test --config=e2e/playwright.config.ts tests/admin/feature-flags.spec.ts --headed
```

### Test Reports
```bash
# View HTML test report
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend
npx playwright show-report e2e/playwright-report
```

Test artifacts on failure:
- Screenshots: `frontend/e2e/test-results/` (only on failure)
- Videos: `frontend/e2e/test-results/` (retained on failure)
- Traces: `frontend/e2e/test-results/` (on first retry)

### Key E2E Gotchas

1. **"All Heroes" button**: Use `{ exact: true }` matcher -- "Browse All Heroes" also matches
   ```typescript
   await page.getByRole('button', { name: 'All Heroes', exact: true }).click();
   ```

2. **Hero cards are buttons**: Full text content is inside the button element
   ```typescript
   await page.getByRole('button', { name: /Jessie/ }).click();
   ```

3. **Feature flag toggles**: Text is "Click to enable" / "Click to disable"
   ```typescript
   await page.getByRole('button', { name: 'Click to enable' }).first().click();
   ```

4. **Admin impersonation**: Uses a "Login" button, redirects to `/`, shows "Viewing as:" banner
   ```typescript
   await page.getByRole('button', { name: 'Login' }).click();
   await expect(page.getByText('Viewing as:')).toBeVisible();
   ```

5. **Profile duplicate**: Opens form with Cancel + confirm "Duplicate" button

6. **Logout "Sign Out"**: May need `force: true` (element in dropdown outside viewport)
   ```typescript
   await page.getByText('Sign Out').click({ force: true });
   ```

7. **Tests run against DEV only**: Never point Playwright at the live URL

## QA Validation Scripts

### Automated QA Check
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer
.venv/Scripts/python.exe scripts/run_qa_check.py
```

Checks:
- All JSON files parse correctly
- Cross-reference integrity (hero count matches images, etc.)
- Key data point validation
- CSS file exists and is reasonable size

### Data Integrity Audit
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer
.venv/Scripts/python.exe scripts/run_data_audit.py
```

Checks:
- JSON validity across all 67 data files
- Hero data consistency
- Chief gear slot validation
- Upgrade edge graph integrity
- Confidence grade review

## Data File Sync Verification

Two copies of heroes.json must match:
```bash
diff /c/Users/adam/IdeaProjects/wos-optimizer/data/heroes.json /c/Users/adam/IdeaProjects/wos-optimizer/backend/data/heroes.json
```

## Pre-Deployment Test Strategy

### Before Dev Deploy
1. Run frontend build: `cd frontend && npm run build`
2. Run data sync check: `diff data/heroes.json backend/data/heroes.json`
3. Validate SAM template: `cd infra && sam validate`

### After Dev Deploy
1. Run smoke tests: `cd frontend && npx playwright test --config=e2e/playwright.config.ts tests/smoke/`
2. Run targeted tests for changed areas
3. Run full suite if time permits: `cd frontend && npm run test:e2e`

### Before Live Deploy
1. All dev tests passing
2. Manual verification on dev site
3. QA script passes: `python scripts/run_qa_check.py`

## Debugging Test Failures

### 1. Check Test Report
```bash
cd /c/Users/adam/IdeaProjects/wos-optimizer/frontend
npx playwright show-report e2e/playwright-report
```

### 2. Run in Debug Mode
```bash
npm run test:e2e:debug
```
Opens Playwright Inspector with step-through debugging.

### 3. Run Headed to Watch
```bash
npx playwright test --config=e2e/playwright.config.ts tests/user/heroes.spec.ts --headed
```

### 4. Check Dev Environment
- Is dev deployed and accessible? `curl -s -o /dev/null -w "%{http_code}" https://wosdev.randomchaoslabs.com`
- Are APIs responding? `curl -s https://iofrdh7vgl.execute-api.us-east-1.amazonaws.com/dev/health`
- Are test credentials still valid? Check global-setup output

### 5. Common Failure Causes
- **Timeout**: Dev environment cold start, increase timeout or add waitFor
- **Element not found**: Page layout changed, update selector
- **Auth failure**: Test account credentials expired or changed
- **Flaky tests**: Race conditions, add explicit waits
- **404 errors**: Frontend not deployed to dev S3

## Workflow

1. **Determine what to test** - Specific area, smoke test, or full suite?
2. **Check prerequisites** - Dev environment up? Credentials valid?
3. **Run tests** - Choose appropriate command (suite, file, or grep)
4. **Analyze results** - Check report, screenshots, traces
5. **Debug failures** - Use headed/debug mode if needed
6. **Report findings** - Summary of pass/fail with failure details
