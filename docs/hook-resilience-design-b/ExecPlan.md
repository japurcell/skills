# Keep editing available and scan at explicit checkpoints and Git gates

This is the active Design B ExecPlan at `docs/hook-resilience-design-b/ExecPlan.md`. Maintain it according to [exec-plans](../../.agents/skills/exec-plans/SKILL.md). Written on 2026-10-15 against repository revision `9e5f88950cda434600bad7051362588296fea33d`. Implementation is authorized by the 2026-10-15 `execplan-implement` request. Work proceeds on `codex/hook-resilience-design-b`, starting from `1cbe2cdf162b823b5f331f002a93464a0a1adca0`. Source changes, isolated fixtures, private task branches, and implementation commits are authorized. Real-home deployment, hook enablement/trust changes, and publication remain separate owner actions.

## Purpose / Big Picture

A secret-scanner failure must no longer prevent an agent from reading files, repairing a merge, or finishing its turn. Tool Guardian continues checking each requested operation. Secret scanning runs synchronously only when a person or agent explicitly requests a checkpoint, or when configured Git hooks check a commit or push. A failed Git gate stops that Git action; it does not lock the rest of the agent session.

End Turn reports the last saved scan result, its scope, and its time. It never starts a scan, waits for one to finish, resumes one, or requests another agent turn. There are no background checkpoints, scheduled scans, filesystem watchers, workers, daemon processes, automatic scan retries, or cached permissions to publish.

The plan includes only retrospective candidates 1-3: verified fixture-patch preflight, macOS security CI, and the scanner/Guardian mode-helper contract. It also includes the five accepted adversarial findings: installed registration retirement, exact outgoing transaction inputs, correct CLI exit semantics, LFS upload ordering and content coverage, and publication-specific capacity. The retracted commit-message-hook race is not a requirement or a verified defect.

Success is observable in a disposable repository: reproduce the large merge and binary workloads; inspect and repair them; end the turn normally; explicitly scan; reject a commit or push containing a fake secret; repair the relevant content or history; retry successfully. No step requires disabling protection or misreporting an incomplete scan as clean.

## Progress

- [x] (2026-10-15) [execution] E0: Create clean base branch `codex/hook-resilience-design-b` from the committed plan at `1cbe2cdf`; verify RTK 0.51.0, Python 3.14.6, Git 2.54.0, PowerShell 7.6.7, and jq 1.7.1. Git LFS is absent on PATH and must be supplied before LFS acceptance.
- [x] (2026-10-15) [planning] P0: Inspect the reports, retrospective candidates, current source and installers, prior implementation evidence, repository rules, and the three saved CLI design sources. Write this implementation contract. No runtime changes made.
- [x] (2026-10-15) [execution] E1: Confirm all public test seams with the user and dispatch independent D0/T1/T2 work. Retain the routing/runtime audit in [delegation.md](delegation.md).
- [ ] [milestone-1] D0: Prove the publication transaction, LFS delivery, supported capacity, and installation interfaces in disposable feasibility fixtures; record the concrete limits and supported platform matrix.
- [ ] [milestone-1] T1: Deliver retrospective candidate 1, the public fixture-patch preflight CLI and its check/apply behavior.
- [x] (2026-10-15) [milestone-1] T2: Deliver retrospective candidate 3, all 12 mode-helper cases and both mutation controls. Integrated at `45401b4789ba9071d6cf90b435fed8bfd8722c51`; [evidence](t2-evidence.md). Full recovery: 15 methods pass. Both assignment-removal controls fail all six corresponding cases.
- [ ] [milestone-1] I1: Verify the preparation tools together without mutating live hooks or the user's pending work.
- [ ] [milestone-2] T3: Extract the result-producing scan engine and deliver the checkpoint CLI with compatibility evidence.
- [ ] [milestone-2] T4: Deliver bounded saved-status storage and the read-only status CLI.
- [ ] [milestone-2] I2: Verify CLI, scan-result, cancellation, capture, and status contracts together.
- [ ] [milestone-3] T5: Deliver staged and outgoing publication collectors through the gate CLI.
- [ ] [milestone-3] T6: Deliver verified LFS content acquisition and scan-before-upload composition.
- [ ] [milestone-3] T7: Deliver explicit repository gate installation, hook composition, and recovery.
- [ ] [milestone-3] I3: Exercise actual commit/push operations against local disposable endpoints, including first publication and blocked LFS transfer.
- [ ] [milestone-4] T8: Deliver provider metadata handling, status-only lifecycle adapters, and exact installed registration retirement.
- [ ] [milestone-4] I4: Verify old-install upgrades and actual permitted repair operations through the new integrated registrations.
- [ ] [milestone-5] T9: Deliver retrospective candidate 2, macOS CI and explicit native capture execution evidence; extend native Windows checks for the new interfaces.
- [ ] [milestone-5] V1: Run integrated functional, capacity, installation, CLI-design, and platform checks; record real CI and authorized host-delivery evidence separately.
- [ ] [milestone-5] K1: Complete one coordinated knowledge-maintenance pass and reconcile documentation with the implemented behavior.

## Context and Orientation

Run repository commands from the repository root, currently `/Users/adam/.codex/worktrees/a468/skills`. Use RTK as required by `AGENTS.md`; use `rtk proxy` when output or subprocess behavior must remain exact. Read [instruction routes](../../.agents/instructions/INDEX.md), [script rules](../../.agents/instructions/scripts.md), [hook rules](../../.agents/instructions/hooks.md), [security rules](../../.agents/instructions/hooks-security.md), and the matching provider/testing branches before implementation. Preserve unrelated staged, unstaged, and untracked work.

A **worktree** is the current set of checked-out files. The **index** contains the versions selected for the next commit; it can also hold several versions of an unresolved conflict. A **Git object ID** names immutable stored Git content. A **gate** is a synchronous check run before a configured Git action proceeds. **LFS** stores large-file payloads outside ordinary Git blobs; a Git blob often contains only a pointer to that payload. A **checkpoint** is an explicit request for feedback about pending changes. A **saved status** is an informational report from a past scan, not permission to commit or push.

The canonical scanner renderer is [hooks/families/scan_secrets.py](../../hooks/families/scan_secrets.py). It owns `main`, `collect_files`, `SnapshotSource`, `ScanBudget`, Git capture, provider response selection, and the exact diagnostic matcher. Matching and reports also use `hooks/families/scanner_stream.py`, `allowlist.py`, `reporting.py`, `audit.py`, and `common.py`. [Tool Guardian](../../hooks/families/tool_guard.py) owns requested-operation policy. [Diagnostics](../../hooks/families/diagnostics.py) owns the standalone diagnostic command.

The generator and [manifest](../../hooks/manifest.py) emit provider-local files under `.codex/hooks/`, `.copilot/hooks/scripts/`, and `.gemini/hooks/scripts/`. Edit canonical source, regenerate, and check parity; never hand-edit generated outputs. Preserve [ADR 0004](../adr/0004-generated-provider-hooks.md): generated provider runtimes must not import another provider's files.

The relevant configuration templates are `.codex/global-hooks.json`, `.copilot/hooks/hooks.json`, and `.gemini/global-settings.json`. The mergers are `scripts/install-codex-hooks.py:merged_config` and `scripts/install-provider-hooks.py:merge_hooks`; both platform installers call them. The proposed Git gates are a new installation surface and are not present merely because provider hooks are installed.

