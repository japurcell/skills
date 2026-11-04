# Organize maintained script tests by task domain

This living ExecPlan is `brain/plans/2026-11-04-scripts-test-organization/ExecPlan.md`. Apply `.agents/skills/exec-plans/SKILL.md` and the parent `execplan-implement` workflow. Repository root for every command below is `/Users/adam/dev/skills`, or its worker worktree equivalent. All proposed verification below is expected, not observed, unless explicitly labeled observed.

## Purpose / Big Picture

A maintainer starting with an installer, hook, scanner, or Guardian task can find the stable command, canonical implementation, narrow behavioral suite, and aggregate check from `scripts/README.md`. Maintained repository test programs and their private support live together under `scripts/tests/<domain>/`. Public commands retain their current paths and behavior. Existing assertions, test identities/counts, filter semantics, provider cases, fixture isolation, and failure semantics survive the move. The root aggregate runner remains `scripts/test-all.py` with an explicit registry, including four skill-owned commands in their existing skill bundles.

After organization, reassess scanner and Guardian locality using actual navigation and behavioral evidence. Implement further cohesion only for demonstrated remaining friction, with an explicit bounded task and validation first. No speculative interface, compatibility wrapper for an internal test, runtime architecture rewrite, or performance claim belongs to this migration. The approved ADR-0004 architectural constraint continues to require canonical sources in `hooks/`, generated provider-local runtime outputs, and installers that copy checked-in outputs; the historical ADR file is absent in this checkout, so the current user contract and active hook guidance govern.

## Progress

- [x] (2026-11-04) [milestone-1] P: Inspect current sources, exact move inventory and consumers; create this plan before implementation.
- [x] (2026-11-04) [milestone-1] B-prep: Coordinator verifies committed plan, clean source base, tools, runner test, saved registry and frozen running baseline; authorizes isolated S work.
- [x] (2026-11-04) [milestone-1] B-full: Record the initial aggregate, targeted retries, and integrated lifecycle fixture repair proof.
- [x] (2026-11-04) [milestone-1] B-fix: Merge the lifecycle fixture repair commit `e701bc95a281f2d92ef5c10d19145226ec778a90` and verify all 32 lifecycle tests.
- [x] (2026-11-04) [milestone-2] S: Isolated implementation and required focused checks passed in dependency commit `552a749c829f7959a91c98c0cac140cae09b1ba3` (verified by parent).
- [ ] [milestone-2] S: Coordinator promotes the verified dependency commit into integration only after B-full succeeds.
- [ ] [milestone-2] A: Lane 1 relocates scanner and Guardian tests/support, runs direct behavioral suites, commits and merges.
- [ ] [milestone-2] C: Lane 2 relocates remaining tests/support, runs direct behavioral suites, commits and merges.
- [ ] [milestone-2] I: Serialized worker integrates registry, CI, active docs and task index; commits and merges.
- [ ] [milestone-2] Integrated parity, aggregate, freshness and cold navigation proof recorded.
- [ ] [milestone-3] D: Bounded scanner/Guardian cohesion assessment and conditional implementation accepted.
- [ ] [milestone-4] R: Biaxis review and fix loop, at most three cycles, passes or unresolved findings recorded.
- [ ] [milestone-4] F: Final checks, metadata commit, worker cleanup and reflection completed.

## Surprises & Discoveries

