import assert from 'node:assert/strict';
import test from 'node:test';
import { request, createServer } from 'node:http';
import { createConnection } from 'node:net';
import { execFile } from 'node:child_process';
import { DatabaseSync } from 'node:sqlite';
import { once } from 'node:events';
import { setTimeout as delay } from 'node:timers/promises';
import { join } from 'node:path';
import { promisify } from 'node:util';
import { randomUUID } from 'node:crypto';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { startObservationHost } from '../dist/dashboard.js';

test('host publishes only a bound loopback endpoint and reuses its current repository claim', async () => {
  const repo = createRepository();
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  let host;
  try {
    host = await startObservationHost({ store });
    assert.match(host.url, /^http:\/\/127\.0\.0\.1:\d+$/);
    const response = await authorizedFetch(host, host.url + '/api/events?after=0&limit=1');
    assert.equal(response.status, 200);
    assert.equal((await response.json()).events.length, 1);
    const reuse = await startObservationHost({ store });
    assert.equal(reuse.reused, true);
    assert.equal(reuse.url, host.url);
    assert.equal(reuse.sessionToken, host.sessionToken);
    assert.equal(reuse.readCredentialAvailable, true);
    assert.equal((await authorizedFetch(reuse, reuse.url + '/api/events')).status, 200);
  } finally { await host?.close(); store.close(); repo.dispose(); }
});

