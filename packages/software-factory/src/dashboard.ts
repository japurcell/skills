import { createHash, createHmac, randomUUID, timingSafeEqual } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import type { IncomingMessage, ServerResponse } from 'node:http';
import { currentOwner, inspectOwner } from './native/process.js';
import type { Claim, RepositoryStore } from './store.js';

const MAX_PAGE = 1048576;
const liveHosts = new Map<string, { claim: Claim; sessionToken: string; available: () => boolean; handoff: () => string }>();
class RequestError extends Error { constructor(readonly status: number, message: string) { super(message); } }
function parameters(route: URL, allowed: string[]) {
  for (const key of route.searchParams.keys()) if (!allowed.includes(key) || route.searchParams.getAll(key).length !== 1) throw new RequestError(400, 'invalid query');
}
function integer(route: URL, key: string, fallback: number, maximum = Number.MAX_SAFE_INTEGER) {
  const value = route.searchParams.get(key);
  if (value === null) return fallback;
  if (!/^(0|[1-9][0-9]{0,15})$/.test(value) || !Number.isSafeInteger(Number(value)) || Number(value) > maximum) throw new RequestError(400, 'invalid page');
  return Number(value);
}
function cursor(value: string) {
  if (!/^(0|[1-9][0-9]{0,18})$/.test(value) || BigInt(value) > 9223372036854775807n) throw new RequestError(400, 'invalid event cursor');
  return value;
}
export type NotificationWrite = (operation: 'preferences' | 'acknowledgments', body: unknown) => Promise<unknown>;
function proof(claim: Claim, challenge: string) {
  return createHmac('sha256', claim.token).update(JSON.stringify([claim.resourceKey, claim.id, claim.owner, claim.endpoint, challenge])).digest('hex');
}
function sameClaim(a: Claim | undefined, b: Claim) {
  return a?.id === b.id && a.token === b.token && a.kind === 'dashboard' && a.resourceKey === b.resourceKey
    && JSON.stringify(a.owner) === JSON.stringify(b.owner) && JSON.stringify(a.endpoint) === JSON.stringify(b.endpoint);
}
function bearerMatches(request: IncomingMessage, token: string) {
  const credential = Buffer.from(request.headers.authorization ?? '');
  const expected = Buffer.from('Bearer ' + token);
  return credential.length === expected.length && timingSafeEqual(credential, expected);
}
function json(response: ServerResponse, status: number, value: unknown) {
  const body = JSON.stringify(value);
  if (Buffer.byteLength(body) > MAX_PAGE) { response.writeHead(413); response.end(); return; }
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8' }); response.end(body);
}
async function verifyExisting(store: RepositoryStore, claim: Claim) {
  if (claim.resourceKey !== store.repositoryId() || !claim.endpoint || inspectOwner(claim.owner).state !== 'known_live') throw new Error('dashboard owner is unverified; explicit clearance required');
  const endpoint = new URL(claim.endpoint.url);
  if (endpoint.origin !== claim.endpoint.url || endpoint.protocol !== 'http:' || endpoint.hostname !== '127.0.0.1' || !endpoint.port) throw new Error('dashboard endpoint is not loopback');
  const challenge = randomUUID();
  try {
    const response = await fetch(endpoint.origin + '/api/identity?challenge=' + challenge, { signal: AbortSignal.timeout(1000), redirect: 'error' });
    if (!response.ok || !response.body) throw new Error('unverified response');
    const reader = response.body.getReader();
    const chunks: Uint8Array[] = []; let size = 0;
    try {
      while (true) {
        const item = await reader.read(); if (item.done) break;
        size += item.value.byteLength;
        if (size > 4096) throw new Error('unverified response');
        chunks.push(item.value);
      }
    } finally { await reader.cancel(); }
    const identity = JSON.parse(Buffer.concat(chunks).toString('utf8')) as { proof?: string };
    if (identity.proof !== proof(claim, challenge) || !sameClaim(store.readDashboardClaim(), claim)) throw new Error('claim changed');
  } catch { throw new Error('dashboard endpoint verification failed; explicit clearance required'); }
  const local = liveHosts.get(claim.id);
  const sessionToken = local?.available() && sameClaim(local.claim, claim) ? local.sessionToken : undefined;
  return { url: endpoint.origin, reused: true as const, sessionToken, readCredentialAvailable: sessionToken !== undefined,
    createUiHandoff: sessionToken === undefined ? undefined : local?.handoff, close: async () => {} };
}

