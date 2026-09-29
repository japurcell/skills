# Simplify and verify local agent hooks across providers

This ExecPlan is a living document. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current. Work from the repository root and follow .agents/skills/exec-plans/SKILL.md.

Planning revision: 2026-09-28. The prior implementation through c0d9ca34 remains checked in. Its completed tests prove the former design only. The user approved this revised ExecPlan and windows-live-check.md on 2026-09-28. Revised source implementation may proceed.

## Purpose / Big Picture

Local Copilot CLI, Gemini CLI, and Codex sessions should show useful security and lifecycle messages without noisy per-tool success messages. Explicit RTK commands should stop showing the false missing-hook warning using stable RTK 0.50.0 or newer. The obsolete repository-state and workspace-wide Markdown hooks should leave maintained source and fresh installations. Repository-local OKF lint should run when an agent tries to finish a turn. High-rate hooks should have measured, reviewed latency.

A user can verify the result by running an explicit RTK command, observing startup and turn-end hook messages, causing a safe Tool Guardian denial that names its exact rule, and viewing one bounded OKF audit record for a turn-end check. Native Windows automation, local provider display checks, and direct macOS hook benchmarks provide separate evidence. A hook observes only calls delivered by its provider; it cannot block arbitrary later writes by child processes. Copilot pre-tool timeouts are fail-open.

## Progress

- [x] (2026-09-28) [planning] Close the reopened Wayfinder decisions and revise this ExecPlan and windows-live-check.md before source work.
- [x] (2026-09-29 00:09Z) [approval] User explicitly approved the revised ExecPlan and Windows checklist before source changes.
- [x] (2026-09-29 01:01Z) [milestone-17] Require stable RTK and migrate warning suppression; retire verified owned prerelease assets. Source and disposable-home proof pass; native Windows real RTK proof remains in milestone 24.
- [x] (2026-09-29) [milestone-18] Integrated repository-state retirement at `6b8e0938`; generator, installer, and retained-hook checks pass on Mac. Native Windows proof remains in milestone 24.
- [x] (2026-09-29) [repair-provider-guidance] Restored approved Gemini and Copilot file-first PowerShell instructions; both existing installer suites pass. The PowerShell suite skips one unsupported junction fixture on this Mac.
- [x] (2026-09-29) [milestone-19] Integrated global Markdown Health retirement at `d54d5619`; source and disposable-home checks pass on Mac. Native Windows proof remains in milestone 24.
- [x] (2026-09-29) [repair-retired-registrations] Integrated Copilot/Gemini refresh preservation at `44daea14`; Bash and PowerShell installer suites and 12 stable RTK tests pass. Native Windows junction behavior remains open in milestone 24.
- [x] (2026-09-29) [milestone-20] Integrated repository-local turn-end OKF adapters and bounded audit at `07d1f133`; focused Mac checks pass. Native Windows proof remains in milestone 24 and installed display in milestones 25-27.
- [x] (2026-09-29) [milestone-21] Integrated sparse lifecycle envelopes and focused Windows automation at `828e4c75`; source checks pass. Native Windows execution and installed CLI display remain later gates.
- [x] (2026-09-29) [milestone-22] Integrated exact Tool Guardian reasons at `cb3f0093`; generator and provider suites pass on Mac. Native display remains in milestones 25-27.
- [x] (2026-09-29) [milestone-23] Inventory all retained high-rate registrations and benchmark direct macOS entrypoints in 45 synthetic scenarios; record method, timing distributions, and host-specific budgets in `docs/ready-ideas-execplan/high-rate-hooks-performance.md`.
- [x] (2026-09-29) [milestone-23] Replace scanner Git polling sleep with early-return process wait, regenerate three provider outputs, and rerun the exact 25-sample matrix. Focused scanner suites and 25 generator tests pass.
- [x] (2026-09-29) [milestone-23] Integrated tested performance audit and scanner wait change at `9dbb901d`; native CLI and Windows timing were not required.
- [x] (2026-09-29) [milestone-24/source] Rechecked 26 generated outputs, 25 parity cases, affected public hook suites, stable RTK, and Bash/PowerShell disposable-home installers on macOS; updated Windows RTK version and processor gates. This is source evidence only.
- [ ] [milestone-24] Pass integrated source, temporary-home installer, and native Windows automation, including the scanner HEAD-failure case.
- [x] (2026-09-29) [repair-24A] Integrated portable converter collision coverage at `3d89d501`; all 14 Mac converter tests and both installer suites pass. The retained real-file case awaits a case-sensitive filesystem.
- [ ] [milestone-25] Verify installed Codex CLI behavior.
- [ ] [milestone-26] Verify installed Copilot CLI behavior in a session with that CLI.
- [ ] [milestone-27] Verify installed Gemini CLI behavior in a session with that CLI.
- [ ] [final] Synchronize agent docs, remove obsolete references, and record final acceptance only after all required milestones pass.

Historical work: prior milestones 1-16 were accepted for the former design. They established read-only orientation, file-first PowerShell guidance, three-file disposable-probe guidance, provider hook transport, bounded scanner capture, security banners, the now-retired repository-state and Markdown hooks, prerelease RTK rewriting, integrated tests, provider live probes, and review repairs. This revision does not reopen those completed facts or count their old acceptance as proof of the new behavior. A later scanner regression added a native Windows committed-repository HEAD-failure case that remains unverified here. Six blocked repair-branch deletions are separate historical housekeeping for a reviewed user-run Git command, not a hook acceptance gate.

## Surprises & Discoveries

