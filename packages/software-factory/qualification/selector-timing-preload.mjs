import { channel } from 'node:diagnostics_channel';
import { labels, telemetry } from './selector-timing.mjs';

const collector = telemetry();
if (collector) {
  const running = new Map();
  const failed = new Set();
  channel('tracing:node.test:start').subscribe(data => {
    const context = labels(data.file, data.name);
    if (!context.caseId) return;
    const key = context.fileId + '/' + context.caseId;
    running.set(key, collector.begin('case', context));
  });
  channel('tracing:node.test:end').subscribe(data => {
    const context = labels(data.file, data.name), key = context.fileId + '/' + context.caseId;
    running.get(key)?.(failed.has(key) ? 'failed' : 'ok'); running.delete(key); failed.delete(key);
  });
  channel('tracing:node.test:error').subscribe(data => {
    const context = labels(data.file, data.name);
    failed.add(context.fileId + '/' + context.caseId);
  });
}