test('notification preferences and one selected acknowledgment persist through authenticated metadata routes', async () => {
  const f = await fixture(); let host;
  try {
    host = await startObservationHost({ store: f.store });
    const preferences = host.url + '/api/notifications/preferences';
    assert.deepEqual(await (await authorizedFetch(host, preferences)).json(), { successNotices: false, reminders: false, updatedAt: null });
    assert.equal((await fetch(preferences)).status, 403);
    const write = (path, body) => authorizedFetch(host, host.url + path, { method: 'POST', headers: { Origin: host.url, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const body = JSON.stringify({ successNotices: true, reminders: false });
    const authorizedHeaders = { Origin: host.url, Authorization: 'Bearer ' + host.sessionToken, 'Content-Type': 'application/json' };
    assert.equal((await http(host.url, { path: '/api/notifications/preferences', method: 'POST', body, headers: { Origin: host.url, 'Content-Type': 'application/json' } })).status, 403);
    assert.equal((await http(host.url, { path: '/api/notifications/preferences', method: 'POST', body, headers: { ...authorizedHeaders, Origin: 'https://foreign.invalid' } })).status, 403);
    assert.equal((await http(host.url, { path: '/api/notifications/preferences', method: 'POST', body, headers: { Authorization: authorizedHeaders.Authorization, 'Content-Type': 'application/json' } })).status, 403);
    assert.equal((await http(host.url, { path: '/api/notifications/preferences', method: 'POST', body, headers: { ...authorizedHeaders, 'Content-Type': 'text/plain' } })).status, 415);
    assert.equal((await http(host.url, { path: '/api/notifications/preferences', method: 'POST', body: 'x'.repeat(8193), headers: authorizedHeaders })).status, 413);
    assert.equal((await http(host.url, { path: '/api/notifications/preferences', method: 'POST', body, headers: ['Origin', host.url, 'Authorization', authorizedHeaders.Authorization, 'Authorization', authorizedHeaders.Authorization, 'Content-Type', 'application/json'] })).status, 400);
    assert.equal(f.store.readNotificationPreferences().successNotices, false);
    assert.equal((await write('/api/notifications/acknowledgments', { invocationId: f.invocation.id })).status, 400);
    const saved = await write('/api/notifications/preferences', { successNotices: true, reminders: false });
    assert.equal(saved.status, 200);
    assert.equal((await saved.json()).successNotices, true);
    for (const body of [{ successNotices: true }, { successNotices: true, reminders: false, extra: 1 }, { successNotices: 'yes', reminders: false }])
      assert.equal((await write('/api/notifications/preferences', body)).status, 400);
    assert.equal((await authorizedFetch(host, preferences)).status, 200);
    await f.store.finalizeInvocation({ id: f.invocation.id, outcome: 'failed', cleanup: 'complete', claimId: f.invocation.claim.id, token: f.invocation.claim.token });
    const ack = await write('/api/notifications/acknowledgments', { invocationId: f.invocation.id });
    assert.equal(ack.status, 200);
    const original = await ack.json();
    assert.equal(original.invocationId, f.invocation.id);
    assert.deepEqual(await (await write('/api/notifications/acknowledgments', { invocationId: f.invocation.id })).json(), original);
    assert.deepEqual((await (await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id)).json()).acknowledgment, original);
    assert.equal((await write('/api/notifications/acknowledgments', { invocationId: f.invocation.id, answer: 'yes' })).status, 400);
    assert.equal((await write('/api/notifications/acknowledgments', { invocationId: '-'.repeat(36) })).status, 400);
    assert.equal((await write('/api/notifications/acknowledgments', { invocationId: '00000000-0000-0000-0000-000000000000' })).status, 404);
    await host.close(); host = undefined; f.store.close();
    const reopened = openRepositoryStore(join(f.repo.path, '.git'));
    try { assert.equal(reopened.readNotificationPreferences().successNotices, true); assert.deepEqual(reopened.readNotificationAcknowledgment(f.invocation.id), original); }
    finally { reopened.close(); }
  } finally { await host?.close(); if (host) f.store.close(); f.repo.dispose(); }
});

async function fixture() {
  const repo = createRepository();
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  const run = await store.createRun();
  const worktree = await store.registerWorktree({ path: repo.path, registration: 'fixture' });
  const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
  await store.activateInvocation(invocation.id);
  return { repo, store, invocation, dispose: () => { store.close(); repo.dispose(); } };
}
function authorizedFetch(host, url, options = {}) {
  return fetch(url, { ...options, headers: { ...options.headers, Authorization: 'Bearer ' + host.sessionToken } });
}

test('selected observation routes require bearer and reject foreign or mismatched saved targets', async () => {
  const f=await fixture();let host;
  try {
    const attempt=await f.store.admitAttempt({id:randomUUID(),invocationId:f.invocation.id,operationKey:'selected-phase',kind:'command',intent:'initial'});
    const event=f.store.readInvocationEvents({invocationId:f.invocation.id,tail:true,limit:1}).events[0];
    host=await startObservationHost({store:f.store});
    const base=host.url+'/api/invocations/'+f.invocation.id;
    const targets=[base+'/events/'+event.cursor,base+'/attempt-page?attempt='+attempt.id+'&phase=selected-phase',base+'/question'];
    for(const target of targets) {
      assert.equal((await fetch(target)).status,403);
      assert.equal((await authorizedFetch(host,target)).status,200);
    }
    const capture=await f.store.createCapture({invocationId:f.invocation.id,attemptId:attempt.id,channel:'stdout'});
    const captureTarget=base+'/captures/'+capture.id;
    assert.equal((await fetch(captureTarget)).status,403);
    assert.equal((await (await authorizedFetch(host,captureTarget)).json()).attemptId,attempt.id);
    await f.store.appendCapture({id:capture.id,chunks:[],state:'complete'});
    assert.equal((await authorizedFetch(host,base+'/attempt-page?attempt='+attempt.id+'&phase=other-phase')).status,404);
    assert.equal((await authorizedFetch(host,base+'/events/999999999')).status,404);
    await f.store.settleAttempt({id:attempt.id,launch:'not_started',outcome:'interrupted',quiescent:true,evidence:'fixture did not launch'});
    await f.store.finalizeInvocation({id:f.invocation.id,outcome:'succeeded',cleanup:'complete',claimId:f.invocation.claim.id,token:f.invocation.claim.token});
    const followup=await f.store.startInvocation({runId:f.invocation.runId,worktreeId:f.invocation.worktreeId,owner:{host:'fixture',pid:process.pid,start:null}});
    assert.equal((await authorizedFetch(host,host.url+'/api/invocations/'+followup.id+'/events/'+event.cursor)).status,404);
    assert.equal((await authorizedFetch(host,host.url+'/api/invocations/'+followup.id+'/attempt-page?attempt='+attempt.id)).status,404);
    assert.equal((await authorizedFetch(host,host.url+'/api/invocations/'+followup.id+'/captures/'+capture.id)).status,404);
  } finally {await host?.close();f.dispose();}
});
async function frame(reader) {
  let text = '';
  while (!text.includes('\n\n')) {
    const result = await Promise.race([reader.read(), new Promise((_, reject) => { const timer = setTimeout(() => reject(new Error('SSE timeout')), 2000); timer.unref(); })]);
    if (result.done) throw new Error('stream ended before event');
    text += new TextDecoder().decode(result.value);
  }
  return text;
}

test('real recorder bytes are committed before SSE references, with saved capture reads and duplicate-free reconnect', async () => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const f = await fixture(); let host, reader;
  try {
    host = await startObservationHost({ store: f.store });
    const recorder = new InvocationRecorder({ store: f.store, invocationId: f.invocation.id, requestShutdown: () => {} });
    const writer = await recorder.openCapture({ channel: 'stdout' });
    const before = (await (await authorizedFetch(host, host.url + '/api/events')).json()).nextCursor;
    await writer.write('saved fixture output');
    const response = await authorizedFetch(host, host.url + '/api/stream?after=' + before);
    assert.equal(response.status, 200); reader = response.body.getReader();
    await recorder.barrier();
    const text = await frame(reader);
    assert.match(text, /capture.appended/);
    const data = JSON.parse(text.split('data: ')[1].split('\n')[0]);
    const capture = await (await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id + '/captures/' + writer.id)).json();
    assert.equal(capture.chunks.map(chunk => chunk.text).join(''), 'saved fixture output');
    const cursor = data.cursor;
    await reader.cancel(); reader = undefined;
    const reconnect = await authorizedFetch(host, host.url + '/api/stream', { headers: { 'Last-Event-ID': cursor } });
    reader = reconnect.body.getReader();
    await writer.finish();
    const next = await frame(reader);
    assert.ok(BigInt(next.match(/id: (\d+)/)[1]) > BigInt(cursor));
    const detail = await (await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id)).json();
    assert.equal(detail.invocation.id, f.invocation.id);
    assert.equal((await (await authorizedFetch(host, host.url + '/api/invocations')).json()).invocations.length, 1);
    assert.equal((await (await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id + '/sessions')).json()).sessions.length, 0);
  } finally { await reader?.cancel(); await host?.close(); f.dispose(); }
});

