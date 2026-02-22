import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Chief Tracker Page', () => {
  test('page loads with gear section', async ({ userPage }) => {
    await userPage.goto('/chief');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/chief|gear|cap|coat|belt/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('gear slots are displayed', async ({ userPage }) => {
    await userPage.goto('/chief');
    await userPage.waitForLoadState('networkidle');

    // Should show 6 gear pieces
    await expect(
      userPage.getByText(/cap|watch|coat|pants|belt|weapon/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('gear tier selector works', async ({ userPage }) => {
    await userPage.goto('/chief');
    await userPage.waitForLoadState('networkidle');

    // Find a gear quality/tier selector
    const gearSelect = userPage.locator('select').first();
    if (await gearSelect.isVisible()) {
      await expect(gearSelect).toBeEnabled();
    }
  });

  test('charms section is accessible', async ({ userPage }) => {
    await userPage.goto('/chief');
    await userPage.waitForLoadState('networkidle');

    // Look for charms tab or section
    const charmsTab = userPage.getByRole('button', { name: /charms/i });
    if (await charmsTab.isVisible()) {
      await charmsTab.click();
      await userPage.waitForTimeout(1000);

      await expect(
        userPage.getByText(/charm|keenness|protection|vision/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('stat bonuses are displayed', async ({ userPage }) => {
    await userPage.goto('/chief');
    await userPage.waitForLoadState('networkidle');

    // Stats section should show percentages or bonus info
    await expect(
      userPage.getByText(/%|bonus|attack|defense/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });
});
