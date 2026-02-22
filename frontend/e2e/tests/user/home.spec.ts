import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Home / Dashboard', () => {
  test('dashboard loads with stats', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // Should show welcome message or dashboard content
    await expect(
      userPage.getByText(/welcome|dashboard|gen/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('shows user info', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // Should display generation or furnace info
    await expect(
      userPage.getByText(/gen|furnace|lv\./i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('generation timeline renders', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // Should have generation indicators
    await expect(
      userPage.getByText(/gen 1|generation/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('navigation sidebar is visible', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // Sidebar should be visible on desktop
    await expect(userPage.locator('aside').first()).toBeVisible();
  });
});
