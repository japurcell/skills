import { inspectInstalledState } from './installed-state.js';

/** Read-only admission facts. This grants no claim, mutation, execution or repair authority. */
export async function inspectInstalledDependencyState(common: string, repository?: string) {
  const installed = await inspectInstalledState(common, repository, { purpose: 'dependency-repair' });
  const toolchain = installed.layout.toolchainInspection;
  if (!toolchain) throw new Error('installed dependency ownership unavailable');
  return { common, active: installed.active, receipt: installed.receipt, receiptSha256: installed.receiptSha256,
    release: installed.release, nodePath: installed.nodePath, toolchain };
}

export type InstalledDependencyState = Awaited<ReturnType<typeof inspectInstalledDependencyState>>;
