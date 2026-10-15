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
- [x] (2026-10-08) [milestone-2] T3: Exact Copilot raw patches and Codex object patches pass with 256 KiB bounds; focused native/limit/shell/corpus tests and negative controls passed.
- [x] (2026-10-08) [milestone-2] T4: Typed incomplete causes, safe metadata, and recovery advice pass all provider scanner/capture suites and merge regression checks.
- [x] (2026-10-08) [milestone-3] T5: Integrated both branches and proved composed behavior for Copilot/Codex: large multi-file patches pass, independent fake-secret findings deny, and benign requests against oversized candidates deny with safe byte diagnostics.
- [x] (2026-10-08) [milestone-3] T5: Rebased scanner without conflicts and fast-forwarded `f158f66471b3ef04f5105000f1ab77ccda546a89`; source/tests are byte-identical to the verified task commit.
- [x] (2026-10-08) [milestone-3] T5: Rebased Guardian without conflicts and fast-forwarded `f0cca423acb598e2a3ee582d44e2de8cc49ee842`; its owned source/tests are byte-identical to the verified task commit, and all 35 generated files are current.
- [x] (2026-10-08) [milestone-3] Refreshed installed hooks through `scripts/install.sh`. Nine changed hook/helper fingerprints match source. Installed Copilot/Codex patch and protected-operation probes plus all-provider scanner diagnostic/finding probes passed.
- [x] (2026-10-08) [milestone-3] Shared proof passed: three provider guard suites, 14 security-banner tests, 26 generator tests, installer fixtures, and two benchmark-runner tests. README now explains patch handling and actionable incomplete scans.
- [x] (2026-10-08) [milestone-3] All 108 resource cases met the 500 ms ceiling; maximum observed sample 58.826750 ms. Retained method and results are in `validation.md`.
- [x] (2026-10-08) [milestone-4] T6: Independent Standards and Spec reviews completed against the initial baseline. Spec reported zero findings; Standards found stale active-plan statements, assigned to coordinator repair R1.
- [x] (2026-10-08) [milestone-4] R1: Standards verified the reconciled active outcomes, context, historical observations, milestone prose, and next steps. No actionable issue remains.
- [x] (2026-10-08) [milestone-4] Completed one coordinated `update-agent-docs` pass with no KB edits warranted, final generated/link/diff checks, and the final documentation checkpoint.

## Surprises & Discoveries

- Initial source passes `rtk proxy python3 scripts/generate-hooks.py --check`: 35 generated files are current.
- Targeted Codex session correlation found 13 actual historical patch segment denials. Twelve reconstructed literal patches, 6,194-24,727 bytes and 124-523 lines, already parsed under the initial native-patch logic. Sampled installed guard logs instead showed 77,089-99,186-byte native patches denied by the former 65,536-byte budget. At diagnosis, installed Codex guard and policy fingerprints matched the initial repository source. After the completed repairs were installed, all nine changed hook/helper fingerprints matched the updated source.
- Tool Guardian already accepts Codex's exact `apply_patch` object with a string `command` field. A synthetic 143-line patch in that envelope passes; unsupported envelopes fall back to the 128-segment shell limit. Shape mismatches alone do not establish the reported cause.
- Secret scanning examines dirty repository state for every tool call. At the initial baseline, a safe read and a no-argument documentation request both reproduced generic denial with a safe file above 1 MiB, 257 untracked files, or a dirty tracked submodule. These remain candidate causes, not proof of the reported host's state; current incomplete responses expose safe typed diagnostics.
- `rtk` 0.51.0 is available. `rtk gain` cannot open its tracking database in this environment; normal prefixed commands work.

## Decision Log