Reuse `scripts/scanner_test_support.py`, `scripts/test-hook-diagnostic-recovery.py`, and the maintained scanner/capture suites. `scripts/test-all.py` has an explicit suite registry and no subset flag. Existing shell scanner suites already invoke capture tests. The checked-in CI workflow is `.github/workflows/ready-ideas-windows.yml`; macOS needs a separate job.

## Surprises & Discoveries

The current scanner retains aggregate limits of 8,388,608 candidate bytes, 256 snapshots, 8,388,608 Git output bytes, and eight seconds. The earlier [implementation plan](../hook-resilience/implementation-ExecPlan.md) removed a per-file limit and improved streaming, but explicitly retained the aggregate limits. Its passing results establish behavior within that envelope, not resolution of the later incidents.

The [image incident](../ideas/archive/hook-failures.md) reports six PNGs totaling 20,026,474 bytes. Its checkout-version observations describe that historical checkout, not today's source. A prior diagnostic experiment in this conversation recreated the workload size with synthetic binary files, not the original images. The [merge incident](../ideas/archive/hook-failure-repair.md) identifies commits `e5c2be2095ba30626559adae7fb2c49ba691734e` and `5f3948c92e5037fb066321e9c9e5b03419410671`. The conversation's disposable replay counted 223 snapshots and 9,453,698 bytes and reproduced the reported 8,403,665-byte reservation failure. Those observations must be captured in repeatable implementation fixtures before being used as acceptance evidence; the original incident state/log was not recovered.

Scanning currently depends on pending repository state rather than the requested operation. The same unchanged incomplete result can therefore block a read and a Stop callback. The previous repair test writes a correction outside the guarded tool path; it does not prove that an agent can perform the repair itself.

The adversarial review's installer finding was reproduced in this conversation by removing scanner entries from copied templates and calling the real merger functions. Copilot retained `preToolUse` and `sessionEnd`; Gemini retained `BeforeTool` and `SessionEnd`; Codex retained `Stop`. Both mergers visit replacement events only, and the Copilot/Gemini merger derives ownership from replacement handlers. A template edit alone cannot perform this migration.

Current provider scanner denials deliberately exit zero because the host interprets JSON. Skipped/non-repository paths can also exit zero. Those process results must never be reused as Git gate authorization. A reviewed commit-message-hook race was retracted after a real Git experiment contradicted it; do not repeat that claim.

Execution baseline on 2026-10-15: `generate-hooks.py --check` passed (38 files), the existing overflow-failure reproducer passed (one test, 0.783 s), and the aggregate suite registry was listed successfully. These confirm the existing contract, not the replacement design. Git LFS is missing from PATH and D0 must resolve or retain that prerequisite.

Current `RecoveryTests.launch` explicitly sets both `SCAN_MODE` and `GUARD_MODE`. Candidate 3 protects this existing correction; it is not a request to rediscover or reapply a missing assignment.

## Decision Log

- 2026-10-15: Adopt the user's selected Design B with no background checkpoints. Scanning remains synchronous and explicit, except for automatic configured Git gates. Saved status is informational only.
- 2026-10-15: Keep Tool Guardian's fail-closed requested-operation policy. Remove only the secret scanner's universal tool/lifecycle enforcement after the replacement and migration proofs pass. Independent OKF, startup, and other user hooks retain their contracts.
- 2026-10-15: Enforce complete-clean at configured commit/push gates. Pre-commit provides early staged-content feedback; pre-push independently checks the immutable publication transaction. Do not claim a universal commit-construction guarantee from ordinary pre-commit.
- 2026-10-15: Publication checks cover relevant history and LFS payloads before upload-capable hooks run. Local hooks remain bypassable. CI runs after upload and cannot establish that no secret reached a remote. This is accidental-publication protection within configured Git workflows, not universal shell/MCP/network data-loss prevention.
- 2026-10-15: Give Git enforcement a provider-neutral CLI and preserve provider JSON adapters separately. No gate may inherit `SCAN_MODE=warn`, `SKIP_SECRETS_SCAN`, or an ambient allowlist as permission to proceed.
- 2026-10-15: Resolve numeric scan budgets through D0 measurements before activation. Preserve finite limits and explicit incomplete results. Do not assume increasing only the old 8 MiB constant solves publication workloads.
- 2026-10-15: Use the CLI rules below as acceptance criteria for every new CLI. Where saved sources conflict, prefer the repository's stdout/stderr rule and security redaction over generic advice to print raw child stderr or full debug tracebacks.
- 2026-10-15: Archive the two promoted idea reports with link repair, as required by repository workflow. Keep their historical evidence and the earlier resilience plan; neither authorizes this implementation or live deployment.

## Target Behavior and Interfaces

### B1. Runtime triggers and End Turn

The runtime call tree is:

```text
read/edit/repair tool call
  Tool Guardian -> requested operation, if permitted

scan-secrets check --scope worktree
  capture pending snapshots -> scan -> save report -> print result

git commit
  installed pre-commit dispatcher -> scan-secrets gate pre-commit
  complete-clean permits the configured commit workflow

git push
  installed pre-push dispatcher -> scan-secrets gate pre-push
  complete-clean permits downstream hooks/LFS and then Git transfer

End Turn
  scan-secrets status --json --no-input
  show last result/scope/time or unavailable -> finish
```

The status adapter has a one-second outer deadline, including process cleanup. It may perform bounded repository-location metadata discovery and a bounded status-file read, but no Git subprocesses, index enumeration, file-content inspection, scan-engine import/startup, remote I/O, or waiting for another scan. Ordinary read errors, no record, invalid records, and timeout produce a short unavailable/not-scanned message and a successful native nonblocking response. Repeated callbacks remain nonblocking, irrespective of `stop_hook_active`. No response instructs the model to run a checkpoint automatically.

Use Codex `Stop`, Copilot CLI `agentStop` (and its documented VS Code event mapping where supported), and Gemini `AfterAgent` for informational turn-end adapters. `sessionEnd`/`SessionEnd` is not an interchangeable turn-end event. Retire the old scanner there rather than claim it supplies turn-end feedback. Verify display-only output against the saved raw provider references and current official/deployed contracts. If a host cannot display safely without continuation, omit that display and retain the manual `status` command; record the capability limit. Do not emit a block/deny/retry decision to make a message visible. Keep unrelated stop validators unchanged.

Provider metadata parsing must validate documented optional outer fields separately from executable tool arguments. In particular, validate the current Codex `model`, `permission_mode`, nullable `transcript_path`, and `turn_id` shapes against current official docs before extending diagnostics. Do not broaden the exact executable diagnostic request or grant arbitrary command exemptions. Unknown or invalid executable fields retain Guardian's strict path.

### B2. Scanner module and packaging

Extract a provider-neutral result-producing module into proposed normal Python modules under `hooks/runtime/`: `scan_engine.py` for matching/result composition, `scan_git.py` for protected snapshots and publication enumeration, and `scan_status.py` for informational reports. Keep existing canonical matching/reporting behavior in one maintained source; move it rather than fork it. Existing renderers may compose or copy these sources into provider-local helper packages through explicit manifest targets. The generator must include every new source dependency in freshness/build identity and emit deterministic imports. Preserve provider-local runtime independence.

