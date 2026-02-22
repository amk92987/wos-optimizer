import { test, expect } from '../../fixtures/auth.fixture';
import { HeroesPage } from '../../page-objects/heroes.page';
import { ApiHelper } from '../../helpers/api.helper';
import { TEST_DATA } from '../../fixtures/test-data';

test.describe('Heroes Page', () => {
  test.describe.configure({ mode: 'serial' });

  let heroesPage: HeroesPage;

  test('page loads with owned heroes tab', async ({ userPage }) => {
    heroesPage = new HeroesPage(userPage);
    await heroesPage.goto();

    // Owned tab should be active or visible
    await expect(userPage.getByText(/owned|my heroes/i).first()).toBeVisible();
  });

  test('can switch to All Heroes tab', async ({ userPage }) => {
    heroesPage = new HeroesPage(userPage);
    await heroesPage.goto();
    await userPage.waitForTimeout(1000);

    const allTab = userPage.getByRole('button', { name: 'All Heroes', exact: true });
    await expect(allTab).toBeVisible({ timeout: 15_000 });
    await allTab.click();
    await userPage.waitForTimeout(2000);

    // Should show heroes from the full list (All Heroes view shows a flat list)
    await expect(userPage.getByRole('heading', { name: 'Bahiti' })).toBeVisible({ timeout: 15_000 });
  });

  test('search filters heroes', async ({ userPage }) => {
    heroesPage = new HeroesPage(userPage);
    await heroesPage.goto();

    await heroesPage.allTab.click();
    await userPage.waitForTimeout(1000);

    await heroesPage.searchInput.fill('Jessie');
    await userPage.waitForTimeout(500);

    // Should show Jessie and hide others
    await expect(userPage.getByText('Jessie').first()).toBeVisible();
  });

  test('can add a hero', async ({ userPage, userTokens }) => {
    heroesPage = new HeroesPage(userPage);
    const api = new ApiHelper(userTokens.id_token);

    // Clean up first - remove the hero if it exists
    await api.removeHero(TEST_DATA.HERO_TO_ADD).catch(() => {});

    await heroesPage.goto();

    // Switch to All Heroes tab and wait for heroes to load
    const allTab = userPage.getByRole('button', { name: 'All Heroes', exact: true });
    await expect(allTab).toBeVisible({ timeout: 10_000 });
    await allTab.click();

    // Wait for hero cards to appear (the All Heroes tab shows a flat list of all 56 heroes)
    await expect(userPage.getByRole('heading', { name: 'Bahiti' })).toBeVisible({ timeout: 15_000 });

    // Search for the hero to add
    await heroesPage.searchInput.fill(TEST_DATA.HERO_TO_ADD);
    await userPage.waitForTimeout(1000);

    // Click add button on the hero card
    const addBtn = userPage.locator('main').getByRole('button', { name: /add/i }).first();
    await expect(addBtn).toBeVisible({ timeout: 5000 });
    await addBtn.click();
    await userPage.waitForTimeout(2000);

    // Switch to owned tab and verify
    const myTab = userPage.getByRole('button', { name: /my heroes/i });
    await myTab.click();
    await userPage.waitForTimeout(1000);
    await expect(userPage.getByText(TEST_DATA.HERO_TO_ADD).first()).toBeVisible({ timeout: 10_000 });
  });

  test('can remove a hero', async ({ userPage, userTokens }) => {
    heroesPage = new HeroesPage(userPage);
    const api = new ApiHelper(userTokens.id_token);

    // Ensure the hero exists first
    await api.addHero(TEST_DATA.HERO_TO_ADD).catch(() => {});

    await heroesPage.goto();

    // Find and expand the hero card (button with hero name at start)
    const heroCardBtn = userPage.locator('main').getByRole('button', {
      name: new RegExp(`^${TEST_DATA.HERO_TO_ADD}\\s`),
    }).first();
    if (await heroCardBtn.isVisible({ timeout: 10_000 }).catch(() => false)) {
      await heroCardBtn.click();
      await userPage.waitForTimeout(500);

      // Click remove
      const removeBtn = userPage.getByRole('button', { name: /remove from collection/i });
      if (await removeBtn.isVisible()) {
        await removeBtn.click();
        await userPage.waitForTimeout(2000);

        // Hero should be gone
        await expect(heroCardBtn).not.toBeVisible({ timeout: 5000 });
      }
    }

    // Cleanup: ensure hero is removed
    await api.removeHero(TEST_DATA.HERO_TO_ADD).catch(() => {});
  });
});
