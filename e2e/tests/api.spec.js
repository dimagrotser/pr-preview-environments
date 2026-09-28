import { expect, test } from '@playwright/test';
import { commit, pr } from './env.js';

test('health endpoint answers through the ingress', async ({ request }) => {
  const res = await request.get('/api/healthz');
  expect(res.status()).toBe(200);
  expect(await res.json()).toEqual({ status: 'ok' });
});

test('version endpoint reports the deployed build', async ({ request }) => {
  const res = await request.get('/api/version');
  expect(res.ok()).toBeTruthy();
  expect(await res.json()).toMatchObject({ pr, commit });
});
