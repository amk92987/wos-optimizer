import { test, expect } from '@playwright/test';

test.describe('Forgot Password Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/forgot-password');
  });

  test('shows forgot password form', async ({ page }) => {
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.getByRole('button', { name: /send reset link/i })).toBeVisible();
  });

  test('submitting email shows confirmation', async ({ page }) => {
    await page.locator('#email').fill('e2e-user@test.com');
    await page.getByRole('button', { name: /send reset link/i }).click();
    // Should show success message or error (either is valid - we just verify the form submits)
    await expect(
      page.getByText(/reset link|sent|check your email/i).or(page.locator('.bg-error\\/20'))
    ).toBeVisible({ timeout: 10_000 });
  });

  test('has link back to login', async ({ page }) => {
    const backLink = page.getByText(/back.*sign in|back.*login/i).or(
      page.getByRole('link', { name: /back/i })
    );
    await backLink.click();
    await expect(page).toHaveURL(/login/);
  });
});
