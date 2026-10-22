import assert from 'node:assert/strict';
import test from 'node:test';
import { chromium } from '@playwright/test';
import { join } from 'node:path';
import { createRepository } from '../fixtures/repository.mjs';
import { initializeRepositoryStore } from '../../dist/store.js';
import { startObservationHost } from '../../dist/dashboard.js';
import { InvocationRecorder } from '../../dist/capture.js';
import { DatabaseSync } from 'node:sqlite';
import { randomUUID } from 'node:crypto';

async function fixture() {
  const repo = createRepository();
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  const run = await store.createRun();
  const worktree = await store.registerWorktree({ path: repo.path, registration: 'fixture' });
  const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
  await store.activateInvocation(invocation.id);
  const host = await startObservationHost({ store });
  return { repo, store, run, worktree, invocation, host, dispose: async () => { await host.close(); store.close(); repo.dispose(); } };
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
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    assert.equal(await page.locator('#connection').getAttribute('aria-live'),null);
    const beforeAnnouncement=await page.locator('#announcement').innerText();
    await capture.write('<script>alert("unsafe")</script> saved output'); await recorder.barrier();
    await page.getByText('capture.appended', { exact: false }).first().waitFor({ timeout: 3000 });
    assert.equal(await page.locator('#announcement').innerText(),beforeAnnouncement);
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

test('populated index updates a saved question and uncertain cleanup in place', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:1280,height:850}});
  try {
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    const search=page.getByRole('searchbox',{name:'Find on this page'});
    await search.fill(f.run.id.slice(0,8));await search.focus();
    const original=await page.locator('.run-card').evaluate(element=>{window.savedCard=element;return element.textContent});
    assert.match(original,/Running/);
    const question=await recorder.openCapture({channel:'request'});
    await question.write(JSON.stringify({question:'Which release channel?',context:'The saved workflow needs a channel before continuing.',suggestions:['stable','preview']}));
    await question.finish();await recorder.barrier();
    await f.store.finishInvocation(f.invocation.id,'needs_input','unknown');
    await page.waitForFunction(()=>document.querySelector('.run-card')?.textContent?.includes('Manual cleanup required'));
    assert.equal(await page.locator('.run-card').evaluate(element=>element===window.savedCard),true);
    assert.equal(await search.evaluate(element=>element===document.activeElement),true);
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByText('Which release channel?',{exact:true}).first().waitFor();
    assert.match(await page.locator('#attention-slot').innerText(),/stable; preview/);
    assert.match(await page.locator('#attention-slot').innerText(),new RegExp(question.id));
    assert.equal(await page.getByText('Question and next input').locator('..').getAttribute('open'),'');
  } finally {await browser.close();await f.dispose();}
});

test('reading old output pauses its scroll while selected outcome and cleanup stay current', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:860,height:650}});
  try {
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    const output=await recorder.openCapture({channel:'stdout'});
    for(let i=0;i<30;i++){await output.write(`line ${i}\n`);await recorder.barrier();}
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    const list=page.locator('#event-list');
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    assert.ok(await list.evaluate(element=>element.scrollHeight>element.clientHeight));
    await list.evaluate(element=>{element.scrollTop=0});
    await f.store.finishInvocation(f.invocation.id,'needs_input','unknown');
    await page.waitForFunction(()=>document.querySelector('#execution-state')?.textContent?.includes('needs input'));
    assert.match(await page.locator('#cleanup-state').innerText(),/Manual cleanup required/);
    assert.match(await page.locator('#pending-events').innerText(),/new events/);
    assert.equal(await list.evaluate(element=>element.scrollTop),0);
    assert.equal(await page.getByText('invocation.finalized',{exact:false}).count(),0);
    await page.getByRole('button',{name:/return to latest/i}).click();
    await page.getByText('invocation.finalized',{exact:false}).waitFor();
  } finally {await browser.close();await f.dispose();}
});

test('saved question is visible before finalization and a failed explanation opens initially', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:860,height:650}});
  try {
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    const question=await recorder.openCapture({channel:'request'});
    await question.write(JSON.stringify({question:'Which environment?',context:'Deployment target was omitted.'}));await question.finish();await recorder.barrier();
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByText('Which environment?',{exact:true}).waitFor();
    assert.match(await page.locator('#attention-slot').innerText(),/No final result has been saved yet/);
    await f.store.finishInvocation(f.invocation.id,'failed','complete');
    await page.waitForFunction(()=>document.querySelector('#execution-state')?.textContent?.includes('Failed'));
    assert.equal(await page.getByText('Failure explanation').locator('..').getAttribute('open'),'');
  } finally {await browser.close();await f.dispose();}
});

