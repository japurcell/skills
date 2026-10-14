# Install default and opt-in Forest Service skills

This living ExecPlan is saved at `docs/conditional-skill-installer/ExecPlan.md` and follows [exec-plans](../../.agents/skills/exec-plans/SKILL.md). Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current.

## Purpose / Big Picture

Users should receive general-purpose skills by default and Forest Service skills only when they select them. Both installers will expose the same flags and environment-variable behavior, while continuing to install individual skills into `~/.agents/skills/<name>/`.

The originating requirement is [Conditional Skill Installer](../ideas/1-conditional-skill-installer.md). The user confirmed the design on 2026-10-14, saved the plan, and subsequently invoked `execplan-implement` to authorize implementation, disposable-fixture verification, private task branches, and local commits. Work runs on base branch `codex/plan-conditional-skill-installer`. Pushing and CI dispatch remain unauthorized; native Windows evidence may require an owner action.

The feature changes skill selection only. Agents, references, RTK configuration, and provider hooks retain their existing installation rules and safety checks. Creating the future `agency-priorities` skill is outside this effort.

## Progress

- [x] (2026-10-14) [milestone-0] Inspect installer behavior, consumers, CLI sources, and test routes; complete the design interview.
- [x] (2026-10-14) [milestone-0] Obtain confirmation of the shared design and permission to save this plan without implementation.
- [x] (2026-10-14) [milestone-0] Save and review this plan; verify links, whitespace, and the implementation stopping boundary.
- [ ] [milestone-1] T1: Migrate published skills and deliver default-category traversal in both installers with disposable-home proof.
- [ ] [milestone-1] T2: Repair maintained consumers, import destinations, authoring paths, and fixtures; verify their public behavior.
- [ ] [milestone-1] Verify the integrated layout and default-install result.
- [ ] [milestone-2] T3: Deliver selection flags, environment precedence, help, diagnostics, and validation through successive public-CLI test cycles.
- [ ] [milestone-2] Verify the complete behavior matrix in Bash and PowerShell.
- [ ] [milestone-3] T4: Obtain integrated source and native Windows evidence; preserve existing installer protections.
- [ ] [milestone-4] T5: Finish user documentation and the single coordinated agent-documentation pass; check links and the final diff.

## Surprises & Discoveries

- Both installers currently enumerate immediate `skills/` entries. Category wrappers would otherwise be installed as skills named `default` and `forest-service`. Evidence: `copy_skills` in `scripts/install.sh` and `Copy-Skills` in `scripts/install.ps1`.
- The current installers preserve destination skills that are no longer selected or present in source. This feature must preserve that behavior. Installation without Forest Service selection is not an uninstall operation.
- Destination mutation starts before skill copying: the installers apply RTK configuration and install Codex agents first. Argument, environment, and category validation must run before these operations, not merely before `copy_skills` or `Copy-Skills`.
- Read-only exploration found 57 root directories with a direct `SKILL.md` and no existing Forest Service skill. The count is a source snapshot, not a hard-coded acceptance value. `docs/ideas/2-agency-priorities-skill.md` names a future Forest Service skill.
- Native PowerShell parameter binding accepts single-hyphen forms but rejects the requested literal `--forest-service` and `--fs` spellings. Explicit argument parsing is required for the agreed interface.
- Workspace cleanup scans root-level `skills/*-workspace`, while archives are historical. Moving these into categories would break a separate artifact lifecycle.
- Source and installed paths have different depths. Runtime examples such as `~/.agents/skills/<name>` and installed reference paths must not receive a category prefix. Addy's `rewrite_references` computes paths relative to its destination, so its deeper default destination requires reference-link verification, not only updated test expectations.
- CLI sources contain advice to display help without arguments. The user explicitly chose the existing no-argument installation behavior. Repository stream rules take precedence over differing warning-stream advice in a source article.
- PowerShell is available on the planning host, but this is macOS. Local PowerShell execution cannot prove native Windows behavior. No installer test suite or native Windows CI was run during planning.

## Decision Log

All decisions below were selected or confirmed by the user on 2026-10-14. They are the current implementation contract, not observed implementation behavior.

