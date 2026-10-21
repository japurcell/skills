# Create a portable brain-install skill

This living plan is `brain/plans/brain-install/ExecPlan.md`. Follow the repository's `exec-plans` skill and keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current. It is an approved design awaiting implementation authorization, not permission to start implementing during the planning turn.

## Purpose / Big Picture

Publish `skills/default/brain-install` so an agent can install this brain system into another repository, including repositories with no guidance system and repositories with existing guidance. The installed system must work without this author's checkout, global skill installation, network access, or repository-specific documentation. Installation uses deterministic templates and Python standard-library scripts for mechanical work; an agent performs the semantic migration of existing guidance.

A successful installation creates a navigable starter vault, installs six local skills, adds the two agreed sections to root `AGENTS.md`, and optionally installs repository hooks for independently selected providers. Existing guidance is preserved obligation by obligation, with durable knowledge in brain and reusable procedures preferably in matching skills. Existing unrelated content remains intact.

Current authorization is to correct the two review findings in this plan and stop. Do not implement, migrate a real target, commit, push, or install global hooks in this turn. Later execution must preserve the user's manual changes and recheck the working tree before editing.

## Progress

- [x] (2026-10-21) [milestone-0] Confirm the design through grilling, inspect source assets, and write this execution contract.
- [x] (2026-10-21) [milestone-0] Resolve review findings with an existing-index preservation gate and per-file keep-existing choices.
- [ ] [milestone-1] T1: Build the self-contained asset snapshot and portable six-skill bundle; verify source parity and intended adaptations.
- [ ] [milestone-2] T2: Implement and verify base installation, AGENTS.md reconciliation, conflict handling, and manual indexing.
- [ ] [milestone-3] T3: Implement and verify optional provider hook merging and preservation across reruns.
- [ ] [milestone-4] T4: Author the brain-install workflow and obligation-level migration reference; evaluate fresh, legacy, and conflicting targets.
- [ ] [milestone-5] T5: Run integrated checks, skill evaluations, and native platform checks; record actual evidence and remaining limits.

## Surprises & Discoveries

- The existing hook scripts are standalone Python 3.12+ programs. Provider copies contain the same runtime; copying these is preferable to importing this repository's generator or installing its other hook families. Evidence: `brain/codebase/brain-hooks.md` and the read-only asset inventory.
- Optional hooks require an explicit manual indexing route. The current brain skill points to this repository's `brain/codebase/brain-hooks.md`; that dependency must become a command using the installed skill's own script.
- `meditate` currently requires `snapshot.sh`, and `ruminate` uses POSIX shell syntax and `/tmp`. Portability therefore involves skill helpers as well as installer and hook scripts.
- `ruminate` currently documents `--copilot-dir`, but `extract-conversations.py` only declares Claude and Codex input options. Do not ship an invalid command or claim unsupported extraction. Correct the bundled instructions to the actual supported inputs; adding another conversation parser is outside this plan.
- Root indexing stops beneath curated indexes, except that all Markdown files under `brain/codebase/` remain listed. Preserve this behavior, including the archive boundary.
- Review found that the unchanged indexer replaces an existing root index without migrating its prose or navigation; installation must gate that replacement before enabling hooks. Review also found that accepting a differing file needs an explicit keep-existing route through preflight.
- The working tree was clean at planning inspection. This is historical evidence, not permission to discard later edits.

## Decision Log

