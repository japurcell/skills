import { createHash, randomUUID } from 'node:crypto';
import { closeSync, constants, fsyncSync, lstatSync, mkdirSync, openSync, readFileSync,
  realpathSync, renameSync, unlinkSync, writeSync } from 'node:fs';
import { dirname, join, relative, sep } from 'node:path';
import { directoryIdentity } from './install-candidate.js';
import { runManagedInstallCommand } from './install.js';
import { validateBoundProviderSources } from './installation-bindings.js';
import { publicationIntentPath, readPublicationRecord, verifyPublicationLayout, writePublicationRecord,
  type PublicationIntent } from './install-publication-state.js';
import { assertInstallBootstrapMarker, measureMaintenanceStage, recordMaintenanceStage } from './maintenance.js';
import { currentOwner } from './native/process.js';
import { validateReleaseBundle } from './release.js';
import { schemaVersion } from './schema.js';
import { openMaintenanceStore, type CandidateBinding, type Claim, type MaintenanceHandle } from './store.js';
import { repositoryIdentity } from './workspace.js';

const SHA = /^[0-9a-f]{64}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
interface InstalledReceipt {
  version: 1; receiptId: string; operationId: string; repositoryId: string; claimId: string;
  release: string; targetSchema: number; selectionDigest: string; manifestSha256: string; candidate: CandidateBinding;
  installIdentity: string; toolchainIdentity: string;
  publicationIntentSha256: string; stageDigest: string; authoring: { path: string; sha256: string; identity: string }[];
}
interface TicketHandle { operationId: string; repositoryId: string; claimId: string; token: string; root: string; commonDir: string }
interface AuthoringPlan {
  version: 1; operationId: string; manifestSha256: string;
  directories: { path: string; identity: string | null }[];
  files: { path: string; sha256: string; existingIdentity: string | null; existingSha256: string | null }[];
}
function fail(message: string): never { throw new Error(`install publication: ${message}`); }
function absent(path: string): boolean {
  try { lstatSync(path); return false; }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return true; throw error; }
}
function hash(bytes: Buffer | string): string { return createHash('sha256').update(bytes).digest('hex'); }
function identity(path: string): string {
  const info = lstatSync(path);
  if (!info.isFile() || info.isSymbolicLink() || info.nlink !== 1 || realpathSync(path) !== path) fail('regular file identity required');
  return `${info.dev}:${info.ino}`;
}
function authoringDirectoryIdentity(path: string): string {
  const info = lstatSync(path);
  if (!info.isDirectory() || info.isSymbolicLink() || realpathSync(path) !== path) fail('authoring directory collision');
  return `${info.dev}:${info.ino}`;
}
function flush(path: string): void {
  if (process.platform === 'win32') fail('Windows publication durability requires native qualification');
  const descriptor = openSync(path, constants.O_RDONLY);
  try { fsyncSync(descriptor); } finally { closeSync(descriptor); }
}
function assertOwner(claim: Claim): void {
  const owner = currentOwner();
  if (claim.owner.host !== owner.host || claim.owner.pid !== owner.pid || !owner.start || claim.owner.start !== owner.start)
    fail('claim is not owned by this live staged process');
}
function readTicket(ticketPath: string): TicketHandle {
  const value = JSON.parse(readPublicationRecord(ticketPath).toString('utf8')) as Record<string, unknown>;
  if (value['version'] !== 1 || typeof value['operationId'] !== 'string' || !UUID.test(value['operationId'])
    || typeof value['claimId'] !== 'string' || !UUID.test(value['claimId'])
    || typeof value['repositoryId'] !== 'string' || !UUID.test(value['repositoryId'])
    || typeof value['token'] !== 'string' || !UUID.test(value['token'])
    || typeof value['root'] !== 'string' || typeof value['commonDir'] !== 'string'
    || ticketPath !== join(String(value['commonDir']), 'factory', 'controller-staging', value['operationId'], 'handoff-ticket.json'))
    fail('private ticket identity invalid');
  return { operationId: value['operationId'], repositoryId: value['repositoryId'], claimId: value['claimId'],
    token: value['token'], root: value['root'], commonDir: value['commonDir'] };
}
async function gate(repository: string, handle: MaintenanceHandle): Promise<{ claim: Claim; layout: ReturnType<typeof verifyPublicationLayout> }> {
  const { root, common } = await repositoryIdentity(repository);
  if (root !== repository || common !== handle.commonDir) fail('repository placement changed');
  const store = openMaintenanceStore(common);
  try {
    const claim = store.readMaintenanceClaim(handle.operationId), recorded = claim.maintenance;
    if (claim.id !== handle.claimId || claim.token !== handle.token || claim.resourceKey !== handle.repositoryId
      || recorded?.kind !== 'install' || !recorded.candidate || !recorded.targetReleaseSha256
      || !recorded.ticketConsumed || !['modifying', 'validating'].includes(recorded.phase)) fail('claim/token/phase changed');
    assertOwner(claim);
    await assertInstallBootstrapMarker(repository, recorded.operationId, claim.id,
      recorded.selectionDigest, recorded.targetReleaseSha256);
    const stage = measureMaintenanceStage(recorded.stagePath);
    if (stage.stageDigest !== recorded.stageDigest || stage.stageIdentity !== recorded.stageIdentity)
      fail('bound controller stage changed');
    const layout = verifyPublicationLayout(common, claim);
    validateBoundProviderSources(layout.receipt.providers);
    return { claim, layout };
  } finally { store.close(); }
}
function authoringPaths(root: string, runtime: string, manifestSha256: string) {
  const manifest = validateReleaseBundle(runtime, manifestSha256);
  const files = manifest.files.filter(file => file.path.startsWith('templates/'));
  if (files.length !== 11) fail('release authoring inventory differs');
  const destination = join(root, '.factory');
  if (!absent(destination)) authoringDirectoryIdentity(destination);
  for (const sub of ['prompts', 'workflows']) {
    const path = join(destination, sub);
    if (!absent(path)) authoringDirectoryIdentity(path);
  }
  for (const file of files) {
    const name = file.path.slice('templates/'.length), path = join(destination, name);
    if (relative(destination, path).startsWith('..') || !path.startsWith(`${destination}${sep}`)) fail('authoring path invalid');
    if (absent(path)) continue;
    const info = lstatSync(path);
    if (info.size > 1024 * 1024) fail('existing authoring file exceeds bound');
    identity(path);
    if (name === 'package.json') {
      const value = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown>;
      if (value['type'] !== 'module') fail('existing authoring package type incompatible');
      for (const field of ['dependencies', 'devDependencies']) {
        const dependencies = value[field];
        if (dependencies === undefined) continue;
        if (!dependencies || typeof dependencies !== 'object' || Array.isArray(dependencies)) fail('authoring dependencies invalid');
        for (const [packageName, version] of Object.entries(dependencies)) {
          if (packageName === 'typescript' && version !== '7.0.2'
            || packageName === '@types/node' && version !== '24.19.2') fail('authoring toolchain declaration incompatible');
        }
      }
    } else if (name === 'agents.json') JSON.parse(readFileSync(path, 'utf8'));
  }
  return files.map(file => ({ name: file.path.slice('templates/'.length), sha256: file.sha256,
    source: join(runtime, file.path), destination: join(destination, file.path.slice('templates/'.length)) }));
}
function authoringPlanPath(common: string, operationId: string): string {
  return join(common, 'factory', `install-authoring-plan-${operationId}.json`);
}
function authoringSidecarPath(common: string, operationId: string, name: string): string {
  return join(common, 'factory', `install-authoring-${operationId}-${name}.json`);
}
function planAuthoring(root: string, runtime: string, manifestSha256: string, common: string,
  operationId: string, allowCreate: boolean): AuthoringPlan {
  const files = authoringPaths(root, runtime, manifestSha256), destination = join(root, '.factory');
  const planPath = authoringPlanPath(common, operationId);
  let plan: AuthoringPlan;
  if (absent(planPath)) {
    if (!allowCreate) fail('authoring plan missing after publication intent');
    plan = { version: 1, operationId, manifestSha256,
      directories: ['', 'prompts', 'workflows'].map(name => {
        const path = join(destination, name);
        return { path: name, identity: absent(path) ? null : authoringDirectoryIdentity(path) };
      }),
      files: files.map(file => ({ path: file.name, sha256: file.sha256,
        existingIdentity: absent(file.destination) ? null : identity(file.destination),
        existingSha256: absent(file.destination) ? null : hash(readFileSync(file.destination)) })) };
    writePublicationRecord(planPath, plan);
  } else {
    plan = JSON.parse(readPublicationRecord(planPath).toString('utf8')) as AuthoringPlan;
    if (plan.version !== 1 || plan.operationId !== operationId || plan.manifestSha256 !== manifestSha256
      || !Array.isArray(plan.directories) || !Array.isArray(plan.files) || plan.files.length !== files.length
      || JSON.stringify(plan.files.map(file => [file.path, file.sha256])) !== JSON.stringify(files.map(file => [file.name, file.sha256]))
      || JSON.stringify(plan.directories.map(dir => dir.path)) !== JSON.stringify(['', 'prompts', 'workflows']))
      fail('recorded authoring plan differs');
  }
  return plan;
}
function createAuthoring(root: string, runtime: string, manifestSha256: string, common: string, operationId: string) {
  const files = authoringPaths(root, runtime, manifestSha256), destination = join(root, '.factory');
  const plan = planAuthoring(root, runtime, manifestSha256, common, operationId, false);
  for (const dir of plan.directories) {
    const path = join(destination, dir.path);
    if (dir.identity !== null) {
      if (authoringDirectoryIdentity(path) !== dir.identity) fail('existing authoring directory changed');
      continue;
    }
    const sidecar = authoringSidecarPath(common, operationId, dir.path || 'root');
    if (absent(sidecar)) {
      if (!absent(path)) fail('unrecorded authoring directory collision');
      mkdirSync(path, { mode: 0o700 }); flush(dirname(path));
      writePublicationRecord(sidecar, { version: 1, operationId, path: dir.path, identity: authoringDirectoryIdentity(path) });
    }
    const recorded = JSON.parse(readPublicationRecord(sidecar).toString('utf8')) as Record<string, unknown>;
    if (recorded['version'] !== 1 || recorded['operationId'] !== operationId || recorded['path'] !== dir.path
      || recorded['identity'] !== authoringDirectoryIdentity(path)) fail('created authoring directory changed');
  }
  const created: InstalledReceipt['authoring'] = [];
  for (const [index, row] of plan.files.entries()) {
    const file = files[index]!;
    if (row.existingIdentity !== null) {
      if (identity(file.destination) !== row.existingIdentity || hash(readFileSync(file.destination)) !== row.existingSha256)
        fail('existing authoring file changed');
      continue;
    }
    const sidecar = authoringSidecarPath(common, operationId, String(index));
    if (absent(sidecar)) {
      if (!absent(file.destination)) fail('unrecorded authoring file collision');
      const bytes = readFileSync(file.source);
      if (hash(bytes) !== file.sha256) fail('release template changed');
      const descriptor = openSync(file.destination, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW ?? 0), 0o600);
      try { for (let offset = 0; offset < bytes.length;) offset += writeSync(descriptor, bytes, offset, bytes.length - offset, offset);
        fsyncSync(descriptor); } finally { closeSync(descriptor); }
      flush(dirname(file.destination));
      writePublicationRecord(sidecar, { version: 1, operationId, path: file.name,
        sha256: file.sha256, identity: identity(file.destination) });
    }
    const recorded = JSON.parse(readPublicationRecord(sidecar).toString('utf8')) as Record<string, unknown>;
    if (recorded['version'] !== 1 || recorded['operationId'] !== operationId || recorded['path'] !== file.name
      || recorded['sha256'] !== file.sha256 || recorded['identity'] !== identity(file.destination)
      || hash(readFileSync(file.destination)) !== file.sha256) fail('created authoring file changed');
    created.push({ path: file.name, sha256: file.sha256, identity: String(recorded['identity']) });
  }
  return created;
}
function validateAuthoring(root: string, runtime: string, manifestSha256: string, common: string,
  operationId: string, created: InstalledReceipt['authoring']): void {
  const files = authoringPaths(root, runtime, manifestSha256);
  const plan = JSON.parse(readPublicationRecord(authoringPlanPath(common, operationId)).toString('utf8')) as AuthoringPlan;
  if (plan.version !== 1 || plan.operationId !== operationId || plan.manifestSha256 !== manifestSha256
    || !Array.isArray(plan.directories) || !Array.isArray(plan.files) || plan.files.length !== files.length)
    fail('authoring plan absent or changed');
  const destination = join(root, '.factory');
  for (const dir of plan.directories) {
    const path = join(destination, dir.path);
    if (dir.identity !== null) { if (authoringDirectoryIdentity(path) !== dir.identity) fail('existing authoring directory changed'); }
    else {
      const recorded = JSON.parse(readPublicationRecord(authoringSidecarPath(common, operationId, dir.path || 'root')).toString('utf8')) as Record<string, unknown>;
      if (recorded['version'] !== 1 || recorded['operationId'] !== operationId || recorded['path'] !== dir.path
        || recorded['identity'] !== authoringDirectoryIdentity(path)) fail('created authoring directory changed');
    }
  }
  const recordedCreated: InstalledReceipt['authoring'] = [];
  for (const [index, row] of plan.files.entries()) {
    const file = files[index]!;
    if (row.path !== file.name || row.sha256 !== file.sha256) fail('authoring plan template differs');
    if (row.existingIdentity !== null) {
      if (identity(file.destination) !== row.existingIdentity || hash(readFileSync(file.destination)) !== row.existingSha256)
        fail('existing authoring file changed');
    } else {
      const saved = JSON.parse(readPublicationRecord(authoringSidecarPath(common, operationId, String(index))).toString('utf8')) as Record<string, unknown>;
      if (saved['version'] !== 1 || saved['operationId'] !== operationId || saved['path'] !== file.name
        || saved['sha256'] !== file.sha256 || saved['identity'] !== identity(file.destination)
        || hash(readFileSync(file.destination)) !== file.sha256) fail('created authoring file changed');
      recordedCreated.push({ path: file.name, sha256: file.sha256, identity: String(saved['identity']) });
    }
  }
  if (JSON.stringify(recordedCreated) !== JSON.stringify(created)) fail('installed authoring ownership differs');
  for (const row of created) {
    const file = files.find(item => item.name === row.path);
    if (!file || file.sha256 !== row.sha256 || identity(file.destination) !== row.identity
      || hash(readFileSync(file.destination)) !== row.sha256) fail('created authoring file differs');
  }
  if (files.some(file => absent(file.destination))) fail('authoring template absent');
}
function intentFor(claim: Claim): PublicationIntent {
  const recorded = claim.maintenance!, candidate = recorded.candidate!;
  return { version: 1, operationId: recorded.operationId, repositoryId: recorded.repositoryId, claimId: claim.id,
    selectionDigest: recorded.selectionDigest, candidateReceiptSha256: candidate.receiptSha256,
    candidateIdentity: candidate.identity, installIdentity: directoryIdentity(join(candidate.path, 'install')),
    toolchainIdentity: directoryIdentity(join(candidate.path, 'toolchain')) };
}
function assertIntent(common: string, intent: PublicationIntent): string {
  const path = publicationIntentPath(common, intent.operationId);
  const actual = readPublicationRecord(path);
  if (JSON.stringify(JSON.parse(actual.toString('utf8'))) !== JSON.stringify(intent)) fail('publication intent changed');
  return hash(actual);
}
function moveSubtree(common: string, claim: Claim, name: 'install' | 'toolchain'): void {
  const source = join(claim.maintenance!.candidate!.path, name), target = join(common, 'factory', name);
  if (!absent(target)) fail('publication target collision');
  renameSync(source, target);
  flush(dirname(source)); flush(dirname(target));
}
async function validatePublished(root: string, common: string, claim: Claim, authoring: InstalledReceipt['authoring']) {
  const recorded = claim.maintenance!, layout = verifyPublicationLayout(common, claim);
  if (layout.install !== 'published' || layout.toolchain !== 'published' || !layout.intent) fail('publication incomplete');
  validateBoundProviderSources(layout.receipt.providers);
  const factory = join(common, 'factory'), runtime = join(factory, 'install/runtime');
  const manifest = validateReleaseBundle(runtime, recorded.targetReleaseSha256!);
  if (manifest.node.sha256 !== layout.receipt.nodeArchiveSha256
    || layout.receipt.toolchainLockSha256 !== 'bea7cfb5a835aba203893966dde3e964418b12c69f8680e53a65b3603b9467d6'
    || hash(readFileSync(join(factory, 'toolchain/package-lock.json'))) !== layout.receipt.toolchainLockSha256
    || JSON.stringify(layout.receipt.omittedLinks) !== JSON.stringify(['bin/corepack', 'bin/npm', 'bin/npx']))
    fail('installed Node or toolchain selection differs');
  validateAuthoring(root, runtime, recorded.targetReleaseSha256!, common, recorded.operationId, authoring);
  const node = join(factory, 'install/node/bin/node'), npm = join(factory, 'install/node/lib/node_modules/npm/bin/npm-cli.js');
  const tsc = join(factory, 'toolchain/node_modules/typescript/bin/tsc');
  const env = { HOME: recorded.stagePath, PATH: '', LANG: 'C', LC_ALL: 'C', NO_COLOR: '1' };
  if ((await runManagedInstallCommand(node, ['--version'], factory, env)).trim() !== 'v24.22.1'
    || (await runManagedInstallCommand(node, [npm, '--version', '--update-notifier=false'], factory, env)).trim() !== '11.19.1'
    || (await runManagedInstallCommand(node, [tsc, '--version'], factory, env)).trim() !== 'Version 7.0.2')
    fail('installed direct command version differs');
}
function installedReceiptPath(common: string): string { return join(common, 'factory', 'installed-receipt.json'); }
function readInstalledReceipt(common: string): { receipt: InstalledReceipt; sha256: string } {
  const bytes = readPublicationRecord(installedReceiptPath(common));
  const value = JSON.parse(bytes.toString('utf8')) as InstalledReceipt;
  if (value.version !== 1 || !UUID.test(value.receiptId) || !UUID.test(value.operationId)
    || !UUID.test(value.claimId) || !UUID.test(value.repositoryId) || !SHA.test(value.selectionDigest)
    || !SHA.test(value.manifestSha256) || !SHA.test(value.publicationIntentSha256)
    || !SHA.test(value.stageDigest) || !Array.isArray(value.authoring) || value.targetSchema !== schemaVersion
    || typeof value.release !== 'string' || value.release.length < 1 || value.release.length > 256
    || !/^\d+:\d+$/.test(value.installIdentity) || !/^\d+:\d+$/.test(value.toolchainIdentity))
    fail('installed receipt invalid');
  return { receipt: value, sha256: hash(bytes) };
}

