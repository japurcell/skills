# Software factory handoff

Updated 2026-11-03. Continue `brain/plans/software-factory/ExecPlan.md`; the current plan controls requirements and status. Historical records are evidence only.

## Authorization and boundaries

- User authorization covers implementation, commits, pushes and qualification Actions. No release publication, global install, real user-repository install/adoption, destructive workspace test, or learning adoption.
- Final source/security reviews remain deferred until all implementation tasks finish. Keep Gemini/OpenCode/Pi provider qualification blocked: no auth or credential inspection, provider calls, or changes. Codex/Copilot call budgets are spent. Live desktop notifications run last.
- Preserve failing assertions and bounds. No broad maintenance completion from T16a. Windows ownership/process lifetime stays fail-closed.
- Shell `login:false`, prefix commands with RTK. `rtk gain` telemetry DB initialization failed once, but `rtk 1.1.0` and other RTK commands work.
- Do not overlap full composed proof with base writes, builds, installation or lifecycle tests.

## Base state and T16a

- Base: `/Users/adam/.codex/worktrees/ea58/skills`, branch `codex/research-agentic-workflow-prototypes`, current source merge `a046e1b4`.
- Worker commit `3dae7fc5` was merged into its branch as `9345ead6`, then merged into base. `maintenance.ts` and `forward-schema.test.mjs` are blob-identical to the worker. Git rename detection carried the fixed Python module inventory to `skills/default/software-factory/scripts/install.py`, adding only `schema-forward` and `forward-backup-entry`.
- T16a narrowly recognizes real v3, v4-base, v4-plus, v5, v6 and v7 shapes; it makes an owned backup, does staged one-step forward migration and stops at v7 with repository incomplete and the sole upgrade claim retained. It does not publish files or mark ready. T16a acceptance remains pending full composed base proof; T16b is the next dependent task only after that pass and a genuine owned installation baseline. Its preparation-only interface/journaling packet is `research/t16b-upgrade-publication-task-2026-11-03.md`; recheck current source before any authorized dispatch.
- Base pinned Node24.22.1/SQLite3.53.4 typecheck and build pass. Focused `test:maintenance -- --operation forward-schema` passes12/12, zero skips (8.871s); base `test:store` passes33/33 (2.137s); `test:release` passes55/55, zero skips (12.290s). Logs: `/tmp/factory-t16a-base-typecheck.log`, `/tmp/factory-t16a-base-build.log`, `/tmp/factory-t16a-base-focused.log`, `/tmp/factory-t16a-base-store.log`, `/tmp/factory-t16a-base-release.log`.
- The base release selector first failed four publication tests because sandboxed sysctl returned EPERM, plus one offline fixture because shared `/tmp/software-factory-npm-cache` lacked locked `undici-types@7.24.6`. Narrow escalation cleared process identity failures. The fixture now accepts `FACTORY_TEST_NPM_CACHE_SEED`, defaulting to the same shared cache; `/tmp/factory-forward-schema-npm-cache` was seeded from the checked-in toolchain lock in a disposable copy with `npm ci --ignore-scripts`. The shared cache was not modified. Full release is now green.
- Public maintenance selector showed red (`no tests match supplied filters`) before registering only `forward-schema`; after registration it passes12/12. Without an operation filter, broad maintenance must continue refusing while install, upgrade, dependencies, repair, uninstall and cleanup suites are missing.

## Windows route diagnostics

- Read-only diagnosis: `research/windows-route-native-diagnosis-2026-11-03.md`. It compared source and the supplied run `39886478568`; previous sanitized artifacts were unavailable, so reported counts do not establish a root-console cause and no native rerun occurred.
- New T17 task requires a bounded qualification-only closed projection reconstructed from private rows, with graph role/class/parent/phase/end and per-predicate subreason counts, no raw telemetry, no guard weakening or product admission; first portable controls, then same seven native cases. Root owns routing and private worker dispatch.
- Diagnosis memo and task are now in the plan graph. Historical handoff details are retained in [checkpoint history](handoff.history-2026-11-03-t16a.md).

## Next action and exact proof

1. Ensure package-pinned Chromium is available only in a new task-private `/tmp` browser directory. The previous `/tmp/software-factory-playwright-browsers` path is missing. Use installed Playwright1.64.1 and its existing package CLI; no browser version substitution or user-cache writes.
2. Run the complete deterministic/browser composed command against stable base `a046e1b4`, with no concurrent base writes:

   `rtk proxy env PATH=/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin:$PATH FACTORY_TEST_PYTHON=/Users/adam/.pyenv/versions/3.13.14/bin/python3.13 PLAYWRIGHT_BROWSERS_PATH=/tmp/factory-forward-schema-playwright-browsers /tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node --experimental-test-module-mocks --test --test-concurrency=2 packages/software-factory/test/*.test.mjs packages/software-factory/test/browser/*.test.mjs packages/software-factory/qualification/runtime.test.mjs packages/software-factory/qualification/ci.test.mjs`

3. Record exact case count, time, skips and log path in the ExecPlan. A pass accepts T16a only to its incomplete-store boundary. Then report the base proof to root so T16b can begin.

## Toolchain and recovery

- Verified runtime: `/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node`, official runtime-manifest archive SHA256 `654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628`; Node24.22.1, SQLite3.53.4. Default Node24.21.0 is not acceptance.
- Python3.13.14: `/Users/adam/.pyenv/versions/3.13.14/bin/python3.13`; do not substitute default Python3.14.6.
- Release test cache: `/tmp/factory-forward-schema-npm-cache`; shared seed remains `/tmp/software-factory-npm-cache` and must not be modified.
- If composed proof fails, retain the log and concrete failing assertion; do not weaken the test. Reconcile the plan/handoff before retrying. No base writes until the composed run exits.
