import { Page } from '@playwright/test';

export class SidebarComponent {
  constructor(private page: Page) {}

  get sidebar() {
    return this.page.locator('aside').first();
  }

  navLink(text: string) {
    return this.sidebar.getByText(text, { exact: false });
  }

  get userMenuButton() {
    return this.page.locator('[class*="user-menu"], [class*="UserMenu"]').first();
  }

  get signOutButton() {
    return this.page.getByText('Sign Out');
  }

  // Navigation groups
  get overviewGroup() {
    return this.sidebar.getByText('Overview');
  }
  get trackerGroup() {
    return this.sidebar.getByText('Tracker');
  }
  get analyticsGroup() {
    return this.sidebar.getByText('Analytics');
  }
  get guidesGroup() {
    return this.sidebar.getByText('Guides');
  }

  // Mobile bottom nav
  get bottomNav() {
    return this.page.locator('.mobile-nav, nav[class*="bottom"], nav.fixed.bottom-0');
  }
}
