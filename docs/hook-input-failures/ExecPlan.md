# Fix opaque secret scans and oversized patch denials

This living ExecPlan is `docs/hook-input-failures/ExecPlan.md`. Follow the `exec-plans` and explicitly requested `execplan-implement` skills, repository `AGENTS.md`, and `.agents/instructions/INDEX.md`. Keep every status below consistent with retained evidence.

## Purpose / Big Picture

Ordinary patches containing documentation, YAML, and source code must not consume shell-command segment budgets when the provider has identified their contents as patch data. Real executable inputs, unsupported shapes, destructive patch operations, and oversized inputs must retain their protections. Users must receive actionable, sanitized reasons when a secret scan cannot complete, instead of identical unexplained denials on every tool.

The requirements are `docs/tool-guard-hook-bug.txt`, `docs/scan-secrets-hook-bug.txt`, and the user's request to sample Codex session logs, implement these fixes, and review all changes on Standards and Spec axes. The user confirmed that both supplied reports came from Copilot. Codex sampling supplies additional tuning evidence; it does not establish that the Copilot patch incident is fixed. The reports concern another machine; local reproductions cannot establish that machine's exact scanner failure. Never disable either hook, approve incomplete scans unconditionally, or retain private session contents.

## Progress

- [x] (2026-10-08) [milestone-1] T1: Sampled targeted Codex denials and reproduced historical passing patches plus all four recent byte failures; see `guardian-evidence.md`.
- [x] (2026-10-08) [milestone-1] T1: Confirmed Copilot raw scalar arguments in 47 actual post/failure hook captures and reproduced the reported failure through its installed public hook. Live pre-tool delivery remains unverified because authentication is unavailable.
- [x] (2026-10-08) [milestone-1] T2: Reproduced scanner failures and retained bounded diagnostic remedy in `scanner-evidence.md`.
- [x] (2026-10-08) [milestone-1] Reconciled implementation tasks with evidence; this planning checkpoint precedes all source edits.
- [ ] [milestone-2] T3: In progress in `guardian-patch-capacity/skills`; tune validated patch capacity and truthful limit diagnostics with red-green public tests.
- [ ] [milestone-2] T4: In progress in `scanner-failure-diagnostics/skills`; repair incomplete-scan diagnostics with red-green public tests.
- [ ] [milestone-3] T5: Integrate private task branches serially and prove composed behavior on the base branch.
- [ ] [milestone-3] Verify generated freshness, affected provider/security suites, resource bounds, and installation behavior.
- [ ] [milestone-4] T6: Run independent Standards and Spec reviews against the initial baseline; repair findings through explicit task nodes.
- [ ] [milestone-4] Complete one coordinated `update-agent-docs` pass, final validation, and a clean committed checkpoint.

## Surprises & Discoveries

- Initial source passes `rtk proxy python3 scripts/generate-hooks.py --check`: 35 generated files are current.
- Targeted Codex session correlation found 13 actual historical patch segment denials. Twelve reconstructed literal patches, 6,194-24,727 bytes and 124-523 lines, already parse under current native-patch logic. Recent installed guard logs instead show 77,089-99,186-byte native patches denied by the 65,536-byte budget. The current installed Codex guard and policy match repository source.
- Tool Guardian already accepts Codex's exact `apply_patch` object with a string `command` field. A synthetic 143-line patch in that envelope passes; unsupported envelopes fall back to the 128-segment shell limit. Shape mismatches alone do not establish the reported cause.
- Secret scanning examines dirty repository state for every tool call. A safe read and a no-argument documentation request both reproduce generic denial with a safe file above 1 MiB, 257 untracked files, or a dirty tracked submodule. These are candidate causes, not proof of the reported host's state.
- `rtk` 0.51.0 is available. `rtk gain` cannot open its tracking database in this environment; normal prefixed commands work.

## Decision Log

