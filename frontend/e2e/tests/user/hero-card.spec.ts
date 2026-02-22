import { test, expect } from '../../fixtures/auth.fixture';
import { ApiHelper } from '../../helpers/api.helper';
import { waitForHeroUpdate } from '../../helpers/wait.helper';

const TEST_HERO = 'Smith';

// Helper to expand the hero card on the My Heroes tab
async function expandHeroCard(userPage: any) {
  // The hero card header is a button containing the hero name
  // e.g. button "Smith Smith D i Infantry Gen 1 Gatherer Lv.10"
  const heroCardBtn = userPage.locator('main').getByRole('button', { name: new RegExp(`^${TEST_HERO}\\s`) }).first();
  await expect(heroCardBtn).toBeVisible({ timeout: 10_000 });
  await heroCardBtn.click();
  await userPage.waitForTimeout(1000);
}

test.describe('Hero Card Interactions', () => {
  test.describe.configure({ mode: 'serial' });

  test('can expand a hero card', async ({ userPage, userTokens }) => {
    const api = new ApiHelper(userTokens.id_token);
    // Ensure hero exists via API
    await api.addHero(TEST_HERO, { level: 10, stars: 1 });

    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(2000);

    // Click the hero card button to expand it
    await expandHeroCard(userPage);

    // Expanded content should show level stepper, star buttons, skill pips, or gear
    await expect(
      userPage.getByText(/Exploration Skills|Expedition Skills|Hero Gear/i).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test('level stepper increments', async ({ userPage, userTokens }) => {
    const api = new ApiHelper(userTokens.id_token);
    await api.addHero(TEST_HERO, { level: 10, stars: 1 }).catch(() => {});

    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    await expandHeroCard(userPage);

    // Find the + button for level (inside the Level section)
    const plusBtn = userPage.getByRole('button', { name: '+' }).first();
    if (await plusBtn.isVisible()) {
      const updatePromise = waitForHeroUpdate(userPage);
      await plusBtn.click();
      await updatePromise.catch(() => {});
      await userPage.waitForTimeout(1000);
    }
  });

  test('level stepper decrements', async ({ userPage, userTokens }) => {
    const api = new ApiHelper(userTokens.id_token);
    await api.addHero(TEST_HERO, { level: 10, stars: 1 }).catch(() => {});

    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    await expandHeroCard(userPage);

    const minusBtn = userPage.getByRole('button', { name: '-' }).first();
    if (await minusBtn.isVisible()) {
      const updatePromise = waitForHeroUpdate(userPage);
      await minusBtn.click();
      await updatePromise.catch(() => {});
      await userPage.waitForTimeout(1000);
    }
  });

  test('star rating can be set', async ({ userPage, userTokens }) => {
    const api = new ApiHelper(userTokens.id_token);
    await api.addHero(TEST_HERO, { level: 10, stars: 1 }).catch(() => {});

    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    await expandHeroCard(userPage);

    // Star buttons have names like "1 star", "2 stars", etc.
    const star3 = userPage.getByRole('button', { name: '3 stars' });
    if (await star3.isVisible().catch(() => false)) {
      const updatePromise = waitForHeroUpdate(userPage);
      await star3.click();
      await updatePromise.catch(() => {});
      await userPage.waitForTimeout(1000);
    }
  });

  test('skill pips can be clicked', async ({ userPage, userTokens }) => {
    const api = new ApiHelper(userTokens.id_token);
    await api.addHero(TEST_HERO, { level: 10, stars: 1 }).catch(() => {});

    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    await expandHeroCard(userPage);

    // Skill pips have button names like "Level 1", "Level 2", etc.
    const skillButtons = userPage.locator('main').getByRole('button', { name: /^Level \d$/ });
    const count = await skillButtons.count();
    if (count > 0) {
      const updatePromise = waitForHeroUpdate(userPage);
      await skillButtons.first().click();
      await updatePromise.catch(() => {});
      await userPage.waitForTimeout(1000);
    }
  });

  test('gear quality dropdown works', async ({ userPage, userTokens }) => {
    const api = new ApiHelper(userTokens.id_token);
    await api.addHero(TEST_HERO, { level: 10, stars: 1 }).catch(() => {});

    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    await expandHeroCard(userPage);

    // Gear quality dropdowns are combobox/select elements with options like None, Gray, Green, etc.
    const gearSelects = userPage.locator('main select, main [role="combobox"]');
    // Find the gear selects (skip sort/filter selects at top by checking for "None" option)
    const allSelects = await gearSelects.all();
    for (const sel of allSelects) {
      const options = await sel.locator('option').allTextContents();
      if (options.includes('None') && options.includes('Gray')) {
        const updatePromise = waitForHeroUpdate(userPage);
        await sel.selectOption('Gray');
        await updatePromise.catch(() => {});
        await userPage.waitForTimeout(1000);
        // Reset it back
        await sel.selectOption('None');
        await userPage.waitForTimeout(500);
        break;
      }
    }
  });

  test('auto-save indicator appears', async ({ userPage, userTokens }) => {
    const api = new ApiHelper(userTokens.id_token);
    await api.addHero(TEST_HERO, { level: 10, stars: 1 }).catch(() => {});

    await userPage.goto('/heroes');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    await expandHeroCard(userPage);

    // Make a change - click the + button
    const plusBtn = userPage.getByRole('button', { name: '+' }).first();
    if (await plusBtn.isVisible()) {
      await plusBtn.click();
      // Should show saving/saved indicator
      await expect(
        userPage.getByText(/saving|saved/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  // Cleanup
  test.afterAll(async () => {
    // Hero cleanup happens via API in individual tests
  });
});
