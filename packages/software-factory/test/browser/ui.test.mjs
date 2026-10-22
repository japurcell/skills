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
    assert.equal(await page.getByText('No managed attempts or reported sessions in this page.').evaluate(element=>element.getBoundingClientRect().right<=element.closest('.timeline-scroll').getBoundingClientRect().right),true);
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

test('repository runs can resume following after Freeze', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    await page.getByRole('button',{name:'Freeze this view'}).click();
    await page.getByRole('button',{name:'Follow latest events'}).click();
    const freeze=page.getByRole('button',{name:'Freeze this view'});
    await freeze.waitFor();
    assert.equal(await freeze.getAttribute('aria-pressed'),'false');
    assert.equal(await page.locator('#connection').getAttribute('data-state'),'connected');
  } finally {await browser.close();await f.dispose();}
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
    await page.waitForFunction(top=>window.scrollY===top,before,{timeout:2000});
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
    await page.getByRole('link',{name:'Return to timeline'}).click();
    await page.waitForFunction(id=>document.activeElement?.matches('.phase-bar')&&document.activeElement?.getAttribute('href')?.includes(id),late.id,{timeout:2000});
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

test('head snapshot race displays one copy of a committed event', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});
  const page=await browser.newPage();
  let unblock,entered;
  const held=new Promise(resolve=>{unblock=resolve});
  const blocked=new Promise(resolve=>{entered=resolve});
  try {
    await page.route(`**/api/runs/${f.run.id}`,async route=>{entered();await held;await route.continue()});
    const navigation=page.goto(f.host.createUiHandoff()+`&run=${f.run.id}&invocation=${f.invocation.id}`);
    await blocked;
    await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'raced-attempt',kind:'command',intent:'initial'});
    const event=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:1}).events[0];
    unblock();await navigation;
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    await page.waitForTimeout(150);
    assert.equal(await page.locator(`.event-row[data-cursor="${event.cursor}"]`).count(),1);
  } finally {unblock?.();await browser.close();await f.dispose();}
});

test('event replay repairs a capture list that was read before the event snapshot', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  let release,entered;const held=new Promise(resolve=>{release=resolve});const intercepted=new Promise(resolve=>{entered=resolve});
  try {
    const stale=f.store.readHistory(f.invocation.id,{limit:50});
    await page.route(url=>url.pathname===`/api/invocations/${f.invocation.id}`&&url.searchParams.has('afterAttempt'),async route=>{
      await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(stale)});
    });
    await page.route(url=>url.pathname===`/api/invocations/${f.invocation.id}/events`&&url.searchParams.get('tail')==='1',async route=>{entered();await held;await route.continue()});
    const navigation=page.goto(f.host.createUiHandoff()+`&run=${f.run.id}&invocation=${f.invocation.id}`);
    await intercepted;
    const capture=await f.store.createCapture({invocationId:f.invocation.id,channel:'stdout'});
    release();await navigation;
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    await page.getByText('capture.created',{exact:false}).first().waitFor();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    await page.locator(`.capture-list [data-id="${capture.id}"]`).waitFor({timeout:2000});
    assert.equal(await page.locator('.event-row').filter({hasText:'capture.created'}).count(),1);
  } finally {release?.();await browser.close();await f.dispose();}
});

