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
  events: [], earlier: false, deferredEvents: [], selectedCapture: null, capturePage: null, captureAfter: 0, capturePending: false, captureVersion: 0, captureRefreshing: false, streamAbort: null,
  routeGeneration: 0,
  snapshotGeneration: 0, readAbort: new AbortController(), streamGeneration: 0, snapshotting: false, projection: null, projecting: false, receivedCursor: '0',
  error: null, connectionKind: null, validatedParent: null,
  notificationPreferences: null, reminderGroups: null, preferencesStatus: '', preferencesError: false, acknowledgment: null, acknowledgmentStatus: '', acknowledgmentError: false,
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
  if(chipSlot) chipSlot.innerHTML=chip(kind==='disconnected'?`Disconnected - last update ${state.lastUpdate?state.lastUpdate.toLocaleTimeString():'unknown'}`:kind==='frozen'?'Frozen at saved cursor '+state.cursor+'; navigation follows latest history':kind==='connecting'?'Catching up':'Connected',kind==='connected'?'success':'attention');
  if (changed) announcement.textContent = kind==='disconnected'?text:kind==='connected'?'Observation connected.':kind==='connecting'?'Catching up with saved observations.':'Observation frozen.';
}
async function api(path, options = {}) {
  const owner=state.readAbort;
  const signal=AbortSignal.any([owner.signal,AbortSignal.timeout(10000)]);
  const response = await fetch(path, { ...options, signal, cache:'no-store', headers: { Authorization:'Bearer ' + state.token, ...options.headers } });
  if (!response.ok) {
    let message = `History request failed (${response.status}).`;
    try { message = (await response.json()).error || message; } catch {}
    const error = new Error(message); error.status = response.status; throw error;
  }
  const result=await response.json();
  signal.throwIfAborted();
  return result;
}
async function writeNotification(path, body) {
  const response = await fetch(path, { method:'POST', cache:'no-store', signal:AbortSignal.timeout(10000),
    headers:{ Authorization:'Bearer '+state.token, 'Content-Type':'application/json' }, body:JSON.stringify(body) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || `Save failed (${response.status}).`);
  return result;
}
async function loadNotificationPreferences() {
  try {
    const [preferences, reminders] = await Promise.all([api('/api/notifications/preferences'), api('/api/notifications/reminders?limit=1')]);
    state.notificationPreferences = preferences; state.reminderGroups = reminders.groups; state.preferencesError = false;
  }
  catch (error) { state.preferencesStatus = error.message; state.preferencesError = true; }
}
function latestReminderStatus() {
  const latest=state.reminderGroups?.[0];
  return latest ? latest.state==='submitted' ? 'Latest reminder submitted to the notification service. Desktop visibility is unverified.'
    : latest.reason==='unbound_sender' ? 'Latest reminder could not be sent because no installed sender is available.'
    : latest.cleanup==='unknown' ? 'Latest reminder submission or cleanup is unknown. The host retains its claim.'
    : `Latest reminder status: ${latest.state}. Desktop visibility is unverified.` : 'No reminder group saved yet.';
}
async function refreshReminderGroups() {
  const reminders=await api('/api/notifications/reminders?limit=1');
  state.reminderGroups=reminders.groups;
  const label=document.getElementById('latest-reminder-status');
  if(label)label.textContent=latestReminderStatus();
}
function preferencesControls() {
  const preferences=state.notificationPreferences;
  return `<details class="surface"><summary class="section-body">Notification preferences</summary><div class="section-body">
    <p class="muted">Repository-wide settings. Success notices and reminders start off. Reminders wait 15 minutes after this host starts or you enable them.</p>
    <form id="notification-preferences" class="notification-form"><label><input type="checkbox" name="successNotices" ${preferences?.successNotices?'checked':''}> Success notices</label>
    <label><input type="checkbox" name="reminders" ${preferences?.reminders?'checked':''}> Reminders</label>
    <button type="submit" ${preferences?'':'disabled'}>Save notification preferences</button></form>
    <p id="preferences-status" class="notification-status" role="${state.preferencesError?'alert':'status'}">${escapeHtml(state.preferencesStatus || (preferences?'Saved settings are shown above.':'Preferences unavailable.'))}</p>
    <p id="latest-reminder-status" class="muted">${escapeHtml(latestReminderStatus())}</p></div></details>`;
}
function acknowledgmentControls(invocation) {
  if (!invocation || invocation.stage !== 'finalized') return '';
  return `<section class="surface"><div class="section-heading"><h2>Selected invocation acknowledgment</h2></div><div class="section-body">
    <p>Acknowledgment records that you saw this finalized invocation. It does not answer a saved question or change the run result or cleanup.</p>
    <div class="controls"><button type="button" data-action="acknowledge-invocation" aria-describedby="acknowledgment-status">${state.acknowledgment?'Acknowledged':'Acknowledge selected invocation'}</button>
    <span id="acknowledgment-status" class="notification-status" role="${state.acknowledgmentError?'alert':'status'}">${escapeHtml(state.acknowledgmentStatus || (state.acknowledgment?'Acknowledged on '+readableTime(state.acknowledgment.acknowledgedAt):'No acknowledgment saved.'))}</span></div></div></section>`;
}
function errorView(message, parent) {
  app.removeAttribute('aria-busy');
  app.innerHTML = `<div class="error-message" role="alert"><h1>History unavailable</h1><p>${escapeHtml(message)}</p><p><a href="${parent || '#'}">${parent ? 'Return to saved parent' : 'Return to runs'}</a></p></div>`;
}
function readFailure(message) {
  const box=document.createElement('div');box.className='error-message';box.setAttribute('role','alert');box.textContent=message;app.prepend(box);
}
function routeError(message, parent) { state.error = message; errorView(message, parent); }
async function loadIndex(generation = state.routeGeneration, pages = state.runPage) {
  const anchor=pages.at(-1)??0,href=location.href,snapshot=state.snapshotGeneration;
  const page = await api(`/api/runs?after=${anchor}&limit=30`);
  if (generation !== state.routeGeneration||href!==location.href||snapshot!==state.snapshotGeneration) return;
  state.runPage=pages;
  state.runs = page.runs; state.runPageNext = page.nextCursor; state.runsHaveMore = page.hasMore;
  state.pending=0;state.deferredEvents=[];
  state.run = null; state.invocation = null; state.error = null;
  renderIndex();
  return true;
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
function matchesRun(run) {
  const latest=run.latestInvocation;
  const haystack=`${run.requestPreview || ''} ${run.workflow || ''} ${run.id} ${latest?.id || ''}`.toLowerCase();
  const current=latest?.outcome || latest?.stage || 'unknown';
  return haystack.includes(state.query.trim().toLowerCase()) && (state.filter==='all' || current===state.filter);
}
function renderCards() {
  const cards = document.getElementById('cards'); if (!cards) return;
  const matches = state.runs.filter(matchesRun);
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
    ${preferencesControls()}
    <details class="surface"><summary class="section-body">Repository storage and maintenance</summary><div class="section-body"><p>Saved history and backup sizes have not been measured by this host. No growth estimate is available.</p><p>Stop the dashboard process before exceptional idle maintenance. Closing this browser tab does not stop the host. After uninstall, a compatible installation is needed to read saved history.</p></div></details>`;
  renderCards();
}
async function loadRun(target, generation = state.routeGeneration, reader = null, restoreWindow) {
  const href=location.href,snapshot=state.snapshotGeneration;
  const current=()=>generation===state.routeGeneration&&href===location.href&&snapshot===state.snapshotGeneration;
  const run = await api(`/api/runs/${target.run}`);
  if(!current())return;
  state.validatedParent=link({run:target.run});
  const selectedId = target.invocation || run.latestInvocation?.id;
  if (selectedId && !idPattern.test(selectedId)) throw new Error('Invalid invocation link.');
  const sameReader=reader?.route?.run===target.run && (!reader.route.invocation||reader.route.invocation===selectedId);
  const savedPages=sameReader?reader.pages:null;
  const pageStack=value=>Array.isArray(value)&&value.length&&value.length<=128&&value.every(cursor=>Number.isSafeInteger(cursor)&&cursor>=0)?value.slice():[0];
  const invocationPage=pageStack(savedPages?.invocations??(state.run?.id===target.run?state.invocationPage:[0]));
  let attemptPage=pageStack(savedPages?.attempts);
  const captureSummaryPage=pageStack(savedPages?.captures);
  const sessionPage=pageStack(savedPages?.sessions);
  const lanePage=Number.isSafeInteger(savedPages?.lane)&&savedPages.lane>=0&&savedPages.lane<128?savedPages.lane:0;
  const selector = await api(`/api/runs/${target.run}/invocations?after=${invocationPage.at(-1) ?? 0}&limit=30`);
  if(!current())return;
  let detail = null, sessions = null, events = null, selectedEvent = null, selectedSession = null, selectedCaptureTarget = null, question = null;
  if (selectedId) {
    [detail,sessions,events] = await Promise.all([
      api(`/api/invocations/${selectedId}?afterAttempt=${attemptPage.at(-1)??0}&afterCapture=${captureSummaryPage.at(-1)??0}&limit=50`),
      api(`/api/invocations/${selectedId}/sessions?after=${sessionPage.at(-1)??0}&limit=50`),
      api(`/api/invocations/${selectedId}/events?tail=1&limit=200`),
    ]);
    if(!current())return;
    if (detail.invocation.runId !== target.run) throw new Error('Invocation does not belong to this run.');
    state.validatedParent=link({run:target.run,invocation:selectedId});
    if (target.cursor) {
      if (!/^\d{1,19}$/.test(target.cursor)) throw new Error('Invalid saved event cursor.');
      selectedEvent=await api(`/api/invocations/${selectedId}/events/${target.cursor}`);
      if(!current())return;
      events=await api(`/api/invocations/${selectedId}/events?before=${BigInt(target.cursor)+1n}&limit=200`);
      if(!current())return;
      if(selectedEvent?.data?.captureId) {
        if(!idPattern.test(selectedEvent.data.captureId))throw new Error('Saved event has an invalid capture identity.');
        selectedCaptureTarget=await api(`/api/invocations/${selectedId}/captures/${selectedEvent.data.captureId}?limit=1`);
        if(!current())return;
        if(selectedEvent.data.attemptId && selectedEvent.data.attemptId!==selectedCaptureTarget.attemptId)throw new Error('Saved event capture does not belong to its recorded attempt.');
      }
    }
    if (target.session) {
      if (!idPattern.test(target.session)) throw new Error('Invalid native session link.');
      selectedSession=await api(`/api/invocations/${selectedId}/sessions/${target.session}`);
      if(!current())return;
    }
    if(!selectedSession && selectedEvent?.data?.sessionId) {
      if(!idPattern.test(selectedEvent.data.sessionId))throw new Error('Saved event has an invalid native session identity.');
      selectedSession=await api(`/api/invocations/${selectedId}/sessions/${selectedEvent.data.sessionId}`);
      if(!current())return;
    }
    question=await api(`/api/invocations/${selectedId}/question`);
  }
  if (!current()) return;
  let attempts=detail?.attempts||[],attemptsNext=detail?.attemptsNextCursor||0,attemptsMore=detail?.hasMoreAttempts||false;
  const sessionList=sessions?.sessions?.slice()||[];
  if(selectedSession&&!sessionList.some(item=>item.id===selectedSession.id))sessionList.push(selectedSession);
  if (selectedSession && target.attempt && selectedSession.attemptId!==target.attempt) throw new Error('Native session does not belong to the selected attempt.');
  const eventAttemptId=selectedCaptureTarget?selectedCaptureTarget.attemptId:selectedEvent?.data?.attemptId;
  if (selectedEvent && target.attempt && eventAttemptId!==target.attempt) throw new Error('Saved event does not belong to the selected attempt.');
  const selectedAttemptId=target.attempt || selectedSession?.attemptId || eventAttemptId;
  if (selectedAttemptId && !idPattern.test(selectedAttemptId)) throw new Error('Invalid saved attempt link.');
  if ((selectedAttemptId && !attempts.some(item=>item.id===selectedAttemptId)) || (target.phase && !attempts.some(item=>item.operationKey===target.phase))) {
    try {
      const params=new URLSearchParams();if(selectedAttemptId)params.set('attempt',selectedAttemptId);if(target.phase)params.set('phase',target.phase);
      const page=await api(`/api/invocations/${selectedId}/attempt-page?${params}`);
      if(!current())return;
      attempts=page.attempts;attemptsNext=page.nextCursor;attemptsMore=page.hasMore;
      attemptPage=page.targetCursor>1?[0,page.targetCursor-1]:[0];
    } catch { if(!current())return;throw new Error('Saved phase or attempt is unavailable or belongs to another invocation.'); }
  }
  const attempt=selectedAttemptId && attempts.find(item=>item.id===selectedAttemptId);
  if (target.phase && attempt && attempt.operationKey!==target.phase) throw new Error('Attempt does not belong to this phase.');
  if (target.phase && !attempts.some(item=>item.operationKey===target.phase)) throw new Error('Saved phase is unavailable.');
  if (selectedEvent?.data?.sessionId && target.session && selectedEvent.data.sessionId!==target.session) throw new Error('Saved event does not belong to the selected native session.');
  const displayTarget={...target,attempt:target.attempt||selectedAttemptId||null,phase:target.phase||attempt?.operationKey||null,session:target.session||selectedSession?.id||null};
  if(!current())return;
  state.runPage=pageStack(reader?.pages?.runs??state.runPage);
  state.invocationPage=invocationPage;state.attemptPage=attemptPage;state.captureSummaryPage=captureSummaryPage;state.sessionPage=sessionPage;state.lanePage=lanePage;
  state.run=run;state.invocation=detail?.invocation||null;
  state.invocationList=selector.invocations;state.invocationNext=selector.nextCursor;state.invocationMore=selector.hasMore;
  state.attempts=attempts;state.captures=detail?.captures||[];
  state.attemptsNext=attemptsNext;state.capturesNext=detail?.capturesNextCursor||0;
  state.attemptsMore=attemptsMore;state.capturesMore=detail?.hasMoreCaptures||false;
  state.accounting=detail?.accounting||null;state.worktree=detail?.worktree||null;state.clearance=detail?.clearance||null;
  state.acknowledgment=detail?.acknowledgment||null;state.acknowledgmentStatus='';state.acknowledgmentError=false;
  state.sessions=sessionList;rememberSessionParents(sessionList);state.sessionsNext=sessions?.nextCursor||0;state.sessionsMore=sessions?.hasMore||false;
  state.events=events?.events||[];state.earlier=events?.hasEarlier||false;
  state.question=question;state.selectedEventCursor=selectedEvent?.cursor||null;state.selectedCaptureTarget=selectedCaptureTarget;
  state.selectedCapture=null;state.capturePage=null;state.capturePending=false;state.captureRefreshing=false;state.captureVersion++;state.pending=0;state.deferredEvents=[];state.error=null;
  if(selectedSession){
    let parent=state.sessions.find(item=>item.attemptId===selectedSession.attemptId&&item.nativeId===selectedSession.parentNativeId);
    const seen=new Set();
    while(parent&&!seen.has(parent.id)){seen.add(parent.id);state.collapsed.delete(parent.id);parent=state.sessions.find(item=>item.attemptId===parent.attemptId&&item.nativeId===parent.parentNativeId);}
  }
  state.displayTarget=displayTarget;
  if(displayTarget.session || selectedAttemptId || displayTarget.phase) {
    const rows=laneRows();
    const index=rows.findIndex(row=>displayTarget.session?row.type==='session'&&row.item.id===displayTarget.session:row.type==='attempt'&&(selectedAttemptId?row.item.id===selectedAttemptId:row.item.operationKey===displayTarget.phase));
    if(index>=0)state.lanePage=Math.floor(index/50);
  }
  renderRun(displayTarget);
  if(reader)restoreWindow(reader.top);
  return true;
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
function showPendingCaptureEvent(event) {
  if(state.frozen||state.snapshotting||!state.invocation||event.data?.invocationId!==state.invocation.id||state.selectedEventCursor)return;
  const list=document.getElementById('event-list');if(!list||list.querySelector(`[data-cursor="${CSS.escape(event.cursor)}"]`))return;
  const selection=window.getSelection();
  if(list.scrollHeight-list.scrollTop-list.clientHeight>48||(selection&&!selection.isCollapsed&&list.contains(selection.anchorNode)))return;
  const selected=route().attempt,capture=state.captures.find(item=>item.id===event.data.captureId);
  if(selected&&event.data.attemptId!==selected&&capture?.attemptId!==selected)return;
  if(list.querySelectorAll('.event-row').length>=200)return;
  const row=document.createElement('article');row.className='event-row';row.dataset.cursor=event.cursor;row.dataset.pending='true';
  const time=document.createElement('time');time.textContent=readableTime(event.data.at);
  const kind=document.createElement('span');kind.className='monospace';kind.textContent=event.kind;
  const summary=document.createElement('span');summary.textContent=eventSummary(event)+' - applying saved text';
  row.append(time,kind,summary);list.append(row);list.scrollTop=list.scrollHeight;
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
    ${acknowledgmentControls(invocation)}
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
// A view intent owns its reads and all continuations. Superseding it never waits
// for obsolete I/O. The cursor remains the last fully applied SSE projection;
// restarting the stream replays anything interrupted by navigation or a reader action.
function beginViewIntent() {
  state.readAbort.abort();
  state.readAbort=new AbortController();
  const snapshot=++state.snapshotGeneration;
  state.streamGeneration++;
  state.streamAbort?.abort();
  state.projection=null;state.projecting=false;state.captureRefreshing=false;
  state.connected=false;state.snapshotting=true;
  state.receivedCursor=state.cursor;
  document.querySelectorAll('.event-row[data-pending="true"]').forEach(row=>row.remove());
  if(!state.frozen)showConnection('connecting','Catching up from saved cursor '+state.cursor);
  return snapshot;
}
async function resumeView(snapshot) {
  let wait=300;
  while(snapshot===state.snapshotGeneration) {
    try {
      const head=await api('/api/events/head');
      if(snapshot!==state.snapshotGeneration)return;
      state.snapshotting=false;
      startStream(head.cursor);
      return;
    } catch {
      if(snapshot!==state.snapshotGeneration)return;
      showConnection('disconnected','History unavailable - retrying saved observations');
      await new Promise(resolve=>setTimeout(resolve,wait));
      wait=Math.min(wait*2,5000);
    }
  }
}
async function loadRoute(reader = null, baseline = null, resume = true, restoreWindow = windowRestoreIntent()) {
  if (!state.token) return;
  const snapshot=beginViewIntent();
  const generation=++state.routeGeneration, target=route();
  state.validatedParent=null;
  // Controls from a different displayed route cannot act on the new URL.
  // Links stay available so another navigation can supersede this read.
  if((target.run||null)!==(state.run?.id||null)||(target.invocation&&target.invocation!==state.invocation?.id)) {
    app.querySelectorAll('button').forEach(button=>{button.disabled=true;});
  }
  app.setAttribute('aria-busy','true');
  let committed=false;
  try {
    if (!target.run) {committed=await loadIndex(generation,reader?.pages?.runs??state.runPage)===true;if(committed)state.lastUpdate=new Date();return;}
    if (!idPattern.test(target.run)) { routeError('Invalid run link. The saved record was not selected.'); return; }
    committed=await loadRun(target,generation,reader,restoreWindow)===true;
    if (generation!==state.routeGeneration||snapshot!==state.snapshotGeneration) return;
    if(committed)state.lastUpdate=new Date();
  } catch(error) { if (generation===state.routeGeneration&&snapshot===state.snapshotGeneration) routeError(error.message,state.validatedParent); }
  finally {
    if(snapshot===state.snapshotGeneration) {
      if(reader)await restoreReader(reader,generation,restoreWindow);
      if(snapshot!==state.snapshotGeneration||generation!==state.routeGeneration)return;
      if(baseline!==null&&committed)state.cursor=baseline;
      state.snapshotting=false;
      state.receivedCursor=state.cursor;
      if(resume){
        if(committed) {
          await resumeView(snapshot);
        } else showConnection('disconnected','History unavailable');
      }
    }
  }
}
function navigateRoute(reader = null, restoreWindow = windowRestoreIntent()) {
  // Explicit navigation reads current projections. End the old view's Freeze
  // before rendering them, then replay through the new catch-up head.
  state.frozen=false;
  return loadRoute(reader,null,true,restoreWindow);
}
function readerSnapshot() {
  const active=document.activeElement;
  const selection=window.getSelection(),selectedText=selection?.toString()||'';
  const path=node=>{if(!node||!app.contains(node))return null;const parts=[];while(node!==app){const parent=node.parentNode;if(!parent)return null;parts.unshift([...parent.childNodes].indexOf(node));node=parent;}return parts;};
  return {top:window.scrollY,timeline:document.querySelector('.timeline-scroll')?.scrollLeft||0,events:document.getElementById('event-list')?.scrollTop||0,
    route:route(),pages:{runs:state.runPage.slice(-128),invocations:state.invocationPage.slice(-128),attempts:state.attemptPage.slice(-128),captures:state.captureSummaryPage.slice(-128),sessions:state.sessionPage.slice(-128),lane:state.lanePage},
    eventWindowEnd:state.events.at(-1)?.cursor||null,capture:state.selectedCapture?{id:state.selectedCapture,after:state.captureAfter}:null,
    disclosures:[...app.querySelectorAll('details')].map(item=>({name:item.querySelector('summary')?.textContent?.trim(),open:item.open})),
    selection:selection&&!selection.isCollapsed&&selectedText.length<=2048?{anchor:path(selection.anchorNode),anchorOffset:selection.anchorOffset,focus:path(selection.focusNode),focusOffset:selection.focusOffset,text:selectedText}:null,
    focus:{id:active?.id,href:active?.getAttribute('href'),action:active?.getAttribute('data-action'),item:active?.getAttribute('data-id'),start:active?.selectionStart,end:active?.selectionEnd}};
}
async function restoreReader(reader, generation=state.routeGeneration, restoreWindow=windowRestoreIntent()) {
  if(!reader||state.error)return;
  const href=location.href,invocationId=state.invocation?.id,snapshot=state.snapshotGeneration;
  const current=()=>generation===state.routeGeneration&&href===location.href&&state.invocation?.id===invocationId&&snapshot===state.snapshotGeneration;
  if(!current())return;
  for(const detail of app.querySelectorAll('details')) {
    const saved=reader.disclosures?.find(item=>item.name===detail.querySelector('summary')?.textContent?.trim());
    if(saved)detail.open=saved.open;
  }
  if(state.invocation && reader.eventWindowEnd && !route().cursor && state.events.at(-1)?.cursor!==reader.eventWindowEnd) {
    try {const page=await api(`/api/invocations/${invocationId}/events?before=${BigInt(reader.eventWindowEnd)+1n}&limit=200`);
      if(current()){state.events=page.events;state.earlier=page.hasEarlier;renderEventList();}}
    catch(error) {if(current())readFailure('Earlier event restoration failed: '+error.message);}
  }
  if(!current())return;
  if(state.invocation && reader.capture?.id) {
    try {
      const captureVersion=++state.captureVersion;
      const page=await api(`/api/invocations/${invocationId}/captures/${reader.capture.id}?after=${reader.capture.after}&limit=50`);
      if(current()&&state.captureVersion===captureVersion){state.selectedCapture=reader.capture.id;state.captureAfter=reader.capture.after;state.capturePending=false;state.capturePage=page;renderCapture();}}
    catch(error) {if(current())readFailure('Saved output restoration failed: '+error.message);}
  }
  if(!current())return;
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
  restoreWindow(reader.top);
}
async function redeem(ticket) {
  if (!ticket) throw new Error('This browser link has no active owner handoff. Start the dashboard from its owner process and open the new link.');
  const response=await fetch('/api/ui-session',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({ticket})});
  if (!response.ok) throw new Error('This handoff is expired or has already been used. Start a new owner link.');
  const result=await response.json();
  if (typeof result.sessionToken!=='string' || !result.sessionToken) throw new Error('Owner handoff returned no credential.');
  state.token=result.sessionToken;
}
function startStream(targetCursor = null) {
  if(!state.token||state.snapshotting)return;
  const generation=++state.streamGeneration;
  void connect(generation,targetCursor);
}
async function connect(generation,targetCursor) {
  let wait=300;
  while (state.token && generation===state.streamGeneration && !state.snapshotting) {
    const abort=new AbortController(); state.streamAbort=abort;
    let projectionFailure=null;
    try {
      if(state.frozen)showConnection('frozen','Frozen at saved cursor '+state.cursor);
      else showConnection('connecting','Catching up from saved cursor '+state.cursor);
      const response=await fetch('/api/stream?after='+encodeURIComponent(state.cursor),{headers:{Authorization:'Bearer '+state.token},cache:'no-store',signal:abort.signal});
      if (!response.ok || !response.body) throw new Error('Observation stream unavailable');
      if(generation!==state.streamGeneration)return;
      await refreshReminderGroups();
      if(generation!==state.streamGeneration)return;
      state.connected=true;
      if(state.frozen)showConnection('frozen','Frozen at saved cursor '+state.cursor);
      else if(targetCursor&&BigInt(state.cursor)<BigInt(targetCursor))showConnection('connecting','Catching up from saved cursor '+state.cursor);
      else showConnection('connected','Connected - saved cursor '+state.cursor);
      wait=300;
      const reader=response.body.getReader(),decoder=new TextDecoder(); let buffer='';
      while (true) {
        const part=await reader.read(); if(generation!==state.streamGeneration)return;if(part.done) break;
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
            if(generation!==state.streamGeneration||state.snapshotting)return;
            let event; try {event=JSON.parse(fields.data);} catch {continue;}
            if(!/^\d+$/.test(event.cursor||'') || BigInt(event.cursor)<=BigInt(state.receivedCursor))continue;
            state.receivedCursor=event.cursor;
            if(state.projecting&&event.kind==='capture.appended')showPendingCaptureEvent(event);
            if(!state.frozen)showConnection('connecting','Applying saved observations after cursor '+state.cursor);
            const previous=state.projection;
            const projection=Promise.resolve(previous).then(()=>{
              if(generation!==state.streamGeneration||state.snapshotting)return;
              return applyEvent(event);
            }).then(()=>{
              if(generation!==state.streamGeneration||state.snapshotting)return;
              if(!state.frozen){state.cursor=event.cursor;state.lastUpdate=new Date();}
              if(state.connected&&!state.frozen&&BigInt(state.cursor)>=BigInt(state.receivedCursor)&&(!targetCursor||BigInt(state.cursor)>=BigInt(targetCursor)))showConnection('connected','Connected - saved cursor '+state.cursor);
            });
            state.projection=projection;state.projecting=true;
            void projection.then(()=>{if(state.projection===projection)state.projecting=false;},error=>{
              if(state.projection===projection)state.projecting=false;
              if(generation===state.streamGeneration&&state.streamAbort===abort){projectionFailure=error;abort.abort();}
            });
          } else if(fields.event==='gap'||fields.event==='unavailable') {
            state.gap=true; throw new Error(fields.event==='gap'?'Saved event gap':'Observation unavailable');
          }
        }
      }
      throw new Error('Observation stream disconnected');
    } catch(error) {
      abort.abort();
      if(generation!==state.streamGeneration||(error.name==='AbortError'&&!projectionFailure))return;
      state.connected=false;
      await state.projection?.catch(()=>{});
      if(generation!==state.streamGeneration)return;
      state.projection=null;state.projecting=false;
      document.querySelectorAll('.event-row[data-pending="true"]').forEach(row=>row.remove());
      state.receivedCursor=state.cursor;
      showConnection('disconnected',`Disconnected - last update ${state.lastUpdate ? state.lastUpdate.toLocaleTimeString() : 'unknown'}`);
      if(state.gap) {
        try {const head=await api('/api/events/head');await loadRoute(readerSnapshot(),head.cursor);return; }
        catch { /* Keep the last saved display and retry. */ }
      }
      await new Promise(resolve=>setTimeout(resolve,wait)); wait=Math.min(wait*2,5000);
    }
  }
}
async function applyEvent(event) {
  const snapshot=state.snapshotGeneration,current=()=>!state.snapshotting&&snapshot===state.snapshotGeneration;
  if(!current())return;
  if(state.frozen) { deferEvent(event);return; }
  if(event.kind==='notification.reminder_reserved'||event.kind==='notification.reminder_recorded') {
    await refreshReminderGroups();
    if(!current())return;
  }
  if(event.kind==='run.created' && !state.runs.some(run=>run.id===event.data?.runId)) {
    state.newRuns++;
    if(!route().run) {
      let notice=document.getElementById('new-runs-notice');
      if(!notice) {notice=document.createElement('div');notice.id='new-runs-notice';notice.className='attention';document.querySelector('.heading-row')?.after(notice);}
      notice.innerHTML=`<p>${state.newRuns} new run${state.newRuns===1?'':'s'} recorded while you were reading.</p><button type="button" data-action="refresh-index">Refresh run order</button>`;
    }
  }
  if(!route().run && state.runs.some(run=>run.id===event.data?.runId || run.latestInvocation?.id===event.data?.invocationId)) await refreshIndexCard(event);
  if(!current())return;
  if(state.frozen){deferEvent(event);return;}
  if(state.invocation && event.data?.invocationId===state.invocation.id) {
    const alreadyShown=state.events.length && BigInt(event.cursor)<=BigInt(state.events.at(-1).cursor);
    if(event.kind==='capture.created' && !state.captures.some(item=>item.id===event.data.captureId)) await refreshCaptureSummaries();
    if(!current())return;
    if(state.frozen){deferEvent(event);return;}
    if(event.kind==='capture.appended') {
      const capture=state.captures.find(item=>item.id===event.data.captureId);
      if(capture) {capture.state=event.data.state;updateCaptureButtons();}
      if(capture?.channel==='request' && event.data.state==='complete')await refreshQuestion();
      if(!current())return;
      if(state.frozen){deferEvent(event);return;}
      if(state.selectedCapture===event.data.captureId && state.capturePage) {
        state.capturePending=true;state.captureVersion++;
        const followed=await followCapture();
        if(!current())return;
        if(followed===false){if(state.frozen){deferEvent(event);return;}throw new Error('Saved output projection failed');}
      }
    }
    if(['invocation.finalized','invocation.running','invocation.shutting_down','owner.cleared'].includes(event.kind)) await refreshCurrentOutcome();
    if(!current())return;
    if(state.frozen){deferEvent(event);return;}
    if(alreadyShown)return;
    const list=document.getElementById('event-list');
    const selection=window.getSelection();
    const readingText=selection && !selection.isCollapsed && list?.contains(selection.anchorNode);
    const away=list && list.scrollHeight-list.scrollTop-list.clientHeight>48;
    if(readingText || away || state.selectedEventCursor) { deferEvent(event); return; }
    state.events.push(event); if(state.events.length>200) {state.events.shift(); state.earlier=true;}
    renderEventList(); if(list)list.scrollTop=list.scrollHeight;
  }
}
function deferEvent(event) {
  // SSE is ordered. The last deferred cursor also covers rows evicted from
  // the bounded window when an owned reader action reconnects while frozen.
  const last=state.deferredEvents.at(-1)?.cursor;
  if(last&&BigInt(event.cursor)<=BigInt(last))return;
  state.pending++;state.deferredEvents.push(event);
  if(state.deferredEvents.length>200)state.deferredEvents.shift();
  updatePending();
}
async function refreshQuestion() {
  const id=state.invocation?.id,generation=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href;if(!id)return;
  const question=await api(`/api/invocations/${id}/question`);if(state.frozen||generation!==state.routeGeneration||snapshot!==state.snapshotGeneration||href!==location.href||state.invocation?.id!==id)return;state.question=question;
  updateAttention();
  updateOutcomeExplanation();
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
  const snapshot=state.snapshotGeneration;
  const latest=await api(`/api/runs/${run.id}`);
  if(state.frozen||route().run||snapshot!==state.snapshotGeneration)return;
  const index=state.runs.findIndex(item=>item.id===run.id);if(index<0)return;
  state.runs[index]=latest;
  const cards=document.getElementById('cards');
  const existing=cards?.querySelector(`[data-run="${CSS.escape(run.id)}"]`);
  if(!cards)return;
  if(!matchesRun(latest)) {
    existing?.remove();
    if(existing&&!cards.querySelector('.run-card'))renderCards();
    return;
  }
  const replacement=document.createElement('div');replacement.innerHTML=card(latest);
  const fresh=replacement.firstElementChild;
  if(!existing) {
    cards.querySelector('.state-message')?.remove();
    // Live updates retain the loaded page and its saved order. Only this
    // card's membership changes; other cards keep their DOM and reader intent.
    const next=state.runs.slice(index+1).map(item=>cards.querySelector(`[data-run="${CSS.escape(item.id)}"]`)).find(Boolean);
    cards.insertBefore(fresh,next||null);
    return;
  }
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
}
function updateCaptureButtons() {
  const container=document.querySelector('.capture-list');if(!container)return;
  reconcileChildren(container,state.captures,item=>item.id,item=>{
    const button=document.createElement('button');button.type='button';button.dataset.action='open-capture';button.dataset.id=item.id;return button;
  },(button,item)=>{button.textContent=`${item.channel} - ${item.state} - ${short(item.id)}`});
  if(!state.captures.length && !container.firstElementChild){const empty=document.createElement('p');empty.textContent='No saved captures in this page.';container.append(empty);}
  const more=document.querySelector('[data-action="more-captures"]');if(more)more.disabled=!state.capturesMore;
}
async function refreshCaptureSummaries() {
  const id=state.invocation?.id,generation=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href,pageStack=state.captureSummaryPage;
  if(!id)return;
  const anchor=pageStack.at(-1)??0;
  const page=await api(`/api/invocations/${id}?afterCapture=${anchor}&limit=50`);
  if(state.frozen||generation!==state.routeGeneration||snapshot!==state.snapshotGeneration||href!==location.href||state.invocation?.id!==id||state.captureSummaryPage!==pageStack)return;
  state.captures=page.captures;
  state.capturesNext=page.capturesNextCursor;
  state.capturesMore=page.hasMoreCaptures;
  updateCaptureButtons();
}
async function refreshCurrentOutcome() {
  if(!state.invocation)return;
  const id=state.invocation.id,routeGeneration=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href;
  const current=()=>!state.frozen&&routeGeneration===state.routeGeneration&&snapshot===state.snapshotGeneration&&href===location.href&&state.invocation?.id===id;
  const page=await api(`/api/invocations/${id}?limit=1`);
  if(!current())return;
  const previous=outcome(state.invocation)[0],previousCleanup=state.invocation.cleanup,previousClearance=state.clearance?.id;
  let question=state.question;
  if(page.invocation.outcome==='needs_input'||page.invocation.outcome==='failed') {
    question=await api(`/api/invocations/${id}/question`);
  }
  if(!current())return;
  state.invocation=page.invocation;state.clearance=page.clearance;state.question=question;
  const [label,tone]=outcome(state.invocation);
  const execution=document.getElementById('execution-state');if(execution)execution.innerHTML=chip(label,tone);
  const cleanup=document.getElementById('cleanup-state');if(cleanup)cleanup.innerHTML=chip(state.clearance?'Operator confirmed':state.invocation.cleanup==='complete'?'Automatically checked':state.invocation.cleanup==='unknown'?'Manual cleanup required':'Cleanup unknown',state.clearance||state.invocation.cleanup==='complete'?'success':'attention');
  updateAttention();
  const inspectorOutcome=document.getElementById('inspector-outcome');if(inspectorOutcome&&!state.displayTarget?.attempt)inspectorOutcome.textContent=label;
  updateOutcomeExplanation();
  if(previous!==label||previousCleanup!==state.invocation.cleanup||previousClearance!==state.clearance?.id)announcement.textContent='Selected invocation updated: '+label+(state.invocation.cleanup==='unknown'?'; manual cleanup required':'');
}
function updatePending() {
  const button=document.getElementById('pending-events');
  if(button) { button.hidden=false; button.textContent=state.pending+' new events - return to latest'; }
}
async function latestEvents() {
  if(!state.frozen&&!state.pending)return;
  const reader=readerSnapshot();reader.eventWindowEnd=null;
  const selected=route();
  if(selected.cursor){history.replaceState({...history.state},'',link({run:selected.run,invocation:selected.invocation,phase:selected.phase,attempt:selected.attempt,session:selected.session}));lastNavigatedHref=location.href;}
  const loading=loadRoute(reader,null,false),snapshot=state.snapshotGeneration;
  await loading;
  if(snapshot!==state.snapshotGeneration)return;
  if(state.error||reader.route.run!==route().run||reader.route.invocation!==route().invocation)return;
  state.frozen=false;state.pending=0;state.deferredEvents=[];state.selectedEventCursor=null;
  document.getElementById('event-list')?.scrollTo({top:10000000});
  document.querySelectorAll('[data-action="freeze"]').forEach(button=>{button.textContent='Freeze this view';button.setAttribute('aria-pressed','false')});
  showConnection('connecting','Catching up from saved cursor '+state.cursor);
  await resumeView(snapshot);
}
async function olderEvents() {
  if(!state.invocation||!state.events.length)return;
  const before=state.events[0].cursor,id=state.invocation.id,generation=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href;
  const page=await api(`/api/invocations/${id}/events?before=${before}&limit=200`);
  if(generation!==state.routeGeneration||snapshot!==state.snapshotGeneration||href!==location.href||state.invocation?.id!==id||state.events[0]?.cursor!==before)return;
  state.events=page.events; state.earlier=page.hasEarlier; state.frozen=true;
  renderEventList(); document.getElementById('event-list')?.scrollTo({top:0});
  document.querySelectorAll('[data-action="freeze"]').forEach(button=>{button.textContent='Follow latest events';button.setAttribute('aria-pressed','true')});
  showConnection('frozen','Frozen at saved cursor '+before);
}
async function openCapture(id) {
  if(!state.invocation)return;
  const invocationId=state.invocation.id,generation=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href;
  const page=await api(`/api/invocations/${invocationId}/captures/${id}?limit=50`);
  if(generation!==state.routeGeneration||snapshot!==state.snapshotGeneration||href!==location.href||state.invocation?.id!==invocationId)return;
  state.selectedCapture=id;state.captureAfter=0;state.capturePending=false;state.captureVersion++;
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
  if(!state.capturePending||state.captureRefreshing||state.frozen||!state.selectedCapture||!state.capturePage)return false;
  if(!force&&!captureAtBottom()){renderCapture();return true;}
  const page=state.capturePage,id=state.selectedCapture,invocationId=state.invocation?.id,generation=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href;
  const owned=()=>generation===state.routeGeneration&&snapshot===state.snapshotGeneration&&href===location.href&&state.invocation?.id===invocationId&&state.selectedCapture===id&&state.capturePage===page;
  const current=()=>!state.frozen&&owned();
  if(page.chunks.length>=50){page.hasMore=true;renderCapture();return true;}
  const version=state.captureVersion;state.captureRefreshing=true;let succeeded=false;
  try {
    const next=await api(`/api/invocations/${invocationId}/captures/${id}?after=${page.nextSequence}&limit=${50-page.chunks.length}`);
    if(!current())return false;
    // Reading intent can change while saved bytes are in flight. Leave them
    // pending when the reader has since scrolled away or selected text.
    if(!force&&!captureAtBottom()){renderCapture();return true;}
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
    succeeded=true;
    return true;
  } catch { if(current())renderCapture();return false; }
  finally {
    if(owned())state.captureRefreshing=false;
    if(succeeded&&current()&&state.capturePending&&!page.hasMore&&captureAtBottom())void followCapture();
  }
}
async function moreOutput() {
  const old=state.capturePage; if(!old)return;
  if(!old.hasMore){await followCapture(true);return;}
  const invocationId=state.invocation?.id,id=state.selectedCapture,generation=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href;
  if(!invocationId||!id)return;
  const next=await api(`/api/invocations/${invocationId}/captures/${id}?after=${old.nextSequence}&limit=50`);
  if(generation!==state.routeGeneration||snapshot!==state.snapshotGeneration||href!==location.href||state.invocation?.id!==invocationId||state.selectedCapture!==id||state.capturePage!==old)return;
  state.captureAfter=old.nextSequence;state.capturePage=next;state.capturePending=false;renderCapture();
}
async function moreHistory(kind, direction='next') {
  if(!state.invocation)return;
  const id=state.invocation.id,generation=state.routeGeneration,snapshot=state.snapshotGeneration,href=location.href;
  const stack=kind==='sessions'?state.sessionPage:kind==='attempts'?state.attemptPage:state.captureSummaryPage;
  const nextStack=stack.slice();
  if(direction==='next')nextStack.push(kind==='sessions'?state.sessionsNext:kind==='attempts'?state.attemptsNext:state.capturesNext);
  else if(nextStack.length>1)nextStack.pop();
  const cursor=nextStack.at(-1) ?? 0;
  const current=()=>generation===state.routeGeneration&&snapshot===state.snapshotGeneration&&href===location.href&&state.invocation?.id===id&&
    (kind==='sessions'?state.sessionPage:kind==='attempts'?state.attemptPage:state.captureSummaryPage)===stack;
  if(kind==='sessions') {
    const page=await api(`/api/invocations/${id}/sessions?after=${cursor}&limit=50`);
    if(!current())return;
    state.sessionPage=nextStack;
    state.sessions=page.sessions;rememberSessionParents(page.sessions);state.sessionsNext=page.nextCursor;state.sessionsMore=page.hasMore;
  } else {
    const key=kind==='attempts'?'afterAttempt':'afterCapture';
    const page=await api(`/api/invocations/${id}?${key}=${cursor}&limit=50`);
    if(!current())return;
    if(kind==='attempts'){state.attemptPage=nextStack;state.attempts=page.attempts;state.attemptsNext=page.attemptsNextCursor;state.attemptsMore=page.hasMoreAttempts;}
    else{state.captureSummaryPage=nextStack;state.captures=page.captures;state.capturesNext=page.capturesNextCursor;state.capturesMore=page.hasMoreCaptures;}
  }
  state.lanePage=0;
  const reader=readerSnapshot();renderRun(route());await restoreReader(reader,generation);
}
app.addEventListener('input',event=>{if(event.target.id==='run-search'){state.query=event.target.value;renderCards();}});
app.addEventListener('scroll',event=>{if(event.target.id==='capture-text'&&state.capturePending)void followCapture();},true);
history.scrollRestoration='manual';
let lastNavigatedHref=location.href;
let recentReading={top:0},userScrollUntil=0,userScrollGeneration=0;
function windowRestoreIntent() {
  const inputAtStart=userScrollGeneration;
  return top=>{if(inputAtStart===userScrollGeneration)window.scrollTo(0,top||0);};
}
const noteUserScroll=()=>{userScrollGeneration++;userScrollUntil=performance.now()+1000;};
window.addEventListener('wheel',noteUserScroll,{passive:true});
window.addEventListener('touchmove',noteUserScroll,{passive:true});
window.addEventListener('keydown',event=>{if(['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(event.key))noteUserScroll();});
window.addEventListener('pointerdown',event=>{if(event.clientX>=document.documentElement.clientWidth)noteUserScroll();});
window.addEventListener('scroll',()=>{
  if(window.scrollY>recentReading.top||performance.now()<userScrollUntil)recentReading={top:window.scrollY};
},{passive:true});
app.addEventListener('click',async event=>{
  const anchor=event.target.closest('a[href^="#"]');
  if(!anchor || event.defaultPrevented || event.button!==0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)return;
  event.preventDefault();
  const current=route(),before=readerSnapshot(),oldRun=current.run;
  const restoreWindow=windowRestoreIntent();
  const returning=anchor.dataset.action==='return-timeline';
  const selected=state.displayTarget;
  const fallbackOrigin=selected?link({run:selected.run,invocation:state.invocation?.id,phase:selected.phase,attempt:selected.attempt,session:selected.session}):null;
  const originHref=returning?(history.state?.origin?.href||fallbackOrigin):null;
  before.focus={href:anchor.getAttribute('href')};
  if(recentReading.top>before.top)before.top=recentReading.top;
  recentReading={top:0};
  history.replaceState({...history.state,reader:before},'');
  history.pushState(!returning&&anchor.matches('.phase-bar, .timeline-text a')?{origin:{href:anchor.getAttribute('href')}}:{},'',anchor.getAttribute('href'));
  lastNavigatedHref=location.href;
  if(returning)[...document.querySelectorAll('.phase-bar, .timeline-text a')].find(item=>item.getAttribute('href')===originHref)?.focus({preventScroll:true});
  const destination=new URLSearchParams(anchor.getAttribute('href').slice(1));
  const sameInvocation=destination.get('run')===state.run?.id&&(!destination.get('invocation')||destination.get('invocation')===state.invocation?.id);
  const loading=navigateRoute(returning||sameInvocation?before:null,restoreWindow),snapshot=state.snapshotGeneration;
  await loading;
  if(snapshot!==state.snapshotGeneration)return;
  restoreWindow(route().run===oldRun?before.top:0);
  if(returning) {
    const phase=[...document.querySelectorAll('.phase-bar, .timeline-text a')].find(item=>item.getAttribute('href')===originHref);
    (phase||document.querySelector('.timeline-scroll'))?.focus({preventScroll:true});
  }
});
document.querySelector('.skip')?.addEventListener('click',event=>{event.preventDefault();app.focus({preventScroll:true});app.scrollIntoView({block:'start'});});
app.addEventListener('change',event=>{if(event.target.id==='outcome-filter'){state.filter=event.target.value;renderCards();}});
app.addEventListener('submit',async event=>{
  if(event.target.id!=='notification-preferences')return;
  event.preventDefault();
  const form=event.target,button=form.querySelector('button[type="submit"]'),status=document.getElementById('preferences-status');
  button.disabled=true;status.textContent='Saving notification preferences';status.setAttribute('role','status');
  try {
    state.notificationPreferences=await writeNotification('/api/notifications/preferences',{
      successNotices:form.elements.successNotices.checked,reminders:form.elements.reminders.checked });
    state.preferencesStatus='Notification preferences saved.';state.preferencesError=false;
  } catch(error) {
    state.preferencesStatus=error.message;state.preferencesError=true;
    form.elements.successNotices.checked=!!state.notificationPreferences?.successNotices;
    form.elements.reminders.checked=!!state.notificationPreferences?.reminders;
  }
  if(status.isConnected){status.textContent=state.preferencesStatus;status.setAttribute('role',state.preferencesError?'alert':'status');button.disabled=false;button.focus({preventScroll:true});}
});
app.addEventListener('click',async event=>{
  const button=event.target.closest('[data-action]');if(!button)return;
  const action=button.dataset.action;
  if(action==='acknowledge-invocation') {
    const invocationId=state.invocation?.id,status=document.getElementById('acknowledgment-status');
    if(!invocationId||!status)return;
    button.disabled=true;status.textContent='Saving acknowledgment';status.setAttribute('role','status');
    try { const saved=await writeNotification('/api/notifications/acknowledgments',{invocationId});
      if(state.invocation?.id===invocationId){state.acknowledgment=saved;state.acknowledgmentStatus='Acknowledged on '+readableTime(saved.acknowledgedAt);state.acknowledgmentError=false;}
    } catch(error) {if(state.invocation?.id===invocationId){state.acknowledgmentStatus=error.message;state.acknowledgmentError=true;}}
    if(status.isConnected){status.textContent=state.acknowledgmentStatus;status.setAttribute('role',state.acknowledgmentError?'alert':'status');button.textContent=state.acknowledgment?'Acknowledged':'Acknowledge selected invocation';button.disabled=false;button.focus({preventScroll:true});}
    return;
  }
  const routes=['next-runs','previous-runs','refresh-index','next-invocations','previous-invocations','latest-events'];
  const ownsView=!routes.includes(action)&&!(action==='freeze'&&state.frozen)&&action!=='return-timeline';
  const snapshot=ownsView?beginViewIntent():state.snapshotGeneration;
  const generation=state.routeGeneration,href=location.href;
  try {
    if(action==='clear-filter'){state.query='';state.filter='all';renderIndex();document.getElementById('run-search')?.focus();}
    else if(action==='next-runs'||action==='previous-runs'||action==='refresh-index'){
      const reader=readerSnapshot(),pages=reader.pages.runs;
      if(action==='next-runs')pages.push(state.runPageNext);
      else if(action==='previous-runs')pages.pop();
      else pages.splice(0,pages.length,0);
      const loading=navigateRoute(reader),owner=state.snapshotGeneration;
      await loading;
      if(owner===state.snapshotGeneration&&action==='refresh-index'&&!state.error)state.newRuns=0;
    }
    else if(action==='next-invocations'||action==='previous-invocations'){
      const reader=readerSnapshot(),pages=reader.pages.invocations;
      if(action==='next-invocations')pages.push(state.invocationNext);else pages.pop();
      await navigateRoute(reader);
    }
    else if(action==='next-lanes'||action==='previous-lanes'){const reader=readerSnapshot();state.lanePage=Math.max(0,state.lanePage+(action==='next-lanes'?1:-1));renderRun(route());await restoreReader(reader,generation);if(generation===state.routeGeneration&&snapshot===state.snapshotGeneration&&href===location.href)document.querySelector(`[data-action="${action}"]`)?.focus({preventScroll:true});}
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
      if(state.frozen)await latestEvents();else{state.frozen=true;document.querySelectorAll('.event-row[data-pending="true"]').forEach(row=>row.remove());showConnection('frozen','Frozen at saved cursor '+state.cursor);document.querySelectorAll('[data-action="freeze"]').forEach(item=>{item.setAttribute('aria-pressed','true');item.textContent='Follow latest events'})}
    }
  } catch(error){if(generation!==state.routeGeneration||snapshot!==state.snapshotGeneration||href!==location.href||!button.isConnected)return;
    readFailure(error.message);}
  finally {if(ownsView)await resumeView(snapshot);}
});
function browserRouteChanged(){if(location.href===lastNavigatedHref)return;lastNavigatedHref=location.href;recentReading={top:0};userScrollUntil=0;void navigateRoute(history.state?.reader);}
window.addEventListener('hashchange',browserRouteChanged);
window.addEventListener('popstate',browserRouteChanged);

export async function start(ticket) {
  const snapshot=state.snapshotGeneration;
  try {
    await redeem(ticket);
    await loadNotificationPreferences();
    // The head is sampled before the first snapshot, so later committed events are replayed by SSE.
    const head=await api('/api/events/head');
    await loadRoute(null,head.cursor);
  } catch(error) {if(snapshot!==state.snapshotGeneration)return;showConnection('disconnected','History unavailable');errorView(error.message);}
}
