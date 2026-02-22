import { defineConfig, devices } from '@playwright/test';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config({ path: path.resolve(__dirname, '.env.test') });

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: true,
  retries: 1,
  workers: 2,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
  ],

  globalSetup: require.resolve('./global-setup'),

  use: {
    baseURL: 'https://wosdev.randomchaoslabs.com',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    locale: 'en-US',
    timezoneId: 'America/New_York',
  },

  outputDir: 'test-results',

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      testMatch: /mobile-nav\.spec\.ts/,
    },
  ],

  timeout: 60_000,
  expect: {
    timeout: 5_000,
  },
});