- 2026-10-08: Use initial commit `72789d6978bb7255583f9fb1cd8e18c37fe3173b` as the fixed review point. "All changes" means this task's complete diff, including tests, generated output, and documentation.
- 2026-10-08: Work on base branch `codex/fix-hook-bug-reports`. Each source task uses a separate private worktree and branch. Rebase and fast-forward one completed task at a time; never push.
- 2026-10-08: Keep exact-schema classification and fail-closed limits. Decide patch grammar/provider changes from session evidence, current source, and official provider documentation, not guessed aliases or an arbitrary increase of every limit.
- 2026-10-08: Both reports are Copilot incidents. Its actual native tool arguments and 47 post/failure hook captures established `toolName: apply_patch`, `toolArgs: <raw patch string>`. The selected repair added only that exact scalar Copilot shape to native patch inspection. At diagnosis, the initial installed public prehook reproduced the segment denial on a harmless 143-line patch and missed raw protected-file delete operations. Both behaviors are corrected in the refreshed installed probes. Isolated live pre-tool probing lacked authentication, including existing `gh` auth; preserve this provider-delivery limitation without guessing aliases or object schemas.
- 2026-10-08: Set validated patches to 262,144 bytes (256 KiB): raw UTF-8 bytes for Copilot and aggregate string/key bytes for Codex's existing object schema. This covers observed Codex patches below 100 KiB with bounded growth headroom and prevents arbitrary shell limits on Copilot patch bodies. Other native data stays at 65,536 bytes; executable/strict text stays at 32,768 bytes; shell segment count stays at 128. Keep patch grammar unchanged. Express both early-stopped segment counters as lower bounds, not exact complete totals.
- 2026-10-08: Keep scanner repository-wide coverage and existing safety bounds unless a bounded diagnosis proves a behavior correction. Diagnostics use a fixed vocabulary and safe counts, never exception messages, subprocess stderr, file contents, or sensitive paths.
- 2026-10-08: Scanner repair is actionable incomplete-scan diagnostics, not a speculative scan-policy change. Dirty submodule support and exemptions for read-only tools are out of scope. Known safe requests in bounded repositories must pass; incomplete repository scans must continue denying with the cause and recovery action exposed safely.
- 2026-10-08: Retain this user-requested plan and sanitized evidence as the reviewable deliverable for this effort. Raw session logs remain outside version control.

## Outcomes & Retrospective

Both implementation tasks are integrated and installed with retained result evidence. T3 passed 22 native-data tests, 18 limit tests, 17 shell-data tests, 144 corpus fixtures, and 26 resource fixture decisions. T4 passed all three provider scanner/capture suites, the 32-test merge suite, and additional diagnostic controls. Integrated composed probes, provider/security/generator suites, disposable-home installer fixtures, installed subprocess controls, and all 108 resource cases passed. Independent review found no Spec issue and one Standards issue: stale active-plan status. Standards verified the repaired plan; no finding remains open. The final knowledge-maintenance pass admitted no new KB content because current rules already cover the changed behavior and source owns the exact schema/budget details. The isolated Copilot live probe could not authenticate; public hook subprocess evidence does not establish provider delivery or Windows behavior. The original external Linux scanner cause remains unknown. Approved native RSS collection succeeded after the sandbox denied `sysctl kern.clockrate`.

## Context and Orientation

The canonical hook implementations are Python renderers in `hooks/families/tool_guard.py` and `hooks/families/scan_secrets.py`. `scripts/generate-hooks.py --write` creates provider-local scripts. Never edit generated scripts directly. Tool Guardian's generated policy helper is identical under `.codex/hooks/helpers/`, `.copilot/hooks/scripts/helpers/`, and `.gemini/hooks/scripts/helpers/`. Each provider's `tool-guard.py` imports only its local helper; `scan-secrets.py` is separately generated for each provider.

Tool Guardian first validates a known provider argument shape, separates inert file data from operations, then applies either native-data bounds or strict executable inspection. `_parse_native_patch`, `_native_tool_shape`, `read_tool_scan_inputs`, `_command_segments`, `ScanLimitExceeded`, and safe denial formatting own the relevant behavior. Current shell limit is 128 segments; early stopping can produce a 129 sentinel rather than a complete count. Unknown fields and malformed syntax must retain strict inspection. Native patch delete and move-source protection must survive.

Secret scanning resolves a Git repository, enumerates staged/worktree/untracked candidates, captures Git output with bounded waits, reads bounded regular files, scans for credential patterns, and writes protected audit records. Incomplete scans now expose a fixed cause and operation, safe measurements when known, and fixed recovery advice. Unknown exceptions retain a sanitized internal-failure result. Repository limits remain 256 candidates, 1 MiB per file, 8 MiB total/captured output, and eight seconds. These are security boundaries; "benign request" does not imply a clean repository.

The source suites are in `scripts/test-tool-guard-*.py`, three `test-*-hooks-tool-guard.sh` scripts, `scripts/test-scan-secrets-capture.py`, `scripts/test-scan-secrets-merge.py`, three secret-scanner shell suites, and `scripts/test-security-banners.py`. Existing shared fixture modules should own reusable sanitized cases. New suites, if necessary, must be registered in `scripts/test-all.py`.

All commands below run from `/Users/adam/.codex/worktrees/2d9c/skills` unless a task worktree is specified. Use Python 3 and Bash through `rtk proxy`; use temporary homes and explicit writable audit/observability paths for tests. macOS is available; native Windows acceptance requires a separate Windows run.

## Plan of Work

### Milestone 1: Establish reproducible causes and bounded decisions

Status: done
Acceptance: met

