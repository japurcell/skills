import assert from 'node:assert/strict';
import test from 'node:test';
import { join } from 'node:path';
import { chromium } from '@playwright/test';
import { createRepository } from '../fixtures/repository.mjs';
import { initializeRepositoryStore } from '../../dist/store.js';
import { startObservationHost } from '../../dist/dashboard.js';

for (const [result, expected] of [
  ['submitted', 'Latest reminder submitted to the notification service. Desktop visibility is unverified.'],
  ['unknown', 'Latest reminder submission or cleanup is unknown. The host retains its claim.'],
]) {
  test(`an open dashboard shows a newly recorded ${result} reminder without moving the reader`, async () => {
    const repo = createRepository();
    const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
    let host, browser, tick;
    try {
      const run = await store.createRun();
      const worktree = await store.registerWorktree({ path: repo.path, registration: 'fixture' });
      const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
      await store.activateInvocation(invocation.id);
      await store.finalizeInvocation({ id: invocation.id, outcome: 'failed', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
      const scheduler = { setTimeout(callback) { tick = callback; return 1; }, clearTimeout() { tick = undefined; } };
      const sender = result === 'submitted' ? async () => ({ state: 'submitted', cleanup: 'complete' }) : async () => { throw new Error('submission uncertain'); };
      host = await startObservationHost({ store, reminderScheduler: scheduler, reminderSender: sender });
      browser = await chromium.launch({ headless: true });
      const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
      await page.goto(host.createUiHandoff());
      await page.getByRole('heading', { name: 'Repository runs' }).waitFor();
      await page.waitForFunction(() => document.getElementById('connection')?.textContent?.startsWith('Connected'));
      await page.getByText('Notification preferences', { exact: true }).click();
      await page.getByText('No reminder group saved yet.').waitFor();
      await page.getByRole('checkbox', { name: 'Reminders' }).check();
      await page.getByRole('button', { name: 'Save notification preferences' }).click();
      await page.getByText('Notification preferences saved.').waitFor();
      const selected = await page.evaluate(() => {
        const paragraph = document.querySelector('.notification-form').previousElementSibling;
        const range = document.createRange(); range.selectNodeContents(paragraph);
        const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
        return { text: selection.toString(), scroll: window.scrollY };
      });
      assert.ok(tick);
      await tick();
      assert.equal(store.readReminderGroups().groups[0].state, result);
      await page.getByText(expected, { exact: true }).waitFor({ timeout: 3000 });
      assert.deepEqual(await page.evaluate(() => ({ text: window.getSelection().toString(), scroll: window.scrollY })), selected);
      assert.equal(await page.locator('details:has-text("Notification preferences")').first().evaluate(element => element.open), true);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      if (process.env.FACTORY_SCREENSHOT_DIR) await page.screenshot({ path: join(process.env.FACTORY_SCREENSHOT_DIR, `reminder-${result}-390.png`), fullPage: true });
    } finally {
      await browser?.close();
      if (host) {
        if (result === 'unknown') await assert.rejects(host.close(), /reminder cleanup or recording unknown/);
        else await host.close();
      }
      store.close(); repo.dispose();
    }
  });
}
