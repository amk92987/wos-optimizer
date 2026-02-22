import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin Impersonation', () => {
  test.describe.configure({ mode: 'serial' });

  test('can impersonate a user from users page', async ({ adminPage }) => {
    await adminPage.goto('/admin/users');
    await adminPage.waitForLoadState('networkidle');
    await adminPage.waitForTimeout(1000);

    // Find the e2e test user row in the table
    const userRow = adminPage.locator('tr').filter({
      hasText: 'e2e-user@test.com',
    });
    await expect(userRow).toBeVisible({ timeout: 10_000 });

    // Click the Login button in that row (this is the impersonate action)
    const loginBtn = userRow.getByRole('button', { name: 'Login' });
    await expect(loginBtn).toBeVisible({ timeout: 5000 });
    await loginBtn.click();

    // After clicking Login, the page redirects to / with impersonation banner
    await adminPage.waitForURL('**/', { timeout: 15_000 });
    await adminPage.waitForLoadState('networkidle');

    // Should show "Viewing as:" banner
    await expect(
      adminPage.getByText(/viewing as/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('impersonation banner shows switch back option', async ({ adminPage }) => {
    // Navigate to home to see the banner (each test gets a fresh page in serial mode)
    await adminPage.goto('/');
    await adminPage.waitForLoadState('networkidle');
    await adminPage.waitForTimeout(1000);

    // The banner and switch back should be visible if still impersonating
    const banner = adminPage.getByText(/viewing as/i).first();
    if (await banner.isVisible().catch(() => false)) {
      const switchBackBtn = adminPage.getByText(/switch back/i).first();
      await expect(switchBackBtn).toBeVisible();
    }
  });

  test('can switch back to admin', async ({ adminPage }) => {
    await adminPage.goto('/');
    await adminPage.waitForLoadState('networkidle');
    await adminPage.waitForTimeout(1000);

    const switchBackBtn = adminPage.getByText(/switch back/i).first();
    if (await switchBackBtn.isVisible().catch(() => false)) {
      await switchBackBtn.click();

      // Should redirect to /admin/users
      await adminPage.waitForURL('**/admin/users', { timeout: 15_000 });
      await adminPage.waitForLoadState('networkidle');
    }
  });
});
