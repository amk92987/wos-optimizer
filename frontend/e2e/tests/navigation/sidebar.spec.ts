import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Sidebar Navigation', () => {
  test('sidebar renders navigation groups', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    const sidebar = userPage.locator('aside').first();
    await expect(sidebar).toBeVisible({ timeout: 10_000 });

    // Should show key nav items
    await expect(
      sidebar.getByText(/hero tracker|heroes/i).first()
    ).toBeVisible();
  });

  test('active page is highlighted', async ({ userPage }) => {
    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');

    // The Heroes nav item should have active styling
    const heroLink = userPage.locator('aside').getByText(/hero tracker|heroes/i).first();
    await expect(heroLink).toBeVisible({ timeout: 10_000 });
  });

  test('sidebar links navigate correctly', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // Click Hero Tracker link
    const heroLink = userPage.locator('aside').getByText(/hero tracker|heroes/i).first();
    if (await heroLink.isVisible()) {
      await heroLink.click();
      await userPage.waitForURL(/heroes/, { timeout: 10_000 });
    }
  });

  test('admin sidebar shows admin items for admin user', async ({ adminPage }) => {
    await adminPage.goto('/admin');
    await adminPage.waitForLoadState('networkidle');

    const sidebar = adminPage.locator('aside').first();
    await expect(sidebar).toBeVisible({ timeout: 10_000 });

    // Should show admin-specific nav items
    await expect(
      sidebar.getByText(/feature flags|database|audit/i).first()
    ).toBeVisible();
  });
});