Add the public standalone entrypoint `scripts/scan-secrets.py` and shared CLI parsing under `hooks/runtime/scan_cli.py`. Source invocation is `rtk proxy python3 scripts/scan-secrets.py ...`; the installed alias is `scan-secrets ...`. Add `scripts/install-scan-secrets.py` to package the entrypoint and its exact runtime dependency closure into a provider-neutral installed bundle. Both `scripts/install.sh` and `scripts/install.ps1` deploy it consistently. The CLI must not depend on a particular provider directory or on the source checkout after installation. Windows gets a tested native launcher; Git dispatchers invoke the recorded absolute interpreter and entrypoint directly, not a PATH lookup. Retain isolated Python startup `-I -S -B` and explicitly load only bundled runtime modules.

The engine's small public interface is conceptually `scan(snapshot, policy, budget) -> ScanResult`. `ScanResult` has schema/build/policy versions, a scope identity, `complete_clean | complete_findings | incomplete`, a separate coverage-complete flag, bounded redacted findings, counts, elapsed time, a reason code, and audit/status persistence outcomes. An interrupted/failed scan can retain known findings while remaining incomplete. Do not confuse zero reported findings, truncated reporting, or failed inspection with clean coverage.

Preserve protected temporary captures, stable object/spooled-file reads, full logical token matching, binary ASCII projection, exact suppression semantics where explicitly supported, safe bounded reports, descendant cleanup, and independent audit outcome. Worktree collection is not globally atomic; detect supported drift and report coverage honestly rather than certify a later filesystem state. Publication uses immutable object IDs. Do not reopen a mutable path after capturing it for the decision.

### B3. Proposed CLI contract and source-derived design requirements

These commands are design targets, not available commands at plan creation:

```text
scan-secrets --help
scan-secrets --version
scan-secrets help check
scan-secrets check --repo PATH --scope worktree|index [--json] [--budget-file PATH]
scan-secrets status --repo PATH [--json]
scan-secrets gate pre-commit --repo PATH
scan-secrets gate pre-push --remote NAME --url URL
scan-secrets hooks install --repo PATH [--budget-file PATH] [--dry-run]
scan-secrets hooks uninstall --repo PATH [--dry-run]
```

`--repo` defaults to the current directory for user commands; dispatchers supply the repository context explicitly. Gate pre-push reads Git's ref-update records from stdin. It never guesses the transaction from HEAD, upstream, or a cached remote-tracking branch. It rejects interactive stdin immediately with usage guidance and bounds input bytes, records, parsing time, and trailing malformed data. A verified empty update stream is a complete empty transaction, distinct from malformed or unavailable input. Help/version never read stdin, resolve Git, load policies, or mutate files.

Check defaults to `worktree`. `worktree` retains current pending-change semantics, including required conflict versions and untracked content. `index` scans the selected staged versions in full and refuses an unresolved index. Publication is exposed through `gate pre-push`, not a misleading bare `--scope outgoing` that lacks a transaction. There is no watch, background, retry, force-clean, skip, or warning-only gate flag.

`check` and gate actions outside a Git repository fail as invalid invocation with exit `3`; they never return a successful skipped scan. `status` outside a repository may return a valid informational `not_scanned` response with reason `not_repository`. A missing report in an identified worktree is also `not_scanned`; a corrupt existing report is an error. Support the common `--json`, `--no-input`, `--quiet`, and `--no-color` options consistently, including gate actions. The installed dispatcher requests JSON explicitly and validates it before proceeding.

All new commands, including fixture preflight and installation helpers, must meet the following acceptance requirements derived from immutable local sources:

| Contract | Source and application |
| --- | --- |
| Discoverable help and names | [clig.dev](../../.agents/sources/clig-dev.md), Help, Arguments and flags, Subcommands; [12 Factor CLI Apps](../../.agents/sources/12-factor-cli-apps.md), factors 1-3 and 11; [Thoughtworks](../../.agents/sources/cli-design-guidelines.md), structure/help/expressive flags. Use standard-library `argparse`, descriptive kebab-case flags, `-h`/`--help` at every level, `help COMMAND`, `--version`, and examples explaining worktree/index/publication. No-argument invocation prints concise help and performs no scan or installation. Reject unknown options and abbreviations; never autocorrect into execution. |
| Predictable streams | clig.dev Basics/Output and 12 Factor factor 4. Primary results go to stdout; errors, progress, and warnings go to stderr. `--json` produces exactly one versioned JSON object with no banners, ANSI, progress, or raw child output mixed in. Normal text is concise and understandable to a novice. |
| Automation and explicit actions | clig.dev Interactivity/Output and Thoughtworks implicit-steps/prompts guidance. Support `--no-input`; no prompts in gates, provider adapters, JSON mode, or non-TTY execution. Installation, uninstallation, and patch application are explicit actions. `--dry-run` must describe intended changes without writing configuration, reports, backups, or hook files. Never install, fetch, upload, or update automatically as a side effect of check/status/help. |
| Truthful exit and error contracts | clig.dev Basics/Errors and 12 Factor factor 5. Use the exit table below; include a stable safe reason code, phase, actual limit/measurement/unit where relevant, and a concrete repair action. Findings and incomplete results are distinct. Do not copy arbitrary exception strings, subprocess stderr, credentials, token values, or credential-bearing remote URLs into output. |
| Terminal behavior | clig.dev Output and 12 Factor factor 6. Text progress, if needed, goes to stderr at a bounded rate. Respect each stream's TTY state, `NO_COLOR`, `TERM=dumb`, and `--no-color`. No decorative output in pipes or JSON. `--quiet` suppresses nonessential human success/progress only, not errors or the requested JSON result. |
| Cancellation and bounded waits | clig.dev Robustness/Signals. Ctrl-C cancels the scan and its children promptly, cleans up within a finite deadline, and cannot leave permission to publish. Broken output pipes do not dump tracebacks or turn a failed gate into success. Required subprocess and filesystem waits are bounded. |
| Stable configuration and versions | clig.dev Configuration/Future-proofing and 12 Factor factor 12. Document every accepted setting, defaults, units, bounds, and precedence. Version JSON schemas and policy/build identities. No implicit `.env` loading, network update checks, arbitrary prefix aliases, or fallback to an incompatible schema. |

For `check` and executed `gate` actions, reserve exit `0` exclusively for complete-clean under the selected policy; `1` means complete-findings; `2` means incomplete inspection or required infrastructure failure; `3` means invalid invocation/configuration; `130` means interruption. Preserve findings alongside exit `2` when later inspection fails. Argument-parser errors must map to `3` rather than collide with incomplete scans. Provider compatibility adapters still render native JSON and exit zero where required by their host protocol; this is a separate adapter, never a Git gate implementation.

For `status`, exit `0` means a valid informational response, including explicit `not_scanned`; it does not certify content. An unreadable/corrupt record returns `2`. End Turn converts that CLI failure to a nonblocking unavailable message. Help/version, successful installation, and successful preflight use their own documented success meanings. Git dispatchers accept only the installed gate action with the expected result schema, scope/policy/build identities, and consistent success exit; a `--help` response or malformed/empty output is not a passing gate.