- Observed 2026-11-04: AST inventory of `scripts/test-all.py` contains 59 commands, of which 55 are scripts-owned and four are skill-owned. There are 58 root test-prefixed files excluding `test-all.py`; this includes private `test-common.sh`, native-only `test-rtk-stable-windows.ps1`, and capture helper `test-scan-secrets-capture.py`. Thus 59 test-prefixed filenames is not 59 suites or the full move count.
- Observed: `test_test_all.py::test_list_covers_maintained_suites_without_running_them` combines root globbing with explicit Python paths. Its expectation must migrate while retaining an independent completeness contract, subprocess fixtures, cancellation descendants, and absence of recursion. It must not become an assertion merely copied from SUITES.
- Observed: scanner provider shell suites invoke capture with a provider argument. `test-install-repo-gates.py` dynamically imports the LFS suite. These are real behavioral dependencies, not just documentation links.
- Observed: public `benchmark-high-rate-hooks.py` and `verify-hook-release.py` import `tool_guard_corpus.py` and `hook_benchmark_support.py`; corpus imports `hook_test_support.py`. Keep these root evidence modules and `scripts/fixtures/` in place. They are shared with public evidence commands, not exclusively private tests.
- Observed 2026-11-04: The unchanged-source aggregate completed with 51 passed and 8 failed in 1603.8 seconds. Seven failed suites passed focused retries under elevated process/socket/sysctl access after providing pinned Git LFS where required. `test-scan-secrets-lifecycle.py` still fails because its installer fixture omits manifest-owned brain-install assets.
- Observed 2026-11-04: `test-scan-secrets-lfs.py` and `test-install-repo-gates.py` require Git LFS 3.8.0. The official Darwin ARM64 release archive SHA-256 is `caff76a7d070d8160c89bc39b6e85d98f24135b6fed038a3b4de2590d25102d8`; the verified binary is `/private/tmp/skills-test-organization-tools/git-lfs-3.8.0/git-lfs`. Focused retries select it through `TEST_GIT_LFS`. Default sandbox execution denies `/bin/ps`, loopback binds and `sysctl kern.clockrate`, so those validation retries require elevated execution.
- Observed: test callbacks cross domain ownership. `test-codex-hooks-tool-guard.sh` calls C-owned `test-security-banners.py`, while that test imports A-owned `tool_guard_test_support.py`. The banner suite tests generated Guardian behavior, so keep its move in the Guardian domain despite its path; Task I updates the callback to `scripts/tests/guardian/test-security-banners.py`, then final integration runs both suites together.

## Decision Log

- 2026-11-04: Use established `brain/plans/` location, linked by its curated index. Preserve machine-owned `brain/index.md` generation.
- 2026-11-04: Choose six task domains: scanner, guardian, hooks, installers, tooling, runner. Shared shell fixture primitives belong in `scripts/tests/support/`; domain-only support stays beside its suites. These groups match current callers and the tasks described above.
- 2026-11-04: Move shared shell support first and update callers in the same worker commit so both later lanes can run focused suites from their own worktrees. Serialize registry/external-reference integration after both lanes merge; this task is worker-owned, not substantive coordinator source editing.
- 2026-11-04: Keep benchmark corpus/support and fixture roots stable. The deletion test shows that removing them spreads scenarios and provider translation into callers. Runtime deepening has not yet been justified.
- 2026-11-04: Split baseline preparation from complete evidence. A committed plan, clean source base, verified tools/runner, saved registry and frozen running baseline permit isolated S implementation/tests; full baseline success still gates its merge and milestone 1 acceptance. Integration sources stay unchanged during baseline execution so evidence cannot mix revisions.
- 2026-11-04: Verified S commit may be consumed as a pending dependency in isolated A/C branches while the frozen baseline continues. Worktrees still start from current integration; merge S into each worker branch before coding. B-full gates every implementation promotion into integration, S is promoted first, and workers merge latest integration into their branches before completion/promotion. This overlaps isolated implementation without changing baseline evidence or acceptance.
- 2026-11-04: Root-script brain guidance is an authoring convention, not a prohibition on this authorized internal-test move. Update it to distinguish stable executable commands from private test organization.

## Outcomes & Retrospective

Planning and milestone 1 are complete. The unchanged-source aggregate finished with 51 passed and 8 failed. Elevated targeted retries passed suites 29, 30, 31, 32, 35, 37 and 47 after providing required process/socket/sysctl access and Git LFS 3.8.0. The lifecycle fixture defect was repaired in commit `e701bc95a281f2d92ef5c10d19145226ec778a90`, merged as `3f76c21b`, and verified by 32 passing tests against integrated source. S remains pending at commit `552a749c829f7959a91c98c0cac140cae09b1ba3`; it is now eligible for promotion. A/C continue in isolated branches and must merge latest integration before promotion. Acceptance remains pending for migration and behavioral checks.

## Context and Orientation

Integration branch is `codex/scripts-test-organization`, starting at `7a13b79ad22235f2bce4534658476bbc34302867`. The persistent coordinator owns that integration checkout and plan/progress/evidence metadata. At most two implementation workers run concurrently. Each creates a separate worktree based on the current integration branch, edits only assigned scope, runs its checks, and commits. Before reporting done, a worker merges the latest integration branch into its own branch and resolves any conflicts there. The coordinator alone merges worker branches into integration, serially. Workers do not edit the active plan or reset others' changes.

