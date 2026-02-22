import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Packs Page', () => {
  test('page loads with pack content', async ({ userPage }) => {
    await userPage.goto('/packs');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/pack|value|item/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('pack items are interactive', async ({ userPage }) => {
    await userPage.goto('/packs');
    await userPage.waitForLoadState('networkidle');

    // Should have some interactive elements (buttons, inputs, selects)
    const interactiveElements = userPage.locator('button, select, input');
    await expect(interactiveElements.first()).toBeVisible({ timeout: 10_000 });
  });
});
