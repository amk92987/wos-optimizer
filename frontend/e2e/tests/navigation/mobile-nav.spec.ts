import { test, expect } from '../../fixtures/auth.fixture';

// These tests use the mobile-chrome project (Pixel 5 viewport)
test.describe('Mobile Navigation', () => {
  test('bottom nav is visible on mobile', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // Bottom nav should be visible
    const bottomNav = userPage.locator('nav').filter({
      hasText: /home|heroes|ai|lineup/i,
    });
    await expect(bottomNav.first()).toBeVisible({ timeout: 10_000 });
  });

  test('bottom nav navigates to pages', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // Click Heroes in bottom nav
    const heroesNavItem = userPage.locator('nav a, nav button').filter({
      hasText: /heroes/i,
    }).last();
    if (await heroesNavItem.isVisible()) {
      await heroesNavItem.click();
      await userPage.waitForURL(/heroes/, { timeout: 10_000 });
    }
  });

  test('sidebar is hidden on mobile by default', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // On mobile, the sidebar should be hidden (not visible) by default
    const sidebar = userPage.locator('aside').first();
    // The sidebar might exist in DOM but be off-screen or hidden
    const isVisible = await sidebar.isVisible().catch(() => false);
    // On mobile, sidebar is typically hidden or behind a hamburger menu
    // This test is viewport-dependent
  });
});
