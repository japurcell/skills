import assert from 'node:assert/strict';
import test from 'node:test';
import { gitModes, parseTrace, validateTrace } from './windows-startup.mjs';

test('closed Git modes have exact native argv and no caller flags', () => {
  assert.deepEqual(gitModes, [
    ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--show-toplevel'],
    ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
    ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--path-format=absolute', '--git-dir'],
    ['--no-pager', '--no-lazy-fetch', 'worktree', 'list', '--porcelain', '-z'],
  ]);
});

test('trace requires a positive child control and complete direct exit', () => {
  const b64 = (text) => Buffer.from(text).toString('base64');
  const root = `ROOT\t10\t${b64('C:\\root.exe')}`;
  const created = `CREATE\t10\t${b64('C:\\root.exe')}`;
  const child = `CREATE\t11\t${b64('C:\\child.exe')}`;
  const exit = `EXIT\t10\t${b64('0')}`;
  const done = `DONE\t10\t${b64('0')}`;
  assert.equal(validateTrace(parseTrace([root, created, exit, done].join('\n')), 10, false).ok, true);
  assert.equal(validateTrace(parseTrace([root, created, child, exit, done].join('\n')), 10, false).ok, false);
  assert.equal(validateTrace(parseTrace([root, created, child, `EXIT\t11\t${b64('0')}`, exit, done].join('\n')), 10, true).ok, true);
  assert.equal(validateTrace(parseTrace([root, created, exit].join('\n')), 10, false).ok, false);
});
