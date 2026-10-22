import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, realpathSync, writeFileSync } from 'node:fs';
import { basename, dirname, isAbsolute, join, posix, resolve, sep } from 'node:path';

export type ReleasePlatform = 'darwin-arm64' | 'linux-x64' | 'win32-x64';
export interface NodeAsset { readonly version: 'v24.22.1'; readonly url: string; readonly sha256: string }
export interface WindowsHelperSelection {
  readonly path: string;
  readonly sha256: string;
  readonly qualificationRun: '39808257041';
}
export interface ReleaseSelection {
  readonly version: string;
  readonly platform: ReleasePlatform;
  readonly node: NodeAsset;
  readonly windowsHelper?: WindowsHelperSelection;
}
export interface ReleaseFile { readonly path: string; readonly bytes: number; readonly sha256: string }
export interface ReleaseManifest {
  readonly schema: 1;
  readonly version: string;
  readonly platform: ReleasePlatform;
  readonly node: NodeAsset;
  readonly windowsHelper?: { readonly path: 'native/windows-notify.exe'; readonly sha256: string; readonly qualificationRun: '39808257041' };
  readonly files: readonly ReleaseFile[];
}

const NODE_ASSETS: Readonly<Record<ReleasePlatform, NodeAsset>> = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz', sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz', sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
  'win32-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-win-x64.zip', sha256: 'd2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5' },
};
const QUALIFIED_WINDOWS_HELPER_SHA256 = 'f46ba4a408f8618d5e186ce29cf47bdac3411b67356136d79da4a0ed0c35ec44';
const WEB_FILES = ['app.js', 'index.html', 'style.css'] as const;
const TEMPLATE_FILES = [
  'agents.json', 'prompts/audit.md', 'prompts/implementation.md', 'prompts/planning.md',
  'prompts/recipe.md', 'prompts/review.md', 'workflows/audit.ts', 'workflows/change.ts',
  'workflows/evaluate.ts', 'workflows/learn.ts',
] as const;

function fail(message: string): never { throw new Error(`release package: ${message}`); }
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('invalid object');
  return value as Record<string, unknown>;
}
function keys(value: Record<string, unknown>, required: readonly string[], optional: readonly string[] = []) {
  if (required.some(key => !Object.hasOwn(value, key)) || Object.keys(value).some(key => !required.includes(key) && !optional.includes(key))) fail('unknown or missing descriptor field');
}
function hash(bytes: Buffer) { return createHash('sha256').update(bytes).digest('hex'); }
const MAX_FILE_BYTES = 32 * 1024 * 1024;
function checkedPath(value: unknown): string {
  if (typeof value !== 'string' || !value || value.includes('\\') || /[\x00-\x1f:]/.test(value) || posix.isAbsolute(value) ||
      value.split('/').some(part => !part || part === '.' || part === '..' || part.toLowerCase() === 'node_modules' || /[. ]$/.test(part) ||
        /^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)/i.test(part)) || posix.normalize(value) !== value) fail('unsafe manifest path');
  return value;
}
function checkedFile(path: string): Buffer {
  const info = lstatSync(path);
  if (info.isSymbolicLink()) fail(`symlink refused: ${path}`);
  if (!info.isFile()) fail(`non-regular file refused: ${path}`);
  if (info.size > MAX_FILE_BYTES) fail(`file exceeds release size limit: ${path}`);
  return readFileSync(path);
}
function checkedRelativeFile(root: string, relative: string): Buffer {
  let parent = root;
  const parts = checkedPath(relative).split('/');
  for (const part of parts.slice(0, -1)) {
    parent = join(parent, part);
    const info = lstatSync(parent);
    if (info.isSymbolicLink()) fail(`symlink refused: ${parent}`);
    if (!info.isDirectory()) fail(`non-directory path component: ${parent}`);
  }
  return checkedFile(join(parent, parts.at(-1)!));
}
function tree(root: string, prefix = ''): string[] {
  const path = prefix ? join(root, prefix) : root;
  const info = lstatSync(path);
  if (info.isSymbolicLink()) fail(`symlink refused: ${path}`);
  if (!info.isDirectory()) fail(`directory required: ${path}`);
  const result: string[] = [];
  for (const entry of readdirSync(path).sort()) {
    const relative = prefix ? `${prefix}/${entry}` : entry;
    checkedPath(relative);
    const child = join(root, relative);
    const childInfo = lstatSync(child);
    if (childInfo.isSymbolicLink()) fail(`symlink refused: ${child}`);
    if (childInfo.isDirectory()) result.push(...tree(root, relative));
    else if (childInfo.isFile()) result.push(relative);
    else fail(`non-regular file refused: ${child}`);
  }
  return result;
}
function treeDirectories(root: string, prefix = ''): string[] {
  const result: string[] = [];
  for (const entry of readdirSync(prefix ? join(root, prefix) : root)) {
    const relative = prefix ? `${prefix}/${entry}` : entry;
    if (lstatSync(join(root, relative)).isDirectory()) {
      result.push(relative, ...treeDirectories(root, relative));
    }
  }
  return result;
}
function sameInventory(actual: readonly string[], expected: readonly string[], context: string) {
  const a = [...actual].sort(); const e = [...expected].sort();
  if (a.length !== e.length || a.some((item, i) => item !== e[i])) fail(`${context}: missing or unowned content`);
  const folded = new Set<string>();
  for (const path of a) {
    const lower = path.toLowerCase();
    if (folded.has(lower)) fail(`${context}: case-insensitive path collision`);
    folded.add(lower);
  }
}
function assertCanonicalDirectory(path: string) {
  if (!isAbsolute(path) || resolve(path) !== path || !lstatSync(path).isDirectory()) fail(`canonical directory required: ${path}`);
}

