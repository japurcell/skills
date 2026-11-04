# Organize maintained script tests by task domain

This completed ExecPlan is `brain/archive/plans/2026-11-04-scripts-test-organization/ExecPlan.md`. It records the approved work, observed proof, and final disposition. The repository root for recorded commands was `/Users/adam/dev/skills`; results below are observed unless explicitly labeled historical.

## Purpose / Big Picture

A maintainer starting with an installer, hook, scanner, or Guardian task can find the stable command, canonical implementation, narrow behavioral suite, and aggregate check from `scripts/README.md`. Maintained repository test programs and their private support live together under `scripts/tests/<domain>/`. Public commands retain their current paths and behavior. Existing assertions, test identities/counts, filter semantics, provider cases, fixture isolation, and failure semantics survive the move. The root aggregate runner remains `scripts/test-all.py` with an explicit registry, including four skill-owned commands in their existing skill bundles.

After organization, reassess scanner and Guardian locality using actual navigation and behavioral evidence. Implement further cohesion only for demonstrated remaining friction, with an explicit bounded task and validation first. No speculative interface, compatibility wrapper for an internal test, runtime architecture rewrite, or performance claim belongs to this migration. The approved ADR-0004 architectural constraint continues to require canonical sources in `hooks/`, generated provider-local runtime outputs, and installers that copy checked-in outputs; the historical ADR file is absent in this checkout, so the current user contract and active hook guidance govern.

## Progress

- [x] (2026-11-04) [milestone-1] P/B-prep/B-full/B-fix: contract, source inventory, baseline retries, and lifecycle fixture repair completed.
- [x] (2026-11-04) [milestone-2] S/A/C/I: 65 test/support files organized into six domains plus shared support; public command paths preserved.
- [x] (2026-11-04) [milestone-2] Integrated proof: 59-command registry parity, direct cross-domain banner/Guardian proof, generator freshness, cold navigation, and final aggregate passed.
- [x] (2026-11-04) [milestone-3] D: scanner/Guardian cohesion review found no evidence for further consolidation.
- [x] (2026-11-04) [milestone-4] R: Standards and Spec reviews completed with zero actionable findings.
- [x] (2026-11-04) [milestone-4] F: final checks, reflection, archive, and five clean task worktrees, five worker branches, and 99 exact task backup refs removed after reachability checks.

## Surprises & Discoveries

- Observed 2026-11-04: AST inventory of `scripts/test-all.py` contains 59 commands, of which 55 are scripts-owned and four are skill-owned. There are 58 root test-prefixed files excluding `test-all.py`; this includes private `test-common.sh`, native-only `test-rtk-stable-windows.ps1`, and capture helper `test-scan-secrets-capture.py`. Thus 59 test-prefixed filenames is not 59 suites or the full move count.
- Observed: `test_test_all.py::test_list_covers_maintained_suites_without_running_them` combines root globbing with explicit Python paths. Its expectation must migrate while retaining an independent completeness contract, subprocess fixtures, cancellation descendants, and absence of recursion. It must not become an assertion merely copied from SUITES.
- Observed: scanner provider shell suites invoke capture with a provider argument. `test-install-repo-gates.py` dynamically imports the LFS suite. These are real behavioral dependencies, not just documentation links.
- Observed: public `benchmark-high-rate-hooks.py` and `verify-hook-release.py` import `tool_guard_corpus.py` and `hook_benchmark_support.py`; corpus imports `hook_test_support.py`. Keep these root evidence modules and `scripts/fixtures/` in place. They are shared with public evidence commands, not exclusively private tests.
- Observed 2026-11-04: The unchanged-source aggregate completed with 51 passed and 8 failed in 1603.8 seconds. Seven failed suites passed focused retries under elevated process/socket/sysctl access after providing pinned Git LFS where required. `test-scan-secrets-lifecycle.py` still fails because its installer fixture omits manifest-owned brain-install assets.
- Observed 2026-11-04: `test-scan-secrets-lfs.py` and `test-install-repo-gates.py` require Git LFS 3.8.0. The official Darwin ARM64 release archive SHA-256 is `caff76a7d070d8160c89bc39b6e85d98f24135b6fed038a3b4de2590d25102d8`; the verified binary is `/private/tmp/skills-test-organization-tools/git-lfs-3.8.0/git-lfs`. Focused retries select it through `TEST_GIT_LFS`. Default sandbox execution denies `/bin/ps`, loopback binds and `sysctl kern.clockrate`, so those validation retries require elevated execution.
- Observed: test callbacks cross domain ownership. `test-codex-hooks-tool-guard.sh` calls `scripts/tests/guardian/test-security-banners.py`, which imports `tool_guard_test_support.py`; combined proof passed both suites with 16 tests each.
- Observed: Gemini SessionStart context injection is provider-authored in `.gemini/hooks/scripts/skill-context-injector.py`; it is not a manifest-generated target. The generator owns its imported `hooks/families/common.py` and `audit.py` helpers, and `--check` does not validate injector content. README navigation distinguishes these owners, and the direct Gemini startup suite passed.
- Observed: final integrated aggregate passed all 59 suites in 1,782.7 seconds with exit 0. Native Windows-only cases reported host-specific skips on macOS. Full evidence log: `/private/tmp/skills-test-organization-tools/final-aggregate.log`.