/** Owns only observation sockets. It never imports or executes a workflow. */
export async function startObservationHost(options: { store: RepositoryStore; port?: number; notificationWrite?: NotificationWrite }) {
  const { store } = options;
  const existing = store.readDashboardClaim();
  if (existing) return verifyExisting(store, existing);
  if (options.port !== undefined && (!Number.isSafeInteger(options.port) || options.port < 0 || options.port > 65535)) throw new Error('invalid port');
  let claim = await store.claimResource({ kind: 'dashboard', owner: currentOwner() });
  const sessionToken = randomUUID() + randomUUID();
  let url = '', closing = false, notificationWrites = 0;
  const uiTickets = new Map<string, number>();
  let badRedemptions = 0;
  const assets = new Map([
    ['/', { file: new URL('./web/index.html', import.meta.url), type: 'text/html; charset=utf-8' }],
    ['/assets/app.js', { file: new URL('./web/app.js', import.meta.url), type: 'text/javascript; charset=utf-8' }],
    ['/assets/style.css', { file: new URL('./web/style.css', import.meta.url), type: 'text/css; charset=utf-8' }],
  ]);
  function createUiHandoff() {
    if (closing || !server.listening || !sameClaim(store.readDashboardClaim(), claim)) throw new Error('dashboard host unavailable');
    for (const [ticket, deadline] of uiTickets) if (deadline < Date.now()) uiTickets.delete(ticket);
    if (uiTickets.size >= 8 || badRedemptions >= 32) throw new Error('UI handoff limit reached');
    const ticket = randomUUID() + randomUUID();
    uiTickets.set(ticket, Date.now() + 60000);
    return url + '/#handoff=' + ticket;
  }
  const streams = new Set<ServerResponse>();
  const server = createServer({ maxHeaderSize: 8192, highWaterMark: 16384 }, (request, response) => { void handle(request, response); });
  async function handle(request: IncomingMessage, response: ServerResponse) {
    response.setHeader('cache-control', 'no-store');
    response.setHeader('x-content-type-options', 'nosniff');
    response.setHeader('referrer-policy', 'no-referrer');
    response.setHeader('x-frame-options', 'DENY');
    response.setHeader('content-security-policy', "default-src 'none'; frame-ancestors 'none'");
    try {
      if (closing || !sameClaim(store.readDashboardClaim(), claim)) { json(response, 503, { error: 'host claim unavailable' }); return; }
      for (const name of ['host', 'origin', 'referer', 'authorization', 'last-event-id']) {
        let count = 0;
        for (let index = 0; index < request.rawHeaders.length; index += 2) if (request.rawHeaders[index]?.toLowerCase() === name) count++;
        if (count > 1) throw new RequestError(400, 'duplicate authority header');
      }
      let refererOrigin: string | undefined;
      if (request.headers.referer !== undefined) {
        try { refererOrigin = new URL(request.headers.referer).origin; } catch { throw new RequestError(403, 'origin denied'); }
      }
      if (request.headers.host !== new URL(url).host || (request.headers.origin !== undefined && request.headers.origin !== url)
        || (refererOrigin !== undefined && refererOrigin !== url)
        || ['cross-site', 'same-site'].includes(String(request.headers['sec-fetch-site']))) { json(response, 403, { error: 'origin denied' }); return; }
      const raw = request.url ?? '';
      if (!raw.startsWith('/') || raw.startsWith('//') || raw.includes('%') || raw.includes('#') || raw.includes('\\') || raw.includes('/..')) { json(response, 400, { error: 'invalid path' }); return; }
      const route = new URL(raw, url);
      if (request.method === 'POST' && route.pathname === '/api/ui-session') {
        parameters(route, []);
        if (request.headers.origin !== url || request.headers['content-type'] !== 'application/json' || badRedemptions >= 32) {
          json(response, 403, { error: 'UI handoff denied' }); return;
        }
        const chunks: Buffer[] = []; let size = 0;
        for await (const chunk of request) {
          const bytes = Buffer.from(chunk as Uint8Array); size += bytes.length;
          if (size > 512) throw new RequestError(413, 'UI handoff exceeds limit');
          chunks.push(bytes);
        }
        let ticket: unknown;
        try { ticket = (JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(chunks))) as { ticket?: unknown }).ticket; }
        catch { throw new RequestError(400, 'invalid UI handoff'); }
        for (const [key, deadline] of uiTickets) if (deadline < Date.now()) uiTickets.delete(key);
        const deadline = typeof ticket === 'string' ? uiTickets.get(ticket) : undefined;
        if (deadline === undefined) { badRedemptions++; json(response, 403, { error: 'UI handoff denied' }); return; }
        uiTickets.delete(ticket as string);
        if (closing || Date.now() > deadline) { badRedemptions++; json(response, 403, { error: 'UI handoff denied' }); return; }
        json(response, 200, { sessionToken }); return;
      }
      if (request.method !== 'GET') {
        if (request.method !== 'POST' || !['/api/notifications/preferences', '/api/notifications/acknowledgments'].includes(route.pathname)) { json(response, 405, { error: 'read only' }); return; }
        parameters(route, []);
        if (request.headers.origin !== url || !bearerMatches(request, sessionToken)) { json(response, 403, { error: 'host session required' }); return; }
        if (request.headers['content-type'] !== 'application/json') throw new RequestError(415, 'JSON required');
        if (!options.notificationWrite) { json(response, 501, { error: 'notification writes unavailable' }); return; }
        const chunks: Buffer[] = []; let size = 0;
        for await (const chunk of request) { const bytes = Buffer.from(chunk as Uint8Array); size += bytes.length; if (size > 8192) throw new RequestError(413, 'notification request exceeds limit'); chunks.push(bytes); }
        let input: unknown;
        try { input = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(chunks))); } catch { throw new RequestError(400, 'invalid JSON'); }
        if (closing || !sameClaim(store.readDashboardClaim(), claim)) throw new RequestError(503, 'host claim unavailable');
        const operation = route.pathname.endsWith('preferences') ? 'preferences' : 'acknowledgments';
        if (notificationWrites >= 4) throw new RequestError(429, 'notification write limit reached');
        notificationWrites++;
        try {
          const saved = await options.notificationWrite(operation, input);
          if (!closing && !response.destroyed) json(response, 200, saved);
        } finally { notificationWrites--; }
        return;
      }
      if (route.pathname === '/api/identity' && /^[0-9a-f-]{36}$/.test(route.searchParams.get('challenge') ?? '')) {
        parameters(route, ['challenge']);
        json(response, 200, { repositoryId: claim.resourceKey, claimId: claim.id, instanceId: claim.endpoint?.instanceId, proof: proof(claim, route.searchParams.get('challenge')!) }); return;
      }
      const asset = assets.get(route.pathname);
      if (asset) {
        parameters(route, []);
        const body = readFileSync(asset.file);
        if (body.byteLength > MAX_PAGE) throw new RequestError(413, 'asset exceeds limit');
        if (route.pathname === '/') {
          const inline = /<script>([\s\S]*?)<\/script>/.exec(body.toString('utf8'))?.[1];
          if (!inline) throw new Error('UI bootstrap missing');
          const hash = createHash('sha256').update(inline).digest('base64');
          response.setHeader('content-security-policy', `default-src 'none'; script-src 'self' 'sha256-${hash}'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`);
        } else response.setHeader('content-security-policy', "default-src 'none'; frame-ancestors 'none'");
        response.writeHead(200, { 'content-type': asset.type }); response.end(body); return;
      }
      if ((route.pathname === '/api/events' || route.pathname === '/api/events/head' || route.pathname === '/api/stream' || route.pathname === '/api/invocations'
        || route.pathname.startsWith('/api/invocations/') || route.pathname === '/api/runs' || route.pathname.startsWith('/api/runs/')) && !bearerMatches(request, sessionToken)) {
        json(response, 403, { error: 'host session required' }); return;
      }
      if (route.pathname === '/api/events') {
        parameters(route, ['after', 'limit']);
        const after = cursor(route.searchParams.get('after') ?? '0'), limit = integer(route, 'limit', 200, 200);
        if (limit < 1) throw new RequestError(400, 'invalid event limit');
        json(response, 200, store.readEvents({ after, limit })); return;
      }
      if (route.pathname === '/api/events/head') {
        parameters(route, []); json(response, 200, store.readEventHead()); return;
      }
      if (route.pathname === '/api/stream') {
        parameters(route, ['after']);
        const last = request.headers['last-event-id'];
        if (Array.isArray(last) || (last !== undefined && route.searchParams.has('after'))) throw new RequestError(400, 'ambiguous cursor');
        const after = cursor(last ?? route.searchParams.get('after') ?? '0');
        stream(response, after); return;
      }
      if (route.pathname === '/api/invocations') {
        parameters(route, ['after', 'limit']);
        const limit = integer(route, 'limit', 30, 100); if (limit < 1) throw new RequestError(400, 'invalid page');
        json(response, 200, store.readInvocations({ after: integer(route, 'after', 0), limit })); return;
      }
      if (route.pathname === '/api/runs') {
        parameters(route, ['after', 'limit']);
        const limit = integer(route, 'limit', 30, 30); if (limit < 1) throw new RequestError(400, 'invalid page');
        json(response, 200, store.readRuns({ after: integer(route, 'after', 0), limit })); return;
      }
      const runDetail = /^\/api\/runs\/([0-9a-f-]{36})$/.exec(route.pathname);
      if (runDetail) { parameters(route, []); json(response, 200, store.readRunSummary(runDetail[1]!)); return; }
      const runMatch = /^\/api\/runs\/([0-9a-f-]{36})\/invocations$/.exec(route.pathname);
      if (runMatch) {
        parameters(route, ['after', 'limit']);
        const limit = integer(route, 'limit', 30, 100); if (limit < 1) throw new RequestError(400, 'invalid page');
        json(response, 200, store.readRunInvocations({ runId: runMatch[1]!, after: integer(route, 'after', 0), limit })); return;
      }
      const invocationEvents = /^\/api\/invocations\/([0-9a-f-]{36})\/events$/.exec(route.pathname);
      if (invocationEvents) {
        parameters(route, ['after', 'before', 'tail', 'limit']);
        const limit = integer(route, 'limit', 200, 200); if (limit < 1) throw new RequestError(400, 'invalid event limit');
        const after = route.searchParams.get('after'), before = route.searchParams.get('before'), tail = route.searchParams.get('tail');
        if ((tail !== null && tail !== '1') || (after !== null && (before !== null || tail !== null)) || (before !== null && tail !== null)) throw new RequestError(400, 'ambiguous event window');
        json(response, 200, store.readInvocationEvents({ invocationId: invocationEvents[1]!, ...(after === null ? {} : { after: cursor(after) }),
          ...(before === null ? {} : { before: cursor(before) }), ...(tail === null ? {} : { tail: true }), limit })); return;
      }
      const selectedEvent = /^\/api\/invocations\/([0-9a-f-]{36})\/events\/([0-9]+)$/.exec(route.pathname);
      if (selectedEvent) {
        parameters(route, []);
        try { json(response, 200, store.readSelectedEvent({ invocationId: selectedEvent[1]!, cursor: cursor(selectedEvent[2]!) })); }
        catch (error) { if (error instanceof Error && error.message === 'saved event not found') throw new RequestError(404, 'saved event unavailable or pruned'); throw error; }
        return;
      }
      const selectedAttempts = /^\/api\/invocations\/([0-9a-f-]{36})\/attempt-page$/.exec(route.pathname);
      if (selectedAttempts) {
        parameters(route, ['attempt', 'phase']);
        const attemptId=route.searchParams.get('attempt'), phase=route.searchParams.get('phase');
        if ((!attemptId && !phase) || (attemptId !== null && !/^[0-9a-f-]{36}$/.test(attemptId)) || (phase !== null && (phase.length < 1 || phase.length > 256))) throw new RequestError(400, 'invalid saved target');
        try { json(response, 200, store.readAttemptPage({ invocationId: selectedAttempts[1]!, ...(attemptId === null ? {} : { attemptId }), ...(phase === null ? {} : { phase }) })); }
        catch (error) { if (error instanceof Error && ['saved attempt or phase not found','attempt does not belong to phase'].includes(error.message)) throw new RequestError(404, error.message); throw error; }
        return;
      }
      const savedQuestion = /^\/api\/invocations\/([0-9a-f-]{36})\/question$/.exec(route.pathname);
      if (savedQuestion) { parameters(route, []); json(response, 200, store.readSavedQuestion(savedQuestion[1]!)); return; }
      const match = /^\/api\/invocations\/([0-9a-f-]{36})(?:\/(sessions|attempts|captures)(?:\/([0-9a-f-]{36}))?)?$/.exec(route.pathname);
      if (match) {
        const id = match[1]!, kind = match[2], detail = match[3];
        if (!kind) {
          parameters(route, ['afterAttempt', 'afterCapture', 'limit']);
          const limit = integer(route, 'limit', 50, 100); if (limit < 1) throw new RequestError(400, 'invalid page');
          json(response, 200, store.readHistory(id, { afterAttempt: integer(route, 'afterAttempt', 0), afterCapture: integer(route, 'afterCapture', 0), limit })); return;
        }
        parameters(route, detail && kind !== 'captures' ? [] : ['after', 'limit']);
        const limit = integer(route, 'limit', 50, 200); if (limit < 1) throw new RequestError(400, 'invalid page');
        if (kind === 'sessions') {
          if (detail) {
            try { json(response, 200, store.readSession({ invocationId: id, id: detail })); }
            catch (error) { if (error instanceof Error && error.message === 'session not found') throw new RequestError(404, 'native session unavailable'); throw error; }
          } else json(response, 200, store.readSessions({ invocationId: id, after: integer(route, 'after', 0), limit }));
          return;
        }
        if (detail && kind === 'captures') { json(response, 200, store.readInvocationCapture({ invocationId: id, id: detail, after: integer(route, 'after', 0), limit })); return; }
        if (detail && kind === 'attempts') {
          const attempt = store.readAttempt(detail);
          if (attempt.invocationId !== id) throw new RequestError(404, 'attempt not found');
          json(response, 200, attempt); return;
        }
      }
      json(response, 404, { error: 'not found' });
    } catch (error) {
      if (response.headersSent) response.destroy();
      else json(response, error instanceof RequestError ? error.status : 503, { error: error instanceof RequestError ? error.message : 'observation unavailable' });
    }
  }
  function stream(response: ServerResponse, initial: string) {
    if (streams.size >= 16) { json(response, 429, { error: 'viewer limit reached' }); return; }
    // Materialize and release the SQLite statement before any response or wait.
    let first: ReturnType<RepositoryStore['readEvents']> | undefined = store.readEvents({ after: initial, limit: 100 });
    streams.add(response);
    response.writeHead(200, { 'content-type': 'text/event-stream; charset=utf-8', 'connection': 'keep-alive' }); response.flushHeaders();
    let after = initial, timer: ReturnType<typeof setTimeout> | undefined, blocked: ReturnType<typeof setTimeout> | undefined;
    let heartbeat = performance.now();
    const clean = () => { if (timer) clearTimeout(timer); if (blocked) clearTimeout(blocked); response.off('drain', drained); streams.delete(response); };
    const drained = () => { if (blocked) clearTimeout(blocked); blocked = undefined; pump(); };
    response.once('close', clean); response.on('error', clean);
    function send(text: string) {
      if (response.destroyed) return false;
      if (response.writableLength + Buffer.byteLength(text) > MAX_PAGE) { response.destroy(); return false; }
      if (!response.write(text)) {
        blocked = setTimeout(() => response.destroy(), 1000);
        response.once('drain', drained); return false;
      }
      return true;
    }
    function pump() {
      if (response.destroyed || closing) return;
      try {
        if (!sameClaim(store.readDashboardClaim(), claim)) throw new Error('claim lost');
        const page = first ?? store.readEvents({ after, limit: 100 }); first = undefined;
        if (page.gap) { send('event: gap\ndata: ' + JSON.stringify({ after, snapshot: '/api/invocations' }) + '\n\n'); response.end(); return; }
        for (const event of page.events) {
          after = event.cursor;
          if (!send('id: ' + event.cursor + '\nevent: observation\ndata: ' + JSON.stringify(event) + '\n\n')) return;
        }
        if (performance.now() - heartbeat > 15000) { heartbeat = performance.now(); if (!send(': heartbeat\n\n')) return; }
        timer = setTimeout(pump, page.events.length ? 0 : 100);
      } catch { send('event: unavailable\ndata: {"resynchronize":true}\n\n'); response.end(); }
    }
    pump();
  }
  server.maxConnections = 32; server.headersTimeout = 5000; server.requestTimeout = 5000; server.keepAliveTimeout = 1000;
  async function stopServer() {
    closing = true;
    uiTickets.clear();
    if (liveHosts.get(claim.id)?.sessionToken === sessionToken) liveHosts.delete(claim.id);
    for (const response of streams) response.destroy();
    const stopped = new Promise<void>(resolve => server.close(() => resolve()));
    server.closeAllConnections();
    await stopped;
    if (notificationWrites) throw new Error('notification write remains unsettled; dashboard claim retained');
  }
  try {
    await new Promise<void>((resolve, reject) => {
      server.once('error', reject);
      server.listen(options.port ?? 0, '127.0.0.1', () => { server.off('error', reject); resolve(); });
    });
    const address = server.address();
    if (!address || typeof address === 'string') throw new Error('loopback bind unavailable');
    url = 'http://127.0.0.1:' + address.port;
    claim = await store.publishDashboardEndpoint({ claimId: claim.id, token: claim.token, url, instanceId: randomUUID() });
    liveHosts.set(claim.id, { claim, sessionToken, available: () => !closing && server.listening, handoff: createUiHandoff });
  } catch (error) {
    await stopServer();
    if (sameClaim(store.readDashboardClaim(), claim)) await store.releaseClaim({ claimId: claim.id, token: claim.token, basis: 'quiescent' });
    throw error;
  }
  let closeTask: Promise<void> | undefined;
  return { url, reused: false as const, sessionToken, readCredentialAvailable: true as const, createUiHandoff, close: () => closeTask ??= (async () => {
    await stopServer();
    if (sameClaim(store.readDashboardClaim(), claim)) await store.releaseClaim({ claimId: claim.id, token: claim.token, basis: 'quiescent' });
  })().catch(error => { closeTask = undefined; throw error; }) };
}
