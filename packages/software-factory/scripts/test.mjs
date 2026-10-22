import { spawn } from 'node:child_process';
import { parseArgs } from 'node:util';

// Explicit registration excludes fixtures, historical experiments and native calls from discovery.
const groups = {
  fixtures: [{ path: 'test/fixtures.test.mjs' }, { path: 'test/cli.test.mjs' }, { path: 'test/dispatch.test.mjs' }],
  store: [{ path: 'test/store.test.mjs' }, { path: 'test/capture.test.mjs' }, { path: 'test/recording-integration.test.mjs' }, { path: 'test/placement.test.mjs' }], lifecycle: [{ path: 'test/startup.test.mjs' }, { path: 'test/shutdown.test.mjs' }], adapters: [{ path: 'test/adapters.test.mjs', provider: 'fake' }, { path: 'test/codex-adapter.test.mjs', provider: 'codex' }], workflows: [{ path: 'test/workflows.test.mjs', provider: 'fake' }], web: [{ path: 'test/dashboard.test.mjs', suite: 'server' }], notifications: [{ path: 'test/notification-senders.test.mjs' }, { path: 'test/notification-preflight.test.mjs', nodeOptions: ['--experimental-test-module-mocks'] }, { path: 'test/notification-pipe.test.mjs', nodeOptions: ['--experimental-test-module-mocks'] }],
  learning: [], maintenance: [], qualification: [{ path: 'qualification/runtime.test.mjs', area: 'runtime' }, { path: 'qualification/ci.test.mjs', area: 'ci' }],
};

try {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: {
    provider: { type: 'string' }, operation: { type: 'string' }, suite: { type: 'string' }, area: { type: 'string' },
  } });
  if (positionals.length !== 1) throw new Error('expected exactly one test group');
  const group = positionals[0];
  const names = group === 'all' ? Object.keys(groups).filter((name) => name !== 'qualification') : [group];
  const files = new Set();
  const nodeOptions = new Set();
  for (const name of names) {
    if (!(name in groups)) throw new Error(`unknown test group: ${name}`);
    const entries = groups[name];
    if (entries.length === 0) throw new Error(`${name}: not implemented; no tests registered`);
    const selected = entries.filter((entry) => Object.entries(values).every(([key, value]) => entry[key] === value));
    if (selected.length === 0) throw new Error(`${name}: no tests match supplied filters`);
    for (const entry of selected) {
      files.add(entry.path);
      for (const option of entry.nodeOptions ?? []) nodeOptions.add(option);
    }
  }
  const child = spawn(process.execPath, [...nodeOptions, '--test', ...files], { cwd: new URL('../', import.meta.url), stdio: 'inherit' });
  for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
  child.on('error', (error) => { process.stderr.write(`${error.message}\n`); process.exitCode = 1; });
  child.on('exit', (code, signal) => { process.exitCode = signal === 'SIGINT' ? 130 : signal === 'SIGTERM' ? 143 : code ?? 1; });
} catch (error) {
  process.stderr.write(`factory tests: ${error.message}\n`);
  process.exitCode = 1;
}