- Stable RTK 0.50.0 has a persistent hooks.suppress_hook_warning setting. The user has already upgraded this Mac's PATH RTK. The former pinned prerelease launcher is no longer needed for this warning.
- The old Markdown Health hook used its own workspace checker. scripts/lint-okf.py is separate and remains useful for canonical agent documentation.
- Gemini AfterModel observability may run once per streaming chunk, faster than per-tool hooks. The previous approximately 6-7 ms Gemini probe measured handler entry-to-completion, not process startup or full provider latency. The milestone 23 direct macOS subprocess measurement is about 27 ms median per synthetic chunk; provider delivery and chunk rate remain unmeasured.
- Before milestone 22, Tool Guardian reduced limit failures to input_limits/critical and discarded the specific bound. The rebased implementation retains safe rule metadata and measured limits; the allowlist still cannot bypass input limits.
- Another machine may still run old user-level repository-state or Markdown Health registrations after source retirement. Their installed files and state directories are left for manual cleanup. Fresh-install acceptance cannot prove every old installation is clean.
- Prior Copilot CLI timeout probing showed a harmless Git read proceed after a one-second pre-tool timeout without a native timeout message. Treat visible progress as informational, not proof of enforcement.
- Native Windows scan-secrets HEAD-failure proof remains open. A macOS PowerShell skip is not native Windows evidence.
- The milestone 24 source sweep exposed a separate `scripts/test-codex-agents.py` failure on this case-insensitive APFS volume: two case-fold-equivalent fixture filenames collapse into one file before the CLI sees them. Keep the case-sensitive end-to-end test and add portable collision coverage through a suitable internal seam under Repair 24A. No test may be skipped or weakened merely to pass locally.
- Native Windows automation requires a remote branch. The base branch is local and ahead of origin; `gh auth status` currently reports an invalid token for the configured account. Do not claim a Windows pass until credentials are restored, the final branch is published, and the job completes.
- Repair 24A reproduced the failure: the converter suite returned `FAILED (failures=1)` because the CLI reported one installed agent after `ONE.md` overwrote `one.md` on APFS. The extracted `validate_agent_collisions` seam permits a two-candidate assertion on every host while the two-file CLI case still runs when both directory entries exist. All 14 converter tests pass on this Mac; the real-file source collision branch remains unexercised here because APFS cannot represent the fixture.
- On 2026-09-29, milestone 18 fresh-install checks passed, but `scripts/test-install.sh` and `scripts/test-install.ps1` failed an existing copied-Gemini-guidance assertion. `.gemini/GEMINI.md` lacks the approved `write_file` saved-script sentence expected by both tests. Preserve the tests and repair the instruction before integrating the affected installer branch.
- The guidance repair made the Gemini assertion pass in both suites. The same suites then exposed missing approved Copilot file-first wording. The PowerShell suite also reports unsupported junction creation on this Mac, which needs separate environmental classification after guidance is repaired.
- Disposable-home refresh tests revealed that both installers replace Copilot and Gemini user hook configuration, incidentally removing old repository-state and Markdown Health registrations. Codex's merge already preserves them. The approved retirement decisions require leaving old installed registrations for manual cleanup; a separate repair must make refresh behavior match that decision without reintroducing retired entries on fresh installs.
- `rtk gain` fails in this Mac sandbox with `Failed to initialize tracking database: unable to open database file` even though `rtk --version` reports 0.50.0 and `rtk hook --help` lists Copilot and Gemini. Treat `rtk gain` as optional diagnostics, not an installation identity gate.
- Milestone 17's disposable-home Bash and PowerShell installer suites pass with stable-version shims. The macOS RTK 0.50.0 explicit missing-file command preserved its error and exit, but this non-agent shell did not emit the old false advisory even when the documented environment override forced it on; native provider and Windows checks remain separate gates.
- macOS `/var` is a symlink to `/private/var`, so safe RTK destination checks normalize the selected home before checking for user-created links. The generator suite needs checkout write permission because it temporarily corrupts and restores generated files; its 25 tests passed with that permission.
- The milestone 18 rebase had 11 content conflicts where stable RTK replaced prerelease registrations and the provider-preservation repair changed documentation. The resolved installer lists and generator expectations keep stable RTK, omit the retired guard, and retain exact old Copilot/Gemini registrations during refresh. Its first generator-suite run hit five sandbox `PermissionError`s while intentionally modifying generated files; the same 25-test suite passed with checkout write access.
- The milestone 19 rebase onto `cc0ca9c7` had 13 conflicted files. Stable RTK and old-registration preservation remained intact; the old Markdown checker and its maintained ownership were removed. The generator now owns 26 outputs. The full aggregate runner stops at dependency preflight on this Mac because external `flock` is absent. Targeted suites below passed; native Windows proof remains in milestone 24.
- Codex runs project hook commands with the session `cwd`, which may be nested. The repository Stop registration resolves its script from the Git root; the POSIX public test invokes that exact command from a nested directory. Native Windows execution remains for milestone 24.
- The Copilot and Gemini startup suites retained obsolete post-tool OKF registration assertions after milestone 20 removed those registrations. The tests now assert turn-end-only repository OKF wiring; no runtime registration was restored.
- The generated-hook writer needs checkout write access to create its lock file in this isolated worktree. Read-only generator checks and provider suites ran normally; the transactional writer and 25 mutation tests ran with scoped checkout write permission.
- Milestone 22 rebased onto accepted M17-21 with one conflict in `.agents/memory/API_MAP.md`: keep the base's 26 generated outputs after hook retirements and the M22 exact-reason contract. The generated output check reports 26 current files. The generator suite's first run hit five sandbox permission errors while mutating fixture copies in this worktree; all 25 tests passed with scoped write access.
- Direct scanner profiling found a 20 ms polling sleep after each fast Git launch. A clean scan has several distinct Git checks, so this repeated delay dominated subprocess wall time. The same 25-sample benchmark fell from 216-225 ms clean-scan median to 102-110 ms after `Popen.wait(timeout=...)`, while malformed-input failure time stayed about 29-38 ms. Scanner timeout, capture-size, descendant, and fail-closed tests still pass.
- Milestone 24's macOS `scripts/test-all.py` preflight stops before suites because external `flock` is absent. Its 15 public CLI/registry tests pass. The separate `scripts/test-codex-agents.py` collision fixture fails one case on this case-insensitive APFS volume because `ONE.md` overwrites `one.md`; preserve that assertion for Repair 24A rather than treating this local run as a converter pass. Concurrent observability suites encountered a SQLite lock and fixture cleanup race; both passed when rerun sequentially.

## Decision Log

- Decision: Keep completed former milestones as compact history and add new numbered milestones with independent acceptance.
  Rationale: Old results remain traceable without implying they prove revised behavior.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Require explicit user approval of this revised plan and the Windows checklist before source implementation.
  Rationale: The user required planning to finish before implementation restarts.
  Date/Author: 2026-09-28, user and Codex.
- Decision: The user approved the revised ExecPlan and Windows checklist and directed implementation to begin.
  Rationale: The agreed planning gate is satisfied; milestone 17 is the first source milestone.
  Date/Author: 2026-09-28, user.
- Decision: Migrate stable RTK and retire obsolete hooks first; add OKF and visible messages; refine Tool Guardian; measure the final high-rate hook set; finish with platform and live checks.
  Rationale: Each later gate can inspect the registrations that will actually remain.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Keep Copilot and Gemini functional live checks in separate later milestones. Run the performance audit by directly executing scripts on macOS, with no live CLI timing gate.
  Rationale: The CLIs are absent on this Mac, while direct process timing measures the hook cost under review.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Leave old installed repository-state and Markdown Health copies and state for manual cleanup. Preserve audit history. Remove only verified owned prerelease RTK assets.
  Rationale: Unknown or modified user files must not be deleted by migration.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Verify stable RTK on Windows with its version and supported hook subcommands rather than requiring `rtk gain`.
  Rationale: The tracking dashboard can fail when its database is unwritable despite a working 0.50.0 binary; installer identity and hook capability are the relevant checks.
  Date/Author: 2026-09-29, Codex.
- Decision: Share stable RTK version, TOML, backup, and verified-file retirement logic through one Python helper called by both installers.
  Rationale: The same public behavior and safety checks apply on Bash and PowerShell, while neither installer downloads a binary.
  Date/Author: 2026-09-29, Codex.
- Decision: Refuse to overwrite an existing RTK config backup; retire old installed scripts only on exact byte hashes and the old bundle only when its receipt names a known asset digest and matches the binary.
  Rationale: A repeated or modified installation must preserve unknown user data for manual review.
  Date/Author: 2026-09-29, Codex.