test('nested native identities, instant timing, and Back reading position survive navigation', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:860,height:650}});
  try {
    const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'review',kind:'agent',intent:'initial'});
    const parent=await f.store.saveSession(attempt.id,{nativeId:'parent-native',parentNativeId:null,lifecycle:'running',usage:{tokens:100,scope:'includes-children'}});
    const child=await f.store.saveSession(attempt.id,{nativeId:'child-native',parentNativeId:'parent-native',lifecycle:'running'});
    const grandchild=await f.store.saveSession(attempt.id,{nativeId:'grandchild-native',parentNativeId:'child-native',lifecycle:'running'});
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    assert.ok(await page.locator('.phase-bar[data-instant="true"]').count()>0);
    await page.locator(`[data-action="collapse"][data-id="${parent.id}"]`).click();
    assert.equal(await page.locator(`[data-session="${child.id}"]`).first().isVisible(),false);
    assert.equal(await page.locator(`[data-session="${grandchild.id}"]`).first().isVisible(),false);
    await page.locator(`[data-action="collapse"][data-id="${parent.id}"]`).click();
    await page.locator(`a[href*="session=${child.id}"]`).first().click();
    await page.getByRole('heading',{name:'Native session child-native'}).waitFor();
    assert.match(await page.getByText('Native session evidence').locator('..').innerText(),/child-native/);
    await page.goBack();
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    await page.waitForFunction(id=>document.activeElement?.getAttribute('href')?.includes(id),child.id);
    await page.goForward();
    await page.getByRole('heading',{name:'Native session child-native'}).waitFor();
    await page.goBack();
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    await page.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));
    await page.waitForTimeout(100);
    const before=await page.evaluate(()=>window.scrollY);
    await page.getByRole('link',{name:'Repository runs',exact:true}).click();
    await page.goBack();
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    assert.equal(await page.evaluate(()=>window.scrollY),before);
    await page.goForward();
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
  } finally {await browser.close();await f.dispose();}
});

test('a collapsed ancestor continues hiding descendants on later session pages', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:860,height:650}});
  try {
    const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'review',kind:'agent',intent:'initial'});
    const parent=await f.store.saveSession(attempt.id,{nativeId:'parent-native',parentNativeId:null,lifecycle:'running'});
    await f.store.saveSession(attempt.id,{nativeId:'child-native',parentNativeId:'parent-native',lifecycle:'running'});
    for(let index=0;index<48;index++)await f.store.saveSession(attempt.id,{nativeId:`other-${index}`,parentNativeId:null,lifecycle:'running'});
    const grandchild=await f.store.saveSession(attempt.id,{nativeId:'grandchild-native',parentNativeId:'child-native',lifecycle:'running'});
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.locator(`[data-action="collapse"][data-id="${parent.id}"]`).click();
    await page.getByRole('button',{name:'Next sessions'}).click();
    const descendant=page.locator(`.timeline-lane[data-session="${grandchild.id}"]`);
    await descendant.waitFor({state:'attached'});
    assert.equal(await descendant.count(),1);
    assert.equal(await descendant.isVisible(),false);
  } finally {await browser.close();await f.dispose();}
});

test('late phase and exact event cursor open bounded saved targets with invalid tuple diagnostics', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:1280,height:850}});
  try {
    let late;
    for(let i=0;i<55;i++) {
      const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:`phase-${i}`,kind:'command',intent:'initial'});
      await f.store.settleAttempt({id:attempt.id,launch:'not_started',outcome:'interrupted',quiescent:true,evidence:'fixture did not launch'});
      late=attempt;
    }
    const selected=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:1}).events[0];
    await page.goto(f.host.createUiHandoff());
    await page.evaluate(({run,invocation,attempt,cursor})=>{location.hash=new URLSearchParams({run,invocation,phase:'phase-54',attempt,cursor}).toString()},
      {run:f.run.id,invocation:f.invocation.id,attempt:late.id,cursor:selected.cursor});
    await page.getByRole('heading',{name:'phase-54'}).waitFor();
    assert.equal(await page.locator(`.event-row[data-cursor="${selected.cursor}"][data-selected="true"]`).count(),1);
    assert.ok(await page.locator('.timeline-lane').count()<=50);
    await page.evaluate(({run,invocation,cursor})=>{location.hash=new URLSearchParams({run,invocation,cursor}).toString()},
      {run:f.run.id,invocation:f.invocation.id,cursor:selected.cursor});
    await page.getByRole('heading',{name:'phase-54'}).waitFor();
    assert.equal(await page.locator(`.event-row[data-cursor="${selected.cursor}"][data-selected="true"]`).count(),1);
    await page.evaluate(({run,invocation})=>{location.hash=new URLSearchParams({run,invocation,phase:'phase-54'}).toString()},
      {run:f.run.id,invocation:f.invocation.id});
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    assert.equal(await page.locator(`.timeline-lane a[href*="attempt=${late.id}"]`).count()>0,true);
    await page.evaluate(({run,invocation,attempt})=>{location.hash=new URLSearchParams({run,invocation,phase:'phase-0',attempt}).toString()},
      {run:f.run.id,invocation:f.invocation.id,attempt:late.id});
    await page.getByRole('heading',{name:'History unavailable'}).waitFor();
    assert.match(await page.locator('.error-message').innerText(),/phase or attempt|does not belong/i);
    assert.match(await page.getByRole('link',{name:'Return to saved parent'}).getAttribute('href'),new RegExp(f.invocation.id));
    await page.evaluate(({run,invocation})=>{location.hash=new URLSearchParams({run,invocation,cursor:'999999999'}).toString()},
      {run:f.run.id,invocation:f.invocation.id});
    await page.getByRole('heading',{name:'History unavailable'}).waitFor();
  } finally {await browser.close();await f.dispose();}
});
