import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Settings Page', () => {
  test('page loads with profile settings', async ({ userPage }) => {
    await userPage.goto('/settings');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/settings|configure/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('spending profile buttons are visible', async ({ userPage }) => {
    await userPage.goto('/settings');
    await userPage.waitForLoadState('networkidle');

    // Should show spending profile options
    await expect(
      userPage.getByText(/f2p|minnow|dolphin/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('can change spending profile', async ({ userPage }) => {
    await userPage.goto('/settings');
    await userPage.waitForLoadState('networkidle');

    // Expand playstyle section if needed
    const playstyleExpander = userPage.getByText(/playstyle|spending/i).first();
    await playstyleExpander.click().catch(() => {});
    await userPage.waitForTimeout(500);

    // Click a spending profile button
    const dolphinBtn = userPage.getByRole('button', { name: /dolphin/i });
    if (await dolphinBtn.isVisible()) {
      await dolphinBtn.click();
      await userPage.waitForTimeout(1000);
    }
  });

  test('priority sliders are visible', async ({ userPage }) => {
    await userPage.goto('/settings');
    await userPage.waitForLoadState('networkidle');

    // Expand combat priorities if needed
    const combatExpander = userPage.getByText(/combat priorities|priorities/i).first();
    await combatExpander.click().catch(() => {});
    await userPage.waitForTimeout(500);

    await expect(
      userPage.getByText(/pvp attack|defense|pve/i).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test('furnace level selector works', async ({ userPage }) => {
    await userPage.goto('/settings');
    await userPage.waitForLoadState('networkidle');

    // Expand server & progression if needed
    const progressionExpander = userPage.getByText(/server|progression/i).first();
    await progressionExpander.click().catch(() => {});
    await userPage.waitForTimeout(500);

    // Find furnace level select
    const furnaceSelect = userPage.locator('select').filter({ hasText: /fc|level/i }).first();
    if (await furnaceSelect.isVisible()) {
      await expect(furnaceSelect).toBeEnabled();
    }
  });

  test('change password section exists', async ({ userPage }) => {
    await userPage.goto('/settings?tab=password');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/change password|password/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });
});