/** Called only by the foreground staged controller after one-use handoff consumption. */
export async function publishFirstInstall(ticketPath: string): Promise<{ state: 'ready'; operationId: string; repositoryId: string }> {
  const ticket = readTicket(ticketPath);
  const handle: MaintenanceHandle = { operationId: ticket.operationId, repositoryId: ticket.repositoryId,
    claimId: ticket.claimId, token: ticket.token, commonDir: ticket.commonDir };
  let { claim, layout } = await gate(ticket.root, handle);
  const common = ticket.commonDir, factory = join(common, 'factory');
  const runtime = join(layout.install === 'candidate' ? claim.maintenance!.candidate!.path : factory, 'install/runtime');
  planAuthoring(ticket.root, runtime, claim.maintenance!.targetReleaseSha256!, common, ticket.operationId, !layout.intent);
  if (!layout.intent) {
    const intent = intentFor(claim);
    writePublicationRecord(publicationIntentPath(common, ticket.operationId), intent);
    ({ claim, layout } = await gate(ticket.root, handle));
  }
  if (layout.install === 'candidate') {
    moveSubtree(common, claim, 'install');
    ({ claim, layout } = await gate(ticket.root, handle));
  }
  if (layout.toolchain === 'candidate') {
    moveSubtree(common, claim, 'toolchain');
    ({ claim, layout } = await gate(ticket.root, handle));
  }
  if (layout.install !== 'published' || layout.toolchain !== 'published') fail('publication not fully moved');
  const created = createAuthoring(ticket.root, join(factory, 'install/runtime'), claim.maintenance!.targetReleaseSha256!,
    common, ticket.operationId);
  await validatePublished(ticket.root, common, claim, created);
  if (claim.maintenance!.phase === 'modifying') await recordMaintenanceStage(handle, 'modifying', 'validating');
  ({ claim } = await gate(ticket.root, handle));
  const expectedReceipt = { version: 1 as const, operationId: ticket.operationId,
    repositoryId: ticket.repositoryId, claimId: ticket.claimId, release: claim.maintenance!.release,
    targetSchema: claim.maintenance!.targetSchema, selectionDigest: claim.maintenance!.selectionDigest,
    manifestSha256: claim.maintenance!.targetReleaseSha256!, candidate: claim.maintenance!.candidate!,
    installIdentity: layout.intent!.installIdentity, toolchainIdentity: layout.intent!.toolchainIdentity,
    publicationIntentSha256: assertIntent(common, layout.intent!), stageDigest: claim.maintenance!.stageDigest!, authoring: created };
  let owned: InstalledReceipt, receiptSha256: string;
  if (absent(installedReceiptPath(common))) {
    owned = { ...expectedReceipt, receiptId: randomUUID() };
    receiptSha256 = writePublicationRecord(installedReceiptPath(common), owned);
  } else {
    ({ receipt: owned, sha256: receiptSha256 } = readInstalledReceipt(common));
    const { receiptId, ...existing } = owned;
    if (!UUID.test(receiptId) || JSON.stringify(existing) !== JSON.stringify(expectedReceipt))
      fail('existing installed receipt differs from operation');
  }
  await validatePublished(ticket.root, common, claim, created);
  const store = openMaintenanceStore(common);
  try { await store.completeFirstInstall({ handle, receiptId: owned.receiptId, receiptSha256,
    selectionDigest: owned.selectionDigest, manifestSha256: owned.manifestSha256 }); }
  finally { store.close(); }
  await recoverCompletedFirstInstall(ticket.root, ticket.operationId);
  return { state: 'ready', operationId: ticket.operationId, repositoryId: ticket.repositoryId };
}

