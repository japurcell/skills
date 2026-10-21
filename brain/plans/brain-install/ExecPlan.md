# Create a portable brain-install skill

This living plan is `brain/plans/brain-install/ExecPlan.md`. Follow the repository's `exec-plans` skill and keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current. Implementation is authorized by the user's execplan-implement invocation on 2026-10-21.

## Purpose / Big Picture

Publish `skills/default/brain-install` so an agent can install this brain system into another repository, including repositories with no guidance system and repositories with existing guidance. The installed system must work without this author's checkout, global skill installation, network access, or repository-specific documentation. Installation uses deterministic templates and Python standard-library scripts for mechanical work; an agent performs the semantic migration of existing guidance.

A successful installation creates a navigable starter vault, installs six local skills, adds the two agreed sections to root `AGENTS.md`, and optionally installs repository hooks for independently selected providers. Existing guidance is preserved obligation by obligation, with durable knowledge in brain and reusable procedures preferably in matching skills. Existing unrelated content remains intact.

Current authorization covers implementation and verification of this plan. Preserve the user's manual changes. The user now authorizes committing and pushing the brain-install changes, inspecting native CI, and fixing resulting failures. Do not migrate a real target or install global hooks. The user confirmed all three test boundaries on 2026-10-21.

## Progress

- [x] (2026-10-21) [milestone-0] Confirm the design through grilling, inspect source assets, and write this execution contract.
- [x] (2026-10-21) [milestone-0] Resolve review findings with an existing-index preservation gate and per-file keep-existing choices.
- [x] (2026-10-21) [milestone-0] Reconcile execution authorization and verify a clean worktree on `codex/brain-system-migration`.
- [x] (2026-10-21) [milestone-1] Confirm the relocated-helper, installer-CLI, and registered-hook test boundaries with the user before writing tests.
- [x] (2026-10-21) [milestone-1] T1: Build the self-contained asset snapshot and portable six-skill bundle; verify source parity and intended adaptations.
- [x] (2026-10-21) [milestone-2] T2: Implement and verify base installation, AGENTS.md reconciliation, conflict handling, and manual indexing.
- [x] (2026-10-21) [milestone-3] T3: Implement and verify optional provider hook merging and preservation across reruns.
- [x] (2026-10-21) [milestone-4] T4: Author the brain-install workflow and obligation-level migration reference; evaluate fresh, legacy, and conflicting targets.
- [x] (2026-10-21) [milestone-5] T5a: Wire the verified installer tests into the existing native workflow.
- [x] (2026-10-21) [milestone-5] T5: Verify the final integrated bundle locally and retain evaluation/parity evidence.
- [ ] [milestone-5] T5: Obtain actual Windows/Linux/macOS Python 3.12/3.14 CI results after separately authorized publication; native acceptance remains unmet.

## Surprises & Discoveries

- The existing hook scripts are standalone Python 3.12+ programs. Provider copies contain the same runtime; copying these is preferable to importing this repository's generator or installing its other hook families. Evidence: `brain/codebase/brain-hooks.md` and the read-only asset inventory.
- Optional hooks require an explicit manual indexing route. The current brain skill points to this repository's `brain/codebase/brain-hooks.md`; that dependency must become a command using the installed skill's own script.
- `meditate` currently requires `snapshot.sh`, and `ruminate` uses POSIX shell syntax and `/tmp`. Portability therefore involves skill helpers as well as installer and hook scripts.
- `ruminate` currently documents `--copilot-dir`, but `extract-conversations.py` only declares Claude and Codex input options. Do not ship an invalid command or claim unsupported extraction. Correct the bundled instructions to the actual supported inputs; adding another conversation parser is outside this plan.
- Root indexing stops beneath curated indexes, except that all Markdown files under `brain/codebase/` remain listed. Preserve this behavior, including the archive boundary.
- Review found that the unchanged indexer replaces an existing root index without migrating its prose or navigation; installation must gate that replacement before enabling hooks. Review also found that accepting a differing file needs an explicit keep-existing route through preflight.
- Initial evaluation grading found a semantic narrowing from a deployment action to deployment plans. The migration reference now requires concrete trigger equivalence and unchanged operative wording when rewriting is unnecessary; the original failed run is retained.
- A CP1252 subprocess reproducer exposed non-UTF-8 installer diagnostics and snapshot output paths. Both entrypoints now emit UTF-8; fifteen installer/helper tests pass.
- The aggregate tool requires `run-1/` directories and cannot sum null timing. Original grading remains intact; canonical presentation copies omit null timing, and generated fallback metrics are removed from the final benchmark rather than treated as measurements.
- The working tree was clean at planning inspection. This is historical evidence, not permission to discard later edits.