These CLI sources provide guidelines, not permission to weaken security. In particular, do not implement arbitrary `--force` bypasses, raw debug tracebacks containing secrets, forwarding unsanitized Git stderr, decorative notifications, or implicit remote calls. The saved Thoughtworks article places warnings on stdout; this plan deliberately follows clig.dev, 12 Factor, and repository conventions by putting them on stderr.

Use platform-appropriate user configuration/data roots, respecting standard configured locations: XDG config/data roots on Unix, appropriate Application Support/data directories on macOS, and application data directories on Windows. Keep mutable reports outside scanned worktrees and outside installed executable bundles. Installation records absolute resolved policy/data/runtime locations so gate behavior is not redirected by ambient environment changes. Expose effective safe locations and versions in help/version or diagnostics, not in every hook success message.

### B4. Saved status and trusted configuration

Write one bounded last-result document per canonical Git worktree identity, namespaced by a digest of the common Git directory and worktree Git directory. A linked worktree must not display another worktree's report. Store at most 64 KiB of allowlisted JSON per report with owner-only access, link/reparse-point checks, atomic replacement, and bounded read/write operations. Include UTC completion time, scope, snapshot/transaction digest, scanner/policy version, safe counts, coverage state, and reason codes. Exclude matched values, file contents, patches, raw errors, and credentials embedded in URLs. Keep full audit requirements separate from this small display document.

Report writes occur only as part of explicit scans or Git gate execution. A failed scan writes incomplete status when possible. A killed process can leave an older report; every display explicitly calls it the last scan and never claims freshness. Concurrent scans use atomic writes and ordered completion metadata; status is not a lock, cache, receipt, or authorization token. A display-write failure is surfaced separately and does not invent a security result. Failure of the existing required security audit still prevents clean gate enforcement.

Policy rules/build identity come from the trusted installed bundle. Resource overrides use an explicit schema-versioned owner-selected JSON budget file, not ambient skip/mode/allowlist variables or an automatically loaded repository file. The file has separate checkpoint and publication profiles containing finite positive `max_objects`, `max_candidate_bytes`, `max_seconds`, `max_capture_bytes`, and `max_temp_bytes`; allowed ranges and defaults are finalized and documented in D0. Publication stdin has a separate finite record/byte/deadline bound. Installation validates and pins the resolved configuration location; each invocation captures and validates its bytes once and includes the digest in the result. Missing, malformed, replaced-untrusted, or out-of-range gate configuration fails before upload.

The capacity recovery path is explicit: identify the reported bound, edit the owner-selected budget file within its supported range or fix the capture/storage problem, then rerun the check or Git action. `scan-secrets hooks install --repo PATH --budget-file PATH --dry-run` previews a change of configuration binding; the same command without `--dry-run` applies it. Never recommend skip, warn, disabling the hook, or excluding binary extensions as the normal recovery procedure.

### B5. Publication transaction and LFS contract

Pre-push input contains every local-ref/local-object/remote-ref/remote-object tuple and the destination arguments. Capture it once, validate OID format against the repository's object format, retain bounded original bytes for replay, and compute a transaction identity. Support non-HEAD branches, explicit OIDs, multiple refs, tags, new refs, deletions, and forced updates. Deleted refs add no content. An empty transaction performs no upload-capable downstream work beyond the documented Git no-op behavior.

Enumerate immutable objects reachable from all nonzero local tips. Only subtract objects proven already reachable from nonzero remote-old tips supplied by this same transaction, when their complete graphs are locally available. Missing remote-old history causes conservative full-local traversal, not a guessed clean baseline or a network fetch. Never subtract arbitrary local branches or stale remote-tracking refs. Missing required local ancestry/blobs, shallow truncation that prevents complete coverage, malformed objects, or unsupported object types produce incomplete. Do not lazily fetch missing partial-clone objects during inspection.

Scan every selected blob in full, including intermediate commits where a secret was later removed. Include selected commit and annotated-tag message content in the publication policy. Apply filename/path rules to every relevant tree occurrence; deduplicating identical blob bytes must not suppress distinct path-dependent rules. Disable Git replacement-object interpretation (`--no-replace-objects` or equivalent pinned environment), reject unsupported graft/shallow substitutions, and control inherited Git environment/configuration that could redirect object access or execute helpers. Do not use current worktree diff-only suppression as a publication proof.

LFS pointer parsing must be strict and bounded. Before any downstream hook can upload, obtain every relevant LFS payload locally, verify its declared size and object digest, and inspect all bytes. A missing, corrupt, oversized, or unavailable payload is incomplete. Do not automatically download it. D0 must prove how the actual LFS uploader consumes the verified immutable bytes: prefer an invocation-private verified LFS store and a controlled, pinned LFS invocation using that store. Recognition/replacement of a standard LFS upload hook must preserve its user-visible behavior and prevent a second upload from unverified storage. Unsupported custom LFS upload arrangements must be refused explicitly during installation or gate execution, not silently treated as ordinary Git blobs.

The dispatcher owns scan-before-upload ordering, stdin replay, and downstream failure propagation. Execute existing hooks only after the scanner passes; give each the original arguments and a fresh copy of the original stdin. Preserve their relative order. Verify that Git transfers the OIDs that were scanned, and that supported LFS uploads use the verified payload snapshot. If a publication path cannot bind checked bytes to delivered bytes, D0 fails for that path and the implementation must not claim it is supported. This is an explicit feasibility check, not a demand for a persistent worker or universal protection from arbitrary malicious local hooks.

The synchronous dispatcher owns the invocation's private temporary directory until scanning and downstream upload finish. The CLI's scan subprocess must not delete a verified LFS snapshot before its caller consumes it. D0 must specify and test the private handoff between those processes, including scope identity, path ownership, cleanup after cancellation, and rejection of missing or altered content. This short-lived handoff is confined to the current invocation; it is never a saved status, reusable permission, queue, or background job.

### B6. Installation and retirement

Add proposed `hooks/registrations.py` as the authoritative list of desired handlers and explicitly retired owned handler/event identities. Retirement must recognize exact trusted installed paths/command pairs and supported historical owned forms, not any command with a matching basename. Preserve unrelated handlers and settings. Ambiguous ownership stops the relevant migration with a safe diagnostic. Process both retained and removed events; leaving an event out of a replacement template must not preserve a known retired scanner.

Update both Python mergers and both platform installers. Deploy and validate replacement assets before activating registrations, retain backups of real semantic changes, and write each config atomically. Describe the ordered multi-file operation honestly: it is not globally atomic. A failed migration must retain a recognizable previous generation or a documented recoverable intermediate state and must not leave a registration pointing at missing assets. Repeating installation is idempotent. Updating an exact owned registration is the scoped policy change approved by this design; unrelated retired user registrations remain preserved.

Repository Git gates require explicit `scan-secrets hooks install --repo PATH`. Implement its filesystem/configuration work in proposed `scripts/install-repo-gates.py` using shared installation code rather than a second parser/policy implementation. Do not automatically enable gates in every discovered repository. Determine effective `core.hooksPath`, configuration origin, existing hook files, and linked-worktree scope before mutation. Use a repository-owned dispatcher directory and a local configuration binding; never overwrite a shared global hook directory. Capture the original effective hook paths/configuration and invoke supported preserved hooks by their original paths after the gate. Detect recursive wrapping, changed prior hooks, unsupported hook managers, linked paths, and per-worktree overrides; refuse ambiguous cases instead of guessing. Explain installation scope for linked worktrees before writing.