- Decision: Resolve milestone 18 on top of stable RTK and the provider-preservation repair by removing only repository-state ownership, source, and fresh registrations.
  Rationale: Current installations may retain exact retired registrations for manual cleanup, while new installations must contain only maintained handlers.
  Date/Author: 2026-09-29, Codex.
- Decision: Treat a definite OKF finding as one repair request, then permit the next stop with an unresolved-finding message; treat infrastructure failure as an allowed `OKF900` warning. Keep source-ingest blocking independent in the Copilot coordinator and Gemini sequential group.
  Rationale: The approved bounded turn-end contract requires useful repair feedback without trapping the turn on a broken checker.
  Date/Author: 2026-09-29, Codex.
- Decision: Use Copilot progress JSON for allowed startup and stop messages, Gemini and Codex `systemMessage` for allowed low-rate outcomes, and the existing denial reason for blocked outcomes. Codex Stop scanner alone adds a safe modified-file count on success.
  Rationale: These are the provider-native display surfaces supported by the existing adapters; denial reasons already have their own display path, and high-rate success must remain quiet.
  Date/Author: 2026-09-29, Codex.
- Decision: Benchmark each distinct high-rate executable through its public JSON process boundary in disposable macOS homes, including Gemini model chunks, then set host-specific budgets from the measured baseline.
  Rationale: Whole-process time captures startup, Git and RTK children, synchronous logging, and no-op cost without claiming provider delivery latency.
  Date/Author: 2026-09-29, Codex.
- Decision: Keep the scanner's distinct Git completeness checks and replace only the unconditional polling sleep with bounded `Popen.wait(timeout=...)`.
  Rationale: The measured repeated sleep was the clear hot-path defect; the replacement wakes on process exit without removing timeout, output-size, descendant, denial, or audit checks.
  Date/Author: 2026-09-29, Codex.
- Decision: Rebase the private M24 workflow preparation onto the Repair 24A planning commit while preserving both records in the handoff.
  Rationale: The native Windows gate and converter repair are separate open work; neither source evidence nor planning should imply acceptance of the other.
  Date/Author: 2026-09-29, Codex.
- Decision: Extract the existing Codex-agent source collision loop into `validate_agent_collisions` and assert its output collision with two in-memory candidates on every filesystem. Keep the real-file CLI assertion when the fixture creates two distinct directory entries.
  Rationale: A case-insensitive filesystem cannot supply the two files needed by the CLI case, while the extracted decision applies the same production checks without changing converter behavior.
  Date/Author: 2026-09-29, Codex.

## Outcomes & Retrospective

Planning decisions are complete and the user approved the revised plan. Milestones 17-23 are integrated. Milestone 19 retired maintained global Markdown Health code while preserving the independent OKF linter and old installed registrations during refresh. Milestone 20 added repository-local turn-end lint for all three CLIs with bounded audit and repair behavior. Milestone 21 added sparse startup and turn-end messages. Milestone 22 added exact safe Tool Guardian reasons and matching log detail. Milestone 23 measured every high-rate handler and cut scanner clean-call median latency from 216-225 ms to 102-110 ms on this Mac. Focused and disposable-home checks passed before the base branch fast-forwarded to tested tip `9dbb901d`. The aggregate runner is blocked at Mac prerequisite preflight by missing `flock`; targeted suites pass. No real user home was changed. Native Windows execution and live provider display remain later gates.

Milestone 20 source was integrated at `07d1f133` after focused public-hook, linter, installer, and generator checks passed on macOS. The audit distinguishes first and retry attempts and omits diagnostic text. Native Windows automation and provider-visible messages are later gates.

Milestone 21 source was integrated at `eba08529` and emits brief native-envelope messages for operational startup and turn-end hooks while retaining silent high-rate passes, SessionEnd success, observability events, and the bell. Focused Mac suites and temporary-home installers passed. Native Windows execution and installed display are later gates.

Milestone 22 source now reports safe exact Tool Guardian rules and true input-limit counts across the three generated provider hooks, with guard-log parity. Its source commit `892b8584` was integrated at `cb3f0093`. The 13 shared banner tests, three provider Tool Guardian suites, 25 generator tests, 15 aggregate-runner registry tests, generated-output check, and OKF lint passed on macOS. Native Windows and provider display proof remain later gates.

Milestone 23 isolated source measured all retained high-rate executable families and event-specific telemetry on macOS with 25 warm whole-subprocess samples per case. Scanner clean medians fell from 216-225 ms to 102-110 ms after the bounded Git wait change; the three scanner suites, generated-output check, and 25 generator tests pass. The full inventory, workloads, cold and warm distributions, budgets, and remaining costs are in `docs/ready-ideas-execplan/high-rate-hooks-performance.md`. Base integration remains before milestone 23 acceptance.

Milestone 24 source and Windows workflow preparation are integrated on `codex/ready-ideas-execplan` at `e98cb87a`. The Mac source sweep passed except for the converter collision fixture, which Repair 24A addresses. Native Windows execution remains required for M24 acceptance.

Repair 24A source commit `fe189186` is rebased onto integrated M24 preparation at `e98cb87a`. The macOS converter suite passes after preserving the file-based collision case on capable filesystems and adding an in-memory assertion of the same decision. Bash and PowerShell temporary-home installer suites pass; PowerShell skips unsupported junction creation on this Mac. Base integration remains outstanding, so repair acceptance is pending. A case-sensitive run can later exercise the retained two-file branch.

## Context and Orientation

Start in the repository root shown by git rev-parse --show-toplevel. Inspect status, staged and unstaged diffs, and untracked paths before changing files. Before edits, read .agents/memory/INDEX.md, then ARCHITECTURE.md and CONVENTIONS.md for nontrivial work, then each affected .agents/instructions area and matching known-issues/testing file. Use the repository tdd skill for source changes. Run update-agent-docs once at the end of each implementation work session, after all related tasks are done. Do not add dependencies without authorization. Never weaken a failing test. Do not write regression tests solely for feature deletions.

The three installed instruction sources are .copilot/copilot-instructions.md, .gemini/GEMINI.md, and .codex/AGENTS.md. The installers are scripts/install.sh and scripts/install.ps1. Canonical generated hook policy is under hooks/families/; hooks/manifest.py and hooks/providers.py describe outputs. Run python3 scripts/generate-hooks.py --write after source changes, then --check and scripts/test-generate-hooks.py. Do not hand-edit a generated provider script. Copilot user-level source is .copilot/hooks/, Gemini user-level source is .gemini/, and Codex user-level source is .codex/global-hooks.json plus .codex/hooks/. The Codex merger, scripts/install-codex-hooks.py, must preserve unrelated user hooks. Repository-local Copilot hooks are in .github/hooks/. The new Codex repository hook belongs in .codex/hooks.json and must not be installed globally.

