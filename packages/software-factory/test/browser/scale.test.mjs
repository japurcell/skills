import assert from 'node:assert/strict';
import test from 'node:test';
import { randomUUID } from 'node:crypto';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { chromium } from '@playwright/test';
import { createRepository } from '../fixtures/repository.mjs';
import { initializeRepositoryStore } from '../../dist/store.js';
import { startObservationHost } from '../../dist/dashboard.js';
import { InvocationRecorder } from '../../dist/capture.js';

test('browser stays bounded and displays real committed events within one second at accepted history scale', async t => {
  const repo=createRepository();
  const store=await initializeRepositoryStore(join(repo.path,'.git'),{release:'fixture'});
  let host,browser,database;
  try {
    const run=await store.createRun();
    const worktree=await store.registerWorktree({path:repo.path,registration:'fixture'});
    const invocation=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner:{host:'fixture',pid:process.pid,start:null}});
    await store.activateInvocation(invocation.id);
    const attempt=await store.admitAttempt({id:randomUUID(),invocationId:invocation.id,operationKey:'deep-session-review',kind:'agent',intent:'initial'});
    const recorder=new InvocationRecorder({store,invocationId:invocation.id,requestShutdown:()=>{}});
    const writer=await recorder.openCapture({channel:'stdout'});
    database=new DatabaseSync(join(repo.path,'.git','factory','history.sqlite'));
    const runInsert=database.prepare('INSERT INTO runs(id,data) VALUES (?,?)');
    const sessionInsert=database.prepare('INSERT INTO sessions(id,invocation_id,attempt_id,native_id,data) VALUES (?,?,?,?,?)');
    const eventInsert=database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)');
    const chunkInsert=database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)');
    database.exec('BEGIN IMMEDIATE');
    for(let index=0;index<9999;index++){
      const id=`00000000-0000-4000-8000-${String(index).padStart(12,'0')}`;
      runInsert.run(id,JSON.stringify({id,additionalLimit:20,codeLimit:2,formatLimit:1}));
    }
    for(let index=0;index<1000;index++){
      const id=randomUUID(),nativeId='native-'+index;
      const session={id,attemptId:attempt.id,invocationId:invocation.id,nativeId,parentNativeId:index?'native-'+(index-1):null,lifecycle:'running',usage:{state:'unknown'},loadedSkills:{state:'unknown'},inputsCaptureId:null,outputCaptureId:null,resultCaptureId:null};
      sessionInsert.run(id,invocation.id,attempt.id,nativeId,JSON.stringify(session));
    }
    const at=new Date().toISOString();
    for(let index=0;index<100000;index++)eventInsert.run('fixture.bulk',JSON.stringify({invocationId:invocation.id,at,index}));
    for(let sequence=1;sequence<=50;sequence++)chunkInsert.run(writer.id,sequence,'x'.repeat(65536));
    database.prepare("UPDATE captures SET sequence=50,state='complete' WHERE id=?").run(writer.id);
    database.exec('COMMIT');
    host=await startObservationHost({store});browser=await chromium.launch({headless:true});
    const page=await browser.newPage({viewport:{width:1280,height:850}});
    const indexStart=performance.now();
    await page.goto(host.createUiHandoff());
    await page.getByRole('heading',{name:'Repository runs'}).waitFor();
    const indexMs=performance.now()-indexStart;
    assert.equal(await page.locator('.run-card').count(),30);
    assert.ok(indexMs<1000,`10,000-run first page displayed in ${indexMs.toFixed(0)} ms`);
    await page.evaluate(id=>{location.hash='run='+id},run.id);
    await page.getByRole('heading',{name:'Invocation timeline'}).waitFor();
    assert.ok(await page.locator('.timeline-lane').count()<=50);
    assert.ok(await page.locator('.event-row').count()<=200);
    await page.getByRole('button',{name:'Next sessions'}).click();
    assert.ok(await page.locator('.timeline-lane').count()<=50);
    await page.getByRole('button',{name:'Previous sessions'}).waitFor();
    await page.waitForFunction(()=>!document.querySelector('[data-action="previous-sessions"]')?.disabled);
    const parentId=await page.getByRole('button',{name:'Hide reported children'}).first().getAttribute('data-id');
    const parent=page.locator(`[data-action="collapse"][data-id="${parentId}"]`);
    await parent.click();
    assert.equal(await parent.getAttribute('aria-expanded'),'false');
    await parent.click();
    assert.equal(await parent.getAttribute('aria-expanded'),'true');
    const latencies=[];
    // A second real recorder capture provides 20 fresh, committed append events under the loaded database.
    const live=await recorder.openCapture({channel:'stderr'});
    let observedCursor=await page.locator('.event-row').last().getAttribute('data-cursor');
    for(let index=1;index<=20;index++){
      const started=performance.now();
      await live.write(`live-scale-${index}`);await recorder.barrier();
      await page.waitForFunction(cursor=>[...document.querySelectorAll('.event-row')].some(row=>BigInt(row.dataset.cursor)>BigInt(cursor)),observedCursor,{timeout:3000});
      observedCursor=await page.locator('.event-row').last().getAttribute('data-cursor');
      latencies.push(performance.now()-started);
    }
    latencies.sort((a,b)=>a-b);
    const p95=latencies[Math.ceil(latencies.length*.95)-1];
    t.diagnostic(`index=${indexMs.toFixed(1)}ms; committed-event p95=${p95.toFixed(1)}ms over ${latencies.length} samples; DOM cards=30, lanes<=50, events<=200`);
    assert.ok(p95<1000,`p95 committed-event display ${p95.toFixed(0)} ms; samples ${latencies.map(value=>value.toFixed(0)).join(',')}`);
    await page.getByText('Saved outputs and traces',{exact:true}).click();
    await page.getByRole('button',{name:/stdout/i}).click();
    assert.ok((await page.locator('#capture-text').textContent()).length<=1047552);
    assert.equal(await page.getByRole('button',{name:'Load next saved text'}).isEnabled(),true);
    await page.getByRole('button',{name:'Load next saved text'}).click();
    await page.getByText(/Showing after chunk [1-9]/).waitFor();
    assert.ok((await page.locator('#capture-text').textContent()).length<=1047552);
    if(process.env.FACTORY_SCREENSHOT_DIR)await page.screenshot({path:join(process.env.FACTORY_SCREENSHOT_DIR,'history-scale.png'),fullPage:true});
  } finally {await browser?.close();await host?.close();database?.close();store.close();repo.dispose();}
});
