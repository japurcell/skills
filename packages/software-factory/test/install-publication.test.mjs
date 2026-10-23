import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';

const selection = { release: '1.2.3', selectionDigest: 'a'.repeat(64), targetReleaseSha256: 'b'.repeat(64),
  artifactDigests: { bundle: 'b'.repeat(64), node: 'c'.repeat(64) }, targetSchema: 7 };

async function fixture() {
  const { beginRepositoryBootstrap, measureMaintenanceStage, prepareMaintenanceHandoff,
    consumeMaintenanceHandoff } = await import('../dist/maintenance.js');
  const { currentOwner } = await import('../dist/native/process.js');
  const { scanOwnedTree, directoryIdentity, writeCandidateReceipt } = await import('../dist/install-candidate.js');
  const { openMaintenanceStore } = await import('../dist/store.js');
  const repository = createRepository();
  const handle = await beginRepositoryBootstrap(repository.path, selection, currentOwner());
  const factory = join(handle.commonDir, 'factory');
  const candidate = join(factory, `install-candidate-${handle.operationId}`);
  mkdirSync(candidate, { mode: 0o700 });
  for (const name of ['install', 'toolchain']) {
    mkdirSync(join(candidate, name), { mode: 0o700 });
    writeFileSync(join(candidate, name, 'payload.txt'), 'same controlled bytes', { mode: 0o600 });
  }
  const tree = scanOwnedTree(candidate, 'candidate'), receiptId = randomUUID(), rootIdentity = directoryIdentity(candidate);
  const receipt = { schema: 1, receiptId, operationId: handle.operationId, repositoryId: handle.repositoryId,
    claimId: handle.claimId, selectionDigest: selection.selectionDigest, manifestSha256: selection.targetReleaseSha256,
    nodeArchiveSha256: selection.artifactDigests.node, toolchainLockSha256: 'd'.repeat(64), omittedLinks: [],
    providers: {}, rootIdentity, treeDigest: tree.digest, entries: tree.rows };
  const receiptSha256 = writeCandidateReceipt(join(candidate, 'candidate-receipt.json'), receipt);
  const binding = { path: candidate, identity: rootIdentity, treeDigest: tree.digest, receiptId, receiptSha256 };
  mkdirSync(join(factory, 'controller-staging'), { mode: 0o700 });
  const stage = join(factory, 'controller-staging', handle.operationId);
  mkdirSync(stage, { mode: 0o700 }); mkdirSync(join(stage, 'payload'), { mode: 0o700 });
  writeFileSync(join(stage, 'payload/node'), 'stage fixture', { mode: 0o700 });
  const store = openMaintenanceStore(handle.commonDir);
  try { await store.bindInstallCandidate({ handle, candidate: binding, ...measureMaintenanceStage(stage) }); }
  finally { store.close(); }
  const prepared = await prepareMaintenanceHandoff(repository.path, handle);
  const ticket = JSON.parse(readFileSync(prepared.ticketPath, 'utf8'));
  writeFileSync(ticket.exitReceiptPath, `${JSON.stringify({ version: 1, operationId: handle.operationId,
    claimId: handle.claimId, stageDigest: prepared.stageDigest, nonce: ticket.nonce })}\n`, { mode: 0o600 });
  await consumeMaintenanceHandoff(prepared.ticketPath);
  const opened = openMaintenanceStore(handle.commonDir);
  let claim;
  try { claim = opened.readMaintenanceClaim(handle.operationId); } finally { opened.close(); }
  return { repository, handle, factory, candidate, receipt, claim, ticketPath: prepared.ticketPath, stage };
}

function intentFor(fixture, directoryIdentity) {
  const { handle, claim, candidate } = fixture;
  return { version: 1, operationId: handle.operationId, repositoryId: handle.repositoryId, claimId: handle.claimId,
    selectionDigest: selection.selectionDigest, candidateReceiptSha256: claim.maintenance.candidate.receiptSha256,
    candidateIdentity: claim.maintenance.candidate.identity,
    installIdentity: directoryIdentity(join(candidate, 'install')),
    toolchainIdentity: directoryIdentity(join(candidate, 'toolchain')) };
}

