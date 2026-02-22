import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Upgrades Page', () => {
  test('page loads with tabs', async ({ userPage }) => {
    await userPage.goto('/upgrades');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/upgrade|recommend|calculator/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('recommendations tab shows content', async ({ userPage }) => {
    await userPage.goto('/upgrades');
    await userPage.waitForLoadState('networkidle');

    // Click recommendations tab if not already active
    const recTab = userPage.getByRole('button', { name: /recommend/i }).first();
    if (await recTab.isVisible()) {
      await recTab.click();
      await userPage.waitForTimeout(2000);
    }

    // Should show recommendation cards or content
    await expect(
      userPage.getByText(/priority|action|hero|upgrade/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('calculators tab shows calculator options', async ({ userPage }) => {
    await userPage.goto('/upgrades');
    await userPage.waitForLoadState('networkidle');

    const calcTab = userPage.getByRole('button', { name: /calculator/i }).first();
    if (await calcTab.isVisible()) {
      await calcTab.click();
      await userPage.waitForTimeout(1000);

      // Should show calculator categories
      await expect(
        userPage.getByText(/enhancement|legendary|mastery|chief gear|charm|war academy|pet/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('enhancement calculator works', async ({ userPage }) => {
    await userPage.goto('/upgrades');
    await userPage.waitForLoadState('networkidle');

    const calcTab = userPage.getByRole('button', { name: /calculator/i }).first();
    if (await calcTab.isVisible()) {
      await calcTab.click();
      await userPage.waitForTimeout(1000);
    }

    // Click enhancement calculator
    const enhBtn = userPage.getByRole('button', { name: /enhancement/i }).first();
    if (await enhBtn.isVisible()) {
      await enhBtn.click();
      await userPage.waitForTimeout(1000);

      // Should show from/to level inputs
      await expect(
        userPage.locator('select, input[type="number"]').first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('chief gear calculator shows stat bonuses', async ({ userPage }) => {
    await userPage.goto('/upgrades');
    await userPage.waitForLoadState('networkidle');

    const calcTab = userPage.getByRole('button', { name: /calculator/i }).first();
    if (await calcTab.isVisible()) {
      await calcTab.click();
      await userPage.waitForTimeout(1000);
    }

    const chiefBtn = userPage.getByRole('button', { name: /chief gear/i }).first();
    if (await chiefBtn.isVisible()) {
      await chiefBtn.click();
      await userPage.waitForTimeout(1000);

      await expect(
        userPage.getByText(/%|bonus|alloy|solution/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });
});
