# Replace the legacy agent knowledge system with brain

This living ExecPlan is `brain/plans/01-brain-migration/ExecPlan.md`, associated with todo 1. Follow the `exec-plans`, `brain`, and `todo` skills. Keep the required living sections and milestone evidence current. The execution-plan contract requires a self-contained document, so this file intentionally exceeds the brain skill's usual note-length guideline.

## Purpose / Big Picture

Agents should find current repository guidance and durable knowledge through `brain/index.md`, maintain useful notes through brain skills, and discover new notes automatically. The repository should no longer depend on `.agents/instructions/`, `.agents/memory/`, `.agents/sources/`, source ingestion, or OKF enforcement. Existing useful knowledge must survive as concise, attributable notes; obsolete material must not survive merely because it existed.

Two portable hook behaviors will maintain the root index and inject that index into supported provider sessions. Copying a generated script and its provider registration into another repository must work with Python 3 and the standard library, without this repository's helper modules or shell utilities. Windows, Linux, and macOS are required targets.

### Current authorization and stopping boundary

On 2026-10-20 the user accepted decisions Q1-Q9 and confirmed the shared design. The latest request authorizes writing this plan and explicitly requires stopping before implementation. This turn may create the plan and its backlog/index links only. Do not migrate notes, delete legacy files, implement hooks, change skills, install anything, commit, or start implementation tests in this turn. The next implementation action requires a subsequent user instruction to proceed.

Future implementation is repository-scoped. Existing user-global installations must remain unchanged until the user explicitly reinstalls. Use isolated temporary destinations for installer validation. The old instruction to run the normal installer before live testing does not override this boundary.

## Progress

- [x] (2026-10-20) [milestone-0] Record the accepted decisions, current repository evidence, task graph, and validation contract.
- [x] (2026-10-20) [milestone-0] Create the plan and link it from the brain backlog and plans index.
- [ ] [milestone-1] T1: Complete a per-file disposition inventory and verify current provider event/output contracts.
- [ ] [milestone-2] T2: Migrate useful instructions, evidence, and ideas; verify provenance, coverage, and reachability.
- [ ] [milestone-3] T3: Deliver standalone index reconciliation through tested command-line behavior.
- [ ] [milestone-3] T4: Deliver index injection and verified lifecycle registrations for each provider.
- [ ] [milestone-3] T5: Integrate generation and isolated installation; prove ordered startup and copy portability.
- [ ] [milestone-4] T6: Remove obsolete knowledge infrastructure and update every active consumer.
- [ ] [milestone-5] T7: Complete integrated validation, cross-platform evidence, documentation, and reflection.

## Surprises & Discoveries

- Commit `54b6a74f853d174fe8de71e2e6eb42db69cf9e9f` introduced the new brain and skills. The existing brain has principles, an empty plans index, and initially no todos.
- `docs/ideas/index.md` lists nine active and five archived idea files. Some active ideas explicitly require validation; archived does not necessarily mean completed, because the old workflow also archived ideas when a plan existed.
- The legacy roots contain routed policies, known issues, raw third-party sources, summaries, and ingestion state. They cannot be copied wholesale without retaining obsolete representation and lifecycle assumptions.
- `hooks/manifest.py` owns generated provider files. Source ingestion has six generated outputs and multiple canonical `auto_ingest*.py` modules. OKF has canonical families and generated helpers for several providers.
- `scripts/test-all.py` explicitly registers ingestion and OKF suites alongside unrelated suites. It supports macOS/Linux, requires Python 3, Bash, Git, jq, flock, SQLite, and PowerShell 7+, and is not a native Windows runner.
- The upstream indexer uses Bash/POSIX utilities and rewrites a fixed-section root index. The upstream injector assumes plain stdout is injected as context. Neither script can be copied unchanged to all target providers and operating systems.
- Existing hook guidance requires standalone provider outputs, JSON-only stdout, UTF-8, bounded input completion without waiting indefinitely for EOF, and generator checks before installation. Retain these relevant constraints in brain notes and the replacement hooks.
- `brain/todos.md` has a historical archive-path comment that differs from the todo skill's `brain/archive/todos.md` rule. Normalize that comment during migration, not by inventing a second archive convention.
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
| Q8 | Reconcile the index before startup injection and after successful tool execution; write only on change. | Catch additions, deletions, renames, and shell-driven changes. Verify provider event mappings before implementation. |
| Q9 | Require an end-of-session `reflect` review after code changes; persist only durable findings. Keep `meditate` and `ruminate` explicitly invoked. | Replace mandatory legacy KB review without requiring low-value writes or automatic semantic maintenance. |