function http(url, { path = '/api/events', method = 'GET', headers = {}, body } = {}) {
  return new Promise((resolve, reject) => {
    const req = request(url, { path, method, headers, agent: false }, response => {
      let text = ''; response.on('data', chunk => { text += chunk; });
      response.on('end', () => resolve({ status: response.statusCode, text, headers: response.headers }));
      response.on('error', reject);
    });
    req.on('error', reject); if (body) req.write(body); req.end();
  });
}

test('saved observation routes reject an unauthenticated local reader', async () => {
  const f = await fixture(); let host;
  try {
    host = await startObservationHost({ store: f.store });
    const prefix = '/api/invocations/' + f.invocation.id;
    for (const path of ['/api/events', '/api/stream', '/api/invocations', prefix,
      prefix + '/sessions', prefix + '/sessions/' + crypto.randomUUID(),
      prefix + '/attempts/' + crypto.randomUUID(), prefix + '/captures/' + crypto.randomUUID()]) {
      assert.equal((await http(host.url, { path })).status, 403, path);
      assert.equal((await http(host.url, { path, headers: { Authorization: 'Bearer wrong' } })).status, 403, path);
    }
    assert.equal((await http(host.url, { path: '/api/identity?challenge=' + crypto.randomUUID() })).status, 200);
    assert.equal((await http(host.url, { headers: { Origin: 'https://evil.invalid', Authorization: 'Bearer ' + host.sessionToken } })).status, 403);
    assert.equal((await http(host.url, { headers: { Host: 'evil.invalid', Authorization: 'Bearer ' + host.sessionToken } })).status, 403);
    const identity = await http(host.url, { path: '/api/identity?challenge=' + crypto.randomUUID() });
    assert.ok(!identity.text.includes(host.sessionToken));
  } finally { await host?.close(); f.dispose(); }
});

test('a separate process can verify the owner without receiving its read credential', async () => {
  const f = await fixture(); let host;
  try {
    host = await startObservationHost({ store: f.store });
    const script = `import { openRepositoryStore } from './dist/store.js';
      import { startObservationHost } from './dist/dashboard.js';
      const store = openRepositoryStore(process.argv[1]);
      try { const host = await startObservationHost({ store });
        process.stdout.write(JSON.stringify({ url: host.url, reused: host.reused, sessionToken: host.sessionToken, readCredentialAvailable: host.readCredentialAvailable }));
      } finally { store.close(); }`;
    const { stdout } = await promisify(execFile)(process.execPath, ['--input-type=module', '-e', script, join(f.repo.path, '.git')], { cwd: new URL('../', import.meta.url) });
    const reuse = JSON.parse(stdout);
    assert.equal(reuse.reused, true);
    assert.equal(reuse.url, host.url);
    assert.equal(reuse.sessionToken, undefined);
    assert.equal(reuse.readCredentialAvailable, false);
    assert.equal((await http(reuse.url)).status, 403);
  } finally { await host?.close(); f.dispose(); }
});

test('host rejects hostile authority, origins, paths, cursors and credentials without read-side mutations', async () => {
  const f = await fixture(); let host; const writes = [];
  try {
    host = await startObservationHost({ store: f.store, notificationWrite: async (kind, body) => { writes.push({ kind, body }); return { saved: true }; } });
    const saved = (await (await authorizedFetch(host, host.url + '/api/events')).json()).nextCursor;
    for (const headers of [{ Host: 'evil.invalid' }, { Origin: 'https://evil.invalid' }, { Referer: 'https://evil.invalid/' }, { Referer: 'malformed' }, { 'Sec-Fetch-Site': 'cross-site' }]) {
      assert.equal((await http(host.url, { headers })).status, 403);
    }
    for (const path of ['//evil.invalid/api/events', '/api/../events', '/api/%2e%2e/events', 'http://evil.invalid/api/events', '/api/events?after=-1', '/api/events?after=1.1', '/api/events?after=9223372036854775808', '/api/events?after=0&after=1', '/api/events?limit=201', '/api/stream?after=garbage', '/api/events?limit=0', '/api/invocations?limit=101', '/api/invocations?after=9007199254740992']) {
      assert.equal((await http(host.url, { path, headers: { Authorization: 'Bearer ' + host.sessionToken } })).status, 400, path);
    }
    for (const path of ['/api/execute', '/api/clearance', '/api/install', '/api/notifications/acknowledgments']) {
      const response = await http(host.url, { path }); assert.equal(response.status, 404);
    }
    const base = { path: '/api/notifications/preferences', method: 'POST', body: '{}', headers: { Origin: host.url, 'Content-Type': 'application/json' } };
    assert.equal((await http(host.url, base)).status, 403);
    assert.equal((await http(host.url, { ...base, headers: { ...base.headers, Authorization: 'Bearer wrong' } })).status, 403);
    assert.equal((await http(host.url, { ...base, headers: { ...base.headers, Origin: 'https://evil.invalid', Authorization: 'Bearer ' + host.sessionToken } })).status, 403);
    assert.equal((await http(host.url, { path: '/api/execute', method: 'POST' })).status, 405);
    const authorized = { ...base, headers: { ...base.headers, Authorization: 'Bearer ' + host.sessionToken } };
    assert.equal((await http(host.url, { ...authorized, body: 'x'.repeat(8193) })).status, 413);
    assert.equal((await http(host.url, { ...authorized, body: '{' })).status, 400);
    assert.equal(writes.length, 0);
    assert.equal((await http(host.url, { ...authorized, body: JSON.stringify({ label: 'λ' }) })).status, 200); assert.equal(writes.length, 1); assert.equal(writes[0].body.label, 'λ');
    assert.equal((await (await authorizedFetch(host, host.url + '/api/events')).json()).nextCursor, saved);
    assert.equal(f.store.readInvocation(f.invocation.id).stage, 'running');
  } finally { await host?.close(); f.dispose(); }
});