### D1: Repository and installed layout

Move all currently published root skills into `skills/default/<name>/`. Create `skills/forest-service/` with `.gitkeep` while it has no published skills. Keep `skills/archive/` and generated `skills/*-workspace/` at the root. New generated workspaces also remain at the root, even when the associated skill lives in a category. Install selected leaf directories into `~/.agents/skills/<name>/`, never into a category wrapper.

Default both import workflows to `skills/default/`. Preserve Addy's flat external `SOURCE_ROOT/skills` layout and its explicit destination overrides. Repair maintained source paths and links. Preserve immutable `.agents/sources/`, archived content, and historical transcripts rather than bulk-rewriting them.

### D2: Selection interface and precedence

Both `scripts/install.sh` and `scripts/install.ps1` accept exactly these option spellings:

| Option | Meaning |
| --- | --- |
| `--forest-service` | Install default and Forest Service skills. |
| `--fs` | Alias of `--forest-service`. |
| `--no-forest-service` | Install default skills only, overriding the environment. |
| `-h`, `--help` | Print usage and examples; exit without installation. |

No selection option means consult `INSTALL_FOREST_SERVICE_SKILLS`. Case-insensitive `1` or `true` enables Forest Service installation; `0` or `false` disables it. Unset or empty also disables it. Other nonempty values fail with exit 2. Do not silently trim or accept additional boolean spellings.

Read the environment only if no explicit selection option is present. Thus `INSTALL_FOREST_SERVICE_SKILLS=banana` with `--fs` succeeds at selection, and the same invalid value with `--no-forest-service` selects default only. Help also ignores this variable.

Repeated matching selection flags, including `--fs --forest-service`, are accepted. Any enable/disable combination is an error, independent of argument order. Reject unknown options, operands, PowerShell-only aliases, and option values such as `--fs=true`. There are no positional arguments. Parse the entire argument list before honoring help: help bypasses environment and source validation but does not excuse invalid arguments or conflicting selection flags.

No arguments still perform installation using the environment/default rule. No prompts are introduced.

### D3: Source validation and preservation

Before any destination mutation, require both category directories even if Forest Service selection is disabled. Empty categories are valid. Enumerate immediate skill directories inside each category; preserve the existing case-sensitive `*-workspace` and exact `archive` exclusions. `.gitkeep` is a marker, not a skill. Other non-directory files are not skill candidates. An unexpected non-excluded directory without a direct `SKILL.md` is a source error.

Reject duplicate destination basenames case-insensitively across both categories, including disabled Forest Service entries. Compare basenames, not frontmatter names. Frontmatter remains subject to authoring validation. Diagnose the conflicting source paths before writing to the home or configured Codex agent destination. Case-insensitive collision checks must not change the case-sensitive workspace/archive exclusion rules.

Preserve existing copying, link handling, executable modes, and installed pruning of `evals/`, `README.md`, `LICENSE.txt`, and `LICENSE.md`. Preserve previously installed Forest Service and unrelated skills. Do not add stale-skill deletion or a legacy root-level installation fallback.

### D4: CLI output and failure behavior

Help and examples go to stdout. Installer status, progress, warnings, and errors go to stderr. Success/help use exit 0; invalid arguments or a consulted invalid environment value use exit 2; category/source and installation failures use exit 1. Apply this classification to the installer entry points, including translating helper failures into an installer failure while preserving their diagnostic and recovery text.

Help must work without valid sources or installer dependencies. Diagnostics identify the bad option, variable, missing source, or conflicting paths and explain the correction. Existing generated-hook stale-output advice must still name the exact recovery command. Do not add dry-run, version, JSON, completion, decorative output, or new interactive flows.

## Outcomes & Retrospective

The design interview and saved-plan verification are complete. Implementation is now authorized; T1 is the ready frontier. No implementation changes have been made yet. The coordinator owns delegation, serial integration, and plan updates. Implementation acceptance and native Windows acceptance remain open.

## Context and Orientation

