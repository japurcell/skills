#!/usr/bin/env node
import { redactText } from './redaction.js';
import { StartupInterrupted } from './workspace.js';
import { clearClaim, inspectClaim } from './clearance.js';
import { invoke } from './lifecycle.js';
import { openRepositoryStore } from './store.js';
import { repositoryIdentity } from './workspace.js';
import { startObservationHost } from './dashboard.js';
const args = process.argv.slice(2);
const help = `software-factory (development)
invoke --repository PATH --workflow .factory/workflows/FILE.ts --input JSON_FILE
       (--new-worktree [--ref COMMIT] | --worktree ID_OR_PATH) [--run ID]
       [--question CAPTURE_ID] [--context CAPTURE_ID ...] [--command-timeout-ms N] [--agent-timeout-ms N] [--shutdown-grace-ms N] [--json]
history --repository PATH --invocation ID [--after-attempt CURSOR] [--after-capture CURSOR] [--limit N] [--json]
        [--capture ID --after-sequence N]
dashboard --repository PATH
inspect-owner (--repository PATH | --common-dir PATH) [--claim ID] [--json]
clear-owner (--repository PATH | --common-dir PATH) --claim ID --token TOKEN --operator-confirmed --note NOTE [--json]
Startup validates the explicitly installed toolchain; no automatic installation or resume.
`;
async function main() {
  if (args.includes('--help')) { process.stdout.write(help); return; }
  const command = args.shift();
  if (!command || !['invoke','history','dashboard','inspect-owner','clear-owner'].includes(command)) throw new Error('command not implemented; startup refused');
  const values = new Map<string, string[]>();
  let json = false, newWorktree = false, operatorConfirmed = false;
  while (args.length) {
    const key = args.shift()!;
    if (key === '--json') { if (json) throw new Error('duplicate --json'); json = true; continue; }
    if (key === '--operator-confirmed' && command === 'clear-owner') { if (operatorConfirmed) throw new Error('duplicate --operator-confirmed'); operatorConfirmed = true; continue; }
    if (key === '--new-worktree') { if (newWorktree) throw new Error('duplicate --new-worktree'); newWorktree = true; continue; }
    const allowed = command === 'invoke' ? ['--repository','--workflow','--input','--ref','--worktree','--run','--question','--context','--command-timeout-ms','--agent-timeout-ms','--shutdown-grace-ms'] : command === 'history' ? ['--repository','--invocation','--capture','--after-sequence','--after-attempt','--after-capture','--limit'] : command === 'dashboard' ? ['--repository'] : command === 'inspect-owner' ? ['--repository','--common-dir','--claim'] : ['--repository','--common-dir','--claim','--token','--note'];
    if (!allowed.includes(key) || !args[0] || args[0].startsWith('--')) throw new Error(`invalid or missing option: ${key}`);
    if (values.has(key) && key !== '--context') throw new Error(`duplicate option: ${key}`);
    values.set(key, [...values.get(key) ?? [], args.shift()!]);
  }
  const get = (key: string) => values.get(key)?.[0];
  const repository = get('--repository');
  const commonDir=get('--common-dir');
  if (!repository && !commonDir) throw new Error('--repository is required');
  if (repository && commonDir) throw new Error('select exactly one of --repository or --common-dir');
  let result;
  if (command === 'dashboard') {
    if (newWorktree || operatorConfirmed || json) throw new Error('invalid dashboard option');
    const store = openRepositoryStore((await repositoryIdentity(repository!)).common);
    let host: Awaited<ReturnType<typeof startObservationHost>> | undefined;
    try {
      host = await startObservationHost({ store });
      if (!host.readCredentialAvailable || !host.createUiHandoff) throw new Error('dashboard is owned by another process; UI handoff unavailable');
      const stopping = new Promise<void>(resolve => {
        process.once('SIGINT', () => resolve()); process.once('SIGTERM', () => resolve());
      });
      process.stdout.write(host.createUiHandoff() + '\n');
      await stopping;
      if (!host.reused) await host.close();
    } finally { store.close(); }
    return;
  } else if (command === 'invoke') {
    const workflow = get('--workflow'), input = get('--input');
    if (!workflow || !input) throw new Error('--workflow and --input are required');
    result = await invoke({ repository:repository!, workflow, input, newWorktree, ...(get('--ref') ? { ref: get('--ref')! } : {}), ...(get('--worktree') ? { worktreeId: get('--worktree')! } : {}), ...(get('--run') ? { runId: get('--run')! } : {}), ...(get('--question') ? { question: get('--question')! } : {}), contexts: values.get('--context') ?? [], ...(get('--command-timeout-ms') ? {commandTimeoutMs:Number(get('--command-timeout-ms'))} : {}), ...(get('--agent-timeout-ms') ? {agentTimeoutMs:Number(get('--agent-timeout-ms'))} : {}), ...(get('--shutdown-grace-ms') ? {shutdownGraceMs:Number(get('--shutdown-grace-ms'))} : {}) });
    process.exitCode = result.exitCode;
  } else if (command === 'inspect-owner' || command === 'clear-owner') {
    if (newWorktree) throw new Error('worktree selection is not valid for owner commands');
    const store = openRepositoryStore(commonDir ?? (await repositoryIdentity(repository!)).common);
    try {
      if (command === 'inspect-owner') result = (get('--claim') ? [store.readClaim(get('--claim')!)] : store.inspectOwners()).map(claim=>inspectClaim(store,claim));
      else {
        const claimId=get('--claim'),token=get('--token'),note=get('--note');
        if (!claimId || !token || !note?.trim() || !operatorConfirmed) throw new Error('clear-owner requires --claim, --token, --operator-confirmed and nonempty --note');
        result = await clearClaim(store,{claimId,token,operatorConfirmed,note});
      }
    } finally { store.close(); }
  } else {
    const id = get('--invocation'); if (!id || newWorktree) throw new Error('history requires --invocation');
    const store = openRepositoryStore((await repositoryIdentity(repository!)).common);
    const number = (key: string, fallback: number) => {
      const value = get(key);
      if (value === undefined) return fallback;
      if (!/^\d+$/.test(value) || !Number.isSafeInteger(Number(value))) throw new Error(`invalid numeric option: ${key}`);
      return Number(value);
    };
    try {
      const capture = get('--capture');
      if (capture) {
        if (get('--after-attempt') || get('--after-capture')) throw new Error('capture text uses --after-sequence');
        result = store.readInvocationCapture({ invocationId: id, id: capture, after: number('--after-sequence', 0), limit: number('--limit', 20) });
      } else {
        if (get('--after-sequence')) throw new Error('--after-sequence requires --capture');
        result = store.readHistory(id, { afterAttempt: number('--after-attempt', 0), afterCapture: number('--after-capture', 0), limit: number('--limit', 50) });
      }
    } finally { store.close(); }
  }
  process.stdout.write(JSON.stringify(result, null, json ? 0 : 2) + '\n', () => { if (command === 'invoke') process.exit(process.exitCode ?? 0); });
}
main().catch(error => { let diagnostic='startup refused';try{diagnostic=redactText(error instanceof Error?error.message:diagnostic);}catch{/* Never echo a failing filter configuration. */}process.stderr.write(`software-factory: ${diagnostic}\n`);process.exitCode=error instanceof StartupInterrupted?error.exitCode:3; });