test('cursor pagination is bounded, gap is explicit and stream limit is reclaimed on disconnect', async () => {
  const f = await fixture(); let host; const readers = [];
  try {
    host = await startObservationHost({ store: f.store });
    let after = '0'; const ids = [];
    while (true) {
      const page = await (await authorizedFetch(host, host.url + '/api/events?limit=1&after=' + after)).json();
      assert.ok(Buffer.byteLength(JSON.stringify(page)) <= 1048576);
      if (!page.events.length) break;
      ids.push(page.events[0].cursor); after = page.nextCursor;
    }
    assert.equal(new Set(ids).size, ids.length); assert.ok(ids.length >= 5);
    let response = await authorizedFetch(host, host.url + '/api/stream?after=9223372036854775807');
    assert.match(await response.text(), /event: gap/);
    assert.equal((await authorizedFetch(host, host.url + '/api/stream?after=0', { headers: { 'Last-Event-ID': '1' } })).status, 400);
    for (let i = 0; i < 16; i++) { response = await authorizedFetch(host, host.url + '/api/stream?after=' + after); readers.push(response.body.getReader()); }
    assert.equal((await authorizedFetch(host, host.url + '/api/stream?after=' + after)).status, 429);
    await readers.pop().cancel(); await delay(50);
    response = await authorizedFetch(host, host.url + '/api/stream?after=' + after); assert.equal(response.status, 200); await response.body.cancel();
  } finally { await Promise.all(readers.map(reader => reader.cancel())); await host?.close(); f.dispose(); }
});

test('bind conflict releases only the failed start claim; stale and wrong-repository endpoints never cause takeover', async () => {
  const f = await fixture(), other = await fixture(); let host;
  const occupied = createServer(); occupied.listen(0, '127.0.0.1'); await once(occupied, 'listening');
  try {
    await assert.rejects(startObservationHost({ store: f.store, port: occupied.address().port }), /EADDRINUSE/);
    assert.equal(f.store.readDashboardClaim(), undefined);
    host = await startObservationHost({ store: f.store });
    const claim = await other.store.claimResource({ kind: 'dashboard', owner: f.store.readDashboardClaim().owner });
    await other.store.publishDashboardEndpoint({ claimId: claim.id, token: claim.token, url: host.url, instanceId: 'wrong-repository' });
    await assert.rejects(startObservationHost({ store: other.store }), /verification failed/);
    assert.equal(other.store.readDashboardClaim().id, claim.id);
    const saved = f.store.readDashboardClaim();
    await f.store.releaseClaim({ claimId: saved.id, token: saved.token, basis: 'quiescent' });
    const replacement = await f.store.claimResource({ kind: 'dashboard', owner: saved.owner });
    await f.store.publishDashboardEndpoint({ claimId: replacement.id, token: replacement.token, url: host.url, instanceId: 'stale-host' });
    assert.equal((await authorizedFetch(host, host.url + '/api/events')).status, 503);
    await assert.rejects(startObservationHost({ store: f.store }), /verification failed/);
    await host.close(); host = undefined;
    assert.equal(f.store.readDashboardClaim().id, replacement.id);
  } finally { await host?.close(); occupied.closeAllConnections(); await new Promise(resolve => occupied.close(resolve)); f.dispose(); other.dispose(); }
});

test('recorder failure never displays uncommitted bytes and unavailable storage closes SSE', async () => {
  const { InvocationRecorder } = await import('../dist/capture.js');
  const f = await fixture(); let host, reader, database;
  try {
    host = await startObservationHost({ store: f.store });
    let shutdown = false;
    const recorder = new InvocationRecorder({ store: f.store, invocationId: f.invocation.id, requestShutdown: () => { shutdown = true; }, fallback: () => {} });
    const writer = await recorder.openCapture({ channel: 'stdout' });
    const after = f.store.readEvents({ after: '0' }).nextCursor;
    const response = await authorizedFetch(host, host.url + '/api/stream?after=' + after); reader = response.body.getReader();
    database = new DatabaseSync(join(f.repo.path, '.git', 'factory', 'history.sqlite'));
    database.exec("CREATE TRIGGER fail_capture BEFORE INSERT ON capture_chunks BEGIN SELECT RAISE(ABORT, 'fixture failure'); END");
    await writer.write('must never be displayed'); await assert.rejects(recorder.barrier(), /recording failed/); assert.equal(shutdown, true);
    const text = await frame(reader); assert.doesNotMatch(text, /must never be displayed/);
    const capture = await (await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id + '/captures/' + writer.id)).json(); assert.deepEqual(capture.chunks, []);
    await reader.cancel(); reader = undefined;
    const current = f.store.readEvents({ after: '0' }).nextCursor;
    const stream = await authorizedFetch(host, host.url + '/api/stream?after=' + current); reader = stream.body.getReader();
    f.store.close();
    assert.match(await frame(reader), /event: unavailable/);
    assert.equal((await authorizedFetch(host, host.url + '/api/events')).status, 503);
    await reader.cancel(); reader = undefined;
    await assert.rejects(host.close()); host = undefined;
  } finally { await reader?.cancel(); await host?.close(); database?.close(); try { f.dispose(); } catch { f.repo.dispose(); } }
});