`hooks/manifest.py` owns generated targets. `scripts/generate-hooks.py --check` checks freshness without source mutation. `scripts/test-all.py --list` lists maintained command tuples without running suites; the runner has no focused selector. Tests generally calculate root with `Path(__file__).resolve().parent.parent`, Bash sibling `source`, or PowerShell `$PSScriptRoot` ancestry. At the new domain path the repository root is `Path(__file__).resolve().parents[3]`; shared shell support similarly ascends three levels from its containing directory. Do not substitute current working directory or Git root discovery, because disposable copies and execution from another working directory are intentional test behavior.

Python suites requiring root script modules should insert the repository `scripts/` directory before imports, preserving existing isolated package registration. Domain peers retain local bare imports. Cross-domain callers use explicit test paths or narrowly add the needed support directory; do not create a new public harness interface. Test fixtures that deliberately copy installer runtime files to `scripts/` must keep those deployed paths. Generated helper closure/fingerprint expectations must not be rewritten indiscriminately.

## Exact Move Inventory

Every following line names one existing source and its exact destination. Move content and executable mode; edit only the path dependencies required for the new location. All other root files remain in place, including public CLIs, benchmarks, `common.sh`, `file_io.py`, corpus/evidence modules and fixtures.

- `scripts/test-codex-hooks-secrets-scanner.sh` -> `scripts/tests/scanner/test-codex-hooks-secrets-scanner.sh`
- `scripts/test-gemini-hooks-secrets-scanner.sh` -> `scripts/tests/scanner/test-gemini-hooks-secrets-scanner.sh`
- `scripts/test-hooks-secrets-scanner.sh` -> `scripts/tests/scanner/test-hooks-secrets-scanner.sh`
- `scripts/test-scan-secrets-capture.py` -> `scripts/tests/scanner/test-scan-secrets-capture.py`
- `scripts/test-scan-secrets-cli.py` -> `scripts/tests/scanner/test-scan-secrets-cli.py`
- `scripts/test-scan-secrets-git-gates.py` -> `scripts/tests/scanner/test-scan-secrets-git-gates.py`
- `scripts/test-scan-secrets-lfs.py` -> `scripts/tests/scanner/test-scan-secrets-lfs.py`
- `scripts/test-scan-secrets-status.py` -> `scripts/tests/scanner/test-scan-secrets-status.py`
- `scripts/test-scan-secrets-lifecycle.py` -> `scripts/tests/scanner/test-scan-secrets-lifecycle.py`
- `scripts/test-scan-status-cancellation.py` -> `scripts/tests/scanner/test-scan-status-cancellation.py`
- `scripts/test-install-scan-secrets.py` -> `scripts/tests/scanner/test-install-scan-secrets.py`
- `scripts/test-install-repo-gates.py` -> `scripts/tests/scanner/test-install-repo-gates.py`
- `scripts/test-scan-secrets-merge.py` -> `scripts/tests/scanner/test-scan-secrets-merge.py`
- `scripts/test-scan-secrets-stream-component.py` -> `scripts/tests/scanner/test-scan-secrets-stream-component.py`
- `scripts/test-scan-secrets-streaming.py` -> `scripts/tests/scanner/test-scan-secrets-streaming.py`
- `scripts/test-scan-secrets-windows.ps1` -> `scripts/tests/scanner/test-scan-secrets-windows.ps1`
- `scripts/scanner_test_support.py` -> `scripts/tests/scanner/scanner_test_support.py`
- `scripts/scanner-test-support.sh` -> `scripts/tests/scanner/scanner-test-support.sh`
- `scripts/test-codex-hooks-tool-guard.sh` -> `scripts/tests/guardian/test-codex-hooks-tool-guard.sh`
- `scripts/test-gemini-hooks-tool-guard.sh` -> `scripts/tests/guardian/test-gemini-hooks-tool-guard.sh`
- `scripts/test-hooks-tool-guard.sh` -> `scripts/tests/guardian/test-hooks-tool-guard.sh`
- `scripts/test-tool-guard-false-positives.py` -> `scripts/tests/guardian/test-tool-guard-false-positives.py`
- `scripts/test-tool-guard-file-operations.py` -> `scripts/tests/guardian/test-tool-guard-file-operations.py`
- `scripts/test-tool-guard-limits.py` -> `scripts/tests/guardian/test-tool-guard-limits.py`
- `scripts/test-tool-guard-native-data.py` -> `scripts/tests/guardian/test-tool-guard-native-data.py`
- `scripts/test-tool-guard-shell-data.py` -> `scripts/tests/guardian/test-tool-guard-shell-data.py`
- `scripts/test-hook-input-bounds.py` -> `scripts/tests/guardian/test-hook-input-bounds.py`
- `scripts/tool_guard_test_support.py` -> `scripts/tests/guardian/tool_guard_test_support.py`
- `scripts/test-codex-hooks-startup.sh` -> `scripts/tests/hooks/test-codex-hooks-startup.sh`
- `scripts/test-gemini-hooks-startup.sh` -> `scripts/tests/hooks/test-gemini-hooks-startup.sh`
- `scripts/test-hooks-startup.sh` -> `scripts/tests/hooks/test-hooks-startup.sh`
- `scripts/test-gemini-hooks-observability.sh` -> `scripts/tests/hooks/test-gemini-hooks-observability.sh`
- `scripts/test-hooks-observability.sh` -> `scripts/tests/hooks/test-hooks-observability.sh`
- `scripts/test-gemini-hooks-rtk.sh` -> `scripts/tests/hooks/test-gemini-hooks-rtk.sh`
- `scripts/test-hooks-rtk.sh` -> `scripts/tests/hooks/test-hooks-rtk.sh`
- `scripts/test-codex-hooks-windows.ps1` -> `scripts/tests/hooks/test-codex-hooks-windows.ps1`
- `scripts/test-lifecycle-messages-windows.ps1` -> `scripts/tests/hooks/test-lifecycle-messages-windows.ps1`
- `scripts/test-generate-hooks.py` -> `scripts/tests/hooks/test-generate-hooks.py`
- `scripts/test-brain-hooks.py` -> `scripts/tests/hooks/test-brain-hooks.py`
- `scripts/test-probe-provider-hook-delivery.py` -> `scripts/tests/hooks/test-probe-provider-hook-delivery.py`
- `scripts/test-security-banners.py` -> `scripts/tests/guardian/test-security-banners.py`
- `scripts/test-security-reporting.py` -> `scripts/tests/hooks/test-security-reporting.py`
- `scripts/test-hook-diagnostics.py` -> `scripts/tests/hooks/test-hook-diagnostics.py`
- `scripts/test-hook-diagnostic-recovery.py` -> `scripts/tests/hooks/test-hook-diagnostic-recovery.py`
- `scripts/test-benchmark-high-rate-hooks.py` -> `scripts/tests/hooks/test-benchmark-high-rate-hooks.py`
- `scripts/test-verify-hook-release.py` -> `scripts/tests/hooks/test-verify-hook-release.py`
- `scripts/test-verify-security-fixture-patch.py` -> `scripts/tests/hooks/test-verify-security-fixture-patch.py`
- `scripts/observability-test-support.sh` -> `scripts/tests/hooks/observability-test-support.sh`
- `scripts/observability-test-python.sh` -> `scripts/tests/hooks/observability-test-python.sh`
- `scripts/rtk-test-support.sh` -> `scripts/tests/hooks/rtk-test-support.sh`
- `scripts/test-addy-install.sh` -> `scripts/tests/installers/test-addy-install.sh`
- `scripts/test-codex-agents.py` -> `scripts/tests/installers/test-codex-agents.py`
- `scripts/test-install-codex-hooks.py` -> `scripts/tests/installers/test-install-codex-hooks.py`
- `scripts/test-install.sh` -> `scripts/tests/installers/test-install.sh`
- `scripts/test-install.ps1` -> `scripts/tests/installers/test-install.ps1`
- `scripts/test-rtk-stable.py` -> `scripts/tests/installers/test-rtk-stable.py`
- `scripts/test-rtk-stable-windows.ps1` -> `scripts/tests/installers/test-rtk-stable-windows.ps1`
- `scripts/test-cleanup-skill-workspaces.sh` -> `scripts/tests/tooling/test-cleanup-skill-workspaces.sh`
- `scripts/test-repo-root.sh` -> `scripts/tests/tooling/test-repo-root.sh`
- `scripts/test_copy_from_git.py` -> `scripts/tests/tooling/test_copy_from_git.py`
- `scripts/test_helpers.py` -> `scripts/tests/tooling/test_helpers.py`
- `scripts/test_workspace_config.py` -> `scripts/tests/tooling/test_workspace_config.py`
- `scripts/test_test_all.py` -> `scripts/tests/runner/test_test_all.py`
- `scripts/test-common.sh` -> `scripts/tests/support/test-common.sh`
- `scripts/security-test-support.sh` -> `scripts/tests/support/security-test-support.sh`