Work from `/Users/adam/.codex/worktrees/d238/skills`. `scripts/install.sh` owns Bash copying through `copy_skills`; `scripts/install.ps1` owns PowerShell copying through `Copy-Skills` and the link-safe `Copy-Entry` helpers. Both have source checks, RTK preflight, generated-hook freshness validation, and provider configuration preflight before their write phase. Neither currently implements the agreed argument interface.

`scripts/test-install.sh` and `scripts/test-install.ps1` build disposable repositories and homes. Their skill fixtures currently use flat paths such as `skills/alpha`. The PowerShell `Invoke-InstallProcess` helper is the existing child-process boundary for home/environment isolation and needs argument forwarding plus reliable environment restoration. These suites also cover provider settings, Codex agent conversion, modes, links, and malformed-input immutability; retain that coverage.

`scripts/addy-install.sh` imports external flat-source skills, prefixes names, and rewrites reference paths. Its default local destination is currently repository `skills/`. `scripts/test-addy-install.sh` covers explicit and default destinations. `scripts/import-skill-repos.sh` maps other imports into root skills; it is human-only and must not be executed by an agent.

`scripts/test-all.py` explicitly registers the `spec-to-tasks` and `prd-ralph-loop` grader paths; `scripts/test_test_all.py` asserts them. Moving skills requires updating those registrations and any maintained file-based test consumers. Preserve external-source fixtures and runtime-installed paths that intentionally remain flat.

Applicable instructions are [repository workflow](../../.agents/instructions/repo.md), [scripts](../../.agents/instructions/scripts.md), [PowerShell](../../.agents/instructions/powershell.md), [skills](../../.agents/instructions/skills.md), and their [testing routes](../../.agents/instructions/testing.md). Follow `.editorconfig`. Before future source design or edits, activate the `tdd` skill. Before changing published skill guidance, activate the `create-skill` and `writing-for-agents` skills as applicable. Protected `AGENTS.md` sections remain intact.

## CLI Guidance Reconciliation

The three local CLI sources are [CLIG](../../.agents/sources/clig-dev.md), [CLI Design Guidelines](../../.agents/sources/cli-design-guidelines.md), and [12 Factor CLI Apps](../../.agents/sources/12-factor-cli-apps.md). Their ingestion manifest entries were active during discovery; no source-ingestion work is needed.

Implement the applicable advice through descriptive long options, reserved help options, discoverable usage with examples, uppercase underscore environment naming, explicit flag precedence, stable streams/exits, actionable failures, and unattended operation. Keep no-argument installation as the documented user-approved exception to no-argument help advice. Follow repository stderr rules when sources disagree. Optional version, dry-run, JSON, completion, and terminal decoration suggestions are outside the agreed feature. Do not modify raw source articles to reconcile these choices.

## Plan of Work

### Milestone 0: Save the approved plan

Status: done
Acceptance: met

This document was saved and reviewed against Q1-Q18. A read-only check verified all 10 local links, required sections, whitespace, and the absence of em dashes. `rtk git diff --check` and `rtk proxy python3 scripts/lint-okf.py` exited 0. `rtk git status --short` showed only the new plan directory. The end-of-session `update-agent-docs` admission pass found no warranted KB changes. Completion proves documentation readiness only. It does not authorize Milestone 1.

### Milestone 1: Deliver the category layout and repair consumers

Status: in progress
Acceptance: not met

#### Task T1: Migrate published skills and default traversal

Prerequisites: explicit user authorization to implement. Inputs: D1 and D3, the current root `SKILL.md` inventory, both installers, and both installer fixture suites. Own the published directory moves, new category directories, `copy_skills`, `Copy-Skills`, and matching default-copy fixture changes.

Start with a public installer fixture that places `alpha` under `skills/default/` and confirms `~/.agents/skills/alpha/SKILL.md` exists without a wrapper. Observe the current failure, then implement the smallest layout/traversal change and repeat for PowerShell. Move the complete published bundles, including evaluation fixtures, without changing unrelated content. Keep root workspaces and archives in place. Preserve installed pruning and copy semantics.

Verify both installer suites with category fixtures, including an empty Forest Service category, generated artifact exclusions, and preservation of unrelated installed files. Stop at working default traversal; conditional selection and the complete new validation contract are T3.

