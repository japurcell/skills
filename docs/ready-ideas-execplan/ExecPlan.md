# Simplify and verify local agent hooks across providers

This ExecPlan is a living document. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current. Work from the repository root and follow .agents/skills/exec-plans/SKILL.md.

Planning revision: 2026-09-28. The prior implementation through c0d9ca34 remains checked in. Its completed tests prove the former design only. No revised source, installer, registration, or user installation has changed. The user must explicitly approve this revised ExecPlan and windows-live-check.md before source implementation resumes.

## Purpose / Big Picture

Local Copilot CLI, Gemini CLI, and Codex sessions should show useful security and lifecycle messages without noisy per-tool success messages. Explicit RTK commands should stop showing the false missing-hook warning using stable RTK 0.50.0 or newer. The obsolete repository-state and workspace-wide Markdown hooks should leave maintained source and fresh installations. Repository-local OKF lint should run when an agent tries to finish a turn. High-rate hooks should have measured, reviewed latency.

A user can verify the result by running an explicit RTK command, observing startup and turn-end hook messages, causing a safe Tool Guardian denial that names its exact rule, and viewing one bounded OKF audit record for a turn-end check. Native Windows automation, local provider display checks, and direct macOS hook benchmarks provide separate evidence. A hook observes only calls delivered by its provider; it cannot block arbitrary later writes by child processes. Copilot pre-tool timeouts are fail-open.

## Progress

- [x] (2026-09-28) [planning] Close the reopened Wayfinder decisions and revise this ExecPlan and windows-live-check.md before source work.
- [ ] [approval] Obtain the user's explicit approval of the completed revised plan before source changes.
- [ ] [milestone-17] Require stable RTK and migrate warning suppression; retire verified owned prerelease assets.
- [ ] [milestone-18] Retire maintained repository-state hook pieces and adjust Git guidance.
- [ ] [milestone-19] Retire maintained global Markdown Health pieces while preserving OKF lint.
- [ ] [milestone-20] Run repository-local OKF lint at turn end on three CLIs.
- [ ] [milestone-21] Show sparse operational lifecycle messages.
- [ ] [milestone-22] Explain exact safe Tool Guardian violations.
- [ ] [milestone-23] Inventory, measure, review, and improve retained high-rate hooks on macOS.
- [ ] [milestone-24] Pass integrated source, temporary-home installer, and native Windows automation, including the scanner HEAD-failure case.
- [ ] [milestone-25] Verify installed Codex CLI behavior.
- [ ] [milestone-26] Verify installed Copilot CLI behavior in a session with that CLI.
- [ ] [milestone-27] Verify installed Gemini CLI behavior in a session with that CLI.
- [ ] [final] Synchronize agent docs, remove obsolete references, and record final acceptance only after all required milestones pass.

Historical work: prior milestones 1-16 were accepted for the former design. They established read-only orientation, file-first PowerShell guidance, three-file disposable-probe guidance, provider hook transport, bounded scanner capture, security banners, the now-retired repository-state and Markdown hooks, prerelease RTK rewriting, integrated tests, provider live probes, and review repairs. This revision does not reopen those completed facts or count their old acceptance as proof of the new behavior. A later scanner regression added a native Windows committed-repository HEAD-failure case that remains unverified here. Six blocked repair-branch deletions are separate historical housekeeping for a reviewed user-run Git command, not a hook acceptance gate.

## Surprises & Discoveries

- Stable RTK 0.50.0 has a persistent hooks.suppress_hook_warning setting. The user has already upgraded this Mac's PATH RTK. The former pinned prerelease launcher is no longer needed for this warning.
- The old Markdown Health hook used its own workspace checker. scripts/lint-okf.py is separate and remains useful for canonical agent documentation.
- Gemini AfterModel observability may run once per streaming chunk, faster than per-tool hooks. The previous approximately 6-7 ms Gemini probe measured handler entry-to-completion, not process startup or full provider latency. No new benchmark has run.
- Current Tool Guardian reduces limit failures to input_limits/critical and discards the specific bound. The allowlist cannot bypass input limits. New messages must preserve secret redaction while exposing safe limit metadata.
- Another machine may still run old user-level repository-state or Markdown Health registrations after source retirement. Their installed files and state directories are left for manual cleanup. Fresh-install acceptance cannot prove every old installation is clean.
- Prior Copilot CLI timeout probing showed a harmless Git read proceed after a one-second pre-tool timeout without a native timeout message. Treat visible progress as informational, not proof of enforcement.
- Native Windows scan-secrets HEAD-failure proof remains open. A macOS PowerShell skip is not native Windows evidence.

