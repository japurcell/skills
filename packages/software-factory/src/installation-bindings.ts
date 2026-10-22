import { createHash } from 'node:crypto';
import { closeSync, constants, fstatSync, lstatSync, openSync, readSync, realpathSync } from 'node:fs';
import { isAbsolute, join, parse, resolve, sep } from 'node:path';
import { validateCopilotPackageArtifact } from './adapters/copilot.js';
import { validateReleaseBundle, type ReleasePlatform } from './release.js';

const CODEX_SHA256 = '8813367285524ac798dd96d1b071aea30d58708c7226fd236cd275cf1cfdee31';
const COPILOT_MANIFEST_SHA256 = 'd7ff80ea8643df65f47546df95f77b07a7130d8bab8bc9ae8886eb23a913e696';
const MAX_NODE_ARCHIVE_BYTES = 128 * 1024 * 1024;
const MAX_CODEX_EXECUTABLE_BYTES = 300 * 1024 * 1024;
type Mode = 'read-only' | 'workspace-write';

export interface InstallSelection {
  readonly bundleRoot: string;
  readonly manifestSha256: string;
  readonly nodeArchivePath: string;
  readonly providers?: {
    readonly codex?: { readonly executable: string; readonly modes: readonly Mode[] };
    readonly copilot?: { readonly packageRoot: string; readonly manifestFile: string; readonly modes: readonly ['read-only'] };
  };
}
export interface VerifiedInstallSelection {
  readonly bundle: { readonly root: string; readonly manifestSha256: string; readonly version: string; readonly platform: ReleasePlatform };
  readonly node: { readonly archivePath: string; readonly version: 'v24.22.1'; readonly url: string; readonly sha256: string; readonly bytes: number };
  readonly windowsHelper?: { readonly path: string; readonly sha256: string; readonly qualificationRun: '39808257041' };
  readonly providers: {
    readonly codex?: { readonly executable: string; readonly version: '0.163.0'; readonly sha256: string; readonly bytes: number; readonly model: 'gpt-6-luna'; readonly reasoning: 'low'; readonly modes: readonly Mode[] };
    readonly copilot?: { readonly packageRoot: string; readonly manifestFile: string; readonly version: '1.0.101'; readonly manifestSha256: string; readonly model: 'gpt-6-luna'; readonly reasoning: 'low'; readonly modes: readonly ['read-only'] };
  };
}

function fail(message: string): never { throw new Error(`install selection: ${message}`); }
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('object required');
  return value as Record<string, unknown>;
}
function keys(value: Record<string, unknown>, required: readonly string[], optional: readonly string[] = []): void {
  if (required.some(key => !Object.hasOwn(value, key)) || Object.keys(value).some(key => !required.includes(key) && !optional.includes(key)))
    fail('unknown or missing selection field');
}

/** Every component must be a real directory; the leaf must have the requested file type. */
function canonicalPath(value: unknown, kind: 'file' | 'directory'): string {
  if (typeof value !== 'string' || !isAbsolute(value) || resolve(value) !== value) fail('canonical absolute path required');
  const root = parse(value).root;
  let current = root;
  for (const part of value.slice(root.length).split(sep).filter(Boolean)) {
    current = join(current, part);
    const info = lstatSync(current);
    if (info.isSymbolicLink()) fail('linked path refused');
    if (current !== value && !info.isDirectory()) fail('non-directory path component');
  }
  const info = lstatSync(value);
  if ((kind === 'file' && !info.isFile()) || (kind === 'directory' && !info.isDirectory()) || realpathSync(value) !== value)
    fail(`canonical ${kind} required`);
  return value;
}

/** Hash only a bounded, regular source file through an open descriptor. */
function checkedHash(path: string, maximum: number): { sha256: string; bytes: number } {
  const descriptor = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const info = fstatSync(descriptor);
    if (!info.isFile() || info.size <= 0 || info.size > maximum) fail('artifact size or type refused');
    const digest = createHash('sha256');
    const buffer = Buffer.allocUnsafe(64 * 1024);
    let offset = 0;
    while (offset < info.size) {
      const count = readSync(descriptor, buffer, 0, Math.min(buffer.length, info.size - offset), offset);
      if (count === 0) fail('artifact changed during read');
      digest.update(buffer.subarray(0, count));
      offset += count;
    }
    if (fstatSync(descriptor).size !== info.size) fail('artifact changed during read');
    return { sha256: digest.digest('hex'), bytes: info.size };
  } finally { closeSync(descriptor); }
}

