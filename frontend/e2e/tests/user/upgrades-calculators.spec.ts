import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Upgrades Page - Original Calculators', () => {
  test.beforeEach(async ({ userPage }) => {
    await userPage.goto('/upgrades');
    await userPage.waitForLoadState('networkidle');

    // Navigate to calculators tab
    const calcTab = userPage.getByRole('button', { name: /calculator/i }).first();
    await calcTab.click();
    await userPage.waitForTimeout(1000);
  });

  // ── Enhancement Calculator ─────────────────────────────────────────

  test.describe('Enhancement Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Enhancement' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with info banner and level inputs', async ({ userPage }) => {
      // Info banner about Enhancement XP
      await expect(
        userPage.getByText(/Enhancement XP/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should mention pre-Legendary and Mastery prerequisite
      await expect(
        userPage.getByText(/pre-Legendary/i).first()
      ).toBeVisible();

      // Should have From Level and To Level number inputs + Gear Slots select
      const numberInputs = userPage.locator('input[type="number"]');
      await expect(numberInputs.first()).toBeVisible();
      expect(await numberInputs.count()).toBeGreaterThanOrEqual(2);

      // Gear Slots dropdown
      const slotSelect = userPage.locator('select').first();
      await expect(slotSelect).toBeVisible();
      const options = await slotSelect.locator('option').allTextContents();
      expect(options).toContain('1 slot');
      expect(options).toContain('4 slots (all)');
    });

    test('shows cost table with Enhancement XP for default range', async ({ userPage }) => {
      // Default is from=0, to=100 — should show results immediately
      await expect(
        userPage.locator('table').first()
      ).toBeVisible({ timeout: 5000 });

      // Should display "Enhancement XP" as a resource row
      await expect(
        userPage.locator('td').filter({ hasText: 'Enhancement XP' }).first()
      ).toBeVisible();
    });

    test('changing from level updates cost display', async ({ userPage }) => {
      // Get the initial cost table content
      const initialContent = await userPage.locator('table').first().textContent();

      // Change the from level to 50
      const fromInput = userPage.locator('input[type="number"]').first();
      await fromInput.fill('50');
      await userPage.waitForTimeout(300);

      // Cost should change
      const updatedContent = await userPage.locator('table').first().textContent();
      expect(updatedContent).not.toBe(initialContent);
    });

    test('selecting multiple gear slots shows total column', async ({ userPage }) => {
      const slotSelect = userPage.locator('select').first();
      await slotSelect.selectOption('4');
      await userPage.waitForTimeout(300);

      // Should show "Total (4 slots)" column header
      await expect(
        userPage.locator('th').filter({ hasText: /4 slots/ }).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('invalid range shows error message', async ({ userPage }) => {
      // Set from > to
      const fromInput = userPage.locator('input[type="number"]').first();
      const toInput = userPage.locator('input[type="number"]').nth(1);
      await fromInput.fill('90');
      await toInput.fill('10');
      await userPage.waitForTimeout(300);

      await expect(
        userPage.getByText(/lower than/i).first()
      ).toBeVisible({ timeout: 5000 });
    });
  });

  // ── Legendary Enhancement Calculator ───────────────────────────────

  test.describe('Legendary Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Legendary' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with info banner mentioning Mithril and Legendary Gear', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Legendary Enhancement/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/Mithril/i).first()
      ).toBeVisible();
    });

    test('shows three resource rows: XP, Mithril, Legendary Gear', async ({ userPage }) => {
      // Default range 0 -> 100 should show all three resources
      await expect(
        userPage.locator('td').filter({ hasText: 'Gear XP' }).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.locator('td').filter({ hasText: 'Mithril' }).first()
      ).toBeVisible();

      await expect(
        userPage.locator('td').filter({ hasText: 'Legendary Gear' }).first()
      ).toBeVisible();
    });

    test('shows milestone unlocks table', async ({ userPage }) => {
      // Default range 0 -> 100 includes milestones at 1, 20, 40, 60, 80, 100
      await expect(
        userPage.getByText(/Milestone Unlocks/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should show Level 20 milestone row
      await expect(
        userPage.locator('td').filter({ hasText: 'Level 20' }).first()
      ).toBeVisible();

      // Should show Level 80 milestone row
      await expect(
        userPage.locator('td').filter({ hasText: 'Level 80' }).first()
      ).toBeVisible();
    });

    test('changing level range updates milestone display', async ({ userPage }) => {
      // Set range 0 -> 30 — should only show milestones at 1 and 20
      const toInput = userPage.locator('input[type="number"]').nth(1);
      await toInput.fill('30');
      await userPage.waitForTimeout(300);

      await expect(
        userPage.locator('td').filter({ hasText: 'Level 20' }).first()
      ).toBeVisible({ timeout: 5000 });

      // Level 40 should NOT be visible with range 0->30
      await expect(
        userPage.locator('td').filter({ hasText: 'Level 40' })
      ).toHaveCount(0);
    });

    test('gear slots selector works and shows total column', async ({ userPage }) => {
      const slotSelect = userPage.locator('select').first();
      await slotSelect.selectOption('2');
      await userPage.waitForTimeout(300);

      await expect(
        userPage.locator('th').filter({ hasText: /2 slots/ }).first()
      ).toBeVisible({ timeout: 5000 });
    });
  });

  // ── Mastery Forging Calculator ─────────────────────────────────────

  test.describe('Mastery Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Mastery' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with info banner mentioning Essence Stones', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Mastery Forging/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/Essence Stones/i).first()
      ).toBeVisible();
    });

    test('shows Essence Stones and Mythic Gear resource rows', async ({ userPage }) => {
      // Default range 0 -> 20
      await expect(
        userPage.locator('td').filter({ hasText: 'Essence Stones' }).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.locator('td').filter({ hasText: 'Mythic Gear' }).first()
      ).toBeVisible();
    });

    test('narrow range below level 11 shows zero Mythic Gear', async ({ userPage }) => {
      // Mythic Gear is only required from level 11+
      const toInput = userPage.locator('input[type="number"]').nth(1);
      await toInput.fill('10');
      await userPage.waitForTimeout(300);

      // Essence Stones should still appear
      await expect(
        userPage.locator('td').filter({ hasText: 'Essence Stones' }).first()
      ).toBeVisible({ timeout: 5000 });

      // Mythic Gear cost should be 0 (displayed in the table)
      const mythicRow = userPage.locator('tr').filter({ hasText: 'Mythic Gear' });
      if (await mythicRow.count() > 0) {
        const values = await mythicRow.first().locator('td').allTextContents();
        // Second td is the "Per Slot" value — it should be "0"
        expect(values.some(v => v.trim() === '0')).toBeTruthy();
      }
    });

    test('input limits enforce 0-20 range', async ({ userPage }) => {
      const fromInput = userPage.locator('input[type="number"]').first();
      const toInput = userPage.locator('input[type="number"]').nth(1);

      // From min is 0, To max is 20
      await expect(fromInput).toHaveAttribute('min', '0');
      await expect(fromInput).toHaveAttribute('max', '19');
      await expect(toInput).toHaveAttribute('min', '1');
      await expect(toInput).toHaveAttribute('max', '20');
    });
  });

  // ── Chief Gear Calculator ──────────────────────────────────────────

  test.describe('Chief Gear Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Chief Gear' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with info banner about Chief Gear', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Chief Gear/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Mentions Attack & Defense and troop types
      await expect(
        userPage.getByText(/Attack/i).first()
      ).toBeVisible();
    });

    test('shows tier select dropdowns with color-coded options', async ({ userPage }) => {
      // Should have From Tier and To Tier selects + Gear Pieces select
      const selects = userPage.locator('select');
      const selectCount = await selects.count();
      expect(selectCount).toBeGreaterThanOrEqual(3);

      // From Tier should have all 46 tiers
      const fromSelect = selects.first();
      const options = await fromSelect.locator('option').allTextContents();
      expect(options.length).toBe(46);

      // Check for expected tier names
      expect(options.some(o => o.includes('Green'))).toBeTruthy();
      expect(options.some(o => o.includes('Blue'))).toBeTruthy();
      expect(options.some(o => o.includes('Purple'))).toBeTruthy();
      expect(options.some(o => o.includes('Gold'))).toBeTruthy();
      expect(options.some(o => o.includes('Pink'))).toBeTruthy();
    });

    test('shows stat bonus percentage display', async ({ userPage }) => {
      // Default range should show Attack + Defense Bonus
      await expect(
        userPage.getByText(/Attack \+ Defense Bonus/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should show percentage values with + sign
      await expect(
        userPage.locator('span').filter({ hasText: /\+\d+(\.\d+)?%/ }).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('shows Hardened Alloy and Polishing Solution cost rows', async ({ userPage }) => {
      await expect(
        userPage.locator('td').filter({ hasText: 'Hardened Alloy' }).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.locator('td').filter({ hasText: 'Polishing Solution' }).first()
      ).toBeVisible();
    });

    test('changing tier range to Pink shows Lunar Amber', async ({ userPage }) => {
      // Pink tiers start at index 26
      const fromSelect = userPage.locator('select').first();
      await fromSelect.selectOption('26');
      await userPage.waitForTimeout(300);

      const toSelect = userPage.locator('select').nth(1);
      await toSelect.selectOption('30');
      await userPage.waitForTimeout(300);

      // Lunar Amber only appears in Pink tiers
      await expect(
        userPage.locator('td').filter({ hasText: 'Lunar Amber' }).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('piece count selector shows total column', async ({ userPage }) => {
      const pieceSelect = userPage.locator('select').nth(2);
      await pieceSelect.selectOption('6');
      await userPage.waitForTimeout(300);

      await expect(
        userPage.locator('th').filter({ hasText: /6 pieces/ }).first()
      ).toBeVisible({ timeout: 5000 });
    });
  });

  // ── Charms Calculator ──────────────────────────────────────────────

  test.describe('Charms Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Charms' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with info banner about Lethality and Health', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Chief Charm/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/Lethality/i).first()
      ).toBeVisible();
    });

    test('shows from/to level selects with sub-level options', async ({ userPage }) => {
      // Should have From Level, To Level, and Charm Slots selects
      const selects = userPage.locator('select');
      const selectCount = await selects.count();
      expect(selectCount).toBeGreaterThanOrEqual(3);

      // From Level select should include sub-level options (e.g. "4-1", "5-0")
      const fromSelect = selects.first();
      const options = await fromSelect.locator('option').allTextContents();
      expect(options.some(o => o === '1')).toBeTruthy();
      expect(options.some(o => o === '4-1')).toBeTruthy();
      expect(options.some(o => o === '16-0')).toBeTruthy();
    });

    test('shows Charm Guides and Charm Designs resource rows', async ({ userPage }) => {
      // Set a valid range first (from defaults to 1, to defaults to 1 — need to increase to)
      const toSelect = userPage.locator('select').nth(1);
      await toSelect.selectOption('4');
      await userPage.waitForTimeout(500);

      await expect(
        userPage.locator('td').filter({ hasText: 'Charm Guides' }).first()
      ).toBeVisible({ timeout: 10_000 });

      await expect(
        userPage.locator('td').filter({ hasText: 'Charm Designs' }).first()
      ).toBeVisible();
    });

    test('shows stat bonus with Lethality + Health percentage', async ({ userPage }) => {
      // Set a valid range to trigger bonus display
      const toSelect = userPage.locator('select').nth(1);
      await toSelect.selectOption('4');
      await userPage.waitForTimeout(500);

      // Should show bonus display with percentage values
      await expect(
        userPage.locator('main span').filter({ hasText: /\+\d+\.\d+%/ }).first()
      ).toBeVisible({ timeout: 10_000 });
    });

    test('high level range shows Jewel Secrets cost row', async ({ userPage }) => {
      // Set to level to 16-0 which includes L12+ (requires Jewel Secrets)
      const toSelect = userPage.locator('select').nth(1);
      await toSelect.selectOption('16-0');
      await userPage.waitForTimeout(500);

      // Should show Jewel Secrets cost row
      await expect(
        userPage.locator('td').filter({ hasText: 'Jewel Secrets' }).first()
      ).toBeVisible({ timeout: 10_000 });
    });

    test('low level range hides Jewel Secrets', async ({ userPage }) => {
      // Set to level below 12 to avoid Jewel Secrets
      const toSelect = userPage.locator('select').nth(1);
      await toSelect.selectOption('4');
      await userPage.waitForTimeout(300);

      // Jewel Secrets warning should NOT be visible
      await expect(
        userPage.getByText(/Jewel Secrets required/i)
      ).not.toBeVisible();
    });

    test('slot selector includes multi-piece options', async ({ userPage }) => {
      const slotSelect = userPage.locator('select').nth(2);
      const options = await slotSelect.locator('option').allTextContents();

      expect(options).toContain('1 slot');
      expect(options).toContain('3 slots (1 piece)');
      expect(options).toContain('18 slots (all 6 pieces)');
    });
  });

  // ── War Academy Calculator ─────────────────────────────────────────

  test.describe('War Academy Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'War Academy' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with info banner about War Academy and Helios', async ({ userPage }) => {
      await expect(
        userPage.getByText(/War Academy/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should mention Furnace 30 unlock
      await expect(
        userPage.getByText(/Furnace 30/i).first()
      ).toBeVisible();

      // Should mention T11 / Helios troops
      await expect(
        userPage.getByText(/Helios/i).first()
      ).toBeVisible();
    });

    test('shows FC level selects with FC1-0 through FC10-0 options', async ({ userPage }) => {
      const selects = userPage.locator('select');
      const selectCount = await selects.count();
      expect(selectCount).toBeGreaterThanOrEqual(2);

      // To Level select should include FC10-0
      const toSelect = selects.nth(1);
      const options = await toSelect.locator('option').allTextContents();
      expect(options.some(o => o === 'FC10-0')).toBeTruthy();
      expect(options.some(o => o === 'FC1-1')).toBeTruthy();
    });

    test('shows resource cost table with Fire Crystal Shards and basic resources', async ({ userPage }) => {
      await expect(
        userPage.locator('td').filter({ hasText: 'Fire Crystal Shards' }).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.locator('td').filter({ hasText: 'Meat' }).first()
      ).toBeVisible();

      await expect(
        userPage.locator('td').filter({ hasText: 'Wood' }).first()
      ).toBeVisible();

      await expect(
        userPage.locator('td').filter({ hasText: 'Coal' }).first()
      ).toBeVisible();

      await expect(
        userPage.locator('td').filter({ hasText: 'Iron' }).first()
      ).toBeVisible();
    });

    test('shows summary cards: Furnace Required, Build Time, Power Gain', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Furnace Required/i).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.getByText(/Base Build Time/i).first()
      ).toBeVisible();

      await expect(
        userPage.getByText(/Power Gain/i).first()
      ).toBeVisible();
    });

    test('shows FC Milestones breakdown', async ({ userPage }) => {
      // Default is FC1-0 -> FC10-0, should show multiple milestone boundaries
      await expect(
        userPage.getByText(/FC Milestones/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should show individual FC boundaries as spans (milestone cards, not table rows)
      await expect(
        userPage.locator('span').filter({ hasText: 'FC2-0' }).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.locator('span').filter({ hasText: 'FC5-0' }).first()
      ).toBeVisible();
    });

    test('higher FC range shows Refined Fire Crystals', async ({ userPage }) => {
      // Set from FC5-0 (index 20) to FC10-0 (index 45) to include Refined FCs
      const fromSelect = userPage.locator('select').first();
      await fromSelect.selectOption('20');
      await userPage.waitForTimeout(300);

      await expect(
        userPage.locator('td').filter({ hasText: 'Refined Fire Crystals' }).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('changing level range updates cost values', async ({ userPage }) => {
      const initialContent = await userPage.locator('main').textContent();

      // Change from FC1-0 (0) to FC3-0 (10)
      const toSelect = userPage.locator('select').nth(1);
      await toSelect.selectOption('10');
      await userPage.waitForTimeout(300);

      const updatedContent = await userPage.locator('main').textContent();
      expect(updatedContent).not.toBe(initialContent);
    });
  });

  // ── Pet Leveling Calculator ────────────────────────────────────────

  test.describe('Pet Leveling Calculator', () => {
    test.beforeEach(async ({ userPage }) => {
      await userPage.getByRole('button', { name: 'Pet Leveling' }).click();
      await userPage.waitForTimeout(500);
    });

    test('loads with info banner about Pet Leveling', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Pet Leveling/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Should mention same rarity sharing costs
      await expect(
        userPage.getByText(/same rarity/i).first()
      ).toBeVisible();
    });

    test('shows rarity selector with all 5 options', async ({ userPage }) => {
      const raritySelect = userPage.locator('select').first();
      await expect(raritySelect).toBeVisible();

      const options = await raritySelect.locator('option').allTextContents();
      expect(options.length).toBe(5);
      expect(options.some(o => o.includes('Common'))).toBeTruthy();
      expect(options.some(o => o.includes('SSR'))).toBeTruthy();
      expect(options.some(o => o.includes('SR'))).toBeTruthy();
    });

    test('default SSR shows Pet Food and Taming Manuals', async ({ userPage }) => {
      // Default is SSR from 1 to 100
      await expect(
        userPage.locator('td').filter({ hasText: 'Pet Food' }).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.locator('td').filter({ hasText: 'Taming Manuals' }).first()
      ).toBeVisible();
    });

    test('SSR full range shows all advancement materials', async ({ userPage }) => {
      // SSR 1->100 includes milestones requiring all three materials
      await expect(
        userPage.locator('td').filter({ hasText: 'Energizing Potions' }).first()
      ).toBeVisible({ timeout: 5000 });

      await expect(
        userPage.locator('td').filter({ hasText: 'Strengthening Serums' }).first()
      ).toBeVisible();
    });

    test('shows advancement milestones section', async ({ userPage }) => {
      await expect(
        userPage.getByText(/Advancement Milestones/i).first()
      ).toBeVisible({ timeout: 5000 });

      // SSR has milestones at 10, 20, ..., 100
      await expect(
        userPage.getByText('Level 10').first()
      ).toBeVisible();

      await expect(
        userPage.getByText('Level 50').first()
      ).toBeVisible();
    });

    test('switching rarity to Common limits max level', async ({ userPage }) => {
      const raritySelect = userPage.locator('select').first();
      await raritySelect.selectOption('Common');
      await userPage.waitForTimeout(500);

      // Common max is 50; To Level input should have max=50
      const toInput = userPage.locator('input[type="number"]').nth(1);
      await expect(toInput).toHaveAttribute('max', '50');

      // Should show pet names for Common
      await expect(
        userPage.getByText(/Cave Hyena/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('switching rarity shows associated pet names', async ({ userPage }) => {
      // Default is SSR — should show SSR pet names
      await expect(
        userPage.getByText(/Cave Lion/i).first()
      ).toBeVisible({ timeout: 5000 });

      // Switch to R
      const raritySelect = userPage.locator('select').first();
      await raritySelect.selectOption('R');
      await userPage.waitForTimeout(500);

      await expect(
        userPage.getByText(/Giant Tapir/i).first()
      ).toBeVisible({ timeout: 5000 });
    });

    test('narrow range below milestone 10 hides advancement materials', async ({ userPage }) => {
      // Set from=1, to=9 (below first milestone at 10)
      const toInput = userPage.locator('input[type="number"]').nth(1);
      await toInput.fill('9');
      await userPage.waitForTimeout(300);

      // Pet Food should still be visible
      await expect(
        userPage.locator('td').filter({ hasText: 'Pet Food' }).first()
      ).toBeVisible({ timeout: 5000 });

      // Taming Manuals should NOT be visible (no milestones in range)
      await expect(
        userPage.locator('td').filter({ hasText: 'Taming Manuals' })
      ).not.toBeVisible();
    });
  });
});