Store an owner-only installation manifest containing ownership, previous configuration, original hook identities, trusted runtime/config bindings, and supported composition. Installation dry-run is read-only. Uninstall restores only exact owned files/config values still matching that manifest; concurrent user edits cause a diagnostic rather than destructive restoration. Existing project-local OKF and unrelated user hooks remain active. Installation never sets global Git configuration, changes remote URLs, or performs a push.

For rollout, build and validate the CLI and gate installation first. Install gates in repositories explicitly selected by the owner, report repositories without gates as unenforced by this publication feature, then migrate provider registrations. Provider templates must not imply universal coverage merely because the CLI exists. Global provider migration is a deliberate policy change; record the selected repository coverage and owner-controlled enable/trust state during deployment. Do not re-enable hooks the user previously disabled without explicit deployment authorization.

## Plan of Work

All proposed test files below are new unless identified as existing. Record commands, exact source revision, platform, observed outcome, and limitations in this directory as milestones execute. Expected outcomes below are not claimed results. Use test-first vertical slices through public interfaces after confirming test seams under the TDD skill; do not write internal-method snapshots or a bulk suite of imagined internals. Do not add tests whose sole purpose is asserting a feature was deleted. Replacement workflow and upgrade behavior need positive end-to-end acceptance.

### Milestone 1: Establish publication feasibility and safe maintenance tools

Status: in progress
Acceptance: not met

**D0 - Publication and capacity decision proof.** Prerequisites: implementation authorization and the public test seams confirmed. Inputs: B3-B6, incident descriptions, existing capture/matching implementation, and Git/provider source references below. First reproduce the existing read/repair/completion lockout through public provider entrypoints in isolated incident-shaped repositories, recording expected native denials and the unchanged pending state. This is the baseline failure, not acceptance of the replacement. Use isolated local repositories, bare remotes, and an LFS endpoint; do not publish to a real service. Prove pre-push tuple/OID binding, multi-ref/new-ref/deletion/force/tag handling, replacement-object resistance, supported preserved-hook ordering/stdin replay, and LFS snapshot-to-upload binding. A rejected LFS push must transfer zero payload objects. Measure a first publication, long outgoing history, repeated blobs, multiple refs, a large individual blob/LFS payload, and the incident-sized workloads. Retain logical candidate bytes, distinct acquired object bytes, object/path counts, capture/temp usage, elapsed time, and peak memory separately.

Create `docs/hook-resilience-design-b/publication-contract.md` with concrete supported Git/LFS versions, platform behavior, numeric checkpoint/publication limits and allowed overrides, rationale, and observable rejection cases. Reconcile any resulting contract changes into B3-B6 here. Promotion requires exact delivered-byte binding for supported paths, complete late-secret detection, measured headroom, and bounded cancellation. If a supported path cannot meet this, record the specific unresolved constraint before dependent gate work; do not quietly downgrade the promise or activate registrations. This bounded task may use throwaway prototypes; it does not implement background execution or install live hooks.

**T1 - Candidate 1, verified fixture patch preflight.** Prerequisites: implementation authorization, confirmed public CLI test seam, and B3's CLI contract; D0 is not a prerequisite for this independent task. Use the retrospective's proposed names: `scripts/apply-verified-security-fixture-patch.py` and `scripts/test-apply-verified-security-fixture-patch.py`. CLI: required `--patch PATH|-`, repeated `--path RELATIVE_PATH`, explicit `--active-hook-root PATH`, mutually exclusive `--check`/`--apply`, plus the common help/version/JSON/noninteractive rules. No mode defaults to apply. Resolve the source candidate adapters from the current checkout and require an explicit reviewed active root; neither root's build is inferred from the other.

Reproduce HEAD/index/worktree/relevant-untracked state in an owner-only disposable repository outside the checkout. Preserve staged versus unstaged differences. Do not execute copied hooks/configuration. Start with named regular text fixture targets; reject traversal, absolute targets, symlinks/reparse points, special files, unresolved indexes, and unsupported rename/binary patches without changing live content. Let real Git classify the candidate diff. Run reviewed active and candidate generated scanner entrypoints with real provider envelopes in block mode, using pending and complete changed-file views. Require clean coverage, expected native permission, build identity, and required audit output; exit zero alone is insufficient. Use the real detector, not a second textual approximation.

Construct fake credential controls at runtime in temporary fixtures. Prove that the repaired source representation preserves the intended runtime bytes and still detects the controls. Before `--apply`, recheck target/index/state fingerprints. Preserve the live index and target modes. Use a bounded journal for multi-file application; restore only files still matching bytes written by this transaction after partial failure. Concurrent edits must not be overwritten. `--check` and rejected `--apply` leave target bytes, modes, and index unchanged. Register the new suite in `scripts/test-all.py`.

Acceptance covers unsafe moved fixtures, Git/text-diff disagreement, dirty staged/unstaged/untracked state, successful repaired content, actual credential controls, missing audit, malformed output, timeout, symlink targets, drift, and failure midway through application. The tool remains useful after universal scanning is retired because it prevents fixture changes from reaching commit/push gates unexpectedly. Run `rtk proxy python3 scripts/test-apply-verified-security-fixture-patch.py`; expect all cases pass with no live-home writes. Stop at this CLI's verified contract; do not refactor unrelated fixture suites.

**T2 - Candidate 3, mode-helper contract.** Prerequisites: confirmed generated-provider CLI seam. Extend existing `RecoveryTests` in `scripts/test-hook-diagnostic-recovery.py` with separate `test_launch_honors_scan_mode` and `test_launch_honors_guard_mode` methods. Reuse `setup_fixture`, `envelope`, and `launch`. Cover two hooks times three providers times block/warn, 12 cases total. Set both inherited mode variables opposite the requested mode. Assert actual native denial versus permitted warning behavior and the corresponding fresh audit record's mode/rule/enforcement. Warning output may contain `systemMessage`. Do not execute the protected operation described by a Guardian fixture. Preserve missing/corrupt helper denial in both modes and the deny-only diagnostic request.

In two disposable source copies, remove one environment assignment at a time; the corresponding focused test must fail. Do not mutate the live helper for this proof. Run both named methods and then the full recovery suite. Stop after retaining the behavioral contract; scanner gate mode semantics are handled independently in T3/T5.

T2 observed result: both focused methods and both-mode missing/corrupt-helper cases pass; the full recovery suite passes 15 methods. Both disposable assignment-removal controls fail all six native permission cases. The primary reviewed all five quality axes with no blockers, then rebased conflict-free and fast-forwarded base to `45401b4789ba9071d6cf90b435fed8bfd8722c51`. Only plan/audit documentation changed under the rebase, so the retained test evidence covers the resulting executable tree; no redundant rerun was needed. The clean task worktree was archived and its local branch removed. Milestone acceptance remains unmet pending D0/T1/I1.