- 2026-10-08: Use initial commit `72789d6978bb7255583f9fb1cd8e18c37fe3173b` as the fixed review point. "All changes" means this task's complete diff, including tests, generated output, and documentation.
- 2026-10-08: Work on base branch `codex/fix-hook-bug-reports`. Each source task uses a separate private worktree and branch. Rebase and fast-forward one completed task at a time; never push.
- 2026-10-08: Keep exact-schema classification and fail-closed limits. Decide patch grammar/provider changes from session evidence, current source, and official provider documentation, not guessed aliases or an arbitrary increase of every limit.
- 2026-10-08: Both reports are Copilot incidents. Its actual native tool arguments and 47 post/failure hook captures establish `toolName: apply_patch`, `toolArgs: <raw patch string>`. Add only that exact scalar Copilot shape to native patch inspection. The installed public prehook reproduces the segment denial on a harmless 143-line patch and currently misses raw protected-file delete operations. Isolated live pre-tool probing lacked authentication, including existing `gh` auth; preserve this provider-delivery limitation without guessing aliases or object schemas.
- 2026-10-08: Set validated patches to 262,144 bytes (256 KiB): raw UTF-8 bytes for Copilot and aggregate string/key bytes for Codex's existing object schema. This covers observed Codex patches below 100 KiB with bounded growth headroom and prevents arbitrary shell limits on Copilot patch bodies. Other native data stays at 65,536 bytes; executable/strict text stays at 32,768 bytes; shell segment count stays at 128. Keep patch grammar unchanged. Express both early-stopped segment counters as lower bounds, not exact complete totals.
- 2026-10-08: Keep scanner repository-wide coverage and existing safety bounds unless a bounded diagnosis proves a behavior correction. Diagnostics use a fixed vocabulary and safe counts, never exception messages, subprocess stderr, file contents, or sensitive paths.
- 2026-10-08: Scanner repair is actionable incomplete-scan diagnostics, not a speculative scan-policy change. Dirty submodule support and exemptions for read-only tools are out of scope. Known safe requests in bounded repositories must pass; incomplete repository scans must continue denying with the cause and recovery action exposed safely.
- 2026-10-08: Retain this user-requested plan and sanitized evidence as the reviewable deliverable for this effort. Raw session logs remain outside version control.

## Outcomes & Retrospective

Diagnosis is complete after the Copilot provider correction. Both source fixes are running in separate managed worktrees. T3 now includes exact Copilot raw patch parsing, protection for its delete/move sources, and the independently evidenced Codex capacity increase. Source evidence, installed copies, actual provider delivery, and native Windows behavior are separate claims. The isolated Copilot live probe could not authenticate; public hook subprocess proof remains available. Native macOS RSS collection first failed with `sysctl kern.clockrate: Operation not permitted`; the approved collector then succeeded and is available for resource proof.

## Context and Orientation

The canonical hook implementations are Python renderers in `hooks/families/tool_guard.py` and `hooks/families/scan_secrets.py`. `scripts/generate-hooks.py --write` creates provider-local scripts. Never edit generated scripts directly. Tool Guardian's generated policy helper is identical under `.codex/hooks/helpers/`, `.copilot/hooks/scripts/helpers/`, and `.gemini/hooks/scripts/helpers/`. Each provider's `tool-guard.py` imports only its local helper; `scan-secrets.py` is separately generated for each provider.

Tool Guardian first validates a known provider argument shape, separates inert file data from operations, then applies either native-data bounds or strict executable inspection. `_parse_native_patch`, `_native_tool_shape`, `read_tool_scan_inputs`, `_command_segments`, `ScanLimitExceeded`, and safe denial formatting own the relevant behavior. Current shell limit is 128 segments; early stopping can produce a 129 sentinel rather than a complete count. Unknown fields and malformed syntax must retain strict inspection. Native patch delete and move-source protection must survive.

Secret scanning resolves a Git repository, enumerates staged/worktree/untracked candidates, captures Git output with bounded waits, reads bounded regular files, scans for credential patterns, and writes protected audit records. Its generic exception handler currently discards the reason. Repository limits are 256 candidates, 1 MiB per file, 8 MiB total/captured output, and eight seconds. These are security boundaries; "benign request" does not imply a clean repository.

The source suites are in `scripts/test-tool-guard-*.py`, three `test-*-hooks-tool-guard.sh` scripts, `scripts/test-scan-secrets-capture.py`, `scripts/test-scan-secrets-merge.py`, three secret-scanner shell suites, and `scripts/test-security-banners.py`. Existing shared fixture modules should own reusable sanitized cases. New suites, if necessary, must be registered in `scripts/test-all.py`.

All commands below run from `/Users/adam/.codex/worktrees/2d9c/skills` unless a task worktree is specified. Use Python 3 and Bash through `rtk proxy`; use temporary homes and explicit writable audit/observability paths for tests. macOS is available; native Windows acceptance requires a separate Windows run.

## Plan of Work

### Milestone 1: Establish reproducible causes and bounded decisions

Status: done
Acceptance: met

