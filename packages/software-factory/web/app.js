const app = document.getElementById('app');
const connection = document.getElementById('connection');
const announcement = document.getElementById('announcement');
const state = {
  token: null, cursor: '0', connected: false, lastUpdate: null, frozen: false, pending: 0, gap: false,
  runPage: [0], runs: [], runPageNext: 0, runsHaveMore: false, query: '', filter: 'all', newRuns: 0,
  run: null, invocation: null, invocationPage: [0], invocationList: [], invocationNext: 0, invocationMore: false,
  attempts: [], captures: [], attemptsNext: 0, capturesNext: 0, attemptsMore: false, capturesMore: false,
  attemptPage: [0], captureSummaryPage: [0], sessionPage: [0],
  sessions: [], sessionsNext: 0, sessionsMore: false, lanePage: 0, collapsed: new Set(),
  events: [], earlier: false, selectedCapture: null, capturePage: null, captureAfter: 0, streamAbort: null,
  routeGeneration: 0, error: null,
};
const idPattern = /^[0-9a-f-]{36}$/;
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[char]);
const short = value => String(value ?? '').slice(0, 8);
const asText = value => value === null || value === undefined ? 'Unknown' : String(value);
const readableTime = value => { const time = Date.parse(value || ''); return Number.isFinite(time) ? new Date(time).toLocaleString() : 'Time unavailable'; };
function outcome(invocation) {
  if (!invocation) return ['No invocation', 'attention'];
  if (invocation.stage !== 'finalized') return [{ starting:'Preparing', running:'Running', shutting_down:'Stopping' }[invocation.stage] || 'Outcome unknown', 'attention'];
  return [{ succeeded:'Succeeded', failed:'Failed', needs_input:'Ended: needs input', interrupted:'Interrupted', cancelled:'Cancelled' }[invocation.outcome] || 'Outcome unknown', invocation.outcome === 'succeeded' ? 'success' : 'attention'];
}
const chip = (label, tone = '') => `<span class="chip status"${tone ? ` data-tone="${tone}"` : ''}>${escapeHtml(label)}</span>`;
function route() {
  const params = new URLSearchParams(location.hash.slice(1));
  return { run:params.get('run'), invocation:params.get('invocation'), phase:params.get('phase'), attempt:params.get('attempt'), cursor:params.get('cursor') };
}
function link(values = {}) {
  const params = new URLSearchParams();
  for (const key of ['run','invocation','phase','attempt','cursor']) if (values[key]) params.set(key, values[key]);
  return '#' + params.toString();
}
function showConnection(kind, text) {
  connection.dataset.state = kind;
  connection.textContent = text;
  if (kind === 'disconnected') announcement.textContent = text;
}
async function api(path, options = {}) {
  const response = await fetch(path, { ...options, cache:'no-store', headers: { Authorization:'Bearer ' + state.token, ...options.headers } });
  if (!response.ok) {
    let message = `History request failed (${response.status}).`;
    try { message = (await response.json()).error || message; } catch {}
    const error = new Error(message); error.status = response.status; throw error;
  }
  return response.json();
}
function errorView(message, parent) {
  app.removeAttribute('aria-busy');
  app.innerHTML = `<div class="error-message" role="alert"><h1>History unavailable</h1><p>${escapeHtml(message)}</p><p><a href="${parent || '#'}">${parent ? 'Return to run' : 'Return to runs'}</a></p></div>`;
}
function routeError(message, parent) { state.error = message; errorView(message, parent); }
function pageAnchor() { return state.runPage.at(-1) ?? 0; }
async function loadIndex(generation = state.routeGeneration) {
  const page = await api(`/api/runs?after=${pageAnchor()}&limit=30`);
  if (generation !== state.routeGeneration) return;
  state.runs = page.runs; state.runPageNext = page.nextCursor; state.runsHaveMore = page.hasMore;
  state.run = null; state.invocation = null; state.error = null;
  renderIndex();
}
function card(run) {
  const invocation = run.latestInvocation;
  const [label, tone] = outcome(invocation);
  const name = run.requestPreview?.trim() || 'Saved run ' + short(run.id);
  const workflow = run.workflow || 'Workflow unavailable';
  const cleanup = run.clearance ? 'Operator confirmed' : invocation?.cleanup === 'complete' ? 'Automatically checked' : invocation?.cleanup === 'unknown' ? 'Manual cleanup required' : 'Cleanup not recorded';
  const capture = run.latestCaptureState ? 'Latest capture: '+run.latestCaptureState : 'No capture recorded';
  const elapsed = run.startedAt ? Math.max(0,Math.round((Date.parse(run.endedAt || new Date().toISOString())-Date.parse(run.startedAt))/1000))+'s as of this view' : 'Elapsed unknown';
  return `<article class="run-card" data-card-search="${escapeHtml(`${name} ${workflow} ${run.id} ${invocation?.id || ''}`.toLowerCase())}" data-outcome="${escapeHtml(invocation?.outcome || invocation?.stage || 'unknown')}">
    <div class="card-head"><a href="${link({ run:run.id })}" aria-label="Open run ${escapeHtml(short(run.id))}: ${escapeHtml(name)}">${escapeHtml(name)}</a>
    <div class="workflow">${escapeHtml(workflow)} - ${escapeHtml(short(run.id))}</div><p class="muted">${escapeHtml(run.requestPreview || 'Request preview unavailable. Open the saved invocation to inspect evidence.')}</p></div>
    <div class="mini-activity" aria-label="Observed activity summary"><span data-kind="${run.startedAt?'active':''}"></span><span data-kind="${run.latestCaptureState?'active':''}"></span><span data-kind="${run.endedAt?'active':''}"></span><small>${invocation ? 'Latest invocation ' + escapeHtml(short(invocation.id)) : 'No invocation yet'}</small></div>
    <div class="card-foot"><div>${chip(label,tone)}<small>${escapeHtml(cleanup)}</small></div><small>${escapeHtml(run.startedAt?'Started '+readableTime(run.startedAt):'Start time unknown')}<br>${escapeHtml(elapsed)}<br>${escapeHtml(capture)}<br>Usage unknown</small></div></article>`;
}
function renderCards() {
  const cards = document.getElementById('cards'); if (!cards) return;
  const needle = state.query.trim().toLowerCase();
  const matches = state.runs.filter(run => {
    const latest = run.latestInvocation;
    const haystack = `${run.requestPreview || ''} ${run.workflow || ''} ${run.id} ${latest?.id || ''}`.toLowerCase();
    const current = latest?.outcome || latest?.stage || 'unknown';
    return haystack.includes(needle) && (state.filter === 'all' || current === state.filter);
  });
  cards.innerHTML = matches.length ? matches.map(card).join('') : `<div class="state-message">${state.runs.length ? 'No matching runs on this page.' : 'No saved runs. Start a workflow from the CLI to record one.'}${state.runs.length ? ' <button type="button" data-action="clear-filter">Clear filters</button>' : ''}</div>`;
}
function renderIndex() {
  app.removeAttribute('aria-busy');
  app.innerHTML = `<div class="heading-row"><div><h1>Repository runs</h1><p class="muted">Saved runs, grouped by run identity. This page shows at most 30 cards.</p></div>
    <div class="controls"><button type="button" data-action="freeze" aria-pressed="${state.frozen}">${state.frozen ? 'Follow latest events' : 'Freeze this view'}</button></div></div>
    ${state.gap ? '<div class="attention" role="status">A saved event gap was detected. This view was rebuilt from a new saved snapshot.</div>' : ''}
    ${state.newRuns ? `<div class="attention"><p>${state.newRuns} new run${state.newRuns === 1 ? '' : 's'} recorded while you were reading.</p><button type="button" data-action="refresh-index">Refresh run order</button></div>` : ''}
    <div class="toolbar"><div class="controls"><label for="run-search">Find on this page <input id="run-search" type="search" placeholder="Request, workflow, or ID" value="${escapeHtml(state.query)}"></label>
    <label for="outcome-filter">Latest invocation <select id="outcome-filter">${[['all','All outcomes'],['running','Running'],['starting','Preparing'],['shutting_down','Stopping'],['succeeded','Succeeded'],['failed','Failed'],['needs_input','Ended: needs input'],['interrupted','Interrupted'],['cancelled','Cancelled'],['unknown','Unknown']].map(([value,label])=>`<option value="${value}"${state.filter===value?' selected':''}>${label}</option>`).join('')}</select></label></div><small>Search and filter apply to this page.</small></div>
    <div id="cards" class="cards" aria-live="off"></div>
    <div class="page-controls"><button type="button" data-action="previous-runs" ${state.runPage.length < 2 ? 'disabled' : ''}>Previous runs</button><small>Page ${state.runPage.length}</small><button type="button" data-action="next-runs" ${state.runsHaveMore ? '' : 'disabled'}>Next runs</button></div>
    <details class="surface"><summary class="section-body">Repository storage and maintenance</summary><div class="section-body"><p>Saved history and backup sizes have not been measured by this host. No growth estimate is available.</p><p>Stop the dashboard process before exceptional idle maintenance. Closing this browser tab does not stop the host. After uninstall, a compatible installation is needed to read saved history.</p></div></details>`;
  renderCards();
}
async function loadRun(target, generation = state.routeGeneration) {
  state.attemptPage=[0];state.captureSummaryPage=[0];state.sessionPage=[0];state.lanePage=0;
  const run = await api(`/api/runs/${target.run}`);
  const selectedId = target.invocation || run.latestInvocation?.id;
  if (selectedId && !idPattern.test(selectedId)) throw new Error('Invalid invocation link.');
  const selector = await api(`/api/runs/${target.run}/invocations?after=${state.invocationPage.at(-1) ?? 0}&limit=30`);
  let detail = null, sessions = null, events = null;
  if (selectedId) {
    [detail,sessions,events] = await Promise.all([
      api(`/api/invocations/${selectedId}?limit=50`),
      api(`/api/invocations/${selectedId}/sessions?limit=50`),
      api(`/api/invocations/${selectedId}/events?tail=1&limit=200`),
    ]);
    if (detail.invocation.runId !== target.run) throw new Error('Invocation does not belong to this run.');
  }
  if (generation !== state.routeGeneration) return;
  state.run = run; state.invocation = detail?.invocation || null;
  state.invocationList = selector.invocations; state.invocationNext = selector.nextCursor; state.invocationMore = selector.hasMore;
  state.attempts = detail?.attempts || []; state.captures = detail?.captures || [];
  state.attemptsNext = detail?.attemptsNextCursor || 0; state.capturesNext = detail?.capturesNextCursor || 0;
  state.attemptsMore = detail?.hasMoreAttempts || false; state.capturesMore = detail?.hasMoreCaptures || false;
  state.accounting = detail?.accounting || null; state.worktree = detail?.worktree || null; state.clearance = detail?.clearance || null;
  state.sessions = sessions?.sessions || []; state.sessionsNext = sessions?.nextCursor || 0; state.sessionsMore = sessions?.hasMore || false;
  state.events = events?.events || []; state.earlier = events?.hasEarlier || false;
  state.selectedCapture = null; state.capturePage = null; state.pending = 0; state.error = null;
  const attempt = target.attempt && state.attempts.find(item => item.id === target.attempt);
  if (target.attempt && !attempt) {
    try {
      const specific = await api(`/api/invocations/${selectedId}/attempts/${target.attempt}`);
      state.attempts.push(specific);
    } catch { throw new Error('Attempt link is unavailable or belongs to another invocation.'); }
  }
  if (target.phase && !state.attempts.some(item => item.operationKey === target.phase)) throw new Error('Phase link is unavailable in this saved page. Open an earlier attempt page.');
  renderRun(target);
}
function attention(invocation) {
  const entries = [];
  if (invocation.outcome === 'needs_input') entries.push('<strong>Saved question needs input.</strong> This invocation has ended. Use its saved question with a fresh CLI invocation from the current workflow entry.');
  if (state.clearance) entries.push(`<strong>Operator confirmed cleanup.</strong> ${escapeHtml(state.clearance.note)} The original ${escapeHtml(invocation.outcome || 'unknown')} outcome and cleanup uncertainty remain saved.`);
  else if (invocation.cleanup === 'unknown') entries.push('<strong>Manual cleanup required.</strong> Inspect reported children and the worktree with the CLI before recording clearance. A browser cannot release ownership.');
  if (!invocation.outcome && invocation.stage === 'finalized') entries.push('<strong>Outcome unknown.</strong> No final result was saved.');
  return entries.length ? `<div class="attention" role="status">${entries.map(item=>`<p>${item}</p>`).join('')}</div>` : '';
}
function invocationLinks(target) {
  return `<div class="controls">${state.invocationList.map(item => `<a class="chip" href="${link({run:target.run,invocation:item.id})}" ${item.id===state.invocation?.id?'aria-current="page"':''}>${escapeHtml(short(item.id))}: ${escapeHtml(outcome(item)[0])}</a>`).join('') || '<span>No invocations on this page.</span>'}</div>
    <div class="page-controls"><button type="button" data-action="previous-invocations" ${state.invocationPage.length<2?'disabled':''}>Earlier invocations</button><small>Chronological page ${state.invocationPage.length}</small><button type="button" data-action="next-invocations" ${state.invocationMore?'':'disabled'}>Later invocations</button></div>`;
}
function laneRows() {
  const attempts = state.attempts.map(item => ({ type:'attempt', key:item.id, item, depth:0 }));
  const sessionsByParent = new Map();
  for (const session of state.sessions) {
    const key = session.parentNativeId || '';
    sessionsByParent.set(key,[...(sessionsByParent.get(key) || []),session]);
  }
  const rows = [...attempts]; const seen = new Set();
  function add(session, depth) {
    if (seen.has(session.id)) return;
    seen.add(session.id); rows.push({type:'session',key:session.id,item:session,depth:Math.min(depth,8)});
    for (const child of sessionsByParent.get(session.nativeId) || []) add(child,depth+1);
  }
  for (const session of state.sessions) if (!session.parentNativeId || !state.sessions.some(candidate=>candidate.nativeId===session.parentNativeId)) add(session,1);
  for (const session of state.sessions) add(session,1);
  return rows;
}
function timing(key, type) {
  const startKind = type === 'attempt' ? 'attempt.admitted' : 'session.changed';
  const matching = state.events.filter(event => type === 'attempt' ? event.data.attemptId === key : event.data.sessionId === key);
  const first = matching.find(event=>event.kind===startKind) || matching[0];
  const last = matching.at(-1);
  const firstTime = Date.parse(first?.data?.at || ''), lastTime = Date.parse(last?.data?.at || '');
  if (!Number.isFinite(firstTime)) return null;
  return { first:firstTime, last:Number.isFinite(lastTime)?lastTime:firstTime };
}
function timeline(target) {
  const all = laneRows(), page = all.slice(state.lanePage*50,(state.lanePage+1)*50);
  const times = page.map(row=>timing(row.key,row.type)).filter(Boolean);
  const min = Math.min(...times.map(time=>time.first)), max = Math.max(...times.map(time=>time.last));
  const span = Number.isFinite(min) && Number.isFinite(max) ? Math.max(1000,max-min) : 0;
  const lane = row => {
    const item = row.item, selected = target.attempt === (row.type==='attempt' ? item.id : item.attemptId);
    const title = row.type==='attempt' ? item.operationKey : `Native session ${short(item.nativeId)}`;
    const status = row.type==='attempt' ? item.outcome || (item.launch==='started'?'Running':'Admitted') : item.lifecycle;
    const detail = row.type==='attempt' ? `Attempt ${short(item.id)} - ${item.kind}` : `Reported ${item.parentNativeId?'child':'parent'} - ${asText(item.usage?.state || 'usage reported')}`;
    const time = timing(row.key,row.type);
    const bar = time && span ? `<a class="phase-bar" href="${link({run:target.run,invocation:state.invocation.id,phase:row.type==='attempt'?item.operationKey:null,attempt:row.type==='attempt'?item.id:item.attemptId})}" data-left="${Math.max(0,(time.first-min)/span*94)}" data-width="${Math.max(4,(time.last-time.first)/span*94)}" data-selected="${selected}" data-tone="${status==='failed'?'error':status==='needs_input'?'attention':''}" aria-label="${escapeHtml(title)}, ${escapeHtml(status)}, inspect details">${escapeHtml(title)}</a>` : `<span class="declared-work">${escapeHtml(status)} - timing unavailable in loaded events</span>`;
    const isChild = row.type==='session' && !!item.parentNativeId;
    const parent = row.type==='session' ? state.sessions.find(candidate=>candidate.nativeId===item.parentNativeId) : null;
    const hidden = !!parent && state.collapsed.has(parent.id);
    return `<div class="timeline-lane" data-parent="${escapeHtml(parent?.id||'')}" ${hidden?'hidden':''}><div class="lane-label depth-${row.depth}"><strong>${escapeHtml(title)}</strong><small>${escapeHtml(detail)}</small><small>${escapeHtml(status)}</small>${row.type==='session' && state.sessions.some(candidate=>candidate.parentNativeId===item.nativeId) ? `<button type="button" data-action="collapse" data-id="${escapeHtml(item.id)}" aria-expanded="${!state.collapsed.has(item.id)}">${state.collapsed.has(item.id)?'Show':'Hide'} reported children</button>`:''}</div><div class="lane-track">${bar}</div></div>`;
  };
  return `<section class="surface" aria-labelledby="timeline-heading"><div class="section-heading"><h2 id="timeline-heading">Invocation timeline</h2><div class="controls"><button type="button" data-action="freeze" aria-pressed="${state.frozen}">${state.frozen?'Follow latest events':'Freeze this view'}</button></div></div>
    <p class="section-body muted">Recorded phases and reported native sessions. Bars represent observed time only. Native IDs are historical evidence, not resume links.</p>
    <div class="timeline-scroll" tabindex="0" role="region" aria-label="Scrollable invocation timeline"><div class="timeline"><div class="timeline-axis"><span>Owner / phase</span><span>Observed time, relative to loaded events</span></div>${page.map(lane).join('') || '<div class="state-message">No managed attempts or reported sessions in this page.</div>'}</div></div>
    <div class="page-controls section-body"><button type="button" data-action="previous-lanes" ${state.lanePage?'':'disabled'}>Previous lanes</button><small>At most 50 rows per page</small><button type="button" data-action="next-lanes" ${(state.lanePage+1)*50<all.length?'':'disabled'}>Next lanes</button></div>
    <div class="timeline-text"><details><summary>All visible phases and attempts (text navigation)</summary><ul>${page.map(row=>{const item=row.item;const label=row.type==='attempt'?`${item.operationKey}, attempt ${short(item.id)}, ${item.outcome||item.launch}`:`Native ${short(item.nativeId)}, ${item.lifecycle}, ${item.parentNativeId?'reported child of '+short(item.parentNativeId):'parent session'}`;return `<li><a href="${link({run:target.run,invocation:state.invocation.id,phase:row.type==='attempt'?item.operationKey:null,attempt:row.type==='attempt'?item.id:item.attemptId})}">${escapeHtml(label)}</a></li>`}).join('') || '<li>No recorded rows.</li>'}</ul></details></div>
    <div class="page-controls section-body"><button type="button" data-action="previous-attempts" ${state.attemptPage.length>1?'':'disabled'}>Previous attempts</button><button type="button" data-action="more-attempts" ${state.attemptsMore?'':'disabled'}>Next attempts</button><button type="button" data-action="previous-sessions" ${state.sessionPage.length>1?'':'disabled'}>Previous sessions</button><button type="button" data-action="more-sessions" ${state.sessionsMore?'':'disabled'}>Next sessions</button></div></section>`;
}
function eventSummary(event) {
  const data = event.data || {};
  return [data.operationKey,data.attemptId && `attempt ${short(data.attemptId)}`,data.sessionId && `session ${short(data.sessionId)}`,data.captureId && `capture ${short(data.captureId)}`,data.outcome,data.lifecycle].filter(Boolean).join(' - ') || 'Saved observation';
}
function renderEventList() {
  const list = document.getElementById('event-list'); if (!list) return;
  const selected = route().attempt;
  const captured = new Map(state.captures.map(item=>[item.id,item.attemptId]));
  const events = selected ? state.events.filter(event => event.data.attemptId===selected || captured.get(event.data.captureId)===selected) : state.events;
  list.innerHTML = events.length ? events.map(event=>`<article class="event-row" data-cursor="${event.cursor}"><time>${escapeHtml(readableTime(event.data.at))}</time><span class="monospace">${escapeHtml(event.kind)}</span><span>${escapeHtml(eventSummary(event))} <small>#${escapeHtml(event.cursor)}</small></span></article>`).join('') : '<p class="state-message">No saved events in this window.</p>';
  const earlier = document.getElementById('earlier-events'); if (earlier) earlier.disabled=!state.earlier;
  const pending = document.getElementById('pending-events'); if (pending) { pending.textContent=state.pending ? `${state.pending} new events - return to latest` : ''; pending.hidden=!state.pending; }
}
function inspector(target) {
  const invocation = state.invocation;
  const selected = target.attempt ? state.attempts.find(item=>item.id===target.attempt) : null;
  const title = selected?.operationKey || 'Invocation evidence';
  const captureButtons = state.captures.map(item=>`<button type="button" data-action="open-capture" data-id="${escapeHtml(item.id)}">${escapeHtml(item.channel)} - ${escapeHtml(item.state)} - ${escapeHtml(short(item.id))}</button>`).join('') || '<p>No saved captures in this page.</p>';
  const agent = selected?.agent;
  return `<section class="surface" id="inspector" aria-labelledby="inspector-heading"><div class="section-heading"><div><h2 id="inspector-heading" tabindex="-1">${escapeHtml(title)}</h2><small>${escapeHtml(state.run.id)} / ${escapeHtml(invocation.id)}${selected?' / '+escapeHtml(selected.id):''}</small></div><a href="${link({run:state.run.id,invocation:invocation.id})}" data-action="return-timeline">Return to timeline</a></div>
    <div class="detail-grid"><div><details open><summary>Request and result</summary><p>${escapeHtml(state.run.requestPreview || 'Request preview unavailable. Open the saved request capture if present.')}</p><dl class="facts"><dt>Outcome</dt><dd>${escapeHtml(selected?.outcome || outcome(invocation)[0])}</dd><dt>Launch</dt><dd>${escapeHtml(selected?.launch || 'Not applicable')}</dd><dt>Evidence</dt><dd>${escapeHtml(selected?.evidence || 'No attempt selected')}</dd></dl></details>
    <details><summary>Workspace and ownership</summary><dl class="facts"><dt>Worktree</dt><dd>${escapeHtml(state.worktree?.path || 'Unknown')}</dd><dt>Registration</dt><dd>${escapeHtml(state.worktree?.registration || 'Unknown')}</dd><dt>Saved cleanup</dt><dd>${escapeHtml(invocation.cleanup==='complete'?'Automatically checked':invocation.cleanup==='unknown'?'Uncertain':'Not recorded')}</dd><dt>Latest clearance</dt><dd>${escapeHtml(state.clearance?'Operator confirmed: '+state.clearance.note:invocation.cleanup==='unknown'?'Manual cleanup required':'No operator clearance recorded')}</dd></dl></details>
    <details><summary>Configuration and inputs</summary><dl class="facts"><dt>Workflow</dt><dd>${escapeHtml(state.run.workflow || 'Unknown')}</dd><dt>Provider</dt><dd>${escapeHtml(agent?.adapter || 'Unknown')}</dd><dt>Requested profile</dt><dd>Not separately recorded</dd><dt>Effective profile</dt><dd>Not separately recorded</dd><dt>Input capture</dt><dd>${escapeHtml(agent?.inputsCaptureId || 'Unknown')}</dd><dt>Result capture</dt><dd>${escapeHtml(agent?.resultCaptureId || 'Unknown')}</dd></dl></details>
    <details><summary>Accounting and usage</summary><pre>${escapeHtml(JSON.stringify(state.accounting || {},null,2))}</pre><p>Native child usage is reported separately. Unknown usage is not zero.</p></details>
    <details><summary>Saved outputs and traces</summary><div class="capture-list">${captureButtons}</div><div class="controls"><button type="button" data-action="previous-captures" ${state.captureSummaryPage.length>1?'':'disabled'}>Previous captures</button><button type="button" data-action="more-captures" ${state.capturesMore?'':'disabled'}>Next captures</button></div></details>
    <div id="capture-view" aria-live="off"></div></div>
    <div><div class="heading-row"><h3>Recorded events</h3><small>Saved before display</small></div>
      <div id="event-list" class="event-list" tabindex="0" role="region" aria-label="Recorded event text"></div>
      <div class="page-controls"><button id="earlier-events" type="button" data-action="earlier-events" ${state.earlier?'':'disabled'}>Load earlier events</button><button id="pending-events" type="button" data-action="latest-events" ${state.pending?'':'hidden'}>${state.pending ? state.pending+' new events - return to latest':''}</button></div>
      <p class="muted">Scrolling away from the bottom pauses automatic following. Recording continues.</p></div></div></section>`;
}
function renderRun(target) {
  app.removeAttribute('aria-busy');
  const run=state.run, invocation=state.invocation;
  const [label,tone]=outcome(invocation);
  app.innerHTML=`<nav aria-label="Breadcrumb"><a href="#">Repository runs</a> / <span>Run ${escapeHtml(short(run.id))}</span></nav>
    <div class="heading-row" style="margin-top:18px"><div><h1>${escapeHtml(run.requestPreview?.trim() || 'Run '+short(run.id))}</h1><p class="muted">${escapeHtml(run.workflow || 'Workflow unavailable')} - run ${escapeHtml(run.id)}</p>
    <div class="chip-list"><span id="execution-state">${chip(label,tone)}</span><span id="cleanup-state">${chip(state.clearance?'Operator confirmed':invocation?.cleanup==='complete'?'Automatically checked':invocation?.cleanup==='unknown'?'Manual cleanup required':'Cleanup unknown',state.clearance||invocation?.cleanup==='complete'?'success':'attention')}</span>${chip('Capture: inspect saved records')}<span id="observation-state">${chip(state.connected?'Connected':'Disconnected',state.connected?'success':'attention')}</span></div></div></div>
    <div id="attention-slot">${invocation ? attention(invocation) : '<div class="state-message">This run has no saved invocation.</div>'}</div>
    ${state.gap?'<div class="attention" role="status">A saved event gap was detected. Details were rebuilt from a new saved snapshot; continuity is unknown.</div>':''}
    <section class="surface"><div class="section-heading"><h2>Invocation history</h2><small>Each invocation starts at the current workflow entry</small></div><div class="section-body">${invocationLinks(target)}</div></section>
    ${invocation ? `${timeline(target)}${inspector(target)}` : ''}
    <details class="surface"><summary class="section-body">Repository storage and maintenance</summary><div class="section-body"><p>History size, backups, measurement time, and growth have not been measured by this host.</p><p>Stop the dashboard process before exceptional idle maintenance. Closing this tab leaves the host running.</p></div></details>`;
  renderEventList();
  const eventList=document.getElementById('event-list');if(eventList)eventList.scrollTop=eventList.scrollHeight;
  document.querySelectorAll('.phase-bar').forEach(bar=>{bar.style.setProperty('--bar-left',bar.dataset.left+'%');bar.style.setProperty('--bar-width',bar.dataset.width+'%')});
  if (target.phase || target.attempt) document.getElementById('inspector-heading')?.focus({preventScroll:true});
}
async function loadRoute() {
  if (!state.token) return;
  const generation=++state.routeGeneration, target=route();
  app.setAttribute('aria-busy','true');
  try {
    if (!target.run) { await loadIndex(generation); return; }
    if (!idPattern.test(target.run)) { routeError('Invalid run link. The saved record was not selected.'); return; }
    if (state.run?.id!==target.run) state.invocationPage=[0];
    await loadRun(target,generation);
    if (generation!==state.routeGeneration) return;
  } catch(error) { if (generation===state.routeGeneration) routeError(error.message, target.run ? link({run:target.run}) : null); }
}
async function resnapshotPreservingReader() {
  const active=document.activeElement;
  const identity={id:active?.id,action:active?.getAttribute('data-action'),item:active?.getAttribute('data-id'),start:active?.selectionStart,end:active?.selectionEnd};
  const top=window.scrollY, timeline=document.querySelector('.timeline-scroll')?.scrollLeft || 0, events=document.getElementById('event-list')?.scrollTop || 0;
  await loadRoute();
  const focus=identity.id ? document.getElementById(identity.id) : identity.action ? [...document.querySelectorAll('[data-action]')].find(item=>item.getAttribute('data-action')===identity.action && item.getAttribute('data-id')===identity.item) : null;
  if(focus){focus.focus({preventScroll:true});if(typeof identity.start==='number'&&typeof focus.setSelectionRange==='function')focus.setSelectionRange(identity.start,identity.end);}
  const timelineNow=document.querySelector('.timeline-scroll');if(timelineNow)timelineNow.scrollLeft=timeline;
  const eventNow=document.getElementById('event-list');if(eventNow)eventNow.scrollTop=events;
  window.scrollTo(0,top);
}
async function redeem(ticket) {
  if (!ticket) throw new Error('This browser link has no active owner handoff. Start the dashboard from its owner process and open the new link.');
  const response=await fetch('/api/ui-session',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({ticket})});
  if (!response.ok) throw new Error('This handoff is expired or has already been used. Start a new owner link.');
  const result=await response.json();
  if (typeof result.sessionToken!=='string' || !result.sessionToken) throw new Error('Owner handoff returned no credential.');
  state.token=result.sessionToken;
}
async function connect() {
  let wait=300;
  while (state.token) {
    const abort=new AbortController(); state.streamAbort=abort;
    try {
      showConnection('connecting','Catching up from saved cursor '+state.cursor);
      const response=await fetch('/api/stream?after='+encodeURIComponent(state.cursor),{headers:{Authorization:'Bearer '+state.token},cache:'no-store',signal:abort.signal});
      if (!response.ok || !response.body) throw new Error('Observation stream unavailable');
      state.connected=true; showConnection(state.frozen?'frozen':'connected',state.frozen?'Frozen at saved cursor '+state.cursor:'Connected - saved cursor '+state.cursor);
      wait=300;
      const reader=response.body.getReader(),decoder=new TextDecoder(); let buffer='';
      while (true) {
        const part=await reader.read(); if(part.done) break;
        buffer+=decoder.decode(part.value,{stream:true});
        let end;
        while((end=buffer.indexOf('\n\n'))!==-1) {
          const frame=buffer.slice(0,end); buffer=buffer.slice(end+2);
          const fields={event:'message',data:'',id:null};
          for(const line of frame.split('\n')) {
            if(line.startsWith('event: '))fields.event=line.slice(7);
            else if(line.startsWith('data: '))fields.data+=line.slice(6);
            else if(line.startsWith('id: '))fields.id=line.slice(4);
          }
          if(fields.event==='observation') {
            let event; try {event=JSON.parse(fields.data);} catch {continue;}
            if(!/^\d+$/.test(event.cursor||'') || BigInt(event.cursor)<=BigInt(state.cursor))continue;
            applyEvent(event); state.cursor=event.cursor; state.lastUpdate=new Date();
          } else if(fields.event==='gap'||fields.event==='unavailable') {
            state.gap=true; throw new Error(fields.event==='gap'?'Saved event gap':'Observation unavailable');
          }
        }
      }
      throw new Error('Observation stream disconnected');
    } catch(error) {
      if(error.name==='AbortError')return;
      state.connected=false;
      showConnection('disconnected',`Disconnected - last update ${state.lastUpdate ? state.lastUpdate.toLocaleTimeString() : 'unknown'}`);
      if(state.gap) {
        try { const head=await api('/api/events/head'); state.cursor=head.cursor; await resnapshotPreservingReader(); }
        catch { /* Keep the last saved display and retry. */ }
      }
      await new Promise(resolve=>setTimeout(resolve,wait)); wait=Math.min(wait*2,5000);
    }
  }
}
function applyEvent(event) {
  if(event.kind==='run.created') {
    state.newRuns++;
    if(!route().run) {
      let notice=document.getElementById('new-runs-notice');
      if(!notice) {notice=document.createElement('div');notice.id='new-runs-notice';notice.className='attention';document.querySelector('.heading-row')?.after(notice);}
      notice.innerHTML=`<p>${state.newRuns} new run${state.newRuns===1?'':'s'} recorded while you were reading.</p><button type="button" data-action="refresh-index">Refresh run order</button>`;
    }
  }
  if(state.frozen) { if(state.invocation && event.data?.invocationId===state.invocation.id){state.pending++;updatePending();} return; }
  if(state.invocation && event.data?.invocationId===state.invocation.id) {
    if(event.kind==='capture.created' && !state.captures.some(item=>item.id===event.data.captureId)) {
      state.captures.push({id:event.data.captureId,channel:event.data.channel,state:'open',attemptId:null});
      if(state.captures.length>50)state.captures.shift();
      updateCaptureButtons();
    }
    if(event.kind==='capture.appended') {
      const capture=state.captures.find(item=>item.id===event.data.captureId);
      if(capture) {capture.state=event.data.state;updateCaptureButtons();}
    }
    const list=document.getElementById('event-list');
    const selection=window.getSelection();
    const readingText=selection && !selection.isCollapsed && list?.contains(selection.anchorNode);
    const away=list && list.scrollHeight-list.scrollTop-list.clientHeight>48;
    if(readingText || away) { state.pending++; updatePending(); return; }
      state.events.push(event); if(state.events.length>200) {state.events.shift(); state.earlier=true;}
    renderEventList(); if(list)list.scrollTop=list.scrollHeight;
    if(['invocation.finalized','invocation.running','invocation.shutting_down','owner.cleared'].includes(event.kind)) void refreshCurrentOutcome();
  }
  showConnection('connected','Connected - saved cursor '+state.cursor);
}
function updateCaptureButtons() {
  const container=document.querySelector('.capture-list');if(!container)return;
  container.innerHTML=state.captures.map(item=>`<button type="button" data-action="open-capture" data-id="${escapeHtml(item.id)}">${escapeHtml(item.channel)} - ${escapeHtml(item.state)} - ${escapeHtml(short(item.id))}</button>`).join('') || '<p>No saved captures in this page.</p>';
}
async function refreshCurrentOutcome() {
  if(!state.invocation)return;
  const id=state.invocation.id;
  try {
    const page=await api(`/api/invocations/${id}?limit=1`);
    if(state.invocation?.id!==id)return;
    state.invocation=page.invocation;state.clearance=page.clearance;
    const [label,tone]=outcome(state.invocation);
    const execution=document.getElementById('execution-state');if(execution)execution.innerHTML=chip(label,tone);
    const cleanup=document.getElementById('cleanup-state');if(cleanup)cleanup.innerHTML=chip(state.clearance?'Operator confirmed':state.invocation.cleanup==='complete'?'Automatically checked':state.invocation.cleanup==='unknown'?'Manual cleanup required':'Cleanup unknown',state.clearance||state.invocation.cleanup==='complete'?'success':'attention');
    const slot=document.getElementById('attention-slot');if(slot)slot.innerHTML=attention(state.invocation);
    announcement.textContent='Selected invocation outcome or cleanup changed: '+label;
  } catch { /* Keep the last saved display until a successful snapshot. */ }
}
function updatePending() {
  const button=document.getElementById('pending-events');
  if(button) { button.hidden=false; button.textContent=state.pending+' new events - return to latest'; }
}
async function latestEvents() {
  if(!state.invocation)return;
  const page=await api(`/api/invocations/${state.invocation.id}/events?tail=1&limit=200`);
  state.events=page.events; state.earlier=page.hasEarlier; state.pending=0; state.frozen=false;
  await refreshCurrentOutcome();
  renderEventList(); document.getElementById('event-list')?.scrollTo({top:10000000});
  document.querySelectorAll('[data-action="freeze"]').forEach(button=>{button.textContent='Freeze this view';button.setAttribute('aria-pressed','false')});
  showConnection(state.connected?'connected':'disconnected',state.connected?'Connected - saved cursor '+state.cursor:'Disconnected - showing last saved view');
}
async function olderEvents() {
  if(!state.invocation||!state.events.length)return;
  const before=state.events[0].cursor;
  const page=await api(`/api/invocations/${state.invocation.id}/events?before=${before}&limit=200`);
  state.events=page.events; state.earlier=page.hasEarlier; state.frozen=true;
  renderEventList(); document.getElementById('event-list')?.scrollTo({top:0});
  document.querySelectorAll('[data-action="freeze"]').forEach(button=>{button.textContent='Follow latest events';button.setAttribute('aria-pressed','true')});
  showConnection('frozen','Frozen at saved cursor '+before);
}
async function openCapture(id) {
  if(!state.invocation)return;
  state.selectedCapture=id;state.captureAfter=0;
  const page=await api(`/api/invocations/${state.invocation.id}/captures/${id}?limit=50`);
  state.capturePage=page;
  renderCapture();
}
function renderCapture() {
  const panel=document.getElementById('capture-view'); if(!panel||!state.capturePage)return;
  const page=state.capturePage;
  panel.innerHTML=`<div class="section-body"><h3>Saved capture ${escapeHtml(short(state.selectedCapture))}</h3><p>${escapeHtml(page.channel || 'Channel unknown')} - ${escapeHtml(page.state)}${page.state==='partial'||page.state==='pruned'||page.state==='unknown'?' - some saved output may be unavailable':''}</p><p>Showing after chunk ${state.captureAfter}; next chunk ${page.nextSequence}.</p><pre class="capture-text" id="capture-text"></pre><div class="controls"><button type="button" data-action="capture-start" ${state.captureAfter?'':'disabled'}>Start of capture</button><button type="button" data-action="more-output" ${page.hasMore?'':'disabled'}>Load next saved text</button></div></div>`;
  document.getElementById('capture-text').textContent=page.chunks.map(chunk=>chunk.text).join('');
}
async function moreOutput() {
  const old=state.capturePage; if(!old?.hasMore)return;
  const next=await api(`/api/invocations/${state.invocation.id}/captures/${state.selectedCapture}?after=${old.nextSequence}&limit=50`);
  state.captureAfter=old.nextSequence;state.capturePage=next;renderCapture();
}
async function moreHistory(kind, direction='next') {
  if(!state.invocation)return;
  const id=state.invocation.id;
  const stack=kind==='sessions'?state.sessionPage:kind==='attempts'?state.attemptPage:state.captureSummaryPage;
  const previousStack=stack.slice();
  if(direction==='next')stack.push(kind==='sessions'?state.sessionsNext:kind==='attempts'?state.attemptsNext:state.capturesNext);
  else if(stack.length>1)stack.pop();
  const cursor=stack.at(-1) ?? 0;
  try {
    if(kind==='sessions') {
      const page=await api(`/api/invocations/${id}/sessions?after=${cursor}&limit=50`);
      state.sessions=page.sessions;state.sessionsNext=page.nextCursor;state.sessionsMore=page.hasMore;
      state.collapsed.clear();
    } else {
      const key=kind==='attempts'?'afterAttempt':'afterCapture';
      const page=await api(`/api/invocations/${id}?${key}=${cursor}&limit=50`);
      if(kind==='attempts'){state.attempts=page.attempts;state.attemptsNext=page.attemptsNextCursor;state.attemptsMore=page.hasMoreAttempts;}
      else{state.captures=page.captures;state.capturesNext=page.capturesNextCursor;state.capturesMore=page.hasMoreCaptures;}
    }
  } catch(error) { stack.splice(0,stack.length,...previousStack);throw error; }
  state.lanePage=0;
  const focus=document.activeElement?.getAttribute('data-action');renderRun(route());
  if(focus)document.querySelector(`[data-action="${focus}"]`)?.focus({preventScroll:true});
}
app.addEventListener('input',event=>{if(event.target.id==='run-search'){state.query=event.target.value;renderCards();}});
document.querySelector('.skip')?.addEventListener('click',event=>{event.preventDefault();app.focus({preventScroll:true});app.scrollIntoView({block:'start'});});
app.addEventListener('change',event=>{if(event.target.id==='outcome-filter'){state.filter=event.target.value;renderCards();}});
app.addEventListener('click',async event=>{
  const button=event.target.closest('[data-action]');if(!button)return;
  const action=button.dataset.action;
  try {
    if(action==='clear-filter'){state.query='';state.filter='all';renderIndex();document.getElementById('run-search')?.focus();}
    else if(action==='next-runs'){state.runPage.push(state.runPageNext);await loadIndex();}
    else if(action==='previous-runs'){state.runPage.pop();await loadIndex();}
    else if(action==='refresh-index'){state.runPage=[0];state.newRuns=0;await loadIndex();}
    else if(action==='next-invocations'){state.invocationPage.push(state.invocationNext);await loadRun(route());}
    else if(action==='previous-invocations'){state.invocationPage.pop();await loadRun(route());}
    else if(action==='next-lanes'||action==='previous-lanes'){state.lanePage=Math.max(0,state.lanePage+(action==='next-lanes'?1:-1));renderRun(route());document.querySelector(`[data-action="${action}"]`)?.focus({preventScroll:true});}
    else if(action==='more-attempts')await moreHistory('attempts');
    else if(action==='more-sessions')await moreHistory('sessions');
    else if(action==='more-captures')await moreHistory('captures');
    else if(action==='previous-attempts')await moreHistory('attempts','previous');
    else if(action==='previous-sessions')await moreHistory('sessions','previous');
    else if(action==='previous-captures')await moreHistory('captures','previous');
    else if(action==='earlier-events')await olderEvents();
    else if(action==='latest-events')await latestEvents();
    else if(action==='open-capture')await openCapture(button.dataset.id);
    else if(action==='more-output')await moreOutput();
    else if(action==='capture-start')await openCapture(state.selectedCapture);
    else if(action==='collapse'){
      const id=button.dataset.id;
      if(state.collapsed.has(id))state.collapsed.delete(id);else state.collapsed.add(id);
      button.setAttribute('aria-expanded',String(!state.collapsed.has(id)));
      button.textContent=state.collapsed.has(id)?'Show reported children':'Hide reported children';
      document.querySelectorAll(`[data-parent="${CSS.escape(id)}"]`).forEach(row=>{row.hidden=state.collapsed.has(id)});
    }
    else if(action==='freeze'){
      if(state.frozen)await latestEvents();else{state.frozen=true;showConnection('frozen','Frozen at saved cursor '+state.cursor);document.querySelectorAll('[data-action="freeze"]').forEach(item=>{item.setAttribute('aria-pressed','true');item.textContent='Follow latest events'})}
    }
    else if(action==='return-timeline')document.querySelector('.timeline-scroll')?.focus({preventScroll:true});
  } catch(error){announcement.textContent=error.message;const box=document.createElement('div');box.className='error-message';box.setAttribute('role','alert');box.textContent=error.message;app.prepend(box);}
});
window.addEventListener('hashchange',()=>{void loadRoute()});

export async function start(ticket) {
  try {
    await redeem(ticket);
    // The head is sampled before the first snapshot, so later committed events are replayed by SSE.
    const head=await api('/api/events/head');state.cursor=head.cursor;
    await loadRoute();
    void connect();
  } catch(error) {showConnection('disconnected','History unavailable');errorView(error.message);}
}
