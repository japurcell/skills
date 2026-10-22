import { createHash } from 'node:crypto';
import { closeSync, existsSync, lstatSync, mkdirSync, openSync, readFileSync, readSync, readdirSync, realpathSync, writeFileSync } from 'node:fs';
import { basename, dirname, isAbsolute, join, posix, resolve, sep } from 'node:path';
import { isDeepStrictEqual } from 'node:util';

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
  readonly schema: 2;
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
// Schema 2 approves these complete lock bytes, including every npm platform,
// executable, engine and package integrity field. A lock change needs a new schema.
const QUALIFIED_TOOLCHAIN_LOCK_SHA256 = 'bea7cfb5a835aba203893966dde3e964418b12c69f8680e53a65b3603b9467d6';
const WEB_FILES = ['app.js', 'index.html', 'style.css'] as const;
const TEMPLATE_FILES = [
  'agents.json', 'package.json', 'prompts/audit.md', 'prompts/implementation.md', 'prompts/planning.md',
  'prompts/recipe.md', 'prompts/review.md', 'workflows/audit.ts', 'workflows/change.ts',
  'workflows/evaluate.ts', 'workflows/learn.ts',
] as const;
const TOOLCHAIN_FILES = ['package.json', 'package-lock.json'] as const;
// Schema 2 names every compiled module, including maps and declarations. Changing
// this list is a release-contract change, not an inference from a proposed bundle.
const RUNTIME_MODULES = [
  'accounting', 'adapters/codex', 'adapters/copilot', 'adapters/fake', 'adapters/types',
  'agents', 'build', 'capture', 'clearance', 'cli', 'dashboard', 'execution-control', 'installation-bindings',
  'learning', 'lifecycle', 'native/notification-transport', 'native/notifications',
  'native/process', 'notifications', 'placement', 'profiles', 'redaction', 'release', 'schema', 'store',
  'workflow', 'workspace',
] as const;
const COMPILED_FILES = RUNTIME_MODULES.flatMap(stem => [`${stem}.js`, `${stem}.js.map`, `${stem}.d.ts`]);
const BUILD_RECEIPT = 'node_modules/.factory-build-receipt.json';