T1 and T2 completed independent read-only diagnosis from the initial source and two bug reports. T1 retained `docs/hook-input-failures/guardian-evidence.md`; T2 retained `docs/hook-input-failures/scanner-evidence.md`. Neither edited source or this plan. Both invoked public provider hook subprocesses with synthetic fixtures before recommending fixes. T1 sampled bounded Codex and Copilot session sets, separated actual hook output from quoted reports, and retained only sanitized counts, sizes, shapes, and rule identifiers. T2 compared clean benign requests, definite fake-secret findings, and intentionally incomplete scans. Their retained reproductions and recommendations met the milestone's stop condition.

Initial-baseline acceptance evidence is retained in [guardian evidence](guardian-evidence.md) and [scanner evidence](scanner-evidence.md). Before the repair, public Codex fixtures allowed the 24,727-byte/523-line historical patch shape, denied synthetic equivalents of all four recent 77,089-99,186-byte cases, allowed an exact 65,536-byte aggregate, and denied 65,537 bytes. All three initial scanners allowed bounded clean/unborn fixtures and detected fake credentials; oversized candidates, excessive candidates, unsafe file types, and unavailable log storage reproduced generic incomplete denial. The repaired behavior is recorded under Milestones 2 and 3. Official Codex hook documentation at <https://learn.chatgpt.com/docs/hooks> specifies `tool_name: apply_patch` and `tool_input.command`; raw session tool-call input is not automatically the hook envelope.

### Milestone 2: Repair each hook with independent regression proof

Status: done
Acceptance: met

T3 completed after T1 evidence and the committed initial plan. It owned `hooks/families/tool_guard.py`, generated Guardian adapters/helpers, native/limit fixtures and tests, resource benchmarks, and `guardian-result.md`. The implementation recognizes exact Copilot raw `toolName: apply_patch` / `toolArgs: string` arguments and gives them the 262,144-byte patch budget shared with Codex's existing exact object schema. Raw patch bytes are bounded before parsing. Unsuccessful parsing retains strict scalar accounting; both early-stopped segment counters identify lower bounds. Unknown shapes, patch grammar, other budgets, and protected delete/move rules remain intact. Passing controls cover prose/YAML/shell examples, single/multi-file patches, observed sizes, late protected operations, malformed inputs, guessed schemas, UTF-8 boundaries, normalized limits, and executable inputs. Sentinel files remained unchanged on denial. Resource fixtures include high-line-count and malformed patches while preserving Copilot's separate 64 KiB writer bounds. The focused checks and scoped implementation commit met the task's stop condition.

T4 completed after T2 acceptance and the committed plan. It owned `hooks/families/scan_secrets.py`, three generated scanner adapters, scanner regression tests, and `scanner-result.md`. Typed causes now cover initialization, input, Git/capture, bounds, candidate safety/read, scan-log, and unexpected internal failures. Fixed recovery advice appears in block and warn responses; safe measurements also enter incomplete scan records when logging works. Diagnostic logging failure preserves the first cause. Passing controls cover missing Git, invalid payload, audit failure, timeout, capture corruption/overflow, HEAD failure, valid unborn repositories, and fake credentials. Unknown exceptions still deny without exposing raw exception text. The focused checks and scoped implementation commit met the task's stop condition.

T3/T4 used separate generated outputs and serialized shared generation work. Each worker activated `tdd` and `addy-security-and-hardening`. Implementation commits followed the invoked skill's `references/message.md`: Conventional Commit subject, Summary/Rationale/Tests body, and default Copilot co-author. Shared integration files stayed coordinator-owned. All branches remain unpushed.

### Milestone 3: Integrate and verify composed behavior

Status: done
Acceptance: met

T5 integrated the clean T3/T4 commits by rebasing each onto current base and fast-forwarding, without conflicts. Scoped source/test comparisons against the tested commits were empty. Both clean integrated task worktrees and branches remain because the app rejected archival as protected by a pinned task or workspace. Cleanup must use the app's archive operation when that protection no longer applies; do not bypass it.

Generator freshness and all applicable provider guard, native/shell/limit/corpus, scanner/capture/merge, shared banner, and generator suites passed. The checkout remained frozen for generator snapshot tests. Checks used disposable writable logs and asserted actual findings for fake-secret fixtures. Detailed task and integrated results are linked in `validation.md`.

Composed Copilot and Codex subprocess probes passed on the same benign repository and large valid patch request. A fake credential still produced scanner findings; oversized safe files produced the new bounded diagnostic. Focused Guardian suites retained executable and protected-operation denials. These probes establish public script behavior, not patch-executor transaction semantics or authenticated provider delivery.