## Decision Log

- 2026-11-04: Use established `brain/plans/` location, linked by its curated index. Preserve machine-owned `brain/index.md` generation.
- 2026-11-04: Choose six task domains: scanner, guardian, hooks, installers, tooling, runner. Shared shell fixture primitives belong in `scripts/tests/support/`; domain-only support stays beside its suites. These groups match current callers and the tasks described above.
- 2026-11-04: Move shared shell support first and update callers in the same worker commit so both later lanes can run focused suites from their own worktrees. Serialize registry/external-reference integration after both lanes merge; this task is worker-owned, not substantive coordinator source editing.
- 2026-11-04: Keep benchmark corpus/support and fixture roots stable. The deletion test shows that removing them spreads scenarios and provider translation into callers. Runtime deepening has not yet been justified.
- 2026-11-04: Split baseline preparation from complete evidence. A committed plan, clean source base, verified tools/runner, saved registry and frozen running baseline permit isolated S implementation/tests; full baseline success still gates its merge and milestone 1 acceptance. Integration sources stay unchanged during baseline execution so evidence cannot mix revisions.
- 2026-11-04: Verified S commit may be consumed as a pending dependency in isolated A/C branches while the frozen baseline continues. Worktrees still start from current integration; merge S into each worker branch before coding. B-full gates every implementation promotion into integration, S is promoted first, and workers merge latest integration into their branches before completion/promotion. This overlaps isolated implementation without changing baseline evidence or acceptance.
- 2026-11-04: Root-script brain guidance is an authoring convention, not a prohibition on this authorized internal-test move. Update it to distinguish stable executable commands from private test organization.
- 2026-11-04: The bounded scanner/Guardian reassessment found the new task map resolves navigation friction; retain shared public corpus/evidence helpers at root and make no speculative production consolidation.
- 2026-11-04: Treat the approved code tree `2131da3ada23eb2899f28808c472a50e1dcf5426` as the reviewed source. Local commit metadata was normalized without changing any tree or parent topology; the archived mapping records original-to-final object IDs.

## Outcomes & Retrospective

The approved reorganization is complete. Maintained test programs and private support now live under `scripts/tests/` by domain, while public commands and the explicit 59-command registry remain stable. The 59-suite aggregate passed with exit 0 in 1,782.7 seconds on the approved code tree. Focused runner, generator, banner, Guardian, security-reporting, lifecycle, and parity checks passed. Cold navigation passed all scenarios. The bounded cohesion review found no further consolidation justified, and biaxis review reported zero actionable Standards findings and zero material Spec findings. Native Windows execution remains a CI responsibility; local Windows-only cases correctly reported host-specific skips. No implementation work remains.

## Context and Orientation

Integration branch is `codex/scripts-test-organization`. The fixed review base is `7a13b79ad22235f2bce4534658476bbc34302867`; the reviewed source tree is `2131da3ada23eb2899f28808c472a50e1dcf5426`, at metadata-normalized commit `51758376e236a54c8ccbbeb2397d5220d044a29b`. The final documentation/archive commit follows that source snapshot. Original-to-final commit object mapping is retained in `metadata-rewrite-map.tsv` beside this plan. All five clean task worktrees and their five worker branches, plus 99 exact task-owned backup refs, were removed after reachability and mapping verification. The original-to-final mapping is retained alongside this plan.

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

The exact move inventory, source ownership, initial aggregate, targeted retries, and lifecycle fixture repair are recorded above.

### Milestone 2: Migrate tests and make task navigation usable
Status: done
Acceptance: met

S moved shared shell support first. A and C moved the remaining maintained suites and private helpers into six domain folders plus `scripts/tests/support/`; I updated the explicit registry, CI references, callbacks, and `scripts/README.md`. Public command paths and suite order stayed stable. The reviewed source tree contains 65 moves, with no executable-mode changes or removed unittest methods/assertion calls. Registry parity remained 59 ordered commands and four unchanged skill tuples. Runner tests passed 14 cases, generator freshness reported 62 current outputs, combined Guardian banner/Codex Guardian/security-reporting checks passed 16/16/14, cold navigation passed all scenarios, and the full aggregate passed 59/59.

### Milestone 3: Decide whether scanner/Guardian still need cohesion
Status: done
Acceptance: met

