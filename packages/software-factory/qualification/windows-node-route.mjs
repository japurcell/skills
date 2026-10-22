// Public qualification protocol for a pinned Node spawn route, never a product import.
import { win32 } from 'node:path';

const image = (value) => typeof value === 'string'
  ? win32.normalize(value.replace(/^\\\\\?\\/, '')).toLowerCase() : '';
const rows = (records, kind) => records.filter((record) => record.kind === kind);

export function validateNodeRoute(records, result, expected) {
  const reasons = [];
  const roots = rows(records, 'ROOT');
  const created = rows(records, 'CREATE');
  const exited = rows(records, 'EXIT');
  const done = rows(records, 'DONE');
  const root = roots[0];
  const rootExit = exited.find((record) => record.pid === root?.pid);
  if (roots.length !== 1 || image(root?.value) !== image(expected.node))
    reasons.push('missing or wrong Node debug root');
  if (created.filter((record) => record.pid === root?.pid && image(record.value) === image(expected.node)).length !== 1)
    reasons.push('Node root creation or image mismatch');
  if (created.length !== new Set(created.map((record) => record.pid)).size)
    reasons.push('duplicate process creation');
  if (created.some((record) => exited.filter((exit) => exit.pid === record.pid).length !== 1) ||
      exited.some((record) => !created.some((creation) => creation.pid === record.pid)))
    reasons.push('process exit unobserved or unmatched');
  if (records[0] !== root || created.some((record) => {
    const exit = exited.find((item) => item.pid === record.pid);
    return exit && records.indexOf(exit) < records.indexOf(record);
  }) || created.filter((record) => record.pid !== root?.pid)
    .some((record) => records.indexOf(record) < records.indexOf(created.find((item) => item.pid === root?.pid))))
    reasons.push('process event order inconsistent');
  if (done.length !== 1 || done[0].pid !== root?.pid || done[0].value !== rootExit?.value ||
      records.at(-1) !== done[0] || rows(records, 'STOP_REQUESTED').length ||
      rows(records, 'STOP_OBSERVED').length || rows(records, 'ERROR').length)
    reasons.push('missing or interrupted completed debug loop');
  if (rootExit?.value !== '0') reasons.push('Node root exit was not clean');
  if (rows(records, 'DLL').some((record) => !created.some((creation) => creation.pid === record.pid)))
    reasons.push('module event belongs to unknown process');

  const children = created.filter((record) => record.pid !== root?.pid);
  const direct = children.find((record) => record.pid === result?.childPid);
  const directExit = exited.find((record) => record.pid === result?.childPid);
  if (!Number.isSafeInteger(result?.childPid) || result.childPid <= 0 || !direct)
    reasons.push('Node reported child PID is absent from independent trace');
  if (image(direct?.value) !== image(expected.helper)) reasons.push('direct helper image differs from pinned executable');
  const nested = children.filter((record) => record.pid !== result?.childPid);
  if (expected.nested) {
    if (nested.length !== 1 || image(nested[0]?.value) !== image(expected.nested))
      reasons.push('intended nested child not independently observed');
    else if (exited.find((record) => record.pid === nested[0].pid)?.value !== '0')
      reasons.push('nested child exit differed from intended success');
  } else if (nested.length && !expected.allowAdditional) {
    reasons.push('unexpected process creation');
  }
  if (!result?.spawnObserved || !result.exitObserved || !result.closeObserved ||
      !result.stdoutClosed || !result.stderrClosed)
    reasons.push('Node spawn, direct exit, close, or pipe closure incomplete');
  if (result?.exitCode !== result?.closeCode || result?.exitSignal !== result?.closeSignal)
    reasons.push('Node exit and close outcomes disagree');
  if (expected.stop) {
    if (result?.stop?.reason !== expected.stop || result.stop.killReturned !== true ||
        !Number.isFinite(result.stop.requestedAtMs) ||
        (result.exitCode === 0 && result.exitSignal === null))
      reasons.push('Node direct stop outcome unproved');
    if (directExit?.value === '0') reasons.push('stopped helper exited normally in independent trace');
  } else if (result?.stop || result?.exitCode !== (expected.exitCode ?? 0) || result?.exitSignal !== null)
    reasons.push('unexpected direct helper exit or stop');
  else if (directExit?.value !== String(result.exitCode))
    reasons.push('direct helper exit differs from independent trace');
  for (const stream of ['stdout', 'stderr']) {
    const bytes = result?.[`${stream}Bytes`];
    const captured = result?.[`${stream}CapturedBytes`];
    if (!Number.isSafeInteger(bytes) || bytes < 0 || !Number.isSafeInteger(captured) ||
        captured < 0 || captured > 262144 || captured !== Math.min(bytes, 262144))
      reasons.push(`${stream} byte count or 256 KiB capture bound invalid`);
  }
  return { ok: reasons.length === 0, reasons, children };
}