test('shutdown destroys slow streams without a held SQLite read transaction and permits a replacement host', async () => {
  const f = await fixture(); let host, socket, database;
  try {
    // Populate committed bounded metadata directly as fixture setup, never as the tested read seam.
    database = new DatabaseSync(join(f.repo.path, '.git', 'factory', 'history.sqlite'));
    const insert = database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)');
    database.exec('BEGIN'); for (let i = 0; i < 1500; i++) insert.run('fixture.bulk', JSON.stringify({ text: 'x'.repeat(8000) })); database.exec('COMMIT');
    host = await startObservationHost({ store: f.store });
    socket = createConnection(new URL(host.url).port, '127.0.0.1'); await once(socket, 'connect');
    socket.write('GET /api/stream HTTP/1.1\r\nHost: ' + new URL(host.url).host + '\r\nAuthorization: Bearer ' + host.sessionToken + '\r\n\r\n'); socket.pause();
    await delay(150);
    database.exec('PRAGMA busy_timeout=100; BEGIN IMMEDIATE; COMMIT');
    const checkpoint = database.prepare('PRAGMA wal_checkpoint(TRUNCATE)').get(); assert.equal(checkpoint.busy, 0);
    const start = performance.now(); await host.close(); host = undefined;
    assert.ok(performance.now() - start < 2000);
    host = await startObservationHost({ store: f.store });
    assert.equal((await authorizedFetch(host, host.url + '/api/events?limit=1')).status, 200);
  } finally { socket?.destroy(); await host?.close(); database?.close(); f.dispose(); }
});

test('paused viewer is disconnected after bounded backpressure while ordinary reads remain responsive', async () => {
  const f = await fixture(); let host, socket, database;
  try {
    database = new DatabaseSync(join(f.repo.path, '.git', 'factory', 'history.sqlite'));
    const insert = database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)');
    database.exec('BEGIN'); for (let i = 0; i < 2000; i++) insert.run('fixture.bulk', JSON.stringify({ text: 'y'.repeat(8000) })); database.exec('COMMIT');
    host = await startObservationHost({ store: f.store });
    socket = createConnection(new URL(host.url).port, '127.0.0.1'); await once(socket, 'connect');
    socket.write('GET /api/stream HTTP/1.1\r\nHost: ' + new URL(host.url).host + '\r\nAuthorization: Bearer ' + host.sessionToken + '\r\n\r\n'); socket.pause();
    await delay(1500);
    assert.equal((await authorizedFetch(host, host.url + '/api/events?limit=1')).status, 200);
    const ended = once(socket, 'end'); socket.resume();
    await Promise.race([ended, delay(2000).then(() => { throw new Error('slow stream was not disconnected'); })]);
  } finally { socket?.destroy(); await host?.close(); database?.close(); f.dispose(); }
});

test('invocation, native session and attempt detail routes remain scoped saved reads', async () => {
  const f = await fixture(); let host;
  try {
    const attempt = await f.store.admitAttempt({ id: crypto.randomUUID(), invocationId: f.invocation.id, operationKey: 'fixture-agent', kind: 'agent', intent: 'initial' });
    const session = await f.store.saveSession(attempt.id, { nativeId: 'native-fixture', parentNativeId: null, lifecycle: 'running', usage: { tokens: 12, scope: 'self' }, loadedSkills: ['fixture-skill'] });
    host = await startObservationHost({ store: f.store });
    const saved = f.store.readEvents({ after: '0' }).nextCursor;
    const prefix = host.url + '/api/invocations/' + f.invocation.id;
    assert.equal((await (await authorizedFetch(host, prefix + '/attempts/' + attempt.id)).json()).operationKey, 'fixture-agent');
    assert.equal((await (await authorizedFetch(host, prefix + '/sessions/' + session.id)).json()).nativeId, 'native-fixture');
    const sessions = await (await authorizedFetch(host, prefix + '/sessions?limit=1')).json(); assert.equal(sessions.sessions.length, 1);
    assert.equal((await (await authorizedFetch(host, prefix + '/sessions?after=' + sessions.nextCursor)).json()).sessions.length, 0);
    const absent = crypto.randomUUID();
    assert.equal((await authorizedFetch(host, host.url + '/api/invocations/' + absent + '/sessions/' + session.id)).status, 404);
    assert.equal((await authorizedFetch(host, host.url + '/api/invocations/' + absent + '/attempts/' + attempt.id)).status, 404);
    const page = await (await authorizedFetch(host, host.url + '/api/invocations?limit=1')).json(); assert.equal(page.invocations[0].id, f.invocation.id);
    assert.equal((await (await authorizedFetch(host, host.url + '/api/invocations?after=' + page.nextCursor)).json()).invocations.length, 0);
    assert.equal(f.store.readEvents({ after: '0' }).nextCursor, saved);
  } finally { await host?.close(); f.dispose(); }
});