function fail(message: string): never { throw new Error(`release package: ${message}`); }
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('invalid object');
  return value as Record<string, unknown>;
}
function keys(value: Record<string, unknown>, required: readonly string[], optional: readonly string[] = []) {
  if (required.some(key => !Object.hasOwn(value, key)) || Object.keys(value).some(key => !required.includes(key) && !optional.includes(key))) fail('unknown or missing descriptor field');
}
function hash(bytes: Buffer) { return createHash('sha256').update(bytes).digest('hex'); }
function hashLargeFile(path: string): string {
  const digest = createHash('sha256');
  const bytes = Buffer.allocUnsafe(1024 * 1024);
  const descriptor = openSync(path, 'r');
  try {
    for (let length = readSync(descriptor, bytes, 0, bytes.length, null); length; length = readSync(descriptor, bytes, 0, bytes.length, null)) {
      digest.update(bytes.subarray(0, length));
    }
  } finally { closeSync(descriptor); }
  return digest.digest('hex');
}
const MAX_FILE_BYTES = 32 * 1024 * 1024;
function checkedPath(value: unknown): string {
  if (typeof value !== 'string' || !value || value.includes('\\') || /[\x00-\x1f<>:"|?*]/.test(value) || posix.isAbsolute(value) ||
      value.split('/').some(part => !part || part === '.' || part === '..' || part.toLowerCase() === 'node_modules' || /[. ]$/.test(part) ||
        /^(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)/i.test(part)) || posix.normalize(value) !== value) fail('unsafe manifest path');
  return value;
}
function checkedFile(path: string): Buffer {
  const info = lstatSync(path);
  if (info.isSymbolicLink()) fail(`symlink refused: ${path}`);
  if (!info.isFile()) fail(`non-regular file refused: ${path}`);
  if (info.size > MAX_FILE_BYTES) fail(`file exceeds release size limit: ${path}`);
  return readFileSync(path);
}
function checkedRelativeFile(root: string, relative: string, buildInput = false): Buffer {
  let parent = root;
  checkedPath(buildInput ? relative.replace(/^node_modules\//, 'toolchain/') : relative);
  const parts = relative.split('/');
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
  sameInventory(tree(join(sourceRoot, 'src')), RUNTIME_MODULES.map(stem => `${stem}.ts`), 'source modules');
  sameInventory(tree(join(sourceRoot, 'web')), WEB_FILES, 'web source');
  sameInventory(tree(join(sourceRoot, 'templates')), TEMPLATE_FILES, 'templates');
  sameInventory(tree(join(sourceRoot, 'toolchain')), TOOLCHAIN_FILES, 'toolchain');
  sameInventory(tree(join(sourceRoot, 'dist')), [...COMPILED_FILES, ...WEB_FILES.map(path => `web/${path}`)], 'built runtime');
  const result = new Map<string, Buffer>();
  for (const path of COMPILED_FILES) result.set(`dist/${path}`, checkedFile(join(sourceRoot, 'dist', path)));
  for (const path of WEB_FILES) {
    const built = checkedFile(join(sourceRoot, 'dist/web', path));
    if (!built.equals(checkedFile(join(sourceRoot, 'web', path)))) fail(`stale built web: ${path}`);
    result.set(`dist/web/${path}`, built);
  }
  for (const path of TEMPLATE_FILES) result.set(`templates/${path}`, checkedFile(join(sourceRoot, 'templates', path)));
  for (const path of TOOLCHAIN_FILES) result.set(`toolchain/${path}`, checkedFile(join(sourceRoot, 'toolchain', path)));
  validateInstallTemplates(result);
  return result;
}

const TYPESCRIPT_OPTIONAL_PLATFORMS = [
  'aix-ppc64', 'darwin-arm64', 'darwin-x64', 'freebsd-arm64', 'freebsd-x64',
  'linux-arm', 'linux-arm64', 'linux-loong64', 'linux-mips64el', 'linux-ppc64',
  'linux-riscv64', 'linux-s390x', 'linux-x64', 'netbsd-arm64', 'netbsd-x64',
  'openbsd-arm64', 'openbsd-x64', 'sunos-x64', 'win32-arm64', 'win32-x64',
] as const;
const TYPESCRIPT_OPTIONAL_PACKAGES = TYPESCRIPT_OPTIONAL_PLATFORMS.map(platform => `@typescript/typescript-${platform}`);
const TOOLCHAIN_DEPENDENCIES = { '@types/node': '24.19.2', typescript: '7.0.2' };

function sameFields(value: Record<string, unknown>, expected: Record<string, unknown>, context: string): void {
  if (!isDeepStrictEqual(value, expected)) fail(`invalid ${context}`);
}

function validateInstallTemplates(files: ReadonlyMap<string, Buffer>): void {
  if (hash(files.get('toolchain/package-lock.json')!) !== QUALIFIED_TOOLCHAIN_LOCK_SHA256) fail('unapproved factory toolchain lock');
  const authoring = object(JSON.parse(files.get('templates/package.json')!.toString('utf8')));
  sameFields(authoring, { name: '@local/software-factory-authoring', version: '0.0.0', private: true, type: 'module' }, 'authoring package');
  const toolchain = object(JSON.parse(files.get('toolchain/package.json')!.toString('utf8')));
  sameFields(toolchain, { name: '@local/software-factory-toolchain', version: '0.0.0', private: true, type: 'module', dependencies: TOOLCHAIN_DEPENDENCIES }, 'factory toolchain package');
  const lock = object(JSON.parse(files.get('toolchain/package-lock.json')!.toString('utf8')));
  keys(lock, ['name', 'version', 'lockfileVersion', 'requires', 'packages']);
  if (lock.name !== toolchain.name || lock.version !== toolchain.version || lock.lockfileVersion !== 3 || lock.requires !== true) fail('invalid factory toolchain lock');
  const packages = object(lock.packages);
  sameInventory(Object.keys(packages), ['', 'node_modules/@types/node', 'node_modules/typescript', 'node_modules/undici-types',
    ...TYPESCRIPT_OPTIONAL_PACKAGES.map(name => `node_modules/${name}`)], 'factory toolchain lock');
  sameFields(object(packages['']), { name: toolchain.name, version: toolchain.version, dependencies: TOOLCHAIN_DEPENDENCIES }, 'factory toolchain lock root');
  const types = object(packages['node_modules/@types/node']);
  const compiler = object(packages['node_modules/typescript']);
  const undici = object(packages['node_modules/undici-types']);
  if (types.version !== '24.19.2' || compiler.version !== '7.0.2' || undici.version !== '7.24.6') fail('unpinned factory toolchain dependency');
  sameFields(object(types.dependencies), { 'undici-types': '>=7.24.0 <7.24.7' }, 'Node types dependency closure');
  sameFields(object(compiler.optionalDependencies), Object.fromEntries(TYPESCRIPT_OPTIONAL_PACKAGES.map(name => [name, '7.0.2'])), 'TypeScript optional dependency closure');
  for (const [path, value] of Object.entries(packages)) {
    if (!path) continue;
    const entry = object(value);
    const name = path.slice('node_modules/'.length);
    const version = entry.version;
    const expectedUrl = `https://registry.npmjs.org/${name}/-/${name.split('/').at(-1)}-${version}.tgz`;
    if (entry.resolved !== expectedUrl || typeof entry.integrity !== 'string' || !/^sha512-[A-Za-z0-9+/]+={0,2}$/.test(entry.integrity) ||
        ('dev' in entry && entry.dev !== false) || (TYPESCRIPT_OPTIONAL_PACKAGES.includes(name) && (version !== '7.0.2' || entry.optional !== true))) fail(`invalid factory toolchain lock entry: ${path}`);
  }
}

function fileEntries(root: string, paths: readonly string[]): ReleaseFile[] {
  return paths.map(path => {
    const bytes = checkedRelativeFile(root, path, true);
    return { path, bytes: bytes.length, sha256: hash(bytes) };
  }).sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
}

function buildInputPaths(root: string): string[] {
  const platformCompiler = `node_modules/@typescript/typescript-${process.platform}-${process.arch}`;
  const groups = ['src', 'web', 'templates', 'node_modules/typescript', platformCompiler, 'node_modules/@types/node', 'node_modules/undici-types'];
  return [
    'package.json', 'package-lock.json', 'tsconfig.json', 'scripts/build.mjs', 'scripts/package-release.mjs',
    ...TOOLCHAIN_FILES.map(path => `toolchain/${path}`),
    ...groups.flatMap(group => tree(join(root, group)).map(path => `${group}/${path}`)),
  ];
}

/** Exact source, build configuration, installed compiler and type inputs seen by a build. */
export function buildInputSnapshot(root: string): string {
  assertCanonicalDirectory(root);
  return JSON.stringify({ schema: 1, node: process.version, nodeSha256: hashLargeFile(process.execPath), platform: process.platform, arch: process.arch,
    inputs: fileEntries(root, buildInputPaths(root)) });
}

function outputEntries(files: Map<string, Buffer>): ReleaseFile[] {
  return [...files].filter(([path]) => path.startsWith('dist/'))
    .map(([path, bytes]) => ({ path, bytes: bytes.length, sha256: hash(bytes) }))
    .sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
}

/** Write only after the compiler succeeds and its input snapshot still matches. */
export function recordBuildReceipt(root: string, before: string): void {
  const after = buildInputSnapshot(root);
  if (before !== after) fail('source or toolchain changed during build');
  const outputs = outputEntries(sourceFiles(root));
  if (before !== buildInputSnapshot(root)) fail('source or toolchain changed during build');
  writeFileSync(join(root, BUILD_RECEIPT), `${JSON.stringify({ ...JSON.parse(before), outputs }, null, 2)}\n`, { flag: 'wx' });
}

function validateBuildReceipt(root: string, inputs: string, files: Map<string, Buffer>): void {
  const receipt = object(JSON.parse(checkedRelativeFile(root, BUILD_RECEIPT, true).toString('utf8')));
  const expected = { ...JSON.parse(inputs), outputs: outputEntries(files) };
  if (JSON.stringify(receipt) !== JSON.stringify(expected)) fail('stale or invalid build receipt');
}

function releasePackageJson(version: string): Buffer {
  return Buffer.from(`${JSON.stringify({ name: '@local/software-factory-runtime', version, private: true, type: 'module' }, null, 2)}\n`);
}
function expectedManifest(selection: ReleaseSelection, files: Map<string, Buffer>): ReleaseManifest {
  const entries: ReleaseFile[] = [...files].map(([path, bytes]) => ({ path, bytes: bytes.length, sha256: hash(bytes) })).sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  return {
    schema: 2, version: selection.version, platform: selection.platform, node: NODE_ASSETS[selection.platform],
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
  if (parsed.schema !== 2 || !Array.isArray(parsed.files) || parsed.files.length > 4096) fail('unsupported release manifest');
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
    if (path !== 'package.json' && path !== 'native/windows-notify.exe' && !path.startsWith('dist/') &&
        !TEMPLATE_FILES.some(file => path === `templates/${file}`) && !TOOLCHAIN_FILES.some(file => path === `toolchain/${file}`)) fail(`unowned release content: ${path}`);
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
  const required = ['package.json', ...COMPILED_FILES.map(path => `dist/${path}`), ...WEB_FILES.map(path => `dist/web/${path}`), ...TEMPLATE_FILES.map(path => `templates/${path}`),
    ...TOOLCHAIN_FILES.map(path => `toolchain/${path}`),
    ...(selection.platform === 'win32-x64' ? ['native/windows-notify.exe'] : [])];
  sameInventory([...files.keys()], required, 'incomplete release payload');
  validateInstallTemplates(files);
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
  const inputs = buildInputSnapshot(sourceRoot);
  const files = sourceFiles(sourceRoot);
  validateBuildReceipt(sourceRoot, inputs, files);
  if (inputs !== buildInputSnapshot(sourceRoot)) fail('source or toolchain changed during packaging');
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
