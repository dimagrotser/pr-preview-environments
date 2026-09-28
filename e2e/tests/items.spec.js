import { expect, test } from '@playwright/test';

test('the list is rendered from the API', async ({ page, request }) => {
  const expected = (await (await request.get('/api/items')).json()).items;

  await page.goto('/');

  const items = page.getByTestId('items').locator('li');
  await expect(items).toHaveCount(expected.length);
  await expect(items.first()).toHaveText(expected[0].name);
  await expect(page.getByTestId('error')).toBeHidden();
});
