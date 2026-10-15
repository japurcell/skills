# Install default and opt-in Forest Service skills

This living ExecPlan is saved at `docs/conditional-skill-installer/ExecPlan.md` and follows [exec-plans](../../.agents/skills/exec-plans/SKILL.md). Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current.

## Purpose / Big Picture

Users should receive general-purpose skills by default and Forest Service skills only when they select them. Both installers will expose the same flags and environment-variable behavior, while continuing to install individual skills into `~/.agents/skills/<name>/`.

The originating requirement is [Conditional Skill Installer](../ideas/1-conditional-skill-installer.md). The user confirmed the design, authorized implementation and five review repairs, and subsequently requested pushing the branch, running native Windows verification, and recording its results. That request supersedes the earlier no-push instruction. Automatic approval review nevertheless rejected publication twice because it requires explicit approval of the payload to the specific public destination [japurcell/skills](https://github.com/japurcell/skills). Work remains on `codex/plan-conditional-skill-installer`; no push or CI run occurred. The next action is that destination-specific user approval, followed by a normal push and native verification.

The feature changes skill selection only. Agents, references, RTK configuration, and provider hooks retain their existing installation rules and safety checks. Creating the future `agency-priorities` skill is outside this effort.

## Progress

- [x] (2026-10-14) [milestone-0] Inspect installer behavior, consumers, CLI sources, and test routes; complete the design interview.
- [x] (2026-10-14) [milestone-0] Obtain confirmation of the shared design and permission to save this plan without implementation.
- [x] (2026-10-14) [milestone-0] Save and review this plan; verify links, whitespace, and the implementation stopping boundary.
- [x] (2026-10-14) [milestone-1] T1: Migrate published skills and deliver default-category traversal in both installers with disposable-home proof; integrated commit `1dadc9993b2885f5448d91a97177872509c706fc`.
- [x] (2026-10-14) [milestone-1] T2: Repair maintained consumers, import destinations, authoring paths, and fixtures; integrated commit `d141e63d6531973f7de98759610d216635b212a0` with reference and linked-target proof.
- [x] (2026-10-14) [milestone-1] Verify the integrated layout and default-install result on base `d141e63d`: Bash, macOS PowerShell, Addy, registry (14), spec-to-tasks (38), prd-ralph-loop (13), handoff (20), skill validator, 29 maintained links, OKF, and whitespace checks passed.
- [x] (2026-10-14) [milestone-2] T3: Deliver selection flags, environment precedence, help, diagnostics, and validation through public red/green cycles; integrated `af3e4806f32a3d89cafa962bd579819af496019a`.
- [x] (2026-10-14) [milestone-2] Verify the complete behavior matrix in Bash and macOS PowerShell against integrated implementation `6f406a1f`; all targeted local checks passed, retained in `verification.json`.
- [x] (2026-10-14) [milestone-2] R1: Make the reference-rebasing CLI directly executable; integrated `d07be4368ecc9b190867979ebc82c2bd050cc71a`. Direct help passed on base, with identical content blob and mode `100755`.
- [x] (2026-10-14) [milestone-3] T4 local: Obtain integrated source evidence and preserve existing protections; evidence commit rebased to integrated `7fe20edaef6485d1263c9c8f9cad8bd3e3e9c40c`.
- [x] (2026-10-14) [milestone-3] Verify configured destination: public `japurcell/skills`, ADMIN permission, and existing feature-base commit confirmed through GitHub. Outgoing added-line private-key/AWS/GitHub credential-pattern scan found zero matches.
- [ ] [milestone-3] T4 Windows: Push and run native verification. Automatic approval review rejected two pushes of `10ae473e` pending explicit approval to publish this branch payload to public `japurcell/skills`. No push or Windows run occurred.
- [x] (2026-10-14) [milestone-4] T5D: Finish user-facing installation documentation; integrated `3110cea24bd20221b235b3d941f345bb02c3fc72`, with both public help outputs and source diagnostics checked.
- [x] (2026-10-14) [milestone-4] Complete the single coordinated agent-doc pass after all delegated work finished; repair PowerShell ordinal-matching/profile guidance, review category-path repairs, verify OKF/links/whitespace, and preserve protected AGENTS sections.
- [ ] [milestone-4] T5: Close the effort after native Windows acceptance; retain current owner actions and this active plan until then.
- [x] (2026-10-14) [milestone-1] R4: Repaired eight source-reference pointers and the live benchmark path in `e63d4951`. All eight targets resolve; four vendored-YAML definition validations and whitespace checks passed.
- [x] (2026-10-14) [milestone-2] R2: NFC-normalized casefold validation rejects canonical aliases before writes. Both full suites and focused enabled/disabled immutability cases passed; integrated as `a18e778a`.
- [x] (2026-10-14) [milestone-2] R3: Safe read-only rebasing, repeat copying/pruning, dotted references, actual Addy targets, and hardlink refusal/pruning passed both full suites at `671f1e78`; integrated as `362dad54` with only this plan differing after rebase.
- [x] (2026-10-14) [milestone-2] R5: Independent review found no further required findings. Seven focused public cases per installer, affected consumers, four definitions, and source targets passed at `698d5410`. Retained source-identical full-suite proof and repair audit; final coordinated KB pass warranted no changes. No push.

## Surprises & Discoveries

- Adversarial review of `4f2b2f4e..a5f50664` reproduced five omissions after the earlier suites passed: NFC/NFD destination aliases overwrite one leaf on macOS; preserved `0444` Markdown raises `PermissionError` during rebasing; valid leading `./` reference paths remain broken; eight live Addy source pointers still have the old depth; create-skill's live benchmark instruction still uses a nonexistent flat source path. Public Bash/macOS PowerShell reproductions and read-only source resolution establish these findings. Earlier evidence remains historical proof of its tested cases, not acceptance of these repairs.

- The original installers at `4f2b2f4e` enumerated immediate `skills/` entries. Category wrappers would otherwise have been installed as skills named `default` and `forest-service`; current installers enumerate category leaves.
- R3 public fixtures exposed coupled read-only behavior: repeat copying and pruning require writable installed directories, and temporary permission elevation on stale excluded hardlinks changed an outside inode from `0444` to `0644`. Final public and helper tests now preserve outside inode bytes/modes and fail closed before changing read-only shared files. Both full suites passed; native Windows branches remain unexecuted.
- Publishing was blocked twice by automatic approval review, including after GitHub confirmed the configured public destination, ADMIN access, and the feature base. The review requires explicit approval of this branch payload to that public repository; the general push request was not accepted as sufficient. No indirect publication or CI workaround was attempted.
- The current installers preserve destination skills that are no longer selected or present in source. This feature must preserve that behavior. Installation without Forest Service selection is not an uninstall operation.
- Destination mutation starts before skill copying: the installers apply RTK configuration and install Codex agents first. Argument, environment, and category validation must run before these operations, not merely before `copy_skills` or `Copy-Skills`.
- Read-only exploration found 57 root directories with a direct `SKILL.md` and no existing Forest Service skill. The count is a source snapshot, not a hard-coded acceptance value. `docs/ideas/2-agency-priorities-skill.md` names a future Forest Service skill.
- Native PowerShell parameter binding accepts single-hyphen forms but rejects the requested literal `--forest-service` and `--fs` spellings. Explicit argument parsing is required for the agreed interface.
- Workspace cleanup scans root-level `skills/*-workspace`, while archives are historical. Moving these into categories would break a separate artifact lifecycle.
- Source and installed paths have different depths. Runtime examples such as `~/.agents/skills/<name>` and installed reference paths must not receive a category prefix. Addy's `rewrite_references` computes paths relative to its destination, so its deeper default destination requires reference-link verification, not only updated test expectations.
- CLI sources contain advice to display help without arguments. The user explicitly chose the existing no-argument installation behavior. Repository stream rules take precedence over differing warning-stream advice in a source article.
- PowerShell is available on the planning host, but this is macOS. Local PowerShell execution cannot prove native Windows behavior. No installer test suite or native Windows CI was run during planning.

## Decision Log

The user selected or confirmed the public contract on 2026-10-14 and authorized all five review repairs. The dated repair details below resolve implementation choices within that scope. These decisions define the current contract; acceptance evidence is recorded separately.

### D1: Repository and installed layout

Published skills now live under `skills/default/<name>/`. `skills/forest-service/` contains `.gitkeep` while it has no published skills. Keep `skills/archive/` and generated `skills/*-workspace/` at the root. New generated workspaces also remain at the root, even when the associated skill lives in a category. Install selected leaf directories into `~/.agents/skills/<name>/`, never into a category wrapper.

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

Repair decision (2026-10-14): normalize destination identity to NFC before Unicode casefold, so canonically equivalent spellings cannot collapse onto one flat target. Keep original path spellings in diagnostics and case-sensitive exclusions. Rebase equivalent leading `./` reference spellings and preserve copied file modes, including read-only Markdown, without rewriting through links. Actual source pointers must resolve from categorized bundles; the installer converts them to flat installed paths.

Read-only repair details: preserve first and repeat installs, directory modes, and existing exclusions. Bash retains `cp -Rp`; the shared helper scopes temporary destination permissions around copying, pruning, and rebasing. PowerShell restores source modes after successful copying and original modes after failure. Pruning remains unconditional when optional shared references are absent; rebasing then does nothing. Do not change outside hardlink inode bytes or permissions. Detach an installed hardlink safely where supported, or fail closed rather than clear shared read-only attributes. Native Windows read-only attribute fixtures remain required; POSIX mode assertions do not establish NTFS ACL behavior.

Preserve existing copying, link handling, executable modes, and installed pruning of `evals/`, `README.md`, `LICENSE.txt`, and `LICENSE.md`. Preserve previously installed Forest Service and unrelated skills. Do not add stale-skill deletion or a legacy root-level installation fallback.

### D4: CLI output and failure behavior

Help and examples go to stdout. Installer status, progress, warnings, and errors go to stderr. Success/help use exit 0; invalid arguments or a consulted invalid environment value use exit 2; category/source and installation failures use exit 1. Apply this classification to the installer entry points, including translating helper failures into an installer failure while preserving their diagnostic and recovery text.

Help must work without valid sources or installer dependencies. Diagnostics identify the bad option, variable, missing source, or conflicting paths and explain the correction. Existing generated-hook stale-output advice must still name the exact recovery command. Do not add dry-run, version, JSON, completion, decorative output, or new interactive flows.

## Outcomes & Retrospective

All five repairs are integrated and independently verified: source paths at `e63d4951`, Unicode validation at `a18e778a`, and reference/mode safety at `362dad54`. R3's full Bash and macOS PowerShell suites passed at `671f1e78`; R5 verified identical implementation/test inputs at `698d5410` and passed seven public repair cases per installer plus affected consumers and four definition validations. Independent review found no further required findings. Milestones 1/2 are accepted locally; [repair-verification.json](repair-verification.json) retains current proof and platform limits. The final coordinated KB admission pass found no warranted changes; OKF lint passed. All clean repair worktrees/branches were removed. Requested publication is blocked by automatic approval review; no push or CI occurred. Native Windows and final closure remain open; a macOS junction skip is not native acceptance. Explicit approval of publication to public japurcell/skills is required next.

## Context and Orientation

Work from `/Users/adam/.codex/worktrees/d238/skills`. `scripts/install.sh` owns Bash copying through `copy_skills`; `scripts/install.ps1` owns PowerShell copying through `Copy-Skills` and the link-safe `Copy-Entry` helpers. Both now implement the agreed raw argument interface, environment resolution, and shared `scripts/validate-skill-sources.py` inventory check before destination mutation. Existing RTK, generated-hook, and provider configuration preflights remain before writes. PowerShell uses ordinal comparisons for literal external strings and isolates Windows profile variables in disposable test children.

`scripts/test-install.sh` and `scripts/test-install.ps1` build disposable repositories and homes. Their skill fixtures now use `skills/default/alpha`, with an empty Forest Service category. The PowerShell `Invoke-InstallProcess` helper is the existing child-process boundary for home/environment isolation and needs argument forwarding plus reliable environment restoration for T3. These suites also cover provider settings, Codex agent conversion, modes, links, and malformed-input immutability; retain that coverage.

`scripts/addy-install.sh` imports external flat-source skills, prefixes names, and rewrites reference paths. Its default local destination is now repository `skills/default/`. `scripts/test-addy-install.sh` covers explicit and default destinations. `scripts/import-skill-repos.sh` destination mappings now use the default category; it is human-only and was syntax-checked, never executed. Both installers invoke `scripts/rebase-skill-references.py` after regular skill copies to adapt shared-reference paths to flat installed leaves. The helper and copy stages preserve linked roots and skip linked descendants.

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

Status: done
Acceptance: met

R4 repaired the eight actual source pointers and benchmark guidance. R5 independently verified all eight source/installed targets through both public installers, the benchmark sample, four definitions, Addy, and registry consumers at `698d5410`. Current acceptance evidence is [repair-verification.json](repair-verification.json); original T1/T2 proof below is retained as historical context.

#### Task T1: Migrate published skills and default traversal

Prerequisites: explicit user authorization to implement. Inputs: D1 and D3, the original pre-migration root `SKILL.md` inventory, both installers, and both installer fixture suites. Own the published directory moves, new category directories, `copy_skills`, `Copy-Skills`, and matching default-copy fixture changes.

Completed evidence: commit `1dadc9993b2885f5448d91a97177872509c706fc`, integrated without rebase changes. Both public fixture suites first failed on missing flat `alpha` installation, then exited 0 after traversal and fixture changes. PowerShell's junction case was skipped on macOS, so this is not Windows evidence. Coordinator review verified 361 `R100` moves and unchanged root workspaces. The task worktree was clean before integration and base tip matched its verified tip.

Completed task scope: public installer fixtures placed `alpha` under `skills/default/` and proved `~/.agents/skills/alpha/SKILL.md` exists without a wrapper. Both old traversals failed that assertion before repair. Complete published bundles, including evaluation fixtures, moved while root workspaces and archives remained in place.

Both suites verified category fixtures, empty Forest Service content, artifact exclusions, and preservation of unrelated installed files. T3 subsequently delivered conditional selection and the complete validation contract.

#### Task T2: Repair maintained source consumers and imports

Prerequisites: T1's moved layout. Inputs: D1, the old-to-new path inventory, current import scripts and consumer tests. Own `scripts/test-all.py`, `scripts/test_test_all.py`, `scripts/addy-install.sh`, `scripts/test-addy-install.sh`, `scripts/import-skill-repos.sh`, `.gitignore` path exceptions, maintained links, and layout-critical skill/agent guidance.

Completed evidence: commit `d141e63d6531973f7de98759610d216635b212a0`, integrated without rebase changes. T2 also owned the observed reference-copy boundary repair in both installers and its shared Python helper. Addy's default-category public case failed before its destination change. Installed source-relative reference links failed before rebasing. Review reproduced external target mutation through a linked skill root, then verified preserved link identity, unchanged external bytes, and safe nested-link handling after repair. The spec-to-tasks suite exposed two repository-root failures and passed all 38 tests after the depth correction. All targeted T2 checks passed; these outcomes do not establish Windows execution.

Completed T2 scope, retained for context: search maintained files for literal old skill paths and one-level discovery assumptions. Update the test registry, `skills/default/create-skill/SKILL.md`, relevant README paths, `.agents/instructions/skills.md`, `.agents/instructions/testing/skills.md`, and affected admitted guidance in `.agents/memory/known-issues/skills.md`. Adjust `.gitignore` exceptions for moved checked-in fixtures without exposing generated outputs. Leave `.agents/skills/` and its tests at their existing local-workflow paths. The following T2 implementation and verification paragraphs describe that completed scope, not current work.

Route Addy's default destination to `skills/default/`, preserving explicit overrides and external source paths. Update only destination sides of `import-skill-repos.sh` mappings. Use syntax/static review for that human-only script; do not invoke it. For moved skill bundles, preserve intra-bundle links and distinguish source-relative paths from installed runtime examples. Check Addy reference rewriting and installed shared-reference resolution before considering path migration complete; fix any observed broken installed links at the appropriate copying/import boundary with a public behavior test, rather than globally replacing relative paths.

Verify Addy's public fixture suite, runner registry tests, relocated grader suites, changed skill-definition validation, and maintained link targets. Stop after all live consumers resolve to the new layout. Historical references and immutable raw sources stay unchanged.

#### Integrated milestone proof

Completed on base `d141e63d`: both default installer suites and Addy passed; registry 14, spec-to-tasks 38, prd-ralph-loop 13, and handoff 20 tests passed. Validator, OKF lint, whitespace, and 29 maintained link checks passed. Inventory matched all 57 original published bundles, with no direct root skill leaves and only `.gitkeep` in Forest Service. Flat install, pruning, exclusions, references, and linked-target preservation were exercised against this same integrated tree. PowerShell's native junction case remains unverified on macOS.

### Milestone 2: Deliver the agreed CLI contract

Status: done
Acceptance: met

R2/R3 repaired Unicode aliases, read-only rebasing and repeats, and dotted references. Both final full suites passed on the source-identical composed implementation. R5 independently passed seven public repair cases per installer at `698d5410`, reviewed safety/failure paths, and found no further required findings. Current local acceptance is [repair-verification.json](repair-verification.json). Native Windows remains Milestone 3.

Historical composed proof: T4 ran the full Bash and macOS PowerShell suites on integrated revision `6f406a1f`, including every agreed CLI/source case, Unicode literal parity, profile isolation, and existing installer protections. All targeted checks exited 0. Evidence is retained in [verification.json](verification.json). This predates the review repairs and is not their acceptance evidence.

#### Task R1: Repair helper executable mode

Completed prerequisite: integrated T2. Source inspection found `scripts/rebase-skill-references.py` recorded as mode `100644`, while script conventions require directly executable helpers. Direct public help failed with permission denied, then passed with exit 0 after mode `100755` was committed as `d07be4368ecc9b190867979ebc82c2bd050cc71a`. The content blob remained `bc20dfbc7895a4ee2412873039c5a201e349f820`. Coordinator verified direct help again on base after matching task/base tips, then removed the clean task worktree and local branch. T3 and all local repair tasks are now complete; the helper remains executable.

#### Task T3: Implement selection, help, and preflight parity

Prerequisites: integrated Milestone 1. Inputs: D2-D4 and both disposable-home fixture suites. Own argument handling, selection state, source inventory validation, user-facing output, and matching cases in `scripts/install.sh`, `scripts/install.ps1`, `scripts/test-install.sh`, and `scripts/test-install.ps1`.

Completed evidence: original task commit `fd5de97af199bcccd4f595af85c3a50890f4c265` rebased to integrated `af3e4806f32a3d89cafa962bd579819af496019a`; all five tested source/test blobs and modes were identical across rebase. Complete installer suites passed on macOS, with native junction proof explicitly skipped. RTK 12 and Codex 14 tests passed. Public cycles reproduced help, selection, environment, preflight ordering, streams, helper exit mapping, invisible-character spellings, exclusion matching, and hook-extension mode failures, then proved their fixes. Failure cases fingerprint home and external `CODEX_HOME`; source failures assert stage markers remain absent. APPDATA/LOCALAPPDATA child isolation and parent restoration passed against disposable external sentinels. Only the four named files and executable `scripts/validate-skill-sources.py` changed. T4 subsequently recorded original composed proof; R5 established current repair proof.

Completed T3 scope, retained for context: use successive vertical test cycles at the installer process boundary: one failing behavior, its minimal implementation, then the next case. Implement native shell argument scanning with identical exact spellings; PowerShell must handle literal double-hyphen arguments explicitly. Reuse existing standard-library/runtime facilities for category validation instead of introducing packages. Keep selection and validated source enumeration separate from copying so both categories can be validated while only selected skills are copied. The following implementation and stopping instructions describe that completed scope.

Order execution as full argument validation, help exit if requested, selection/environment resolution, category and collision validation, existing dependency/configuration preflights, then existing writes. Preserve existing safety checks and diagnostics. Ensure usage and errors do not accidentally enter PowerShell's success pipeline and that native child output is routed appropriately. Verify exit codes at the process boundary, not through private parser calls.

Stop after the complete matrix in Validation and Acceptance passes in both local suites. Native Windows acceptance remains T4.

### Milestone 3: Prove integrated and native Windows behavior

Status: in progress
Acceptance: not met

#### Task T4: Verify the integrated implementation

Prerequisites: accepted Milestone 1 and integrated T3/R1 with their recorded local task proof. Inputs: changed tree, CLI matrix, existing regression suites, and `.github/workflows/ready-ideas-windows.yml`. Own integration verification and minimal workflow adjustments only if the existing native Windows job does not exercise the changed suites. Its local composed proof establishes Milestone 2 acceptance; its native Windows proof establishes Milestone 3 acceptance. Retain command/revision/platform/exit evidence in `docs/conditional-skill-installer/verification.json`; the coordinator owns this ExecPlan.

Historical original local work is complete: [verification.json](verification.json) records all targeted commands at `6f406a1fee1f640106d459c682561af8fedb7c1b`, macOS arm64/PowerShell 7.6.6, exit 0 results, registry/grader counts, inventory, and platform limits. The evidence commit rebased from `a15aef68` to `7fe20edaef6485d1263c9c8f9cad8bd3e3e9c40c`; only README/plan differed from its tested tree before integration, with no source/test changes. Coordinator confirmed task/base tips and cleaned the worktree/branch. The existing `windows-latest` workflow already runs `pwsh -NoProfile -File scripts/test-install.ps1`, so no workflow modification was needed. Native execution is `not_run`: no local Windows host is available, and automatic approval review blocks the requested push pending destination-specific payload approval. Keep this milestone acceptance unmet.

Run the targeted commands below sequentially where fixture mutation could interfere. Obtain native Windows execution of `scripts/test-install.ps1` through the existing workflow or a Windows-capable host. Record the run URL or host, revision, command, result, and any junction-capability limit. A macOS `pwsh` pass or a platform skip cannot satisfy Windows acceptance. Do not dispatch CI or push changes without session authorization for that action.

Stop with acceptance not met if Windows evidence is unavailable. Preserve completed local evidence and state the exact remaining external action. Do not weaken failing tests, synthesize a pass, or treat planned commands as results.

### Milestone 4: Finish documentation and quality checks

Status: in progress
Acceptance: not met

#### Task T5D: Deliver user documentation before external acceptance

Prerequisites: integrated T3 with local CLI task proof. Own only `README.md` installation guidance. Document both invocation forms, flags and exact alias, environment values/precedence, explicit disabling, preserved installed Forest Service skills, empty initial Forest Service content, required categories, and actionable error recovery with exits/streams. Verify against both public `--help` outputs and actual source; do not run a real-home installation. Stop after a scoped documentation commit and whitespace/link checks. This bounded task separates independently deliverable documentation from T5's Windows-dependent closure. The coordinator retains exclusive ownership of the final canonical KB pass.

Completed evidence: `3110cea24bd20221b235b3d941f345bb02c3fc72` changes only `README.md`. Both public help screens were invoked and checked against the documentation, and source diagnostics/exits were cross-checked. Whitespace passed; no new links or em dashes were added. The clean task branch integrated without rebase changes, matching base tip before cleanup. No product tests were invented for the documentation-only change.

#### Task T5: Synchronize documentation and close the effort

Prerequisites: integrated implementation work and tests have finished; native Windows acceptance must be recorded before full completion. Inputs: final diff, current README, CLI help, changed authoring guidance, and admission rules. Own final documentation reconciliation and the single end-of-session KB pass.

Local documentation/quality work is complete. T5D delivered README guidance. The original implementation session's admission pass repaired `.agents/instructions/powershell.md` for ordinal matching and profile isolation. This repair session's final coordinated pass reviewed current guidance and found no warranted KB additions, corrections, splits, or index changes; easily rediscovered code facts and session history were omitted. OKF lint passed. Final T5 closure remains pending T4's native Windows evidence, with no unfinished authorized local documentation.

Document both invocation forms, environment values and precedence, explicit disabling, preservation of previously installed skills, empty initial Forest Service content, and error recovery. After all work and any delegated tasks finish, activate `update-agent-docs` once. Apply knowledge admission, update the smallest relevant canonical documents, and activate `okf-authoring` for canonical semantic edits. Do not create memory solely to record this task. Repair affected indexes and inbound links without editing protected `AGENTS.md` sections.

Review the final diff for lost behavior, incorrect installed paths, ignored fixtures, and unauthorized scope. Record actual outcomes here. Follow repository retention policy when this implementation effort is complete; the current plan remains active while implementation or acceptance is pending.

## Concrete Steps

Next action belongs to the user: explicitly approve publishing `codex/plan-conditional-skill-installer` and its feature, skill, test, and documentation contents to the public `https://github.com/japurcell/skills` repository. Automatic approval review rejected both normal push attempts; no files were published. After approval, the coordinator will push normally, inspect the exact-SHA `ready-ideas-windows.yml` run, explicitly dispatch only if no matching push run starts, retain actual native results, and reconcile Milestones 3/4. Do not bypass the rejection through another upload or indirect execution path.

### Completed repair task graph and ownership

R2/R4/R3 scopes below are retained as completed task specifications. Their verification and integration are recorded in Progress; they are not instructions to restart implementation.

R2 has prerequisite `a5f50664` and owns `scripts/validate-skill-sources.py` plus canonical-collision cases in `scripts/test-install.sh` and `scripts/test-install.ps1`. First reproduce the public overwrite/accepted collision, then reject NFC-normalized casefold aliases before any writes; assert whole-home/external-Codex fingerprints and stage markers. Stop at a tested scoped commit.

R4 independently consumes `a5f50664` and owns the three `skills/default/addy-{code-review-and-quality,performance-optimization,security-and-hardening}/SKILL.md` files and `skills/default/create-skill/SKILL.md`. Verify current missing source targets before repairing only live relative pointers and the benchmark path; preserve installed/runtime and root workspace examples. Validate definitions with vendored YAML and resolve all repaired source targets. No real-home install or live benchmark is required.

R3 requires integrated R2/R4 and owns `scripts/rebase-skill-references.py`, minimal installer copy-boundary changes if needed, and both shared installer fixture suites. Reproduce read-only and dotted-reference failures through both public processes before fixing them. Preserve file/directory modes, source bytes, unrelated installed assets, and root/nested link safety. Handle leading `./` equivalently; verify actual migrated Addy pointers resolve in source and installed copies. Avoid broad text replacements unrelated to reference paths.

R5 completed after integrated R2/R4/R3. It verified all implementation/test inputs match R3's full-suite revision, independently reviewed the repair diff, exercised seven canonical public cases per installer, and ran Addy, registry, RTK, Codex, and four definition validations. All checks exited 0 at `698d5410`; no further required findings. The coordinator retained [repair-verification.json](repair-verification.json) and [repair-dispatch-audit.json](repair-dispatch-audit.json), then completed the no-change final KB pass after delegated work ended. Milestones 1/2 are accepted locally; Milestones 3/4 retain native Windows closure limits.

The original graph was T1 before T2, their integrated proof before T3, integrated T3 and independent R1 before T4, and T3 before T5D. The completed repair graph is independent R2/R4 before serialized R3, then independent R5 proof. Only T4 native execution and final T5 closure remain unfinished; native T4 acceptance precedes that closure. Shared installer ownership was serialized; the coordinator retained exclusive plan/evidence/KB ownership.

Use the repository root as the working directory for every command. Prefix shell commands with RTK; use `rtk proxy` when exact subprocess behavior matters. Keep disposable profile roots in task-specific variables rather than repurposing `$HOME` in the orchestrating shell. Tests establish the child process home themselves.

## Validation and Acceptance

Current repair proof is [repair-verification.json](repair-verification.json): both source-identical full suites, independent public repair cases, affected consumer checks, four definitions, and five-axis review passed. The original T4 targeted checks below are historical results in [verification.json](verification.json); unchanged relocated graders need no duplicate run for these repairs. Native Windows remains unfinished.

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
| Equal, case-only, or canonically equivalent Unicode destination basenames across categories | Exit 1 with both original paths, even when Forest Service is disabled; no writes. |
| Read-only Markdown and directories, first and repeat install | Exit 0; flat references resolve; copied modes, source bytes, and pruning remain correct. |
| Shared references with one or repeated leading `./`, including nested Markdown | Equivalent flat target resolves; unrelated slash-prefixed examples remain unchanged. |
| Actual migrated Addy bundles and create-skill benchmark guidance | All eight source/installed targets and the benchmark source sample resolve. |
| Optional reference directory absent | Pruning still occurs; unresolved source reference text remains unchanged. |
| Read-only installed regular file has multiple hardlinks | Exit 1 before unsafe chmod/copy/rebase; external bytes, inode, and mode remain unchanged. |
| Excluded `archive` or `*-workspace` entries | Not installed; retain existing case-sensitive exclusion semantics. |
| Opted-in install followed by default-only install | Previously installed Forest Service skill remains. |
| Successful installs and repeats | Existing pruning, modes, links, settings preservation, and agents/hooks behavior remain correct; status on stderr. |

On case-insensitive hosts, create case-only collision fixtures in different categories so both source paths can exist. Keep frontmatter identity tests separate from destination-basename collision checks. For immutability cases, fingerprint before invoking the actual entry point; also confirm RTK application, Codex conversion, directory creation, and copy stages were not reached.

### Targeted commands

Completed local verification commands (rerun only after relevant changes or a new failure):

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

### Historical saved-plan acceptance

The earlier planning-only session verified local links and Q1-Q18 obligations, `rtk git diff --check`, and `rtk git status --short`, with only this ExecPlan changed. This historical evidence does not establish implementation acceptance.

## Idempotence and Recovery

The layout migration is a tracked move, not a new import. Inventory current published directories before editing and verify old/new identities to avoid nesting an already-moved bundle. Do not move root workspaces, archives, or other contributors' unrelated changes. If implementation is abandoned, restore only the effort's known moves and edits after reviewing the diff; do not reset the whole worktree.

CLI and source-validation failures must leave installed destinations unchanged. Runtime failures after the write phase begins retain the existing installer's partial-update behavior; this feature does not claim transactionality for the entire multi-provider install. Correct the reported prerequisite or I/O problem and retry with the same selection. Preserve existing backup/configuration safeguards and unrelated files. Do not remove installed Forest Service skills as recovery.

Test cleanup owns only its exact disposable paths. Do not mutate real home directories for proof. If native Windows validation or another external action is unavailable, leave the corresponding milestone open and document the owner, command, and missing evidence inline.

## Interfaces and Dependencies

The public interfaces are the two installer processes, their exact option spellings, `INSTALL_FOREST_SERVICE_SKILLS`, the category source tree, and the existing flat installed destinations. Consumer verification uses Addy's public fixture process, the aggregate runner's CLI, relocated graders, and skill-definition validation. These tests observe process output and filesystem results rather than private parser implementations.

Keep Bash portability consistent with the current supported host shell; do not require newer Bash-only collection syntax without existing support. PowerShell remains `pwsh -NoProfile` compatible and uses its existing link-safe/mode-preserving copy helpers. Python is already an installation dependency; use standard-library facilities if shared validation or reference-path handling requires them. Add no external module or package requirement for option parsing.

## Artifacts and Notes

Current repair proof is [repair-verification.json](repair-verification.json), with actual revisions, commands/results, all five outcomes, independent review, and platform limits. [repair-dispatch-audit.json](repair-dispatch-audit.json) records four repair dispatches, verified outputs, warning mechanisms, and unconfirmed executed settings. Historical initial implementation proof remains in [verification.json](verification.json) and [dispatch-audit.json](dispatch-audit.json). Every implementation branch stayed private and integrated serially; clean task worktrees/branches were removed. Native Windows evidence will be added only when obtained. This user-requested plan remains active for that unmet acceptance; no push occurred.
