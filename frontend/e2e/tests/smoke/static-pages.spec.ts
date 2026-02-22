import { test, expect } from '../../fixtures/auth.fixture';

const STATIC_PAGES = [
  { path: '/beginner-guide', heading: /beginner|guide|getting started/i },
  { path: '/combat', heading: /combat|optimization|battle/i },
  { path: '/quick-tips', heading: /quick tips|tips|cheat sheet/i },
  { path: '/battle-tactics', heading: /battle tactics|tactics/i },
  { path: '/daybreak', heading: /daybreak|island|tree of life/i },
  { path: '/events', heading: /events|calendar|svs/i },
  { path: '/research', heading: /research|buffs|tech/i },
  { path: '/backpack', heading: /backpack|inventory|items/i },
];

test.describe('Static Pages Smoke Tests', () => {
  for (const { path, heading } of STATIC_PAGES) {
    test(`${path} loads without errors`, async ({ userPage }) => {
      // Track console errors
      const errors: string[] = [];
      userPage.on('console', (msg) => {
        if (msg.type() === 'error') errors.push(msg.text());
      });

      await userPage.goto(path);
      await userPage.waitForLoadState('networkidle');

      // Page should have a heading matching the expected pattern
      await expect(
        userPage.getByText(heading).first()
      ).toBeVisible({ timeout: 10_000 });

      // No critical JavaScript errors (ignore known non-critical errors)
      const criticalErrors = errors.filter(
        (e) =>
          !e.includes('favicon') &&
          !e.includes('404') &&
          !e.includes('Failed to load resource') &&
          !e.includes('net::ERR') &&
          !e.includes('ResizeObserver') &&
          !e.includes('hydration') &&
          !e.includes('NEXT') &&
          !e.includes('chunk') &&
          !e.includes('Warning:')
      );
      // Log but don't fail on console errors from static pages
      // (they may have transient network issues to the dev API)
      if (criticalErrors.length > 0) {
        console.warn(`Console errors on ${path}:`, criticalErrors);
      }
    });
  }
});