## Decision Log

- Decision: Keep completed former milestones as compact history and add new numbered milestones with independent acceptance.
  Rationale: Old results remain traceable without implying they prove revised behavior.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Require explicit user approval of this revised plan and the Windows checklist before source implementation.
  Rationale: The user required planning to finish before implementation restarts.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Migrate stable RTK and retire obsolete hooks first; add OKF and visible messages; refine Tool Guardian; measure the final high-rate hook set; finish with platform and live checks.
  Rationale: Each later gate can inspect the registrations that will actually remain.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Keep Copilot and Gemini functional live checks in separate later milestones. Run the performance audit by directly executing scripts on macOS, with no live CLI timing gate.
  Rationale: The CLIs are absent on this Mac, while direct process timing measures the hook cost under review.
  Date/Author: 2026-09-28, user and Codex.
- Decision: Leave old installed repository-state and Markdown Health copies and state for manual cleanup. Preserve audit history. Remove only verified owned prerelease RTK assets.
  Rationale: Unknown or modified user files must not be deleted by migration.
  Date/Author: 2026-09-28, user and Codex.

## Outcomes & Retrospective

Planning decisions are complete. Revised implementation acceptance is not met: no new source, installed-hook, RTK configuration, or benchmark change has run. Prior provider and Windows results are historical evidence for the old design. The next action after user approval is milestone 17. Keep this section current after every milestone and name any unmet live or native Windows gate.

## Context and Orientation

Start in the repository root shown by git rev-parse --show-toplevel. Inspect status, staged and unstaged diffs, and untracked paths before changing files. Before edits, read .agents/memory/INDEX.md, then ARCHITECTURE.md and CONVENTIONS.md for nontrivial work, then each affected .agents/instructions area and matching known-issues/testing file. Use the repository tdd skill for source changes. Run update-agent-docs once at the end of each implementation work session, after all related tasks are done. Do not add dependencies without authorization. Never weaken a failing test. Do not write regression tests solely for feature deletions.

The three installed instruction sources are .copilot/copilot-instructions.md, .gemini/GEMINI.md, and .codex/AGENTS.md. The installers are scripts/install.sh and scripts/install.ps1. Canonical generated hook policy is under hooks/families/; hooks/manifest.py and hooks/providers.py describe outputs. Run python3 scripts/generate-hooks.py --write after source changes, then --check and scripts/test-generate-hooks.py. Do not hand-edit a generated provider script. Copilot user-level source is .copilot/hooks/, Gemini user-level source is .gemini/, and Codex user-level source is .codex/global-hooks.json plus .codex/hooks/. The Codex merger, scripts/install-codex-hooks.py, must preserve unrelated user hooks. Repository-local Copilot hooks are in .github/hooks/. The new Codex repository hook belongs in .codex/hooks.json and must not be installed globally.

A provider envelope is the JSON request and response for one hook event. Copilot CLI uses sessionStart, preToolUse, postToolUse, and agentStop. Gemini uses SessionStart, BeforeTool, AfterTool, AfterAgent, SessionEnd, and AfterModel. Codex uses SessionStart, PreToolUse, PostToolUse, and Stop. Provider versions may differ. Keep stdout to one valid final JSON response, except documented Copilot progress messages. Expected allow, warn, and deny control flow exits 0. Windows Copilot command hooks need powershell, and Codex uses commandWindows. Do not infer native display from an isolated stdin/stdout test. User-level cloud Copilot and VS Code Local or Copilot Agent Host are outside the new lifecycle and OKF live gates. Retain provider-envelope compatibility where already tested.

Use safe disposable repositories and fake data for security examples. Keep logs and transcripts outside scanner fixtures so they do not become scanned candidates. Keep permanent tests in tracked source; place probes in .agents/scratchpad/ or operating-system temp and remove only exact created files. For a real-home install, first run source and temporary-home tests, inspect destination changes and backup paths, then review provider hook trust. Do not bypass trust.

## Plan of Work

### Milestone 17: Move warning suppression to stable RTK