test('unpublished and unverifiable native claims remain for explicit clearance', async () => {
  const f = await fixture();
  try {
    const claim = await f.store.claimResource({ kind: 'dashboard', owner: { host: 'unknown-host', pid: process.pid, start: null } });
    await assert.rejects(startObservationHost({ store: f.store }), /unverified/);
    assert.equal(f.store.readDashboardClaim().id, claim.id);
    assert.equal(f.store.readDashboardClaim().endpoint, undefined);
  } finally { f.dispose(); }
});

test('untrusted identity responses are bounded and receive no claim or host credentials', async () => {
  const f = await fixture(); let host, saved;
  const requests = [];
  const fake = createServer((request, response) => { requests.push({ url: request.url, headers: request.headers }); response.end('z'.repeat(100000)); });
  fake.listen(0, '127.0.0.1'); await once(fake, 'listening');
  try {
    host = await startObservationHost({ store: f.store }); saved = f.store.readDashboardClaim(); await host.close(); host = undefined;
    const claim = await f.store.claimResource({ kind: 'dashboard', owner: saved.owner });
    await f.store.publishDashboardEndpoint({ claimId: claim.id, token: claim.token, url: 'http://127.0.0.1:' + fake.address().port, instanceId: 'untrusted-server' });
    const start = performance.now(); await assert.rejects(startObservationHost({ store: f.store }), /verification failed/); assert.ok(performance.now() - start < 2000);
    assert.equal(requests.length, 1); assert.equal(requests[0].headers.authorization, undefined);
    assert.ok(!JSON.stringify(requests).includes(claim.token)); assert.ok(!JSON.stringify(requests).includes(saved.token));
    assert.equal(f.store.readDashboardClaim().id, claim.id);
  } finally { await host?.close(); fake.closeAllConnections(); await new Promise(resolve => fake.close(resolve)); f.dispose(); }
});

test('shutdown retains the exact claim while an authorized notification write remains unsettled', async () => {
  const f = await fixture(); let host, release;
  let entered; const started = new Promise(resolve => { entered = resolve; });
  const pending = new Promise(resolve => { release = resolve; });
  try {
    host = await startObservationHost({ store: f.store, notificationWrite: async () => { entered(); await pending; return { saved: true }; } });
    const saved = f.store.readDashboardClaim();
    const writing = http(host.url, { path: '/api/notifications/preferences', method: 'POST', headers: { Origin: host.url, Authorization: 'Bearer ' + host.sessionToken, 'Content-Type': 'application/json' }, body: '{}' }).catch(() => {});
    await started;
    await assert.rejects(host.close(), /notification write/);
    assert.equal(f.store.readDashboardClaim().id, saved.id);
    release(); await writing; await delay(10);
    assert.equal(f.store.readDashboardClaim().id, saved.id);
    await host.close(); host = undefined;
    assert.equal(f.store.readDashboardClaim(), undefined);
  } finally { release?.(); await host?.close(); f.dispose(); }
});

test('large saved invocation inputs cannot block summary pagination or exceed detail response bounds', async () => {
  const f = await fixture(); let host;
  try {
    await f.store.saveInvocationMetadata(f.invocation.id, { fixtureInput: 'x'.repeat(1100000) });
    host = await startObservationHost({ store: f.store });
    const response = await authorizedFetch(host, host.url + '/api/invocations?limit=1'); const text = await response.text();
    assert.equal(response.status, 200); assert.ok(Buffer.byteLength(text) < 1048576);
    const page = JSON.parse(text); assert.equal(page.invocations[0]?.id, f.invocation.id); assert.equal(page.invocations[0].metadata, undefined);
    assert.ok(page.nextCursor > 0); assert.equal(page.hasMore, false);
    assert.equal((await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id)).status, 413);
  } finally { await host?.close(); f.dispose(); }
});