## Path Consumers and Ownership

Task S owns `scripts/test-common.sh`, `scripts/security-test-support.sh` and their current shell source references in every script suite. `test-common.sh` must compute the same physical checkout root; `mock_bin` must retain `printf "%b\n"`. Its tests still exercise root and fallback behavior. S does not move other tests.

Task A owns all scanner/guardian inventory entries and their imports, root constants, shell source directives, provider capture invocations, explicit LFS import in `test-install-repo-gates.py`, fake-git environment paths, and source-free/copy fixtures. Private `scanner_test_support.py` adds root scripts for shared `hook_test_support` import after relocation; `tool_guard_test_support.py` resolves root corpus similarly. Preserve `scripts/scan-secrets.py`, `scan_install_windows.py`, installed bundle member names and `.local/lib/scan-secrets/scripts/scan-secrets.py`. Shell scanner suites source `../support/security-test-support.sh` and `../support/test-common.sh`; scanner-specific support is sibling. Guardian shell suites source the same shared support.

Task C owns hooks/installers/tooling/runner inventory entries, their imports/root constants, fixture source copies and dynamic script references. Hooks observability suites point to sibling `observability-test-python.sh` and `observability-test-support.sh`; RTK suites point to sibling `rtk-test-support.sh`. All moved shell suites source `../support/test-common.sh`. Existing installer fixture references to production `scripts/install.sh`, `scripts/install.ps1`, helper modules, vendor assets, generated hook roots and manifests stay intact. C updates runner test root calculation but leaves its registry expectation path integration to I if aggregate registry is still old; direct non-registry test cases can be run before I. C records this intentional integration dependency rather than claiming full runner suite success early.

