# Dependency ownership inspection foundation

This is a read-only package seam, not a dependency repair command. It produces no claim, backup, candidate, completion or publication. Public dependency selection, preparation, two-move publication/recovery, authored dependencies and general installation repair remain separate tasks.

`inspectInstalledDependencyState(common, repository?)` in `src/dependency-state.ts` uses the same typed installed ownership interpretation as startup. It returns the active install/upgrade completion and receipt, plus a selected toolchain inspection with authenticated `expected.rows`, independently measured `observed` inventory/digest, and sorted `missing` and `changed` file paths. It never executes a compiler or npm. `common` is the canonical Git common directory, not the repository working directory.

Only missing or byte-mismatched known regular toolchain files are reportable. Missing directories or the whole root, changed root identity or modes, extra entries, symlinks, hardlinks, special files, unchanged-runtime/Node damage and retained-original damage refuse. All receipts, publication positions and selected providers retain their existing verification. Expected inventory remains distinct from observed damage; the latter cannot select replacement versions. Unknown future maintenance completion kinds refuse instead of falling back to an older install/upgrade event. No dependency completion producer exists yet.

`inspectInstalledOwnership` and upgrade-original capture always use strict inspection. The narrow existing layout-reader inspection mode is explicitly typed and defaults to strict. The dependency-state entry alone selects damage inspection. New runtime modules are explicitly listed in both the TypeScript release inventory and Python bootstrap inventory; schema 2 is unchanged.

## Verification

From `packages/software-factory`, with Node 24.22.1 on PATH, run:

```sh
rtk proxy node --test test/dependency-state.test.mjs test/installed-bindings.test.mjs test/install-publication.test.mjs test/upgrade-retained-providers.test.mjs
rtk proxy node --test qualification/dependency-state-native.qualification.mjs
```

The native command requires `FACTORY_TEST_NODE_ARCHIVE`, `FACTORY_TEST_NPM_CACHE_SEED` and `FACTORY_TEST_PYTHON`. Use the manifest-pinned archive for Darwin arm64 or Linux x64, a task-private offline cache seed containing the exact toolchain lock, and the already qualified Python 3.13.14 interpreter. Set `FACTORY_ATOMIC_PYTHON` to that same interpreter. Missing prerequisites are failures, with no skip or interpreter/network fallback. Native process-owner checks require permission to query the test's own identities. No account, provider, credential, desktop, global installation or real repository is used.

The genuine disposable public-install fixture removes the owned compiler before inspecting, verifies ordinary installed CLI refusal and strict upgrade-original refusal, checks history remains byte-identical during inspection, and restores fixture-owned bytes. Controls cover a changed compiler that must never execute, missing lock, foreign entry, changed mode, symlink, hardlink, socket, missing directory/root, changed root identity, simultaneous runtime damage and an unsupported future dependency completion. A genuine public upgrade then proves selected damage is reportable only in the current toolchain while the retained old tree stays strict; no agent attempt or native session is created.

Freeze the entire private checkout from the pinned build through the end of each native/release proof. This fixture packages a second bundle after its first installed controls. Editing between those phases invalidates the source-bound build receipt even when initial installation passed. Rebuild after edits and rerun the whole affected proof. Native fixture-only restoration is not product restore behavior.

The coordinator owns public test registration and native CI wiring. This file does not claim Linux native acceptance from a Darwin run, or dependency mutation support from read-only inspection.