/** Verify caller-selected release facts against the qualified, versioned artifact table. */
export function validateReleaseSelection(value: unknown): ReleaseSelection {
  const selection = object(value);
  keys(selection, ['version', 'platform', 'node'], ['windowsHelper']);
  if (typeof selection.version !== 'string' || !/^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$/.test(selection.version)) fail('invalid release version');
  if (typeof selection.platform !== 'string' || !Object.hasOwn(NODE_ASSETS, selection.platform)) fail('unqualified platform');
  const platform = selection.platform as ReleasePlatform;
  const node = object(selection.node);
  keys(node, ['version', 'url', 'sha256']);
  const pinned = NODE_ASSETS[platform];
  if (node.version !== pinned.version || node.url !== pinned.url || node.sha256 !== pinned.sha256) fail('unqualified Node asset');
  if (platform === 'win32-x64') {
    const helper = object(selection.windowsHelper);
    keys(helper, ['path', 'sha256', 'qualificationRun']);
    if (helper.qualificationRun !== '39808257041' || helper.sha256 !== QUALIFIED_WINDOWS_HELPER_SHA256 ||
        typeof helper.path !== 'string' || !isAbsolute(helper.path) || resolve(helper.path) !== helper.path) fail('unqualified Windows helper');
    if (hash(checkedFile(helper.path)) !== helper.sha256) fail('changed Windows helper hash');
  } else if ('windowsHelper' in selection) fail('unexpected Windows helper');
  return selection as unknown as ReleaseSelection;
}

