import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin AI Settings', () => {
  test('page loads with AI configuration', async ({ adminPage }) => {
    await adminPage.goto('/admin/ai');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/ai|settings|advisor/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('mode toggle is visible', async ({ adminPage }) => {
    await adminPage.goto('/admin/ai');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/off|on|unlimited/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('rate limit fields are visible', async ({ adminPage }) => {
    await adminPage.goto('/admin/ai');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/limit|daily|cooldown|rate/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });
});