T1 and T2 are independent read-only diagnosis tasks, with exclusive evidence-file ownership. T1 owns `docs/hook-input-failures/guardian-evidence.md`; T2 owns `docs/hook-input-failures/scanner-evidence.md`. Neither edits source or this plan. Both first invoke public provider hook subprocesses with synthetic fixtures, before recommending fixes. T1 samples a bounded recent Codex session set, separates real tool-output denials from quoted reports, and records only dates, counts, sizes, structural syntax, and safe rule identifiers. T2 compares clean benign requests, definite fake-secret findings, and intentionally incomplete scans. Prerequisites: initial source and the two bug reports. Stop after reproducible evidence and bounded recommendations are retained.

Acceptance evidence is retained in [guardian evidence](guardian-evidence.md) and [scanner evidence](scanner-evidence.md). Public Codex fixtures allow the 24,727-byte/523-line historical patch shape, deny synthetic equivalents of all four recent 77,089-99,186-byte cases, allow an exact 65,536-byte aggregate, and deny 65,537 bytes. All three scanner providers allow bounded clean/unborn fixtures and detect fake credentials; oversized candidates, excessive candidates, unsafe file types, and unavailable log storage reproduce generic incomplete denial. Official Codex hook documentation at <https://learn.chatgpt.com/docs/hooks> specifies `tool_name: apply_patch` and `tool_input.command`; raw session tool-call input is not automatically the hook envelope.

### Milestone 2: Repair each hook with independent regression proof

Status: in progress
Acceptance: not met

T3 prerequisites: T1 evidence and committed initial plan, both met. Own `hooks/families/tool_guard.py`, its generated adapters/helpers, `scripts/test-tool-guard-native-data.py`, `scripts/test-tool-guard-limits.py`, `scripts/fixtures/tool_guard_vectors.py` if needed, `scripts/benchmark-tool-guard-resources.py`, and `guardian-result.md` beside this plan. Add exact Copilot raw `toolName: apply_patch` / `toolArgs: string` classification and a 262,144-byte patch budget shared with the existing exact Codex object schema. Bound raw patch bytes before parsing. Retain strict fallback after unsuccessful parsing, without changing scalar strict accounting, and make both early-stopped segment counters truthful. Keep other scalar/unknown-tool fallback, patch grammar, and all other budgets unchanged. Exercise prose, YAML, shell examples, single/multi-file patches near the historical segment boundary and recent byte sizes, late protected delete/move sources, malformed inputs, aliases and guessed object controls, normalized limits, exact UTF-8 byte boundaries, and executable controls. A denied hook must leave fixture files unchanged; this does not prove the patch executor's transaction semantics. Update both providers' patch resource boundary fixtures, including high-line-count and malformed inputs; preserve Copilot's separate 64 KiB writer bounds. Stop after focused tests pass and one implementation commit is ready.

T4 prerequisites: T2 acceptance and committed plan. Own `hooks/families/scan_secrets.py`, its three generated adapters, existing scanner tests, the scanner-specific portion of `scripts/test-security-banners.py`, and `scanner-result.md` beside this plan. Implement fixed-vocabulary typed incomplete causes for initialization, input, Git/capture, bounds, candidate safety/read, scan-log, and unexpected internal failures. Attach trusted exit status, elapsed threshold, measured count, or byte limit when known. Expose short fixed recovery advice in both block and warn messages and retain the same safe metadata in incomplete scan records when logging works. Do not classify arbitrary exception text. Preserve the first cause when diagnostic logging also fails. Preserve missing-Git, invalid payload, audit failure, timeout, capture corruption/overflow, HEAD failure, valid unborn repository, and fake-credential controls. Never convert an unknown exception into approval or echo an exception's raw text. Stop after focused tests pass and one implementation commit is ready.

The shared generator has separate outputs for T3/T4, but generation and shared test-file edits must be serialized during integration. Do not edit `README.md`, KB guidance, shared banner tests, or `scripts/test-all.py` concurrently; request coordinator assignment when needed. Activate `tdd` and `addy-security-and-hardening` for each source task. Follow the invoked implementation skill's `references/message.md`: Conventional Commit subject, Summary/Rationale/Tests body, default Copilot co-author. Keep branches unpushed.

### Milestone 3: Integrate and verify composed behavior

Status: open
Acceptance: not met

T5 prerequisites: T3 and T4 commits with clean task worktrees and focused evidence. The coordinator owns integration. Rebase each task onto current base, repair conflicts in that task worktree, rerun affected checks when resulting interactions differ, and fast-forward base. Verify equal branch tips before removing clean integrated task worktrees and local branches. Keep unresolved branches intact.