- D1 (user, 2026-10-21): Bundle a self-contained snapshot of the six skills, hooks, templates, `brain/principles.md`, and its 14 linked principle notes. Avoid downloads and dependencies on this checkout. Copy principles unchanged.
- D2 (user, 2026-10-21): Preserve existing content and unrelated configuration. Identical files are no-ops; conflicts require a concrete choice before replacement. Never reset todos or existing principles.
- D3 (user, 2026-10-21): Audit migration obligation by obligation. Prefer matching skills for reusable procedures. Preserve scoped instructions and provider entrypoints; retire obsolete guidance only after checking preservation.
- D4 (user, 2026-10-21): Support Windows, Linux, and macOS across installer and bundled helpers. Prefer Python standard-library scripts and minimal adaptations; provide fallbacks for unavailable optional skills or tools.
- D5 (user, 2026-10-21): Hook installation is optional. Copilot, Codex, and Gemini are independently selectable, including any combination or none. Never change user-global configurations.
- D6 (user, 2026-10-21): Always install the existing standalone indexer inside the brain skill. Generate the initial index and document manual invocation when hooks are absent. Preserve the agreed AGENTS.md sections verbatim despite their hook-oriented wording.
- D7 (user, 2026-10-21): Unselected providers remain untouched, including previously installed brain hooks. Selection installs or updates; it never means uninstall.
- Implementation choice: use one Python installer with an inspect/default mode and an explicit apply mode. Do not add an ownership database, daemon, generic migration engine, automatic update service, broad overwrite flag, or dependency framework. Resolve content conflicts through reviewed edits or explicit per-file `--keep-existing` choices, then rerun the installer.
- Review correction (2026-10-21): existing root indexes require `--index-reviewed` before application. The agent must preserve original bytes and migrate meaningful content before giving this acknowledgement; an already generated index needs only review. These invocation-local choices require no ownership database.

## Outcomes & Retrospective

Planning and both review corrections are complete. Existing-index preservation and keep-existing reruns now have explicit CLI, workflow, and acceptance contracts. No skill, installer, bundled asset, test, or workflow implementation has started. All implementation and runtime acceptance remain open. The next owner action is to authorize execution of this plan. Once authorized, start T1 after checking current source and worktree state; later tasks follow the explicit dependencies below.

## Context and Orientation

This repository publishes portable skills from `skills/`. The source brain skills currently live under `.agents/skills/brain`, `.agents/skills/meditate`, `.agents/skills/reflect`, `.agents/skills/ruminate`, `.agents/skills/todo`, and `.agents/skills/todo-refine`. Copy their required runtime resources, not just SKILL.md files. Preserve `disable-model-invocation: true` on meditate and ruminate. Do not invoke those skills automatically during installation.

`brain/principles.md` is a curated link index, not the principle content itself. Its 14 notes under `brain/principles/` must accompany it. Do not copy this repository's backlog, project notes, audits, archived plans, task identifiers, historical live-provider results, or migration reports into a target's starter vault.

Hook sources to snapshot are `.github/hooks/scripts/auto-index-brain.py` and `.github/hooks/scripts/inject-brain.py`; equivalent copies exist in `.codex/hooks/` and `.gemini/hooks/scripts/`. Repository registration sources are `.github/hooks/hooks.json`, `.codex/hooks.json`, and `.gemini/settings.json`. Extract only the brain registrations. `.copilot/hooks` is user-level instrumentation and is not a brain installation destination.

The existing indexer accepts `--provider codex` with JSON stdin containing an absolute `cwd` and `hook_event_name: PostToolUse`. This is also the manual invocation route without Codex installed. It uses the payload's location, not its own script directory, to select the vault. Hook scripts intentionally fail nonblockingly, so a zero process exit alone does not prove that installation generated an index.

`scripts/install-provider-hooks.py` and `scripts/install-codex-hooks.py` provide examples of preserving unrelated configuration, but are not drop-in dependencies for this bundle. `scripts/test-brain-hooks.py` proves existing hook contracts. `.github/workflows/brain-hooks.yml` already runs a Windows/Linux/macOS matrix on Python 3.12 and 3.14. Reuse that bounded workflow for new installer tests rather than expanding the slow general hook workflow.

Skill authoring must activate `create-skill`, `skill-creator`, and `writing-for-agents`. Script implementation must activate `tdd`, confirming applicable test boundaries before writing tests when required by that skill. Historical test-boundary approvals for the migration do not automatically cover this new installer. Skill maintenance and evaluation instructions belong in README.md, not runtime SKILL.md or runtime references.

## Interfaces and Dependencies

Create this bundle layout, using only files needed for the agreed behavior:

