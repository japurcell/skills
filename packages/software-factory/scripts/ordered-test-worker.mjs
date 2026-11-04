import { once } from 'node:events';
import { run } from 'node:test';
import { tap } from 'node:test/reporters';
import { labels, telemetry } from '../qualification/selector-timing.mjs';

async function runFiles({ files, concurrency, cwd, execArgv }, signal) {
  const summaries = new Map();
  let finalSummary;
  let failed = false;
  const stream = run({ files, concurrency, cwd, execArgv, signal });
  for (const event of ['dequeue', 'complete']) stream.on(`test:${event}`, data => {
    telemetry()?.mark(event, labels(data.file ?? data.name, data.name));
  });
  stream.on('test:fail', () => { failed = true; });
  stream.on('test:summary', (summary) => {
    telemetry()?.mark('summary', labels(summary.file));
    if (summary.file === undefined) finalSummary = summary;
    else summaries.set(summary.file, summary);
  });
  for await (const chunk of stream.compose(tap)) {
    if (!process.stdout.write(chunk)) await once(process.stdout, 'drain');
  }
  const complete = finalSummary?.counts.tests > 0 &&
    finalSummary.counts.cancelled === 0 && finalSummary.counts.skipped === 0 && finalSummary.counts.todo === 0 &&
    finalSummary.counts.tests ===
    [...summaries.values()].reduce((total, summary) => total + summary.counts.tests, 0) &&
    files.every((file) => summaries.get(file)?.counts.tests > 0);
  if (!complete) process.stderr.write('factory tests: incomplete test execution\n');
  return !failed && finalSummary?.success && complete ? 0 : 1;
}

const controller = new AbortController();
process.on('message', (message) => { if (message === 'abort') { telemetry()?.mark('cancel'); controller.abort(); } });
process.on('disconnect', () => { telemetry()?.mark('cancel'); controller.abort(); });
try {
  const config = JSON.parse(process.argv[2]);
  telemetry(config.timingWorkerId);
  process.exitCode = await runFiles(config, controller.signal);
} catch (error) {
  process.stderr.write(`factory tests: ${error.message}\n`);
  process.exitCode = 1;
} finally {
  if (process.connected) process.disconnect();
}