Status: open
Acceptance: not met

Require RTK 0.50.0 or newer before either installer changes installed files. Do not download RTK. In scripts/install.sh and scripts/install.ps1, locate the user RTK TOML config at the platform location: macOS Library/Application Support/rtk/config.toml under the home directory, Linux .config/rtk/config.toml under the home directory, or Windows APPDATA/rtk/config.toml. Set only hooks.suppress_hook_warning to true. Preserve all other settings and comments where possible, back up a changed file, leave a correct file byte-identical, and stop safely on ambiguous or malformed config. An older or missing RTK stops the installer before any destination mutation and prints upgrade guidance.

Keep the Copilot and Gemini automatic RTK forwarders and their registrations. They call rtk hook copilot or rtk hook gemini for automatic filtering; the Copilot forwarder also maps RTK's ask to allow. Remove the pinned prerelease downloader scripts/install-rtk-prerelease.py, receipt/provenance route, explicit-command adapters, launchers, their generated targets and registrations, owned-file lists, obsolete tests, and old documentation from hooks/families/rtk.py, hooks/manifest.py, provider configs, and installers. Remove an installed prerelease asset only after exact repo ownership and content or receipt verification; leave unknown or modified files for manual review. Add scripts/test-rtk-stable.py and scripts/test-rtk-stable-windows.ps1 to test idempotent config migration, backups, malformed config, missing/old RTK preflight, POSIX and Windows paths, and clean installs with no stale registration. Exercise explicit RTK success and missing-file calls: the false notice is absent, while other stderr, stdout, argv effects, and exit codes remain. Test automatic forwarders separately.

### Milestone 18: Retire maintained repository-state enforcement

Status: open
Acceptance: not met

Remove hooks/families/repository_state.py, its three generated provider scripts, manifest targets, Copilot/Gemini/Codex registrations, installer ownership entries, dedicated tests, and aggregate test or workflow references. Preserve shared audit infrastructure and unrelated hooks. Do not add deletion regression tests. Update AGENTS.md Git protection text: keep the direct .git edit ban and review before destructive Git commands, but remove instructions that depend on a repository-state hook blocking them. Do not claim instructions prevent arbitrary writes.

Do not automatically remove old installed scripts or registrations. Document their likely locations and manual cleanup; they can keep running on another machine. Inspect source registrations, generator output, both installers, and fresh temporary-home installations for absence of the retired guard. Keep the change isolated so retained hooks still run. The acceptance claim applies to checked-in source and fresh installations.

### Milestone 19: Retire global Markdown Health

Status: open
Acceptance: not met

Remove hooks/families/markdown_health.py, its generated Copilot/Gemini/Codex scripts, manifest targets, maintained user-level pre/post/stop registrations, installer copy and ownership rules, and dedicated tests or aggregate references. Preserve scripts/lint-okf.py and its tests. Preserve existing audit.log history and dedicated markdown-health-state directories. Do not automatically remove installed old hook files or registrations; document them for manual cleanup and state clearly that they may still execute. Do not add deletion regression tests.

Inspect checked-in source, generated targets, registrations, installers, and a fresh temporary-home installation. Show that the old checker is absent and unrelated hook groups remain. This source and fresh-install proof does not certify older user installations.

### Milestone 20: Validate repository OKF at turn end

Status: open
Acceptance: not met

Keep scripts/lint-okf.py as the only OKF rule authority. It checks canonical Markdown under .agents/instructions/ and .agents/memory/, exiting 0 for pass, 1 for findings, and 2 for infrastructure failure. Keep Copilot's repository-local agentStop adapter through .github/hooks/scripts/validate-stop.py and Gemini's repository-local AfterAgent adapter under .gemini/hooks/scripts/lint-okf.py. Remove only redundant Copilot postToolUse and Gemini AfterTool OKF registrations. Add a repository-local .codex/hooks.json Stop command and self-contained adapter, never a user-global Codex registration. If installed provider versions or worktree rules differ, record the observed limit and keep acceptance open.

Validate the full canonical OKF tree once per turn-end attempt. Report pass, definite findings, or incomplete with provider-valid, bounded JSON. Give the agent one repair attempt after a definite finding; on the next stop attempt permit completion with visible unresolved findings. A checker crash, timeout, or malformed output is incomplete and must not strand the turn. Emit one audit.log line per nonempty validation batch with outcome, safe counts, and sorted workspace-relative checked paths. Cap the physical line at 4 KiB, show omitted-path count, suppress identical repeated stop events, and keep content, link targets, and diagnostic text out. An audit-write failure warns without changing the lint decision.