```text
skills/default/brain-install/
  SKILL.md
  README.md
  references/migration.md
  scripts/install.py
  assets/AGENTS-brain.md
  assets/brain/principles.md
  assets/brain/principles/*.md
  assets/brain/todos.md
  assets/brain/codebase/index.md
  assets/brain/plans/index.md
  assets/brain/audits/index.md
  assets/brain/archive/index.md
  assets/skills/{brain,meditate,reflect,ruminate,todo,todo-refine}/...
  assets/hooks/inject-brain.py
  assets/hooks/{copilot,codex,gemini}.json
  tests/test_install.py
  evals/evals.json
```

The always-installed indexer lives in `assets/skills/brain/scripts/auto-index-brain.py` and installs to `.agents/skills/brain/scripts/auto-index-brain.py`. Reuse that asset when copying provider indexers; no second source implementation. The injector installs only for selected providers. Replace the bundled meditate snapshot helper with `scripts/snapshot.py`, preserving its snapshot format, and update bundled ruminate to use the portable command. Keep adaptations within the new bundle unless a separate source change is necessary and explicitly justified.

`install.py TARGET [--provider copilot|codex|gemini ...] [--keep-existing RELATIVE_PATH ...] [--index-reviewed] [--apply]` uses an explicit target path. Omitted providers mean no hook installation. Default mode inspects and reports proposed changes without writes. `--apply` performs only conflict-free installation. Exit 0 means successful inspection or application, exit 1 means an I/O/application failure, and exit 2 means invalid input, prerequisites, malformed configuration, or a conflict. Print affected paths and actionable diagnostics. Do not prompt inside the script; the skill handles user choices.

Repeat `--keep-existing RELATIVE_PATH` for each reviewed existing seed note, curated index, or skill file to retain unchanged. Preflight and apply honor the same choice; it suppresses only that file's template-content conflict. Reject missing, unknown, absolute, or escaping paths. It does not bypass path safety or validation and cannot skip AGENTS sections, provider configuration, or the generated `brain/index.md`. Retained skill files still require compatibility verification before claiming a working installation. Choices are invocation-local, not persisted.

When `brain/index.md` already exists, inspection reports the preservation checkpoint and apply refuses before any writes unless `--index-reviewed` is supplied. This flag acknowledges the agent's completed review, not an automated semantic check. For a legacy/custom index, preserve its exact bytes and migrate meaningful guidance/navigation first. For an already generated inventory, confirm it has no unique content to migrate. Never activate new index-writing hooks before this checkpoint.

Require Python 3.12+ and standard library only. Runtime commands must not require RTK, Git, Bash, PowerShell-specific helper scripts, Node, network downloads, or the author's installed skills. Provider-specific launchers may use their provider's native shell fields as existing registrations require. Detect a suitable interpreter and quote paths using the existing tested launcher patterns; do not embed the author's absolute paths.

An empty `todos.md` retains the numeric-ID convention with `<!-- next-id: 1 -->`. Starter directory indexes contain only a heading until content exists. The initial `brain/index.md` is generated by the existing indexer, not copied from this repository. Do not create a fake todo solely to number this implementation plan.

## Plan of Work

### Milestone 0: Agreed execution contract

Status: done
Acceptance: met

The user confirmed D1-D7 and requested this plan only. Source inspection established the reusable assets and portability gaps. This document records all pending work and the stopping boundary.

### Milestone 1: Self-contained portable assets

Status: open
Acceptance: not met

#### T1: Prepare the payload

Prerequisites: new authorization to implement. Inputs: D1, D4, D6, the six source skill trees, principle files, AGENTS.md, and the two standalone hooks. Own the new bundle's `assets/` tree and asset/helper checks in `tests/test_install.py`.

Copy principle bytes exactly and extract the complete `## Brain` and `## End of Work Session Defined` sections into `assets/AGENTS-brain.md`. Do not include the source repository's opening publishing paragraph. Populate minimal skeletons and snapshot the six skills. Replace author-repository runtime document pointers with bundled instructions; intentional paths to files this installer creates in the target brain are allowed. Use activation language for other skills and explicit local fallbacks when optional skills, subagents, or planning tools are unavailable.