## Decision Log

- D1 (user, 2026-10-21): Bundle a self-contained snapshot of the six skills, hooks, templates, `brain/principles.md`, and its 14 linked principle notes. Avoid downloads and dependencies on this checkout. Copy principles unchanged.
- D2 (user, 2026-10-21): Preserve existing content and unrelated configuration. Identical files are no-ops; conflicts require a concrete choice before replacement. Never reset todos or existing principles.
- D3 (user, 2026-10-21): Audit migration obligation by obligation. Prefer matching skills for reusable procedures. Preserve scoped instructions and provider entrypoints; retire obsolete guidance only after checking preservation.
- D4 (user, 2026-10-21): Support Windows, Linux, and macOS across installer and bundled helpers. Prefer Python standard-library scripts and minimal adaptations; provide fallbacks for unavailable optional skills or tools.
- D5 (user, 2026-10-21): Hook installation is optional. Copilot, Codex, and Gemini are independently selectable, including any combination or none. Never change user-global configurations.
- D6 (user, 2026-10-21): Always install the existing standalone indexer inside the brain skill. Generate the initial index and document manual invocation when hooks are absent. Preserve the agreed AGENTS.md sections verbatim despite their hook-oriented wording.
- D8 (user, 2026-10-21): make brain-install explicitly invoked with `disable-model-invocation: true` and an `argument-hint`; add the official Claude Code frontmatter reference to `skills/default/create-skill/SKILL.md`.
- D7 (user, 2026-10-21): Unselected providers remain untouched, including previously installed brain hooks. Selection installs or updates; it never means uninstall.
- Implementation choice: use one Python installer with an inspect/default mode and an explicit apply mode. Do not add an ownership database, daemon, generic migration engine, automatic update service, broad overwrite flag, or dependency framework. Resolve content conflicts through reviewed edits or explicit per-file `--keep-existing` choices, then rerun the installer.
- Review correction (2026-10-21): existing root indexes require `--index-reviewed` before application. The agent must preserve original bytes and migrate meaningful content before giving this acknowledgement; an already generated index needs only review. These invocation-local choices require no ownership database.

## Outcomes & Retrospective

T1-T4 and T5a are complete. The self-contained skill includes deterministic starter assets, six portable local skills, preservation-first installation, optional provider hooks, migration guidance, maintenance documentation, and three realistic evaluated scenarios. Requested invocation metadata and the create-skill guidance reference are present. The validator's one-field allowlist correction accepts the documented argument hint.

T5 local integration passes: fifteen installer/helper tests, twenty-six existing standalone hook tests (one platform-specific skip), eight skill validators, exact principle/AGENTS/hook parity, Python syntax, runtime resource/link checks, negative validator input, YAML matrix checks, and whitespace checks. Selected evaluations pass 14/14 per arm; the original semantic failure and all limitations remain in [evaluation results](evaluation-results.md). No performance improvement or live-provider delivery is claimed.

T5 acceptance remains unmet because the changed implementation has not run on the six native CI cells. Python 3.12, Windows, and Linux are unavailable on this host. The user authorized commit/push and native CI repairs on 2026-10-21. The executing agent is publishing this implementation, then inspecting `.github/workflows/brain-hooks.yml` and fixing any failures. No publication has occurred yet for these changes; no real target migration or global installation occurred. All delegated tasks are complete. Reflection found the durable lessons already encoded in trigger-equivalence guidance, UTF-8 entrypoints, validation metadata support, and maintenance instructions; no additional brain topic note is needed.

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