test('run pages stay grouped and each run retains its chronological invocation history', async () => {
  const f = await fixture(); let host;
  try {
    const second = await f.store.createRun();
    const firstPageRun = f.invocation.runId;
    const first = await f.store.readRunInvocations({ runId: firstPageRun, limit: 1 });
    assert.equal(first.invocations[0].id, f.invocation.id);
    await f.store.finalizeInvocation({ id: f.invocation.id, outcome: 'succeeded', cleanup: 'complete', claimId: f.invocation.claim.id, token: f.invocation.claim.token });
    const followup = await f.store.startInvocation({ runId: firstPageRun, worktreeId: f.invocation.worktreeId, owner: { host: 'fixture', pid: process.pid, start: null } });
    host = await startObservationHost({ store: f.store });
    const page = await (await authorizedFetch(host, host.url + '/api/runs?limit=1')).json();
    assert.equal(page.runs.length, 1);
    assert.equal(page.runs[0].id, second.id);
    const next = await (await authorizedFetch(host, host.url + '/api/runs?limit=1&after=' + page.nextCursor)).json();
    assert.equal(next.runs[0].id, firstPageRun);
    assert.equal(next.runs[0].latestInvocation.id, followup.id);
    const history = await (await authorizedFetch(host, host.url + '/api/runs/' + firstPageRun + '/invocations?limit=1')).json();
    assert.equal(history.invocations[0].id, f.invocation.id);
    assert.equal(history.hasMore, true);
    const later = await (await authorizedFetch(host, host.url + '/api/runs/' + firstPageRun + '/invocations?limit=1&after=' + history.nextCursor)).json();
    assert.equal(later.invocations[0].id, followup.id);
    assert.equal(later.hasMore, false);
  } finally { await host?.close(); f.dispose(); }
});

test('owner handoff is one-use, short lived, same-origin and never a public GET credential', async () => {
  const f = await fixture(); let host;
  try {
    host = await startObservationHost({ store: f.store });
    const handoff = host.createUiHandoff();
    assert.match(handoff, /^http:\/\/127\.0\.0\.1:\d+\/#handoff=[0-9a-f-]+$/);
    const ticket = new URL(handoff).hash.slice('#handoff='.length);
    for (const path of ['/', '/assets/app.js', '/assets/style.css']) {
      const response = await fetch(host.url + path);
      assert.equal(response.status, 200, path);
      assert.ok(!(await response.text()).includes(host.sessionToken));
    }
    assert.equal((await http(host.url, { path: '/assets/../dashboard.js', headers: { Authorization: 'Bearer ' + host.sessionToken } })).status, 400);
    assert.equal((await http(host.url, { path: '/', headers: { Host: 'evil.invalid' } })).status, 403);
    assert.equal((await fetch(host.url + '/api/runs')).status, 403);
    const body = JSON.stringify({ ticket });
    const foreign = await fetch(host.url + '/api/ui-session', { method: 'POST', headers: { Origin: 'http://evil.invalid', 'Content-Type': 'application/json' }, body });
    assert.equal(foreign.status, 403);
    const redeemed = await fetch(host.url + '/api/ui-session', { method: 'POST', headers: { Origin: host.url, 'Content-Type': 'application/json' }, body });
    assert.equal(redeemed.status, 200);
    assert.equal((await redeemed.json()).sessionToken, host.sessionToken);
    const replay = await fetch(host.url + '/api/ui-session', { method: 'POST', headers: { Origin: host.url, 'Content-Type': 'application/json' }, body });
    assert.equal(replay.status, 403);
    assert.equal((await fetch(host.url + '/api/identity?challenge=' + crypto.randomUUID())).status, 200);
    assert.equal((await fetch(host.url + '/api/runs?ticket=' + ticket)).status, 403);
  } finally { await host?.close(); f.dispose(); }
});

test('selected invocation event pages include its saved attempt and capture lifecycle only', async () => {
  const f = await fixture(); let host;
  try {
    const attempt = await f.store.admitAttempt({ id: crypto.randomUUID(), invocationId: f.invocation.id, operationKey: 'fixture-step', kind: 'agent', intent: 'initial' });
    await f.store.markStarted({ id: attempt.id, owner: { host: 'fixture', pid: process.pid, start: null } });
    await f.store.settleAttempt({ id: attempt.id, launch: 'started', outcome: 'succeeded', quiescent: true, evidence: 'fixture complete' });
    const capture = await f.store.createCapture({ invocationId: f.invocation.id, attemptId: attempt.id, channel: 'stdout' });
    await f.store.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: 'saved output' }], state: 'complete' });
    host = await startObservationHost({ store: f.store });
    const url = host.url + '/api/invocations/' + f.invocation.id + '/events?limit=2';
    const first = await (await authorizedFetch(host, url)).json();
    assert.equal(first.events.length, 2);
    assert.equal(first.events.every(event => event.data.invocationId === f.invocation.id), true);
    let after = first.nextCursor, names = first.events.map(event => event.kind);
    while (true) {
      const page = await (await authorizedFetch(host, url + '&after=' + after)).json();
      names.push(...page.events.map(event => event.kind));
      if (!page.hasMore) break;
      after = page.nextCursor;
    }
    assert.ok(names.includes('attempt.started'));
    assert.ok(names.includes('attempt.settled'));
    assert.ok(names.includes('capture.appended'));
    assert.ok(!names.includes('dashboard.published'));
    const tail = await (await authorizedFetch(host, url + '&tail=1')).json();
    assert.equal(tail.events.at(-1).kind, 'capture.appended');
    assert.equal(tail.hasEarlier, true);
    const head = await (await authorizedFetch(host, host.url + '/api/events/head')).json();
    assert.ok(BigInt(head.cursor) >= BigInt(tail.nextCursor));
    for (const path of ['/api/events/head', '/api/runs', '/api/runs/' + f.invocation.runId, '/api/runs/' + f.invocation.runId + '/invocations', '/api/invocations/' + f.invocation.id + '/events']) {
      assert.equal((await fetch(host.url + path)).status, 403, path);
    }
  } finally { await host?.close(); f.dispose(); }
});