test('operation-bound publication intent survives each rename and rejects altered published bytes', async () => {
  const { verifyPublicationLayout, publicationIntentPath, writePublicationRecord } = await import('../dist/install-publication-state.js');
  const { directoryIdentity } = await import('../dist/install-candidate.js');
  const { inspectMaintenance, reclaimMaintenance } = await import('../dist/maintenance.js');
  const item = await fixture();
  try {
    const intent = intentFor(item, directoryIdentity);
    writePublicationRecord(publicationIntentPath(item.handle.commonDir, item.handle.operationId), intent);
    assert.deepEqual([verifyPublicationLayout(item.handle.commonDir, item.claim).install,
      verifyPublicationLayout(item.handle.commonDir, item.claim).toolchain], ['candidate', 'candidate']);
    renameSync(join(item.candidate, 'install'), join(item.factory, 'install'));
    assert.deepEqual([verifyPublicationLayout(item.handle.commonDir, item.claim).install,
      verifyPublicationLayout(item.handle.commonDir, item.claim).toolchain], ['published', 'candidate']);
    assert.equal((await inspectMaintenance(item.repository.path)).status, 'incomplete');
    await assert.rejects(reclaimMaintenance(item.repository.path, item.handle.operationId, { host: 'replacement', pid: process.pid, start: 'replacement' },
      { operatorConfirmed: true, note: 'fixture known-live owner remains' }), /known-live/);
    renameSync(join(item.candidate, 'toolchain'), join(item.factory, 'toolchain'));
    assert.deepEqual([verifyPublicationLayout(item.handle.commonDir, item.claim).install,
      verifyPublicationLayout(item.handle.commonDir, item.claim).toolchain], ['published', 'published']);
    writeFileSync(join(item.factory, 'install/payload.txt'), 'tampered published bytes');
    assert.throws(() => verifyPublicationLayout(item.handle.commonDir, item.claim), /inventory differs/);
    assert.equal((await inspectMaintenance(item.repository.path)).status, 'blocked');
  } finally { item.repository.dispose(); }
});

test('foreign same-byte and linked publication targets are never adopted', async () => {
  const { verifyPublicationLayout, publicationIntentPath, writePublicationRecord } = await import('../dist/install-publication-state.js');
  const { directoryIdentity } = await import('../dist/install-candidate.js');
  const { inspectMaintenance } = await import('../dist/maintenance.js');
  for (const linked of [false, true]) {
    const item = await fixture();
    try {
      writePublicationRecord(publicationIntentPath(item.handle.commonDir, item.handle.operationId),
        intentFor(item, directoryIdentity));
      if (linked) {
        const { symlinkSync } = await import('node:fs');
        symlinkSync(join(item.candidate, 'install'), join(item.factory, 'install'));
      } else {
        mkdirSync(join(item.factory, 'install'), { mode: 0o700 });
        writeFileSync(join(item.factory, 'install/payload.txt'), 'same controlled bytes', { mode: 0o600 });
      }
      assert.throws(() => verifyPublicationLayout(item.handle.commonDir, item.claim), /conflicting tree/);
      assert.equal((await inspectMaintenance(item.repository.path)).status, 'blocked');
      assert.equal(readFileSync(join(item.candidate, 'install/payload.txt'), 'utf8'), 'same controlled bytes');
    } finally { item.repository.dispose(); }
  }
});