The always-installed indexer lives in `assets/skills/brain/scripts/auto-index-brain.py` and installs to `.agents/skills/brain/scripts/auto-index-brain.py`. Reuse that asset when copying provider indexers; no second source implementation. The injector installs only for selected providers. Replace the bundled meditate snapshot helper with `scripts/snapshot.py`, preserving its snapshot format, and update bundled ruminate to use the portable command. Keep adaptations within the new bundle unless a separate source change is necessary and explicitly justified. D8 explicitly authorizes the create-skill reference addition. The existing quick validator rejected the documented `argument-hint` field through its public CLI; its allowlist received a one-field correction and the same CLI now passes. This is the only source-tooling change outside the bundle.

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

Status: done
Acceptance: met

#### T1: Prepare the payload

Prerequisites: implementation authorization and confirmation of applicable test boundaries (both received 2026-10-21). Inputs: D1, D4, D6, the six source skill trees, principle files, AGENTS.md, and the two standalone hooks. Own the new bundle's `assets/` tree and asset/helper checks in `tests/test_install.py`.

Copy principle bytes exactly and extract the complete `## Brain` and `## End of Work Session Defined` sections into `assets/AGENTS-brain.md`. Do not include the source repository's opening publishing paragraph. Populate minimal skeletons and snapshot the six skills. Replace author-repository runtime document pointers with bundled instructions; intentional paths to files this installer creates in the target brain are allowed. Use activation language for other skills and explicit local fallbacks when optional skills, subagents, or planning tools are unavailable.

Port snapshot generation to Python, use portable temporary directories, and update both callers. Correct ruminate's unsupported option without promising new provider extraction. Preserve runtime behavior, explicit-only controls, supported extraction formats, and cleanup limited to temporary files created by that invocation. Do not import historical migration policy that the user deliberately removed from current sources.

Verification: copy the payload to a temporary location outside the checkout. Check principle byte equality, runtime resource closure, portable helper operation on representative Markdown paths, and the documented extraction command against its parser. Compare copied hook bytes to source and validate all six skill frontmatters. Stop at verified assets; installer and migration behavior belong to later tasks.

Observed 2026-10-21 on macOS, Python 3.14.6: the relocated snapshot subprocess test failed first because `snapshot.py` was absent, then passed after implementation (`python3 -m unittest discover -s skills/default/brain-install/tests -p 'test_*.py'`, one test). A separate relocated extraction check parsed representative Claude and Codex JSONL into two conversations and two manifests. All six `quick_validate.py` runs passed; explicit-only flags remain. Byte comparisons passed for the 14 principle notes, principle index, complete AGENTS sections, both hooks, and three registration snapshots. Runtime reference review found no remaining author-repository document dependency. Snapshot/caller changes stay inside the new bundle. Native helper checks remain part of T5.

### Milestone 2: Safe base installation and manual indexing

Status: done
Acceptance: met

#### T2: Implement the base installer

Prerequisites: T1. Inputs: D2, D6, the CLI contract, and the finished assets. Own `scripts/install.py` and base installer cases in `tests/test_install.py`.

Preflight all intended destinations before mutation: reject malformed selected configuration, duplicate JSON keys, ambiguous duplicate target AGENTS sections, unsupported Python, and unsafe linked destinations/ancestors. Do not follow symlinks or Windows junctions into other locations. Use atomic replacement for owned regular files so hard links cannot mutate an external inode. Validate only selected provider destinations; unselected broken configuration must not block a no-hooks install.