function sourceFiles(sourceRoot: string): Map<string, Buffer> {
  assertCanonicalDirectory(sourceRoot);
  const source = tree(join(sourceRoot, 'src'));
  if (source.some(path => !path.endsWith('.ts')) || !source.includes('cli.ts') || !source.includes('learning.ts') || !source.includes('release.ts')) fail('missing or unexpected source module');
  const compiled = source.flatMap(path => {
    const stem = path.slice(0, -3);
    return [`${stem}.js`, `${stem}.js.map`, `${stem}.d.ts`];
  });
  sameInventory(tree(join(sourceRoot, 'web')), WEB_FILES, 'web source');
  sameInventory(tree(join(sourceRoot, 'templates')), TEMPLATE_FILES, 'templates');
  sameInventory(tree(join(sourceRoot, 'dist')), [...compiled, ...WEB_FILES.map(path => `web/${path}`)], 'built runtime');
  const result = new Map<string, Buffer>();
  for (const path of compiled) result.set(`dist/${path}`, checkedFile(join(sourceRoot, 'dist', path)));
  for (const path of WEB_FILES) {
    const built = checkedFile(join(sourceRoot, 'dist/web', path));
    if (!built.equals(checkedFile(join(sourceRoot, 'web', path)))) fail(`stale built web: ${path}`);
    result.set(`dist/web/${path}`, built);
  }
  for (const path of TEMPLATE_FILES) result.set(`templates/${path}`, checkedFile(join(sourceRoot, 'templates', path)));
  return result;
}

function releasePackageJson(version: string): Buffer {
  return Buffer.from(`${JSON.stringify({ name: '@local/software-factory-runtime', version, private: true, type: 'module' }, null, 2)}\n`);
}
function expectedManifest(selection: ReleaseSelection, files: Map<string, Buffer>): ReleaseManifest {
  const entries: ReleaseFile[] = [...files].map(([path, bytes]) => ({ path, bytes: bytes.length, sha256: hash(bytes) })).sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  return {
    schema: 1, version: selection.version, platform: selection.platform, node: NODE_ASSETS[selection.platform],
    ...(selection.platform === 'win32-x64' ? { windowsHelper: { path: 'native/windows-notify.exe' as const, sha256: QUALIFIED_WINDOWS_HELPER_SHA256, qualificationRun: '39808257041' as const } } : {}),
    files: entries,
  };
}

/** T15b must supply the selected manifest SHA256 when consuming a published bundle. */
export function validateReleaseBundle(root: string, expectedManifestSha256: string): ReleaseManifest {
  assertCanonicalDirectory(root);
  const manifestBytes = checkedFile(join(root, 'release-manifest.json'));
  if (manifestBytes.length > 1_048_576) fail('release manifest exceeds size limit');
  if (!/^[a-f0-9]{64}$/.test(expectedManifestSha256) || hash(manifestBytes) !== expectedManifestSha256) fail('changed release manifest hash');
  const parsed = object(JSON.parse(manifestBytes.toString('utf8')));
  keys(parsed, ['schema', 'version', 'platform', 'node', 'files'], ['windowsHelper']);
  if (parsed.schema !== 1 || !Array.isArray(parsed.files) || parsed.files.length > 4096) fail('unsupported release manifest');
  if (parsed.platform === 'win32-x64') {
    keys(object(parsed.windowsHelper), ['path', 'sha256', 'qualificationRun']);
    checkedRelativeFile(root, 'native/windows-notify.exe');
  }
  const selection = validateReleaseSelection({ version: parsed.version, platform: parsed.platform, node: parsed.node,
    ...(parsed.platform === 'win32-x64' ? { windowsHelper: { path: join(root, 'native/windows-notify.exe'), sha256: object(parsed.windowsHelper).sha256, qualificationRun: object(parsed.windowsHelper).qualificationRun } } : {}) });
  if (selection.platform === 'win32-x64' && object(parsed.windowsHelper).path !== 'native/windows-notify.exe') fail('invalid Windows helper path');
  if (selection.platform !== 'win32-x64' && 'windowsHelper' in parsed) fail('unexpected Windows helper');
  const files = new Map<string, Buffer>();
  const foldedPaths = new Set<string>();
  let totalBytes = 0;
  for (const item of parsed.files) {
    const entry = object(item);
    keys(entry, ['path', 'bytes', 'sha256']);
    const path = checkedPath(entry.path);
    if (path === 'release-manifest.json' || files.has(path) || typeof entry.bytes !== 'number' || !Number.isSafeInteger(entry.bytes) || entry.bytes < 0 ||
        typeof entry.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(entry.sha256)) fail('invalid or duplicate manifest file');
    if (foldedPaths.has(path.toLowerCase())) fail('case-insensitive manifest path collision');
    foldedPaths.add(path.toLowerCase());
    totalBytes += entry.bytes;
    if (entry.bytes > MAX_FILE_BYTES || totalBytes > 256 * 1024 * 1024) fail('release payload exceeds size limit');
    if (path !== 'package.json' && path !== 'native/windows-notify.exe' && !path.startsWith('dist/') && !TEMPLATE_FILES.some(file => path === `templates/${file}`)) fail(`unowned release content: ${path}`);
    files.set(path, checkedRelativeFile(root, path));
    if (files.get(path)!.length !== entry.bytes || hash(files.get(path)!) !== entry.sha256) fail(`changed file hash: ${path}`);
  }
  sameInventory(tree(root), [...files.keys(), 'release-manifest.json'], 'release payload');
  const ownedDirectories = new Set<string>();
  for (const path of files.keys()) {
    let parent = posix.dirname(path);
    while (parent !== '.') { ownedDirectories.add(parent); parent = posix.dirname(parent); }
  }
  sameInventory(treeDirectories(root), [...ownedDirectories], 'release directories');
  const listedPaths = [...files.keys()];
  const sortedPaths = [...listedPaths].sort();
  if (listedPaths.some((path, index) => path !== sortedPaths[index])) fail('manifest files are not sorted');
  const required = ['package.json', 'dist/cli.js', 'dist/learning.js', ...WEB_FILES.map(path => `dist/web/${path}`), ...TEMPLATE_FILES.map(path => `templates/${path}`)];
  if (required.some(path => !files.has(path))) fail('incomplete release payload');
  if (!files.get('package.json')!.equals(releasePackageJson(selection.version))) fail('invalid runtime package metadata');
  if (selection.platform === 'win32-x64' && !files.has('native/windows-notify.exe')) fail('missing Windows helper');
  if (selection.platform !== 'win32-x64' && files.has('native/windows-notify.exe')) fail('unexpected Windows helper');
  return parsed as unknown as ReleaseManifest;
}

