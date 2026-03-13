import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Quick Tips Page - Experts & New Content', () => {
  test.beforeEach(async ({ userPage }) => {
    await userPage.goto('/quick-tips');
    await userPage.waitForLoadState('networkidle');
  });

  test.describe('Page Structure', () => {
    test('page loads with all tabs visible', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Quick Tips/i).first()
      ).toBeVisible({ timeout: 10_000 });

      const expectedTabs = [
        'Critical Tips',
        'Hidden Gems',
        'Pets',
        'Hero Investment',
        'Alliance (R4/R5)',
        'Common Mistakes',
        'By Category',
      ];

      for (const tabName of expectedTabs) {
        await expect(
          userPage.getByRole('button', { name: tabName, exact: true })
        ).toBeVisible();
      }
    });
  });

  test.describe('By Category Tab - Experts Category', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'By Category', exact: true }).click();
      await userPage.waitForTimeout(500);
    });

    test('experts category appears in category list', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Experts & Treks/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('experts category shows correct tip count', async ({ userPage }) => {
      // The experts category should display "(10 tips)"
      const expertsSection = userPage.locator('details').filter({ hasText: 'Experts & Treks' });
      await expect(expertsSection.getByText(/10 tips/i)).toBeVisible({ timeout: 5000 });
    });

    test('expanding experts category shows expert tips', async ({ userPage }) => {
      // Click the summary to expand the details element
      const expertsSummary = userPage.locator('summary').filter({ hasText: 'Experts & Treks' });
      await expertsSummary.click();
      await userPage.waitForTimeout(500);

      await expect(
        userPage.getByText(/Experts unlock at FC4-FC5/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/Prioritize Valeria and Romulus/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('experts category has Crystal Lab tips', async ({ userPage }) => {
      const expertsSummary = userPage.locator('summary').filter({ hasText: 'Experts & Treks' });
      await expertsSummary.click();
      await userPage.waitForTimeout(500);

      await expect(
        userPage.getByText(/Crystal Laboratory/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/Super Refinement/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('experts category has trek tips', async ({ userPage }) => {
      const expertsSummary = userPage.locator('summary').filter({ hasText: 'Experts & Treks' });
      await expertsSummary.click();
      await userPage.waitForTimeout(500);

      await expect(
        userPage.getByText(/Frontier Trek unlocks after 60/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/Collect ALL free Trek Supplies/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('experts tips have correct priority badges', async ({ userPage }) => {
      const expertsSummary = userPage.locator('summary').filter({ hasText: 'Experts & Treks' });
      await expertsSummary.click();
      await userPage.waitForTimeout(500);

      const expertsSection = userPage.locator('details').filter({ hasText: 'Experts & Treks' });

      // Should have MUST KNOW (critical) badges for FC unlock + Valeria/Romulus tips
      const criticalBadges = expertsSection.getByText('MUST KNOW');
      const criticalCount = await criticalBadges.count();
      expect(criticalCount).toBeGreaterThanOrEqual(2);

      // Should have Important (high) badges
      const highBadges = expertsSection.getByText('Important');
      const highCount = await highBadges.count();
      expect(highCount).toBeGreaterThanOrEqual(3);
    });
  });

  test.describe('Events Category - Wild Brawl', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'By Category', exact: true }).click();
      await userPage.waitForTimeout(500);
    });

    test('events category contains Wild Brawl tip', async ({ userPage }) => {
      // Expand the Events category (name is just "Events")
      const eventsSummary = userPage.locator('summary').filter({ hasText: /^.*Events\b/ });
      await eventsSummary.click();
      await userPage.waitForTimeout(500);

      await expect(
        userPage.getByText(/Wild Brawl/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('Wild Brawl tip mentions F25 requirement', async ({ userPage }) => {
      const eventsSummary = userPage.locator('summary').filter({ hasText: /^.*Events\b/ });
      await eventsSummary.click();
      await userPage.waitForTimeout(500);

      // Should mention F25 or Furnace 25
      await expect(
        userPage.getByText(/Furnace 25|F25/i).first()
      ).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Tab Navigation', () => {
    test('switching between tabs works correctly', async ({ userPage }) => {
      // Go to By Category tab
      await userPage.getByRole('button', { name: 'By Category', exact: true }).click();
      await userPage.waitForTimeout(300);
      await expect(
        userPage.getByText(/All Tips by Category/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Switch to Critical Tips tab
      await userPage.getByRole('button', { name: 'Critical Tips', exact: true }).click();
      await userPage.waitForTimeout(300);
      await expect(
        userPage.getByText(/The most impactful knowledge/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Switch back to By Category
      await userPage.getByRole('button', { name: 'By Category', exact: true }).click();
      await userPage.waitForTimeout(300);
      await expect(
        userPage.getByText(/All Tips by Category/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('Pets tab loads with pet content', async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Pets', exact: true }).click();
      await userPage.waitForTimeout(500);

      await expect(
        userPage.getByText(/pet|combat|refinement/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('Hidden Gems tab loads with insights', async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Hidden Gems', exact: true }).click();
      await userPage.waitForTimeout(500);

      await expect(
        userPage.getByText(/Hidden Gems/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/damage|multiplier|formula/i).first()
      ).toBeVisible({ timeout: 5000 });
    });
  });
});
