import { Page } from '@playwright/test';

export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  get emailInput() {
    return this.page.locator('#email');
  }
  get passwordInput() {
    return this.page.locator('#password');
  }
  get submitButton() {
    return this.page.getByRole('button', { name: /sign in/i });
  }
  get errorMessage() {
    return this.page.locator('.bg-error\\/20');
  }
  get forgotPasswordLink() {
    return this.page.getByText('Forgot your password?');
  }
  get registerLink() {
    return this.page.getByText('Create one');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