Task I owns `scripts/test-all.py::SUITES`, `scripts/tests/runner/test_test_all.py` completeness expectations, `.github/workflows/hooks-posix.yml` (direct commands and embedded importlib path), `.github/workflows/ready-ideas-windows.yml` (all six native commands), `.github/workflows/brain-hooks.yml` (path trigger and command), root `README.md`, new `scripts/README.md`, `skills/default/brain-install/README.md`, and active `brain/codebase/` references in agents-installation, brain-hooks, hook-observability, hook-testing, installer-testing, live-hook-testing, powershell-installers, script-testing, scripts-and-installers, secret-scanner, secret-scanner-recovery, security-hooks, security-testing, skill-evaluation and testing. Search other tracked active consumers before completion. Leave archived plans and evaluation workspace transcripts as historical evidence. The active plan itself intentionally contains old-to-new source mappings.

## Plan of Work and Task Graph

### Milestone 1: Freeze contract and baseline
Status: done
Acceptance: met

P is complete with source inventory evidence above. B-prep has prerequisite P and is coordinator-owned. The plan gate was committed at `66996eefb1b099fd7da1a63f63822d21c5b1e6f1`; the integration source baseline is `7a13b79ad22235f2bce4534658476bbc34302867`. Tools are present: Python 3.14.6, Bash 3.2.57, PowerShell 7.6.9, Git, jq, flock, and sqlite3. `rtk proxy python3 scripts/test-all.py --list` and `--help` both exited 0; the 59-command list is saved at `/private/tmp/scripts-test-organization-registry-before.txt` and help at `/private/tmp/scripts-test-organization-help.txt`. `rtk proxy python3 scripts/test_test_all.py` passed 14 tests. `rtk proxy python3 scripts/generate-hooks.py --check` exited 0 with `Generated hooks are current (62 files).` The full aggregate completed on the unchanged source baseline with 51 passed and 8 failed in 1603.8 seconds. Seven affected suites passed targeted retries: `test-verify-security-fixture-patch.py` (30 tests), `test-scan-secrets-cli.py` (36), `test-scan-secrets-git-gates.py` (63), `test-scan-secrets-lfs.py` (44), `test-scan-status-cancellation.py` (5), `test-install-repo-gates.py` (62), and `test-verify-hook-release.py` (37). The LFS checks used the verified binary `/private/tmp/skills-test-organization-tools/git-lfs-3.8.0/git-lfs` via `TEST_GIT_LFS`; archive checksum is recorded above. The remaining failure, `test-scan-secrets-lifecycle.py`, still fails 7 of 32 tests because the disposable installer source omits a generated target's manifest-owned parent path. No aggregate log file exists; commands and results are retained in the task transcript.