Port snapshot generation to Python, use portable temporary directories, and update both callers. Correct ruminate's unsupported option without promising new provider extraction. Preserve runtime behavior, explicit-only controls, supported extraction formats, and cleanup limited to temporary files created by that invocation. Do not import historical migration policy that the user deliberately removed from current sources.

Verification: copy the payload to a temporary location outside the checkout. Check principle byte equality, runtime resource closure, portable helper operation on representative Markdown paths, and the documented extraction command against its parser. Compare copied hook bytes to source and validate all six skill frontmatters. Stop at verified assets; installer and migration behavior belong to later tasks.

### Milestone 2: Safe base installation and manual indexing

Status: open
Acceptance: not met

#### T2: Implement the base installer

Prerequisites: T1. Inputs: D2, D6, the CLI contract, and the finished assets. Own `scripts/install.py` and base installer cases in `tests/test_install.py`.

Preflight all intended destinations before mutation: reject malformed selected configuration, duplicate JSON keys, ambiguous duplicate target AGENTS sections, unsupported Python, and unsafe linked destinations/ancestors. Do not follow symlinks or Windows junctions into other locations. Use atomic replacement for owned regular files so hard links cannot mutate an external inode. Validate only selected provider destinations; unselected broken configuration must not block a no-hooks install.

Create missing files and leave identical files untouched. Existing notes, todos, principles, or differing skill files are conflicts, not overwrite candidates. Existing matching AGENTS sections are no-ops; absent sections are appended; differing sections are reported with their proposed replacement. Match real Markdown sections, respecting fenced examples and the next peer heading. Preserve all unrelated AGENTS text. Once the agent has resolved a conflict with the user's concrete choice, rerun preflight with any eligible `--keep-existing` paths instead of introducing force-overwrite machinery. A kept todo or principle file remains byte-for-byte intact while other installation work proceeds. Required AGENTS sections and selected hook registrations still need reconciliation; keeping an unrelated seed file cannot waive those requirements.

Before any apply-time mutation, enforce the existing-index checkpoint from Interfaces and Dependencies, including when hooks are selected. Only after that checkpoint, invoke the standalone indexer with the explicit target cwd and Codex PostToolUse payload after creating the vault. Verify that the resulting index exists and reaches the expected files; report indexing diagnostics as application failures rather than claiming installation success from exit status alone. Add the persistent brain lock path to the target's ignore rules without duplicating or replacing unrelated rules. Document the same portable JSON-stdin invocation in the installed brain skill.

Verification: fresh target, existing target, repeated application, read-only inspection, spaces/non-ASCII paths, conflicting principle/todo/skill/AGENTS files, unsafe links, and missing interpreter prerequisite. Compare unrelated-file fingerprints before and after, and unchanged managed-file timestamps on rerun. Exercise manual indexing from the copied installed bundle with no hook configurations. Add a legacy index containing unique prose and navigation: unacknowledged apply must leave the entire target unchanged; after preservation and migration, acknowledged apply must retain the original bytes in recovery evidence and keep the migrated content reachable. Also edit todos and a principle after installation, retain them with `--keep-existing`, and add another provider successfully without changing those files. Stop when base installation and its negative cases pass.

### Milestone 3: Independently selectable repository hooks

Status: open
Acceptance: not met

#### T3: Merge selected provider registrations

Prerequisites: T2. Inputs: D5, D7, existing brain registration objects and standalone scripts. Extend only the new installer, hook assets, and installer tests.

For Copilot install `.github/hooks/scripts/{auto-index-brain,inject-brain}.py` and merge `.github/hooks/hooks.json`. For Codex install `.codex/hooks/{auto-index-brain,inject-brain}.py` and merge `.codex/hooks.json`. For Gemini install `.gemini/hooks/scripts/{auto-index-brain,inject-brain}.py` and merge `.gemini/settings.json`. Preserve unrelated settings and handlers. Exact brain registrations are no-ops; recognizable but differing brain registrations are conflicts requiring review, not duplicate append targets. If ownership is ambiguous, preserve and report it.

