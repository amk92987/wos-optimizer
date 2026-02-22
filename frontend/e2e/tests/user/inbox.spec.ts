import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Inbox Page', () => {
  test('page loads with tabs', async ({ userPage }) => {
    await userPage.goto('/inbox');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/inbox|notification|message/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('notifications section is accessible', async ({ userPage }) => {
    await userPage.goto('/inbox');
    await userPage.waitForLoadState('networkidle');

    const notifTab = userPage.getByRole('button', { name: /notification/i }).first();
    if (await notifTab.isVisible()) {
      await notifTab.click();
      await userPage.waitForTimeout(1000);
    }

    // Should show notifications or empty state
    await expect(
      userPage.getByText(/notification|no.*notification|empty/i).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test('messages section is accessible', async ({ userPage }) => {
    await userPage.goto('/inbox');
    await userPage.waitForLoadState('networkidle');

    const msgTab = userPage.getByRole('button', { name: /message/i }).first();
    if (await msgTab.isVisible()) {
      await msgTab.click();
      await userPage.waitForTimeout(1000);
    }

    // Should show messages or empty state
    await expect(
      userPage.getByText(/message|thread|no.*message|empty/i).first()
    ).toBeVisible({ timeout: 5000 });
  });
});