The actual skill directory is `update-agent-docs`, despite the original request spelling it `update-agents-docs`. Remove the actual retired skill and fix references to either spelling where present.

## Outcomes & Retrospective

Planning is complete; implementation has not started. This turn adds only this plan and its two navigation/backlog edits. No migrated content, hook behavior, provider compatibility, or platform acceptance is claimed. The next owner is the implementing agent after the user resumes the work.

## Context and Orientation

Working directory: `/Users/adam/.codex/worktrees/6578/skills`. Paths below are repository-relative. Read `AGENTS.md`, `brain/index.md`, and relevant topic notes before changing anything. Root brain navigation already links `brain/plans/index.md`, so adding this plan there makes it reachable without rebuilding the root index during planning.

The repository publishes skills from `skills/`, custom agents from `agents/`, project Copilot hooks from `.github/hooks/`, installed Copilot sources from `.copilot/hooks/`, Gemini hooks/config from `.gemini/`, and Codex hook sources from `.codex/`. Repo-local brain and retired KB skills are under `.agents/skills/`; do not confuse them with generated user-global custom agents.

Canonical hook renderers live in `hooks/families/`; `hooks/manifest.py:targets()` lists generated files. `hooks/providers.py` and `hooks/registrations.py` supply provider behavior and registrations. `scripts/generate-hooks.py` supports `--write` and `--check`. Generated provider files must not be hand-edited. The shared generator may reuse build-time code, but copied runtime scripts must be self-contained.

Inspect installer ownership through `scripts/install.sh`, `scripts/install.ps1`, `scripts/install-provider-hooks.py`, and `scripts/install-codex-hooks.py`. Preserve unrelated settings and runtime logs. Inspect `scripts/test-generate-hooks.py`, `scripts/test-install-codex-hooks.py`, `scripts/test-install.sh`, `scripts/test-install.ps1`, and `scripts/probe-provider-hook-delivery.py` before extending their relevant contracts.

### Migration map

T1 must expand this category map into a file-by-file disposition ledger before deletion. Store the ledger at `brain/plans/01-brain-migration/migration-map.md` and link it from the plans index. Each row records original path, keep/merge/drop decision, destination or deletion reason, provenance, and verification status. Include all file types, not just Markdown. This ledger replaces no ingestion runtime and is only migration evidence.

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

Earlier read-only discovery supplied the following references. T1 must verify current schemas and lifecycle guarantees against official pages and the supported CLI versions; this plan does not treat a copied summary as proof of deployed behavior.

