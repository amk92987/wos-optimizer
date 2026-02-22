import { test, expect } from '@playwright/test';
import { LoginPage } from '../../page-objects/login.page';

test.describe('Login Page', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('shows login form with email and password fields', async ({ page }) => {
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.submitButton).toBeVisible();
  });

  test('successful login redirects to home', async ({ page }) => {
    await loginPage.login(
      process.env.E2E_USER_EMAIL || 'e2e-user@test.com',
      process.env.E2E_USER_PASSWORD || 'TestPassword123!'
    );
    await page.waitForURL('/', { timeout: 10_000 });
    await expect(page).toHaveURL('/');
  });

  test('invalid credentials show error message', async ({ page }) => {
    await loginPage.login('e2e-user@test.com', 'WrongPassword123!');
    await expect(loginPage.errorMessage).toBeVisible({ timeout: 10_000 });
  });

  test('navigates to forgot password page', async ({ page }) => {
    await loginPage.forgotPasswordLink.click();
    await expect(page).toHaveURL(/forgot-password/);
  });

  test('navigates to register page', async ({ page }) => {
    await loginPage.registerLink.click();
    await expect(page).toHaveURL(/register/);
  });
});