A provider envelope is the JSON request and response for one hook event. Copilot CLI uses sessionStart, preToolUse, postToolUse, and agentStop. Gemini uses SessionStart, BeforeTool, AfterTool, AfterAgent, SessionEnd, and AfterModel. Codex uses SessionStart, PreToolUse, PostToolUse, and Stop. Provider versions may differ. Keep stdout to one valid final JSON response, except documented Copilot progress messages. Expected allow, warn, and deny control flow exits 0. Windows Copilot command hooks need powershell, and Codex uses commandWindows. Do not infer native display from an isolated stdin/stdout test. User-level cloud Copilot and VS Code Local or Copilot Agent Host are outside the new lifecycle and OKF live gates. Retain provider-envelope compatibility where already tested.

Use safe disposable repositories and fake data for security examples. Keep logs and transcripts outside scanner fixtures so they do not become scanned candidates. Keep permanent tests in tracked source; place probes in .agents/scratchpad/ or operating-system temp and remove only exact created files. For a real-home install, first run source and temporary-home tests, inspect destination changes and backup paths, then review provider hook trust. Do not bypass trust.

## Plan of Work

### Milestone 17: Move warning suppression to stable RTK

Status: done
Acceptance: met

Local source and disposable-home acceptance is met. Native Windows execution and provider-visible behavior remain in milestones 24-27.

Require RTK 0.50.0 or newer before either installer changes installed files. Do not download RTK. In scripts/install.sh and scripts/install.ps1, locate the user RTK TOML config at the platform location: macOS Library/Application Support/rtk/config.toml under the home directory, Linux .config/rtk/config.toml under the home directory, or Windows APPDATA/rtk/config.toml. Set only hooks.suppress_hook_warning to true. Preserve all other settings and comments where possible, back up a changed file, leave a correct file byte-identical, and stop safely on ambiguous or malformed config. An older or missing RTK stops the installer before any destination mutation and prints upgrade guidance.

Keep the Copilot and Gemini automatic RTK forwarders and their registrations. They call rtk hook copilot or rtk hook gemini for automatic filtering; the Copilot forwarder also maps RTK's ask to allow. Remove the pinned prerelease downloader scripts/install-rtk-prerelease.py, receipt/provenance route, explicit-command adapters, launchers, their generated targets and registrations, owned-file lists, obsolete tests, and old documentation from hooks/families/rtk.py, hooks/manifest.py, provider configs, and installers. Remove an installed prerelease asset only after exact repo ownership and content or receipt verification; leave unknown or modified files for manual review. Add scripts/test-rtk-stable.py and scripts/test-rtk-stable-windows.ps1 to test idempotent config migration, backups, malformed config, missing/old RTK preflight, POSIX and Windows paths, and clean installs with no stale registration. Exercise explicit RTK success and missing-file calls: the false notice is absent, while other stderr, stdout, argv effects, and exit codes remain. Test automatic forwarders separately.

### Milestone 18: Retire maintained repository-state enforcement

Status: done
Acceptance: met for checked-in source and fresh disposable installs; native Windows proof remains in milestone 24.

Integrated source commit: `21e14129`; tested branch tip `6b8e0938` matches the base after fast-forward. The source and fresh-install checks pass locally.

Remove hooks/families/repository_state.py, its three generated provider scripts, manifest targets, Copilot/Gemini/Codex registrations, installer ownership entries, dedicated tests, and aggregate test or workflow references. Preserve shared audit infrastructure and unrelated hooks. Do not add deletion regression tests. Update AGENTS.md Git protection text: keep the direct .git edit ban and review before destructive Git commands, but remove instructions that depend on a repository-state hook blocking them. Do not claim instructions prevent arbitrary writes.

Do not automatically remove old installed scripts or registrations. Document their likely locations and manual cleanup; they can keep running on another machine. Inspect source registrations, generator output, both installers, and fresh temporary-home installations for absence of the retired guard. Keep the change isolated so retained hooks still run. The acceptance claim applies to checked-in source and fresh installations.

### Milestone 19: Retire global Markdown Health

Status: done
Acceptance: met for checked-in source and fresh disposable installs; native Windows proof remains in milestone 24.

Remove hooks/families/markdown_health.py, its generated Copilot/Gemini/Codex scripts, manifest targets, maintained user-level pre/post/stop registrations, installer copy and ownership rules, and dedicated tests or aggregate references. Preserve scripts/lint-okf.py and its tests. Preserve existing audit.log history and dedicated markdown-health-state directories. Do not automatically remove installed old hook files or registrations; document them for manual cleanup and state clearly that they may still execute. Do not add deletion regression tests.

Inspect checked-in source, generated targets, registrations, installers, and a fresh temporary-home installation. Show that the old checker is absent and unrelated hook groups remain. This source and fresh-install proof does not certify older user installations.

### Repair 19A: Preserve retired installed registrations on refresh

Status: done
Acceptance: met for source and disposable-home behavior; native Windows junction proof remains in milestone 24.

When `install.sh` or `install.ps1` refreshes an existing user home, preserve exact existing Copilot and Gemini registrations that invoke the retired repository-state or Markdown Health scripts. Preserve unrelated user settings and hook entries. Do not restore retired registrations to a fresh install, add duplicate entries on repeated refresh, or copy retired scripts into a new home. Stop safely on malformed or ambiguous existing JSON rather than overwriting it. Keep the existing Codex merge behavior, which already leaves old unowned registrations alone. Add disposable-home Bash and PowerShell tests for old-entry preservation, fresh absence, unrelated entries, idempotence, and malformed input. Record the old-hook manual cleanup limitation. Integrate this repair before accepting milestones 18 and 19.

### Milestone 20: Validate repository OKF at turn end

Status: done
Acceptance: met for checked-in source and temporary-home installs; native Windows proof remains in milestone 24 and installed provider display in milestones 25-27.

Keep scripts/lint-okf.py as the only OKF rule authority. It checks canonical Markdown under .agents/instructions/ and .agents/memory/, exiting 0 for pass, 1 for findings, and 2 for infrastructure failure. Keep Copilot's repository-local agentStop adapter through .github/hooks/scripts/validate-stop.py and Gemini's repository-local AfterAgent adapter under .gemini/hooks/scripts/lint-okf.py. Remove only redundant Copilot postToolUse and Gemini AfterTool OKF registrations. Add a repository-local .codex/hooks.json Stop command and self-contained adapter, never a user-global Codex registration. If installed provider versions or worktree rules differ, record the observed limit and keep acceptance open.

Validate the full canonical OKF tree once per turn-end attempt. Report pass, definite findings, or incomplete with provider-valid, bounded JSON. Give the agent one repair attempt after a definite finding; on the next stop attempt permit completion with visible unresolved findings. A checker crash, timeout, or malformed output is incomplete and must not strand the turn. Emit one audit.log line per nonempty validation batch with outcome, safe counts, and sorted workspace-relative checked paths. Cap the physical line at 4 KiB, show omitted-path count, suppress identical repeated stop events, and keep content, link targets, and diagnostic text out. An audit-write failure warns without changing the lint decision.