B-full is accepted from the completed initial aggregate, targeted environmental retries, and integrated B-fix proof. The initial aggregate reported 51 passed / 8 failed. Elevated focused retries then passed suites 29, 30, 31, 32, 35, 37 and 47. B-fix commit `e701bc95a281f2d92ef5c10d19145226ec778a90` repaired the lifecycle test fixture; after its integration merge `3f76c21b`, the full lifecycle suite passed all 32 tests under elevated execution with verified Git LFS 3.8.0. The integration source baseline remains `7a13b79ad22235f2bce4534658476bbc34302867` apart from this scoped fixture correction. Missing native Windows execution is an evidence limit, not a reason to skip available PowerShell suites. Preserve the failed initial aggregate evidence; no assertions were weakened or tests skipped.

#### Task B-fix: Repair the baseline lifecycle fixture

Prerequisites: B-prep and the initial aggregate failure in suite 34. Lane 1 changed only `scripts/test-scan-secrets-lifecycle.py::installed_assets` in commit `e701bc95a281f2d92ef5c10d19145226ec778a90`. The disposable source now includes the full manifest-owned `skills/default/brain-install` package needed for generator freshness preflight, while retaining existing fault, upgrade, source-free, and cleanup assertions. Lane 1's public command proof passed 32 tests in 48.280 seconds; after coordinator integration merge `3f76c21b`, the same elevated command with verified `TEST_GIT_LFS` passed 32 tests in 47.426 seconds. This task is complete; A merges latest integration so the repair carries through its test move.

### Milestone 2: Migrate tests and make task navigation usable
Status: open
Acceptance: not met

S (lane 2) implementation and focused verification require B-prep; its promotion into integration additionally requires B-full success. Use its own worktree to relocate shared support and update all existing shell callers atomically. Verify `rtk proxy bash scripts/test-repo-root.sh`, `rtk proxy bash scripts/test-hooks-tool-guard.sh`, and `rtk proxy bash scripts/test-install.sh`; expect exits 0 and original assertions. Record S implementation/test evidence while the unchanged integration baseline runs. S is implemented and verified at `552a749c829f7959a91c98c0cac140cae09b1ba3`, pending promotion. A/C may start now from current integration and merge that exact dependency into their isolated branches. Wait for B-full success before promoting S into integration, then A/C promotion follows the latest-integration merge gate below.

A (lane 1) implementation requires B-prep and the verified S dependency commit. Create its worktree from the current integration tip, then merge `552a749c829f7959a91c98c0cac140cae09b1ba3` into its own branch. B-fix must merge into integration first; before reporting complete, merge latest integration into A's branch so the lifecycle fixture repair carries through its move, resolve conflicts, and rerun affected checks. Promotion requires B-full success and S/B-fix already promoted. Scope is scanner and Guardian inventory only. Run every maintained registry command whose old path is in its ownership, substituted with the mapped path, sequentially; also run `rtk proxy python3 scripts/tests/scanner/test-scan-secrets-capture.py copilot`, then gemini and codex, unless those same runs have already been observed through provider shell suites. Preserve capture invocation through all providers, limits/incomplete results, descendant cleanup, fake findings, LFS failures, merge and lifecycle semantics. Native Windows suite remains available via `rtk proxy pwsh -NoProfile -File scripts/tests/scanner/test-scan-secrets-windows.ps1`; native-only cases require Windows CI evidence. Record direct checks and merge, without editing the registry.

C (lane 2) implementation requires B-prep and the verified S dependency commit; it may run alongside A. Create its worktree from current integration, then merge `552a749c829f7959a91c98c0cac140cae09b1ba3` into its own branch. Promotion requires B-full success and S/B-fix already promoted; merge latest integration into its branch and rerun affected checks before reporting complete/coordinator promotion. Scope is remaining map except shared support already moved; C owns the security banner suite in `scripts/tests/guardian/` because it verifies Guardian behavior. Run every maintained registry command in its ownership with mapped paths, sequentially; runner registry case may remain pending I as explained above. Explicitly run `rtk proxy python3 -W error scripts/tests/tooling/test_helpers.py`, `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py`, and `rtk proxy python3 scripts/generate-hooks.py --check`. Keep existing parser, resource cleanup, package-isolation and installer preflight cases. Check native-only RTK test source parsing and retain native command for CI. Merge before reporting C done.