test('open stdout follows committed text without replacing focused controls or event links', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    const output=await recorder.openCapture({channel:'stdout'});
    await output.write('first line\n');await recorder.barrier();
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    const captureButton=page.getByRole('button',{name:/stdout/}).first();
    await captureButton.click();
    await page.getByText('first line',{exact:false}).waitFor();
    await captureButton.focus();
    await captureButton.evaluate(element=>{window.savedCaptureButton=element});
    await output.write('second line\n');await recorder.barrier();
    await page.waitForFunction(()=>document.querySelector('#capture-text')?.textContent?.includes('second line'));
    assert.equal(await captureButton.evaluate(element=>element===window.savedCaptureButton&&element===document.activeElement),true);
    assert.equal(await page.getByRole('button',{name:'Load next saved text'}).isDisabled(),true);
    const eventLink=page.locator('.event-row a').last();await eventLink.focus();
    const focusedCursor=await eventLink.getAttribute('aria-label');
    await eventLink.evaluate(element=>{window.savedEventLink=element});
    await output.write('third line\n');await recorder.barrier();
    await page.waitForFunction(()=>document.querySelector('#capture-text')?.textContent?.includes('third line'));
    assert.equal(await page.evaluate(()=>document.activeElement===window.savedEventLink),true);
    assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('aria-label')),focusedCursor);
    if(process.env.FACTORY_SCREENSHOT_DIR)await page.screenshot({path:join(process.env.FACTORY_SCREENSHOT_DIR,'live-output.png'),fullPage:true});
    await page.locator('#capture-text').evaluate(element=>{const selection=window.getSelection(),range=document.createRange();range.setStart(element.firstChild,0);range.setEnd(element.firstChild,5);selection.removeAllRanges();selection.addRange(range)});
    await output.write('fourth line\n');await recorder.barrier();
    const fourth=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:1}).events[0];
    await page.locator(`.event-row[data-cursor="${fourth.cursor}"]`).waitFor();
    assert.equal(await page.evaluate(()=>window.getSelection()?.toString()),'first');
    assert.equal(await page.locator('#capture-text').innerText(),'first line\nsecond line\nthird line\n');
    await page.locator('#capture-text').evaluate(element=>{window.getSelection()?.removeAllRanges();element.scrollTop=element.scrollHeight;element.dispatchEvent(new Event('scroll',{bubbles:true}))});
    await page.waitForFunction(()=>document.querySelector('#capture-text')?.textContent?.includes('fourth line'));
  } finally {await browser.close();await f.dispose();}
});

test('rapid capture appends catch up after a stale in-flight page response', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  let release;const held=new Promise(resolve=>{release=resolve});
  let entered;const intercepted=new Promise(resolve=>{entered=resolve});
  try {
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    const output=await recorder.openCapture({channel:'stdout'});
    await output.write('first line\n');await recorder.barrier();
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    await page.getByRole('button',{name:/stdout/}).click();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    await page.route(url=>url.pathname.endsWith('/captures/'+output.id)&&url.searchParams.get('after')==='1',async route=>{
      entered();await held;await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(stale)});
    });
    await output.write('second line\n');await recorder.barrier();
    await intercepted;
    const stale=f.store.readInvocationCapture({invocationId:f.invocation.id,id:output.id,after:1,limit:49});
    await output.write('third line\n');await recorder.barrier();
    const third=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:1}).events[0];
    await page.locator(`.event-row[data-cursor="${third.cursor}"]`).waitFor({timeout:2000});
    release();
    await page.waitForFunction(()=>document.querySelector('#capture-text')?.textContent?.includes('third line'),null,{timeout:2000});
    assert.equal(await page.getByRole('button',{name:'Load next saved text'}).isDisabled(),true);
  } finally {release?.();await browser.close();await f.dispose();}
});

test('delayed output page cannot replace a newly selected capture', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  let release,entered;const held=new Promise(resolve=>{release=resolve});const intercepted=new Promise(resolve=>{entered=resolve});
  try {
    const first=await f.store.createCapture({invocationId:f.invocation.id,channel:'stdout'});
    for(let start=1;start<=51;start+=4)await f.store.appendCapture({id:first.id,chunks:Array.from({length:Math.min(4,52-start)},(_,index)=>({sequence:start+index,text:`A-${start+index}\n`}))});
    const second=await f.store.createCapture({invocationId:f.invocation.id,channel:'stderr'});
    await f.store.appendCapture({id:second.id,chunks:[{sequence:1,text:'B-only\n'}]});
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    await page.locator(`[data-action="open-capture"][data-id="${first.id}"]`).click();
    await page.getByText('A-50',{exact:false}).waitFor();
    await page.route(url=>url.pathname.endsWith('/captures/'+first.id)&&url.searchParams.get('after')==='50',async route=>{entered();await held;await route.continue()});
    const pending=page.locator('[data-action="more-output"]').click({noWaitAfter:true});
    await intercepted;
    const secondButton=page.locator(`[data-action="open-capture"][data-id="${second.id}"]`);
    await secondButton.click();
    await page.getByText('B-only',{exact:false}).waitFor();
    await secondButton.focus();
    release();await pending;
    assert.match(await page.locator('#capture-view').innerText(),/B-only/);
    assert.doesNotMatch(await page.locator('#capture-view').innerText(),/A-51/);
    assert.equal(await secondButton.evaluate(element=>element===document.activeElement),true);
  } finally {release?.();await browser.close();await f.dispose();}
});