The bounded assessment traced scanner capture/lifecycle and Guardian policy/evidence routes. The task map resolved navigation friction; shared public corpus/evidence stayed with public commands. No concrete production defect or repeated caller burden justified more consolidation, so no source change was made.

### Milestone 4: Review, finalize and clean up
Status: done
Acceptance: met

Biaxis review against base `7a13b79ad22235f2bce4534658476bbc34302867` reported zero actionable Standards findings and zero material Spec findings on source tree `2131da3ada23eb2899f28808c472a50e1dcf5426`. Independent metadata verification passed on `51758376e236a54c8ccbbeb2397d5220d044a29b`. The aggregate passed 59 suites with exit 0. The plan and original-to-final mapping are archived here; five clean task worktrees, five worker branches, and 99 exact task backup refs were removed after reachability checks.

## Concrete Steps

No implementation, test, or review work remains. The implementation, bounded reassessment, integrated proof, biaxis review, archive, and cleanup are complete. Revalidation is not pending; the final report links this archive and states the macOS/native-Windows evidence limit.

## Validation and Acceptance

Observed on the frozen reviewed source tree `2131da3ada23eb2899f28808c472a50e1dcf5426` at `51758376e236a54c8ccbbeb2397d5220d044a29b`:

- `python3 scripts/test-all.py` completed with `Suites: 59 passed, 0 failed in 1782.7s.` Runner exit code was 0. Log: `/private/tmp/skills-test-organization-tools/final-aggregate.log`.
- `scripts/tests/runner/test_test_all.py` passed 14 tests; registry parity preserved 59 ordered commands and four skill-owned tuples.
- `scripts/generate-hooks.py --check` reported 62 current outputs.
- Combined Guardian banner, Codex Guardian, and security-reporting checks passed 16, 16, and 14 tests. The moved lifecycle suite passed 32 tests.
- `git diff --check` passed for the fixed-base source diff. Biaxis Standards and Spec reviews had zero actionable/material findings.

The aggregate used verified Git LFS 3.8.0 via `TEST_GIT_LFS` and an environment permitting required process, loopback socket, and sysctl checks. Windows-native cases emitted expected host-specific skips on macOS; Windows CI remains the native proof.

## Idempotence and Recovery

Reads, list/help, freshness checks and focused suites use disposable fixture roots and can be repeated. Preserve failure transcripts. Moves are not replayed blindly: check both mapped paths and current Git status first, then resume only missing operations. Never delete an untracked or dirty worktree. A failed frozen baseline blocks all implementation promotion into integration; preserve the isolated worktree, diagnose unchanged integration sources, add a scoped fix task and record successful complete baseline evidence before promoting S, followed by A/C after each incorporates latest integration. A worker conflict stops its merge, not independent authorized tasks; inspect both sides and preserve behavior, then rerun focused checks. If rollback is necessary, coordinator reverts the offending task commit with Git history preserved and updates dependent task states; do not hard-reset integration or overwrite another worker. If runtime behavior changes unexpectedly, keep the stable public command paths, stop promotion of dependent work, diagnose with the existing public test reproducer and restore parity before final acceptance.

## Interfaces and Dependencies

No new callable interface is planned. Public script paths, flags, stdout/stderr, exit semantics, installed scanner closure, generated hook ownership, explicit aggregate registry and skill-owned commands remain stable. Python 3, Bash, Git, jq, flock, sqlite3 and PowerShell 7+ are required for the aggregate. Native Windows runtime claims depend on Windows CI. Private modules may use direct root-script imports, but public commands must not start depending on a test-only directory. Keep fixtures/vendor and shared public evidence corpus at their existing root paths.

## Artifacts and Notes

- [Original-to-final commit mapping](metadata-rewrite-map.tsv) maps all 23 original task commits to final metadata-normalized commits while preserving their trees and graph topology.
- Final aggregate log: `/private/tmp/skills-test-organization-tools/final-aggregate.log`; outcome `59 passed, 0 failed`, exit 0.
- The initial baseline aggregate had 51 passes and 8 environment/fixture failures. Seven suites passed focused retries with required host permissions and Git LFS. The lifecycle fixture was repaired by copying the complete manifest-owned Brain Install package; all 32 lifecycle tests passed.
- The verified Git LFS Darwin ARM64 archive SHA-256 was `caff76a7d070d8160c89bc39b6e85d98f24135b6fed038a3b4de2590d25102d8`; temporary executable path was `/private/tmp/skills-test-organization-tools/git-lfs-3.8.0/git-lfs`.
- Prior navigation/dependency notes: `/tmp/scripts-navigation-20261104T172901Z.md` and `/tmp/scripts-dependencies-2026-11-04-0142.md`. They informed the plan but do not prove acceptance.
