import { expect, test } from '@playwright/test';
import { commit, pr } from './env.js';

test('the page belongs to this pull request', async ({ page }) => {
  await page.goto('/');

  const banner = page.getByTestId('banner');
  await expect(banner).toHaveAttribute('data-pr', pr);
  await expect(banner).toHaveAttribute('data-commit', commit);
  await expect(banner).toContainText(`PR #${pr}`);
});