test('older schema is refused without mutation until explicit forward maintenance', async () => {
  const repo = createRepository();
  const path = join(repo.path, '.git', 'factory', 'history.sqlite');
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  const run = await store.createRun(); store.close();
  const database = new DatabaseSync(path); database.exec('PRAGMA user_version=3'); database.close();
  try {
    assert.throws(() => openRepositoryStore(join(repo.path, '.git')), /incompatible schema/);
    const retained = new DatabaseSync(path);
    try { assert.equal(retained.prepare('PRAGMA user_version').get().user_version, 3); assert.equal(retained.prepare('SELECT id FROM runs').get().id, run.id); }
    finally { retained.close(); }
  } finally { repo.dispose(); }
});

test('version 5 notification store is refused without creating metadata tables', async () => {
  const repo = createRepository();
  const common = join(repo.path, '.git'), path = join(common, 'factory', 'history.sqlite');
  const store = await initializeRepositoryStore(common, { release: 'fixture' });
  const run = await store.createRun(); store.close();
  const database = new DatabaseSync(path);
  database.exec('DROP TABLE notification_acknowledgments; DROP TABLE notification_preferences; PRAGMA user_version=5'); database.close();
  try {
    assert.throws(() => openRepositoryStore(common), /incompatible schema/);
    const retained = new DatabaseSync(path);
    try {
      assert.equal(retained.prepare('PRAGMA user_version').get().user_version, 5);
      assert.equal(retained.prepare('SELECT id FROM runs').get().id, run.id);
      assert.equal(retained.prepare("SELECT count(*) AS count FROM sqlite_schema WHERE name LIKE 'notification_%' AND type='table'").get().count, 1);
    } finally { retained.close(); }
  } finally { repo.dispose(); }
});

test('operator confirmation appears beside the original outcome and cleanup uncertainty', async () => {
  const f = await fixture(); let host;
  try {
    await f.store.finishInvocation(f.invocation.id, 'interrupted', 'unknown');
    const clearance = await f.store.clearOwner({ claimId: f.invocation.claim.id, token: f.invocation.claim.token,
      operatorConfirmed: true, note: 'children checked by operator', inspection: 'unknown' });
    host = await startObservationHost({ store: f.store });
    const history = await (await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id)).json();
    assert.equal(history.invocation.outcome, 'interrupted');
    assert.equal(history.invocation.cleanup, 'unknown');
    assert.equal(history.clearance?.id, clearance.id);
    assert.equal(history.clearance?.basis, 'operator_confirmed');
    assert.equal(history.clearance?.note, 'children checked by operator');
    const runs = await (await authorizedFetch(host, host.url + '/api/runs')).json();
    assert.equal(runs.runs[0].clearance?.id, clearance.id);
  } finally { await host?.close(); f.dispose(); }
});

test('history previews stay responsive with one hundred megabytes of saved capture text', async () => {
  const f = await fixture(); let host, database;
  try {
    database = new DatabaseSync(join(f.repo.path, '.git', 'factory', 'history.sqlite'));
    const capture = database.prepare('INSERT INTO captures(id,invocation_id,attempt_id,channel,state,sequence) VALUES (?,?,NULL,?,?,16)');
    const chunk = database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)');
    const payload = 'x'.repeat(65536);
    let firstCaptureId;
    database.exec('BEGIN');
    for (let index = 0; index < 100; index++) {
      const id = crypto.randomUUID();
      if (index === 0) firstCaptureId = id;
      capture.run(id, f.invocation.id, 'stdout', 'complete');
      for (let sequence = 1; sequence <= 16; sequence++) chunk.run(id, sequence, payload);
    }
    database.exec('COMMIT');
    host = await startObservationHost({ store: f.store });
    const elapsed = [];
    let response;
    for (let sample = 0; sample < 3; sample++) {
      const started = performance.now();
      response = await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id + '?limit=100');
      elapsed.push(performance.now() - started);
      if (sample < 2) await response.arrayBuffer();
    }
    assert.equal(response.status, 200);
    const history = await response.json();
    assert.equal(history.captures.length, 100);
    assert.equal(history.hasMoreCaptures, false);
    assert.equal(history.captures[0].state, 'complete');
    assert.equal(history.captures[0].hasMore, true);
    assert.equal(history.captures.at(-1).chunks.length, 0);
    assert.equal(history.captures.at(-1).hasMore, true);
    const detailElapsed = [];
    for (let sample = 0; sample < 3; sample++) {
      const started = performance.now();
      const detail = await authorizedFetch(host, host.url + '/api/invocations/' + f.invocation.id + '/captures/' + firstCaptureId);
      await detail.arrayBuffer();
      detailElapsed.push(performance.now() - started);
    }
    const median = elapsed.sort((a, b) => a - b)[1];
    const detailMedian = detailElapsed.sort((a, b) => a - b)[1];
    assert.ok(median < detailMedian * 4 + 10, `history ${median.toFixed(0)} ms versus one capture ${detailMedian.toFixed(0)} ms for 100 MiB saved text`);
  } finally { await host?.close(); database?.close(); f.dispose(); }
});