test('stale ticket token, altered stage and changed candidate refuse before a publication move', async () => {
  const { publishFirstInstall } = await import('../dist/install-publication.js');
  for (const damage of ['token', 'stage', 'candidate']) {
    const item = await fixture();
    try {
      if (damage === 'token') {
        const ticket = JSON.parse(readFileSync(item.ticketPath, 'utf8'));
        ticket.token = randomUUID();
        writeFileSync(item.ticketPath, `${JSON.stringify(ticket)}\n`, { mode: 0o600 });
      } else if (damage === 'stage') writeFileSync(join(item.stage, 'payload/node'), 'changed stage');
      else writeFileSync(join(item.candidate, 'install/payload.txt'), 'changed candidate');
      await assert.rejects(publishFirstInstall(item.ticketPath), error => {
        assert.match(error.message, damage === 'token' ? /claim\/token\/phase/ : damage === 'stage' ? /stage changed/ : /candidate tree differs/);
        assert.ok(!error.message.includes(item.handle.token));
        return true;
      });
      assert.equal(existsSync(join(item.factory, 'install')), false);
      assert.equal(existsSync(join(item.factory, 'toolchain')), false);
      assert.equal(existsSync(join(item.factory, 'bootstrap-incomplete')), true);
    } finally { item.repository.dispose(); }
  }
});

test('a ready row cannot remove the marker until actual installed files validate', async () => {
  const { publicationIntentPath, writePublicationRecord } = await import('../dist/install-publication-state.js');
  const { directoryIdentity } = await import('../dist/install-candidate.js');
  const { recordMaintenanceStage, inspectMaintenance } = await import('../dist/maintenance.js');
  const { recoverCompletedFirstInstall } = await import('../dist/install-publication.js');
  const { openMaintenanceStore, openRepositoryStore } = await import('../dist/store.js');
  const item = await fixture();
  try {
    const intent = intentFor(item, directoryIdentity);
    const intentPath = publicationIntentPath(item.handle.commonDir, item.handle.operationId);
    const intentSha256 = writePublicationRecord(intentPath, intent);
    renameSync(join(item.candidate, 'install'), join(item.factory, 'install'));
    renameSync(join(item.candidate, 'toolchain'), join(item.factory, 'toolchain'));
    await recordMaintenanceStage(item.handle, 'modifying', 'validating');
    const receiptId = randomUUID();
    const receiptSha256 = writePublicationRecord(join(item.factory, 'installed-receipt.json'), {
      version: 1, receiptId, operationId: item.handle.operationId, repositoryId: item.handle.repositoryId,
      claimId: item.handle.claimId, release: selection.release, targetSchema: 7,
      selectionDigest: selection.selectionDigest,
      manifestSha256: selection.targetReleaseSha256, candidate: item.claim.maintenance.candidate,
      installIdentity: intent.installIdentity, toolchainIdentity: intent.toolchainIdentity,
      publicationIntentSha256: intentSha256, stageDigest: item.claim.maintenance.stageDigest, authoring: [],
    });
    const store = openMaintenanceStore(item.handle.commonDir);
    try { await store.completeFirstInstall({ handle: item.handle, receiptId, receiptSha256,
      selectionDigest: selection.selectionDigest, manifestSha256: selection.targetReleaseSha256 }); }
    finally { store.close(); }
    await assert.rejects(recoverCompletedFirstInstall(item.repository.path, item.handle.operationId));
    assert.equal(existsSync(join(item.factory, 'bootstrap-incomplete')), true);
    assert.equal((await inspectMaintenance(item.repository.path)).status, 'incomplete');
    assert.throws(() => openRepositoryStore(item.handle.commonDir), /incomplete bootstrap/);
  } finally { item.repository.dispose(); }
});

test('external selected provider descriptors require exact qualified source fields', async () => {
  const { validateBoundProviderSources } = await import('../dist/installation-bindings.js');
  assert.doesNotThrow(() => validateBoundProviderSources({}));
  assert.throws(() => validateBoundProviderSources({ codex: { executable: '/nonexistent', version: '0.163.0',
    sha256: '0'.repeat(64), bytes: 1, model: 'gpt-6-luna', reasoning: 'low', modes: ['read-only'] } }));
  assert.throws(() => validateBoundProviderSources({ copilot: { packageRoot: '/nonexistent', manifestFile: '/nonexistent',
    version: '1.0.101', manifestSha256: '0'.repeat(64), model: 'gpt-6-luna', reasoning: 'low', modes: ['workspace-write'] } }));
  assert.throws(() => validateBoundProviderSources({ unknown: true }), /selection field/);
});
