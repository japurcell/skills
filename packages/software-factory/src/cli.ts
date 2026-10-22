#!/usr/bin/env node
import { invoke } from './lifecycle.js';
import { openRepositoryStore } from './store.js';
import { repositoryIdentity } from './workspace.js';
const args = process.argv.slice(2);
const help = `software-factory (development)
invoke --repository PATH --workflow .factory/workflows/FILE.ts --input JSON_FILE
       (--new-worktree [--ref COMMIT] | --worktree ID_OR_PATH) [--run ID]
       [--question CAPTURE_ID] [--context CAPTURE_ID ...] [--json]
history --repository PATH --invocation ID [--json]
Startup validates the explicitly installed toolchain; no automatic installation or resume.
`;
async function main() {
  if (args.includes('--help')) { process.stdout.write(help); return; }
  const command = args.shift();
  if (command !== 'invoke' && command !== 'history') throw new Error('command not implemented; startup refused');
  const values = new Map<string, string[]>();
  let json = false, newWorktree = false;
  while (args.length) {
    const key = args.shift()!;
    if (key === '--json') { if (json) throw new Error('duplicate --json'); json = true; continue; }
    if (key === '--new-worktree') { if (newWorktree) throw new Error('duplicate --new-worktree'); newWorktree = true; continue; }
    const allowed = command === 'invoke' ? ['--repository','--workflow','--input','--ref','--worktree','--run','--question','--context'] : ['--repository','--invocation'];
    if (!allowed.includes(key) || !args[0] || args[0].startsWith('--')) throw new Error(`invalid or missing option: ${key}`);
    if (values.has(key) && key !== '--context') throw new Error(`duplicate option: ${key}`);
    values.set(key, [...values.get(key) ?? [], args.shift()!]);
  }
  const get = (key: string) => values.get(key)?.[0];
  const repository = get('--repository');
  if (!repository) throw new Error('--repository is required');
  let result;
  if (command === 'invoke') {
    const workflow = get('--workflow'), input = get('--input');
    if (!workflow || !input) throw new Error('--workflow and --input are required');
    result = await invoke({ repository, workflow, input, newWorktree, ...(get('--ref') ? { ref: get('--ref')! } : {}), ...(get('--worktree') ? { worktreeId: get('--worktree')! } : {}), ...(get('--run') ? { runId: get('--run')! } : {}), ...(get('--question') ? { question: get('--question')! } : {}), contexts: values.get('--context') ?? [] });
    process.exitCode = result.exitCode;
  } else {
    const id = get('--invocation'); if (!id || newWorktree) throw new Error('history requires --invocation');
    const store = openRepositoryStore(repositoryIdentity(repository).common);
    try { result = store.readHistory(id); } finally { store.close(); }
  }
  process.stdout.write(JSON.stringify(result, null, json ? 0 : 2) + '\n');
}
main().catch(error => { process.stderr.write(`software-factory: ${error instanceof Error ? error.message : 'startup refused'}\n`); process.exitCode = 3; });
