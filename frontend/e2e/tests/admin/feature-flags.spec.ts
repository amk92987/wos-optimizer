import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin Feature Flags', () => {
  test('page loads with flag list', async ({ adminPage }) => {
    await adminPage.goto('/admin/feature-flags');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/feature flag|flags/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('flags have enable/disable buttons', async ({ adminPage }) => {
    await adminPage.goto('/admin/feature-flags');
    await adminPage.waitForLoadState('networkidle');

    // Flags use "Click to enable" / "Click to disable" buttons
    const toggleBtns = adminPage.getByRole('button', { name: /click to enable|click to disable/i });
    await expect(toggleBtns.first()).toBeVisible({ timeout: 10_000 });
  });

  test('flag descriptions are visible', async ({ adminPage }) => {
    await adminPage.goto('/admin/feature-flags');
    await adminPage.waitForLoadState('networkidle');

    // Should show known flags
    await expect(
      adminPage.getByText(/hero_recommendations|analytics|beta/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('can toggle a flag', async ({ adminPage }) => {
    await adminPage.goto('/admin/feature-flags');
    await adminPage.waitForLoadState('networkidle');
    await adminPage.waitForTimeout(1000);

    // Get all toggle buttons and record initial count of enabled/disabled
    const enableBtns = adminPage.getByRole('button', { name: 'Click to enable' });
    const disableBtns = adminPage.getByRole('button', { name: 'Click to disable' });
    const initialEnableCount = await enableBtns.count();
    const initialDisableCount = await disableBtns.count();

    // Click the first "Click to enable" button to enable a flag
    if (initialEnableCount > 0) {
      await enableBtns.first().click();
      await adminPage.waitForTimeout(1500);

      // Should now have one fewer "Click to enable" and one more "Click to disable"
      const newDisableCount = await disableBtns.count();
      expect(newDisableCount).toBe(initialDisableCount + 1);

      // Toggle it back - click the newest "Click to disable" button
      await disableBtns.first().click();
      await adminPage.waitForTimeout(1000);
    }
  });
});
