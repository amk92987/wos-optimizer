import { Locator, Page } from '@playwright/test';

/**
 * Wait for the auto-save cycle to complete.
 * The app debounces 300ms then sends an API call.
 * SaveIndicator shows "Saving..." then "Saved".
 */
export async function waitForAutoSave(card: Locator) {
  // Wait for "Saving" to appear (debounce fired)
  try {
    await card.getByText('Saving').waitFor({ state: 'visible', timeout: 2000 });
  } catch {
    // May have already transitioned to "Saved"
  }
  // Wait for "Saved" to confirm the API call completed
  await card.getByText('Saved').waitFor({ state: 'visible', timeout: 5000 });
}

/**
 * Wait for a hero PUT API response.
 */
export async function waitForHeroUpdate(page: Page) {
  await page.waitForResponse(
    (resp) =>
      resp.url().includes('/api/heroes/') &&
      resp.request().method() === 'PUT' &&
      resp.ok(),
    { timeout: 10_000 }
  );
}

/**
 * Wait for any API response matching a pattern.
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string,
  method = 'GET'
) {
  await page.waitForResponse(
    (resp) =>
      resp.url().includes(urlPattern) &&
      resp.request().method() === method &&
      resp.ok(),
    { timeout: 10_000 }
  );
}

/**
 * Wait for the page to finish loading (spinner gone, content visible).
 */
export async function waitForPageLoad(page: Page) {
  // Wait for any loading spinner to disappear
  const spinner = page.locator('.animate-spin');
  if (await spinner.isVisible().catch(() => false)) {
    await spinner.waitFor({ state: 'hidden', timeout: 15_000 });
  }
}
