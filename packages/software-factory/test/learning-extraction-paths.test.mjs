import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fixture } from './fixtures/learning-extraction-fixture.mjs';

test('extraction rejects diff paths that disagree with the single declared target', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' }).saved;
    const attemptId = repo.history(source.invocationId).attempts.find(item => item.operationKey === 'observed').id;
    const target = { scope: 'repository', path: '.factory/prompts/check.md' };
    const base = { key: 'path-check', summary: 'Clarify the selected check.', target,
      supportingEvidence: [{ invocationId: source.invocationId, attemptId }], contraryEvidence: [], suggestedCases: ['Selected check'] };
    const cases = [
      '--- a/other.md\n+++ b/other.md\n@@ -1 +1 @@\n-old\n+new',
      '--- a/.factory/prompts/check.md\n+++ b/.factory/prompts/check.md\n@@ -1 +1 @@\n-old\n+new\n--- a/other.md\n+++ b/other.md\n@@ -1 +1 @@\n-old\n+new',
      '--- a/.factory/prompts/../agents.json\n+++ b/.factory/prompts/../agents.json\n@@ -1 +1 @@\n-old\n+new',
      'diff --git a/.factory/prompts/check.md b/.factory/prompts/check.md\nrename from other.md\nrename to .factory/prompts/check.md\n--- a/.factory/prompts/check.md\n+++ b/.factory/prompts/check.md\n@@ -1 +1 @@\n-old\n+new',
    ];
    for (const diff of cases) {
      const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source.invocationId }] },
        { kind: 'result', payload: { proposals: [{ ...base, diff }] } });
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.saved.diagnostic, /result invalid|unresolved invalid/i);
    }
  } finally { repo.dispose(); }
});

test('extraction accepts a new-file diff without applying it', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' }).saved;
    const attemptId = repo.history(source.invocationId).attempts.find(item => item.operationKey === 'observed').id;
    const diff = 'diff --git a/.factory/prompts/new.md b/.factory/prompts/new.md\nnew file mode 100644\nindex 0000000..1234567\n--- /dev/null\n+++ b/.factory/prompts/new.md\n@@ -0,0 +1 @@\n+New prompt';
    const proposal = { key: 'new-prompt', summary: 'Add a prompt.', target: { scope: 'repository', path: '.factory/prompts/new.md' }, diff,
      supportingEvidence: [{ invocationId: source.invocationId, attemptId }], contraryEvidence: [], suggestedCases: ['New prompt check'] };
    const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source.invocationId }] },
      { kind: 'result', payload: { proposals: [proposal] } });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.deepEqual(repo.report(result.saved.invocationId).proposals, [proposal]);
    assert.equal(existsSync(join(result.saved.worktree, '.factory/prompts/new.md')), false);
  } finally { repo.dispose(); }
});
