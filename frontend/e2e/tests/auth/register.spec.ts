import { test, expect } from '@playwright/test';

test.describe('Register Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('shows registration form with email and password fields', async ({ page }) => {
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#confirmPassword')).toBeVisible();
    await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
  });

  test('shows error for password mismatch', async ({ page }) => {
    await page.locator('#email').fill('test-mismatch@example.com');
    await page.locator('#password').fill('Password123!');
    await page.locator('#confirmPassword').fill('DifferentPassword!');
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page.getByText(/match/i)).toBeVisible();
  });

  test('shows error for short password', async ({ page }) => {
    await page.locator('#email').fill('test-short@example.com');
    await page.locator('#password').fill('abc');
    await page.locator('#confirmPassword').fill('abc');
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page.getByText(/6 characters/i)).toBeVisible();
  });

  test('has link back to login page', async ({ page }) => {
    await page.getByText(/sign in/i).click();
    await expect(page).toHaveURL(/login/);
  });
});