I (reuse one worker lane, serialized) requires A and C. Create a fresh worker worktree based on their merged integration commit. Update exactly the registry and external consumers above; keep suite command order and count 59, public runner behavior, four skill commands and no aggregate recursion. Adapt the independent completeness assertion to domain directories and the original exclusion rules; do not discover tests at runtime. Add the task-oriented scripts index, linking install/refresh, change hook behavior, scanner/gates, Guardian/evidence, harness, and maintenance routes. Each route names public command, canonical owner, focused test command, generated-output rule, private support and related brain guidance. Document Git LFS 3.8.0 prerequisite setup for suites that exercise real LFS transfers, including the `TEST_GIT_LFS` override. Resolve the cross-domain callback by updating Codex Guardian's banner command to `scripts/tests/guardian/test-security-banners.py`; retain its import of Guardian-owned `tool_guard_test_support.py`. Include native Windows limitations and human-only import/pull prohibition. Run `rtk proxy python3 scripts/tests/runner/test_test_all.py` and `rtk proxy python3 scripts/test-all.py --list`, expect all original runner cases and 59 commands. After both domains are integrated, explicitly run the banner and Codex Guardian suites together. Commit and merge I.

The coordinator then records integrated proof: full aggregate, freshness, stale active-reference search and cold navigation exercise. Domain task passes or clean merges alone do not accept this milestone.

### Milestone 3: Decide whether scanner/Guardian still need cohesion
Status: open
Acceptance: not met

D requires accepted milestone 2. Reuse one worker lane for a bounded assessment. Trace one scanner lifecycle/capture change and one Guardian policy/evidence change from the new README to canonical source, provider adapters, fixture owner and validation. Record exact files, remaining forced cross-tree edits and an actual failing behavior or repeated caller knowledge if present. Apply deletion test: a new module must hide real complexity and reduce caller knowledge, not forward calls or mirror names.

Default outcome is a documented no-change decision if organization resolves navigation friction and no behavioral defect is demonstrated. That is full acceptance for this conditional requirement. If a concrete remaining defect justifies implementation, first reproduce through public CLI/provider entrypoint, update this plan with exact source ownership, invariant, negative cases and focused acceptance, and dispatch one bounded worker task E (prerequisite D) from integrated state. No speculative interface or runtime/source separation changes. For canonical hook edits regenerate with `rtk proxy python3 scripts/generate-hooks.py --write`, then check freshness and all affected public provider suites. D/E stop after the demonstrated issue and proof; unrelated redesign is outside scope.

### Milestone 4: Review, finalize and clean up
Status: open
Acceptance: not met

R requires D and E if E exists. Run `code-review-biaxis` against fixed base `7a13b79ad22235f2bce4534658476bbc34302867`; compare Standards against active repository guidance and Spec against this approved purpose/invariants. Reuse the two worker slots for review as required by that skill, keeping the coordinator persistent. Fix actionable findings in a worker-owned worktree, merge, rerun affected checks, and repeat review up to three cycles. Unresolved findings after three cycles must be reported and prevent claiming clean acceptance. Do not weaken tests or silently ignore baseline flakiness.

F requires review acceptance. On frozen integrated source, rerun only checks justified by fixes; record final `rtk git diff --check`, generator freshness and aggregate result if source changed since the prior full run. Coordinator reconciles all plan status/evidence, runs reflect skill, persists only durable knowledge, commits metadata and integration changes through the repository commit workflow, confirms no worker commits remain unmerged, and removes only task-owned clean worktrees/branches after their commits are reachable. As the coordinator final metadata/reflection task, move the completed plan and retained evidence into `brain/archive/plans/2026-11-04-scripts-test-organization/`, verify the completed file and evidence links exist, update `brain/archive/plans/index.md` and `brain/plans/index.md`, and remove only the now-empty active plan directory. Preserve the user-requested completed plan, and link its retained archive path in the final answer. Hooks reconcile the root brain index.

## Concrete Steps

Next: promote verified S into integration. A/C then merge latest integration into their own branches, resolve any conflicts, rerun affected checks, and return commits for serialized coordinator promotion. Run worker commands from their own checkout root, never another worker's files. Coordinator serializes all merges and owns active plan metadata. I's worker performs substantive registry/docs/CI edits after A+C; coordinator can maintain progress and commit metadata throughout.

Before dispatch each worker reads current AGENTS guidance and activates required implementation skills, including tdd when editing source. Each records task input integration SHA, exact commands, exits, failures/skips, resulting commit and merge SHA. Timeouts are failures/evidence limits until diagnosed; use process group cleanup and preserve logs.

## Validation and Acceptance