Keep the existing event semantics: Copilot successful postToolUse, Codex every completed PostToolUse including failures, Gemini AfterTool without an error, and each provider's startup/resume injection behavior. Preserve isolated interpreter flags, launcher root discovery, context caps, timeouts, and provider-specific output shapes. The hook scripts must remain usable alone. Recheck provider registration schemas against official documentation before changing registration mechanics; do not infer current support from old live-probe evidence.

Verification: none, each individual provider, all combinations, reruns, and changing selections after installation. Unselected provider files and all user-global files must remain unchanged. Test unrelated handlers/settings preservation, malformed/duplicate JSON, conflicting brain handlers, and launcher execution from paths containing spaces. Exercise registered commands with representative provider payloads. Stop after the provider-selection matrix and preservation cases pass.

### Milestone 4: Usable installation and migration skill

Status: open
Acceptance: not met

#### T4: Author runtime guidance and migration procedure

Prerequisites: T3. Inputs: verified installer behavior and D1-D7. Own SKILL.md, `references/migration.md`, README.md, and `evals/evals.json`.

The runtime skill identifies the target and requested providers, inventories guidance including any existing root index, and runs installer inspection. Before mechanical installation, it preserves and migrates meaningful content from an existing root index, then supplies `--index-reviewed`; an already generated inventory only needs review. It resolves other concrete conflicts through reviewed edits or eligible `--keep-existing` choices, applies mechanical installation, completes the remaining guidance migration, and verifies the result. This runtime ordering is required even though T4 authors the procedure after the installer tasks. Do not require another approval for conflict-free work already requested by the target user. Read `references/migration.md` only when existing guidance requires migration. Keep skill maintenance, source refresh instructions, eval commands, and benchmark procedures in README.md.

Migration starts with an inventory of root/nested instructions, memory/KB notes, linked references, relevant existing skills, and registrations that load legacy guidance. Decompose obligations, including conditions, scope, exclusions, and approval requirements. Record each source obligation as retained, moved with an exact destination, consolidated with equivalent coverage, or obsolete with a specific reason. Preserve the mapping in a concise target migration audit under `brain/audits/`; do not dump source transcripts or secrets into it.

Move repository knowledge into topic notes, preserve scoped behavioral rules where their scope remains effective, and place reusable procedures in matching skills after reading their existing content. Keep root/nested AGENTS policy and provider compatibility bridges that still serve a purpose. Update references before removing legacy files. Remove retired ingestion/loading registrations only when they belong to the superseded guidance workflow and preservation is verified; leave unrelated hooks intact. Do not recreate OKF/frontmatter requirements, source-ingestion automation, global tool guards, automatic semantic maintenance, or a second knowledge system.

Validate every migration obligation, navigation, preserved scope, and source retirement before declaring migration complete. Uncertain or conflicting guidance remains intact and is reported for a concrete decision. Do not treat bulk copying legacy folders or rewriting every instruction into prose as a migration. Never make a real repository migration part of authoring this skill; use disposable fixtures.

Verification: at least three realistic evaluations covering a fresh install with no hooks, a legacy guidance migration with selected providers and scoped rules, and a conflicting/repeated installation that preserves user changes. Include conditions and approval constraints that must survive migration, stale links to repair, and an unrelated provider handler. Use deterministic checks for file and config outcomes and review semantic obligation preservation directly. Benchmark against `without_skill` as required by authoring guidance. Stop at an authored, evaluated skill; integrated/native acceptance is T5.

### Milestone 5: Integrated and native verification

Status: open
Acceptance: not met

#### T5: Prove the complete bundle

Prerequisites: T4. Inputs: the integrated bundle, focused test evidence, evaluation artifacts, and existing CI workflow. Own integration verification and the minimal extension of `.github/workflows/brain-hooks.yml` needed to run the installer tests and trigger on bundle changes.

Run the installer from a relocated copy into disposable targets, with disposable homes, and exercise the installed manual indexer plus selected launchers. Prove fresh installation, migration preservation, conflict behavior, unchanged reruns, and hook-selection transitions together. All runtime resources must resolve without this checkout. Check source snapshot parity with explicit exceptions for portable skill/helper adaptations. Inspect diffs to ensure unrelated source skills, manual changes, and global installations remain untouched.

