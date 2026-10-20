# Replace the legacy agent knowledge system with brain

This living ExecPlan is `brain/plans/01-brain-migration/ExecPlan.md`, associated with todo 1. Follow the `exec-plans`, `brain`, and `todo` skills. Keep the required living sections and milestone evidence current. The execution-plan contract requires a self-contained document, so this file intentionally exceeds the brain skill's usual note-length guideline.

## Purpose / Big Picture

Agents should find current repository guidance and durable knowledge through `brain/index.md`, maintain useful notes through brain skills, and discover new notes automatically. The repository should no longer depend on `.agents/instructions/`, `.agents/memory/`, `.agents/sources/`, source ingestion, or OKF enforcement. Existing useful knowledge must survive as concise, attributable notes; obsolete material must not survive merely because it existed.

Two portable hook behaviors will maintain the root index and inject that index into supported provider sessions. Copying a generated script and its provider registration into another repository must work with Python 3 and the standard library, without this repository's helper modules or shell utilities. Windows, Linux, and macOS are required targets.

### Current authorization and stopping boundary

On 2026-10-20 the user accepted decisions Q1-Q9 and confirmed the shared design. The user subsequently invoked execplan-implement, authorizing execution of the task graph. Repository implementation and isolated verification may proceed. On 2026-10-20 the user explicitly authorized committing and pushing the migration branch to run the native CI matrix. This supersedes the earlier commit/publication restriction. T7 and todo 1 must remain open until all remaining checks pass. Global installations remain out of scope. The user clarified that Copilot brain hooks belong only in repository `.github/hooks`, not global `.copilot/hooks`, and explicitly confirmed removal of global tool-guard registrations for all three providers ("Remove global tool guards intentionally"). Commit `a73a33c1` also removes brain registrations from all three global templates; preserve that repository-only boundary.

Future implementation is repository-scoped. Existing user-global installations must remain unchanged until the user explicitly reinstalls. Use isolated temporary destinations for installer validation. The old instruction to run the normal installer before live testing does not override this boundary.

## Progress

- [x] (2026-10-20) [milestone-0] Record the accepted decisions, current repository evidence, task graph, and validation contract.
- [x] (2026-10-20) [milestone-0] Create the plan and link it from the brain backlog and plans index.
- [x] (2026-10-20) [milestone-1] T1: Read all 62 legacy content files, 15 retired-skill files, and four ADRs; retain exact coverage in [[migration-map]].
- [x] (2026-10-20) [milestone-1] T1: Verify provider contracts and record user approval to index after every completed Codex tool call.
- [x] (2026-10-20) [milestone-2] T2: Add 19 topic notes and six investigation todos; verify wikilinks and permanent IDs.
- [x] (2026-10-20) [milestone-2] T2: Complete claim-to-destination review, preserve admission rules and missing lifecycle/Windows/loader contracts, and verify navigation. Active skill routing was completed in T6.
- [x] (2026-10-20) [milestone-3] T3: Deliver standalone index reconciliation with copied-process checks on macOS. Native OS/minimum-version proof remains in T7.
- [x] (2026-10-20) [milestone-3] T4: Deliver provider completion policies, startup/reset envelopes and safe statuses, and project/global lifecycle registrations; verify public process/config contracts locally.
- [x] (2026-10-20) [milestone-3] T5: Integrate exact provider arguments, pinned installed launches, Codex copy lists, and content-verified retirement cleanup. Verify isolated fresh/repeat installs and nested project launches locally.
- [x] (2026-10-20) [milestone-3] T5: Pass final Bash and PowerShell installer suites on macOS, including new Codex asset copies. Native platform/minimum-version and live provider acceptance remains T7.
- [x] (2026-10-20) [milestone-4] T6: Remove legacy content roots, retired skills, ingestion/OKF infrastructure and exclusive tests. Update active routing, replacement skills, historical ADR status and machine-owned root inventory; verify links and IDs.
- [x] (2026-10-20) [milestone-5] T7: Pass all 55 maintained suites on macOS, verify 62 generated outputs, complete documentation and reflection, and retain explicit platform skips.
- [x] (2026-10-20) [milestone-5] T7: Verify the six native Windows/Linux/macOS jobs on Python 3.12/3.14 for published commit `f49edd58ca048438636ae40024db2818b35f6a4f`; record platform skips.
- [x] (2026-10-20) [milestone-5] T7: Verify native Windows installer/security run `39510956697` succeeded for migration commit `f49edd58ca048438636ae40024db2818b35f6a4f`.
- [x] (2026-10-20) [milestone-3] T8: Reconcile repository-only brain hooks, intentional global guard removal, generated assets, and affected local checks.
- [ ] [milestone-3] T8: Publish the scoped correction and verify the native matrix, Windows installer, and macOS security workflows for the corrected commit.
- [x] (2026-10-20) [milestone-5] T7: Verify original macOS security run `39510956707` passed, including all 12 native Darwin capture cases and both installers.
- [ ] [milestone-5] T7: Verify corrected-tree CI and real provider startup/reset delivery in configured isolated profiles; then complete todo 1.

## Surprises & Discoveries

- Commit `54b6a74f853d174fe8de71e2e6eb42db69cf9e9f` introduced the new brain and skills. At baseline, the brain had principles, an empty plans index and no todos.
- At baseline, `docs/ideas/index.md` listed nine active and five archived idea files. Some active ideas explicitly require validation; archived does not necessarily mean completed, because the old workflow also archived ideas when a plan existed.
- The legacy roots contained routed policies, known issues, raw third-party sources, summaries and ingestion state. They cannot be copied wholesale without retaining obsolete representation and lifecycle assumptions.
- `hooks/manifest.py` owns generated provider files. Before cutover, source ingestion had six generated outputs and multiple canonical `auto_ingest*.py` modules. OKF had canonical families and generated helpers for several providers; T6 removed these exclusive assets.
- The original `scripts/test-all.py` registry included ingestion and OKF suites alongside unrelated suites. The current registry retains 55 surviving/new suites. It supports macOS/Linux, requires Python 3, Bash, Git, jq, flock, SQLite, and PowerShell 7+, and is not a native Windows runner.
- The upstream indexer uses Bash/POSIX utilities and rewrites a fixed-section root index. The upstream injector assumes plain stdout is injected as context. Neither script can be copied unchanged to all target providers and operating systems.
- Existing hook guidance requires standalone provider outputs, JSON-only stdout, UTF-8, bounded input completion without waiting indefinitely for EOF, and generator checks before installation. Retain these relevant constraints in brain notes and the replacement hooks.
- The initial `brain/todos.md` had a historical archive-path comment that differed from the todo skill's `brain/archive/todos.md` rule. Normalize that comment during migration, not by inventing a second archive convention.
- Initial exploration reported `rtk gain` could not initialize its tracking database. RTK reads, searches, and Git commands worked; tracking failure is not evidence of a repository test failure.

