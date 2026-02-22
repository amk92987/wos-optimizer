import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Lineups Page', () => {
  test('page loads with lineup tabs', async ({ userPage }) => {
    await userPage.goto('/lineups');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/lineup|rally|garrison|bear trap/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('can select a game mode', async ({ userPage }) => {
    await userPage.goto('/lineups');
    await userPage.waitForLoadState('networkidle');

    // Click on a lineup type tab
    const rallyTab = userPage.getByRole('button', { name: /rally leader|rally/i }).first();
    if (await rallyTab.isVisible()) {
      await rallyTab.click();
      await userPage.waitForTimeout(2000);

      // Should show hero slots or lineup content
      await expect(
        userPage.getByText(/infantry|lancer|marksman|lead|slot/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('troop ratio is displayed', async ({ userPage }) => {
    await userPage.goto('/lineups');
    await userPage.waitForLoadState('networkidle');

    // Select a game mode that shows troop ratios
    const bearTrapTab = userPage.getByRole('button', { name: /bear trap/i });
    if (await bearTrapTab.isVisible()) {
      await bearTrapTab.click();
      await userPage.waitForTimeout(2000);
    }

    // Should display ratio information
    await expect(
      userPage.getByText(/%|ratio|infantry|marksman/i).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test('joiner tab shows recommendations', async ({ userPage }) => {
    await userPage.goto('/lineups');
    await userPage.waitForLoadState('networkidle');

    const joinerTab = userPage.getByRole('button', { name: /joiner/i }).first();
    if (await joinerTab.isVisible()) {
      await joinerTab.click();
      await userPage.waitForTimeout(2000);

      await expect(
        userPage.getByText(/joiner|expedition|skill/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });
});
