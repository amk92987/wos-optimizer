import { test, expect } from '../../fixtures/auth.fixture';

test.describe('Logout', () => {
  test('logout clears tokens and redirects', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');
    await userPage.waitForTimeout(1000);

    // Open user menu dropdown in the header
    const userMenu = userPage.getByRole('button', { name: /e2e-user/i });
    await expect(userMenu).toBeVisible({ timeout: 10_000 });
    await userMenu.click();
    await userPage.waitForTimeout(500);

    // Click Sign Out from the dropdown (use force since it may be positioned off viewport)
    const signOut = userPage.getByText('Sign Out');
    await signOut.click({ force: true });

    // Should redirect to login
    await userPage.waitForURL(/login|landing/, { timeout: 10_000 });

    // Tokens should be cleared
    const token = await userPage.evaluate(() => localStorage.getItem('id_token'));
    expect(token).toBeNull();
  });

  test('protected pages redirect to login after logout', async ({ userPage }) => {
    // Clear tokens manually to simulate logged-out state
    await userPage.evaluate(() => {
      localStorage.removeItem('id_token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token');
    });

    await userPage.goto('/heroes');
    // Should redirect to landing or login
    await userPage.waitForURL(/login|landing/, { timeout: 10_000 });
  });
});