#### Task T2: Repair maintained source consumers and imports

Prerequisites: T1's moved layout. Inputs: D1, the old-to-new path inventory, current import scripts and consumer tests. Own `scripts/test-all.py`, `scripts/test_test_all.py`, `scripts/addy-install.sh`, `scripts/test-addy-install.sh`, `scripts/import-skill-repos.sh`, `.gitignore` path exceptions, maintained links, and layout-critical skill/agent guidance.

Search maintained files for literal old skill paths and one-level discovery assumptions. Update the test registry, `skills/default/create-skill/SKILL.md`, relevant README paths, `.agents/instructions/skills.md`, `.agents/instructions/testing/skills.md`, and affected admitted guidance in `.agents/memory/known-issues/skills.md`. Adjust `.gitignore` exceptions for moved checked-in fixtures without exposing generated outputs. Leave `.agents/skills/` and its tests at their existing local-workflow paths.

Route Addy's default destination to `skills/default/`, preserving explicit overrides and external source paths. Update only destination sides of `import-skill-repos.sh` mappings. Use syntax/static review for that human-only script; do not invoke it. For moved skill bundles, preserve intra-bundle links and distinguish source-relative paths from installed runtime examples. Check Addy reference rewriting and installed shared-reference resolution before considering path migration complete; fix any observed broken installed links at the appropriate copying/import boundary with a public behavior test, rather than globally replacing relative paths.

Verify Addy's public fixture suite, runner registry tests, relocated grader suites, changed skill-definition validation, and maintained link targets. Stop after all live consumers resolve to the new layout. Historical references and immutable raw sources stay unchanged.

#### Integrated milestone proof

Run both default installer suites and consumer checks against the same migrated tree. Confirm every maintained published skill is in one category, default skill leaves install flat, no wrappers/artifacts install, and consumer fixtures still run. T1 and T2 individual results do not establish this integrated acceptance.

### Milestone 2: Deliver the agreed CLI contract

Status: open
Acceptance: not met

#### Task T3: Implement selection, help, and preflight parity

Prerequisites: integrated Milestone 1. Inputs: D2-D4 and both disposable-home fixture suites. Own argument handling, selection state, source inventory validation, user-facing output, and matching cases in `scripts/install.sh`, `scripts/install.ps1`, `scripts/test-install.sh`, and `scripts/test-install.ps1`.

Use successive vertical test cycles at the installer process boundary: one failing behavior, its minimal implementation, then the next case. Implement native shell argument scanning with identical exact spellings; PowerShell must handle literal double-hyphen arguments explicitly. Reuse existing standard-library/runtime facilities for category validation instead of introducing packages. Keep selection and validated source enumeration separate from copying so both categories can be validated while only selected skills are copied.

Order execution as full argument validation, help exit if requested, selection/environment resolution, category and collision validation, existing dependency/configuration preflights, then existing writes. Preserve existing safety checks and diagnostics. Ensure usage and errors do not accidentally enter PowerShell's success pipeline and that native child output is routed appropriately. Verify exit codes at the process boundary, not through private parser calls.

Stop after the complete matrix in Validation and Acceptance passes in both local suites. Native Windows acceptance remains T4.

### Milestone 3: Prove integrated and native Windows behavior

Status: open
Acceptance: not met

#### Task T4: Verify the integrated implementation

Prerequisites: Milestones 1 and 2. Inputs: changed tree, CLI matrix, existing regression suites, and `.github/workflows/ready-ideas-windows.yml`. Own integration verification and minimal workflow adjustments only if the existing native Windows job does not exercise the changed suites.

Run the targeted commands below sequentially where fixture mutation could interfere. Obtain native Windows execution of `scripts/test-install.ps1` through the existing workflow or a Windows-capable host. Record the run URL or host, revision, command, result, and any junction-capability limit. A macOS `pwsh` pass or a platform skip cannot satisfy Windows acceptance. Do not dispatch CI or push changes without session authorization for that action.

Stop with acceptance not met if Windows evidence is unavailable. Preserve completed local evidence and state the exact remaining external action. Do not weaken failing tests, synthesize a pass, or treat planned commands as results.

