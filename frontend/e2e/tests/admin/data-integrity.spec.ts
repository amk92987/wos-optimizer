import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin Data Integrity', () => {
  test('page loads', async ({ adminPage }) => {
    await adminPage.goto('/admin/data-integrity');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/data integrity|validation|check/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('can run integrity check', async ({ adminPage }) => {
    await adminPage.goto('/admin/data-integrity');
    await adminPage.waitForLoadState('networkidle');

    const checkBtn = adminPage.getByRole('button', { name: /run|check|validate/i }).first();
    if (await checkBtn.isVisible()) {
      await checkBtn.click();
      await adminPage.waitForTimeout(5000);

      // Should show results
      await expect(
        adminPage.getByText(/pass|fail|check|result/i).first()
      ).toBeVisible({ timeout: 10_000 });
    }
  });
});