test('delayed history page cannot alter a different reader', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  let release,entered;const held=new Promise(resolve=>{release=resolve});const intercepted=new Promise(resolve=>{entered=resolve});
  try {
    const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'history-race',kind:'agent',intent:'initial'});
    for(let i=0;i<55;i++)await f.store.saveSession(attempt.id,{nativeId:`session-${i}`,parentNativeId:null,lifecycle:'running'});
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.route(url=>url.pathname.endsWith(`/invocations/${f.invocation.id}/sessions`)&&url.searchParams.get('after')!=='0',async route=>{entered();await held;await route.continue()});
    const pending=page.getByRole('button',{name:'Next sessions'}).click({noWaitAfter:true});
    await intercepted;
    await page.getByRole('link',{name:'Repository runs',exact:true}).click();
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    release();await pending;
    assert.equal(await page.locator('h1').first().innerText(),'Repository runs');
    assert.deepEqual(await page.locator('.error-message').allInnerTexts(),[]);
  } finally {release?.();await browser.close();await f.dispose();}
});

test('delayed earlier event page cannot freeze Repository runs', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  let release,entered;const held=new Promise(resolve=>{release=resolve});const intercepted=new Promise(resolve=>{entered=resolve});
  try {
    for(let i=0;i<205;i++)await f.store.createCapture({invocationId:f.invocation.id,channel:'stdout'});
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.route(url=>url.pathname.endsWith(`/invocations/${f.invocation.id}/events`)&&url.searchParams.has('before'),async route=>{entered();await held;await route.continue()});
    const pending=page.getByRole('button',{name:'Load earlier events'}).click({noWaitAfter:true});
    await intercepted;
    await page.getByRole('link',{name:'Repository runs',exact:true}).click();
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    release();await pending;
    assert.equal(await page.getByRole('button',{name:'Freeze this view'}).getAttribute('aria-pressed'),'false');
    assert.equal(await page.locator('#connection').getAttribute('data-state'),'connected');
  } finally {release?.();await browser.close();await f.dispose();}
});

test('delayed latest event page cannot unfreeze Repository runs', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  let release,entered;const held=new Promise(resolve=>{release=resolve});const intercepted=new Promise(resolve=>{entered=resolve});
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByRole('button',{name:'Freeze this view'}).click();
    await page.route(url=>url.pathname.endsWith(`/invocations/${f.invocation.id}/events`)&&url.searchParams.get('tail')==='1',async route=>{entered();await held;await route.continue()});
    const pending=page.getByRole('button',{name:'Follow latest events'}).click({noWaitAfter:true});
    await intercepted;
    await page.getByRole('link',{name:'Repository runs',exact:true}).click();
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    release();await pending;
    assert.equal(await page.getByRole('button',{name:'Follow latest events'}).getAttribute('aria-pressed'),'true');
    assert.equal(await page.locator('#connection').getAttribute('data-state'),'frozen');
  } finally {release?.();await browser.close();await f.dispose();}
});

