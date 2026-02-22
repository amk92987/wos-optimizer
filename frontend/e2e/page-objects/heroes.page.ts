import { Page, Locator } from '@playwright/test';

export class HeroesPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/heroes');
    await this.waitForLoad();
  }

  // Tabs
  get ownedTab() {
    return this.page.getByRole('button', { name: /owned/i });
  }
  get allTab() {
    return this.page.getByRole('button', { name: 'All Heroes', exact: true });
  }

  // Filters
  get searchInput() {
    return this.page.getByPlaceholder(/search/i);
  }

  // Hero cards
  heroCard(name: string): Locator {
    return this.page.locator('.group').filter({ hasText: new RegExp(`^\\s*${name}`, 'i') });
  }

  heroCards(): Locator {
    return this.page.locator('.group');
  }

  // Add hero button (on All Heroes tab)
  addButton(name: string) {
    return this.page
      .locator('.group')
      .filter({ hasText: name })
      .getByRole('button', { name: /add/i });
  }

  async waitForLoad() {
    // Wait for either hero cards to appear or empty state
    await this.page.waitForResponse(
      (resp) => resp.url().includes('/api/heroes/') && resp.ok(),
      { timeout: 15_000 }
    ).catch(() => {});
    // Give React time to render
    await this.page.waitForTimeout(500);
  }
}
