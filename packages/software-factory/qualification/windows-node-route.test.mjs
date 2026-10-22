import assert from 'node:assert/strict';
import test from 'node:test';
import { validateNodeRoute } from './windows-node-route.mjs';

const node = 'C:\\tools\\node-v24.22.1-win-x64\\node.exe';
const git = 'C:\\tools\\git\\mingw64\\bin\\git.exe';
const cmd = 'C:\\Windows\\System32\\cmd.exe';
const row = (kind, pid, value) => ({ kind, pid, value });
const trace = (children) => [
  row('ROOT', 10, node), row('CREATE', 10, node),
  ...children.map(([pid, image]) => row('CREATE', pid, image)),
  ...children.map(([pid]) => row('EXIT', pid, '0')),
  row('EXIT', 10, '0'), row('DONE', 10, '0'),
];
const result = (pid = 11) => ({ childPid: pid, spawnObserved: true, exitObserved: true,
  exitCode: 0, exitSignal: null, closeObserved: true, closeCode: 0, closeSignal: null,
  stdoutClosed: true, stderrClosed: true, stdoutBytes: 0, stderrBytes: 0,
  stdoutCapturedBytes: 0, stderrCapturedBytes: 0, stop: null });

test('public route protocol binds Node PID, direct child PID and exact images', () => {
  assert.equal(validateNodeRoute(trace([[11, git]]), result(), { node, helper: git }).ok, true);
  assert.match(validateNodeRoute(trace([[11, git]]), result(12), { node, helper: git }).reasons.join('; '),
    /reported child PID/);
  assert.match(validateNodeRoute(trace([[11, git], [12, cmd]]), result(), { node, helper: git }).reasons.join('; '),
    /unexpected process creation/);
  assert.match(validateNodeRoute(trace([[11, cmd]]), result(), { node, helper: git }).reasons.join('; '),
    /direct helper image/);
});

test('positive nested cmd requires its intended observed descendant and every exit', () => {
  assert.equal(validateNodeRoute(trace([[11, cmd], [12, cmd]]), result(),
    { node, helper: cmd, nested: cmd }).ok, true);
  assert.match(validateNodeRoute(trace([[11, cmd]]), result(),
    { node, helper: cmd, nested: cmd }).reasons.join('; '), /intended nested child/);
  const incomplete = trace([[11, cmd], [12, cmd]]).filter((item) => !(item.kind === 'EXIT' && item.pid === 12));
  assert.match(validateNodeRoute(incomplete, result(), { node, helper: cmd, nested: cmd }).reasons.join('; '),
    /process exit unobserved/);
  const failedNested = trace([[11, cmd], [12, cmd]]).map((item) => item.kind === 'EXIT' && item.pid === 12
    ? row('EXIT', 12, '1') : item);
  assert.match(validateNodeRoute(failedNested, result(), { node, helper: cmd, nested: cmd }).reasons.join('; '),
    /nested child exit/);
});

test('complete debug loop and both pipe closures are mandatory', () => {
  assert.match(validateNodeRoute(trace([[11, git]]).slice(0, -1), result(),
    { node, helper: git }).reasons.join('; '), /completed debug loop/);
  assert.match(validateNodeRoute(trace([[11, git]]), { ...result(), stderrClosed: false },
    { node, helper: git }).reasons.join('; '), /pipe closure/);
  const reordered = trace([[11, git]]);
  [reordered[2], reordered[3]] = [reordered[3], reordered[2]];
  assert.match(validateNodeRoute(reordered, result(), { node, helper: git }).reasons.join('; '),
    /event order/);
});

test('direct outcome must agree with independent EXIT and Node must finish cleanly', () => {
  const differentChildExit = trace([[11, git]]).map((item) => item.kind === 'EXIT' && item.pid === 11
    ? row('EXIT', 11, '7') : item);
  assert.match(validateNodeRoute(differentChildExit, result(), { node, helper: git }).reasons.join('; '),
    /direct helper exit differs/);
  const failedNode = trace([[11, git]]).map((item) => item.kind === 'EXIT' && item.pid === 10
    ? row('EXIT', 10, '1') : item.kind === 'DONE' ? row('DONE', 10, '1') : item);
  assert.match(validateNodeRoute(failedNode, result(), { node, helper: git }).reasons.join('; '),
    /Node root exit/);
});

test('stop controls require a requested direct kill and independently observed termination', () => {
  const stopped = { ...result(), exitCode: null, exitSignal: 'SIGTERM', closeCode: null,
    closeSignal: 'SIGTERM', stdoutBytes: 15, stdoutCapturedBytes: 15,
    stop: { reason: 'deadline', requestedAtMs: 501, killReturned: true } };
  const stoppedTrace = trace([[11, git]]).map((item) => item.kind === 'EXIT' && item.pid === 11
    ? row('EXIT', 11, '1') : item);
  assert.equal(validateNodeRoute(stoppedTrace, stopped, { node, helper: git, stop: 'deadline' }).ok, true);
  assert.match(validateNodeRoute(stoppedTrace, { ...stopped, stop: { ...stopped.stop, killReturned: false } },
    { node, helper: git, stop: 'deadline' }).reasons.join('; '), /direct stop outcome/);
});
