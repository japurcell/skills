import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { dirname, join, sep } from 'node:path';
import { createCodexAdapter } from './adapters/codex.js';
import { createCopilotAdapter } from './adapters/copilot.js';
import type { AgentAdapter } from './adapters/types.js';
import { directoryIdentity } from './install-candidate.js';
import { readInstalledReceipt } from './install-publication.js';
import { publicationIntentPath, readPublicationRecord, verifyPublicationLayout } from './install-publication-state.js';
import { validateBoundProviderSources, type VerifiedInstallSelection } from './installation-bindings.js';
import { sendDesktopNotification } from './native/notifications.js';
import type { NotificationSender } from './notifications.js';
import { validateReleaseBundle } from './release.js';
import { readInstalledCompletion, type Claim } from './store.js';
import { repositoryIdentity } from './workspace.js';

type Providers = VerifiedInstallSelection['providers'];
export interface InstalledBindings {
  readonly common: string;
  readonly adapters: Record<string, AgentAdapter>;
  readonly notificationSender: NotificationSender;
}
function fail(): never { throw new Error('installed binding refused'); }
function hash(bytes: Buffer): string { return createHash('sha256').update(bytes).digest('hex'); }
function nativeEnvironment(): Record<string, string> {
  const selected: Record<string, string> = {};
  for (const name of ['HOME', 'PATH', 'TMPDIR', 'LANG', 'LC_ALL', 'TERM', 'CODEX_HOME',
    'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'GH_CONFIG_DIR']) {
    const value = process.env[name];
    if (value !== undefined) selected[name] = value;
  }
  return selected;
}
function external(path: string, factory: string): void {
  if (path === factory || path.startsWith(`${factory}${sep}`)) fail();
}
function boundAdapters(providers: Providers, factory: string): Record<string, AgentAdapter> {
  const adapters: Record<string, AgentAdapter> = {}, environment = nativeEnvironment();
  if (providers.codex) {
    const source = providers.codex;
    external(source.executable, factory);
    const adapter = createCodexAdapter({ executable: source.executable, sha256: source.sha256, environment });
    adapters.codex = {
      ...adapter,
      capabilities: adapter.capabilities.filter(value => value !== 'workspace-write' || source.modes.includes('workspace-write')),
      validateProfile(inputs) {
        if (!source.modes.includes(inputs.permissions)) throw new Error('Codex installed mode unselected');
        adapter.validateProfile(inputs);
      },
      start(request) {
        if (!source.modes.includes(request.inputs.permissions)) throw new Error('Codex installed mode unselected');
        return adapter.start(request);
      },
    };
  }
  if (providers.copilot) {
    const source = providers.copilot;
    external(source.packageRoot, factory);
    external(source.manifestFile, factory);
    adapters.copilot = createCopilotAdapter({ packageRoot: source.packageRoot,
      manifestFile: source.manifestFile, manifestSha256: source.manifestSha256, environment });
  }
  return adapters;
}

/** No provider is constructed until its exact external artifact and selected modes pass qualification. */
export function createSelectedAdapters(providers: unknown, factory: string): Record<string, AgentAdapter> {
  validateBoundProviderSources(providers);
  return boundAdapters(providers as Providers, factory);
}

/** The actual module location selects installed mode; no environment or CLI flag can assert it. */
export function installedCommonForCli(modulePath: string): string | null {
  const common = dirname(dirname(dirname(dirname(dirname(modulePath)))));
  return join(common, 'factory', 'install', 'runtime', 'dist', 'cli.js') === modulePath ? common : null;
}

/** Verify durable ownership after temporary stage cleanup, before CLI dispatch or provider construction. */
export async function loadInstalledBindings(modulePath: string, repository?: string, commonArg?: string): Promise<InstalledBindings | null> {
  const common = installedCommonForCli(modulePath);
  if (common === null) return null;
  try {
    if (realpathSync(modulePath) !== modulePath || realpathSync(common) !== common) fail();
    if (commonArg !== undefined && commonArg !== common) fail();
    if (repository !== undefined && (await repositoryIdentity(repository)).common !== common) fail();
    const factory = join(common, 'factory');
    directoryIdentity(factory);
    const { receipt, sha256 } = readInstalledReceipt(common);
    const { completion, repositoryId, release } = readInstalledCompletion(common, receipt.operationId);
    if (completion.version !== 1 || completion.operationId !== receipt.operationId
      || completion.repositoryId !== receipt.repositoryId || repositoryId !== receipt.repositoryId
      || completion.claimId !== receipt.claimId || completion.selectionDigest !== receipt.selectionDigest
      || completion.manifestSha256 !== receipt.manifestSha256 || completion.receiptId !== receipt.receiptId
      || completion.receiptSha256 !== sha256 || release !== receipt.release
      || receipt.candidate.path !== join(factory, `install-candidate-${receipt.operationId}`)) fail();
    const synthetic: Claim = { id: receipt.claimId, token: '', kind: 'maintenance', resourceKey: receipt.repositoryId,
      invocationId: null, owner: { host: '', pid: 0, start: null }, maintenance: {
        operationId: receipt.operationId, repositoryId: receipt.repositoryId, kind: 'install', release: receipt.release,
        targetReleaseSha256: receipt.manifestSha256, selectionDigest: receipt.selectionDigest, artifactDigests: {},
        targetSchema: receipt.targetSchema, stagePath: '', stageDigest: receipt.stageDigest, stageIdentity: null,
        phase: 'validating', ownedReceiptId: receipt.receiptId, backupId: null, ticketNonceHash: null,
        ticketConsumed: true, candidate: receipt.candidate,
      } };
    const layout = verifyPublicationLayout(common, synthetic);
    if (!layout.intent || layout.install !== 'published' || layout.toolchain !== 'published'
      || layout.intent.installIdentity !== receipt.installIdentity
      || layout.intent.toolchainIdentity !== receipt.toolchainIdentity
      || hash(readPublicationRecord(publicationIntentPath(common, receipt.operationId))) !== receipt.publicationIntentSha256) fail();
    const runtime = join(factory, 'install', 'runtime');
    const manifest = validateReleaseBundle(runtime, receipt.manifestSha256);
    const platform = `${process.platform}-${process.arch}`;
    if (manifest.version !== receipt.release || manifest.platform !== platform
      || manifest.node.sha256 !== layout.receipt.nodeArchiveSha256
      || JSON.stringify(layout.receipt.omittedLinks) !== JSON.stringify(['bin/corepack', 'bin/npm', 'bin/npx'])
      || hash(readFileSync(join(factory, 'toolchain', 'package-lock.json')))
        !== hash(readFileSync(join(runtime, 'toolchain', 'package-lock.json')))
      || process.versions.node !== '24.22.1') fail();
    const nodePath = join(factory, 'install', 'node', 'bin', 'node');
    const nodeFile = lstatSync(nodePath);
    if (!nodeFile.isFile() || nodeFile.isSymbolicLink() || realpathSync(nodePath) !== nodePath
      || process.execPath !== nodePath) fail();
    const adapters = createSelectedAdapters(layout.receipt.providers, factory);
    return { common, adapters, notificationSender: sendDesktopNotification };
  } catch { fail(); }
}