The baseline acceptance combines the initial aggregate, targeted environmental retries, and integrated B-fix proof; the initial aggregate finished `Suites: 51 passed, 8 failed`, seven affected suites passed focused retries, and the lifecycle fixture repair passed all 32 tests. Do not rerun passing suites solely to obtain one aggregate exit 0. Worker-local merging of verified dependency commits does not change the frozen integration source baseline. Baseline and final parity compare maintained command identities after normalizing only source-to-destination path mapping. Expect 59 registry commands in identical order and four unchanged skill commands; preserve existing test IDs/assertions and platform skip reasons. Do not add layout-only tests. Existing runner completeness tests remain the meaningful interface check and independent of runtime registry discovery. Final integrated proof explicitly runs the relocated banner and Codex Guardian suites together because their test callbacks cross domain boundaries.

Final root commands: `rtk proxy python3 scripts/test-all.py --list`, `rtk proxy python3 scripts/tests/runner/test_test_all.py`, `rtk proxy python3 -W error scripts/tests/tooling/test_helpers.py`, `rtk proxy python3 scripts/generate-hooks.py --check`, `rtk proxy python3 scripts/test-all.py`, and `rtk git diff --check`. Expected exits 0. The aggregate reports `Suites: 59 passed, 0 failed` when all available-host suites pass; visible native skips remain a limitation and are not native Windows success. Missing tools produce exit 2 and must be recorded and resolved where possible. Do not run frozen timing probes concurrently with this validation or claim performance improvements from it.

Check active references with `rtk rg -n 'scripts/(test[-_]|scanner_test_support|scanner-test-support|security-test-support|observability-test-support|observability-test-python|rtk-test-support)' README.md .github/workflows brain/codebase skills/default/brain-install/README.md scripts --glob '!tests/**' --glob '!vendor/**'`. Inspect each result; root `scripts/test-all.py` and historical/fixture literal contracts are legitimate, stale invocation/import paths are not. Validate Markdown targets touched by I, YAML command paths, executable modes and fixture copy paths directly.

Cold-agent exercise: give an otherwise uninformed reviewer only `scripts/README.md` and three tasks: find installer preflight behavior and its focused tests; find canonical Gemini startup owner and generation/freshness checks; find scanner capture/lifecycle and Guardian policy/evidence support without editing generated outputs. Require returned exact paths/commands and correct distinction among canonical source, generated provider output, private test support, public CLIs and native validation. Record the reviewer response and any wrong turns; revise index for observed ambiguity and repeat just the failed scenario. No source changes are required solely to satisfy a navigation questionnaire.

## Idempotence and Recovery

Reads, list/help, freshness checks and focused suites use disposable fixture roots and can be repeated. Preserve failure transcripts. Moves are not replayed blindly: check both mapped paths and current Git status first, then resume only missing operations. Never delete an untracked or dirty worktree. A failed frozen baseline blocks all implementation promotion into integration; preserve the isolated worktree, diagnose unchanged integration sources, add a scoped fix task and record successful complete baseline evidence before promoting S, followed by A/C after each incorporates latest integration. A worker conflict stops its merge, not independent authorized tasks; inspect both sides and preserve behavior, then rerun focused checks. If rollback is necessary, coordinator reverts the offending task commit with Git history preserved and updates dependent task states; do not hard-reset integration or overwrite another worker. If runtime behavior changes unexpectedly, keep the stable public command paths, stop promotion of dependent work, diagnose with the existing public test reproducer and restore parity before final acceptance.

## Interfaces and Dependencies

No new callable interface is planned. Public script paths, flags, stdout/stderr, exit semantics, installed scanner closure, generated hook ownership, explicit aggregate registry and skill-owned commands remain stable. Python 3, Bash, Git, jq, flock, sqlite3 and PowerShell 7+ are required for the aggregate. Native Windows runtime claims depend on Windows CI. Private modules may use direct root-script imports, but public commands must not start depending on a test-only directory. Keep fixtures/vendor and shared public evidence corpus at their existing root paths.

## Artifacts and Notes

Source inspection on 2026-11-04 verified every move-map source exists and all 58 non-aggregate test-prefixed root files are covered. Prior review pointers are `/tmp/scripts-navigation-20261104T172901Z.md` and `/tmp/scripts-dependencies-2026-11-04-0142.md`; their architecture observations informed this plan, but their suggested root-only constraint was superseded by explicit user approval. They do not prove current test success. Baseline and task transcripts will be linked here by the coordinator as actual evidence arrives.