Extend scripts/test-hooks-okf-lint.sh and scripts/test-gemini-hooks-okf-lint.sh, and add scripts/test-codex-repository-okf.sh and scripts/test-repository-okf-windows.ps1. Use public envelope tests for pass, findings, incomplete, first block, allowed second stop, repeated stop deduplication, path and output caps, nested-worktree resolution, and Windows path behavior. Verify no post-tool OKF entry and no user-global copy. Run scripts/test-okf-lint.sh for the independent central linter. Installed native message proof belongs to milestones 25-27; Windows automated behavior belongs to milestone 24.

The integrated source has the adapters, project registrations, and focused public-envelope suites. Copilot and Gemini post-tool OKF registrations are absent. Codex uses a project-local Stop command resolved from the Git root, with no global installer copy. Copilot, Gemini, and Codex direct tests, central linter, generator freshness, aggregate-runner CLI tests, Codex hook merger, and both temporary-home installer suites pass on macOS. PowerShell installer tests skip one unsupported junction fixture, and the new Windows suite skips native behavior here. Native Windows execution and installed provider display remain separate later acceptance gates.

### Milestone 21: Show sparse lifecycle messages

Status: done
Acceptance: met for checked-in source and temporary-home installs; native Windows proof remains in milestone 24 and installed provider display in milestones 25-27.

For local Copilot CLI, Gemini CLI, and Codex CLI only, make each retained operational low-rate startup or turn-end hook report one short native message with hook name, outcome, and safe count when useful. Show every stop attempt, including a repair retry; do not add a turn-end coordinator. Ordinary success lines contain no path, command, or document content. SessionEnd success, telemetry-only hooks, and the completion bell stay silent. High-rate pre/post-tool passes stay silent, while a block, warning, incomplete result, or meaningful change appears immediately.

Use provider-native message fields, keep stdout JSON-only, and avoid a second display when the provider already shows a denial reason. Existing Tool Guardian and scanner logs plus RTK observability traces supply high-rate run evidence; do not add one RTK audit line per call or claim one shared audit log covers every hook. Add scripts/test-lifecycle-messages-windows.ps1 and focused provider-envelope cases for startup pass, turn-end pass/fail/incomplete, repeated stop, tool pass silence, block/warn visibility, message bounds, and safe counts in provider envelopes. Native CLI display proof is in milestones 25-27. The new repository OKF hook follows this policy.

The integrated implementation updates startup loaders, source-ingest startup hooks, the Copilot stop coordinator, Gemini source-ingest and OKF `AfterAgent` hooks, Codex repository OKF, and Codex Stop scanner. Generated provider outputs are current. The new Windows fixture is registered in the focused workflow and aggregate runner, but its native cases have not run on this Mac. Source and disposable-home proof is recorded below.

### Milestone 22: Explain Tool Guardian violations

Status: done
Acceptance: met for checked-in source and provider envelopes; native display remains in milestones 25-27.

The tested source commit `892b8584` is integrated at tip `cb3f0093`. One API map conflict retained the current 26-output generator count and the new exact-reason contract. Focused source and generated-output checks pass.

Edit canonical hooks/families/tool_guard.py and regenerate provider outputs. Retain a safe rule identifier and cause when building threats instead of reducing each finding to category/severity. Show up to three distinct reasons and an omitted count while preserving blocked versus warning wording, severity, safe action name, and one redacted Action excerpt of at most 160 characters. For an input limit, identify the exact limit, configured threshold, and measured count with its true unit when available. Name a provider field such as write_file.content only from a trusted known-field list; otherwise say tool input. For known inspection failure, state only a safe cause and keep fail-closed behavior. Do not echo exception text, arbitrary keys, raw input, or matched secrets.

Do not tell an agent to adjust TOOL_GUARD_ALLOWLIST for input limits, since that setting cannot bypass them. Reuse an existing static suggestion only when accurate and simple; no new remediation engine is required. Guard logs must contain the same safe rule IDs, limit/count detail, and identical redacted Action excerpt shown to the agent, with no raw input. Extend the Copilot/Gemini Tool Guardian suites and add scripts/test-codex-hooks-tool-guard.sh to test scan-size, segment, token, depth, node, string, and byte limits; dangerous-operation rules; multiple findings; known/unknown fields; inspection failure; block/warn; log alignment; and redaction. Use public Copilot, Gemini, and Codex envelopes plus native display in the later live milestones. Preserve the prior scan-secrets generic message rule: no matched value in its banner.

### Milestone 23: Measure and improve every retained high-rate hook

Status: done
Acceptance: met for direct macOS script performance and source checks.

After milestones 17-22 fix the final hook graph, enumerate every retained handler called per tool or faster across three providers. Include security, RTK automatic forwarding, no-op paths, observability telemetry, and Gemini AfterModel streaming chunks. Record provider, source scope, event, matcher, executable, and expected call rate. On macOS, invoke each entrypoint directly with representative provider JSON and environment. Include clean, finding, failure, repeated, large-input, and concurrent workloads. Measure whole subprocess wall time, including Python startup, input/output, synchronous logging, and message creation. Where practical, measure handler-only time separately and compare a minimal process control and previous handler version. Report cold and warm median, p95, variation, and unisolatable cost.

Set numeric budgets only after the baseline shows noise and configured timeout headroom. Review redundant launches, parsing, scans, disk sync, locks, and unbounded work. Fix clear redundant or reproducibly slow hot paths and rerun exact scenarios. Never remove a security check, weaken fail-closed behavior, or suppress needed diagnostics for speed. Record before/after measurements, units, environment, sample count, risk, and remaining cost. This milestone requires no live provider CLI or Windows benchmark.

The integrated implementation and direct-script proof are recorded in `high-rate-hooks-performance.md`. The test command is `rtk test python3 scripts/benchmark-high-rate-hooks.py --samples 25 --warmups 3 --output /private/tmp/high-rate-hooks.json` from the repository root. Expect 45 measured scenarios, provider-valid denials on synthetic findings, and approximately 100-110 ms clean scanner medians on the recorded Mac host after the change. Do not treat those host-specific numbers as Windows or installed CLI proof.

### Milestone 24: Prove integrated source and native Windows behavior

Status: in progress
Acceptance: not met

Regenerate all maintained targets and run the generator's check and parity tests. Run affected public hook suites, scripts/test-all.py where it provides distinct integration proof, and Bash and PowerShell temporary-home installer tests. Verify both installers preserve unrelated settings, stop before mutation on preflight failure, keep owner-only permissions, and install only current maintained handlers. Check no repository-state, global Markdown Health, or prerelease RTK registration appears in a fresh home. Verify the new repository Codex OKF registration stays in the checkout. Update README.md, the three provider instruction sources, .agents/instructions/hooks.md, relevant script guidance, and the .agents file, API, testing, and known-issue maps to describe the retained hook set. Review all changed source and docs for obsolete claims.