test('Follow replays an event committed while its tail page was in flight', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  let release,entered;const held=new Promise(resolve=>{release=resolve});const intercepted=new Promise(resolve=>{entered=resolve});
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    await page.getByRole('button',{name:'Freeze this view'}).click();
    const stale=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:200});
    await page.route(url=>url.pathname.endsWith(`/invocations/${f.invocation.id}/events`)&&url.searchParams.get('tail')==='1',async route=>{entered();await held;await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(stale)})});
    const pending=page.getByRole('button',{name:'Follow latest events'}).click({noWaitAfter:true});
    await intercepted;
    const capture=await f.store.createCapture({invocationId:f.invocation.id,channel:'stdout'});
    await page.locator('#pending-events').getByText(/new events/).waitFor();
    release();await pending;
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    await page.locator(`.capture-list [data-id="${capture.id}"]`).waitFor({timeout:2000});
    assert.equal(await page.locator('.event-row').filter({hasText:'capture.created'}).count(),1);
  } finally {release?.();await browser.close();await f.dispose();}
});

test('capture event resolves its saved attempt, invalid direct link retains parent, and return focuses the phase', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'capture-phase',kind:'command',intent:'initial'});
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    const capture=await recorder.openCapture({channel:'stdout',attemptId:attempt.id});
    await capture.write('captured bytes');await recorder.barrier();
    const saved=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:200}).events.find(event=>event.kind==='capture.appended');
    await page.goto(f.host.createUiHandoff()+`&run=${f.run.id}&invocation=${f.invocation.id}&phase=capture-phase&attempt=${attempt.id}&cursor=${saved.cursor}`);
    await page.getByRole('heading',{name:'capture-phase'}).waitFor({timeout:2000});
    assert.equal(await page.locator(`.event-row[data-cursor="${saved.cursor}"]`).count(),1);
    assert.doesNotMatch(await page.locator('#inspector').innerText(),/No attempt selected/);
    if(process.env.FACTORY_SCREENSHOT_DIR)await page.screenshot({path:join(process.env.FACTORY_SCREENSHOT_DIR,'capture-target.png'),fullPage:true});
    const direct=await browser.newPage();
    await direct.goto(f.host.createUiHandoff()+`&run=${f.run.id}&invocation=${f.invocation.id}&cursor=999999999`);
    await direct.getByRole('heading',{name:'History unavailable'}).waitFor();
    assert.equal(await direct.getByRole('link',{name:'Return to saved parent'}).getAttribute('href'),`#run=${f.run.id}&invocation=${f.invocation.id}`);
    await page.getByRole('link',{name:'Return to timeline'}).click();
    await page.waitForFunction(id=>document.activeElement?.matches('.phase-bar')&&document.activeElement?.getAttribute('href')?.includes(id),attempt.id,{timeout:2000});
    assert.equal(await page.evaluate(id=>document.activeElement?.matches('.phase-bar')&&document.activeElement?.getAttribute('href')?.includes(id),attempt.id),true);
  } finally {await browser.close();await f.dispose();}
});

test('a capture beyond the first history page resolves only its saved attempt', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    const first=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'first-phase',kind:'command',intent:'initial'});
    const late=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'late-phase',kind:'command',intent:'initial'});
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    for(let i=0;i<55;i++) {
      const capture=await recorder.openCapture({channel:'stdout',attemptId:i===54?late.id:first.id});
      if(i===54)await capture.write('late saved bytes');
      await capture.finish();
    }
    await recorder.barrier();
    const saved=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:1}).events[0];
    await page.goto(f.host.createUiHandoff()+`&run=${f.run.id}&invocation=${f.invocation.id}&attempt=${late.id}&phase=late-phase&cursor=${saved.cursor}`);
    await page.getByRole('heading',{name:'late-phase'}).waitFor({timeout:2000});
    assert.ok(await page.locator('.capture-list button').count()<=50);
    await page.evaluate(values=>{location.hash=new URLSearchParams(values).toString()},
      {run:f.run.id,invocation:f.invocation.id,attempt:first.id,phase:'first-phase',cursor:saved.cursor});
    await page.getByRole('heading',{name:'History unavailable'}).waitFor({timeout:2000});
    assert.match(await page.locator('.error-message').innerText(),/does not belong to the selected attempt/i);
  } finally {await browser.close();await f.dispose();}
});

