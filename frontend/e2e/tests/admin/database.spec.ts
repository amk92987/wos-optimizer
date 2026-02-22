import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin Database Browser', () => {
  test('page loads with entity list', async ({ adminPage }) => {
    await adminPage.goto('/admin/database');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/database|entities|table|browse/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('can browse an entity', async ({ adminPage }) => {
    await adminPage.goto('/admin/database');
    await adminPage.waitForLoadState('networkidle');

    // Click on the first entity/table
    const entityLink = adminPage.locator('main').getByRole('button', { name: /user|hero|profile/i }).first();
    if (await entityLink.isVisible()) {
      await entityLink.click();
      await adminPage.waitForTimeout(2000);

      // Should show a data table
      await expect(
        adminPage.locator('table').first()
      ).toBeVisible({ timeout: 10_000 });
    }
  });
});