Extend the existing six-cell native matrix for Python 3.12/3.14 on Windows/Linux/macOS. Keep its ten-minute job budget; do not move these tests into the slow general workflow or remove existing coverage. Native success is required to claim cross-platform installer verification. If dispatch needs a push not yet authorized, leave native acceptance open and report that exact owner action. Live-provider delivery is separate from process/config testing: report any live checks actually performed, but do not inherit historical delivery claims or add a mandatory Gemini live session to this installer scope.

Completion requires passing integrated tests, skill validation/evaluations, and native checks with evidence. At the end of a code-changing implementation session activate reflect; persist only new durable findings. Do not mark completion from a clean diff alone. Stop without committing or pushing unless the user separately authorizes those actions.

## Concrete Steps

The next action is the user's authorization to implement. No implementation command below is authorized during this planning turn. Once authorized, the executing agent checks `rtk git status --short`, reads this plan and current authoring guidance, confirms required TDD boundaries, and starts T1.

Run commands from the repository root. The following are proposed verification commands; none have been run for an implementation that does not yet exist:

```text
rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests -p 'test_*.py'
rtk proxy python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/brain-install
rtk proxy python3 scripts/generate-hooks.py --check
rtk proxy python3 scripts/test-brain-hooks.py
rtk git diff --check
```

On Windows use the available Python 3.12+ executable (`python` or `py -3.12`) and native invocation conventions. RTK is this author's repository convention, not a dependency of the published bundle. Document exact evaluation runner commands in the new README after inspecting the current skill-creator tooling; do not invent benchmark metrics. Inspect failed-case counts even if a grader exits zero.

For an installation smoke test, create a disposable target and run `python3 <copied-bundle>/scripts/install.py <target>` followed by the same command with `--apply`. Expect a complete brain, six skills, the two AGENTS sections, and no provider hook files. Repeat with `--provider copilot`, then Codex and Gemini combinations. The test suite must generate and inspect JSON through Python rather than relying on shell-specific quoting.

## Validation and Acceptance

Every task records its actual command, platform, result, and any omitted cases before its Progress entry is checked. Expected results above are not current pass evidence. Tests must observe installed behavior through subprocesses and target files, not merely compare installer internals.

Shared invariants are no silent content loss, no mutation outside the target, no user-global installation, no change to unselected providers, no runtime dependency on this repository, exact principle/AGENTS templates for fresh targets, preservation on rerun, standard Markdown navigation, and unchanged standalone hook semantics. Test unsafe-path and malformed-config cases before any destination mutation. A late I/O failure must report partial completion accurately; rerun and recovery must preserve existing content.

Migration acceptance includes a human-readable obligation mapping and semantic review, not just file counts. Skill benchmark evidence must distinguish measured tokens/time from proxy or missing values. Native skips are unverified cases, not passes. Record live-provider delivery separately from successful process-level tests.

## Idempotence and Recovery

Inspection is read-only. Preflight known conflicts before applying any writes. Atomic per-file writes protect existing files but do not promise a transaction across the target tree. If an I/O failure interrupts application, report completed and failed paths, preserve existing data, and retry after resolving the cause. Identical files remain no-ops. Repeat the reviewed per-file keep choices on retries; retained files are not reset to template bytes. Recheck the current root index before repeating `--index-reviewed`. Do not require a persistent installer ledger to recover.

Before replacement or removal of existing guidance, including installer-triggered regeneration of a legacy/custom `brain/index.md`, retain a recoverable copy of each affected file in a user-approved target-local or temporary backup location, or verify that its exact pre-edit content is recoverable from version control. A tracked file with uncommitted changes is not backed up merely because Git exists. Do not automatically commit, stash, reset, or restore the whole tree. Restore only the affected files if migration verification fails, preserving later user changes.

Do not delete existing hooks because their provider was omitted, and do not remove an active index lock file. Failed indexing must leave its diagnostic and installation status visible. Fix the cause and rerun the installed standalone indexer; never replace it with a different ad hoc inventory implementation.