Create missing files and leave identical files untouched. Existing notes, todos, principles, or differing skill files are conflicts, not overwrite candidates. Existing matching AGENTS sections are no-ops; absent sections are appended; differing sections are reported with their proposed replacement. Match real Markdown sections, respecting fenced examples and the next peer heading. Preserve all unrelated AGENTS text. Once the agent has resolved a conflict with the user's concrete choice, rerun preflight with any eligible `--keep-existing` paths instead of introducing force-overwrite machinery. A kept todo or principle file remains byte-for-byte intact while other installation work proceeds. Required AGENTS sections and selected hook registrations still need reconciliation; keeping an unrelated seed file cannot waive those requirements.

Before any apply-time mutation, enforce the existing-index checkpoint from Interfaces and Dependencies, including when hooks are selected. Only after that checkpoint, invoke the standalone indexer with the explicit target cwd and Codex PostToolUse payload after creating the vault. Verify that the resulting index exists and reaches the expected files; report indexing diagnostics as application failures rather than claiming installation success from exit status alone. Add the persistent brain lock path to the target's ignore rules without duplicating or replacing unrelated rules. Document the same portable JSON-stdin invocation in the installed brain skill.

Verification: fresh target, existing target, repeated application, read-only inspection, spaces/non-ASCII paths, conflicting principle/todo/skill/AGENTS files, unsafe links, and missing interpreter prerequisite. Compare unrelated-file fingerprints before and after, and unchanged managed-file timestamps on rerun. Exercise manual indexing from the copied installed bundle with no hook configurations. Add a legacy index containing unique prose and navigation: unacknowledged apply must leave the entire target unchanged; after preservation and migration, acknowledged apply must retain the original bytes in recovery evidence and keep the migrated content reachable. Also edit todos and a principle after installation, retain them with `--keep-existing`, and add another provider successfully without changing those files. Stop when base installation and its negative cases pass.

Observed 2026-10-21 on macOS, Python 3.14.6: the installer CLI subprocess suite passed ten tests. Fresh inspection is read-only; fresh application and unchanged reruns work outside the checkout with disposable homes. Checks cover fenced AGENTS examples, section conflicts/duplicates, edited todo/principle/skill retention, invalid keep paths, existing-index preservation and recovery bytes, linked destinations/ancestors, hard-link-safe ignore updates, unrelated files, and indexing failures. The linked-parent case reproduced an unintended write before the safety fix and passes afterward. Provider-addition retention is composed with T3. Python version rejection is explicit; alternate interpreter/native checks remain T5.

### Milestone 3: Independently selectable repository hooks

Status: done
Acceptance: met

#### T3: Merge selected provider registrations

Prerequisites: T2. Inputs: D5, D7, existing brain registration objects and standalone scripts. Extend only the new installer, hook assets, and installer tests.

For Copilot install `.github/hooks/scripts/{auto-index-brain,inject-brain}.py` and merge `.github/hooks/hooks.json`. For Codex install `.codex/hooks/{auto-index-brain,inject-brain}.py` and merge `.codex/hooks.json`. For Gemini install `.gemini/hooks/scripts/{auto-index-brain,inject-brain}.py` and merge `.gemini/settings.json`. Preserve unrelated settings and handlers. Exact brain registrations are no-ops; recognizable but differing brain registrations are conflicts requiring review, not duplicate append targets. If ownership is ambiguous, preserve and report it.

Keep the existing event semantics: Copilot successful postToolUse, Codex every completed PostToolUse including failures, Gemini AfterTool without an error, and each provider's startup/resume injection behavior. Preserve isolated interpreter flags, launcher root discovery, context caps, timeouts, and provider-specific output shapes. The hook scripts must remain usable alone. Recheck provider registration schemas against official documentation before changing registration mechanics; do not infer current support from old live-probe evidence.

Verification: none, each individual provider, all combinations, reruns, and changing selections after installation. Unselected provider files and all user-global files must remain unchanged. Test unrelated handlers/settings preservation, malformed/duplicate JSON, conflicting brain handlers, and launcher execution from paths containing spaces. Exercise registered commands with representative provider payloads. Stop after the provider-selection matrix and preservation cases pass.