## Decision Log

All decisions below were accepted by the user on 2026-10-20. Preserve them unless the user changes scope.

| ID | Decision | Rationale |
| --- | --- | --- |
| Q1 | Update repository sources and installers; leave existing global installations untouched until explicit reinstall. | Keep rollout reviewable and avoid changing active environments. |
| Q2 | Remove ingestion gates, manifests, OKF linting, and dedicated hooks with the retired skills. | The new brain model replaces their representation and lifecycle. Preserve general checks and relevant guidance. |
| Q3 | Distill useful source knowledge into concise brain notes with provenance links; delete raw snapshots and ingestion bookkeeping after preserving unique relevant evidence. | Retain useful knowledge without maintaining a second source archive. Git history preserves historical snapshots. |
| Q4 | Convert active ideas to actionable todos, framing speculative ideas as investigations. Exclude completed or superseded archived ideas. | Preserve useful follow-up work without misrepresenting speculation as an implementation commitment. |
| Q5 | Require Python 3; provide two standalone standard-library scripts with explicit provider selection and provider-specific launch commands. | Native portability without Bash, jq, or repository helper dependencies. |
| Q6 | Automation fully owns `brain/index.md`, regenerating it deterministically from Markdown inventory. | Human explanations belong in topic notes and curated subindexes. Hooks make no semantic edits. |
| Q7 | Inject only the root index at session start and supported context-reset events. | Let agents retrieve relevant topics without repeatedly loading the entire vault. |
| Q8 | Reconcile before startup injection and after successful tool execution; for Codex, reconcile after every completed tool call, including failures. Write only on change. | Catch additions, deletions, renames, and partial changes from failed Codex calls. The user approved the Codex exception on 2026-10-20 because no universal success field exists. |
| Q9 | Require an end-of-session `reflect` review after code changes; persist only durable findings. Keep `meditate` and `ruminate` explicitly invoked. | Replace mandatory legacy KB review without requiring low-value writes or automatic semantic maintenance. |

The actual skill directory is `update-agent-docs`, despite the original request spelling it `update-agents-docs`. Remove the actual retired skill and fix references to either spelling where present.

## Outcomes & Retrospective

Implementation started on 2026-10-20 from clean branch codex/brain-system-migration at 092038394a2e3bb0cc21fffdec2eb60a12cece29. T1 and T2 are complete. T4 now supplies documented completion policies, startup/reset context and safe diagnostics, plus both installed and project registrations. T5 integrates pinned provider arguments, isolated installation and receipt-based retirement cleanup. The original 23 public brain checks passed on macOS/Python 3.14.6; the repository-only suite now passes 22 cases after removing its exclusive global-install test; generator and Codex merge checks pass. Final Bash and PowerShell installer suites passed on macOS. All six standalone native Windows/Linux/macOS jobs on Python 3.12/3.14 now pass for published commit `f49edd58ca048438636ae40024db2818b35f6a4f`, with explicit platform skips. Live provider delivery remains unverified. Milestone 3 contract and isolated installation acceptance is met. T6 cutover and T7 local integration are complete: all 55 maintained suites pass on macOS with explicit native-only skips. T7 remains open for corrected-tree workflow completion and real provider delivery proof. The migration branch is committed and pushed; global installations remain untouched.

## Context and Orientation

Working directory: `/Users/adam/.codex/worktrees/6578/skills`. Paths below are repository-relative. Read `AGENTS.md`, `brain/index.md`, and relevant topic notes before changing anything. Root brain navigation already links `brain/plans/index.md`, so adding this plan there makes it reachable without rebuilding the root index during planning.

The repository publishes skills from `skills/`, custom agents from `agents/`, project Copilot hooks from `.github/hooks/`, installed Copilot sources from `.copilot/hooks/`, Gemini hooks/config from `.gemini/`, and Codex hook sources from `.codex/`. Repo-local brain and retired KB skills are under `.agents/skills/`; do not confuse them with generated user-global custom agents.

Canonical hook renderers live in `hooks/families/`; `hooks/manifest.py:targets()` lists generated files. `hooks/providers.py` and `hooks/registrations.py` supply provider behavior and registrations. `scripts/generate-hooks.py` supports `--write` and `--check`. Generated provider files must not be hand-edited. The shared generator may reuse build-time code, but copied runtime scripts must be self-contained.

Inspect installer ownership through `scripts/install.sh`, `scripts/install.ps1`, `scripts/install-provider-hooks.py`, and `scripts/install-codex-hooks.py`. Preserve unrelated settings and runtime logs. Inspect `scripts/test-generate-hooks.py`, `scripts/test-install-codex-hooks.py`, `scripts/test-install.sh`, `scripts/test-install.ps1`, and `scripts/probe-provider-hook-delivery.py` before extending their relevant contracts.

### Migration map

T1 completed the file-by-file disposition ledger at `brain/plans/01-brain-migration/migration-map.md`, linked from the plans index. T6 executed its dispositions after the coverage review. Each row records original path, keep/merge/drop decision, destination or deletion reason, provenance, and verification status. Include all file types, not just Markdown. This ledger replaces no ingestion runtime and is only migration evidence.