Update .github/workflows/ready-ideas-windows.yml and windows-live-check.md for the current hook set. Provision stable RTK on the Windows runner with the official winget package rtk-ai.rtk before installer tests, then verify rtk --version is at least 0.50.0 and rtk hook --help lists copilot and gemini processors. Keep the repository installers free of RTK download logic. Remove obsolete deletion-only suites from the workflow and run scripts/test-rtk-stable-windows.ps1, scripts/test-repository-okf-windows.ps1, scripts/test-lifecycle-messages-windows.ps1, and existing current-hook Windows tests. Run the existing native Windows scripts/test-scan-secrets-windows.ps1 committed-repository HEAD-failure case: an unexpected rev-parse failure must be incomplete, not clean; a genuinely unborn branch must still work. A macOS skip does not satisfy this gate. Windows automation plus a documented live-check procedure is required; a live Windows provider run is not the completion gate. Do not fabricate a pass if a runner is unavailable.

### Repair 24A: Make converter collision coverage portable

Status: done
Acceptance: met for portable collision decision coverage and the full Mac converter suite; real-file two-name execution remains a separate case-sensitive check.

The `scripts/test-codex-agents.py` case-fold collision fixture cannot create two distinct case-fold-equivalent filenames on this Mac's case-insensitive APFS volume. Reproduce the existing suite failure, retain its real-file end-to-end collision case on filesystems that support both names, and add an internal test seam that exercises the same collision decision portably. Do not skip, delete, or weaken the collision assertion. Run the complete converter suite on this Mac and record the filesystem limit of the end-to-end fixture. Keep this repair separate from milestone 24 hook and Windows work.

The integrated implementation extracts the existing collision loop into `scripts/install-codex-agents.py:validate_agent_collisions`. `scripts/test-codex-agents.py` asserts the duplicate output error with two in-memory agent definitions on every host. The original two-file CLI assertion still runs when the fixture produces two directory entries. The current Mac produces one entry, so its real-file branch cannot execute; retain that branch for a case-sensitive filesystem.

### Milestone 25: Verify installed Codex CLI

Status: open
Acceptance: not met

On a host with Codex CLI, install only after source and temporary-home checks. Inspect the exact user-hook config merge and backups, then review hook trust through /hooks. In a disposable checkout, verify stable RTK explicit success and error behavior; sparse startup and every Stop result; repository OKF repair and audit; Tool Guardian exact safe rule/cause and redacted log; scan-secrets generic warning/denial; and silence on successful per-tool events. Confirm retired user-level handlers are absent from a fresh install. If an older installed registration remains, report it separately rather than calling a fresh-install check complete. Capture provider version and exact observed text. Restore only probe-owned user settings and remove exact disposable paths.

### Milestone 26: Verify installed Copilot CLI

Status: open
Acceptance: not met

In a session with Copilot CLI available, follow the same safe install, backup, trust, disposable-checkout, and evidence rules. Exercise native startup, preToolUse, postToolUse, and agentStop delivery. Confirm automatic RTK forwarding remains, explicit stable RTK lacks the false notice, security messages identify exact safe causes, repository OKF runs at turn end but not after tools, and ordinary high-rate passes produce no user message. Use fake data and a harmless blocked action; keep logs outside the checkout. Record provider version and the documented fail-open timeout limitation. Deployed VS Code modes are outside this gate; retain their source envelope tests where applicable.

### Milestone 27: Verify installed Gemini CLI

Status: open
Acceptance: not met

In a session with Gemini CLI available, repeat the corresponding safe installed checks for SessionStart, BeforeTool, AfterTool, AfterAgent, and scanner SessionEnd. Confirm automatic RTK forwarding, stable explicit RTK behavior, actionable Tool Guardian reason, repository OKF at turn end only, visible repeated stop attempts, and high-rate pass silence. Verify any SessionEnd success stays audit-only and actionable warning is visible. Record provider version and distinguish handler runtime from startup latency. Keep any accepted timeout tool-continuation limitation explicit. Restore exact probe-owned settings and files after recording evidence.

## Concrete Steps

Run commands from the repository root. First run rtk git status --short and inspect affected staged, unstaged, and untracked paths. After approval, use a failing public behavior test before each source change, except feature deletion, which uses source/install inspection and no deletion regression test. For generated hooks:

    python3 scripts/generate-hooks.py --write
    rtk test python3 scripts/generate-hooks.py --check
    rtk test python3 scripts/test-generate-hooks.py

For focused scanner and security behavior, use the existing public entrypoint suites where present:

    rtk test bash scripts/test-hooks-tool-guard.sh
    rtk test bash scripts/test-gemini-hooks-tool-guard.sh
    rtk test bash scripts/test-codex-hooks-tool-guard.sh
    rtk test bash scripts/test-hooks-secrets-scanner.sh
    rtk test bash scripts/test-gemini-hooks-secrets-scanner.sh
    rtk test bash scripts/test-codex-hooks-secrets-scanner.sh

For OKF and installers, run these existing and planned suites after their milestone creates any missing one:

    rtk test bash scripts/test-okf-lint.sh
    rtk test bash scripts/test-hooks-okf-lint.sh
    rtk test bash scripts/test-gemini-hooks-okf-lint.sh
    rtk test bash scripts/test-codex-repository-okf.sh
    rtk test python3 scripts/test-rtk-stable.py
    rtk test bash scripts/test-install.sh
    rtk test pwsh -NoProfile -File scripts/test-install.ps1

The native Windows workflow must run its current commands on a Windows runner; a local macOS pwsh skip is only syntax evidence. For live delivery, use scripts/probe-provider-hook-delivery.py prepare, then the provider CLI, then verify, and always cleanup. The probe inserts uniquely named temporary handlers, records owner-only nonce markers, and restores only unchanged settings it owns. A nonce must not appear in the agent prompt; native display of that nonce proves hook delivery. Do not use a trust-bypass flag against ordinary user settings.

For each milestone, add short output, command, date, and scope to Progress and Artifacts and Notes. Mark its narrative Status and Acceptance at the same time as its Progress item. Before stopping after code changes, synchronize this plan and run update-agent-docs once. Finish with rtk git diff --check and a comparison of final Git status to its starting baseline.

## Validation and Acceptance

Each milestone is independently accepted only after its stated behavioral proof. Historical old-design results never close new milestones. Distinguish source tests, fresh temporary-home installs, real installed behavior, native Windows automation, and macOS performance measurements. Copilot/Gemini live sessions can occur later without keeping completed source milestones open; the overall revised plan remains incomplete until all required live milestones and the native Windows scanner gate pass.

Final acceptance requires stable RTK warning suppression with preserved errors and exit codes; current fresh registrations with obsolete hook families absent; repository-only OKF turn-end pass/fail/incomplete messages and bounded audit; sparse lifecycle output; specific and redacted Tool Guardian reasons; generic secret-scanner notices; and a measured, improved or justified high-rate hook inventory. Keep user-global old-copy limitations and fail-open provider timeouts explicit. Run no destructive Git action and use no real secret for acceptance.

## Idempotence and Recovery