/** Package a selected release into a new directory, or verify an exact already-written repeat. */
export function packageRelease(value: unknown, sourceRoot: string, destination: string): { manifest: ReleaseManifest; manifestSha256: string } {
  const selection = validateReleaseSelection(value);
  if (!isAbsolute(destination) || resolve(destination) !== destination || basename(destination) === 'release-manifest.json') fail('absolute destination required');
  assertCanonicalDirectory(dirname(destination));
  const sourcePath = realpathSync(sourceRoot).toLowerCase();
  const destinationPath = join(realpathSync(dirname(destination)), basename(destination)).toLowerCase();
  if (destinationPath === sourcePath || destinationPath.startsWith(`${sourcePath}${sep}`)) fail('destination must be outside source tree');
  const files = sourceFiles(sourceRoot);
  files.set('package.json', releasePackageJson(selection.version));
  if (selection.platform === 'win32-x64') files.set('native/windows-notify.exe', checkedFile(selection.windowsHelper!.path));
  const manifest = expectedManifest(selection, files);
  const manifestBytes = Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`);
  const manifestSha256 = hash(manifestBytes);
  if (existsSync(destination)) {
    validateReleaseBundle(destination, manifestSha256);
    return { manifest, manifestSha256 };
  }
  mkdirSync(destination);
  for (const [path, bytes] of files) {
    mkdirSync(dirname(join(destination, path)), { recursive: true });
    writeFileSync(join(destination, path), bytes, { flag: 'wx', mode: path === 'native/windows-notify.exe' ? 0o755 : 0o644 });
  }
  writeFileSync(join(destination, 'release-manifest.json'), manifestBytes, { flag: 'wx', mode: 0o644 });
  validateReleaseBundle(destination, manifestSha256);
  return { manifest, manifestSha256 };
}
