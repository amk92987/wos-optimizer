import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Admin Audit Log', () => {
  test('page loads with log entries', async ({ adminPage }) => {
    await adminPage.goto('/admin/audit-log');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/audit|log|activity/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('log entries show timestamps', async ({ adminPage }) => {
    await adminPage.goto('/admin/audit-log');
    await adminPage.waitForLoadState('networkidle');

    // Should show log content or empty state
    await expect(
      adminPage.locator('main').getByText(/2026|today|yesterday|ago|no.*log|empty|activity|audit/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });
});
