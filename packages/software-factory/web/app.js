const app = document.getElementById('app');
const connection = document.getElementById('connection');
const announcement = document.getElementById('announcement');
const state = {
  token: null, cursor: '0', connected: false, lastUpdate: null, frozen: false, pending: 0, gap: false,
  runPage: [0], runs: [], runPageNext: 0, runsHaveMore: false, query: '', filter: 'all', newRuns: 0,
  run: null, invocation: null, invocationPage: [0], invocationList: [], invocationNext: 0, invocationMore: false,
  attempts: [], captures: [], attemptsNext: 0, capturesNext: 0, attemptsMore: false, capturesMore: false,
  attemptPage: [0], captureSummaryPage: [0], sessionPage: [0],
  sessions: [], sessionsNext: 0, sessionsMore: false, lanePage: 0, collapsed: new Set(), sessionParents: new Map(), question: null,
  events: [], earlier: false, selectedCapture: null, capturePage: null, captureAfter: 0, capturePending: false, captureVersion: 0, captureRefreshing: false, streamAbort: null,
  routeGeneration: 0, outcomeGeneration: 0, cardRefreshSequence: 0, cardGenerations: new Map(), error: null, connectionKind: null, validatedParent: null,
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
  return { run:params.get('run'), invocation:params.get('invocation'), phase:params.get('phase'), attempt:params.get('attempt'), session:params.get('session'), cursor:params.get('cursor') };
}
function link(values = {}) {
  const params = new URLSearchParams();
  for (const key of ['run','invocation','phase','attempt','session','cursor']) if (values[key]) params.set(key, values[key]);
  return '#' + params.toString();
}
function showConnection(kind, text) {
  const changed = state.connectionKind !== kind;
  state.connectionKind = kind;
  connection.dataset.state = kind;
  connection.textContent = text;
  const chipSlot=document.getElementById('observation-state');
  if(chipSlot) chipSlot.innerHTML=chip(kind==='disconnected'?`Disconnected - last update ${state.lastUpdate?state.lastUpdate.toLocaleTimeString():'unknown'}`:kind==='frozen'?'Frozen at saved cursor '+state.cursor:kind==='connecting'?'Catching up':'Connected',kind==='connected'?'success':'attention');
  if (changed) announcement.textContent = kind==='disconnected'?text:kind==='connected'?'Observation connected.':kind==='connecting'?'Catching up with saved observations.':'Observation frozen.';
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
  app.innerHTML = `<div class="error-message" role="alert"><h1>History unavailable</h1><p>${escapeHtml(message)}</p><p><a href="${parent || '#'}">${parent ? 'Return to saved parent' : 'Return to runs'}</a></p></div>`;
}
function routeError(message, parent) { state.error = message; errorView(message, parent); }
function pageAnchor() { return state.runPage.at(-1) ?? 0; }
async function loadIndex(generation = state.routeGeneration) {
  const page = await api(`/api/runs?after=${pageAnchor()}&limit=30`);
  if (generation !== state.routeGeneration) return;
  state.runs = page.runs; state.runPageNext = page.nextCursor; state.runsHaveMore = page.hasMore;
  state.cardGenerations.clear();
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
  return `<article class="run-card" data-run="${escapeHtml(run.id)}" data-card-search="${escapeHtml(`${name} ${workflow} ${run.id} ${invocation?.id || ''}`.toLowerCase())}" data-outcome="${escapeHtml(invocation?.outcome || invocation?.stage || 'unknown')}">
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
async function loadRun(target, generation = state.routeGeneration, reader = null) {
  const run = await api(`/api/runs/${target.run}`);
  if(generation===state.routeGeneration)state.validatedParent=link({run:target.run});
  const selectedId = target.invocation || run.latestInvocation?.id;
  if (selectedId && !idPattern.test(selectedId)) throw new Error('Invalid invocation link.');
  const sameReader=reader?.route?.run===target.run && (!reader.route.invocation||reader.route.invocation===selectedId);
  const savedPages=sameReader?reader.pages:null;
  const pageStack=value=>Array.isArray(value)&&value.length&&value.length<=128&&value.every(cursor=>Number.isSafeInteger(cursor)&&cursor>=0)?value.slice():[0];
  if(savedPages?.invocations)state.invocationPage=pageStack(savedPages.invocations);
  state.attemptPage=pageStack(savedPages?.attempts);
  state.captureSummaryPage=pageStack(savedPages?.captures);
  state.sessionPage=pageStack(savedPages?.sessions);
  state.lanePage=Number.isSafeInteger(savedPages?.lane)&&savedPages.lane>=0&&savedPages.lane<128?savedPages.lane:0;
  const selector = await api(`/api/runs/${target.run}/invocations?after=${state.invocationPage.at(-1) ?? 0}&limit=30`);
  let detail = null, sessions = null, events = null, selectedEvent = null, selectedSession = null, selectedCaptureTarget = null, question = null;
  if (selectedId) {
    [detail,sessions,events] = await Promise.all([
      api(`/api/invocations/${selectedId}?afterAttempt=${state.attemptPage.at(-1)??0}&afterCapture=${state.captureSummaryPage.at(-1)??0}&limit=50`),
      api(`/api/invocations/${selectedId}/sessions?after=${state.sessionPage.at(-1)??0}&limit=50`),
      api(`/api/invocations/${selectedId}/events?tail=1&limit=200`),
    ]);
    if (detail.invocation.runId !== target.run) throw new Error('Invocation does not belong to this run.');
    if(generation===state.routeGeneration)state.validatedParent=link({run:target.run,invocation:selectedId});
    if (target.cursor) {
      if (!/^\d{1,19}$/.test(target.cursor)) throw new Error('Invalid saved event cursor.');
      selectedEvent=await api(`/api/invocations/${selectedId}/events/${target.cursor}`);
      events=await api(`/api/invocations/${selectedId}/events?before=${BigInt(target.cursor)+1n}&limit=200`);
      if(selectedEvent?.data?.captureId) {
        if(!idPattern.test(selectedEvent.data.captureId))throw new Error('Saved event has an invalid capture identity.');
        selectedCaptureTarget=await api(`/api/invocations/${selectedId}/captures/${selectedEvent.data.captureId}?limit=1`);
        if(selectedEvent.data.attemptId && selectedEvent.data.attemptId!==selectedCaptureTarget.attemptId)throw new Error('Saved event capture does not belong to its recorded attempt.');
      }
    }
    if (target.session) {
      if (!idPattern.test(target.session)) throw new Error('Invalid native session link.');
      selectedSession=await api(`/api/invocations/${selectedId}/sessions/${target.session}`);
    }
    if(!selectedSession && selectedEvent?.data?.sessionId) {
      if(!idPattern.test(selectedEvent.data.sessionId))throw new Error('Saved event has an invalid native session identity.');
      selectedSession=await api(`/api/invocations/${selectedId}/sessions/${selectedEvent.data.sessionId}`);
    }
    question=await api(`/api/invocations/${selectedId}/question`);
  }
  if (generation !== state.routeGeneration) return;
  state.run = run; state.invocation = detail?.invocation || null;
  state.invocationList = selector.invocations; state.invocationNext = selector.nextCursor; state.invocationMore = selector.hasMore;
  state.attempts = detail?.attempts || []; state.captures = detail?.captures || [];
  state.attemptsNext = detail?.attemptsNextCursor || 0; state.capturesNext = detail?.capturesNextCursor || 0;
  state.attemptsMore = detail?.hasMoreAttempts || false; state.capturesMore = detail?.hasMoreCaptures || false;
  state.accounting = detail?.accounting || null; state.worktree = detail?.worktree || null; state.clearance = detail?.clearance || null;
  state.sessions = sessions?.sessions || []; rememberSessionParents(state.sessions); state.sessionsNext = sessions?.nextCursor || 0; state.sessionsMore = sessions?.hasMore || false;
  state.events = events?.events || []; state.earlier = events?.hasEarlier || false;
  state.question=question; state.selectedEventCursor=selectedEvent?.cursor || null;state.selectedCaptureTarget=selectedCaptureTarget;
  state.selectedCapture = null; state.capturePage = null; state.capturePending=false;state.captureVersion++;state.pending = 0; state.error = null;
  if (selectedSession && !state.sessions.some(item=>item.id===selectedSession.id)) state.sessions.push(selectedSession);
  if (selectedSession) rememberSessionParents([selectedSession]);
  if (selectedSession) {
    let parent=state.sessions.find(item=>item.attemptId===selectedSession.attemptId && item.nativeId===selectedSession.parentNativeId);
    const seen=new Set();
    while(parent && !seen.has(parent.id)) { seen.add(parent.id);state.collapsed.delete(parent.id);parent=state.sessions.find(item=>item.attemptId===parent.attemptId && item.nativeId===parent.parentNativeId); }
  }
  if (selectedSession && target.attempt && selectedSession.attemptId!==target.attempt) throw new Error('Native session does not belong to the selected attempt.');
  const eventAttemptId=selectedCaptureTarget?selectedCaptureTarget.attemptId:selectedEvent?.data?.attemptId;
  if (selectedEvent && target.attempt && eventAttemptId!==target.attempt) throw new Error('Saved event does not belong to the selected attempt.');
  const selectedAttemptId=target.attempt || selectedSession?.attemptId || eventAttemptId;
  if (selectedAttemptId && !idPattern.test(selectedAttemptId)) throw new Error('Invalid saved attempt link.');
  if ((selectedAttemptId && !state.attempts.some(item=>item.id===selectedAttemptId)) || (target.phase && !state.attempts.some(item=>item.operationKey===target.phase))) {
    try {
      const params=new URLSearchParams();if(selectedAttemptId)params.set('attempt',selectedAttemptId);if(target.phase)params.set('phase',target.phase);
      const page=await api(`/api/invocations/${selectedId}/attempt-page?${params}`);
      state.attempts=page.attempts;state.attemptsNext=page.nextCursor;state.attemptsMore=page.hasMore;
      state.attemptPage=page.targetCursor>1?[0,page.targetCursor-1]:[0];
    } catch { throw new Error('Saved phase or attempt is unavailable or belongs to another invocation.'); }
  }
  const attempt=selectedAttemptId && state.attempts.find(item=>item.id===selectedAttemptId);
  if (target.phase && attempt && attempt.operationKey!==target.phase) throw new Error('Attempt does not belong to this phase.');
  if (target.phase && !state.attempts.some(item=>item.operationKey===target.phase)) throw new Error('Saved phase is unavailable.');
  if (selectedEvent?.data?.sessionId && target.session && selectedEvent.data.sessionId!==target.session) throw new Error('Saved event does not belong to the selected native session.');
  const displayTarget={...target,attempt:target.attempt||selectedAttemptId||null,phase:target.phase||attempt?.operationKey||null,session:target.session||selectedSession?.id||null};
  state.displayTarget=displayTarget;
  if(displayTarget.session || selectedAttemptId || displayTarget.phase) {
    const rows=laneRows();
    const index=rows.findIndex(row=>displayTarget.session?row.type==='session'&&row.item.id===displayTarget.session:row.type==='attempt'&&(selectedAttemptId?row.item.id===selectedAttemptId:row.item.operationKey===displayTarget.phase));
    if(index>=0)state.lanePage=Math.floor(index/50);
  }
  renderRun(displayTarget);
}
function attention(invocation) {
  const entries = [];
  if (invocation.outcome === 'needs_input' || state.question?.available) {
    const question=state.question;
    entries.push(`<strong>${invocation.outcome==='needs_input'?'Saved question needs input.':'Saved question.'}</strong> ${question?.available?`<span class="question-text">${escapeHtml(question.question)}</span><span>${escapeHtml(question.context)}</span>${question.suggestions?.length?`<span>Suggested answers: ${question.suggestions.map(escapeHtml).join('; ')}</span>`:''}`:'Question text is unavailable in the current saved capture.'} ${!invocation.outcome?'<span>No final result has been saved yet; outcome is unknown.</span>':''}<span>To answer, start a fresh CLI invocation with run ${escapeHtml(state.run.id)}, worktree ${escapeHtml(state.worktree?.id || 'unknown')}, and saved question ${escapeHtml(question?.captureId || 'unknown')}. The new invocation starts at the current workflow entry.</span>`);
  }
  if (invocation.outcome === 'failed') entries.push('<strong>Failed invocation.</strong> Open the saved result and attempt evidence below to inspect the failure.');
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
    const key = session.attemptId+':'+(session.parentNativeId || '');
    sessionsByParent.set(key,[...(sessionsByParent.get(key) || []),session]);
  }
  const rows = [...attempts]; const seen = new Set();
  function add(session, depth) {
    if (seen.has(session.id)) return;
    seen.add(session.id); rows.push({type:'session',key:session.id,item:session,depth:Math.min(depth,8)});
    for (const child of sessionsByParent.get(session.attemptId+':'+session.nativeId) || []) add(child,depth+1);
  }
  for (const session of state.sessions) if (!session.parentNativeId || !state.sessions.some(candidate=>candidate.attemptId===session.attemptId && candidate.nativeId===session.parentNativeId)) add(session,1);
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
    const item = row.item, selected = row.type==='attempt' ? target.attempt===item.id : target.session===item.id;
    const title = row.type==='attempt' ? item.operationKey : `Native session ${short(item.nativeId)}`;
    const status = row.type==='attempt' ? item.outcome || (item.launch==='started'?'Running':'Admitted') : item.lifecycle;
    const detail = row.type==='attempt' ? `Attempt ${short(item.id)} - ${item.kind}` : `Reported ${item.parentNativeId?'child':'parent'} - ${asText(item.usage?.state || 'usage reported')}`;
    const time = timing(row.key,row.type);
    const destination=link({run:target.run,invocation:state.invocation.id,phase:row.type==='attempt'?item.operationKey:null,attempt:row.type==='attempt'?item.id:item.attemptId,session:row.type==='session'?item.id:null});
    const width=time && time.last>time.first?Math.max(4,(time.last-time.first)/span*94):0;
    const compact=width<12;
    const bar = time && span ? `<a class="phase-bar" href="${destination}" data-left="${Math.max(0,(time.first-min)/span*94)}" data-width="${width}" data-compact="${compact}" data-instant="${time.last===time.first}" data-selected="${selected}" data-tone="${status==='failed'?'error':status==='needs_input'?'attention':''}" aria-label="${escapeHtml(title)}, ${escapeHtml(status)}, ${time.last===time.first?'one observed instant; duration unknown':'observed interval'}, inspect details">${compact?'':escapeHtml(title)}</a>` : `<span class="declared-work">${escapeHtml(status)} - timing unavailable in loaded events</span>`;
    const isChild = row.type==='session' && !!item.parentNativeId;
    const parent = row.type==='session' ? state.sessions.find(candidate=>candidate.attemptId===item.attemptId && candidate.nativeId===item.parentNativeId) : null;
    return `<div class="timeline-lane" data-session="${row.type==='session'?escapeHtml(item.id):''}" data-parent="${escapeHtml(parent?.id||'')}"><div class="lane-label depth-${row.depth}"><strong>${escapeHtml(title)}</strong><small>${escapeHtml(detail)}</small><small>${escapeHtml(status)}</small>${row.type==='session' && state.sessions.some(candidate=>candidate.attemptId===item.attemptId && candidate.parentNativeId===item.nativeId) ? `<button type="button" data-action="collapse" data-id="${escapeHtml(item.id)}" aria-expanded="${!state.collapsed.has(item.id)}">${state.collapsed.has(item.id)?'Show':'Hide'} reported children</button>`:''}</div><div class="lane-track">${bar}</div></div>`;
  };
  return `<section class="surface" aria-labelledby="timeline-heading"><div class="section-heading"><h2 id="timeline-heading">Invocation timeline</h2><div class="controls"><button type="button" data-action="freeze" aria-pressed="${state.frozen}">${state.frozen?'Follow latest events':'Freeze this view'}</button></div></div>
    <p class="section-body muted">Recorded phases and reported native sessions. Bars represent observed time only. Native IDs are historical evidence, not resume links.</p>
    <div class="timeline-scroll" tabindex="0" role="region" aria-label="Scrollable invocation timeline"><div class="timeline${page.length?'':' timeline-empty'}"><div class="timeline-axis"><span>Owner / phase</span><span>Observed time, relative to loaded events</span></div>${page.map(lane).join('') || '<div class="state-message">No managed attempts or reported sessions in this page.</div>'}</div></div>
    <div class="page-controls section-body"><button type="button" data-action="previous-lanes" ${state.lanePage?'':'disabled'}>Previous lanes</button><small>At most 50 rows per page</small><button type="button" data-action="next-lanes" ${(state.lanePage+1)*50<all.length?'':'disabled'}>Next lanes</button></div>
    <div class="timeline-text"><details><summary>All visible phases and attempts (text navigation)</summary><ul>${page.map(row=>{const item=row.item;const label=row.type==='attempt'?`${item.operationKey}, attempt ${short(item.id)}, ${item.outcome||item.launch}`:`Native ${item.nativeId}, ${item.lifecycle}, ${item.parentNativeId?'reported child of '+item.parentNativeId:'parent session'}`;return `<li data-session="${row.type==='session'?escapeHtml(item.id):''}"><a href="${link({run:target.run,invocation:state.invocation.id,phase:row.type==='attempt'?item.operationKey:null,attempt:row.type==='attempt'?item.id:item.attemptId,session:row.type==='session'?item.id:null})}">${escapeHtml(label)}</a></li>`}).join('') || '<li>No recorded rows.</li>'}</ul></details></div>
    <div class="page-controls section-body"><button type="button" data-action="previous-attempts" ${state.attemptPage.length>1?'':'disabled'}>Previous attempts</button><button type="button" data-action="more-attempts" ${state.attemptsMore?'':'disabled'}>Next attempts</button><button type="button" data-action="previous-sessions" ${state.sessionPage.length>1?'':'disabled'}>Previous sessions</button><button type="button" data-action="more-sessions" ${state.sessionsMore?'':'disabled'}>Next sessions</button></div></section>`;
}
function eventSummary(event) {
  const data = event.data || {};
  return [data.operationKey,data.attemptId && `attempt ${short(data.attemptId)}`,data.sessionId && `session ${short(data.sessionId)}`,data.captureId && `capture ${short(data.captureId)}`,data.outcome,data.lifecycle].filter(Boolean).join(' - ') || 'Saved observation';
}
function reconcileChildren(container, items, key, create, update) {
  const old=new Map([...container.children].filter(node=>node.dataset.key||node.dataset.id||node.dataset.cursor).map(node=>[node.dataset.key||node.dataset.id||node.dataset.cursor,node]));
  items.forEach((item,index)=>{
    const identity=key(item),node=old.get(identity)||create(item);
    node.dataset.key=identity;
    update(node,item);
    if(container.children[index]!==node)container.insertBefore(node,container.children[index]||null);
    old.delete(identity);
  });
  for(const node of old.values())node.remove();
  for(const node of [...container.children].slice(items.length))node.remove();
}
function renderEventList() {
  const list = document.getElementById('event-list'); if (!list) return;
  const selected = route().attempt;
  const captured = new Map(state.captures.map(item=>[item.id,item.attemptId]));
  if(state.selectedCaptureTarget)captured.set(state.selectedCaptureTarget.id,state.selectedCaptureTarget.attemptId);
  const events = selected ? state.events.filter(event => event.data.attemptId===selected || captured.get(event.data.captureId)===selected) : state.events;
  reconcileChildren(list,events,event=>event.cursor,event=>{
    const row=document.createElement('article');row.className='event-row';row.dataset.cursor=event.cursor;
    const time=document.createElement('time');time.textContent=readableTime(event.data.at);
    const kind=document.createElement('span');kind.className='monospace';kind.textContent=event.kind;
    const summary=document.createElement('span');summary.append(document.createTextNode(eventSummary(event)+' '));
    const anchor=document.createElement('a');anchor.href=link({run:state.run.id,invocation:state.invocation.id,cursor:event.cursor});
    anchor.setAttribute('aria-label','Inspect saved event '+event.cursor);anchor.textContent='#'+event.cursor;
    summary.append(anchor);row.append(time,kind,summary);return row;
  },(row,event)=>{row.dataset.selected=String(state.selectedEventCursor===event.cursor)});
  if(!events.length && !list.firstElementChild){const empty=document.createElement('p');empty.className='state-message';empty.textContent='No saved events in this window.';list.append(empty);}
  const earlier = document.getElementById('earlier-events'); if (earlier) earlier.disabled=!state.earlier;
  const pending = document.getElementById('pending-events'); if (pending) { pending.textContent=state.pending ? `${state.pending} new events - return to latest` : ''; pending.hidden=!state.pending; }
}
function inspector(target) {
  const invocation = state.invocation;
  const session=target.session ? state.sessions.find(item=>item.id===target.session) : null;
  const selected = (target.attempt || session?.attemptId) ? state.attempts.find(item=>item.id===(target.attempt||session?.attemptId)) : target.phase ? state.attempts.find(item=>item.operationKey===target.phase) : null;
  const title = session ? `Native session ${session.nativeId}` : selected?.operationKey || 'Invocation evidence';
  const captureButtons = state.captures.map(item=>`<button type="button" data-action="open-capture" data-id="${escapeHtml(item.id)}">${escapeHtml(item.channel)} - ${escapeHtml(item.state)} - ${escapeHtml(short(item.id))}</button>`).join('') || '<p>No saved captures in this page.</p>';
  const agent = selected?.agent;
  return `<section class="surface" id="inspector" aria-labelledby="inspector-heading"><div class="section-heading"><div><h2 id="inspector-heading" tabindex="-1">${escapeHtml(title)}</h2><small>${escapeHtml(state.run.id)} / ${escapeHtml(invocation.id)}${selected?' / '+escapeHtml(selected.operationKey)+' / '+escapeHtml(selected.id):''}${session?' / '+escapeHtml(session.id):''}</small></div><a href="${link({run:state.run.id,invocation:invocation.id})}" data-action="return-timeline">Return to timeline</a></div>
    <div class="detail-grid"><div><details open><summary>Request and result</summary><p>${escapeHtml(state.run.requestPreview || 'Request preview unavailable. Open the saved request capture if present.')}</p><dl class="facts"><dt>Outcome</dt><dd id="inspector-outcome">${escapeHtml(selected?.outcome || outcome(invocation)[0])}</dd><dt>Launch</dt><dd>${escapeHtml(selected?.launch || 'Not applicable')}</dd><dt>Evidence</dt><dd>${escapeHtml(selected?.evidence || (selected?'No saved evidence for this attempt':'No attempt selected'))}</dd></dl></details>
    ${session?`<details open><summary>Native session evidence</summary><dl class="facts"><dt>Native identity</dt><dd>${escapeHtml(session.nativeId)}</dd><dt>Reported parent</dt><dd>${escapeHtml(session.parentNativeId || 'Parent session')}</dd><dt>Lifecycle</dt><dd>${escapeHtml(session.lifecycle)}</dd><dt>Shared managed attempt</dt><dd>${escapeHtml(session.attemptId)}</dd><dt>Usage</dt><dd>${escapeHtml(session.usage?.state==='unknown'?'Unknown':`${session.usage.tokens} tokens (${session.usage.scope==='includes-children'?'includes children; do not add to child usage':'this session only'})`)}</dd><dt>Loaded skills</dt><dd>${escapeHtml(Array.isArray(session.loadedSkills)?session.loadedSkills.join(', '):'Unknown')}</dd></dl><p>Reported native sessions share a managed attempt. Their usage is evidence, not additional managed allowance.</p></details>`:''}
    <div id="outcome-explanation">${(invocation.outcome==='failed'||invocation.outcome==='needs_input')?`<details open><summary>${invocation.outcome==='failed'?'Failure explanation':'Question and next input'}</summary><p>${escapeHtml(selected?.evidence || (invocation.outcome==='failed'?'The saved invocation failed. Inspect recorded events and captures for the cause.':state.question?.available?state.question.question:'The saved question text is unavailable.'))}</p>${state.question?.available?`<p>${escapeHtml(state.question.context)}</p>`:''}</details>`:''}</div>
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
    <div class="chip-list"><span id="execution-state">${chip(label,tone)}</span><span id="cleanup-state">${chip(state.clearance?'Operator confirmed':invocation?.cleanup==='complete'?'Automatically checked':invocation?.cleanup==='unknown'?'Manual cleanup required':'Cleanup unknown',state.clearance||invocation?.cleanup==='complete'?'success':'attention')}</span>${chip('Capture: inspect saved records')}<span id="observation-state"></span></div></div></div>
    <div id="attention-slot">${invocation ? attention(invocation) : '<div class="state-message">This run has no saved invocation.</div>'}</div>
    ${state.gap?'<div class="attention" role="status">A saved event gap was detected. Details were rebuilt from a new saved snapshot; continuity is unknown.</div>':''}
    <section class="surface"><div class="section-heading"><h2>Invocation history</h2><small>Each invocation starts at the current workflow entry</small></div><div class="section-body">${invocationLinks(target)}</div></section>
    ${invocation ? `${timeline(target)}${inspector(target)}` : ''}
    <details class="surface"><summary class="section-body">Repository storage and maintenance</summary><div class="section-body"><p>History size, backups, measurement time, and growth have not been measured by this host.</p><p>Stop the dashboard process before exceptional idle maintenance. Closing this tab leaves the host running.</p></div></details>`;
  renderEventList();
  state.renderedAttention=invocation?attention(invocation):null;
  showConnection(state.connectionKind||'connecting',connection.textContent||'Catching up');
  updateCollapsedRows();
  const eventList=document.getElementById('event-list');
  if(eventList) {
    if(target.cursor) {const selected=eventList.querySelector(`[data-cursor="${CSS.escape(target.cursor)}"]`);if(selected)eventList.scrollTop=selected.offsetTop-eventList.offsetTop;}
    else eventList.scrollTop=eventList.scrollHeight;
  }
  document.querySelectorAll('.phase-bar').forEach(bar=>{bar.style.setProperty('--bar-left',bar.dataset.left+'%');bar.style.setProperty('--bar-width',bar.dataset.width+'%')});
  if (target.phase || target.attempt || target.session) document.getElementById('inspector-heading')?.focus({preventScroll:true});
}

function rememberSessionParents(sessions) {
  for(const session of sessions)state.sessionParents.set(session.attemptId+':'+session.nativeId,{
    id:session.id,attemptId:session.attemptId,parentNativeId:session.parentNativeId,
  });
}

function updateCollapsedRows() {
  const byId=new Map(state.sessions.map(item=>[item.id,item]));
  for(const row of document.querySelectorAll('.timeline-lane[data-session]')) {
    const id=row.dataset.session;if(!id)continue;
    let session=byId.get(id),hidden=false;const seen=new Set();
    while(session?.parentNativeId) {
      const parent=state.sessionParents.get(session.attemptId+':'+session.parentNativeId);
      if(!parent || seen.has(parent.id))break;
      seen.add(parent.id);if(state.collapsed.has(parent.id))hidden=true;session=parent;
    }
    row.hidden=hidden;
    const textLink=document.querySelector(`.timeline-text [data-session="${CSS.escape(id)}"]`);if(textLink)textLink.hidden=hidden;
  }
}
async function loadRoute(reader = null) {
  if (!state.token) return;
  const generation=++state.routeGeneration, target=route();
  state.validatedParent=null;
  app.setAttribute('aria-busy','true');
  try {
    if (!target.run) { await loadIndex(generation);if(generation===state.routeGeneration)state.lastUpdate=new Date(); return; }
    if (!idPattern.test(target.run)) { routeError('Invalid run link. The saved record was not selected.'); return; }
    if (state.run?.id!==target.run) state.invocationPage=[0];
    await loadRun(target,generation,reader);
    if (generation!==state.routeGeneration) return;
    state.lastUpdate=new Date();
  } catch(error) { if (generation===state.routeGeneration) routeError(error.message,state.validatedParent); }
}
function readerSnapshot() {
  const active=document.activeElement;
  const selection=window.getSelection(),selectedText=selection?.toString()||'';
  const path=node=>{if(!node||!app.contains(node))return null;const parts=[];while(node!==app){const parent=node.parentNode;if(!parent)return null;parts.unshift([...parent.childNodes].indexOf(node));node=parent;}return parts;};
  return {top:window.scrollY,timeline:document.querySelector('.timeline-scroll')?.scrollLeft||0,events:document.getElementById('event-list')?.scrollTop||0,
    route:route(),pages:{invocations:state.invocationPage.slice(-128),attempts:state.attemptPage.slice(-128),captures:state.captureSummaryPage.slice(-128),sessions:state.sessionPage.slice(-128),lane:state.lanePage},
    eventWindowEnd:state.events.at(-1)?.cursor||null,capture:state.selectedCapture?{id:state.selectedCapture,after:state.captureAfter}:null,
    disclosures:[...app.querySelectorAll('details')].map(item=>({name:item.querySelector('summary')?.textContent?.trim(),open:item.open})),
    selection:selection&&!selection.isCollapsed&&selectedText.length<=2048?{anchor:path(selection.anchorNode),anchorOffset:selection.anchorOffset,focus:path(selection.focusNode),focusOffset:selection.focusOffset,text:selectedText}:null,
    focus:{id:active?.id,href:active?.getAttribute('href'),action:active?.getAttribute('data-action'),item:active?.getAttribute('data-id'),start:active?.selectionStart,end:active?.selectionEnd}};
}
async function restoreReader(reader) {
  if(!reader)return;
  if(state.invocation && reader.eventWindowEnd && !route().cursor && state.events.at(-1)?.cursor!==reader.eventWindowEnd) {
    try {const page=await api(`/api/invocations/${state.invocation.id}/events?before=${BigInt(reader.eventWindowEnd)+1n}&limit=200`);state.events=page.events;state.earlier=page.hasEarlier;renderEventList();}
    catch { /* Keep the current saved window when older evidence cannot be read. */ }
  }
  if(state.invocation && reader.capture?.id) {
    try {state.selectedCapture=reader.capture.id;state.captureAfter=reader.capture.after;state.capturePending=false;state.captureVersion++;
      state.capturePage=await api(`/api/invocations/${state.invocation.id}/captures/${reader.capture.id}?after=${reader.capture.after}&limit=50`);renderCapture();}
    catch { /* Keep other saved details available. */ }
  }
  for(const detail of app.querySelectorAll('details')) {
    const saved=reader.disclosures?.find(item=>item.name===detail.querySelector('summary')?.textContent?.trim());
    if(saved)detail.open=saved.open;
  }
  const timeline=document.querySelector('.timeline-scroll');if(timeline)timeline.scrollLeft=reader.timeline||0;
  const events=document.getElementById('event-list');if(events)events.scrollTop=reader.events||0;
  const identity=reader.focus||{};
  const focus=identity.id?document.getElementById(identity.id):identity.href?[...app.querySelectorAll('a[href]')].find(item=>item.getAttribute('href')===identity.href):identity.action?[...document.querySelectorAll('[data-action]')].find(item=>item.getAttribute('data-action')===identity.action&&item.getAttribute('data-id')===identity.item):null;
  if(focus){focus.focus({preventScroll:true});if(typeof identity.start==='number'&&typeof focus.setSelectionRange==='function')focus.setSelectionRange(identity.start,identity.end);}
  const selection=reader.selection;
  if(selection?.anchor&&selection.focus) {
    const resolve=parts=>parts.reduce((node,index)=>node?.childNodes[index],app);
    const anchor=resolve(selection.anchor),end=resolve(selection.focus);
    if(anchor&&end) {const current=window.getSelection();try{current.setBaseAndExtent(anchor,selection.anchorOffset,end,selection.focusOffset);if(current.toString()!==selection.text)current.removeAllRanges();}catch {current.removeAllRanges();}}
  }
  window.scrollTo(0,reader.top||0);
}
async function resnapshotPreservingReader() {
  const reader=readerSnapshot();
  await loadRoute(reader);
  await restoreReader(reader);
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
            if(state.connected && !state.frozen)showConnection('connected','Connected - saved cursor '+state.cursor);
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
  if(event.kind==='run.created' && !state.runs.some(run=>run.id===event.data?.runId)) {
    state.newRuns++;
    if(!route().run) {
      let notice=document.getElementById('new-runs-notice');
      if(!notice) {notice=document.createElement('div');notice.id='new-runs-notice';notice.className='attention';document.querySelector('.heading-row')?.after(notice);}
      notice.innerHTML=`<p>${state.newRuns} new run${state.newRuns===1?'':'s'} recorded while you were reading.</p><button type="button" data-action="refresh-index">Refresh run order</button>`;
    }
  }
  if(state.frozen) { if(state.invocation && event.data?.invocationId===state.invocation.id){state.pending++;updatePending();} return; }
  if(!route().run && state.runs.some(run=>run.id===event.data?.runId || run.latestInvocation?.id===event.data?.invocationId)) void refreshIndexCard(event);
  if(state.invocation && event.data?.invocationId===state.invocation.id) {
    if(state.events.length && BigInt(event.cursor)<=BigInt(state.events.at(-1).cursor)) return;
    if(event.kind==='capture.created' && !state.captures.some(item=>item.id===event.data.captureId)) {
      if(state.captures.length<50)state.captures.push({id:event.data.captureId,channel:event.data.channel,state:'open',attemptId:event.data.attemptId||null});
      else state.capturesMore=true;
      updateCaptureButtons();
    }
    if(event.kind==='capture.appended') {
      const capture=state.captures.find(item=>item.id===event.data.captureId);
      if(capture) {capture.state=event.data.state;updateCaptureButtons();}
      if(capture?.channel==='request' && event.data.state==='complete')void refreshQuestion();
      if(state.selectedCapture===event.data.captureId && state.capturePage) {
        state.capturePending=true;state.captureVersion++;
        void followCapture();
      }
    }
    const list=document.getElementById('event-list');
    const selection=window.getSelection();
    const readingText=selection && !selection.isCollapsed && list?.contains(selection.anchorNode);
    const away=list && list.scrollHeight-list.scrollTop-list.clientHeight>48;
    if(['invocation.finalized','invocation.running','invocation.shutting_down','owner.cleared'].includes(event.kind)) void refreshCurrentOutcome();
    if(readingText || away || state.selectedEventCursor) { state.pending++; updatePending(); return; }
    state.events.push(event); if(state.events.length>200) {state.events.shift(); state.earlier=true;}
    renderEventList(); if(list)list.scrollTop=list.scrollHeight;
  }
}
async function refreshQuestion() {
  const id=state.invocation?.id;if(!id)return;
  try {const question=await api(`/api/invocations/${id}/question`);if(state.invocation?.id!==id)return;state.question=question;
    updateAttention();
    updateOutcomeExplanation();
  } catch { /* Keep the saved view until a successful snapshot. */ }
}
function updateAttention() {
  const slot=document.getElementById('attention-slot');if(!slot||!state.invocation)return;
  const markup=attention(state.invocation);
  if(markup!==state.renderedAttention){slot.innerHTML=markup;state.renderedAttention=markup;}
}
function updateOutcomeExplanation() {
  const slot=document.getElementById('outcome-explanation'),invocation=state.invocation;
  if(!slot||!invocation)return;
  const needsExplanation=invocation.outcome==='failed'||invocation.outcome==='needs_input';
  let detail=slot.querySelector('details');
  if(!needsExplanation){detail?.remove();return;}
  if(!detail){detail=document.createElement('details');detail.open=true;detail.append(document.createElement('summary'));slot.append(detail);}
  detail.querySelector('summary').textContent=invocation.outcome==='failed'?'Failure explanation':'Question and next input';
  const selected=state.displayTarget?.attempt&&state.attempts.find(item=>item.id===state.displayTarget.attempt);
  const message=selected?.evidence||(invocation.outcome==='failed'?'The saved invocation failed. Inspect recorded events and captures for the cause.':state.question?.available?state.question.question:'The saved question text is unavailable.');
  const paragraphs=[message,...(state.question?.available?[state.question.context]:[])];
  paragraphs.forEach((value,index)=>{let paragraph=detail.querySelectorAll('p')[index];if(!paragraph){paragraph=document.createElement('p');detail.append(paragraph);}if(paragraph.textContent!==value)paragraph.textContent=value;});
  for(const extra of [...detail.querySelectorAll('p')].slice(paragraphs.length))extra.remove();
}
async function refreshIndexCard(event) {
  const run=state.runs.find(item=>item.id===event.data?.runId || item.latestInvocation?.id===event.data?.invocationId);
  if(!run)return;
  const generation=++state.cardRefreshSequence;state.cardGenerations.set(run.id,generation);
  try {
    const latest=await api(`/api/runs/${run.id}`);
    if(route().run||state.cardGenerations.get(run.id)!==generation)return;
    const index=state.runs.findIndex(item=>item.id===run.id);if(index<0)return;
    state.runs[index]=latest;
    const cards=document.getElementById('cards');
    const existing=cards?.querySelector(`[data-run="${CSS.escape(run.id)}"]`);
    if(!existing)return;
    const replacement=document.createElement('div');replacement.innerHTML=card(latest);
    const fresh=replacement.firstElementChild;
    existing.dataset.outcome=fresh.dataset.outcome;
    existing.dataset.cardSearch=fresh.dataset.cardSearch;
    const oldHead=existing.querySelector('.card-head'),newHead=fresh.querySelector('.card-head');
    const oldLink=oldHead?.querySelector('a'),newLink=newHead?.querySelector('a');
    if(oldLink&&newLink){oldLink.textContent=newLink.textContent;oldLink.setAttribute('aria-label',newLink.getAttribute('aria-label'));}
    for(const selector of ['.workflow','p']) {
      const old=oldHead?.querySelector(selector),next=newHead?.querySelector(selector);if(old&&next)old.textContent=next.textContent;
    }
    for(const selector of ['.mini-activity','.card-foot']) {
      const old=existing.querySelector(selector),next=fresh.querySelector(selector);if(old&&next)old.replaceWith(next);
    }
  } catch { /* Keep the last saved card until the next saved snapshot. */ }
}
function updateCaptureButtons() {
  const container=document.querySelector('.capture-list');if(!container)return;
  reconcileChildren(container,state.captures,item=>item.id,item=>{
    const button=document.createElement('button');button.type='button';button.dataset.action='open-capture';button.dataset.id=item.id;return button;
  },(button,item)=>{button.textContent=`${item.channel} - ${item.state} - ${short(item.id)}`});
  if(!state.captures.length && !container.firstElementChild){const empty=document.createElement('p');empty.textContent='No saved captures in this page.';container.append(empty);}
  const more=document.querySelector('[data-action="more-captures"]');if(more)more.disabled=!state.capturesMore;
}
async function refreshCurrentOutcome() {
  if(!state.invocation)return;
  const id=state.invocation.id,generation=++state.outcomeGeneration;
  try {
    const page=await api(`/api/invocations/${id}?limit=1`);
    if(state.invocation?.id!==id||generation!==state.outcomeGeneration)return;
    const previous=outcome(state.invocation)[0],previousCleanup=state.invocation.cleanup,previousClearance=state.clearance?.id;
    state.invocation=page.invocation;state.clearance=page.clearance;
    if(state.invocation.outcome==='needs_input'||state.invocation.outcome==='failed') {
      try {state.question=await api(`/api/invocations/${id}/question`);} catch {state.question=null;}
    }
    if(state.invocation?.id!==id||generation!==state.outcomeGeneration)return;
    const [label,tone]=outcome(state.invocation);
    const execution=document.getElementById('execution-state');if(execution)execution.innerHTML=chip(label,tone);
    const cleanup=document.getElementById('cleanup-state');if(cleanup)cleanup.innerHTML=chip(state.clearance?'Operator confirmed':state.invocation.cleanup==='complete'?'Automatically checked':state.invocation.cleanup==='unknown'?'Manual cleanup required':'Cleanup unknown',state.clearance||state.invocation.cleanup==='complete'?'success':'attention');
    updateAttention();
    const inspectorOutcome=document.getElementById('inspector-outcome');if(inspectorOutcome&&!state.displayTarget?.attempt)inspectorOutcome.textContent=label;
    updateOutcomeExplanation();
    if(previous!==label||previousCleanup!==state.invocation.cleanup||previousClearance!==state.clearance?.id)announcement.textContent='Selected invocation updated: '+label+(state.invocation.cleanup==='unknown'?'; manual cleanup required':'');
  } catch { /* Keep the last saved display until a successful snapshot. */ }
}
function updatePending() {
  const button=document.getElementById('pending-events');
  if(button) { button.hidden=false; button.textContent=state.pending+' new events - return to latest'; }
}
async function latestEvents() {
  if(!state.invocation)return;
  const page=await api(`/api/invocations/${state.invocation.id}/events?tail=1&limit=200`);
  state.events=page.events; state.earlier=page.hasEarlier; state.pending=0; state.frozen=false;state.selectedEventCursor=null;
  if(route().cursor){history.replaceState({...history.state},'',link({run:state.run.id,invocation:state.invocation.id}));lastNavigatedHref=location.href;}
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
  state.selectedCapture=id;state.captureAfter=0;state.capturePending=false;state.captureVersion++;
  const page=await api(`/api/invocations/${state.invocation.id}/captures/${id}?limit=50`);
  if(state.selectedCapture!==id)return;
  state.capturePage=page;
  renderCapture();
}
function renderCapture() {
  const panel=document.getElementById('capture-view'); if(!panel||!state.capturePage)return;
  const page=state.capturePage;
  if(panel.dataset.captureId!==state.selectedCapture || panel.dataset.after!==String(state.captureAfter)) {
    panel.innerHTML=`<div class="section-body"><h3>Saved capture ${escapeHtml(short(state.selectedCapture))}</h3><p data-capture-status></p><p data-capture-page></p><pre class="capture-text" id="capture-text"></pre><div class="controls"><button type="button" data-action="capture-start">Start of capture</button><button type="button" data-action="more-output">Load next saved text</button></div></div>`;
    panel.dataset.captureId=state.selectedCapture;panel.dataset.after=String(state.captureAfter);
  }
  panel.querySelector('[data-capture-status]').textContent=`${page.channel||'Channel unknown'} - ${page.state}${['partial','pruned','unknown'].includes(page.state)?' - some saved output may be unavailable':''}`;
  panel.querySelector('[data-capture-page]').textContent=`Showing after chunk ${state.captureAfter}; next chunk ${page.nextSequence}.`;
  const pre=panel.querySelector('#capture-text'),wasBottom=pre.scrollHeight-pre.scrollTop-pre.clientHeight<=48;
  const content=page.chunks.map(chunk=>chunk.text).join('');
  if(content.startsWith(pre.textContent))pre.append(document.createTextNode(content.slice(pre.textContent.length)));
  else if(pre.textContent!==content)pre.textContent=content;
  if(wasBottom)pre.scrollTop=pre.scrollHeight;
  panel.querySelector('[data-action="capture-start"]').disabled=!state.captureAfter;
  const more=panel.querySelector('[data-action="more-output"]');more.disabled=!(page.hasMore||state.capturePending);
  more.textContent=page.hasMore?'Load next saved text':state.capturePending?'Load new saved text':'Load next saved text';
}
function captureAtBottom() {
  const pre=document.getElementById('capture-text');
  const selection=window.getSelection();
  return !!pre && pre.scrollHeight-pre.scrollTop-pre.clientHeight<=48 && !(selection&&!selection.isCollapsed&&(pre.contains(selection.anchorNode)||pre.contains(selection.focusNode)));
}
async function followCapture(force=false) {
  if(!state.capturePending||state.captureRefreshing||state.frozen||!state.selectedCapture||!state.capturePage)return;
  if(!force&&!captureAtBottom()){renderCapture();return;}
  const page=state.capturePage,id=state.selectedCapture,invocationId=state.invocation?.id;
  if(page.chunks.length>=50){page.hasMore=true;renderCapture();return;}
  const version=state.captureVersion;state.captureRefreshing=true;
  try {
    const next=await api(`/api/invocations/${invocationId}/captures/${id}?after=${page.nextSequence}&limit=${50-page.chunks.length}`);
    if(state.selectedCapture!==id||state.capturePage!==page)return;
    const encoder=new TextEncoder();let bytes=page.chunks.reduce((total,chunk)=>total+encoder.encode(chunk.text).length,0),accepted=0;
    for(const chunk of next.chunks) {
      const size=encoder.encode(chunk.text).length;
      if(bytes+size>1047552)break;
      page.chunks.push(chunk);bytes+=size;accepted++;
    }
    page.nextSequence=page.chunks.at(-1)?.sequence??page.nextSequence;
    page.hasMore=next.hasMore||accepted<next.chunks.length;page.state=next.state;
    state.capturePending=state.captureVersion!==version;
    renderCapture();
  } catch { if(state.selectedCapture===id)renderCapture(); }
  finally {
    state.captureRefreshing=false;
    if(state.capturePending && (state.selectedCapture!==id || (state.capturePage===page&&!page.hasMore&&captureAtBottom())))void followCapture();
  }
}
async function moreOutput() {
  const old=state.capturePage; if(!old)return;
  if(!old.hasMore){await followCapture(true);return;}
  const next=await api(`/api/invocations/${state.invocation.id}/captures/${state.selectedCapture}?after=${old.nextSequence}&limit=50`);
  state.captureAfter=old.nextSequence;state.capturePage=next;state.capturePending=false;renderCapture();
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
      state.sessions=page.sessions;rememberSessionParents(page.sessions);state.sessionsNext=page.nextCursor;state.sessionsMore=page.hasMore;
    } else {
      const key=kind==='attempts'?'afterAttempt':'afterCapture';
      const page=await api(`/api/invocations/${id}?${key}=${cursor}&limit=50`);
      if(kind==='attempts'){state.attempts=page.attempts;state.attemptsNext=page.attemptsNextCursor;state.attemptsMore=page.hasMoreAttempts;}
      else{state.captures=page.captures;state.capturesNext=page.capturesNextCursor;state.capturesMore=page.hasMoreCaptures;}
    }
  } catch(error) { stack.splice(0,stack.length,...previousStack);throw error; }
  state.lanePage=0;
  const reader=readerSnapshot();renderRun(route());await restoreReader(reader);
}
app.addEventListener('input',event=>{if(event.target.id==='run-search'){state.query=event.target.value;renderCards();}});
app.addEventListener('scroll',event=>{if(event.target.id==='capture-text'&&state.capturePending)void followCapture();},true);
history.scrollRestoration='manual';
let lastNavigatedHref=location.href;
let recentReading={top:0,at:0};
window.addEventListener('scroll',()=>{
  const now=performance.now();
  if(now-recentReading.at>1500 || window.scrollY>recentReading.top)recentReading={top:window.scrollY,at:now};
},{passive:true});
app.addEventListener('click',async event=>{
  const anchor=event.target.closest('a[href^="#"]');
  if(!anchor || event.defaultPrevented || event.button!==0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)return;
  event.preventDefault();
  const current=route(),before=readerSnapshot(),oldRun=current.run;
  const returning=anchor.dataset.action==='return-timeline';
  const selected=state.displayTarget;
  const fallbackOrigin=selected?link({run:selected.run,invocation:state.invocation?.id,phase:selected.phase,attempt:selected.attempt,session:selected.session}):null;
  const originHref=returning?(history.state?.origin?.href||fallbackOrigin):null;
  before.focus={href:anchor.getAttribute('href')};
  if(performance.now()-recentReading.at<1500 && recentReading.top>before.top)before.top=recentReading.top;
  recentReading={top:0,at:0};
  history.replaceState({...history.state,reader:before},'');
  history.pushState(!returning&&anchor.matches('.phase-bar, .timeline-text a')?{origin:{href:anchor.getAttribute('href')}}:{},'',anchor.getAttribute('href'));
  lastNavigatedHref=location.href;
  if(returning)[...document.querySelectorAll('.phase-bar, .timeline-text a')].find(item=>item.getAttribute('href')===originHref)?.focus({preventScroll:true});
  await loadRoute(returning?before:null);
  if(route().run===oldRun) {window.scrollTo(0,before.top);}
  else window.scrollTo(0,0);
  if(returning) {
    const phase=[...document.querySelectorAll('.phase-bar, .timeline-text a')].find(item=>item.getAttribute('href')===originHref);
    (phase||document.querySelector('.timeline-scroll'))?.focus({preventScroll:true});
  }
});
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
    else if(action==='next-lanes'||action==='previous-lanes'){const reader=readerSnapshot();state.lanePage=Math.max(0,state.lanePage+(action==='next-lanes'?1:-1));renderRun(route());await restoreReader(reader);document.querySelector(`[data-action="${action}"]`)?.focus({preventScroll:true});}
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
      updateCollapsedRows();
    }
    else if(action==='freeze'){
      if(state.frozen)await latestEvents();else{state.frozen=true;showConnection('frozen','Frozen at saved cursor '+state.cursor);document.querySelectorAll('[data-action="freeze"]').forEach(item=>{item.setAttribute('aria-pressed','true');item.textContent='Follow latest events'})}
    }
  } catch(error){announcement.textContent=error.message;const box=document.createElement('div');box.className='error-message';box.setAttribute('role','alert');box.textContent=error.message;app.prepend(box);}
});
function browserRouteChanged(){if(location.href===lastNavigatedHref)return;lastNavigatedHref=location.href;const reader=history.state?.reader;void loadRoute(reader).then(()=>restoreReader(reader));}
window.addEventListener('hashchange',browserRouteChanged);
window.addEventListener('popstate',browserRouteChanged);

export async function start(ticket) {
  try {
    await redeem(ticket);
    // The head is sampled before the first snapshot, so later committed events are replayed by SSE.
    const head=await api('/api/events/head');state.cursor=head.cursor;
    await loadRoute();
    void connect();
  } catch(error) {showConnection('disconnected','History unavailable');errorView(error.message);}
}
