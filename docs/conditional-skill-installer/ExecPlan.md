# Install default and opt-in Forest Service skills

This living ExecPlan is saved at `docs/conditional-skill-installer/ExecPlan.md` and follows [exec-plans](../../.agents/skills/exec-plans/SKILL.md). Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current.

## Purpose / Big Picture

Users receive general-purpose skills by default and Forest Service skills only when they select them. Both installers expose the same flags and environment-variable behavior, while continuing to install individual skills into `~/.agents/skills/<name>/`.

The originating requirement is [Conditional Skill Installer](../ideas/archive/1-conditional-skill-installer.md). The user authorized implementation, review repairs, publication to public [japurcell/skills](https://github.com/japurcell/skills), native Windows verification, and result documentation. Branch `codex/plan-conditional-skill-installer` is published. Its first native run exposed a Unicode diagnostic encoding defect; W1 repaired that boundary. [Windows run 38660179633](https://github.com/japurcell/skills/actions/runs/38660179633) passed the complete workflow at `44a47e5b`, including the native installer suite. Follow-up review found three import destinations missed by the migration. R6 repaired that Milestone 1 gap and passed local verification. R6 was published with the explicitly approved cleanup on 2026-10-15. This requested plan retains the requirements and evidence.

The original feature changes skill selection only. On 2026-10-15 the user additionally requested moving benchmark workspaces beside their owning skills and updating every affected document and script. Milestone 8 completed that extension and supersedes the earlier root-workspace decision. Agents, references, RTK configuration, and provider hooks retain their existing installation rules and safety checks. Creating the future `agency-priorities` skill is outside this effort.

Milestone 5 completed the user's subsequent duplication cleanup over fixed `main...HEAD`: all 23 safe candidates are refactored and independently validated locally. The [complete ledger](techdebt-findings.md) records every selected and retained group, commands, input hashes and limits. Cleanup is committed and published as `b1e3704a`. The user explicitly approved its public publication on 2026-10-15; [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419) passed the complete workflow at that exact revision. Milestone 6 acceptance is met; result documentation was committed as `e5c2be20`. Milestone 7 integrates requested main `5f3948c92e5037fb066321e9c9e5b03419410671` locally with passing installer and trusted-launch checks. Publication and fresh native verification of the merge are outside this request.

## Progress

- [x] (2026-10-15) [milestone-8] D0: Verified all ten owners and affected maintained consumers in [workspace discovery](workspace-discovery.md). Commit `f505830e` explicitly renamed prd-to-tasks to spec-to-tasks; preserve the retained legacy workspace basename beside that successor. Corrected the initial discovery draft's mistaken nested destinations before implementation.
- [x] (2026-10-15) [milestone-8] WS1: Moved all ten workspace trees with matching Git tree IDs and 2,477 tracked entries. Original private `1f6e290c` rebased through `eee6854a` to `7078adb6`; [move evidence](workspace-move-evidence.json) retains identities and counts. Initial traversal gap was repaired by WS1R before integration.
- [x] (2026-10-15) [milestone-8] WS1R: Reproduced both nested payload/skill-bundle deletions, then passed two public red/green cycles and the full eight-case cleanup suite. Independent coordinator replay also passes. Original private `8fa91919` rebased without conflicts to `9fd84059` with identical cleanup/test/evidence blobs. [Repair evidence](workspace-cleanup-repair-evidence.md) retains exact results and limits.
- [x] (2026-10-15) [milestone-8] WS2: Repaired live authoring documentation, README, eight grader usage paths, layout recognition and evaluation expectations. The new public create-skill grader suite passes 5 cases; registry passes 14. Original private commit `98d670ec` rebased without conflicts to `509e3f3b`; affected implementation/test blobs are unchanged. [Consumer evidence](workspace-consumer-evidence.md) retains red/green proof. Historical payloads remain untouched.
- [x] (2026-10-15) [milestone-8] WS3: Independent composed verification passed at `00d01d7696d641aa046208f1f7bab99c6ef9c1a2`: all ten trees/2,477 physical entries, cleanup, graders, registry, serial Bash/PowerShell installers, syntax, category inventory, freshness, OKF, links and protected AGENTS checks. [Verification](workspace-verification.md) and [machine-readable proof](workspace-verification.json) retain results and the unsupported macOS junction limit. Evidence commit is `b02d5523`. Coordinator labeled discovery as historical, finished the single canonical-doc admission/OKF pass, and retained the [dispatch audit](workspace-dispatch-audit.json). Only documentation differs from the tested source; final checks confirm implementation/test/workspace blobs remain unchanged. This result is committed locally without publication.
- [x] (2026-10-15) [milestone-7] M1: Resolved four content conflicts, retaining trusted hook-launch preflight and the selection/stream contract. Both incoming evals now live under the default category with exact main bytes. Archived the completed idea and repaired its index and links under main's retention policy.
- [x] (2026-10-15) [milestone-7] M1: Both full installer suites, 26 generator tests, 14 registry tests, 14 agent-converter tests, Codex hook merging and 13 trusted-launch recovery tests passed. Final freshness, OKF, links and whitespace checks passed. The coordinated KB pass warranted no further canonical edits. This merge commit retains the reconciled result locally without publication; native proof remains scoped to `b1e3704a`.
- [x] (2026-10-15) [milestone-6] W3: Pre-publication checks confirmed committed cleanup `b1e3704a`, unchanged six-file local-proof hashes, public `japurcell/skills` destination, ADMIN access and previous remote `ae19dc32`. Automatic review initially rejected the push before execution; the subsequent explicit approval resolved that gate. [Native evidence](techdebt-native-windows-verification.json) retains both events.
- [x] (2026-10-15) [milestone-6] W3: User explicitly approved commits `6ff95ef6` and `b1e3704a`; normal push succeeded to public `japurcell/skills` on `codex/plan-conditional-skill-installer`. [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419) completed successfully at exact SHA `b1e3704a972a2e8840057af43e62cdededd976b4`.
- [x] (2026-10-15) [milestone-6] W3: Recorded native Windows Server 2025 host/image, Python 3.13.15, RTK 0.50.0, exact SHA, all successful steps and the three POSIX-only skips. Native ReadOnly/hard-link and junction cases passed without capability skips. Reconciled plan/ledger/evidence; final documentation and no-change KB admission checks passed. Result documents were committed as `e5c2be20`.
- [x] (2026-10-14) [milestone-5] TD1: Three discovery lanes inspected fixed `main...HEAD` scope `4f2b2f4e..6ff95ef6`. The complete [candidate ledger](techdebt-findings.md) records 23 safe candidates plus intentional, incompatible, ambiguous, and unrelated repetitions, without a result cap.
- [x] (2026-10-14) [milestone-5] TD2: Three scoped workers implemented all 23 safe candidates. Source/test files are frozen; syntax and author preservation audits passed.
- [x] (2026-10-14) [milestone-5] TD2: Independent validators accepted all 23 candidates locally with no weakened assertions or changed case data. All six frozen source/test hashes remained unchanged. Fresh native Windows junction/ReadOnly/profile proof subsequently passed at `b1e3704a` under Milestone 6; general NTFS ACL behavior is outside the fixtures.
- [x] (2026-10-14) [milestone-5] TD3: Serial Bash installer, local PowerShell installer, 15 baseline/current helper cases, and Addy checks passed. Retained the complete ledger and exact input hashes. Syntax, whitespace and OKF checks passed; the final coordinated agent-doc admission warranted no canonical changes. Cleanup subsequently committed as `b1e3704a` and published on 2026-10-15.
- [x] (2026-10-14) [milestone-1] R6: Corrected the caveman, show-me, and lavish import destinations. The local Git import-to-install regression failed with stale installed content before repair; the complete Bash installer suite passed after repair. Syntax, OKF, and whitespace checks passed. Final agent-doc admission found no warranted canonical changes. Published with the approved cleanup on 2026-10-15.
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
- [x] (2026-10-14) [milestone-3] Publish the explicitly approved branch to public `japurcell/skills`; pushed `31d1d799` and confirmed its exact-SHA Windows push run `38658790851`.
- [x] (2026-10-14) [milestone-3] Run native Windows verification at `31d1d799`: workflow `38658790851` failed in the native installer step with `Expected bad source path: nfc-nfd-disabled.`; later workflow tests were skipped. This is failing evidence, not acceptance.
- [x] (2026-10-14) [milestone-3] W1: Paired UTF-8 source-validation boundary integrated as `306daa22` after local full PowerShell, normal/cp1252 diagnostics, and success/failure restoration proof at `19ffb9f2`. Rebase changed only this plan; two PowerShell files changed.
- [x] (2026-10-14) [milestone-3] W2: Native Windows run `38660179633` passed the complete workflow at `44a47e5b`. Original/legacy Unicode diagnostics, Windows ReadOnly attributes, and junction cases passed; only inapplicable POSIX-mode assertions were skipped. Retained failed and successful attempts in `native-windows-verification.json`.
- [x] (2026-10-14) [milestone-4] T5D: Finish user-facing installation documentation; integrated `3110cea24bd20221b235b3d941f345bb02c3fc72`, with both public help outputs and source diagnostics checked.
- [x] (2026-10-14) [milestone-4] Complete the single coordinated agent-doc pass after all delegated work finished; repair PowerShell ordinal-matching/profile guidance, review category-path repairs, verify OKF/links/whitespace, and preserve protected AGENTS sections.
- [x] (2026-10-14) [milestone-4] T5: Native acceptance is established; completed result documentation and final coordinated KB admission pass, with no warranted canonical changes. Retain this requested ExecPlan and native result evidence; no implementation/verification work remains.
- [x] (2026-10-14) [milestone-1] R4: Repaired eight source-reference pointers and the live benchmark path in `e63d4951`. All eight targets resolve; four vendored-YAML definition validations and whitespace checks passed.
- [x] (2026-10-14) [milestone-2] R2: NFC-normalized casefold validation rejects canonical aliases before writes. Both full suites and focused enabled/disabled immutability cases passed; integrated as `a18e778a`.
- [x] (2026-10-14) [milestone-2] R3: Safe read-only rebasing, repeat copying/pruning, dotted references, actual Addy targets, and hardlink refusal/pruning passed both full suites at `671f1e78`; integrated as `362dad54` with only this plan differing after rebase.
- [x] (2026-10-14) [milestone-2] R5: Independent review found no further required findings. Seven focused public cases per installer, affected consumers, four definitions, and source targets passed at `698d5410`. Retained source-identical full-suite proof and repair audit; final coordinated KB pass warranted no changes. No push.

## Surprises & Discoveries

- Milestone 8 integration inspection reproduced a deletion-boundary miss in private WS1 `1f6e290c`: `find -maxdepth 2` also discovered a direct workspace's nested `snapshot-workspace` and a flat skill's nested workspace. A disposable public-CLI replay exited 1 with `FAIL: cleanup deleted iterations inside a workspace payload or skill bundle.` Integration paused until WS1R repaired both cases; the same replay then passed, followed by independent composed cleanup proof. No real benchmark payload was pruned.
- On 2026-10-15, automatic approval review initially rejected publication of this exact cleanup payload. The user then explicitly approved both commits and the public destination; normal push succeeded and native run `38737045419` passed. The rejection is resolved history, not a current blocker. No indirect publication path was used.
- Duplication cleanup found that reference rewriting rejects unsafe hard links before its try block but performs chmod inside it. Sharing chmod with other callers would change exception cleanup. The refactor therefore shares mode calculation/refusal while keeping every caller's chmod and restoration boundary local.
- Follow-up review of `4f2b2f4e..ae19dc32` found three import mappings still targeting root `skills/`. A local Git fixture replayed the declared mappings through the real copy helper and installer: installation succeeded but `caveman/SKILL.md` contained `Stale caveman.` instead of `Refreshed caveman.`. Human-only import orchestration was not executed.
- Adversarial review of `4f2b2f4e..a5f50664` reproduced five omissions after the earlier suites passed: NFC/NFD destination aliases overwrite one leaf on macOS; preserved `0444` Markdown raises `PermissionError` during rebasing; valid leading `./` reference paths remain broken; eight live Addy source pointers still have the old depth; create-skill's live benchmark instruction still uses a nonexistent flat source path. Public Bash/macOS PowerShell reproductions and read-only source resolution establish these findings. Earlier evidence remains historical proof of its tested cases, not acceptance of these repairs.

- The original installers at `4f2b2f4e` enumerated immediate `skills/` entries. Category wrappers would otherwise have been installed as skills named `default` and `forest-service`; current installers enumerate category leaves.
- R3 public fixtures exposed coupled read-only behavior: repeat copying and pruning require writable installed directories, and temporary permission elevation on stale excluded hardlinks changed an outside inode from `0444` to `0644`. Final public and helper tests now preserve outside inode bytes/modes and fail closed before changing read-only shared files. Both local full suites passed; W2 later verified Windows ReadOnly and junction branches.
- Historical publication review rejected two pushes despite verified destination, ADMIN access, and feature base. The user's subsequent explicit payload/destination approval resolved that gate; normal push succeeded. No indirect publication or CI workaround was used.
- Native Windows run `38658790851` at `31d1d799` passed prerequisites, generated-hook freshness, and security-banner tests, then failed the Unicode source-path assertion in `nfc-nfd-disabled`. Controlled cp1252 byte/public-process proof identified producer escaping and consumer replacement; paired UTF-8 now passes exact original-path assertions locally. W2 subsequently established native acceptance at 44a47e5b.
- The current installers preserve destination skills that are no longer selected or present in source. This feature must preserve that behavior. Installation without Forest Service selection is not an uninstall operation.
- Destination mutation starts before skill copying: the installers apply RTK configuration and install Codex agents first. Argument, environment, and category validation must run before these operations, not merely before `copy_skills` or `Copy-Skills`.
- Read-only exploration found 57 root directories with a direct `SKILL.md` and no existing Forest Service skill. The count is a source snapshot, not a hard-coded acceptance value. `docs/ideas/2-agency-priorities-skill.md` names a future Forest Service skill.
- Native PowerShell parameter binding accepts single-hyphen forms but rejects the requested literal `--forest-service` and `--fs` spellings. Explicit argument parsing is required for the agreed interface.
- Historical planning observation: workspace cleanup scanned root-level `skills/*-workspace`. The user's 2026-10-15 change supersedes retaining that layout; Milestone 8 updates the lifecycle consumer together with the moves.
- Source and installed paths have different depths. Runtime examples such as `~/.agents/skills/<name>` and installed reference paths must not receive a category prefix. Addy's `rewrite_references` computes paths relative to its destination, so its deeper default destination requires reference-link verification, not only updated test expectations.
- CLI sources contain advice to display help without arguments. The user explicitly chose the existing no-argument installation behavior. Repository stream rules take precedence over differing warning-stream advice in a source article.
- PowerShell is available on the planning host, but this is macOS. Local PowerShell execution cannot prove native Windows behavior. No installer test suite or native Windows CI was run during planning.

## Decision Log

Sibling workspace decision (2026-10-15): the user explicitly reversed the earlier root-only workspace choice. A published skill at `skills/<category>/<name>/` owns `skills/<category>/<name>-workspace/`; a repo-local skill at `.agents/skills/<name>/` owns `.agents/skills/<name>-workspace/`. Preserve retained iterations, run outputs, snapshots and transcripts byte-for-byte during relocation. Resolve historical skill aliases using source/history before moving them; do not invent a second skill or leave an unexplained root orphan. Keep installed skill destinations flat and workspace entries excluded from installation. The coordinator owns this plan, shared canonical guidance and the single final KB pass; workers own only their assigned implementation/evidence files. No publication or real-home install is authorized by this extension.

Main integration (2026-10-15): preserve main's trusted installed security launches and early Codex configuration check alongside category selection, immutable source preflights, stderr status and cleanup refactors. Incoming skill artifacts follow D1. Finish locally without pushing. The earlier native result remains scoped to `b1e3704a`.

Native cleanup verification (2026-10-15): explicit user approval for commits `6ff95ef6` and `b1e3704a` resolved the public-payload gate. The coordinator performed the normal push to `japurcell/skills`, branch `codex/plan-conditional-skill-installer`. Run acceptance requires the exact approved SHA and complete workflow results; prior native passes remain historical.

Cleanup decision (2026-10-14): process all 23 safe candidates in substantively changed units, including inherited repetition within those units. Keep incompatible cross-script algorithms, independent test oracles, literal case matrices, and pure-move bodies separate. Use private same-module helpers and existing cleanup/interpreter helpers; preserve public interfaces and caller-specific failure boundaries. The [complete ledger](techdebt-findings.md) records every selected and retained group.

The user selected or confirmed the public contract on 2026-10-14 and authorized all five review repairs. The dated repair details below resolve implementation choices within that scope. These decisions define the current contract; acceptance evidence is recorded separately.

### D1: Repository and installed layout

Published skills now live under `skills/default/<name>/`. `skills/forest-service/` contains `.gitkeep` while it has no published skills. Keep any repository-level `skills/archive/` separate from published categories. Under the user's revised contract, each generated `<name>-workspace/` is a sibling of its owning skill, including category-specific published skills and repo-local `.agents/skills/` owners. Milestone 8 migrates the existing root workspaces and their consumers; the earlier root-only decision is historical. Install selected leaf directories into `~/.agents/skills/<name>/`, never into a category wrapper, and never install workspace artifacts.

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

Native diagnostic repair decision (2026-10-14): pair UTF-8 producer and consumer encodings only around PowerShell's Python source-validator invocation, restoring previous settings in `finally`. Controlled cp1252 public-process reproduction showed NFC bytes decoded as replacement characters and NFD accents escaped as literal `\u0301`; UTF-8 preserves both original spellings. Keep the exact path assertions and test the legacy-encoding case on every host. Local proof is not native acceptance.

Preserve existing copying, link handling, executable modes, and installed pruning of `evals/`, `README.md`, `LICENSE.txt`, and `LICENSE.md`. Preserve previously installed Forest Service and unrelated skills. Do not add stale-skill deletion or a legacy root-level installation fallback.

### D4: CLI output and failure behavior

Help and examples go to stdout. Installer status, progress, warnings, and errors go to stderr. Success/help use exit 0; invalid arguments or a consulted invalid environment value use exit 2; category/source and installation failures use exit 1. Apply this classification to the installer entry points, including translating helper failures into an installer failure while preserving their diagnostic and recovery text.

Help must work without valid sources or installer dependencies. Diagnostics identify the bad option, variable, missing source, or conflicting paths and explain the correction. Existing generated-hook stale-output advice must still name the exact recovery command. Do not add dry-run, version, JSON, completion, decorative output, or new interactive flows.

## Outcomes & Retrospective

Milestone 8 is complete. All ten workspaces are siblings of their owners, including the local OKF workspace and the retained legacy PRD workspace beside spec-to-tasks. All 2,477 tracked payload entries retain their bytes and Git modes; old physical root workspace directories are gone. Cleanup now supports category/local siblings and protects workspace payloads and skill bundles. Live authoring guidance, eight grader usage paths, layout recognition, public tests, registry, README and canonical guidance are synchronized. Independent composed proof passed on macOS, including both serial installer suites. Discovery is explicitly historical; final admission added no memory, split or index changes. The branch remains local and unpushed; native Windows/provider delivery are outside this extension's proof.

Main integration combines feature `e5c2be20` and main `5f3948c9`. Four content conflicts and two incoming eval locations are reconciled. Full Bash and macOS PowerShell installer suites, generator, registry, Codex merge, agent-converter and trusted-launch recovery checks pass. The completed idea is archived under main's retention policy, and an incoming trailing blank line was removed to satisfy whitespace checks. Existing native acceptance establishes the premerge cleanup only. The merged branch is local and has not been pushed.

The 2026-10-15 publication gate was resolved by explicit user approval. Cleanup `b1e3704a` is published and [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419) passed the complete workflow on that exact revision. Windows Server 2025 exercised the ReadOnly hard-link, junction, profile and Unicode fixtures; only POSIX-specific checks skipped. Milestone 6 acceptance is met. [Native evidence](techdebt-native-windows-verification.json) retains actual step outcomes, host, times, versions and limits. Result documentation was committed as `e5c2be20`; the subsequent merge requires Milestone 7 integration proof.

The implementation, five earlier review repairs, native encoding repair, and follow-up importer repair are complete. W2's Windows workflow passed at `44a47e5b`, including Unicode diagnostics, ReadOnly attributes, and junction cases. [Local repair proof](repair-verification.json) and [native proof](native-windows-verification.json) retain those revisions and limits. R6 subsequently corrected three import destinations and added a regression through the real copy helper and Bash installer; the complete local suite passed. R6 changed only the Bash importer, its Bash regression, and this plan; that repair used local proof. W3 now verifies the composed cleanup revision on native Windows. Earlier native evidence remains scoped to its recorded revision. Milestones 0-4 are accepted; R6 was published on 2026-10-15. The final coordinated agent-doc pass found no warranted canonical changes; OKF lint passed. Milestone 5's duplication cleanup is complete locally: all 23 selected candidates and affected suites passed independent validation. Its committed changes at `b1e3704a` are published; Milestone 6 records the passing native Windows proof separately from earlier feature acceptance. General NTFS ACL behavior is outside the fixture proof.

## Context and Orientation

Work from `/Users/adam/.codex/worktrees/d238/skills`. `scripts/install.sh` owns Bash copying through `copy_skills`; `scripts/install.ps1` owns PowerShell copying through `Copy-Skills` and the link-safe `Copy-Entry` helpers. Both now implement the agreed raw argument interface, environment resolution, and shared `scripts/validate-skill-sources.py` inventory check before destination mutation. Existing RTK, generated-hook, and provider configuration preflights remain before writes. PowerShell uses ordinal comparisons for literal external strings and isolates Windows profile variables in disposable test children.

`scripts/test-install.sh` and `scripts/test-install.ps1` build disposable repositories and homes. Their skill fixtures use `skills/default/alpha`, with an empty Forest Service category. PowerShell's `Invoke-InstallProcess` supplies the child-process boundary, argument forwarding, and home/environment isolation. The source-validator invocation pairs UTF-8 producer/consumer encodings and restores prior settings. These suites also cover provider settings, Codex agent conversion, modes, links, and malformed-input immutability; retain that coverage.

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

R6 closed the three missed import destinations: `caveman`, `show-me`, and `lavish` now target `skills/default`. The new local Git import-to-install regression and complete Bash installer suite passed on the repaired tree. Syntax, OKF, and whitespace checks also passed.

#### Task R6: Complete third-party import destinations

Prerequisite: follow-up review of `4f2b2f4e..ae19dc32` and the user's instruction to fix all findings. Inputs: D1, the three destination mappings in `scripts/import-skill-repos.sh`, and the existing public Bash installer fixture seam. Correct only those destination arguments and add `test_refreshed_imports_install_from_default_category` to `scripts/test-install.sh`.

Completed evidence (2026-10-14): the test reads declarations as data, substitutes a local Git origin, runs the real `copy-from-git.sh`, and invokes the real fixture installer against a disposable home. Before repair, the suite exited 1 because installed caveman content was `Stale caveman.`. After repair, `rtk proxy bash scripts/test-install.sh` exited 0, checking refreshed content for all three skills and absence of uncategorized copies. `rtk proxy bash -n scripts/import-skill-repos.sh scripts/test-install.sh`, `rtk proxy python3 scripts/lint-okf.py`, and `rtk proxy git diff --check` exited 0. No human-only import orchestration, external fetch, or real-home installation ran. Stop at this locally verified repair; no push was performed.

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

Status: done
Acceptance: met

[Windows run 38660179633](https://github.com/japurcell/skills/actions/runs/38660179633) passed on exact pushed revision `44a47e5bd758966a6d7e37d9e8ad2b9f834eaba9`. The host was Microsoft Windows Server 2025 (`windows-latest`, image `windows-2025-vs2026`), Python 3.13.15, and RTK 0.50.0. The native installer command exited 0 with `test-install.ps1: all tests passed.` Windows ReadOnly and junction cases ran without a capability skip; POSIX-only mode and unreadable000 assertions were intentionally skipped. All downstream scanner, RTK, OKF, and lifecycle checks also passed. Actual revisions, timings, steps, failed attempt, and limits are retained in [native-windows-verification.json](native-windows-verification.json).

#### Task T4: Verify the integrated implementation

Prerequisites: accepted Milestone 1 and integrated T3/R1 with their recorded local task proof. Inputs: changed tree, CLI matrix, existing regression suites, and `.github/workflows/ready-ideas-windows.yml`. Own integration verification and minimal workflow adjustments only if the existing native Windows job does not exercise the changed suites. Its local composed proof establishes Milestone 2 acceptance; its native Windows proof establishes Milestone 3 acceptance. Retain command/revision/platform/exit evidence in `docs/conditional-skill-installer/verification.json`; the coordinator owns this ExecPlan.

Historical original local work is complete: [verification.json](verification.json) records all targeted commands at `6f406a1fee1f640106d459c682561af8fedb7c1b`, macOS arm64/PowerShell 7.6.6, exit 0 results, registry/grader counts, inventory, and platform limits. The evidence commit rebased from `a15aef68` to `7fe20edaef6485d1263c9c8f9cad8bd3e3e9c40c`; only README/plan differed from its tested tree before integration, with no source/test changes. Coordinator confirmed task/base tips and cleaned the worktree/branch. The existing `windows-latest` workflow already runs `pwsh -NoProfile -File scripts/test-install.ps1`, so no workflow modification was needed. Native CI ran at 31d1d799 and failed its Unicode source-path diagnostic assertion. W1 fixed that boundary; W2 subsequently passed the full native workflow at 44a47e5b. Milestone acceptance is now met.

Run the targeted commands below sequentially where fixture mutation could interfere. Obtain native Windows execution of `scripts/test-install.ps1` through the existing workflow or a Windows-capable host. Record the run URL or host, revision, command, result, and any junction-capability limit. A macOS `pwsh` pass or a platform skip cannot satisfy Windows acceptance. Do not dispatch CI or push changes without session authorization for that action.

Stop with acceptance not met if Windows evidence is unavailable. Preserve completed local evidence and state the exact remaining external action. Do not weaken failing tests, synthesize a pass, or treat planned commands as results.

### Milestone 4: Finish documentation and quality checks

Status: done
Acceptance: met

#### Task T5D: Deliver user documentation before external acceptance

Prerequisites: integrated T3 with local CLI task proof. Own only `README.md` installation guidance. Document both invocation forms, flags and exact alias, environment values/precedence, explicit disabling, preserved installed Forest Service skills, empty initial Forest Service content, required categories, and actionable error recovery with exits/streams. Verify against both public `--help` outputs and actual source; do not run a real-home installation. Stop after a scoped documentation commit and whitespace/link checks. This bounded task separates independently deliverable documentation from T5's Windows-dependent closure. The coordinator retains exclusive ownership of the final canonical KB pass.

Completed evidence: `3110cea24bd20221b235b3d941f345bb02c3fc72` changes only `README.md`. Both public help screens were invoked and checked against the documentation, and source diagnostics/exits were cross-checked. Whitespace passed; no new links or em dashes were added. The clean task branch integrated without rebase changes, matching base tip before cleanup. No product tests were invented for the documentation-only change.

#### Task T5: Synchronize documentation and close the effort

Prerequisites: integrated implementation work and tests have finished; native Windows acceptance must be recorded before full completion. Inputs: final diff, current README, CLI help, changed authoring guidance, and admission rules. Own final documentation reconciliation and the single end-of-session KB pass.

Local documentation/quality work is complete. T5D delivered README guidance. The original implementation session's admission pass repaired `.agents/instructions/powershell.md` for ordinal matching and profile isolation. This repair session's final coordinated pass reviewed current guidance and found no warranted KB additions, corrections, splits, or index changes; easily rediscovered code facts and session history were omitted. OKF lint passed. Native W2 proof is accepted; final T5 reconciliation is complete, including this session's coordinated no-change KB pass.

Completed local T5 scope: document both invocation forms, environment values and precedence, explicit disabling, preservation of previously installed skills, empty initial Forest Service content, and error recovery. The final coordinated `update-agent-docs` pass applied knowledge admission after all work finished; no canonical changes were warranted. Protected `AGENTS.md` sections, immutable sources, and indexes remain intact.

Review the final diff for lost behavior, incorrect installed paths, ignored fixtures, and unauthorized scope. Record actual outcomes here. Follow repository retention policy when this implementation effort is complete; retain this user-requested plan as a completed result record.

### Milestone 5: Remove safe duplication from the feature changes

Status: done
Acceptance: met

The user requested `techdebt` over `main...HEAD`, without a finding cap, and authorized fixing all findings. The fixed review range is merge base `4f2b2f4efb8823683ceb046b51248f0dc0f27f37` through `6ff95ef643506332e6ff9f68ae30cf0c11cd089b`; local `main` resolves to `7182b156`. Preserve the D1-D4 contract and every test assertion. Pure file moves do not justify unrelated refactors of unchanged bodies. Classify intentional or unsafe repetition explicitly rather than forcing new abstractions.

TD1 has no prerequisites and uses the exact range plus nearby helpers relevant to changed units. Three independent discovery lanes cover production helpers, Bash tests, and PowerShell tests plus maintained consumers. The coordinator owns this plan and the complete candidate ledger. Discovery is read-only.

TD2 requires the candidate ledger. PROD-01 through PROD-06 belong to the production worker (`scripts/rebase-skill-references.py`, `scripts/install.sh`, `scripts/install.ps1`); BT-01 through BT-13 belong to the Bash-test worker (`scripts/test-install.sh`, `scripts/test-addy-install.sh`); PSC-001 through PSC-004 belong to the PowerShell-test worker (`scripts/test-install.ps1`). An independent validator checks every candidate in each ownership group. Shared-file edits and tests that mutate fixtures must be serialized. Require the applicable TDD and area instructions; preserve approved process/CLI seams. Public interface changes, architectural choices, broad naming changes, and unrelated refactors require a user decision rather than automatic implementation.

TD3 requires all candidate work and validation to finish. Verify the composed tree with the affected suites, syntax/whitespace checks, and knowledge admission. Record exact commands, actual outcomes, retained candidates, and platform limits in `docs/conditional-skill-installer/techdebt-findings.md`. Existing native Windows proof remains scoped to `44a47e5b`; a local PowerShell pass cannot establish fresh native acceptance.

Completed local evidence: all 23 candidates passed independent source/test preservation audits. `rtk proxy bash scripts/test-install.sh`, `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1`, the 15-case baseline/current public-helper harness, and the full Addy suite all exited 0 in serial execution. Both Bash test files parse under macOS Bash 3.2.57; production Python/PowerShell and embedded fixture scripts parse. Every original assertion/case/dispatch remains; the six source/test hashes were unchanged throughout verification. Whitespace and OKF checks passed, and the final KB admission pass made no canonical changes. The complete ledger retains details and all rejected/retained candidates.

Milestone 5 established local cleanup acceptance; Milestone 6 subsequently passed native Windows verification at published `b1e3704a`. Native ReadOnly/hard-link and junction cases ran without capability skips. The three Windows skips are intentionally inapplicable POSIX mode/executable/unreadable000 assertions, which retain local proof. No test or implementation changes were required after native execution.

### Milestone 6: Verify the committed cleanup on native Windows

Status: done
Acceptance: met

W3 completed after local Milestone 5 proof and the user's explicit 2026-10-15 approval to publish commits `6ff95ef6` and `b1e3704a`. Normal push succeeded to the approved public repository/branch, and the coordinator inspected the exact-SHA workflow and logs. Published target `b1e3704a972a2e8840057af43e62cdededd976b4` retains all six source/test hashes from local proof. Result documentation was committed as `e5c2be20` before main integration.

[Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419) completed `.github/workflows/ready-ideas-windows.yml` with conclusion `success`. Job `116428884885` ran on Microsoft Windows Server 2025 (`windows-latest`, image `windows-2025-vs2026`, version `20260925.250.1`) from `2026-10-15T12:45:12Z` to `2026-10-15T12:49:04Z` (232 seconds). The native command `pwsh -NoProfile -File scripts/test-install.ps1` ran from `12:45:44Z` to `12:47:48Z` and reported `test-install.ps1: all tests passed.` Python was 3.13.15 and RTK was 0.50.0; the PowerShell patch version was not printed.

Every workflow step succeeded: prerequisites, generated hooks, security banners, native installer, Codex scanner Windows envelopes, generated scanner capture, stable RTK configuration, repository OKF hooks and lifecycle messages. ReadOnly hard-link/inode safety and junction preservation/external-target immutability fixtures passed. The only native installer skips concerned POSIX directory/file modes plus unreadable000 failure assertions, executable bits, and Unix file modes. These skips do not establish general NTFS ACL behavior. [Native evidence](techdebt-native-windows-verification.json) records full step timings, exact input and publication history.

### Milestone 7: Integrate main without losing installer behavior

Status: done
Acceptance: met

M1 depends on committed feature `e5c2be20` and fetched main `5f3948c92e5037fb066321e9c9e5b03419410671`. Resolve `scripts/install.sh`, `scripts/install.ps1`, `scripts/test-install.sh`, and `scripts/test_test_all.py` by preserving both intents. Move incoming eval JSON files into their existing `skills/default/` bundles. Reconcile the new ideas index with the completed feature. Preserve incoming historical hook evidence rather than dropping it to satisfy a scanner size budget.

Completed verification: Bash and PowerShell syntax, generated freshness and generator tests, both complete installer fixture suites, aggregate-runner registry tests, and trusted registration/converter/recovery suites pass. Installer and generator fixture mutations ran serially. No unresolved Git entries remain. The local merge commit includes this outcome record; no push was performed. Native Windows is not available locally; no fresh native or provider-delivery claim is made. The known skill-validator incompatibility below remains distinct from passing integration checks.

### Milestone 8: Keep workspaces beside their owning skills

Status: done
Acceptance: met

The starting base was `c8d36350`, including the locally completed main merge and retained hook incident report. At that base, published skills were under `skills/default/`, while ten benchmark workspace trees remained at root `skills/`. D0 established the following exact mapping in the retained [pre-migration discovery](workspace-discovery.md). No untracked or ignored files were found under the ten source workspace trees before migration. All listed moves are now complete.

| Source directory | Destination directory |
| --- | --- |
| `skills/architecture-design-contest-workspace/` | `skills/default/architecture-design-contest-workspace/` |
| `skills/code-review-workspace/` | `skills/default/code-review-workspace/` |
| `skills/commit-workspace/` | `skills/default/commit-workspace/` |
| `skills/create-skill-workspace/` | `skills/default/create-skill-workspace/` |
| `skills/handoff-workspace/` | `skills/default/handoff-workspace/` |
| `skills/official-sources-workspace/` | `skills/default/official-sources-workspace/` |
| `skills/okf-authoring-workspace/` | `.agents/skills/okf-authoring-workspace/` |
| `skills/prd-to-tasks-workspace/` | `skills/default/prd-to-tasks-workspace/` |
| `skills/self-improve-workspace/` | `skills/default/self-improve-workspace/` |
| `skills/techdebt-workspace/` | `skills/default/techdebt-workspace/` |

The legacy `prd-to-tasks-workspace` is retained history owned by successor `skills/default/spec-to-tasks/`, as established by rename commit `f505830e`. Its basename remains unchanged; future runs use the canonical sibling `skills/default/spec-to-tasks-workspace/`. All destinations are siblings of owners, never children inside skill bundles.

Completed WS1 scope: it depended on D0 and owned all mapped physical moves, the cleanup CLI/suite and [move evidence](workspace-move-evidence.json). The ten directory trees retain their original contents. Cleanup now discovers bounded category/local siblings and confines an explicit `CLEANUP_SKILLS_ROOT` to that root; an explicitly empty override fails. The original category discovery failure and empty-root failure were demonstrated before their fixes. The initial depth-only safety gap required WS1R below; no real benchmark cleanup was run.

Completed WS2 scope, retained for context: it depended on D0 and owned maintained `skills/default/` authoring guidance, grader usage/help and actual workspace-layout recognition, evaluation expectations/fixtures, plus README workspace examples. It also registered the new public grader suite in `scripts/test-all.py` and `scripts/test_test_all.py`. Scope excluded all `*-workspace/` payloads, immutable sources and historical research/evidence. Examples now show category/default and repo-local owner-relative siblings. Public-process red/green proof covers changed layout recognition; historical grading scores were not rewritten. Commit `509e3f3b` is the rebased consumer implementation; [consumer evidence](workspace-consumer-evidence.md) retains commands and results.

Completed WS1R scope: it consumed WS1 and the coordinator's failing public-CLI replay in a fresh private worktree. Two red/green cycles now establish traversal stops at workspace payloads and real skill bundles. Archives, category/default/Forest Service/local cleanup, literal names, snapshot retention, symlinks and override isolation remain covered by the eight-case suite. The original failing versions remain attributable in [repair evidence](workspace-cleanup-repair-evidence.md). Final cleanup source/test proof applies to rebased `9fd84059`; all ten move trees remain unchanged.

Completed WS3 consumed integrated WS1/WS1R/WS2 and canonical guidance. It independently checked exact tree/blob/mode/symlink preservation, absent old roots, cleanup boundaries and isolation, grader examples, registry and workspace exclusion. `rtk proxy bash scripts/test-cleanup-skill-workspaces.sh` passed eight cases, the new public create-skill grader suite passed five, and `rtk proxy python3 scripts/test_test_all.py` passed fourteen. Existing spec-to-tasks, loop, handoff and ExecPlan grader suites passed 38, 13, 20 and 35 tests. `rtk proxy bash scripts/test-install.sh` and `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1` passed serially in disposable profiles. Syntax, eight usage checks, definition/eval JSON, actual category inventory, generated freshness, OKF, 72 local links, whitespace and unchanged protected AGENTS checks passed. [Verification evidence](workspace-verification.json) records exact commands, fingerprints, exits, decisive outputs and platform limits at `00d01d76`. Its Bash wrapper initially expected an undocumented success message; actual exit 0 was retained and correctly interpreted without changing or rerunning the suite. The only product-test skip was unsupported junction creation on macOS; no native Windows claim is made. Coordinator subsequently labeled the discovery snapshot, added the new grader test route, and verified final documentation without changing the tested implementation or workspace blobs. All required local acceptance is met; no push or real-home installation occurred.

Every implementation task uses a fresh private worktree and branch under `codex/`. Rebase and fast-forward them into the base branch one at a time, rechecking evidence after conflicts or changed interactions. The coordinator retains plan/canonical-doc ownership and performs one final knowledge-admission pass after all tasks finish. Retain evidence-backed corrections and update recursive workspace ignore guidance, preserving protected AGENTS sections and operational source-ingestion state.

## Concrete Steps

No implementation or verification work remains for Milestone 8. Consumer implementation is `509e3f3b`, moves are `7078adb6`, cleanup repair is `9fd84059`, and composed source proof is pinned to `00d01d76` with evidence commit `b02d5523`. Final documentation preserves those implementation/test/workspace blobs. All task branches were private and integrated locally. The approved published code remains `b1e3704a`; the user owns any next publication or fresh native-verification request. Do not publish this extension or run real-home installation without a new request.

Retain this requested plan and native JSON as outcome records. Main changes installer and hook inputs; fresh local integration checks passed under Milestone 7. Historical W2 proof stays scoped to `44a47e5b`; cleanup native acceptance uses `b1e3704a` and does not establish merged native behavior.

### Completed native repair tasks

W1/W2 scopes below are retained as completed task specifications. W1 integrated at `306daa22`; W2 passed at pushed `44a47e5b`. They are not instructions to restart implementation or CI.

W1 depends on the failing native run at `31d1d799`. It owns only `scripts/install.ps1`, `scripts/validate-skill-sources.py` if producer changes are needed, and narrow diagnostic regression cases in `scripts/test-install.ps1`. Diagnose actual diagnostic bytes before changing code; use a deterministic local public-process reproduction where possible, and retain an assertion containing actual stderr for future failures. Preserve both original NFC/NFD paths, both category selections, whole-home/Codex immutability, and status/error stream contracts. Do not weaken the original path assertion or skip Windows cases. Stop at a locally tested scoped commit. The coordinator owns this plan and all canonical KB/evidence.

W2 depends on integrated W1 and owns native CI execution/evidence. Push normally under the user's explicit public-destination approval, run the existing Windows workflow, and inspect all results. A later failure reopens its owning bounded repair rather than establishing acceptance. No real-home local installation, live model evaluation, or human-only import orchestration is authorized.

### Completed repair task graph and ownership

R2/R4/R3 scopes below are retained as completed task specifications. Their verification and integration are recorded in Progress; they are not instructions to restart implementation.

R2 has prerequisite `a5f50664` and owns `scripts/validate-skill-sources.py` plus canonical-collision cases in `scripts/test-install.sh` and `scripts/test-install.ps1`. First reproduce the public overwrite/accepted collision, then reject NFC-normalized casefold aliases before any writes; assert whole-home/external-Codex fingerprints and stage markers. Stop at a tested scoped commit.

R4 independently consumes `a5f50664` and owns the three `skills/default/addy-{code-review-and-quality,performance-optimization,security-and-hardening}/SKILL.md` files and `skills/default/create-skill/SKILL.md`. Verify current missing source targets before repairing only live relative pointers and the benchmark path; preserve installed/runtime and root workspace examples. Validate definitions with vendored YAML and resolve all repaired source targets. No real-home install or live benchmark is required.

R3 requires integrated R2/R4 and owns `scripts/rebase-skill-references.py`, minimal installer copy-boundary changes if needed, and both shared installer fixture suites. Reproduce read-only and dotted-reference failures through both public processes before fixing them. Preserve file/directory modes, source bytes, unrelated installed assets, and root/nested link safety. Handle leading `./` equivalently; verify actual migrated Addy pointers resolve in source and installed copies. Avoid broad text replacements unrelated to reference paths.

R5 completed after integrated R2/R4/R3. It verified all implementation/test inputs match R3's full-suite revision, independently reviewed the repair diff, exercised seven canonical public cases per installer, and ran Addy, registry, RTK, Codex, and four definition validations. All checks exited 0 at `698d5410`; no further required findings. The coordinator retained [repair-verification.json](repair-verification.json) and [repair-dispatch-audit.json](repair-dispatch-audit.json), then completed the no-change final KB pass after delegated work ended. Milestones 1/2 were accepted locally; W2 has now established native acceptance and completed Milestones 3/4.

The original graph was T1 before T2, their integrated proof before T3, integrated T3 and independent R1 before T4, and T3 before T5D. The completed repair graph is independent R2/R4 before serialized R3, then independent R5 proof. W1 repaired the native encoding failure; W2 supplied passing native T4 proof and T5 closure. All graph nodes are complete. Shared installer ownership was serialized; the coordinator retained exclusive plan/evidence/KB ownership.

Use the repository root as the working directory for every command. Prefix shell commands with RTK; use `rtk proxy` when exact subprocess behavior matters. Keep disposable profile roots in task-specific variables rather than repurposing `$HOME` in the orchestrating shell. Tests establish the child process home themselves.

## Validation and Acceptance

Milestone 8 acceptance is met locally. All ten move identities and all 2,477 physical entries match their original Git blobs/modes; source directories and root workspaces are absent. Independent source checks and both full installer suites passed at `00d01d76`, as retained in [workspace verification](workspace-verification.md) and [JSON proof](workspace-verification.json). WS1R's two public reproductions, eight-case cleanup suite and the coordinator's original replay all pass. WS2's five public grader cases, fourteen registry tests, eight usage checks and validation also pass. Conflict-free rebases preserved relevant source/test/evidence blobs. The coordinator resolved the discovery-label finding, completed the single agent-doc admission/OKF pass, and rechecked final links, whitespace, artifacts and unchanged source inputs. No further memory, split, deduplication, index or protected-section change was warranted. Prior failures remain attributed; native Windows proof is scoped to older revisions below. The verification record's remaining-coordinator section describes its frozen checkpoint before these final documentation corrections, not an outstanding owner action.

Milestone 7 local verification passed on the integrated tree. Before resolution, `bash -n scripts/install.sh` failed at the conflict marker and `python3 scripts/test_test_all.py` failed with `SyntaxError`. After resolution, Bash and PowerShell syntax, all 26 generator tests, generated freshness (38 files), both full installer suites, all 14 registry tests, the Codex hook merge suite and all 14 agent-converter tests passed. `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py` passed all 13 tests in 54.662 seconds, including actual installed commands, startup/PATH injection and enforcement/recovery controls. Full local PowerShell reported `test-install.ps1: all tests passed.` with only the host's unsupported-junction skip. Native Windows junction behavior is not established for this merge.

Source-category validation passed; both relocated eval JSON files parse and match main byte-for-byte. The delegate and router definitions pass quick validation. The execplan-implement definition retains required `disable-model-invocation: true`; quick validation rejects that unchanged key, matching the documented [validator limitation](../../.agents/memory/known-issues/skills.md#invocation-controls-and-validation). That result is not a pass and no invocation control or validation rule was weakened. Final OKF lint, changed-document link checks, whitespace checks and generated freshness passed. The single final `update-agent-docs` admission pass found no new durable knowledge beyond existing guidance and retained feature evidence, so no further canonical edits were warranted.

The session scanner rejected the pending index at 8,403,665 bytes against its 8,388,608-byte limit; the user reported disabling the hook outside this chat and instructed continuation. No repository hook setting was changed to bypass that gate. The blocked scan does not establish a clean secret scan.

Current cleanup-native status is `success` at published `b1e3704a`. [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419) passed every workflow step, including the complete native installer suite, ReadOnly hard-link and junction cases. [Native evidence](techdebt-native-windows-verification.json) records actual host/image, versions, times, skips, exact input and publication history. Fresh cleanup-native acceptance is met.

Historical installer acceptance combined initial local repair proof in [repair-verification.json](repair-verification.json) with W1's local encoding checks and W2's native pass in [native-windows-verification.json](native-windows-verification.json). The native test revision is `44a47e5b`. R6 later changes only import destinations and a Bash regression; its red/green and complete local suite proof are recorded under Task R6. No PowerShell or installer implementation changed in R6, and no new native run was performed. Original T4 checks in [verification.json](verification.json) remain historical; unchanged relocated graders need no duplicate run.

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

The layout migration is a tracked move, not a new import. Inventory source/destination identities before editing to avoid nesting an already-moved bundle. Milestone 8 explicitly authorizes the mapped root workspace moves beside their owners. Preserve archived skill bundles and unrelated changes. Record source tree identities before each move; refuse an existing destination rather than merging or overwriting it. Recover a failed move from its verified source/destination state and retained manifest, restoring only this effort's known moves and edits after reviewing the diff; do not reset the whole worktree.

CLI and source-validation failures must leave installed destinations unchanged. Runtime failures after the write phase begins retain the existing installer's partial-update behavior; this feature does not claim transactionality for the entire multi-provider install. Correct the reported prerequisite or I/O problem and retry with the same selection. Preserve existing backup/configuration safeguards and unrelated files. Do not remove installed Forest Service skills as recovery.

Test cleanup owns only its exact disposable paths. Do not mutate real home directories for proof. If native Windows validation or another external action is unavailable, leave the corresponding milestone open and document the owner, command, and missing evidence inline.

## Interfaces and Dependencies

The public interfaces are the two installer processes, their exact option spellings, `INSTALL_FOREST_SERVICE_SKILLS`, the category source tree, and the existing flat installed destinations. Consumer verification uses Addy's public fixture process, the aggregate runner's CLI, relocated graders, and skill-definition validation. These tests observe process output and filesystem results rather than private parser implementations.

Keep Bash portability consistent with the current supported host shell; do not require newer Bash-only collection syntax without existing support. PowerShell remains `pwsh -NoProfile` compatible and uses its existing link-safe/mode-preserving copy helpers. Python is already an installation dependency; use standard-library facilities if shared validation or reference-path handling requires them. Add no external module or package requirement for option parsing.

## Artifacts and Notes

Current cleanup-native evidence is [techdebt-native-windows-verification.json](techdebt-native-windows-verification.json), recording published `b1e3704a` and successful [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419). The earlier automatic-review rejection is retained as resolved history. Historical native evidence below remains scoped to its original revisions.

Earlier native proof is [native-windows-verification.json](native-windows-verification.json): both attempts, W1's encoding repair/local proof, actual native revision/host/times/step results, capability limits, and its dispatch audit. Initial local repair proof remains in [repair-verification.json](repair-verification.json) and [repair-dispatch-audit.json](repair-dispatch-audit.json); historical initial implementation proof remains in [verification.json](verification.json) and [dispatch-audit.json](dispatch-audit.json). Worker branches stayed private until serial integration and cleanup; the explicitly approved base branch is published. This user-requested plan is retained as the feature outcome record; Milestones 0-4 retain their recorded acceptance, and Milestone 5 has local cleanup acceptance. The complete [duplication ledger](techdebt-findings.md) records new source/test hashes, commands, retained groups, and the passing current-revision native Windows proof under Milestone 6.