### Milestone 4: Finish documentation and quality checks

Status: open
Acceptance: not met

#### Task T5: Synchronize documentation and close the effort

Prerequisites: integrated implementation work and tests have finished; native Windows acceptance must be recorded before full completion. Inputs: final diff, current README, CLI help, changed authoring guidance, and admission rules. Own final documentation reconciliation and the single end-of-session KB pass.

Document both invocation forms, environment values and precedence, explicit disabling, preservation of previously installed skills, empty initial Forest Service content, and error recovery. After all work and any delegated tasks finish, activate `update-agent-docs` once. Apply knowledge admission, update the smallest relevant canonical documents, and activate `okf-authoring` for canonical semantic edits. Do not create memory solely to record this task. Repair affected indexes and inbound links without editing protected `AGENTS.md` sections.

Review the final diff for lost behavior, incorrect installed paths, ignored fixtures, and unauthorized scope. Record actual outcomes here. Follow repository retention policy when this implementation effort is complete; the current plan remains active while implementation or acceptance is pending.

## Concrete Steps

The next unfinished implementation action is T1: migrate published skills and default traversal in an isolated implementer worktree. The user's `execplan-implement` invocation authorizes this work and local commits.

The reconciled task graph is T1 before T2; their integrated proof before T3; T3 before T4; T4 before T5. Shared installer and fixture files require serialized ownership. The invoked implementation skill requires fresh implementer subagents for distinct tasks. The coordinator owns the ExecPlan and final shared canonical-document admission pass; T2 owns only its specifically named layout guidance repairs.

Use the repository root as the working directory for every command. Prefix shell commands with RTK; use `rtk proxy` when exact subprocess behavior matters. Keep disposable profile roots in task-specific variables rather than repurposing `$HOME` in the orchestrating shell. Tests establish the child process home themselves.

## Validation and Acceptance

Implementation checks below are expected future evidence. None was executed during planning.

### Public behavior matrix

Use disposable copied repositories containing default `alpha` and Forest Service `agency-priorities` fixtures. A real Forest Service skill need not be added to production for these tests. Compare installed files, stdout, stderr, exit status, and whole-home/configured-Codex-destination fingerprints where failure must be immutable.

| Scenario | Expected result |
| --- | --- |
| No arguments; environment unset, empty, `0`, or case-varied `false` | Default skill only; exit 0. |
| No arguments; environment `1` or case-varied `true` | Both skill leaves installed flat; exit 0. |
| `--forest-service` or `--fs`; environment disabled or invalid | Both skill leaves; explicit flag wins. |
| `--no-forest-service`; environment enabled or invalid | Default skill only; explicit flag wins. |
| Repeated enabling aliases or repeated disabling flag | Accepted; same result as one flag. |
| Enable and disable in either order | Exit 2, actionable stderr, no writes. |
| Unknown option, operand, `--fs=true`, or consulted invalid environment | Exit 2, actionable stderr, no writes. |
| `-h` or `--help`; invalid environment, absent sources/dependencies | Usage/examples on stdout, exit 0, no writes. |
| Help with unknown arguments or conflicting selection flags | Exit 2, no writes. |
| Either category missing, including disabled Forest Service | Exit 1, missing-path diagnostic, no writes. |
| Empty Forest Service directory with `.gitkeep`, enabled or disabled | Valid; no marker or wrapper installed. |
| Category child directory lacks `SKILL.md` | Exit 1, source-path diagnostic, no writes. |
| Equal or case-only destination basenames across categories | Exit 1 with both paths, even when Forest Service is disabled; no writes. |
| Excluded `archive` or `*-workspace` entries | Not installed; retain existing case-sensitive exclusion semantics. |
| Opted-in install followed by default-only install | Previously installed Forest Service skill remains. |
| Successful installs and repeats | Existing pruning, modes, links, settings preservation, and agents/hooks behavior remain correct; status on stderr. |

