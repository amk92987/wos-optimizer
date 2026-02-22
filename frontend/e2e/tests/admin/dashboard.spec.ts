import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin Dashboard', () => {
  test('page loads with metrics', async ({ adminPage }) => {
    await adminPage.goto('/admin');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/dashboard|admin|users|profiles/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('shows user count metrics', async ({ adminPage }) => {
    await adminPage.goto('/admin');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/total users|active|users/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('navigation to users page works', async ({ adminPage }) => {
    await adminPage.goto('/admin');
    await adminPage.waitForLoadState('networkidle');

    const usersLink = adminPage.getByText(/users/i).first();
    await usersLink.click();
    await adminPage.waitForURL(/admin\/users/, { timeout: 10_000 });
  });

  test('admin sidebar shows admin navigation', async ({ adminPage }) => {
    await adminPage.goto('/admin');
    await adminPage.waitForLoadState('networkidle');

    // Admin sidebar should have admin-specific items
    await expect(
      adminPage.getByText(/feature flags|audit log|database/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });
});