Repeat generation and isolated installation without duplicate handlers or unnecessary config rewrites. On RTK preflight or TOML ambiguity, stop before installed-file mutation and leave the old installation intact; report exact manual recovery. Back up only changed RTK config and owned hook settings. Remove prerelease installed files only with verified ownership and exact content evidence. Leave modified or unknown files, old repository-state and Markdown Health installed copies, state directories, and audit history untouched for manual review. Do not make stale user registrations look like current fresh-install behavior.

Scanner failure discards partial Git output and returns incomplete, with block-mode denial or warn-mode notice. A failed provider live check leaves its milestone open and preserves working hooks; restore only the probe's exact owned changes. Never clear a dirty worktree for a test, overwrite unrelated user hooks, or disable a failing test.

## Artifacts and Notes

Planning inputs are the closed decision tickets under docs/ready-ideas-execplan/tickets/ and the provider facts in its research directory. This plan embeds their executable requirements, so an executor need not read the tickets to know the target behavior. The prior implementation reached c0d9ca34 and passed old source/provider tests and live Copilot, Gemini, and Codex probes. Its scanner HEAD-failure native Windows extension still needs proof. Milestone 17 removed checked-in prerelease RTK source; milestone 18 retired the maintained repository-state guard; milestone 19 retired global Markdown Health.

Milestone 17 local evidence (2026-09-29, isolated `codex/ready-rtk-stable` checkout): `rtk --version` reported `rtk 0.50.0`; `python3 scripts/test-rtk-stable.py` passed 12 tests; `bash scripts/test-install.sh` and `pwsh -NoProfile -File scripts/test-install.ps1` passed in disposable homes; `python3 scripts/test-generate-hooks.py` passed 25 tests with checkout write permission; `python3 scripts/generate-hooks.py --check` reported 32 current outputs. The Copilot and Gemini automatic RTK suites and Codex hook merger test passed. `python3 scripts/lint-okf.py` and `rtk git diff --check` passed. A disposable migration probe removed an exact old Codex adapter while preserving a modified Gemini file for manual review. A disposable explicit `rtk read absent-file` kept nonzero exit and file error, but this shell did not show the former warning before or after configuration; no live provider display or native Windows run is claimed.

Milestone 19 rebase evidence (2026-09-29, isolated `codex/ready-retire-markdown` at `46eef579`, based on `cc0ca9c7`): generator `--write` and `--check` reported 26 current outputs; 25 generator tests passed with checkout write permission. Both full temporary-home installer suites passed, with PowerShell's junction case skipped on this Mac. Codex merger, Codex Windows envelopes, 15 aggregate-runner unit tests, standalone OKF lint and its CLI suite, and Copilot/Gemini RTK and Tool Guardian suites passed. Source search found no Markdown Health family, generated target, maintained registration, installer ownership, or aggregate entry. `scripts/test-all.py` exited 2 before suites because external `flock` is unavailable. `git diff --check` passed. This proves source and fresh-install behavior, not native Windows or older user homes.

Repair 19A evidence (2026-09-29, isolated `codex/ready-preserve-retired` checkout rebased onto milestone 17): both installer suites passed with the provider configuration checks preceding RTK configuration writes. The 12 stable RTK tests, generated-hook freshness check for 32 files, OKF lint, Bash syntax check, and `git diff --check` passed. The PowerShell suite skipped its junction fixture on this Mac; native Windows proof remains later work.

Milestone 20 isolated source evidence (2026-09-29, `codex/ready-repository-okf`, original pre-rebase commit `4e07e714`): `bash scripts/test-hooks-okf-lint.sh`, `bash scripts/test-gemini-hooks-okf-lint.sh`, `bash scripts/test-codex-repository-okf.sh`, `bash scripts/test-okf-lint.sh`, `python3 scripts/test_test_all.py`, `python3 scripts/test-install-codex-hooks.py`, `bash scripts/test-install.sh`, `pwsh -NoProfile -File scripts/test-install.ps1`, `python3 scripts/generate-hooks.py --check`, and `python3 scripts/lint-okf.py` passed. The native Windows OKF suite skipped on macOS, and PowerShell installer junction creation was unsupported here. No real user home was modified.

Milestone 20 rebase evidence (2026-09-29, source commit `a58ae3bb` on `73db7d4d`): Four content conflicts were resolved in `.agents/memory/FILE_MAP.md`, `.github/workflows/ready-ideas-windows.yml`, this ExecPlan, and `docs/ready-ideas-execplan/handoff.md`. The retired Markdown Health Windows test stayed removed; the repository OKF test was retained. Post-rebase `rtk test bash scripts/test-hooks-okf-lint.sh`, `rtk test bash scripts/test-gemini-hooks-okf-lint.sh`, `rtk test bash scripts/test-codex-repository-okf.sh`, `rtk test bash scripts/test-okf-lint.sh`, `rtk test python3 scripts/test_test_all.py` (15 tests), `rtk test python3 scripts/test-install-codex-hooks.py`, `rtk test python3 scripts/generate-hooks.py --check` (26 current outputs), `rtk test python3 scripts/lint-okf.py`, `rtk test bash scripts/test-install.sh`, `rtk test pwsh -NoProfile -File scripts/test-install.ps1`, and `rtk git diff --check` passed. `rtk test pwsh -NoProfile -File scripts/test-repository-okf-windows.ps1` exited 0 with native cases skipped on macOS; the PowerShell installer skipped unsupported junction creation. Base integration and native Windows behavior remain unverified.

Milestone 21 isolated source evidence (2026-09-29, `codex/ready-lifecycle-messages` based on `30e621d2`): Copilot/Gemini/Codex startup and OKF focused suites, both source-ingest suites, all three scanner suites, the security-banner suite, 15 aggregate-runner tests, both disposable-home installer suites, central OKF lint, generated-hook check (26 outputs), and 25 generated-hook tests passed on macOS. The PowerShell installer skipped its unsupported junction fixture. `scripts/test-lifecycle-messages-windows.ps1` parsed and skipped native cases here; its embedded Python envelope checks also passed in a Mac compatibility run with only the native-OS guard removed. This does not claim a native Windows or live CLI display pass. The generator writer and its mutation tests required scoped checkout write permission. No real user home was installed or changed.

Milestone 23 isolated source evidence (2026-09-29, `codex/ready-hook-performance` based on `9ef9e8e5`): `scripts/benchmark-high-rate-hooks.py` ran 45 direct-script scenarios with 25 warm samples after three warmups, first-call cold values, and four-process clean-handler batches. The scanner's clean median improved from 225.1 to 110.3 ms for Copilot, 216.4 to 102.3 ms for Gemini, and 216.4 to 103.6 ms for Codex. Finding and large-file paths improved similarly, beyond baseline variation. The malformed-input path remained about 29-38 ms. All three scanner public suites, generator `--check` for 26 outputs, and 25 generator tests passed. The first generator mutation run had five sandbox lock-write errors; scoped checkout write access made all 25 pass. The report `docs/ready-ideas-execplan/high-rate-hooks-performance.md` has the full inventory, method, budgets, remaining cost, and limits. No live provider or Windows benchmark ran.

