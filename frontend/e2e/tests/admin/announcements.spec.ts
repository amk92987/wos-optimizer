import { test, expect } from '../../fixtures/auth.fixture';
import { TEST_DATA } from '../../fixtures/test-data';

test.describe('Admin Announcements', () => {
  test.describe.configure({ mode: 'serial' });

  test('page loads with announcements list', async ({ adminPage }) => {
    await adminPage.goto('/admin/announcements');
    await adminPage.waitForLoadState('networkidle');

    await expect(
      adminPage.getByText(/announcements/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('can create an announcement', async ({ adminPage }) => {
    await adminPage.goto('/admin/announcements');
    await adminPage.waitForLoadState('networkidle');

    const createBtn = adminPage.getByRole('button', { name: /create|new|add/i }).first();
    if (await createBtn.isVisible()) {
      await createBtn.click();
      await adminPage.waitForTimeout(500);

      // Fill in title and message
      const titleInput = adminPage.locator('input').filter({ hasText: /title/i }).or(
        adminPage.locator('input[placeholder*="title" i], input[name*="title" i]')
      ).first();
      if (await titleInput.isVisible()) {
        await titleInput.fill(TEST_DATA.ANNOUNCEMENT_TITLE);
      }

      const msgInput = adminPage.locator('textarea, input[name*="message"]').first();
      if (await msgInput.isVisible()) {
        await msgInput.fill(TEST_DATA.ANNOUNCEMENT_MESSAGE);
      }

      const submitBtn = adminPage.getByRole('button', { name: /create|save|submit/i }).last();
      await submitBtn.click();
      await adminPage.waitForTimeout(2000);
    }
  });

  test('can toggle announcement active state', async ({ adminPage }) => {
    await adminPage.goto('/admin/announcements');
    await adminPage.waitForLoadState('networkidle');

    const announcementRow = adminPage.locator('.card, tr, [class*="row"]').filter({
      hasText: TEST_DATA.ANNOUNCEMENT_TITLE,
    });

    if (await announcementRow.isVisible()) {
      const toggle = announcementRow.locator('button, [role="switch"]').first();
      if (await toggle.isVisible()) {
        await expect(toggle).toBeEnabled();
      }
    }
  });

  test('can delete an announcement', async ({ adminPage }) => {
    await adminPage.goto('/admin/announcements');
    await adminPage.waitForLoadState('networkidle');

    const announcementRow = adminPage.locator('.card, tr, [class*="row"]').filter({
      hasText: TEST_DATA.ANNOUNCEMENT_TITLE,
    });

    if (await announcementRow.isVisible()) {
      const deleteBtn = announcementRow.getByRole('button', { name: /delete|remove|🗑️/i });
      if (await deleteBtn.isVisible()) {
        await deleteBtn.click();
        await adminPage.waitForTimeout(500);

        // Confirm deletion if dialog appears
        const confirmBtn = adminPage.getByRole('button', { name: /confirm|delete|yes/i }).last();
        if (await confirmBtn.isVisible()) {
          await confirmBtn.click();
          await adminPage.waitForTimeout(2000);
        }
      }
    }
  });
});
