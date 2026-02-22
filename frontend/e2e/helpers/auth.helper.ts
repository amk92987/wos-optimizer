import { Page } from '@playwright/test';

export interface AuthTokens {
  id_token: string;
  access_token: string;
  refresh_token?: string;
  user: {
    id: string;
    email: string;
    username: string;
    role: string;
    is_active: boolean;
    is_test_account: boolean;
  };
}

export async function loginViaApi(
  baseUrl: string,
  email: string,
  password: string
): Promise<AuthTokens> {
  const res = await fetch(`${baseUrl}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Login failed (${res.status}): ${body}`);
  }
  return res.json();
}

export async function injectTokens(page: Page, tokens: AuthTokens) {
  await page.evaluate((t) => {
    localStorage.setItem('id_token', t.id_token);
    localStorage.setItem('access_token', t.access_token);
    if (t.refresh_token) {
      localStorage.setItem('refresh_token', t.refresh_token);
    }
    localStorage.setItem('token', t.id_token);
  }, tokens);
}

export async function clearAllTokens(page: Page) {
  await page.evaluate(() => {
    localStorage.removeItem('id_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token');
    localStorage.removeItem('impersonating');
    localStorage.removeItem('impersonate_user_id');
    localStorage.removeItem('impersonate_user');
    localStorage.removeItem('admin_user');
  });
}