**I1 - Preparation integration.** Prerequisites: T1 and T2. Run their public suites serially, generated parity, and affected provider scanner shell suites. Verify that fixture application preserves test data behavior and does not rely on ambient warning/skip settings. D0's contract artifact must exist before gate work begins. Missing prerequisites or unpublished prototype evidence leave acceptance not met.

### Milestone 2: Deliver synchronous checkpoints and historical status

Status: open
Acceptance: not met

**T3 - Result engine and CLI.** Prerequisites: D0, T1, T2. Extract B2 with generator/build-identity updates. Add `scripts/test-scan-secrets-cli.py` and the standalone installer dependency closure. Exercise actual CLI processes for help/version outside a repository, no-argument behavior, invalid options/types, both scopes, clean/findings/incomplete, JSON streams, redaction, environment poisoning, interruption, broken pipes, configuration bounds, and missing helpers. Confirm generated provider adapters preserve matching/audit behavior during the additive migration. Source check commands must not install hooks or change Git configuration. Register the new suite.

Run `rtk proxy python3 scripts/test-scan-secrets-cli.py`, existing merge/streaming/capture/reporting suites, generator parity, and installer fixtures for the bundle. Preserve meaningful detection and fault tests while adapting their public invocation where needed; do not weaken an assertion to hide a behavior change. Stop when the same engine supports explicit CLI checks and compatibility adapters with distinct correct output/exit contracts.

**T4 - Status storage and CLI.** Prerequisites: T3. Implement B4 in `scan_status.py` and add `scripts/test-scan-secrets-status.py`. Exercise `status` as a public process after a scan, without a previous scan, from linked worktrees, with concurrent completion, after interruption, and with stale/malformed/oversized/unreadable/linked records. Ensure status reads cannot trigger content inspection, Git subprocesses, network activity, or writes. Verify bounded process behavior and redaction with fake values. Stop at the CLI/report contract; provider lifecycle activation belongs to T8.

**I2 - CLI integration.** Prerequisites: T3 and T4. Run the two new suites with source and installed bundles in disposable homes. A report from one scan must remain purely historical after another edit. Audit failure must not produce clean enforcement; status-write failure must retain the independently correct security outcome. Verify all CLI-source requirements using actual stdout/stderr, exit status, stdin/TTY conditions, and cancellation. No background subprocess may remain after a completed command.

### Milestone 3: Enforce configured Git publication workflows

Status: open
Acceptance: not met

**T5 - Git transaction collectors and gate actions.** Prerequisites: D0 and I2. Implement B5 in `scan_git.py` and gate CLI actions in `scan_cli.py`. Add `scripts/test-scan-secrets-git-gates.py` using real Git commands and local bare remotes. Cover staged-only versus worktree content, alternate commit/index modes, unresolved indexes, empty/unborn repositories, non-HEAD and explicit-OID pushes, multiple refs, annotated tags/messages, deletions, force updates, unavailable remote baselines, shallow/partial object absence, replacement objects, malformed stdin, and a secret introduced then removed in intermediate history. A clean current tree must not hide unsafe outgoing history. Assert actual commit/ref/object transfer outcomes, not only process output. Invocation errors, missing/malformed/mismatched results, audit failure, ambient warn/skip settings, and capacity failures must prevent the configured action.

The pre-commit contract is staged feedback, not a proof about every possible later hook mutation. Independently exercise actual pre-push rejection of unsafe committed content. Register and run `rtk proxy python3 scripts/test-scan-secrets-git-gates.py`. Stop before installation integration; T7 owns binding these actions to repositories.

**T6 - LFS publication.** Prerequisites: T5 and D0's accepted LFS binding proof. Implement strict pointer/payload handling, private verified delivery storage, supported upload composition, and cleanup. Add `scripts/test-scan-secrets-lfs.py` using a local endpoint that records transferred payload objects. Cover clean payloads, fake secrets inside payloads, missing/corrupt payloads, mismatched size/digest, multiple refs sharing payloads, a late finding, interruption, mutation after acquisition, and an existing standard LFS hook. Reject before any upload on failure and verify zero transferred payload objects, not merely unchanged Git refs. Missing Git LFS is a failed prerequisite for this suite/CI, not a passing skip. Stop when checked-byte/delivered-byte equivalence and preserved upload behavior are proven for the documented support set.

**T7 - Repository gate installation.** Prerequisites: T5 and T6. Implement B6's `hooks install/uninstall` commands through `scripts/install-repo-gates.py` and shared runtime installation code. Add `scripts/test-install-repo-gates.py` with real temporary repositories, existing custom hooks, standard LFS, global/relative/custom `core.hooksPath`, linked worktrees, ambiguous managers, paths with spaces, malformed manifests, and interrupted writes. Verify dry-run, idempotence, ownership-only uninstall, exact original arguments, identical stdin for each preserved hook, correct order, downstream error propagation, absolute runtime binding, and native platform launch behavior. Never write into a shared/global hook directory. Stop after explicit per-repository install/recovery works; global provider migration remains T8.

**I3 - Publication integration.** Prerequisites: T5-T7. From a fresh and an upgraded installed fixture, perform real add/commit/push cycles. Measure first publication, long history, repeated blobs, multi-ref pushes, large individual content, and both incident-sized workloads under the recorded D0 limits. Pair accepted workloads with late fake secrets and just-over-new-limit incomplete controls. Measure enumeration, acquisition, matching, temp usage, output, and elapsed time independently. Prove ordinary repair and a fresh retry succeed without disabling hooks. No saved status may be consumed as gate authorization.

### Milestone 4: Migrate provider hooks without leaving old blockers

Status: open
Acceptance: not met

**T8 - Metadata, lifecycle adapters, and reconciliation.** Prerequisites: I3. Update canonical common/diagnostic envelope handling only where needed for documented metadata; preserve Guardian's strict executable interface. Add a canonical `hooks/families/scan_status.py` renderer for thin status-only provider adapters, generated to explicitly manifest-owned provider-local scripts. Add all runtime assets to both platform installer lists and ownership checks. Apply B1 native output schemas and B6 retirement registry in both mergers and templates. Use existing `scripts/test-install-codex-hooks.py`, Bash/PowerShell installer fixtures, recovery/reporting/lifecycle suites, and a proposed `scripts/test-scan-secrets-lifecycle.py` for integrated public delivery cases.

Start installer fixtures from actual old template shapes with pinned commands, scanner-only removed events, scanner plus unrelated handlers, nested settings, legacy exact owned forms, user commands with the same basename, ambiguous commands, and linked/hard-linked destinations. Verify the resulting installed workflow and user settings, then reinstall and compare. Cover partial-install recovery. Do not write deletion-only regression tests; old-install upgrade acceptance must show the new intended work and status/gate behavior actually execute.

**I4 - Recovery and lifecycle integration.** Prerequisites: T8. Exercise an installed disposable environment with the large unresolved merge and 20,026,474-byte binary workload. Deliver permitted reads and real repair writes through the host/tool harness, not by modifying the fixture outside the guarded path. Finish the turn repeatedly while the saved report is absent, stale, incomplete, corrupt, or unavailable. Verify the provider records only the status action for this feature and never creates a scanner-triggered continuation. Guardian still denies established protected-operation controls. Explicit checkpoint and Git gate scans still detect late fake secrets. Direct script execution is source/installed proof; authenticated host delivery is a separate V1 requirement.