| Source | Intended disposition |
| --- | --- |
| `.agents/instructions/repo.md`, `agents.md`, `skills.md`, `scripts.md`, `powershell.md` | Concise topic notes under `brain/codebase/`, preserving current conventions and correcting obsolete paths. |
| `.agents/instructions/hooks*.md`, excluding ingestion and OKF specifics | Split by shared rules, provider, security, and observability under `brain/codebase/`; preserve official reference URLs. |
| `.agents/instructions/testing.md`, `testing/*` | Preserve applicable validation guidance by topic; drop only checks exclusive to retired features. |
| `.agents/instructions/knowledge-base.md`, `INDEX.md`, ingestion and OKF guides | Retire legacy format/routing/lifecycle rules; extract any independently useful guidance before removal. |
| `.agents/memory/known-issues/*` | Revalidate against current code; keep unresolved issues and useful constraints in topic notes or todos. |
| `.agents/memory/sources/*.summary.md` and `.agents/sources/*` | Merge relevant knowledge into topic notes, preserving source URLs and unique evidence; discard superseded or irrelevant details. |
| `.agents/memory/LOG.md`, source manifest, legacy indexes | Extract durable facts if any, then delete lifecycle bookkeeping and routing. |
| `docs/ideas/*.md`, `docs/ideas/archive/*.md` | Triage each idea; assign permanent todo IDs to useful work and link necessary context notes. Remove superseded idea documents after coverage verification. |

The nine active ideas concern source-injection manifests, wayfinder/grilling, pre-commit hooks, agent memory, software-factory workflows, durable learning, just-in-time context, nested AGENTS files, and skill auditing. Do not create a todo for source-ingestion repair if removing ingestion already resolves it. Revalidate the five archived files before deciding whether they are completed, superseded, or still contain useful work.

### Source references and verification status

T1 verified provider schemas and lifecycle mappings against the following official references and recorded installed CLI versions. A copied summary or contract test does not establish deployed behavior.