On case-insensitive hosts, create case-only collision fixtures in different categories so both source paths can exist. Keep frontmatter identity tests separate from destination-basename collision checks. For immutability cases, fingerprint before invoking the actual entry point; also confirm RTK application, Codex conversion, directory creation, and copy stages were not reached.

### Targeted commands

Run these after implementation, adapting only the documented source path when a skill was relocated:

    rtk proxy bash -n scripts/install.sh
    rtk proxy bash scripts/test-install.sh
    rtk proxy pwsh -NoProfile -File scripts/test-install.ps1
    rtk proxy bash -n scripts/addy-install.sh
    rtk proxy bash scripts/test-addy-install.sh
    rtk proxy bash -n scripts/import-skill-repos.sh
    rtk proxy python3 scripts/test_test_all.py
    rtk proxy python3 scripts/test-rtk-stable.py
    rtk proxy python3 scripts/test-codex-agents.py
    rtk proxy python3 skills/default/spec-to-tasks/evals/test_grade_benchmark.py
    rtk proxy python3 skills/default/prd-ralph-loop/evals/test_grade_benchmark.py
    rtk proxy python3 -m unittest discover -s skills/default/handoff/evals -p test_grade_benchmark.py
    rtk proxy python3 -m unittest discover -s .agents/skills/exec-plans/evals -p test_grade_benchmark.py
    rtk proxy python3 scripts/test-all.py --list
    rtk proxy python3 scripts/lint-okf.py
    rtk git diff --check

Each check must exit 0 and assert its relevant behavior, not merely launch successfully. For changed skill definitions, run the relocated validator with vendored YAML, for example:

    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/create-skill

Validate other changed skill definitions similarly. Do not run live model evaluations, imported-repository orchestration, account-wide installers, or packaging solely because directories moved. Missing tooling is a verification blocker, not a passing skip. Use broader aggregate testing only when changed consumers, failures, or unresolved integration concerns warrant it.

Native Windows must run `pwsh -NoProfile -File scripts/test-install.ps1` on the implementation revision. Syntax checks and non-Windows PowerShell results are additional evidence, not substitutes.

### Saved-plan acceptance

For this planning-only session, verify this file's local links and the Q1-Q18 obligations, run `rtk git diff --check`, and inspect `rtk git status --short`. The only intended change is this ExecPlan. Do not run implementation acceptance commands while merely saving the plan.

## Idempotence and Recovery

The layout migration is a tracked move, not a new import. Inventory current published directories before editing and verify old/new identities to avoid nesting an already-moved bundle. Do not move root workspaces, archives, or other contributors' unrelated changes. If implementation is abandoned, restore only the effort's known moves and edits after reviewing the diff; do not reset the whole worktree.

CLI and source-validation failures must leave installed destinations unchanged. Runtime failures after the write phase begins retain the existing installer's partial-update behavior; this feature does not claim transactionality for the entire multi-provider install. Correct the reported prerequisite or I/O problem and retry with the same selection. Preserve existing backup/configuration safeguards and unrelated files. Do not remove installed Forest Service skills as recovery.

Test cleanup owns only its exact disposable paths. Do not mutate real home directories for proof. If native Windows validation or another external action is unavailable, leave the corresponding milestone open and document the owner, command, and missing evidence inline.

## Interfaces and Dependencies

The public interfaces are the two installer processes, their exact option spellings, `INSTALL_FOREST_SERVICE_SKILLS`, the category source tree, and the existing flat installed destinations. Consumer verification uses Addy's public fixture process, the aggregate runner's CLI, relocated graders, and skill-definition validation. These tests observe process output and filesystem results rather than private parser implementations.

Keep Bash portability consistent with the current supported host shell; do not require newer Bash-only collection syntax without existing support. PowerShell remains `pwsh -NoProfile` compatible and uses its existing link-safe/mode-preserving copy helpers. Python is already an installation dependency; use standard-library facilities if shared validation or reference-path handling requires them. Add no external module or package requirement for option parsing.

## Artifacts and Notes

Planning evidence is the current source inspection and the confirmed interview contract recorded above. Actual implementation test transcripts, CI references, and milestone acceptance evidence will be added when obtained. Do not mark an implementation milestone done from planning evidence.
