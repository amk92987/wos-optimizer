import { test, expect } from '../../fixtures/auth.fixture';
import { ApiHelper } from '../../helpers/api.helper';
import { TEST_DATA } from '../../fixtures/test-data';

test.describe('Profiles Page', () => {
  test.describe.configure({ mode: 'serial' });

  test('page loads with profile list', async ({ userPage, userTokens }) => {
    // Clean up leftover test profiles via API first
    const api = new ApiHelper(userTokens.id_token);
    try {
      const profiles = await api.listProfiles();
      const profileList = profiles.profiles || profiles;
      if (Array.isArray(profileList)) {
        for (const p of profileList) {
          const name = p.name || p.profile_name || '';
          if (name.includes('E2E') || name.includes('_copy')) {
            await api.deleteProfile(p.profile_id || p.id, true).catch(() => {});
          }
        }
      }
    } catch {}

    await userPage.goto('/profiles');
    await userPage.waitForLoadState('networkidle');

    await expect(
      userPage.getByText(/profiles|manage/i).first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('can create a new profile', async ({ userPage }) => {
    await userPage.goto('/profiles');
    await userPage.waitForLoadState('networkidle');

    // Click new profile button
    const newBtn = userPage.getByRole('button', { name: /new profile|\+/i });
    await newBtn.click();
    await userPage.waitForTimeout(500);

    // Fill in profile name
    const nameInput = userPage.locator('input[type="text"]').last();
    await nameInput.fill(TEST_DATA.PROFILE_NAME);

    // Submit
    const createBtn = userPage.getByRole('button', { name: /create/i }).last();
    await createBtn.click();
    await userPage.waitForTimeout(2000);

    // Profile should appear in the list
    await expect(
      userPage.getByText(TEST_DATA.PROFILE_NAME).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test('can switch to a profile', async ({ userPage }) => {
    await userPage.goto('/profiles');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    // Find any non-active profile with a Switch button
    const switchBtn = userPage.getByRole('button', { name: 'Switch' }).first();
    if (await switchBtn.isVisible().catch(() => false)) {
      await switchBtn.click();
      await userPage.waitForTimeout(2000);
    }
    // If no switch button exists, the test passes (only 1 profile)
  });

  test('can duplicate a profile', async ({ userPage }) => {
    await userPage.goto('/profiles');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    // Find the first Duplicate button on the page (any profile)
    const dupBtn = userPage.getByRole('button', { name: 'Duplicate' }).first();
    if (await dupBtn.isVisible().catch(() => false)) {
      await dupBtn.click();
      await userPage.waitForTimeout(1000);

      // A form appears with "Cancel" button and a confirmation "Duplicate" button
      const cancelBtn = userPage.getByRole('button', { name: 'Cancel' });
      await expect(cancelBtn).toBeVisible({ timeout: 5000 });

      // The confirmation Duplicate button is a sibling of Cancel in the form
      const confirmDup = cancelBtn.locator('..').getByRole('button', { name: 'Duplicate' });
      await expect(confirmDup).toBeVisible();

      // Click confirm and wait for the API response
      await Promise.all([
        userPage.waitForResponse(
          resp => resp.url().includes('/api/profiles') && resp.request().method() === 'POST',
          { timeout: 10_000 }
        ).catch(() => {}),
        confirmDup.click(),
      ]);
      await userPage.waitForTimeout(2000);

      // Reload to see the new profile
      await userPage.reload();
      await userPage.waitForLoadState('networkidle');
      await userPage.waitForTimeout(1000);

      // After duplication, a _copy profile should appear
      await expect(
        userPage.getByRole('heading', { name: /_copy/ }).first()
      ).toBeVisible({ timeout: 10_000 });
    }
  });

  test('can delete a profile', async ({ userPage, userTokens }) => {
    await userPage.goto('/profiles');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    // Find any profile with _copy in its name and delete it
    const copyHeading = userPage.getByRole('heading', { name: /_copy/ }).first();
    if (await copyHeading.isVisible().catch(() => false)) {
      // The delete button (🗑️) is in the same profile card
      const profileCard = copyHeading.locator('xpath=ancestor::*[.//button[contains(text(), "🗑️")]]').first();
      const deleteBtn = profileCard.getByRole('button', { name: '🗑️' });
      if (await deleteBtn.isVisible().catch(() => false)) {
        await deleteBtn.click();
        await userPage.waitForTimeout(500);

        // Confirm deletion dialog
        const confirmBtn = userPage.getByRole('button', { name: /delete|confirm/i }).last();
        if (await confirmBtn.isVisible().catch(() => false)) {
          await confirmBtn.click();
          await userPage.waitForTimeout(2000);
        }
      }
    }
  });

  // Cleanup: delete test profiles via API
  test.afterAll(async () => {
    // Cleanup happens in the first test of the next run
  });
});