- Upstream behavior examples: [auto-index-brain.sh](https://github.com/poteto/noodle/blob/main/.agents/hooks/auto-index-brain.sh), [inject-brain.sh](https://github.com/poteto/noodle/blob/main/.agents/hooks/inject-brain.sh).
- Copilot: [hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference).
- Codex: [hooks documentation](https://learn.chatgpt.com/docs/hooks).
- Gemini: [hooks overview](https://geminicli.com/docs/hooks/), [best practices](https://geminicli.com/docs/hooks/best-practices/). Additional exact references are in the existing Gemini source snapshots and must be retained before their removal.

Discovery reported Copilot startup `additionalContext`, Codex `SessionStart` context injection including compact/reset sources, and Gemini JSON `hookSpecificOutput.additionalContext`. Provider contracts are recorded below; actual delivery and reset behavior remain live verification tasks. Do not infer provider equivalence from similar event names.

## Plan of Work

### Milestone 0: Establish the implementation contract
Status: done
Acceptance: met

The accepted design, ownership boundary, proposed interfaces, dependencies, and verification criteria are captured here. Todo 1 and the plans index link to the plan. Acceptance is document creation and navigation validation, not implementation approval or executable verification.

### Milestone 1: Account for content and verify lifecycle feasibility
Status: done
Acceptance: met

#### T1: Inventory and contract verification

Prerequisites: satisfied by the user's execplan-implement invocation. Recheck the worktree and read the plan against current files. Inventory tracked legacy files, retired skills and their support files, idea documents, and every active path/skill reference. Exclude untracked skill benchmark workspaces from bulk searches; do not delete unrelated workspace data.

Produce the disposition ledger described above. Read each source before assigning a decision. Resolve copied policy conflicts against current code and the accepted design. Review existing ADRs, especially ingestion decisions, and mark superseded guidance as historical rather than rewriting historical claims to appear current.

Verify official provider contracts, record exact event names, success detection, root fields/environment variables, output envelopes, launch commands, timeout units, and supported reset events in a provider table in this plan. Establish how index refresh is guaranteed to precede injection. Do not rely on configuration array order unless documented and demonstrated. If necessary, the injector can perform the same embedded reconciliation before reading, while remaining independently copyable. This is still two public hook behaviors, not a third helper dependency.

Acceptance: every legacy file has a proposed destination or reason for deletion; each supported provider has a feasible, documented lifecycle mapping. Any unsupported capability must be surfaced as a limitation before claiming parity or silently substituting per-prompt injection. Stop dependent implementation if a required lifecycle behavior cannot be delivered.

### Milestone 2: Preserve useful knowledge and backlog
Status: done
Acceptance: met

#### T2: Migrate content additively

Prerequisite: T1 content inventory (verified); provider success-policy verification is independent. Use `brain` for durable notes and `todo` for backlog changes. Merge duplicate material, split notes by topic, retain source URLs next to derived claims, and omit obsolete frontmatter/OKF typing. Prefer existing principles when they already cover the lesson. Keep most notes around 50 lines; use link-only category indexes as necessary.

Read all active and archived ideas. Allocate todo IDs from the next-id marker without renumbering; distinguish investigation from implementation. Preserve still-useful context through linked notes, and record skipped ideas with a reason in the ledger. Normalize the stale archive-path comment to the todo skill's convention.

Update human navigation enough to make every new file reachable before automatic indexing exists. Verify every retained legacy assertion has a destination, every source-derived note has usable attribution, every todo link resolves, and no old policy silently overrides the accepted design. Keep legacy originals until T6's deletion gate.

Acceptance: the completed ledger accounts for the full source inventory; a reader can find retained knowledge and useful follow-up work through the brain without consulting the legacy roots.

### Milestone 3: Deliver portable index and context hooks
Status: in progress
Acceptance: not met

#### T3: Implement index reconciliation

Prerequisite: T1 root/input feasibility verified (all providers supply absolute cwd); full content inventory is independent of index reconciliation. Add canonical generation in `hooks/families/brain.py` (proposed new file) and targets in `hooks/manifest.py:targets()`. Public generated entrypoint: `auto-index-brain.py`. Use the existing generator structure, with provider-local files containing all needed runtime logic.

Use Python standard-library filesystem and JSON operations. Resolve repository identity from validated provider context, never from the installed script location. Respect worktrees and nested working directories. An absent brain is a quiet no-op; an existing brain with a missing root index can be indexed. Never create a brain in an unrelated repository.

Generate sorted vault-relative wikilinks for Markdown files, excluding only the root index itself. Include nested indexes and plans/archive notes, grouped deterministically by directory so all files remain discoverable. Keep human-edited subindexes untouched. Define handling for filenames containing wikilink metacharacters without emitting broken links. Do not follow symlink directories or traverse outside the vault. Read no note bodies merely to build the inventory.

Compare rendered bytes before writing. Replace atomically through a same-directory temporary file, clean up temporary files, and prevent concurrent invocations from corrupting or overwriting a newer inventory with stale results. Bound input and filesystem work; errors must preserve the previous index and report a concise stderr diagnostic without blocking ordinary agent work or leaking note contents.

#### T4: Implement injection and provider adapters

Prerequisites: T1 and T3's reconciliation contract. Public generated entrypoint: `inject-brain.py`. Emit only the root index as context, in the verified provider-specific JSON envelope. Logs go to stderr. Support explicit provider selection as accepted in Q5, using values `copilot`, `codex`, and `gemini`; the GitHub project variant uses Copilot's verified contract.

Register startup/reset injection and post-tool reconciliation under Q8 (every completed Codex call; successful calls for the other providers) in repository provider configurations. `hooks/registrations.py` owns global installer identities and must retire, rather than add, the former global brain registrations. Reconcile before reading the startup index. Do not inject on every prompt or every tool call. For Copilot and Gemini, recognize success through provider evidence, including shell tools, rather than editor tool names. Codex requires no success inference.

Use provider context limits where available and bound outputs without emitting malformed JSON or broken UTF-8. Preserve index content under normal limits; if a limit prevents full injection, provide a clear route to `brain/index.md` and record the limitation. Missing or unreadable input must not accidentally inject another repository's index. Keep lifecycle diagnostics consistent with retained local conventions and keep routine tool-pass output quiet.

#### T5: Integrate generation and isolated installation

Prerequisites: T3 and T4. Emit both scripts under `.github/hooks/scripts/`, `.gemini/hooks/scripts/`, and `.codex/hooks/`, with corresponding project registrations in `.github/hooks/hooks.json`, `.gemini/settings.json`, and `.codex/hooks.json`. Do not emit Copilot brain hooks into the global `.copilot/hooks` tree. Global templates `.copilot/hooks/hooks.json`, `.gemini/global-settings.json`, and `.codex/global-hooks.json` intentionally omit brain and tool-guard registrations. The Codex global file is an installer input, not a Codex-discovered runtime file.

Each script must run after being copied alone with its registration; no sibling import, third-party package, Bash, Git, jq, or RTK may be required at runtime. Build-time reuse is encouraged. Follow existing executable-mode and launcher conventions, including Windows Python invocation and paths containing spaces.

Extend isolated installer fixtures to prove fresh installs and upgrades converge, retired owned files are removed on explicit reinstall, unrelated user configuration/logs survive, and repeated installs are idempotent. Do not run the normal installer against the actual home directory. Do not repurpose `$HOME` or `$CODEX_HOME` as shell scratch variables; use existing test isolation mechanisms or explicit temporary destinations.

Acceptance for milestone 3: generated artifacts are current; a fresh temporary vault is indexed before its startup context is returned; successful add/rename/delete actions reconcile the index; unchanged runs do not rewrite it; copied scripts work independently. Record per-provider and per-platform results, distinguishing payload-contract tests from real CLI delivery.

### Milestone 4: Retire the old system and update consumers
Status: done
Acceptance: met

#### T6: Perform the cutover

Prerequisites: T2 and T5 accepted. Remove `.agents/skills/clean-agent-docs/`, `.agents/skills/okf-authoring/`, `.agents/skills/update-agent-docs/`, and `.agents/skills/ingest-source/`, including exclusively owned support files. Find other maintained published copies and references before removing them. Do not remove the entire `.agents/` tree; replacement skills still live there.

Remove canonical `hooks/families/auto_ingest*.py`, exclusively owned OKF family/runtime files, corresponding generated manifest targets and registrations, and obsolete linter/gate entrypoints including `scripts/lint-okf.py`. Shared utilities remain if other hook families use them. Remove exclusively obsolete test suites and fixture registrations from `scripts/test-all.py`; preserve mixed-suite coverage of surviving behavior. Do not write regression tests for feature deletion or weaken unrelated failing tests.

Update `AGENTS.md`, `README.md`, affected skills such as `skills/default/create-skill/SKILL.md`, installer manifests, script consumers, test fixtures, and documentation links. Relevant brain guidance replaces old routing and raw-source authority rules. Official upstream documentation becomes the precise provider-contract reference after snapshots are removed.

Encode mandatory end-of-session reflection after code changes in the maintained instruction/skill locations that own that workflow. Review does not require a write when there is no durable finding. Do not automatically invoke `meditate` or `ruminate`; keep hooks strictly mechanical. Adapt incompatible tool assumptions in replacement skills only as necessary for this workflow, following the skill-authoring guidance when editing them.

Before deleting originals, verify completed ledger coverage, destination links, provenance, new hook acceptance, and absence of active dependencies. Then remove `.agents/instructions/`, `.agents/memory/`, `.agents/sources/`, and superseded `docs/ideas/` content. Git history supplies historical recovery; do not introduce another raw-source archive.

Acceptance: all three legacy roots are absent; active runtime/config/skill references no longer require them or retired skills; useful knowledge and todos remain reachable; historical mentions are clearly historical. Audit remaining references individually rather than blindly rewriting history or unrelated fixtures.

### Milestone 5: Prove the integrated result
Status: in progress
Acceptance: not met

#### T7: Validate and document the cutover

Prerequisite: T6. Run the validation below on the integrated tree. Repair relevant failures without skipping or weakening surviving tests. Confirm standalone script portability on native Windows, Linux, and macOS; a mocked Windows path on macOS is not Windows runtime evidence.

Document Python prerequisites, copy/paste installation examples for every provider, index ownership, lifecycle behavior, reset limitations, explicit reinstall behavior, and recovery. Use an isolated provider profile or temporary project for live delivery checks. If isolation cannot be established, report live verification as pending instead of changing the user's active installation.

Perform the required reflection review and record only durable findings in the brain. Update this plan's acceptance/evidence and the disposition ledger. Mark todo 1 complete only after the user outcome is delivered and required checks pass; use the todo skill's archive convention. Do not commit or deploy unless subsequently requested.

Acceptance: integrated checks pass with actual output recorded, no required platform/provider result is falsely claimed, migration coverage is complete, and normal repository workflows operate without the legacy knowledge system. Missing native environments or CLI access leave the corresponding acceptance open.

#### T8: Reconcile repository-only brain hooks and intentional global guard removal

Prerequisites: the user's scope correction and commit `a73a33c1`. Keep Copilot brain scripts and registrations in `.github/hooks`; remove their duplicate `.copilot/hooks` outputs and generated targets. Preserve removal of brain and tool-guard registrations from all global templates. Reconcile installer ownership identities, generated diagnostics, documentation, and affected tests with that boundary. Keep direct guard-runtime tests and surviving installer preservation/idempotence checks. Recovery tests invoke installed guard scripts explicitly; registered launch-identity checks use the surviving scan-status handlers. Remove only assertions that require deleted automatic global registrations. Do not add regression tests for deleted features.

Verification: reproduce the six stale generated outputs with `scripts/generate-hooks.py --check` and the obsolete installed-brain expectations with `scripts/test-brain-hooks.py` before editing. Regenerate, run affected process/generator/installer/recovery suites, then commit and push the scoped repair and inspect native CI. The three failed workflows for `a73a33c1` stop at generated freshness; the earlier green native matrix and Windows workflow for `f49edd58` do not prove the new tree. T7 stays open until current-tree checks and live-provider verification pass.

## Task Graph and Ownership

T1 content inventory precedes T2. T1 root/input feasibility precedes T3 and is verified; the Codex completion policy is now approved, satisfying the remaining T1 prerequisite for T4. T4 depends on T1 and T3's contract. T5 depends on T3 and T4. T6 depends on T2 and T5. T7 depends on T6. One implementing owner integrates shared manifests, configuration, indexes, installer changes, and documentation. The invoked execplan-implement skill authorizes scoped delegation. Two read-only T1 assignments collect content and provider evidence; the coordinator owns repository integration. Routing selected gpt-6-luna/max (Standard), with gpt-5.6-luna/max as fallback: substantive cross-file judgments require Standard; published rates provisionally favor Luna. Runtime accepts both settings, but actual execution settings are unconfirmed. Each assignment has a 12-minute warning threshold. No delegated implementation worktrees or commits have been created.

## Concrete Steps

The current published head is `a73a33c16f69c50f03b09137f95fdc0572717a70`. Its three CI workflows fail generated freshness after global templates changed. The T8 correction is now verified locally: duplicate Copilot global brain assets are removed, ownership/tests align with repository-only brain registrations and intentionally removed global guards, and 60 generated outputs are current. The next executor action is to commit and push this scoped correction, then verify all three native workflows for that new commit. Earlier commit `f49edd58` passed the six-job brain matrix, Windows installer workflow, and complete macOS security workflow. These results do not replace corrected-tree CI. Keep T7 and todo 1 open; earlier passes are historical evidence, not current-tree acceptance.

Then verify actual startup/reset delivery in isolated configured provider profiles. The previous isolated Copilot probe lacked authentication, Codex isolated hook trust has not been established, and Gemini CLI is absent. Copilot is 1.0.101 and Codex is 0.163.0; version checks provide no delivery proof. Git push and GitHub Actions reads now work under the authorized execution context, so the earlier GitHub authentication error no longer blocks CI inspection. Do not bypass trust or modify active user-global installs. Commit and push are authorized; no merge or global installation is authorized.

Use RTK-prefixed repository commands. Start with `rtk git status --short`, `rtk git rev-parse HEAD`, and scoped tracked-file inventories. Record the starting commit and unrelated work before modifications. For searches use `rtk proxy rg`, excluding benchmark workspaces and generated logs. The migration ledger must include files discoverable by Git even when default search ignore rules hide them.

After implementation changes to canonical hook sources, run `rtk python3 scripts/generate-hooks.py --write`, followed by `rtk python3 scripts/generate-hooks.py --check`. Expect zero exit and no stale generated output. The write command is authorized during implementation.

## Validation and Acceptance

### Test boundaries and workflow

Proposed public test seams are generated hook process stdin/stdout plus observable vault files; provider registration/generation output; and installer behavior in isolated destinations. These catch protocol, lifecycle, portability, and rollout failures. They do not establish actual CLI context delivery without live probes. Avoid testing private rendering functions as substitutes for these outcomes.

The user confirmed all three proposed public test boundaries on 2026-10-20. The TDD seam prerequisite is satisfied. For new executable behavior, use one failing public-behavior test followed by the minimal implementation, repeating in vertical slices. Do not add tests that only assert removed features remain absent.

### Published native matrix evidence (2026-10-20)

`rtk gh run view 39510956769 --json jobs,conclusion,headSha,url` reports success for all six combinations of `windows-latest`, `ubuntu-latest`, and `macos-latest` with Python 3.12 and 3.14. The run's exact head is `f49edd58ca048438636ae40024db2818b35f6a4f`. Every job passed generated-output verification (`62 files`) and the 23-case standalone process suite. Windows reports two skipped cases per job, Ubuntu one, and macOS none. The suite retains its explicit POSIX permission-fixture and unsupported-interpreter availability limits; passing jobs do not establish skipped behavior. No test was changed or bypassed for this run.

Evidence: [native matrix run](https://github.com/japurcell/skills/actions/runs/39510956769); retained log `/tmp/brain-native-matrix-39510956769.log`. This proves the copied scripts execute under the native operating systems and minimum supported Python. It does not prove actual provider context delivery. The related [Windows installer workflow](https://github.com/japurcell/skills/actions/runs/39510956697) passed at the same commit, including every workflow step: native PowerShell installation, Windows scanner envelopes/capture, stable RTK configuration, and lifecycle messages. Its log is retained at `/tmp/brain-windows-installer-39510956697.log`. The [macOS security workflow](https://github.com/japurcell/skills/actions/runs/39510956707) also passed completely for the original migration commit, including all 12 required native Darwin capture cases, Bash and PowerShell installers, and final generated freshness. Its retained log is `/tmp/brain-macos-security-39510956707.log`. No source or test fix was needed for that original commit. The later `a73a33c1` template edits require the T8 correction and fresh CI before current-tree acceptance.

### Behavioral scenarios

Create a temporary repository with a brain containing a principle, nested codebase note, and this kind of plan. Invoke startup through each provider's actual registered command with representative JSON. Expect a complete index to exist before returned context is decoded, and expect only index text in the provider context field.

Exercise creation, rename, and deletion via editor and shell tool events, failed tool execution, unchanged inventory, missing brain, missing index, malformed input, open stdin, Unicode and spaces in paths, Windows drive paths, nested cwd, worktrees, concurrent invocations, read-only index destinations, and symlink escapes. Expectations follow the contract above, including no-op behavior, bounded completion, atomic preservation, and no unrelated file mutation.

Copy each generated script alone into a fresh temporary project and run it without repository helpers or package dependencies. Verify both scripts independently. Exercise supported reset/compaction events separately from startup and record any provider-version limitation.

### Commands and evidence

All commands below run from the repository root. New test paths are proposed deliverables, not existing successful checks.

- `rtk python3 scripts/test-brain-hooks.py`: proposed new cross-platform subprocess contract suite for the two public scripts and provider payloads. Expected exit 0.
- `rtk python3 scripts/test-generate-hooks.py`: generation and target ownership consistency. Expected exit 0.
- `rtk python3 scripts/test-install-codex-hooks.py`: isolated Codex installation/upgrade preservation. Expected exit 0.
- `rtk bash scripts/test-install.sh` and `rtk pwsh -NoProfile -File scripts/test-install.ps1`: existing installer suites, extended only for surviving/new behavior. Verify isolation before running. Expected exit 0.
- `rtk python3 scripts/generate-hooks.py --check`: expected exit 0 and no stale output after generation.
- `rtk python3 scripts/test-all.py --list`: confirm the maintained suite registry resolves and contains the new suite, with retired-only suites removed.
- `rtk python3 scripts/test-all.py`: full maintained suite on supported macOS/Linux hosts. Expected exit 0; dependency errors and visible platform skips are not passes.
- On native Windows, run the new subprocess suite with `py -3 scripts/test-brain-hooks.py` and the relevant PowerShell installer/hook suites through RTK where available. Use native Linux/macOS Python launchers for their equivalent evidence.
- `rtk git diff --check`: expected no whitespace errors. Review `rtk git diff --stat` and scoped diffs for unintended changes.

Validate brain wikilink resolution using the brain skill's same-directory, relative, then vault-root order, stripping heading anchors. Check reachability from the root, permanent todo IDs, full source-ledger coverage, source attribution, directory removal, and active-reference cleanup as migration acceptance checks rather than permanent deletion regression tests.

Record command, OS, Python/provider version, exit status, and the smallest decisive result for each check. Keep platform limitations explicit. The full repository suite passing does not prove native Windows operation or actual provider injection. Baseline on macOS 26.7.1 arm64, Python 3.14.6: `rtk python3 scripts/generate-hooks.py --check` exited 0, reporting 68 current generated files. The copied-script process suite now passes 23 cases on macOS/Python 3.14.6, including inventory, symlinks, lock contention, special filenames, startup JSON, limits, event guards, retained stdin, nested/worktree roots, read-only destinations, and rejecting Python 3.9.6. The pre-cutover generator suite passed 27 cases with inventory 76; after retiring 14 unused outputs and two retired-family cases, the suite passed 25 cases with inventory 62. The suite-registry tests passed all 14 cases after registering the new suite. Brain reachability, wikilink resolution, todo IDs, and exact one-row coverage for all 62 legacy content paths passed. These results are not native Windows/Linux or live provider proof. Local native Linux/Windows runners and Gemini CLI remain unavailable, but the published matrix now supplies native standalone-hook evidence. Actual provider delivery remains pending.

## Idempotence and Recovery

Preserve unrelated work. Make content migration additive until coverage is verified; do not delete original knowledge before retained content is reachable. Repeated index runs and isolated reinstalls must converge without unnecessary writes or duplicate registrations. Allocate todo IDs once and record mappings so retries do not create duplicate todos.

Use atomic index replacement and bounded coordination to preserve the last valid index after interruptions. A hook failure must not trigger semantic edits or a blocking ingestion-style repair loop. A later successful invocation should repair index drift.

If cutover fails, restore only the affected tracked files from the recorded starting commit or the user's reviewed migration commit, after checking for newer edits. Do not use broad reset/clean commands or revert unrelated changes. Restore coherent configuration and generated targets together. Because actual global installations are untouched, repository recovery does not require modifying the user's installed hooks.

## Interfaces and Dependencies

Public script names: `auto-index-brain.py` and `inject-brain.py`. Explicit provider option: `--provider copilot|codex|gemini`. Inputs are the verified provider hook JSON and documented environment context; outputs are valid provider JSON on stdout and bounded diagnostic text on stderr. The filesystem boundary is the selected repository's `brain/` directory. Python's standard library is the only runtime library dependency.

Generation may share reconciliation and parsing source internally, but each emitted file must embed what it needs. No runtime import from `hooks/`, sibling helper files, or another provider tree is permitted. Python >=3.12 is the selected floor. Python 3.14.6 behavior and Python 3.9.6 rejection are verified locally. The published brain-hooks workflow passed on native Windows/Linux/macOS with Python 3.12 and 3.14; platform-specific skips are recorded below.

The verified provider table below and `docs/brain-hooks.md` describe launcher commands, event identifiers, limits and root resolution. Startup injection performs embedded reconciliation itself; it must not rely on separate handlers running in configuration order. Their verification is a bounded prerequisite, not permission to revise accepted lifecycle behavior silently.

## Verified provider contract checkpoint (2026-10-20)

| Provider | Event/context | Completion and limits |
| --- | --- | --- |
| Copilot | sessionStart startup/resume/new; top-level additionalContext; cwd input | postToolUse reports toolResult.resultType success; failures have a separate event. bash/powershell launch; timeoutSec seconds. |
| Codex | SessionStart startup/resume/clear/compact/fork; hookSpecificOutput with hookEventName and additionalContext; cwd input | PostToolUse includes failed Bash and has tool-specific responses without a documented universal success flag. command/commandWindows; timeout seconds. |
| Gemini | SessionStart startup/resume/clear; hookSpecificOutput.additionalContext; cwd input | AfterTool has optional tool_response.error. PreCompress is notification-only. command is host-native; timeout milliseconds. |

Official sources are linked above. Copilot CLI 1.0.100 and Codex CLI 0.163.0 are installed; no live delivery is claimed. New scripts target Python >=3.12, matching the maintained security installer's floor, with native minimum-version verification now passing in the published matrix. The injector reconciles internally before emitting context. Existing nearest Git boundaries prevent a nested unrelated repository from inheriting an ancestor vault. No script uses its installed location to find a vault.

Index bounds: 20,000 scanned entries, two-second inventory deadline, 512 KiB rendered index, 24,000-byte injection budget. Oversized injection returns a pointer to the complete disk index. Invalid inventory preserves the previous index. A persistent kernel-released `.brain-index.lock` serializes scans and atomic writes with a 300 ms wait; ignore it in version control. Wikilink metacharacters use encoded ordinary Markdown destinations.

## Current base state and remaining ownership

Reflection review: the durable correction is captured in `brain/codebase/hooks-copilot.md` and `brain/codebase/hooks.md`. Repository and user-level hook paths define deployment scope; shared runtime behavior does not justify registering repository maintenance globally. No skill-file update or new backlog item is needed.

- Branch: `codex/brain-system-migration`; published migration HEAD is `f49edd58ca048438636ae40024db2818b35f6a4f`, based on `092038394a2e3bb0cc21fffdec2eb60a12cece29`. Commit and push are authorized. No private implementation worktrees or global installations were changed.
- New public entrypoints exist in all four provider trees and are registered in project configuration and installed templates. Copilot filters successful tool results; Gemini filters error results; Codex indexes every completed call. No actual user-global install was changed.
- Canonical implementation: `hooks/families/brain.py`; subprocess suite: `scripts/test-brain-hooks.py`. `scripts/test-all.py` includes the new suite. `.github/workflows/brain-hooks.yml` passed all six native platform/version jobs in run `39510956769`.
- Generation updates diagnostic/build fingerprints and registration receipts because canonical sources and templates changed. Installer E2E verification reproduced removal of the existing tool guard by incomplete maintained templates; all three templates now preserve that security registration. Security enforcement logic is unchanged; diagnostic collectors now recognize exact brain launch arguments.
- Sandbox initially denied generator staging in `.codex`; scoped elevated regeneration succeeded. The failed generator rolled back, and subsequent freshness checks passed.
- Current local correction: repository brain suite 22 cases, generator 25 cases, recovery 17 cases, lifecycle 32 cases, Codex merge CLI, and complete Bash installer pass. The lifecycle suite initially hit sandbox-only `/bin/ps` denial; its elevated rerun passed unchanged. Complete PowerShell installation, security banners (14 cases), and diagnostics (10 cases) also pass. Corrected native CI remains pending. No global installation was changed.
- The user approved mechanical Codex reconciliation on every completed call, including failures, on 2026-10-20. No completion-policy decision remains pending. The subsequent execplan-implement invocation resumes execution after T2.
- Native standalone Windows/Linux/macOS and Python 3.12/3.14 matrix evidence is verified. The original related Windows installer/security and macOS security workflows both passed. Corrected-tree CI remains pending. Real provider startup/reset delivery remains unverified. Existing global installations must stay untouched.
- Retired skills, source ingestion/OKF families/adapters, all three legacy content roots and `docs/ideas` are removed. The corrected generator owns 60 surviving outputs; its post-cutover suite passes 25 cases after removing only two retired-family tests. The full maintained runner passes all 55 suites on macOS.
- Reflection review: durable generator serialization, standalone input rules, provider schema limits, and source-versus-live verification distinctions are retained in codebase notes. No speculative session narrative was added as knowledge.

## T2 final coverage evidence (2026-10-20)

Final validation passed: all 40 brain Markdown files are reachable from the root, every wikilink resolves, and all 62 tracked legacy content files have exactly one disposition row. `rtk git diff --check` passed.

A read-only review compared all 19 topic notes, the codebase index, and todos with the complete migration ledger and nine raw snapshots. The coordinator restored the missing shared lifecycle-message policy, Windows path/command lookup rules, and required-skill loader output contract. The loader remains active and its generated output confirms the preserved fields. Version-sensitive Gemini telemetry detail is not promoted to a current claim without fresh verification; the retained no-raw-input logging rule covers the durable privacy requirement. Knowledge admission rules are retained in `brain/codebase/knowledge-maintenance.md`; active skill integration belongs to T6. The later T6 gate passed and originals were removed after this content-preservation review.

## T4/T5 integration evidence (2026-10-20)

The public completion-policy test failed for Copilot/Gemini errors and unrelated Codex events before filtering, then passed. Startup/reset status and maintained-template tests likewise failed before their implementation. All 23 `scripts/test-brain-hooks.py` cases now pass, including each independently copied artifact with a fresh index, all documented reset sources, large-index fallback, exact provider completion rules, nested project launchers without Git, and pinned/idempotent isolated installs for three providers. Copilot progress lines precede exactly one final JSON document; Codex/Gemini use safe `systemMessage`. Codex handlers set `additionalContextLimit: 0` because the script enforces its own 24,000-byte cap.

`rtk python3 scripts/test-install-codex-hooks.py` passes. `rtk python3 scripts/test-generate-hooks.py` passes 27 cases; registry tests pass 14. The Bash E2E installer initially failed with missing `PreToolUse`, reproducing loss of the installed guard when a maintained template omitted it. Codex, Copilot and Gemini templates now retain the guard; a subsequent Bash run passed. The PowerShell run reached its old positional startup assertion, which failed after the new injector was added; that assertion now selects the required-skill handler by its command and still requires exactly one. Final full installer reruns passed: Bash exit 0; PowerShell exit 0 with explicit native Windows DACL/junction skips.

An isolated one-off public installer exercise verified receipt-owned old Codex/Gemini assets are removed, modified assets and custom hooks/logs survive, and repeated installs keep configuration bytes unchanged. No permanent deletion regression test was added. Retirement checks reject linked ancestors and non-private/nonregular assets, bound input size, and compare known SHA-256 receipts before deletion. Only explicit reinstall invokes cleanup. The receipt list covers the migration-boundary assets; modified or unrecognized older assets remain for manual review.

Setup, limits, provider examples, reset limitations and recovery are documented in `docs/brain-hooks.md` and linked from README. Native OS, minimum-version and actual provider delivery evidence remains missing. None of these local results establishes it.

Decision checkpoint (2026-10-20): T5 proves replacement process/config/install contracts on the available host. T7 retains the original native Windows/Linux/macOS, minimum Python and live-delivery obligations. No missing proof is waived or claimed; T6 can now retire the old source as the original task graph intends. The final deletion preflight reconfirmed exact ledger coverage for 62 files and full brain navigation.

## T6 cutover and T7 current evidence (2026-10-20)

Cutover removed 37 explicitly owned source/runtime/test files, the retired skill bundles, all three legacy content roots, the superseded idea directory and exclusive OKF fixtures. Shared common/audit families remain for surviving providers; their now-unused GitHub helper outputs were removed. Mixed startup/lifecycle suites retain required-skill and security behavior. The Windows workflow no longer calls the removed OKF suite. README, create-skill routing and the live installer architecture eval point to brain notes. Historical dotnet migration validation is labeled historical; ADRs 0001/0002 are superseded. A generic cleanup fixture's `okf-authoring-workspace` name is only disposable test data, not an active retired-skill dependency.

AGENTS.md now requires end-session reflect review with no-write permitted; brain owns evidence admission and machine-index rules. Reflect, meditate and ruminate use available task/delegation tools rather than requiring unavailable harness APIs; meditate respects user commit authorization. Both explicit-only skills retain `disable-model-invocation: true`. Quick validation initially rejected meditate/ruminate because of the documented metadata allowlist incompatibility. The existing CLI reproducer failed before the allowlist correction and passes afterward. Official Claude Code documentation confirms the explicit-only field; the validator now admits that field without removing the invocation control. Quick validation passes create-skill and all five replacement/backlog skills. No new model benchmark is claimed for these routing/tool-portability edits.

Static audit confirms all legacy roots and four retired skill directories are absent. Brain wikilinks resolve, todo IDs are unique with next-id above the maximum, and the actual standalone indexer regenerated the real root inventory without diagnostics. Copied-script tests pass 23 cases after cutover; generator tests pass 25, suite-registry tests pass 14. A real POSIX/PowerShell launch exercise passed with apostrophes, ampersands and spaces in installed hook paths on macOS. This is shell-contract proof, not native Windows or provider delivery.

A bounded isolated Copilot CLI probe used a fresh COPILOT_HOME, temporary project and normal one-session folder trust. After correcting CLI argument restrictions, the valid invocation exited 1 with `No authentication information found` before startup. No nonce delivery or index creation occurred. No actual-home auth/config was changed. Native Windows/Linux, Python 3.12, Codex isolated trust and Gemini availability remain limits. Todo 1 stays open until final acceptance.

Additional environment evidence: local Python installations are 3.13.14 and 3.14.6; no 3.12 runtime is installed. The 23 brain cases also pass under Python 3.13.14. Docker Desktop has no running daemon/socket, so it provides no Linux evidence. These facts do not waive native/minimum-version checks.

Aggregate verification is currently running on the final registration tree. Prior stopped-run logs are `/tmp/brain-test-all-first-run.log` and `/tmp/brain-test-all-second-run.log`; the active log is `/tmp/brain-test-all.log`. The second run passed source startup/guard suites, Codex agents and merge, provider probe fixtures and the 25 generator cases before being stopped during suite 20. It is not a complete aggregate pass.

T7 repair checkpoint: the third aggregate run passed suites 1-25, then exposed a real diagnostic collector mismatch in both Bash and PowerShell installed recovery scenarios. Diagnostics counted the two pinned brain handlers as missing/unowned because only security filenames were transformed into installed launch identities. The canonical collector now embeds the same pinned-file set and exact provider-argument helper used by installers. It still requires exact full-handler identity; the existing recovery case that appends an unknown argument must remain rejected. Regenerated collectors are under focused recovery verification. The third run was stopped cleanly for this repair; `/tmp/brain-test-all-third-run.log` retains its evidence. No full aggregate pass is claimed yet.

T7 complete-run checkpoint: the fourth aggregate run completed in 1897.3 seconds with 54 passing suites and one failure in `scripts/test_helpers.py`. All failures there referenced the removed GitHub-only helper copies. Four exclusive GitHub helper tests and that provider's entries in shared loops were retired; three unique path-normalization assertions were retained in the live Gemini helper case. No surviving-provider assertion was weakened. The resulting 12-case helper suite passes. Product runtime code is unchanged by this cleanup. A final full run is in progress; `/tmp/brain-test-all-fourth-run.log` preserves the completed 54/55 result.

## Final local validation and reflection (2026-10-20)

`rtk python3 scripts/test-all.py` completed with exit 0 on macOS 26.7.1 arm64/Python 3.14.6: `Suites: 55 passed, 0 failed in 1890.8s.` Full output is `/tmp/brain-test-all.log`. Native Windows entrypoints explicitly skipped on macOS; they are not native proof. `rtk python3 scripts/generate-hooks.py --check` reports `Generated hooks are current (62 files).` The three new path-normalization assertion lines and changed provider loop in the mixed-line-ending helper suite were normalized to LF after the run; this whitespace-only cleanup does not change test behavior. Focused helper verification passed all 12 cases after that cleanup. `rtk git diff --check` passed. The final navigation audit found 40 reachable brain files with valid wikilinks, all legacy roots absent and HEAD unchanged.

Reflection completed: exact installed launch identity must include provider arguments in both installation reconciliation and diagnostic receipts. Both now share the canonical argument helper, and existing public recovery tests prove unknown suffixes remain unowned. Current evidence admission, deterministic inventory ownership, provider limits, explicit-only maintenance and no-write reflection are retained in existing brain notes/skills rather than duplicated as session narrative. No extra backlog item was created for validation already tracked by todo 1.

At the local validation checkpoint, no commits, staging, private implementation worktrees, real-home installs or publication had occurred. The starting HEAD was `092038394a2e3bb0cc21fffdec2eb60a12cece29` on `codex/brain-system-migration`. T7 acceptance stays unmet solely for required native/minimum-version and live-provider evidence; no unavailable result is claimed.

## Active-hook source repair (2026-10-20)

After the local cutover, an actual Stop invocation failed because its `hook_run_id` named `/Users/adam/dev/skills/.codex/hooks.json`, while its Git-root-resolved command targeted the removed adapter in this worktree. The worktree configuration was already migrated; the unchanged main-checkout source still contained the retired OKF Stop handler. The coordinator removed exactly that baseline handler from the main checkout's repository-local file using an atomic write and preserved other settings. This is one additional uncommitted edit outside the implementation worktree, required to repair the active invocation. No user-global hook installation was changed. JSON and scoped diff verification confirm the stale registration is gone; a later actual Stop invocation is the live confirmation. No deletion regression test or compatibility shim was added.