Extend scripts/test-hooks-okf-lint.sh and scripts/test-gemini-hooks-okf-lint.sh, and add scripts/test-codex-repository-okf.sh and scripts/test-repository-okf-windows.ps1. Use public envelope tests for pass, findings, incomplete, first block, allowed second stop, repeated stop deduplication, path and output caps, nested-worktree resolution, and Windows path behavior. Verify no post-tool OKF entry and no user-global copy. Run scripts/test-okf-lint.sh for the independent central linter. Installed native message proof belongs to milestones 25-27; Windows automated behavior belongs to milestone 24.

### Milestone 21: Show sparse lifecycle messages

Status: open
Acceptance: not met

For local Copilot CLI, Gemini CLI, and Codex CLI only, make each retained operational low-rate startup or turn-end hook report one short native message with hook name, outcome, and safe count when useful. Show every stop attempt, including a repair retry; do not add a turn-end coordinator. Ordinary success lines contain no path, command, or document content. SessionEnd success, telemetry-only hooks, and the completion bell stay silent. High-rate pre/post-tool passes stay silent, while a block, warning, incomplete result, or meaningful change appears immediately.

Use provider-native message fields, keep stdout JSON-only, and avoid a second display when the provider already shows a denial reason. Existing Tool Guardian and scanner logs plus RTK observability traces supply high-rate run evidence; do not add one RTK audit line per call or claim one shared audit log covers every hook. Add scripts/test-lifecycle-messages-windows.ps1 and focused provider-envelope cases for startup pass, turn-end pass/fail/incomplete, repeated stop, tool pass silence, block/warn visibility, message bounds, and safe counts in provider envelopes. Native CLI display proof is in milestones 25-27. The new repository OKF hook follows this policy.

### Milestone 22: Explain Tool Guardian violations

Status: open
Acceptance: not met

Edit canonical hooks/families/tool_guard.py and regenerate provider outputs. Retain a safe rule identifier and cause when building threats instead of reducing each finding to category/severity. Show up to three distinct reasons and an omitted count while preserving blocked versus warning wording, severity, safe action name, and one redacted Action excerpt of at most 160 characters. For an input limit, identify the exact limit, configured threshold, and measured count with its true unit when available. Name a provider field such as write_file.content only from a trusted known-field list; otherwise say tool input. For known inspection failure, state only a safe cause and keep fail-closed behavior. Do not echo exception text, arbitrary keys, raw input, or matched secrets.

Do not tell an agent to adjust TOOL_GUARD_ALLOWLIST for input limits, since that setting cannot bypass them. Reuse an existing static suggestion only when accurate and simple; no new remediation engine is required. Guard logs must contain the same safe rule IDs, limit/count detail, and identical redacted Action excerpt shown to the agent, with no raw input. Extend the Copilot/Gemini Tool Guardian suites and add scripts/test-codex-hooks-tool-guard.sh to test scan-size, segment, token, depth, node, string, and byte limits; dangerous-operation rules; multiple findings; known/unknown fields; inspection failure; block/warn; log alignment; and redaction. Use public Copilot, Gemini, and Codex envelopes plus native display in the later live milestones. Preserve the prior scan-secrets generic message rule: no matched value in its banner.

### Milestone 23: Measure and improve every retained high-rate hook

Status: open
Acceptance: not met

After milestones 17-22 fix the final hook graph, enumerate every retained handler called per tool or faster across three providers. Include security, RTK automatic forwarding, no-op paths, observability telemetry, and Gemini AfterModel streaming chunks. Record provider, source scope, event, matcher, executable, and expected call rate. On macOS, invoke each entrypoint directly with representative provider JSON and environment. Include clean, finding, failure, repeated, large-input, and concurrent workloads. Measure whole subprocess wall time, including Python startup, input/output, synchronous logging, and message creation. Where practical, measure handler-only time separately and compare a minimal process control and previous handler version. Report cold and warm median, p95, variation, and unisolatable cost.

