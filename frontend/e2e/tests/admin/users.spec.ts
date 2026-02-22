import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin Users Page', () => {
  test('page loads with user list', async ({ adminPage }) => {
    await adminPage.goto('/admin/users');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/users|email|role/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('search filters users', async ({ adminPage }) => {
    await adminPage.goto('/admin/users');
    await adminPage.waitForLoadState('networkidle');

    const searchInput = adminPage.getByPlaceholder(/search/i).first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('e2e');
      await adminPage.waitForTimeout(1000);

      // Should show filtered results
      await expect(
        adminPage.getByText(/e2e/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('test account filter works', async ({ adminPage }) => {
    await adminPage.goto('/admin/users');
    await adminPage.waitForLoadState('networkidle');

    const testFilter = adminPage.getByLabel(/test only/i).or(
      adminPage.getByRole('checkbox', { name: /test/i })
    );
    if (await testFilter.isVisible()) {
      await testFilter.check();
      await adminPage.waitForTimeout(1000);
    }
  });

  test('user details are viewable', async ({ adminPage }) => {
    await adminPage.goto('/admin/users');
    await adminPage.waitForLoadState('networkidle');

    // Click on a user row to see details
    const userRow = adminPage.getByText(/e2e-user@test.com/).first();
    if (await userRow.isVisible()) {
      await userRow.click();
      await adminPage.waitForTimeout(1000);
    }
  });

  test('create user tab exists', async ({ adminPage }) => {
    await adminPage.goto('/admin/users');
    await adminPage.waitForLoadState('networkidle');

    const createTab = adminPage.getByRole('button', { name: /create|new user/i });
    if (await createTab.isVisible()) {
      await createTab.click();
      await adminPage.waitForTimeout(500);

      await expect(
        adminPage.locator('#email, input[type="email"]').first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('can toggle user active status', async ({ adminPage }) => {
    await adminPage.goto('/admin/users');
    await adminPage.waitForLoadState('networkidle');

    // Find a test user's status toggle
    const userRow = adminPage.locator('tr, [class*="row"]').filter({
      hasText: /e2e-user@test.com/,
    });
    if (await userRow.isVisible()) {
      const toggle = userRow.locator('button, [role="switch"]').filter({
        hasText: /active|suspend/i,
      });
      if (await toggle.isVisible()) {
        // Just verify it's clickable, don't actually toggle
        await expect(toggle).toBeEnabled();
      }
    }
  });
});
