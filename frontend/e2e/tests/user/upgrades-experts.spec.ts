import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Upgrades Page - Expert Calculators', () => {
  test.beforeEach(async ({ userPage }) => {
    await userPage.goto('/upgrades');
    await userPage.waitForLoadState('networkidle');

    // Navigate to calculators tab
    const calcTab = userPage.getByRole('button', { name: /calculator/i }).first();
    await calcTab.click();
    await userPage.waitForTimeout(1000);
  });

  test.describe('Calculator Navigation', () => {
    test('experts category shows Expert Skills and Affinity buttons', async ({ userPage }) => {
      await expect(userPage.getByText('Experts', { exact: true })).toBeVisible({ timeout: 5000 });
      await expect(userPage.getByRole('button', { name: 'Expert Skills' })).toBeVisible();
      await expect(userPage.getByRole('button', { name: 'Affinity' })).toBeVisible();
    });

    test('Crystal Lab button appears under Buildings category', async ({ userPage }) => {
      await expect(userPage.getByRole('button', { name: 'Crystal Lab' })).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Expert Skills Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Expert Skills' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with expert and skill selectors', async ({ userPage }) => {
      // Should show the info banner about Books of Knowledge
      await expect(
        userPage.getByText(/Books of Knowledge/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should have expert selector dropdown with all 7 experts
      const expertSelect = userPage.locator('select').first();
      await expect(expertSelect).toBeVisible();

      const options = await expertSelect.locator('option').allTextContents();
      expect(options.length).toBe(7);
      expect(options.some(o => o.includes('Agnes'))).toBeTruthy();
      expect(options.some(o => o.includes('Valeria'))).toBeTruthy();
      expect(options.some(o => o.includes('Romulus'))).toBeTruthy();
      expect(options.some(o => o.includes('Baldur'))).toBeTruthy();
      expect(options.some(o => o.includes('Holger'))).toBeTruthy();
      expect(options.some(o => o.includes('Cyrille'))).toBeTruthy();
      expect(options.some(o => o.includes('Fabian'))).toBeTruthy();
    });

    test('selecting an expert shows their skills', async ({ userPage }) => {
      // Select Valeria (options have format "Valeria — High Marshal")
      const expertSelect = userPage.locator('select').first();
      await expertSelect.selectOption({ index: 1 }); // Valeria is second
      await userPage.waitForTimeout(300);

      // The skill selector should now show Valeria's 4 skills
      const skillSelect = userPage.locator('select').nth(1);
      const skillOptions = await skillSelect.locator('option').allTextContents();
      expect(skillOptions.length).toBe(4);
    });

    test('shows skill description card', async ({ userPage }) => {
      // Default expert (Agnes) should show a skill description with max level info
      await expect(
        userPage.getByText(/Max Lv\./).first()
      ).toBeVisible({ timeout: 10_000 });
    });

    test('default state shows costs (from=1, to=max)', async ({ userPage }) => {
      // Calculator defaults to from=1, to=max — should show results immediately
      await expect(
        userPage.getByText(/Books of Knowledge/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should show the cost table with resource rows
      await expect(
        userPage.locator('table').first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('per-level breakdown table appears', async ({ userPage }) => {
      // Default state already has from=1, to=5 — should show breakdown
      await expect(
        userPage.getByText(/Per-Level Breakdown/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should have table rows for each level transition
      const breakdownTable = userPage.locator('table').nth(1); // Second table is breakdown
      const levelRows = breakdownTable.locator('tbody tr');
      const rowCount = await levelRows.count();
      expect(rowCount).toBeGreaterThanOrEqual(2);
    });

    test('show all skills total toggle works', async ({ userPage }) => {
      // Click the "Show all skills total" button
      const toggleBtn = userPage.getByRole('button', { name: /show all skills total/i });
      await expect(toggleBtn).toBeVisible({ timeout: 5000 });
      await toggleBtn.click();
      await userPage.waitForTimeout(1000);

      // Should show the "All Skills Total" section heading
      await expect(
        userPage.getByRole('heading', { name: /All Skills Total/i })
      ).toBeVisible({ timeout: 10_000 });

      // Should show a Grand Total row within the table
      await expect(
        userPage.locator('td').filter({ hasText: 'Grand Total' }).first()
      ).toBeVisible({ timeout: 10_000 });
    });

    test('switching expert resets levels', async ({ userPage }) => {
      // Modify from level
      const fromInput = userPage.locator('input[type="number"]').first();
      await fromInput.fill('3');

      // Switch to a different expert (Romulus = index 3)
      const expertSelect = userPage.locator('select').first();
      await expertSelect.selectOption({ index: 3 });
      await userPage.waitForTimeout(300);

      // From level should reset to 1
      const fromValue = await fromInput.inputValue();
      expect(fromValue).toBe('1');
    });
  });

  test.describe('Expert Affinity Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Affinity' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with expert selector and milestone dropdowns', async ({ userPage }) => {
      // Should show the info banner about affinity
      await expect(
        userPage.getByText(/affinity/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should have at least 3 selects: Expert, From, To
      const selects = userPage.locator('select');
      const selectCount = await selects.count();
      expect(selectCount).toBeGreaterThanOrEqual(3);
    });

    test('shows sigil and advancement costs for valid range', async ({ userPage }) => {
      // Select a higher "To" milestone
      const toSelect = userPage.locator('select').nth(2);
      await toSelect.selectOption({ index: 3 });
      await userPage.waitForTimeout(300);

      // Should show sigil costs in the results
      await expect(
        userPage.getByText(/sigil/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('displays bonus percentage for valid range', async ({ userPage }) => {
      // Set a higher "To" milestone (index 3 is safe for any expert)
      const toSelect = userPage.locator('select').nth(2);
      await toSelect.selectOption({ index: 3 });
      await userPage.waitForTimeout(500);

      // Should show bonus display with visible percentage text (not hidden option elements)
      // Look for the bonus gain badge which shows "+X.X%"
      await expect(
        userPage.locator('main span').filter({ hasText: /\+\d+\.\d+%/ }).first()
      ).toBeVisible({ timeout: 10_000 });
    });

    test('milestone breakdown table appears with valid range', async ({ userPage }) => {
      const toSelect = userPage.locator('select').nth(2);
      await toSelect.selectOption({ index: 3 });
      await userPage.waitForTimeout(500);

      // Should show milestone breakdown section
      await expect(
        userPage.getByText(/Milestone Breakdown/i).first()
      ).toBeVisible({ timeout: 10_000 });

      // Should have a "Sigils" column header (checking for the word, not exact label)
      await expect(
        userPage.locator('th').filter({ hasText: /Sigils/ }).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('switching expert updates milestone options', async ({ userPage }) => {
      // Switch to Baldur (index 2)
      const expertSelect = userPage.locator('select').first();
      await expertSelect.selectOption({ index: 2 });
      await userPage.waitForTimeout(300);

      // From/To selectors should have milestone options
      const fromSelect = userPage.locator('select').nth(1);
      const fromOptions = await fromSelect.locator('option').allTextContents();
      expect(fromOptions.length).toBeGreaterThan(0);
      expect(fromOptions.some(opt => /level/i.test(opt) || /\d/.test(opt))).toBeTruthy();
    });
  });

  test.describe('Crystal Laboratory Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Crystal Lab' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with FC level and time period inputs', async ({ userPage }) => {
      await expect(
        userPage.getByText(/crystal lab/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should have at least one select (FC level)
      const selects = userPage.locator('select');
      const selectCount = await selects.count();
      expect(selectCount).toBeGreaterThanOrEqual(1);
    });

    test('shows normal refinement costs', async ({ userPage }) => {
      await expect(
        userPage.getByText(/normal refinement/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should show resource rows
      await expect(userPage.getByText(/meat/i).first()).toBeVisible({ timeout: 5000 });
      await expect(userPage.getByText(/wood/i).first()).toBeVisible();
      await expect(userPage.getByText(/coal/i).first()).toBeVisible();
      await expect(userPage.getByText(/iron/i).first()).toBeVisible();
    });

    test('shows expected fire crystal output', async ({ userPage }) => {
      await expect(
        userPage.getByText(/fire crystal/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('shows drop rates reference', async ({ userPage }) => {
      await expect(
        userPage.getByText(/drop rate/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should show individual FC drop amounts
      await expect(userPage.getByText(/1 FC/).first()).toBeVisible({ timeout: 5000 });
    });

    test('shows super refinement section', async ({ userPage }) => {
      await expect(
        userPage.getByText(/super refinement/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/refined fc/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('changing FC level updates costs', async ({ userPage }) => {
      const fcSelect = userPage.locator('select').first();
      const initialContent = await userPage.locator('main').textContent();

      const options = await fcSelect.locator('option').allTextContents();
      if (options.length > 1) {
        await fcSelect.selectOption({ index: options.length - 1 });
        await userPage.waitForTimeout(300);

        const updatedContent = await userPage.locator('main').textContent();
        expect(updatedContent).not.toBe(initialContent);
      }
    });

    test('changing time period updates total column', async ({ userPage }) => {
      const periodInput = userPage.locator('input[type="number"]').first();
      if (await periodInput.isVisible()) {
        await periodInput.fill('30');
        await userPage.waitForTimeout(300);

        // Should show "Total (30d)" in the header
        await expect(
          userPage.getByText(/30d/).first()
        ).toBeVisible({ timeout: 5000 });
      }
    });
  });
});
