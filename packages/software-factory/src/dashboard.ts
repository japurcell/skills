import { createHmac, randomUUID, timingSafeEqual } from 'node:crypto';
import { createServer } from 'node:http';
import type { IncomingMessage, ServerResponse } from 'node:http';
import { currentOwner, inspectOwner } from './native/process.js';
import type { Claim, RepositoryStore } from './store.js';

const MAX_PAGE = 1048576;
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
  return { url: endpoint.origin, reused: true as const, close: async () => {} };
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
  const streams = new Set<ServerResponse>();
  const server = createServer({ maxHeaderSize: 8192, highWaterMark: 16384 }, (request, response) => { void handle(request, response); });
  async function handle(request: IncomingMessage, response: ServerResponse) {
    response.setHeader('cache-control', 'no-store');
    response.setHeader('x-content-type-options', 'nosniff');
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
      if (request.method !== 'GET') {
        if (request.method !== 'POST' || !['/api/notifications/preferences', '/api/notifications/acknowledgments'].includes(route.pathname)) { json(response, 405, { error: 'read only' }); return; }
        parameters(route, []);
        const credential = Buffer.from(request.headers.authorization ?? '');
        const expected = Buffer.from('Bearer ' + sessionToken);
        if (request.headers.origin !== url || credential.length !== expected.length || !timingSafeEqual(credential, expected)) { json(response, 403, { error: 'host session required' }); return; }
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
      if (route.pathname === '/api/events') {
        parameters(route, ['after', 'limit']);
        const after = cursor(route.searchParams.get('after') ?? '0'), limit = integer(route, 'limit', 200, 200);
        if (limit < 1) throw new RequestError(400, 'invalid event limit');
        json(response, 200, store.readEvents({ after, limit })); return;
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
        if (kind === 'sessions') { json(response, 200, detail ? store.readSession({ invocationId: id, id: detail }) : store.readSessions({ invocationId: id, after: integer(route, 'after', 0), limit })); return; }
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
  } catch (error) {
    await stopServer();
    if (sameClaim(store.readDashboardClaim(), claim)) await store.releaseClaim({ claimId: claim.id, token: claim.token, basis: 'quiescent' });
    throw error;
  }
  let closeTask: Promise<void> | undefined;
  return { url, reused: false as const, sessionToken, close: () => closeTask ??= (async () => {
    await stopServer();
    if (sameClaim(store.readDashboardClaim(), claim)) await store.releaseClaim({ claimId: claim.id, token: claim.token, basis: 'quiescent' });
  })().catch(error => { closeTask = undefined; throw error; }) };
}