function modes(value: unknown, allowed: readonly Mode[]): readonly Mode[] {
  if (!Array.isArray(value) || value.length === 0 || value.length > allowed.length) fail('unqualified provider modes');
  const selected = [...value] as unknown[];
  if (selected.some(mode => !allowed.includes(mode as Mode)) || new Set(selected).size !== selected.length) fail('unqualified provider modes');
  return Object.freeze(selected as Mode[]);
}

/** Bind only qualified source bytes to an externally selected release bundle. This performs no installation. */
export function validateInstallSelection(value: unknown): VerifiedInstallSelection {
  const selected = object(value);
  keys(selected, ['bundleRoot', 'manifestSha256', 'nodeArchivePath'], ['providers']);
  const bundleRoot = canonicalPath(selected.bundleRoot, 'directory');
  if (typeof selected.manifestSha256 !== 'string') fail('external manifest SHA256 required');
  const manifest = validateReleaseBundle(bundleRoot, selected.manifestSha256);
  const nodeArchivePath = canonicalPath(selected.nodeArchivePath, 'file');

  const providers = selected.providers === undefined ? {} : object(selected.providers);
  keys(providers, [], ['codex', 'copilot']);
  const verifiedProviders: {
    codex?: VerifiedInstallSelection['providers']['codex'];
    copilot?: VerifiedInstallSelection['providers']['copilot'];
  } = {};
  if (providers.codex !== undefined || providers.copilot !== undefined) {
    if (manifest.platform !== 'darwin-arm64') fail('native provider platform unqualified');
  }
  if (providers.codex !== undefined) {
    const source = object(providers.codex);
    keys(source, ['executable', 'modes']);
    const selectedModes = modes(source.modes, ['read-only', 'workspace-write']);
    const executable = canonicalPath(source.executable, 'file');
    const measured = checkedHash(executable, MAX_CODEX_EXECUTABLE_BYTES);
    if (measured.sha256 !== CODEX_SHA256) fail('unqualified Codex executable hash');
    verifiedProviders.codex = Object.freeze({ executable, version: '0.163.0', sha256: CODEX_SHA256, bytes: measured.bytes,
      model: 'gpt-6-luna', reasoning: 'low', modes: selectedModes });
  }
  if (providers.copilot !== undefined) {
    const source = object(providers.copilot);
    keys(source, ['packageRoot', 'manifestFile', 'modes']);
    const selectedModes = modes(source.modes, ['read-only']);
    const packageRoot = canonicalPath(source.packageRoot, 'directory');
    const manifestFile = canonicalPath(source.manifestFile, 'file');
    validateCopilotPackageArtifact({ packageRoot, manifestFile, manifestSha256: COPILOT_MANIFEST_SHA256 });
    verifiedProviders.copilot = Object.freeze({ packageRoot, manifestFile, version: '1.0.101', manifestSha256: COPILOT_MANIFEST_SHA256,
      model: 'gpt-6-luna', reasoning: 'low',
      modes: selectedModes as readonly ['read-only'] });
  }

  const measuredNode = checkedHash(nodeArchivePath, MAX_NODE_ARCHIVE_BYTES);
  if (measuredNode.sha256 !== manifest.node.sha256) fail('unqualified Node archive hash');
  const windowsHelper = manifest.windowsHelper === undefined ? undefined : Object.freeze({
    path: join(bundleRoot, manifest.windowsHelper.path), sha256: manifest.windowsHelper.sha256, qualificationRun: manifest.windowsHelper.qualificationRun,
  });
  return Object.freeze({
    bundle: Object.freeze({ root: bundleRoot, manifestSha256: selected.manifestSha256, version: manifest.version, platform: manifest.platform }),
    node: Object.freeze({ archivePath: nodeArchivePath, version: manifest.node.version, url: manifest.node.url, sha256: manifest.node.sha256, bytes: measuredNode.bytes }),
    ...(windowsHelper ? { windowsHelper } : {}),
    providers: Object.freeze(verifiedProviders),
  }) as VerifiedInstallSelection;
}