Observed 2026-10-21 on macOS, Python 3.14.6: fourteen subprocess tests passed, including all eight provider combinations, unchanged reruns, provider additions with edited todos, unselected malformed configuration preservation, selected malformed/duplicate-key rejection before mutation, unrelated settings/handlers, ambiguous brain conflicts, and six startup/post-tool registered commands from a nested directory containing spaces. The selected host interpreter is pinned while the source root-discovery code and provider fields remain intact. Copilot progress lines and its final context JSON are both parsed. Official registration references were rechecked: [Copilot](https://docs.github.com/en/copilot/reference/hooks-reference), [Codex](https://learn.chatgpt.com/docs/hooks), and [Gemini](https://geminicli.com/docs/hooks/reference/). No live delivery or Windows/Linux pass is claimed. Subsequent malformed-config checks also reproduced acceptance of NaN and non-string command fields; both now fail before writes and the fourteen-test suite passes again.

### Milestone 4: Usable installation and migration skill

Status: done
Acceptance: met

#### T4: Author runtime guidance and migration procedure

Prerequisites: T3. Inputs: verified installer behavior and D1-D7. Own SKILL.md, `references/migration.md`, README.md, and `evals/evals.json`.

The runtime skill has `argument-hint` and `disable-model-invocation: true`, per D8. Its description is human-facing. The requested authoring guidance reference belongs in `skills/default/create-skill/SKILL.md`. The runtime skill identifies the target and requested providers, inventories guidance including any existing root index, and runs installer inspection. Before mechanical installation, it preserves and migrates meaningful content from an existing root index, then supplies `--index-reviewed`; an already generated inventory only needs review. It resolves other concrete conflicts through reviewed edits or eligible `--keep-existing` choices, applies mechanical installation, completes the remaining guidance migration, and verifies the result. This runtime ordering is required even though T4 authors the procedure after the installer tasks. Do not require another approval for conflict-free work already requested by the target user. Read `references/migration.md` only when existing guidance requires migration. Keep skill maintenance, source refresh instructions, eval commands, and benchmark procedures in README.md.

Migration starts with an inventory of root/nested instructions, memory/KB notes, linked references, relevant existing skills, and registrations that load legacy guidance. Decompose obligations, including conditions, scope, exclusions, and approval requirements. Record each source obligation as retained, moved with an exact destination, consolidated with equivalent coverage, or obsolete with a specific reason. Preserve the mapping in a concise target migration audit under `brain/audits/`; do not dump source transcripts or secrets into it.

Move repository knowledge into topic notes, preserve scoped behavioral rules where their scope remains effective, and place reusable procedures in matching skills after reading their existing content. Keep root/nested AGENTS policy and provider compatibility bridges that still serve a purpose. Update references before removing legacy files. Remove retired ingestion/loading registrations only when they belong to the superseded guidance workflow and preservation is verified; leave unrelated hooks intact. Do not recreate OKF/frontmatter requirements, source-ingestion automation, global tool guards, automatic semantic maintenance, or a second knowledge system.

Validate every migration obligation, navigation, preserved scope, and source retirement before declaring migration complete. Uncertain or conflicting guidance remains intact and is reported for a concrete decision. Do not treat bulk copying legacy folders or rewriting every instruction into prose as a migration. Never make a real repository migration part of authoring this skill; use disposable fixtures.

Verification: at least three realistic evaluations covering a fresh install with no hooks, a legacy guidance migration with selected providers and scoped rules, and a conflicting/repeated installation that preserves user changes. Include conditions and approval constraints that must survive migration, stale links to repair, and an unrelated provider handler. Use deterministic checks for file and config outcomes and review semantic obligation preservation directly. Benchmark against `without_skill` as required by authoring guidance. Stop at an authored, evaluated skill; integrated/native acceptance is T5.

Observed 2026-10-21: all seven skill validators passed (brain-install plus six installed skills), runtime links resolve, and the requested invocation fields parse correctly. Six initial evaluation runs were independently graded 27/28; after the general trigger-equivalence correction, a fresh repeated-install pair passed 4/4 per arm. Selected evidence totals 14/14 per arm across three scenarios. Baselines share mechanical assets; no performance advantage is claimed. Missing metrics, model changes, baseline gaps, original failures, and evidence locations are recorded in [evaluation results](evaluation-results.md). Both initial and selected static viewers were generated with the existing skill-creator tooling.

### Milestone 5: Integrated and native verification

Status: in progress
Acceptance: not met

#### T5a: Prepare native CI while evaluations complete

Prerequisites: T3. The installer subprocess tests are already verified locally. Add the bundle path trigger and its unittest command to `.github/workflows/brain-hooks.yml`, preserving the existing six-cell matrix, ten-minute limit, and hook checks. Verify the YAML still describes that matrix and budget. This mechanical CI preparation is independent of semantic evaluation results; final acceptance remains T5. Commit/push is now authorized for this implementation; keep T5 open until native results pass.

Observed 2026-10-21: the workflow now triggers on `skills/default/brain-install/**` and runs the installer unittest suite. Parsed YAML retains all six platform/version cells, existing hook checks, and the ten-minute budget. A narrow `.gitignore` exception retains the synthetic legacy release-skill fixture, which the generic `[Rr]elease/` rule otherwise excluded.

#### T5: Prove the complete bundle

Prerequisites: T4 and T5a. Inputs: the integrated bundle, focused test evidence, evaluation artifacts, and existing CI workflow. Own final integration verification; T5a owns the focused workflow registration.

Run the installer from a relocated copy into disposable targets, with disposable homes, and exercise the installed manual indexer plus selected launchers. Prove fresh installation, migration preservation, conflict behavior, unchanged reruns, and hook-selection transitions together. All runtime resources must resolve without this checkout. Check source snapshot parity with explicit exceptions for portable skill/helper adaptations. Inspect diffs to ensure unrelated source skills, manual changes, and global installations remain untouched.

Extend the existing six-cell native matrix for Python 3.12/3.14 on Windows/Linux/macOS. Keep its ten-minute job budget; do not move these tests into the slow general workflow or remove existing coverage. Native success is required to claim cross-platform installer verification. If dispatch needs a push not yet authorized, leave native acceptance open and report that exact owner action. Live-provider delivery is separate from process/config testing: report any live checks actually performed, but do not inherit historical delivery claims or add a mandatory Gemini live session to this installer scope.

Observed 2026-10-21 on macOS/Python 3.14.6: `python3 -m unittest discover -s skills/default/brain-install/tests -p 'test_*.py'` passed 15 tests in 4.505 seconds; `python3 scripts/test-brain-hooks.py` passed 26 tests with one platform-specific skip in 4.541 seconds. `generate-hooks.py --check` reports 60 current outputs. All eight validators and the unknown-field negative case passed; principle/index/AGENTS/hook parity, syntax, resource links, final metadata, new-bundle whitespace, and `git diff --check` passed. The workflow YAML preserves six native cells and the ten-minute budget. No native matrix was dispatched for these uncommitted changes.

Completion requires passing integrated tests, skill validation/evaluations, and native checks with evidence. At the end of a code-changing implementation session activate reflect; persist only new durable findings. Do not mark completion from a clean diff alone. Stop without committing or pushing unless the user separately authorizes those actions.

## Concrete Steps

The next action is to commit and push the reviewed brain-install implementation, then inspect its native six-cell matrix and repair failures; the user explicitly authorized this on 2026-10-21. T1-T4, independent semantic grading, T5a CI wiring, and T5 local integration are verified. After publication, inspect the actual six-cell native run and repair failures before marking T5 acceptance met. Do not treat older workflow runs as evidence for these unpublished changes. Evidence is retained in [evaluation results](evaluation-results.md) and `/private/tmp/brain-install-evals-g5zwusni/`.

Run commands from the repository root. The following are the implementation verification commands; actual observed results are recorded per milestone and in the final integration evidence:

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