- Upstream behavior examples: [auto-index-brain.sh](https://github.com/poteto/noodle/blob/main/.agents/hooks/auto-index-brain.sh), [inject-brain.sh](https://github.com/poteto/noodle/blob/main/.agents/hooks/inject-brain.sh).
- Copilot: [hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference).
- Codex: [hooks documentation](https://learn.chatgpt.com/docs/hooks).
- Gemini: [hooks overview](https://geminicli.com/docs/hooks/), [best practices](https://geminicli.com/docs/hooks/best-practices/). Additional exact references are in the existing Gemini source snapshots and must be retained before their removal.

Discovery reported Copilot startup `additionalContext`, Codex `SessionStart` context injection including compact/reset sources, and Gemini JSON `hookSpecificOutput.additionalContext`. Post-tool success signaling, reset coverage, and startup ordering remain explicit verification tasks. Do not infer provider equivalence from similar event names.

## Plan of Work

### Milestone 0: Establish the implementation contract
Status: done
Acceptance: met

The accepted design, ownership boundary, proposed interfaces, dependencies, and verification criteria are captured here. Todo 1 and the plans index link to the plan. Acceptance is document creation and navigation validation, not implementation approval or executable verification.

### Milestone 1: Account for content and verify lifecycle feasibility
Status: open
Acceptance: not met

#### T1: Inventory and contract verification

Prerequisites: a subsequent user instruction to implement. Recheck the worktree and read the plan against current files. Inventory tracked legacy files, retired skills and their support files, idea documents, and every active path/skill reference. Exclude untracked skill benchmark workspaces from bulk searches; do not delete unrelated workspace data.

Produce the disposition ledger described above. Read each source before assigning a decision. Resolve copied policy conflicts against current code and the accepted design. Review existing ADRs, especially ingestion decisions, and mark superseded guidance as historical rather than rewriting historical claims to appear current.

Verify official provider contracts, record exact event names, success detection, root fields/environment variables, output envelopes, launch commands, timeout units, and supported reset events in a provider table in this plan. Establish how index refresh is guaranteed to precede injection. Do not rely on configuration array order unless documented and demonstrated. If necessary, the injector can perform the same embedded reconciliation before reading, while remaining independently copyable. This is still two public hook behaviors, not a third helper dependency.

Acceptance: every legacy file has a proposed destination or reason for deletion; each supported provider has a feasible, documented lifecycle mapping. Any unsupported capability must be surfaced as a limitation before claiming parity or silently substituting per-prompt injection. Stop dependent implementation if a required lifecycle behavior cannot be delivered.

### Milestone 2: Preserve useful knowledge and backlog
Status: open
Acceptance: not met

#### T2: Migrate content additively

Prerequisite: T1. Use `brain` for durable notes and `todo` for backlog changes. Merge duplicate material, split notes by topic, retain source URLs next to derived claims, and omit obsolete frontmatter/OKF typing. Prefer existing principles when they already cover the lesson. Keep most notes around 50 lines; use link-only category indexes as necessary.

Read all active and archived ideas. Allocate todo IDs from the next-id marker without renumbering; distinguish investigation from implementation. Preserve still-useful context through linked notes, and record skipped ideas with a reason in the ledger. Normalize the stale archive-path comment to the todo skill's convention.

Update human navigation enough to make every new file reachable before automatic indexing exists. Verify every retained legacy assertion has a destination, every source-derived note has usable attribution, every todo link resolves, and no old policy silently overrides the accepted design. Keep legacy originals until T6's deletion gate.

Acceptance: the completed ledger accounts for the full source inventory; a reader can find retained knowledge and useful follow-up work through the brain without consulting the legacy roots.

### Milestone 3: Deliver portable index and context hooks
Status: open
Acceptance: not met

#### T3: Implement index reconciliation

Prerequisite: T1. Add canonical generation in `hooks/families/brain.py` (proposed new file) and targets in `hooks/manifest.py:targets()`. Public generated entrypoint: `auto-index-brain.py`. Use the existing generator structure, with provider-local files containing all needed runtime logic.

Use Python standard-library filesystem and JSON operations. Resolve repository identity from validated provider context, never from the installed script location. Respect worktrees and nested working directories. An absent brain is a quiet no-op; an existing brain with a missing root index can be indexed. Never create a brain in an unrelated repository.

Generate sorted vault-relative wikilinks for Markdown files, excluding only the root index itself. Include nested indexes and plans/archive notes, grouped deterministically by directory so all files remain discoverable. Keep human-edited subindexes untouched. Define handling for filenames containing wikilink metacharacters without emitting broken links. Do not follow symlink directories or traverse outside the vault. Read no note bodies merely to build the inventory.

Compare rendered bytes before writing. Replace atomically through a same-directory temporary file, clean up temporary files, and prevent concurrent invocations from corrupting or overwriting a newer inventory with stale results. Bound input and filesystem work; errors must preserve the previous index and report a concise stderr diagnostic without blocking ordinary agent work or leaking note contents.

#### T4: Implement injection and provider adapters

Prerequisites: T1 and T3's reconciliation contract. Public generated entrypoint: `inject-brain.py`. Emit only the root index as context, in the verified provider-specific JSON envelope. Logs go to stderr. Support explicit provider selection as accepted in Q5, using values `copilot`, `codex`, and `gemini`; the GitHub project variant uses Copilot's verified contract.

Register startup/reset injection and successful post-tool reconciliation in `hooks/registrations.py` and the provider metadata/config owners identified by T1. Reconcile before reading the startup index. Do not inject on every prompt or every tool call. Recognize successful execution through provider evidence, including shell tools, rather than a narrow list of editor tool names.

Use provider context limits where available and bound outputs without emitting malformed JSON or broken UTF-8. Preserve index content under normal limits; if a limit prevents full injection, provide a clear route to `brain/index.md` and record the limitation. Missing or unreadable input must not accidentally inject another repository's index. Keep lifecycle diagnostics consistent with retained local conventions and keep routine tool-pass output quiet.

#### T5: Integrate generation and isolated installation

Prerequisites: T3 and T4. Emit both scripts under `.github/hooks/scripts/`, `.copilot/hooks/scripts/`, `.gemini/hooks/scripts/`, and `.codex/hooks/`, with corresponding registrations in `.github/hooks/hooks.json`, `.copilot/hooks/hooks.json`, `.gemini/settings.json`, and `.codex/hooks.json` through their actual ownership mechanism.

Each script must run after being copied alone with its registration; no sibling import, third-party package, Bash, Git, jq, or RTK may be required at runtime. Build-time reuse is encouraged. Follow existing executable-mode and launcher conventions, including Windows Python invocation and paths containing spaces.

Extend isolated installer fixtures to prove fresh installs and upgrades converge, retired owned files are removed on explicit reinstall, unrelated user configuration/logs survive, and repeated installs are idempotent. Do not run the normal installer against the actual home directory. Do not repurpose `$HOME` or `$CODEX_HOME` as shell scratch variables; use existing test isolation mechanisms or explicit temporary destinations.

Acceptance for milestone 3: generated artifacts are current; a fresh temporary vault is indexed before its startup context is returned; successful add/rename/delete actions reconcile the index; unchanged runs do not rewrite it; copied scripts work independently. Record per-provider and per-platform results, distinguishing payload-contract tests from real CLI delivery.

### Milestone 4: Retire the old system and update consumers
Status: open
Acceptance: not met

#### T6: Perform the cutover

Prerequisites: T2 and T5 accepted. Remove `.agents/skills/clean-agent-docs/`, `.agents/skills/okf-authoring/`, `.agents/skills/update-agent-docs/`, and `.agents/skills/ingest-source/`, including exclusively owned support files. Find other maintained published copies and references before removing them. Do not remove the entire `.agents/` tree; replacement skills still live there.

Remove canonical `hooks/families/auto_ingest*.py`, exclusively owned OKF family/runtime files, corresponding generated manifest targets and registrations, and obsolete linter/gate entrypoints including `scripts/lint-okf.py`. Shared utilities remain if other hook families use them. Remove exclusively obsolete test suites and fixture registrations from `scripts/test-all.py`; preserve mixed-suite coverage of surviving behavior. Do not write regression tests for feature deletion or weaken unrelated failing tests.

Update `AGENTS.md`, `README.md`, affected skills such as `skills/default/create-skill/SKILL.md`, installer manifests, script consumers, test fixtures, and documentation links. Relevant brain guidance replaces old routing and raw-source authority rules. Official upstream documentation becomes the precise provider-contract reference after snapshots are removed.

Encode mandatory end-of-session reflection after code changes in the maintained instruction/skill locations that own that workflow. Review does not require a write when there is no durable finding. Do not automatically invoke `meditate` or `ruminate`; keep hooks strictly mechanical. Adapt incompatible tool assumptions in replacement skills only as necessary for this workflow, following the skill-authoring guidance when editing them.

Before deleting originals, verify completed ledger coverage, destination links, provenance, new hook acceptance, and absence of active dependencies. Then remove `.agents/instructions/`, `.agents/memory/`, `.agents/sources/`, and superseded `docs/ideas/` content. Git history supplies historical recovery; do not introduce another raw-source archive.

Acceptance: all three legacy roots are absent; active runtime/config/skill references no longer require them or retired skills; useful knowledge and todos remain reachable; historical mentions are clearly historical. Audit remaining references individually rather than blindly rewriting history or unrelated fixtures.

### Milestone 5: Prove the integrated result
Status: open
Acceptance: not met

#### T7: Validate and document the cutover

Prerequisite: T6. Run the validation below on the integrated tree. Repair relevant failures without skipping or weakening surviving tests. Confirm standalone script portability on native Windows, Linux, and macOS; a mocked Windows path on macOS is not Windows runtime evidence.

Document Python prerequisites, copy/paste installation examples for every provider, index ownership, lifecycle behavior, reset limitations, explicit reinstall behavior, and recovery. Use an isolated provider profile or temporary project for live delivery checks. If isolation cannot be established, report live verification as pending instead of changing the user's active installation.

Perform the required reflection review and record only durable findings in the brain. Update this plan's acceptance/evidence and the disposition ledger. Mark todo 1 complete only after the user outcome is delivered and required checks pass; use the todo skill's archive convention. Do not commit or deploy unless subsequently requested.

Acceptance: integrated checks pass with actual output recorded, no required platform/provider result is falsely claimed, migration coverage is complete, and normal repository workflows operate without the legacy knowledge system. Missing native environments or CLI access leave the corresponding acceptance open.

## Task Graph and Ownership

T1 precedes T2 and T3. T4 depends on T1 and T3's contract. T5 depends on T3 and T4. T6 depends on T2 and T5. T7 depends on T6. One implementing owner integrates shared manifests, configuration, indexes, installer changes, and documentation. This plan does not authorize additional agent dispatch by itself.

## Concrete Steps

Next action: wait for the user's instruction to implement. Then the implementing agent reconciles this plan with the worktree and performs T1. Do not rerun the grilling session for settled choices.

Use RTK-prefixed repository commands. Start with `rtk git status --short`, `rtk git rev-parse HEAD`, and scoped tracked-file inventories. Record the starting commit and unrelated work before modifications. For searches use `rtk proxy rg`, excluding benchmark workspaces and generated logs. The migration ledger must include files discoverable by Git even when default search ignore rules hide them.

After implementation changes to canonical hook sources, run `rtk python3 scripts/generate-hooks.py --write`, followed by `rtk python3 scripts/generate-hooks.py --check`. Expect zero exit and no stale generated output. The write command belongs to implementation, not this planning turn.

## Validation and Acceptance

### Test boundaries and workflow

Proposed public test seams are generated hook process stdin/stdout plus observable vault files; provider registration/generation output; and installer behavior in isolated destinations. These catch protocol, lifecycle, portability, and rollout failures. They do not establish actual CLI context delivery without live probes. Avoid testing private rendering functions as substitutes for these outcomes.

The TDD skill requires confirmation of test seams before writing tests. The user accepted the overall design but has not separately confirmed these proposed seams. At the start of implementation, settle this narrow prerequisite before writing tests, while continuing independent content inventory if needed. For new executable behavior, use one failing public-behavior test followed by the minimal implementation, repeating in vertical slices. Do not add tests that only assert removed features remain absent.

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

Record command, OS, Python/provider version, exit status, and the smallest decisive result for each check. Keep platform limitations explicit. The full repository suite passing does not prove native Windows operation or actual provider injection. No implementation test has been run during this planning turn.

## Idempotence and Recovery

Preserve unrelated work. Make content migration additive until coverage is verified; do not delete original knowledge before retained content is reachable. Repeated index runs and isolated reinstalls must converge without unnecessary writes or duplicate registrations. Allocate todo IDs once and record mappings so retries do not create duplicate todos.

Use atomic index replacement and bounded coordination to preserve the last valid index after interruptions. A hook failure must not trigger semantic edits or a blocking ingestion-style repair loop. A later successful invocation should repair index drift.

If cutover fails, restore only the affected tracked files from the recorded starting commit or the user's reviewed migration commit, after checking for newer edits. Do not use broad reset/clean commands or revert unrelated changes. Restore coherent configuration and generated targets together. Because actual global installations are untouched, repository recovery does not require modifying the user's installed hooks.

## Interfaces and Dependencies

Public script names: `auto-index-brain.py` and `inject-brain.py`. Explicit provider option: `--provider copilot|codex|gemini`. Inputs are the verified provider hook JSON and documented environment context; outputs are valid provider JSON on stdout and bounded diagnostic text on stderr. The filesystem boundary is the selected repository's `brain/` directory. Python's standard library is the only runtime library dependency.

Generation may share reconciliation and parsing source internally, but each emitted file must embed what it needs. No runtime import from `hooks/`, sibling helper files, or another provider tree is permitted. Pin the minimum supported Python 3 version after inspecting existing compatibility requirements in T1, and verify the selected floor rather than assuming every Python 3 version works.

The final provider table, precise launcher commands, event identifiers, timeout values, and root-resolution precedence belong in this plan after T1 verification. Their verification is a bounded prerequisite, not permission to revise accepted lifecycle behavior silently.