Set numeric budgets only after the baseline shows noise and configured timeout headroom. Review redundant launches, parsing, scans, disk sync, locks, and unbounded work. Fix clear redundant or reproducibly slow hot paths and rerun exact scenarios. Never remove a security check, weaken fail-closed behavior, or suppress needed diagnostics for speed. Record before/after measurements, units, environment, sample count, risk, and remaining cost. This milestone requires no live provider CLI or Windows benchmark.

### Milestone 24: Prove integrated source and native Windows behavior

Status: open
Acceptance: not met

Regenerate all maintained targets and run the generator's check and parity tests. Run affected public hook suites, scripts/test-all.py where it provides distinct integration proof, and Bash and PowerShell temporary-home installer tests. Verify both installers preserve unrelated settings, stop before mutation on preflight failure, keep owner-only permissions, and install only current maintained handlers. Check no repository-state, global Markdown Health, or prerelease RTK registration appears in a fresh home. Verify the new repository Codex OKF registration stays in the checkout. Update README.md, the three provider instruction sources, .agents/instructions/hooks.md, relevant script guidance, and the .agents file, API, testing, and known-issue maps to describe the retained hook set. Review all changed source and docs for obsolete claims.

Update .github/workflows/ready-ideas-windows.yml and windows-live-check.md for the current hook set. Provision stable RTK on the Windows runner with the official winget package rtk-ai.rtk before installer tests, then verify rtk --version is at least 0.50.0 and rtk gain identifies Rust Token Killer. Keep the repository installers free of RTK download logic. Remove obsolete deletion-only suites from the workflow and run scripts/test-rtk-stable-windows.ps1, scripts/test-repository-okf-windows.ps1, scripts/test-lifecycle-messages-windows.ps1, and existing current-hook Windows tests. Run the existing native Windows scripts/test-scan-secrets-windows.ps1 committed-repository HEAD-failure case: an unexpected rev-parse failure must be incomplete, not clean; a genuinely unborn branch must still work. A macOS skip does not satisfy this gate. Windows automation plus a documented live-check procedure is required; a live Windows provider run is not the completion gate. Do not fabricate a pass if a runner is unavailable.

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

Planning inputs are the closed decision tickets under docs/ready-ideas-execplan/tickets/ and the provider facts in its research directory. This plan embeds their executable requirements, so an executor need not read the tickets to know the target behavior. The prior implementation reached c0d9ca34 and passed old source/provider tests and live Copilot, Gemini, and Codex probes. Its scanner HEAD-failure native Windows extension still needs proof. The old prerelease RTK and retired hooks are checked in as of this revision; no new behavior is claimed.

Capture concise evidence after execution: RTK version and config backup path without private contents; an explicit missing-file RTK exit; current registration lists; one safe OKF audit line with counts; a redacted Tool Guardian reason and matching log fields; per-handler timing distributions; native Windows scanner HEAD-failure result; and provider-visible messages. Do not paste raw tool input, credential values, entire logs, or private home paths unnecessarily. The Windows checklist is docs/ready-ideas-execplan/windows-live-check.md.

## Interfaces and Dependencies

Canonical generated hook families expose render(provider, target) through hooks/families/, hooks/providers.py, and hooks/manifest.py. Generated scripts must be self-contained at runtime and output provider-valid JSON; they must not import another provider's installed files. scripts/install-codex-hooks.py owns exact maintained command identities, not whole user event groups. A repository-local .codex/hooks.json is separate from the user-global .codex/global-hooks.json template. Keep Copilot bash/powershell command alternatives, Codex commandWindows, and Gemini millisecond timeout units.

RTK stable 0.50.0 or newer is an external prerequisite, not installed by this repository. Python standard-library code and existing scripts supply the hook behavior; no new package, database, or service is planned. Existing scan-secrets file-backed Git capture remains a security boundary and must return complete output or a typed incomplete result, never partial bytes. The OKF adapter calls scripts/lint-okf.py rather than copying its rules. Tool Guardian uses safe structured rule metadata and the prior redacted Action formatter; no provider runtime imports another provider's code.

Revision note, 2026-09-28: The user replaced the old prerelease and guard/checker outcomes, requested lifecycle visibility and high-rate performance review, then added exact Tool Guardian causes. This revision compresses old milestones, adds new gates, and removes old-design implementation instructions. Source work waits for explicit approval of this plan and the updated Windows checklist.
