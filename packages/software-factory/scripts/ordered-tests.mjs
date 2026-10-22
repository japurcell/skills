import { once } from 'node:events';
import { resolve } from 'node:path';
import { run } from 'node:test';
import { tap } from 'node:test/reporters';

// The programmatic runner schedules its files in array order. The --test CLI
// expands and sorts positional paths before it starts test processes.
export async function runOrderedTests(files, { concurrency, cwd, execArgv = [], signal } = {}) {
  if (files.length === 0) throw new Error('no test files selected');
  const selected = files.map((file) => resolve(cwd, file));
  const summaries = new Map();
  let finalSummary;
  let failed = false;
  const stream = run({ files: selected, concurrency, cwd, execArgv, signal });
  stream.on('test:fail', () => { failed = true; });
  stream.on('test:summary', (summary) => {
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
    selected.every((file) => summaries.get(file)?.counts.tests > 0);
  if (!complete) process.stderr.write('factory tests: incomplete test execution\n');
  return !failed && finalSummary?.success && complete ? 0 : 1;
}
