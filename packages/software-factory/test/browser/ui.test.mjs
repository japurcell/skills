import assert from 'node:assert/strict';
import test from 'node:test';
import { chromium } from '@playwright/test';
import { join } from 'node:path';
import { createRepository } from '../fixtures/repository.mjs';
import { initializeRepositoryStore } from '../../dist/store.js';
import { startObservationHost } from '../../dist/dashboard.js';
import { InvocationRecorder } from '../../dist/capture.js';
import { DatabaseSync } from 'node:sqlite';

async function fixture() {
  const repo = createRepository();
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  const run = await store.createRun();
  const worktree = await store.registerWorktree({ path: repo.path, registration: 'fixture' });
  const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
  await store.activateInvocation(invocation.id);
  const host = await startObservationHost({ store });
  return { repo, store, run, invocation, host, dispose: async () => { await host.close(); store.close(); repo.dispose(); } };
}

test('owner link opens grouped run card and saved invocation without exposing bearer in URL', async () => {
  const f = await fixture(); const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 850 } });
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('heading', { name: 'Repository runs' }).waitFor();
    assert.ok(!page.url().includes('handoff'));
    assert.ok(!page.url().includes(f.host.sessionToken));
    await page.getByRole('link', { name: new RegExp(f.run.id.slice(0, 8)) }).click();
    await page.getByRole('heading', { name: 'Invocation timeline' }).waitFor();
    await page.getByText('Running', { exact: true }).first().waitFor();
  } finally { await browser.close(); await f.dispose(); }
});

test('real recorder output is available as inert text and saved events arrive while following', async () => {
  const f = await fixture(); const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  try {
    const recorder = new InvocationRecorder({ store: f.store, invocationId: f.invocation.id, requestShutdown: () => {} });
    const capture = await recorder.openCapture({ channel: 'stdout' });
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('heading', { name: 'Repository runs' }).waitFor();
    await page.getByRole('link', { name: new RegExp(f.run.id.slice(0, 8)) }).click();
    await page.getByRole('heading', { name: 'Invocation timeline' }).waitFor();
    await capture.write('<script>alert("unsafe")</script> saved output'); await recorder.barrier();
    await page.getByText('capture.appended', { exact: false }).first().waitFor({ timeout: 3000 });
    await page.getByText('Saved outputs and traces', { exact: true }).click();
    await page.getByRole('button', { name: /stdout/i }).click();
    await page.getByText('<script>alert("unsafe")</script> saved output', { exact: false }).waitFor();
    assert.equal(await page.locator('script').count(), 1);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  } finally { await browser.close(); await f.dispose(); }
});

test('keyboard skip link, frozen view, invalid link and narrow zoom remain usable', async () => {
  const f = await fixture(); const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('heading', { name: 'Repository runs' }).waitFor();
    if (process.env.FACTORY_SCREENSHOT_DIR) await page.screenshot({ path: join(process.env.FACTORY_SCREENSHOT_DIR, 'index-390.png'), fullPage: true });
    await page.evaluate(() => { document.documentElement.style.zoom = '2'; });
    const dimensions = await page.evaluate(() => ({ viewport:innerWidth, document:document.documentElement.scrollWidth,
      offenders:[...document.querySelectorAll('body *')].filter(element => element.getBoundingClientRect().right > innerWidth + 1).slice(0,8).map(element=>({tag:element.tagName,className:element.className,right:Math.round(element.getBoundingClientRect().right)})) }));
    assert.ok(dimensions.document <= dimensions.viewport, JSON.stringify(dimensions));
    if (process.env.FACTORY_SCREENSHOT_DIR) await page.screenshot({ path: join(process.env.FACTORY_SCREENSHOT_DIR, 'index-200-percent.png'), fullPage: true });
    await page.evaluate(() => { document.documentElement.style.zoom = '1'; });
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement?.textContent?.trim()), 'Skip to content');
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => document.activeElement?.id), 'app');
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.getByRole('link', { name: new RegExp(f.run.id.slice(0, 8)) }).click();
    await page.getByRole('heading', { name: 'Invocation timeline' }).waitFor();
    if (process.env.FACTORY_SCREENSHOT_DIR) await page.screenshot({ path: join(process.env.FACTORY_SCREENSHOT_DIR, 'run-390.png'), fullPage: true });
    await page.evaluate(() => { document.documentElement.style.zoom = '2'; });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    if (process.env.FACTORY_SCREENSHOT_DIR) await page.screenshot({ path: join(process.env.FACTORY_SCREENSHOT_DIR, 'run-200-percent.png'), fullPage: true });
    await page.evaluate(() => { document.documentElement.style.zoom = '1'; });
    await page.getByRole('button', { name: 'Freeze this view' }).click();
    const recorder = new InvocationRecorder({ store: f.store, invocationId: f.invocation.id, requestShutdown: () => {} });
    const capture = await recorder.openCapture({ channel: 'stdout' });
    await capture.write('arrived while frozen'); await recorder.barrier();
    await page.getByRole('button', { name: 'Follow latest events' }).waitFor();
    assert.equal(await page.getByText('capture.appended', { exact: false }).count(), 0);
    await page.getByRole('button', { name: 'Follow latest events' }).click();
    await page.getByText('capture.appended', { exact: false }).first().waitFor();
    await page.evaluate(() => { location.hash = 'run=00000000-0000-0000-0000-000000000000'; });
    await page.getByRole('heading', { name: 'History unavailable' }).waitFor();
    assert.ok(!page.url().includes(f.run.id));
  } finally { await browser.close(); await f.dispose(); }
});

test('saved event gap is disclosed and a disconnected tab retains its last display', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:860,height:650}});let database;
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    const search=page.getByRole('searchbox',{name:'Find on this page'});
    await search.fill(f.run.id.slice(0,8));await search.focus();
    const head=f.store.readEventHead().cursor;
    database=new DatabaseSync(join(f.repo.path,'.git','factory','history.sqlite'));
    database.prepare('DELETE FROM observation_events WHERE cursor=?').run(BigInt(head));
    await page.getByText(/saved event gap was detected/i).waitFor({timeout:4000});
    assert.equal(await search.inputValue(),f.run.id.slice(0,8));
    assert.equal(await search.evaluate(element=>element===document.activeElement),true);
    await f.host.close();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Disconnected - last update'),null,{timeout:4000});
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    assert.equal(await page.locator('.run-card').count(),1);
  } finally {database?.close();await browser.close();await f.dispose();}
});
