# Software factory handoff

Updated 2026-11-03. Continue `brain/plans/software-factory/ExecPlan.md`; the current plan controls requirements and status. Historical records are evidence only.

## Authorization and boundaries

- User authorization covers implementation, commits, pushes and qualification Actions. No release publication, global install, real user-repository installation/adoption, destructive workspace test, or learning adoption.
- All final source/security reviews remain deferred until implementation tasks finish. Keep Gemini/OpenCode/Pi provider qualification blocked: no auth or credential inspection, provider calls or changes. Codex/Copilot paid-call budgets are spent. Live desktop notifications run last.
- T16a is accepted only to its schema7/incomplete/claimed boundary. Never mark broad maintenance, ready upgrade, dependency repair, uninstall or cleanup complete from this result. Windows ownership/process lifetime stays fail-closed.
- Shell `login:false`, prefix commands with RTK. `rtk gain` telemetry DB initialization failed once, but `rtk 1.1.0` and other RTK commands work. Never weaken assertions or bounds.

## Accepted T16a checkpoint

- Base: `/Users/adam/.codex/worktrees/ea58/skills`, branch `codex/research-agentic-workflow-prototypes`, source checkpoint `4d75045b9153b5710171e45298bf5c2923e7da22`.
- Worker source commit `3dae7fc5` merged through `9345ead6` into base. `maintenance.ts` and `forward-schema.test.mjs` are blob-identical to worker source. Git rename detection carried the fixed Python inventory to `skills/default/software-factory/scripts/install.py`, adding `schema-forward` and `forward-backup-entry`.
- Full deterministic/browser composed proof on stable base passes530/530, zero failures, zero skips, Node duration209.064s (`/tmp/factory-t16a-base-composed.log`). No overlapping base writes/builds occurred.
- Focused evidence: pinned typecheck/build pass; forward-schema public selection12/12 (8.871s); base store33/33 (2.137s); release55/55 (12.290s), all zero skips. Logs: `/tmp/factory-t16a-base-typecheck.log`, `/tmp/factory-t16a-base-build.log`, `/tmp/factory-t16a-base-focused.log`, `/tmp/factory-t16a-base-store.log`, `/tmp/factory-t16a-base-release.log`.
- Public API ready for T16b: `prepareForwardSchema`, `prepareMaintenanceHandoff`, `consumeMaintenanceHandoff`, `advanceForwardSchema`, `inspectForwardSchema`, and `resumeForwardSchema`. T16a ends v7/incomplete/claimed; no installed file publication or ready transition.
- T16b preparation packet: `research/t16b-upgrade-publication-task-2026-11-03.md`. Root is assigning `/root/upgrade_publication` to the retained installer checkout after I create branch `codex/factory-upgrade-publication` from the accepted base checkpoint. Recheck source signatures before editing. If a genuine owned installation baseline cannot be established, installed-upgrade acceptance stays blocked.

## T17 Windows route diagnostics

- Read-only evidence analysis: `research/windows-route-native-diagnosis-2026-11-03.md`. Run `39886478568` reported aggregate extra descendants and console-class events, but those counts do not establish process association, role or predicate cascade. Previous sanitized artifacts could not be fetched; no native rerun occurred.
- Root reports a clean qualification-only worker branch `codex/factory-etw-route-diagnostics` in `/Users/adam/.codex/worktrees/factory-windows-etw-route/skills`, commit `21c57d664d70225aeea5a960b13f1b684fc6f120`. Portable tests20/20, zero skips (`/tmp/factory-etw-route-diagnostics-tests.log`); no native run. Author stopped and ownership transferred. After T16b checkout prep, integration owner must merge this branch into base using merge workflow, verify source identity and all existing guards/privacy/productAdmission=false, and rerun20 portable plus artifact-guard tests. Root owns native job coordination and has authorized the existing seven-case workflow run. Upload only its two sanitized artifacts; raw ETL is removed.
- No diagnostic projection may contain PIDs, keys, timestamps, paths, argv, hashes, output or free text. Preserve unknown/identity ambiguity; no guard weakening, console-client inference, arbitrary signaling, helper admission or product support claim.

## Immediate next actions

1. Commit the updated T16a acceptance evidence and handoff.
2. In the clean retained `/Users/adam/.codex/worktrees/factory-install-candidate/skills`, switch from the fully integrated clean `codex/factory-forward-store` branch to a new `codex/factory-upgrade-publication` based on the accepted checkpoint. Only then delete the verified clean, fully integrated forward-store branch. Keep the worktree for explicit reuse and send the clean branch/status to root so T16b can start. Assign no source work yourself.
3. After T16b checkout prep, integrate the Windows diagnostics worker branch into base, verify owned-file identity and portable/artifact checks, then let root coordinate the authorized exact-head seven-case Windows observation. Keep base source edits serialized with the ongoing T16b private worker.

## Toolchain and recovery

- Pinned Node: `/tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node` (Node24.22.1, SQLite3.53.4). Archive SHA256 `654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628`.
- Python3.13.14: `/Users/adam/.pyenv/versions/3.13.14/bin/python3.13`; do not substitute Python3.14.6.
- Private release npm cache: `/tmp/factory-forward-schema-npm-cache`. Shared seed `/tmp/software-factory-npm-cache` was not modified.
- Private Playwright1.64.1 browser cache: `/tmp/factory-forward-schema-playwright-browsers` (Chromium/headless-shell1248, Chrome156.0.8078.4, FFmpeg1013).
- Preserve complete run logs under `/tmp`. On a failure, capture the exact assertion and stop dependent integration; never reset user work or weaken tests.
