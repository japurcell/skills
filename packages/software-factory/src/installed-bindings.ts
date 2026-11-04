import { inspectInstalledState } from './installed-state.js';
import { realpathSync } from 'node:fs';
import { dirname, join, sep } from 'node:path';
import { createCodexAdapter } from './adapters/codex.js';
import { createCopilotAdapter } from './adapters/copilot.js';
import type { AgentAdapter } from './adapters/types.js';
import { validateBoundProviderSources, type VerifiedInstallSelection } from './installation-bindings.js';
import { sendDesktopNotification } from './native/notifications.js';
import type { NotificationSender } from './notifications.js';

type Providers = VerifiedInstallSelection['providers'];
export interface InstalledBindings {
  readonly common: string;
  readonly adapters: Record<string, AgentAdapter>;
  readonly notificationSender: NotificationSender;
}
function fail(): never { throw new Error('installed binding refused'); }
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

/** Strict startup and upgrade ownership never select damage inspection. */
export async function inspectInstalledOwnership(common: string, repository?: string, retained = false) {
  return inspectInstalledState(common, repository, { purpose: 'strict', retained });
}

export async function loadInstalledBindings(modulePath: string, repository?: string, commonArg?: string): Promise<InstalledBindings | null> {
  const common = installedCommonForCli(modulePath);
  if (common === null) return null;
  try {
    if (realpathSync(modulePath) !== modulePath || (commonArg !== undefined && commonArg !== common)) fail();
    const installed = await inspectInstalledOwnership(common, repository);
    if (process.execPath !== installed.nodePath) fail();
    const adapters = createSelectedAdapters(installed.layout.receipt.providers, join(common, 'factory'));
    return { common, adapters, notificationSender: sendDesktopNotification };
  } catch { fail(); }
}