The resource runner completed sequentially against frozen source with an approved native RSS collector. All 108 cases met the 500 ms finite-case ceiling; the maximum sample was 58.826750 ms. The artifact `/private/tmp/hook-input-resources.json` retains source fingerprints, first-process observations, 25 samples/three warmups, medians/p95/MAD, and separate RSS measurements. This is bounded-input evidence, not a baseline latency comparison or universal JSON-memory claim. Future latency comparisons must still follow the matched warm/cold procedure in `.agents/instructions/testing/hooks-security.md`.

Disposable-home installer fixtures and read-only installed configuration preflights passed before the approved `rtk proxy bash scripts/install.sh` refresh. All nine changed installed hook/helper files match source. Installed Copilot/Codex accept large native patches and deny late protected-file deletions with the sentinel intact. Installed scanners for all three providers deny oversized safe candidates with sanitized cause/count diagnostics and deny fake-secret findings without disclosing the value. No authenticated provider dispatch or native Windows claim follows from these direct probes. Codex trust review through `/hooks` remains user-owned if requested by the runtime.

### Milestone 4: Independent review and final checkpoint

Status: done
Acceptance: met

T6 completed two fresh independent reviews using `code-review-biaxis` against `72789d6978bb7255583f9fb1cd8e18c37fe3173b...5ce57e8784ad2b1243ef625e7f9dbf30bed4b958` and its matching commit list. Standards received applicable repository rules and the full smell baseline. Spec received both bug reports, the user's log-sampling request and Copilot clarification, and this plan. Standards found one documentation violation and no source/security issue. Spec found zero actionable mismatches and independently passed targeted Guardian and scanner controls. Reports remain separate.

R1 completed a bounded coordinator-owned documentation repair of this plan. Stale outcomes, initial installed-parity claims, old scanner behavior, completed-task imperatives, and obsolete next steps were replaced. Standards verified consistency with implementation and retained validation while preserving unavailable platform/provider gates. No source change or test weakening occurred; the original finding is resolved.

After all delegated work finished, the coordinator completed one `update-agent-docs` pass under the knowledge-admission rubric. Existing hook/security/test guidance remains accurate, and the scanner consistency memory still describes current limits. No new rule or memory was admitted; no canonical KB files changed, so OKF representation/lint work was unnecessary. Final generated freshness, artifact-link checks, and diff checks passed. Review and delegation records are retained beside this synchronized plan.

## Concrete Steps

Complete. Source, composed, generator, installer-fixture, installed, and bounded resource checks passed; see [validation](validation.md). Independent reviews completed against checkpoint `5ce57e8784ad2b1243ef625e7f9dbf30bed4b958`, and Standards verified the subsequent documentation repair; see [separate reports](review.md) and [delegation audit](delegation-audit.yml). Scanner integration is `f158f66471b3ef04f5105000f1ab77ccda546a89`; Guardian integration is `f0cca423acb598e2a3ee582d44e2de8cc49ee842`. No local implementation or verification task remains. Both clean integrated task worktrees and their branches remain protected by the app. Authenticated Copilot pre-tool delivery, native Windows, and the external Linux incident's exact scanner cause remain unverified; do not infer them from subprocess proof.

## Validation and Acceptance

Executed source gates include `rtk proxy python3 scripts/generate-hooks.py --check`, `rtk proxy python3 scripts/test-tool-guard-native-data.py`, `rtk proxy python3 scripts/test-tool-guard-shell-data.py`, `rtk proxy python3 scripts/test-tool-guard-limits.py`, `rtk proxy python3 scripts/test-tool-guard-false-positives.py`, `rtk proxy python3 scripts/test-scan-secrets-capture.py`, `rtk proxy python3 scripts/test-scan-secrets-merge.py`, `rtk proxy python3 scripts/test-security-banners.py`, and `rtk proxy python3 scripts/test-generate-hooks.py`. The task and integrated reports record provider shell suites and installer checks from the testing routes. Exit zero plus the intended public decisions establishes source acceptance; retained observations, not this command list alone, establish the result.

Retain failing-before/passing-after observations, integrated suite totals, exact commit identities, sanitized log-sampling scope, resource evidence when required, and separate installed/platform limitations. No real credential or raw session body belongs in a fixture, output, or commit.

## Idempotence and Recovery

Generator write mode is repeatable and touches only manifest-owned outputs. Keep implementation commits scoped and unpushed. If a task fails, leave its branch and evidence intact, reopen its Progress item, and repair in its own worktree. Never remove an unintegrated or dirty worktree. Failed or incomplete scans keep denying in block mode. Installation uses existing safe mergers and backups; do not bypass Codex hook trust or overwrite unrelated settings. Revert a verified bad implementation commit on the topic branch if recovery is needed; do not reset user work or modify unrelated branches.