Milestone 24 macOS source evidence (2026-09-29, isolated `codex/ready-integrated-windows` based on `342d6391`): `scripts/generate-hooks.py --write` found 26 current outputs, `--check` passed, and all 25 generator parity tests passed with scoped worktree write access. Bash and PowerShell disposable-home installer suites passed; PowerShell skipped unsupported junction creation. Twelve stable RTK tests, 13 shared security-banner tests, 15 aggregate-runner CLI/registry tests, central OKF lint and its CLI suite, all three startup, scanner, and Tool Guardian suites, Copilot/Gemini auto-ingest, repository OKF, Copilot/Gemini RTK, and both sequential observability suites passed. The checked-in Copilot, Gemini, and user-global Codex registration files contain no retired commands; repository Codex OKF is registered only in `.codex/hooks.json`. The aggregate runner itself exited 2 at `flock` preflight before suites. The separate Codex-agent converter suite passed 12 of 13 tests; its case-folded filename collision fixture cannot form distinct source files on this case-insensitive volume and awaits Repair 24A. The native Windows scanner, RTK, repository OKF, and lifecycle scripts all skipped on macOS. No real home, Windows runner, provider CLI, workflow dispatch, or push was used. The workflow now installs the official `rtk-ai.rtk` winget package and requires a stable version at least 0.50.0 plus `copilot` and `gemini` processors; actual runner version and native outcomes remain unverified.

Repair 24A isolated source evidence (2026-09-29, `codex/ready-converter-portable` based on `743abc01`): before the change, `python3 scripts/test-codex-agents.py` ran 13 tests with one failure at the two-file source collision fixture; the CLI installed one agent because APFS merged `one.md` and `ONE.md`. The test-first seam case initially failed with missing `validate_agent_collisions`. After extracting the unchanged collision loop, the complete converter suite passed 14 tests. `bash -n scripts/install.sh`, `bash scripts/test-install.sh`, `pwsh -NoProfile -File scripts/test-install.ps1`, `python3 scripts/test_test_all.py` (15 tests), `python3 scripts/lint-okf.py`, and `git diff --check` passed. PowerShell skipped only junction creation, unsupported on this host. The two-file CLI branch remains for a case-sensitive filesystem and was not exercised here; no native Windows result or integration is claimed.

Capture concise evidence after execution: RTK version and config backup path without private contents; an explicit missing-file RTK exit; current registration lists; one safe OKF audit line with counts; a redacted Tool Guardian reason and matching log fields; per-handler timing distributions; native Windows scanner HEAD-failure result; and provider-visible messages. Do not paste raw tool input, credential values, entire logs, or private home paths unnecessarily. The Windows checklist is docs/ready-ideas-execplan/windows-live-check.md.

## Interfaces and Dependencies

Canonical generated hook families expose render(provider, target) through hooks/families/, hooks/providers.py, and hooks/manifest.py. Generated scripts must be self-contained at runtime and output provider-valid JSON; they must not import another provider's installed files. scripts/install-codex-hooks.py owns exact maintained command identities, not whole user event groups. A repository-local .codex/hooks.json is separate from the user-global .codex/global-hooks.json template. Keep Copilot bash/powershell command alternatives, Codex commandWindows, and Gemini millisecond timeout units.

RTK stable 0.50.0 or newer is an external prerequisite, not installed by this repository. Python standard-library code and existing scripts supply the hook behavior; no new package, database, or service is planned. Existing scan-secrets file-backed Git capture remains a security boundary and must return complete output or a typed incomplete result, never partial bytes. The OKF adapter calls scripts/lint-okf.py rather than copying its rules. Tool Guardian uses safe structured rule metadata and the prior redacted Action formatter; no provider runtime imports another provider's code.

Revision note, 2026-09-28: The user replaced the old prerelease and guard/checker outcomes, requested lifecycle visibility and high-rate performance review, then added exact Tool Guardian causes. This revision compresses old milestones, adds new gates, and removes old-design implementation instructions.

Revision note, 2026-09-29: The user explicitly approved this plan and the Windows checklist, clearing the source implementation gate.

Revision note, 2026-09-29: A working local RTK 0.50.0 could not open its tracking database for `rtk gain`. Windows proof now checks version and the hook command surface rather than dashboard storage.

Revision note, 2026-09-29: Milestone 17 implementation now uses stable RTK config and verified legacy-file cleanup. Its local tests and generator checks pass; real Windows and provider-session proof remain in later milestones.

Revision note, 2026-09-29: Repair 19A now preserves retired Copilot and Gemini registrations during refresh while checking both configurations before stable RTK changes the home. Its isolated rebase and tests passed; integration and milestone acceptance remain open.

Revision note, 2026-09-29: Milestone 19 was rebased onto integrated stable RTK, repository-state retirement, and Repair 19A. Its source and disposable-home proof preceded acceptance at `73db7d4d`; the Mac aggregate preflight lacks `flock`.

Revision note, 2026-09-29: Milestone 20 implementation added project-local turn-end OKF validation, bounded audit, and public-envelope suites. This isolated result is recorded for integration without claiming native Windows or live provider acceptance.

Revision note, 2026-09-29: Rebased milestone 20 source as `a58ae3bb` onto accepted M19 at `73db7d4d`. Four documentation and workflow conflicts were resolved with both retirements intact; post-rebase focused checks passed. Milestone 20 remains open until base fast-forward.

Revision note, 2026-09-29: Implemented milestone 21 on an isolated branch with provider-native sparse lifecycle messages and a registered Windows fixture. Source checks pass; integration, native Windows execution, and installed display remain open.

Revision note, 2026-09-29: Rebased milestone 22 onto accepted M17-21, resolved the API map output-count conflict, and reran focused Tool Guardian, generator, registry, and OKF checks. The base later integrated and accepted it at `cb3f0093`.

Revision note, 2026-09-29: Recorded milestone 23's direct macOS high-rate inventory and benchmark evidence, set host-specific budgets after the baseline, and reduced scanner Git polling delay without changing security checks. Acceptance remains open until the isolated source commit is integrated.

Revision note, 2026-09-29: Milestone 24 source and Windows workflow preparation are recorded without native Windows acceptance. Repair 24A owns the existing converter collision fixture's case-insensitive-volume failure; keep M24 open until a native Windows run proves the scanner HEAD-failure distinction and other current suites.

Revision note, 2026-09-29: Rebased M24 preparation as `cc94dcda` over Repair 24A planning at `743abc01`. The handoff conflict now preserves both records; Windows acceptance and converter repair stay open.

Revision note, 2026-09-29: Repair 24A preserves the real-file Codex-agent collision case on capable filesystems and adds a portable assertion at the extracted collision decision. The local converter and pertinent installer checks pass. Acceptance remains pending branch integration; the case-sensitive CLI branch remains available for later verification.

Revision note, 2026-09-29: Rebased Repair 24A source as `fe189186` onto the integrated M24 preparation at `e98cb87a`. The ExecPlan and handoff conflicts were resolved with both evidence sets preserved. The converter suite, both installer suites, OKF lint, and diff checks passed after resolution; native Windows and case-sensitive two-file verification remain open.