test('loaded run card updates saved workflow and request preview in place', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    const card=page.locator('.run-card');
    await card.evaluate(element=>{window.savedCard=element;window.savedCardLink=element.querySelector('.card-head a')});
    const link=card.locator('.card-head a');await link.focus();
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    const context=await recorder.openCapture({channel:'context'});
    await context.write(JSON.stringify({inputs:'Unique live preview',question:null,contexts:[]}));
    await context.finish();await recorder.barrier();
    await f.store.saveInvocationMetadata(f.invocation.id,{workflow:'new-workflow',inputCaptureId:context.id});
    await page.waitForFunction(()=>document.querySelector('.card-head')?.textContent?.includes('Unique live preview'),null,{timeout:2000});
    assert.match(await card.locator('.card-head').innerText(),/new-workflow/);
    assert.equal(await card.evaluate(element=>element===window.savedCard&&document.activeElement===window.savedCardLink),true);
  } finally {await browser.close();await f.dispose();}
});

test('Back restores manually selected attempt page and selected reader window', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    for(let i=0;i<55;i++) {
      const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:`phase-${i}`,kind:'command',intent:'initial'});
      await f.store.settleAttempt({id:attempt.id,launch:'not_started',outcome:'interrupted',quiescent:true,evidence:'not launched'});
    }
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByRole('button',{name:'Next attempts'}).click();
    await page.getByText('phase-50',{exact:true}).first().waitFor();
    await page.getByRole('link',{name:'Repository runs',exact:true}).click();
    await page.goBack();
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    await page.waitForFunction(()=>document.getElementById('app')?.getAttribute('aria-busy')===null);
    assert.equal(await page.locator('.timeline-lane .lane-label strong').first().innerText(),'phase-50');
  } finally {await browser.close();await f.dispose();}
});

test('a closed failure explanation stays closed during later cleanup updates', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    await f.store.finishInvocation(f.invocation.id,'failed','unknown');
    const explanation=page.getByText('Failure explanation').locator('..');
    await explanation.waitFor();
    assert.equal(await explanation.getAttribute('open'),'');
    await explanation.locator('summary').click();
    assert.equal(await explanation.getAttribute('open'),null);
    if(process.env.FACTORY_SCREENSHOT_DIR)await page.screenshot({path:join(process.env.FACTORY_SCREENSHOT_DIR,'closed-explanation.png'),fullPage:true});
    await explanation.evaluate(element=>{window.savedExplanation=element});
    await f.store.clearOwner({claimId:f.invocation.claim.id,token:f.invocation.claim.token,operatorConfirmed:true,note:'Fixture inspection',inspection:'not_live'});
    await page.waitForFunction(()=>document.querySelector('#cleanup-state')?.textContent?.includes('Operator confirmed'),null,{timeout:2000});
    assert.equal(await explanation.evaluate(element=>element===window.savedExplanation&&element.open===false),true);
  } finally {await browser.close();await f.dispose();}
});

