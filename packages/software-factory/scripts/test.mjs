import { spawn } from 'node:child_process';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';
import { runOrderedTests } from './ordered-tests.mjs';

// Explicit registration excludes fixtures, historical experiments and native calls from discovery.
const groups = {
  fixtures: [{ path: 'test/fixtures.test.mjs' }, { path: 'test/cli.test.mjs' }, { path: 'test/dispatch.test.mjs' }, { path: 'test/notification-selector-order.test.mjs' }],
  store: [{ path: 'test/store.test.mjs' }, { path: 'test/capture.test.mjs' }, { path: 'test/recording-integration.test.mjs' }, { path: 'test/placement.test.mjs' }], lifecycle: [{ path: 'test/startup.test.mjs' }, { path: 'test/shutdown.test.mjs' }], adapters: [{ path: 'test/adapters.test.mjs', provider: 'fake' }, { path: 'test/validated-results.test.mjs', provider: 'fake' }, { path: 'test/codex-adapter.test.mjs', provider: 'codex' }, { path: 'test/copilot-adapter.test.mjs', provider: 'copilot' }], workflows: [{ path: 'test/workflows.test.mjs', provider: 'fake' }], web: [{ path: 'test/dashboard.test.mjs', suite: 'server' }, { path: 'test/browser/ui.test.mjs', suite: 'browser' }, { path: 'test/browser/scale.test.mjs', suite: 'browser' }, { path: 'test/browser/reminders.test.mjs', suite: 'browser' }], notifications: [
    // Start fixed five-second uncertainty cases early so their waits overlap other fixtures.
    { path: 'test/notification-sender-uncertain.test.mjs' },
    { path: 'test/notification-success-uncertain.test.mjs' },
    { path: 'test/notification-reminder-uncertain.test.mjs' },
    { path: 'test/notification-records-cli.test.mjs' },
    { path: 'test/notification-records.test.mjs' },
    { path: 'test/notification-records-success.test.mjs' },
    { path: 'test/notification-reminders.test.mjs' },
    { path: 'test/notification-senders.test.mjs' },
    { path: 'test/notification-preflight.test.mjs', nodeOptions: ['--experimental-test-module-mocks'] },
    { path: 'test/notification-pipe.test.mjs', nodeOptions: ['--experimental-test-module-mocks'] },
  ],
  learning: [
    { path: 'test/learning.test.mjs', operation: 'extract', testConcurrency: 2 },
    { path: 'test/learning-extraction-sources.test.mjs', operation: 'extract', testConcurrency: 2 },
    { path: 'test/learning-extraction-evidence.test.mjs', operation: 'extract', testConcurrency: 2 },
    { path: 'test/learning-extraction-paths.test.mjs', operation: 'extract', testConcurrency: 2 },
    { path: 'test/learning-evaluation.test.mjs', operation: 'evaluate' },
    { path: 'test/learning-adoption.test.mjs', operation: 'adopt' },
  ], maintenance: [{ path: 'test/maintenance-controller.test.mjs', operation: 'controller' }], release: [{ path: 'test/release-packaging.test.mjs' }, { path: 'test/installation-bindings.test.mjs' }, { path: 'test/install-bootstrap.test.mjs', area: 'bootstrap' }, { path: 'test/install-bootstrap-process.test.mjs', area: 'bootstrap' }, { path: 'test/install-candidate.test.mjs', area: 'candidate' }, { path: 'test/install-publication.test.mjs', area: 'publication' }, { path: 'test/installed-bindings.test.mjs', area: 'installed' }, { path: 'test/install-platform-qualification.test.mjs', area: 'installed' }, { path: 'test/install-provider-selection.test.mjs', area: 'providers' }], qualification: [{ path: 'qualification/runtime.test.mjs', area: 'runtime' }, { path: 'qualification/ci.test.mjs', area: 'ci' }, { path: 'qualification/windows-etw-route.test.mjs', area: 'windows-etw-route' }],
};

try {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: {
    provider: { type: 'string' }, operation: { type: 'string' }, suite: { type: 'string' }, area: { type: 'string' },
  } });
  if (positionals.length !== 1) throw new Error('expected exactly one test group');
  const group = positionals[0];
  const names = group === 'all' ? Object.keys(groups).filter((name) => name !== 'qualification') : [group];
  const files = new Set();
  const extractionFiles = new Set();
  const nodeOptions = new Set();
  let extractionConcurrency;
  for (const name of names) {
    if (!(name in groups)) throw new Error(`unknown test group: ${name}`);
    const entries = groups[name];
    if (name === 'maintenance' && values.operation === undefined) {
      const required = ['controller', 'install', 'upgrade', 'dependencies', 'repair', 'uninstall', 'cleanup'];
      const missing = required.filter(operation => !entries.some(entry => entry.operation === operation));
      if (missing.length > 0) throw new Error(`maintenance: not implemented; missing operations: ${missing.join(', ')}`);
    }
    if (entries.length === 0) throw new Error(`${name}: not implemented; no tests registered`);
    const selected = entries.filter((entry) => Object.entries(values).every(([key, value]) => entry[key] === value));
    if (selected.length === 0) throw new Error(`${name}: no tests match supplied filters`);
    for (const entry of selected) {
      if (entry.testConcurrency !== undefined) {
        extractionFiles.add(entry.path);
        extractionConcurrency = entry.testConcurrency;
      } else {
        files.add(entry.path);
        for (const option of entry.nodeOptions ?? []) nodeOptions.add(option);
      }
    }
  }

  let child;
  let orderedController;
  let interruptedBy;
  const signalHandlers = new Map();
  for (const signal of ['SIGINT', 'SIGTERM']) {
    const handler = () => { interruptedBy = signal; child?.kill(signal); orderedController?.abort(); };
    signalHandlers.set(signal, handler);
    process.on(signal, handler);
  }
  const run = args => new Promise((resolve) => {
    const running = spawn(process.execPath, args, { cwd: new URL('../', import.meta.url), stdio: 'inherit' });
    child = running;
    let settled = false;
    const finish = code => {
      if (settled) return;
      settled = true;
      if (child === running) child = undefined;
      resolve(code);
    };
    running.on('error', (error) => { process.stderr.write(`${error.message}\n`); finish(1); });
    running.on('exit', (code, signal) => {
      finish(signal === 'SIGINT' ? 130 : signal === 'SIGTERM' ? 143 : code ?? 1);
    });
  });
  try {
    let exitCode = 0;
    if (files.size > 0 && !interruptedBy) {
      if (group === 'notifications') {
        orderedController = new AbortController();
        exitCode = await runOrderedTests([...files], {
          concurrency: 4,
          cwd: fileURLToPath(new URL('../', import.meta.url)),
          execArgv: [...nodeOptions],
          signal: orderedController.signal,
        });
        orderedController = undefined;
      } else {
        exitCode = await run([...nodeOptions, '--test', ...files]);
      }
    }
    if (!interruptedBy && exitCode !== 130 && exitCode !== 143 && extractionFiles.size > 0) {
      const extractionExitCode = await run([`--test-concurrency=${extractionConcurrency}`, '--test', ...extractionFiles]);
      if (exitCode === 0) exitCode = extractionExitCode;
    }
    if (interruptedBy) exitCode = interruptedBy === 'SIGINT' ? 130 : 143;
    process.exitCode = exitCode;
  } finally {
    for (const [signal, handler] of signalHandlers) process.off(signal, handler);
  }
} catch (error) {
  process.stderr.write(`factory tests: ${error.message}\n`);
  process.exitCode = 1;
}
