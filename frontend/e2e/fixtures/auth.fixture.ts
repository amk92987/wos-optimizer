import { test as base, Page } from '@playwright/test';
import { injectTokens, AuthTokens } from '../helpers/auth.helper';
import fs from 'fs';
import path from 'path';

type AuthFixtures = {
  userPage: Page;
  adminPage: Page;
  userTokens: AuthTokens;
  adminTokens: AuthTokens;
};

function loadTokens(role: 'user' | 'admin'): AuthTokens {
  const filePath = path.resolve(__dirname, '..', '.auth', `${role}.json`);
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

export const test = base.extend<AuthFixtures>({
  userTokens: async ({}, use) => {
    await use(loadTokens('user'));
  },

  adminTokens: async ({}, use) => {
    await use(loadTokens('admin'));
  },

  userPage: async ({ browser, userTokens }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    // Navigate to set the origin, then inject tokens
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await injectTokens(page, userTokens);

    await use(page);
    await context.close();
  },

  adminPage: async ({ browser, adminTokens }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    // Navigate to set the origin, then inject tokens
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await injectTokens(page, adminTokens);

    await use(page);
    await context.close();
  },
});

export { expect } from '@playwright/test';