test('scrolling away pauses open capture follow while outcome stays live and output stays bounded', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    const capture=await f.store.createCapture({invocationId:f.invocation.id,channel:'stdout'});
    const chunk='x'.repeat(65536);
    for(let start=1;start<=15;start+=4) {
      const chunks=Array.from({length:Math.min(4,16-start)},(_,index)=>({sequence:start+index,text:chunk}));
      await f.store.appendCapture({id:capture.id,chunks});
    }
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    await page.getByRole('button',{name:/stdout/}).click();
    const text=page.locator('#capture-text');
    assert.equal(await text.evaluate(element=>element.textContent.length),15*65536);
    await text.evaluate(element=>{element.scrollTop=0});
    await f.store.appendCapture({id:capture.id,chunks:[{sequence:16,text:'NEW'+chunk.slice(3)}]});
    await f.store.finishInvocation(f.invocation.id,'needs_input','unknown');
    await page.waitForFunction(()=>document.querySelector('#cleanup-state')?.textContent?.includes('Manual cleanup required'),null,{timeout:2000});
    assert.equal(await text.evaluate(element=>element.scrollTop),0);
    assert.equal(await text.evaluate(element=>element.textContent.length),15*65536);
    await text.evaluate(element=>{element.scrollTop=element.scrollHeight;element.dispatchEvent(new Event('scroll',{bubbles:true}));});
    await page.getByRole('button',{name:'Load next saved text'}).waitFor({state:'visible'});
    await page.waitForFunction(()=>!document.querySelector('[data-action="more-output"]')?.disabled,null,{timeout:2000});
    assert.ok(await text.evaluate(element=>element.textContent.length)<=1047552);
    await page.getByRole('button',{name:'Load next saved text'}).click();
    await page.getByText('NEW',{exact:false}).waitFor();
  } finally {await browser.close();await f.dispose();}
});

test('Back restores session, capture and earlier event pages with the selected capture', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'history-pages',kind:'agent',intent:'initial'});
    const sessions=[];
    for(let i=0;i<55;i++)sessions.push(await f.store.saveSession(attempt.id,{nativeId:`session-${i}`,parentNativeId:null,lifecycle:'running'}));
    const captures=[];
    for(let i=0;i<180;i++)captures.push(await f.store.createCapture({invocationId:f.invocation.id,channel:'stdout'}));
    await page.goto(f.host.createUiHandoff());
    await page.getByRole('link',{name:new RegExp(f.run.id.slice(0,8))}).click();
    await page.getByRole('button',{name:'Next sessions'}).click();
    await page.locator(`.timeline-lane[data-session="${sessions[50].id}"]`).waitFor({timeout:2000});
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    await page.getByRole('button',{name:'Next captures'}).click();
    await page.locator(`.capture-list [data-id="${captures[50].id}"]`).click();
    await page.getByRole('button',{name:'Load earlier events'}).click();
    await page.getByRole('button',{name:'Follow latest events'}).first().waitFor({timeout:2000});
    const firstCursor=await page.locator('.event-row').first().getAttribute('data-cursor');
    await page.getByRole('link',{name:'Repository runs',exact:true}).click();
    await page.goBack();
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    await page.waitForFunction(id=>document.querySelector('#capture-view')?.textContent?.includes(id.slice(0,8)),captures[50].id,{timeout:2000});
    assert.equal(await page.locator(`.timeline-lane[data-session="${sessions[50].id}"]`).count(),1);
    assert.equal(await page.locator(`.capture-list [data-id="${captures[50].id}"]`).count(),1);
    assert.equal(await page.locator('.event-row').first().getAttribute('data-cursor'),firstCursor);
  } finally {await browser.close();await f.dispose();}
});

test('a selected attempt shows newly committed capture events for its saved owner', async () => {
  const f=await fixture();const browser=await chromium.launch({headless:true});const page=await browser.newPage();
  try {
    const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'live-capture-owner',kind:'command',intent:'initial'});
    await page.goto(f.host.createUiHandoff()+`&run=${f.run.id}&invocation=${f.invocation.id}&phase=live-capture-owner&attempt=${attempt.id}`);
    await page.getByRole('heading',{name:'live-capture-owner'}).waitFor();
    await page.waitForFunction(()=>document.getElementById('connection')?.textContent?.startsWith('Connected'));
    const recorder=new InvocationRecorder({store:f.store,invocationId:f.invocation.id,requestShutdown:()=>{}});
    const capture=await recorder.openCapture({channel:'stdout',attemptId:attempt.id});
    await capture.write('owner text');await recorder.barrier();
    const saved=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:1}).events[0];
    await page.locator(`.event-row[data-cursor="${saved.cursor}"]`).waitFor({timeout:2000});
  } finally {await browser.close();await f.dispose();}
});