Run generator freshness before and after relevant security suites. Run all three provider guard suites, native-data/shell-data/limits/false-positive tests, all three scanner suites, capture and merge tests, shared security banners, and generator tests. Freeze the entire checkout while generator tests compare snapshots. All logs must use disposable writable paths. Tests must assert real findings for fake-secret fixtures, not merely generic denial.

Exercise both generated hooks on the same benign repository and large valid patch request; both should allow. A fake credential in the repository must still yield scanner findings, and executable or protected-operation controls must still be denied. The coordinator may delegate a named bounded integration task if new test source is needed.

If input budgets change, run `rtk proxy python3 scripts/benchmark-tool-guard-resources.py --output /private/tmp/hook-input-resources.json --ceiling-ms 500` sequentially against frozen source. Resource measurements require an approved collector if macOS sandbox blocks RSS. If timing-sensitive classification changes warrant acceptance comparison, follow `.agents/instructions/testing/hooks-security.md`: two alternating matched warm pairs with 25 samples/three warmups and 25 fresh-copy cold launches; preserve failures and investigate a targeted repeat. Do not claim latency acceptance from an exit status alone.

Installation proof uses disposable homes first. Before any live installed-hook validation, run `rtk proxy bash scripts/install.sh` as required by repository guidance, preserving unrelated settings/logs and honoring runtime permissions. Codex trust review through `/hooks` remains user-owned if requested by the runtime. An installed-script probe is not proof of provider dispatch. Record anything unavailable explicitly.

### Milestone 4: Independent review and final checkpoint

Status: open
Acceptance: not met

T6 prerequisites: integrated verified source. Spawn fresh, independent Standards and Spec reviewers using `code-review-biaxis`. Validate the fixed point, then use `git diff 72789d6978bb7255583f9fb1cd8e18c37fe3173b...HEAD` and the matching commit list. Standards receives applicable repository rules plus the skill's full smell baseline. Spec receives both bug reports, the user's log-sampling request, and this plan. Retain each report separately and do not merge or rerank axes.

Add bounded repair nodes for actionable findings, dispatch each to a fresh implementer unless it repairs that implementer's original node, and rerun affected checks. Once all agents finish, activate `update-agent-docs` for one coordinated pass, applying knowledge admission. Update canonical instructions only for durable evidence-backed obligations; no new memory is required. If KB Markdown changes, activate `okf-authoring`, run `rtk proxy python3 scripts/lint-okf.py`, check links, and inspect for lost rules. Commit synchronized documentation and reconcile all plan sections.

## Concrete Steps

Next: finish T3/T4 and verify clean branch state and scoped commits. Both implementation tasks began after planning commit `be01b9a` in managed worktrees under `/Users/adam/.codex/worktrees/`; their branches are `codex/hook-patch-capacity` and `codex/hook-scan-diagnostics`. Copilot input evidence is now sufficient for the exact source repair, while live provider delivery remains unverified. Integrate completed commits serially, run composed checks, and review the complete diff from the pinned initial commit.

## Validation and Acceptance

Expected commands include `rtk proxy python3 scripts/generate-hooks.py --check`, `rtk proxy python3 scripts/test-tool-guard-native-data.py`, `rtk proxy python3 scripts/test-tool-guard-shell-data.py`, `rtk proxy python3 scripts/test-tool-guard-limits.py`, `rtk proxy python3 scripts/test-tool-guard-false-positives.py`, `rtk proxy python3 scripts/test-scan-secrets-capture.py`, `rtk proxy python3 scripts/test-scan-secrets-merge.py`, `rtk proxy python3 scripts/test-security-banners.py`, and `rtk proxy python3 scripts/test-generate-hooks.py`. Provider shell suites and fixture installer checks follow the testing routes. Exit zero plus the intended public decisions establishes source acceptance; planned commands are not results.

Retain failing-before/passing-after observations, integrated suite totals, exact commit identities, sanitized log-sampling scope, resource evidence when required, and separate installed/platform limitations. No real credential or raw session body belongs in a fixture, output, or commit.

## Idempotence and Recovery

Generator write mode is repeatable and touches only manifest-owned outputs. Keep implementation commits scoped and unpushed. If a task fails, leave its branch and evidence intact, reopen its Progress item, and repair in its own worktree. Never remove an unintegrated or dirty worktree. Failed or incomplete scans keep denying in block mode. Installation uses existing safe mergers and backups; do not bypass Codex hook trust or overwrite unrelated settings. Revert a verified bad implementation commit on the topic branch if recovery is needed; do not reset user work or modify unrelated branches.
