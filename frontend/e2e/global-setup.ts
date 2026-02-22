import { loginViaApi } from './helpers/auth.helper';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config({ path: path.resolve(__dirname, '.env.test') });

async function globalSetup() {
  const authDir = path.resolve(__dirname, '.auth');
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  const baseUrl = 'https://wosdev.randomchaoslabs.com';

  // Login as regular user
  console.log('[Setup] Logging in as test user...');
  const userTokens = await loginViaApi(
    baseUrl,
    process.env.E2E_USER_EMAIL!,
    process.env.E2E_USER_PASSWORD!
  );
  fs.writeFileSync(
    path.join(authDir, 'user.json'),
    JSON.stringify(userTokens, null, 2)
  );
  console.log('[Setup] User tokens saved.');

  // Login as admin
  console.log('[Setup] Logging in as test admin...');
  const adminTokens = await loginViaApi(
    baseUrl,
    process.env.E2E_ADMIN_EMAIL!,
    process.env.E2E_ADMIN_PASSWORD!
  );
  fs.writeFileSync(
    path.join(authDir, 'admin.json'),
    JSON.stringify(adminTokens, null, 2)
  );
  console.log('[Setup] Admin tokens saved.');
}

export default globalSetup;