### Milestone 5: Make validation repeatable and record release limits

Status: open
Acceptance: not met

**T9 - Candidate 2, focused macOS CI.** Prerequisites: I1 for initial wiring; expand the job as T3-T8 land. Add `.github/workflows/hooks-posix.yml` with pull-request, push path filters, and manual dispatch. Include canonical runtime, all generated provider roots, scripts, and relevant workflow paths. Use read-only repository permissions and the repository's action version conventions. Install/verify Git, Bash, Python 3.13, jq, PowerShell 7+, stable RTK >=0.50.0 with required processors, and Git LFS for the new publication suite. These are CI prerequisites, not permission to raise the runtime interpreter floor silently. Writable homes/logs/Git fixtures belong in runner-temporary storage.

Run the initial focused commands serially: generated parity, recovery, security reporting, and the three provider scanner shell suites. Capture runs are already transitive. Modify existing `scripts/test-scan-secrets-capture.py` to emit safe explicit execution evidence for the Darwin `native_once` process-exhaustion branch; a generic PASS or skip is insufficient. Add the new CLI, status, fixture preflight, Git gate, LFS, lifecycle, and installation suites to the job once available. Register standalone suites in `scripts/test-all.py`, not duplicate nested capture execution.

Keep `.github/workflows/ready-ideas-windows.yml` as a separate result and add native launcher, gate, status, migration, and LFS coverage where supported. Preserve existing Windows capture/ACL/junction checks. A macOS PowerShell pass is not Windows evidence. In disposable branches/copies, deliberately fail a recovery assertion and introduce generated drift separately; each must fail the appropriate CI job. Remove those deliberate faults before integration. A workflow file is not proof that a remote run passed or that branch protection requires it.

**V1 - Integrated acceptance and deployment evidence.** Prerequisites: I4 and T9. Run the commands below against frozen integrated source. Verify all requirement groups, both historical workload shapes, adversarial negatives, all three providers, native platforms, and installed old-to-new migration. Run benchmarks separately from functional suites. If Guardian runtime changed, retain the existing matched latency/resource acceptance from [security testing](../../.agents/instructions/testing/hooks-security.md); do not silently replace its budgets with slower CLI budgets. Record actual CI links and source hashes. Native Windows and authenticated provider delivery remain explicitly unverified until observed.

Real-home deployment is an owner-authorized action after source and isolated installation checks. Record selected repositories, effective Git gates, provider build/asset identities, backups, `/hooks` review where required, and the control that the user used to disable old hooks. Reinstalling files does not prove that a disabled hook was re-enabled. Do not change trust or enablement merely to collect evidence. When authorized, use the existing provider-delivery probe and verify the visible nonblocking status and actual tool execution in disposable repositories. Keep external acceptance open if access is unavailable; finish independent source work without claiming completion.

**K1 - Documentation and maintenance.** Prerequisites: all implementation tasks and any delegated work are finished. Update `README.md`, add `docs/hook-resilience-design-b/cli.md` with novice examples/configuration/recovery/coverage limits, and reconcile the current rules in hook/security/provider/script/testing instructions. Narrowly replace the obsolete universal-scanner registration and exact-owned-retirement descriptions after the behavior changes. Keep unrelated obligations, immutable raw sources, and protected AGENTS.md sections. Run `update-agent-docs` once, applying knowledge admission; no new memory is required. Apply OKF and its linter only if canonical KB semantics change. Reconcile this plan's progress, evidence, remaining owner actions, and outcome together.

## Task Dependencies and Integration Ownership

D0 precedes T3 and all publication implementation. T1 and T2 can be independently completed before extraction; I1 integrates them. T3 precedes T4; I2 integrates both. T5 depends on D0/I2; T6 depends on T5; T7 depends on T5/T6; I3 integrates T5-T7. T8 depends on I3; I4 integrates the migrated runtime. T9 can begin after I1 and must include all later suites before V1. V1 depends on I4/T9; K1 follows all completed work. These prerequisites are not authorization to dispatch agents or execute the plan.

One integrator owns `hooks/manifest.py`, `scripts/generate-hooks.py`, both platform installers, provider templates, `scripts/test-all.py`, and this plan. Serialize edits to those shared files and regenerate from combined canonical source. Generator tests compare whole-checkout state, so pause concurrent edits during them. Installer suites and performance measurements must not overlap tests that mutate shared fixtures. If future delegation is authorized, assign bounded tasks and exclusive evidence files; the integrator alone reconciles shared status and the final KB pass.

## Concrete Steps

Implementation authorization has arrived. The base branch is `codex/hook-resilience-design-b`, created from the clean planning commit `1cbe2cdf162b823b5f331f002a93464a0a1adca0`. The user explicitly confirmed all listed public seams on 2026-10-15. D0, T1, and T2 are running in separate private worktrees. Next: verify their evidence and integrate each clean branch serially; continue the task graph only when prerequisites pass. The primary agent owns this plan, shared generator/install/registry files, integration, and the final coordinated documentation pass. Recheck current source rather than resetting to the authoring revision.

Use these existing baseline commands from the repository root before changing code. They demonstrate current limits and contracts, not success of Design B:

```sh
rtk proxy python3 scripts/generate-hooks.py --check
rtk proxy python3 scripts/test-scan-secrets-merge.py --provider codex -k conflict_snapshots
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py -k overflow_failure
rtk proxy python3 scripts/test-all.py --list
```

Reconstruct the named merge only in a disposable clone/worktree with isolated Git configuration and identity and `commit.gpgsign=false`. If either historical commit is unavailable, record that limitation and retain the independent conflict-size fixture; do not claim an exact replay. Build synthetic binary files with the six reported sizes for the workload control and clearly distinguish them from the original PNGs. Construct credential controls at runtime, never embed real secrets or assembled sensitive fixtures in source.

After each runtime slice, regenerate with `rtk proxy python3 scripts/generate-hooks.py --write`, then run `--check`. The new test commands below are expected to become available as their owning tasks land; they do not exist at plan creation:

```sh
rtk proxy python3 scripts/test-apply-verified-security-fixture-patch.py
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_launch_honors_scan_mode
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_launch_honors_guard_mode
rtk proxy python3 scripts/test-scan-secrets-cli.py
rtk proxy python3 scripts/test-scan-secrets-status.py
rtk proxy python3 scripts/test-scan-secrets-git-gates.py
rtk proxy python3 scripts/test-scan-secrets-lfs.py
rtk proxy python3 scripts/test-install-repo-gates.py
rtk proxy python3 scripts/test-scan-secrets-lifecycle.py
```

The maintained integration commands, run serially when required by their fixture behavior, include:

```sh
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py
rtk proxy python3 scripts/test-hook-diagnostics.py
rtk proxy python3 scripts/test-security-reporting.py
rtk proxy python3 scripts/test-scan-secrets-merge.py
rtk proxy python3 scripts/test-scan-secrets-streaming.py
rtk proxy python3 scripts/test-scan-secrets-stream-component.py
rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh
rtk proxy python3 scripts/test-install-codex-hooks.py
rtk proxy python3 scripts/test-generate-hooks.py
rtk proxy bash scripts/test-install.sh
rtk proxy pwsh -NoProfile -File scripts/test-install.ps1
rtk proxy python3 scripts/test_test_all.py
rtk proxy python3 scripts/generate-hooks.py --check
rtk git diff --check
```