/** Exact ready-before-marker-unlink recovery; unrelated ready repositories cannot use it. */
export async function recoverCompletedFirstInstall(repository: string, operationId: string): Promise<void> {
  const { root, common } = await repositoryIdentity(repository);
  const { receipt, sha256 } = readInstalledReceipt(common);
  if (receipt.operationId !== operationId) fail('completed operation differs');
  const { markerClaim } = await assertInstallBootstrapMarker(root, operationId, receipt.claimId,
    receipt.selectionDigest, receipt.manifestSha256);
  const store = openMaintenanceStore(common);
  try {
    const { completion, repositoryId } = store.readFirstInstallCompletion(operationId);
    if (completion.version !== 1 || repositoryId !== receipt.repositoryId || completion.repositoryId !== receipt.repositoryId
      || completion.claimId !== receipt.claimId || completion.selectionDigest !== receipt.selectionDigest
      || completion.manifestSha256 !== receipt.manifestSha256 || completion.receiptId !== receipt.receiptId
      || completion.receiptSha256 !== sha256) fail('committed installed ownership differs');
  } finally { store.close(); }
  const original = markerClaim.maintenance!;
  if (receipt.release !== original.release || receipt.targetSchema !== original.targetSchema)
    fail('completed release or schema differs from bootstrap intent');
  const synthetic: Claim = { ...markerClaim, maintenance: { ...original, phase: 'validating', ticketConsumed: true,
    stageDigest: receipt.stageDigest, candidate: receipt.candidate } };
  const layout = verifyPublicationLayout(common, synthetic);
  validateBoundProviderSources(layout.receipt.providers);
  if (!layout.intent || layout.install !== 'published' || layout.toolchain !== 'published'
    || layout.intent.installIdentity !== receipt.installIdentity
    || layout.intent.toolchainIdentity !== receipt.toolchainIdentity
    || hash(readPublicationRecord(publicationIntentPath(common, operationId))) !== receipt.publicationIntentSha256)
    fail('completed publication layout differs');
  await validatePublished(root, common, synthetic, receipt.authoring);
  await assertInstallBootstrapMarker(root, operationId, receipt.claimId, receipt.selectionDigest, receipt.manifestSha256);
  unlinkSync(join(common, 'factory', 'bootstrap-incomplete'));
  flush(join(common, 'factory'));
}