On native Windows also run `rtk proxy pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1` and `rtk proxy pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1`, plus the new installed CLI/gate suites. Run the aggregate `rtk proxy python3 scripts/test-all.py` on a supported POSIX host for final integration after prerequisites are present. Apply the matching Guardian suites if its parser/runtime changed. An unavailable prerequisite is an incomplete verification item, not a successful skip.

## Validation and Acceptance

Public seams are the standalone CLI process, generated provider JSON entrypoints, actual Git commit/push through installed dispatchers, fixture-preflight CLI, and real installer interfaces in disposable homes. Native host delivery is an additional external seam. Confirm these seams before writing tests; do not mistake this plan's proposed test list for user confirmation of tests not yet discussed.

Acceptance requires all of the following outcomes, with evidence tied to the integrated revision:

1. Both incident-shaped workloads allow ordinary read/repair/turn completion through the configured provider workflow. An incomplete explicit check does not create a tool lockout or automatic continuation.
2. There are no automatic/background checkpoint triggers. End Turn only reports historical status, including missing/stale/unavailable cases, within its bounded lifecycle contract.
3. Configured Git gates reject findings, incomplete inspection, invalid/mismatched results, missing helpers, and required-audit failure. Successful publication scans all required immutable bytes under the selected policy. No prior status authorizes later work.
4. Transaction tests cover non-HEAD/multi-ref/tag/new/deleted/forced updates, complete intermediate history, missing history, and replacement-object resistance. Commit/tag message scope and binary limitations are explicit.
5. LFS failures cause zero payload transfer before rejection. Existing supported hooks receive original args/stdin and run in the declared order. Clean supported pushes still work.
6. Upgrade fixtures started from old installed configurations exercise the new workflow and preserve unrelated settings/hooks. CLI assets, absolute interpreter bindings, native launchers, idempotence, rollback, and explicit repository coverage are verified.
7. Candidate 1 rejects an unsafe fixture patch without live changes, accepts the repaired representation, and preserves runtime fake-credential detection and index/modes. Candidate 3 passes all 12 cases and fails both isolated assignment-removal controls.
8. Candidate 2's macOS CI actually runs the native capture branch and fails controlled recovery/drift faults. Native Windows remains separate. Real CI runs and required branch protection are not inferred from a YAML file.
9. Every new CLI passes B3's help, streams, JSON, exit, noninteractive, configuration, no-hidden-side-effect, cancellation, and redaction checks. Gates cannot turn ambient warning/skip settings into permission.
10. Capacity is measured for the new publication workload, with finite approved limits and a usable capacity-adjustment path. Late-secret and over-limit controls retain meaningful expected results. No truncation, extension skip, blanket allowlist, or weakened failing test is accepted as a repair.

The scanner detects its maintained text patterns, including supported raw strings in binary content; it does not perform image OCR or general archive extraction. A clean result is scoped to that policy and captured content, not proof that arbitrary data contains no secret. Installed local hooks do not stop intentional bypass or unrelated network tools. Document these limits alongside the useful configured-workflow guarantee.

## Idempotence and Recovery

Check and gate commands do not modify source, index, refs, or remote configuration; they may write declared private temporary captures, required audit records, and the informational last report. Status/help/version are read-only. The dispatcher may invoke preserved hooks with their existing effects only after the gate passes. Rejecting a push must occur before supported upload-capable hooks run.

Preserve original bytes/configuration and a manifest before any installer mutation. Repeating a completed install should produce no new semantic changes or unnecessary backups. After interruption, validate manifest and file identities, restore or finish only this installation's assets, and never replace concurrent user edits. Do not roll back by deleting unrelated hooks, disabling checks, globally replacing `core.hooksPath`, or resetting the repository. The preflight patch tool uses its own bounded transaction journal and likewise preserves concurrent edits.

When a gate finds a secret, remove it from the relevant staged content or outgoing history and rerun. Deleting it from the latest working file alone does not repair an earlier outgoing commit. When scanning is incomplete, follow the concrete reported resource/storage/history remediation and retry the same action. Reads, edits, diagnostics, and End Turn remain available throughout. New attempts are explicit actions, never an automatically repeating hook loop.

## Outcomes & Retrospective

Planning is complete and implementation is authorized. Branch preparation is complete; T2 is implemented, reviewed, and integrated; D0/T1 are running. New CLI commands, repository gates, provider migration, CI execution, and live deployment have not occurred. The plan incorporates the user-selected no-background design, candidates 1-3, the five accepted adversarial findings, and source-derived CLI requirements. The two promoted idea reports are retained in `docs/ideas/archive/` with their historical scope and repaired links.

Documentation-only verification on 2026-10-15 checked all 60 local Markdown links across the plan, idea index, and archived reports; required living sections and all five open milestone states; preserved report contents apart from archive notices and link repair; and Git whitespace checks. Runtime tests were not run for this planning-only change. The coordinated knowledge-maintenance pass adds no canonical instruction or memory: the new behavior is proposed, and current runtime guidance remains current until implementation.

Do not mark implementation milestones complete based on this document, earlier resilience tests, or the discussion's disposable probes. As work proceeds, replace this paragraph with observed outcomes, remaining owner actions, and evidence for each acceptance dimension. Preserve the distinction between source behavior, installed assets, actual host delivery, and native platform execution.

## References and Historical Evidence

- [Retrospective and candidate implementation guide](../retros/2026-10-15-hook-resilience-retro.md), candidates 1-3 only.
- [Archived image incident](../ideas/archive/hook-failures.md) and [archived merge repair report](../ideas/archive/hook-failure-repair.md). Historical suggestions do not override this plan's selected design.
- [Original investigation](../hook-resilience/ExecPlan.md) and [previous implementation](../hook-resilience/implementation-ExecPlan.md). Retain their evidence and outstanding external acceptance; this plan changes future scanner placement and workflow, not historical outcomes.
- [clig.dev saved source](../../.agents/sources/clig-dev.md), [12 Factor CLI Apps saved source](../../.agents/sources/12-factor-cli-apps.md), and [Thoughtworks CLI guidelines saved source](../../.agents/sources/cli-design-guidelines.md). B3 identifies the adopted requirements and resolves conflicting advice.
- [Copilot raw hook reference](../../.agents/sources/copilot-hooks-ref.md), [VS Code raw hook reference](../../.agents/sources/vscode-agent-hooks.md), [Gemini overview](../../.agents/sources/gemini-hooks.md), and [Gemini hook guidance](../../.agents/sources/gemini-hooks-best-practices.md). Recheck current official/deployed contracts for exact lifecycle and metadata behavior.
- [Current Codex hook documentation](https://learn.chatgpt.com/docs/hooks), [Git hook contract](https://git-scm.com/docs/githooks), [Git push interface](https://git-scm.com/docs/git-push), [Git object replacement](https://git-scm.com/docs/git-replace), and [Git LFS pre-push source documentation](https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/man/git-lfs-pre-push.adoc). These informed the earlier diagnosis/review; D0 must verify the versions actually exercised.
