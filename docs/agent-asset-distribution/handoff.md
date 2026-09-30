# Agent Asset Distribution Handoff

## Status

All eight planning tickets are closed. Milestones 1 and 2 are integrated. Milestone 3 is unfinished in `/private/tmp/agent-assets-m3` on private `codex/agent-assets-m3`; it has uncommitted source/test/doc work and required review repairs. Active implementer `/root/installer_m3` and replacement reviewer `/root/installer_m3_recheck` are interrupted while answering the user's direct prerequisite question, under the standing answer-and-stop instruction. Implementation authorization remains established, but no further work or installation occurs this turn. Milestones 4 through 7 remain open. Base branch: `codex/research-agent-distribution-options`.

## Next step

On an explicit resume, reactivate the original milestone 3 implementer for repairs and replacement reviewer for its original review. Preserve their worktree; do not replace or discard uncommitted work. Repair (1) pruning authority from forged valid in-root lock items and (2) regular-directory movement during staged replacement leaving visible content inconsistent with the lock. Rerun affected public cases and final suite, complete independent review/doc pass, then commit and serialize integration. Windows mutations currently fail closed until safe native support is added in milestone 6. Use the [ExecPlan](../agent-asset-installer/ExecPlan.md). Milestone 2 tip is `c0351a9a5daecb5f797baa1a0b6c794fbe2941c8`; earlier clean node worktrees/branches are removed.

## Important boundaries

- The user explicitly excluded a rollback feature. Restoring the currently recorded immutable revision is supported; a rollback command or retained installation history is not part of the contract.
- Keep this effort and its cited findings under `docs/agent-asset-distribution/`, as the user requested. Use [the map](map.md) as the closed decision index, [the recommendation](recommendation.md) for comparative evidence, and [the source inventory](local-inventory.md) for current code constraints.
- The user authorized the grilling/research fallback without the unavailable `domain-modeling` skill on 2026-09-29. Do not ask for that authorization again. Missing workflow dependencies still need explicit handling in the future distribution catalog.
- The later explicit implementation request lifts the earlier hold. Native publication and real-home mutations have not been requested.

## Implementation constraints and durable learnings

- The plan chooses one Python 3.11+ lifecycle engine with shell/PowerShell compatibility entry points. It covers catalog/dependencies, immutable provenance, owned files/configuration, branch updates and recorded restoration, pruning, provider adapters, personal adoption, and OS/client acceptance.
- Native local mode cannot hide edits to tracked configuration. Refuse the whole operation unless a verified native local override expresses it. Gemini has no documented project `settings.local.json`; never invent that path or bypass project trust with a system layer.
- Missing workflow dependencies must fail selection before writes. The missing `domain-modeling` dependency remains relevant; the interview fallback is not a portable distribution dependency policy.
- Tool Guardian blocked two oversized plan patches before mutation: `46899 bytes exceeds limit 32768 bytes` and `129 segments exceeds limit 128 segments`. Smaller independent patches succeeded. Keep future document mutations below both limits; do not disable the guard.
- Patch matching uses complete physical lines. A comparison-status patch failed before mutation because it used only the first two sentences of a longer paragraph. Reread exact lines and replace the complete paragraph or use an exact-count replacement; split unrelated edits.
- APM source citations initially used web extraction indices instead of physical source lines. Targeted verification corrected anchors in both owned files; unconfirmed anchors were removed. Verify code anchors against actual source files, not HTML extraction positions.

## Review findings

- APM supports committed payloads and an audit-only CI pattern, correcting the supplied research's manifest-only framing. Its normal install overwrites managed files, and its resolution transaction excludes native target outputs; an ownership wrapper would duplicate substantial lifecycle responsibility.
- ECC's catalog and semantic hook IDs are useful references. Its ordinary successful upgrade replaces managed files. Kimi-specific preflight is stronger but can finish partially. Deselection pruning was not verified.
- Skills-lock reinforces pins and content digests; frozen install still writes payloads. Superpowers and wshobson reinforce client adapters/native packages later. Skillet is skills-only and has inconsistent update maturity claims.
- APM's audit motivates checking committed files before any repair. Git's documented checkout conversion motivates declaring line-ending policy, retaining exact hashes, and testing fresh Windows clones. The comparison holds the accepted refinements and evidence limits.

## Verification

Milestone 3's initial 54 public cases passed before final hardening. Review reproduced a same-target parent link replacement overwriting an external temporary sentinel; POSIX descriptor operations now fix that case. Source kind/location/policy disagreement previously passed strict check and now has a passing repair case. Final review and full rerun are outstanding. A structurally valid extra lock item still permits unrelated-file pruning; a regular-directory replacement can still produce successful lock/content disagreement. Do not trust unfinished M3 acceptance. The first security-review worker stopped with a service content flag before a verdict; its partial concern was retained and reproduced by the writer, then a replacement reviewer continued.

Milestone 2 passes 17 public selection cases, 24 team-install cases, all 41 combined cases, and 14 runner cases. Independent code/security review approves without blocking findings. Compilation, OKF/whitespace, committed catalog listing, and actual repo-local exec-plans dependency installation pass. [The catalog audit](../agent-asset-installer/catalog-audit.md) records explicit required/conditional dependencies, support files, and unavailable chains. Maintained tracked prerequisites can declare a narrow `.agents/skills/<name>` source root without editing canonical authored skills. Optional prose mentions are excluded from dependency requirements. Agents/hooks remain unavailable to install until milestone 4.

Milestone 1 passes 24 public team-install cases, 14 aggregate-runner CLI cases, Python compileall, OKF lint, and whitespace checks. A committed-catalog smoke proves actual caveman files, immutable HEAD, unchanged index, and no-write repetition. Primary review reproduced an unlisted tracked file's clean filter executing during equal-length content verification; the implementer repaired transform preflight for all selected-root index paths. Review confirmed the repair before integration. Source-index stat-cache mutation and nested attribute cancellation are also repaired and documented.

The aggregate baseline exits `2` before suites because this macOS host lacks `flock`; prerequisites were not weakened. macOS has Python 3.14.6, Git 2.50.1, Bash 3.2.57, PowerShell 7.6.6, RTK 0.50.0, and Codex CLI 0.159.0. Other advertised client commands are absent from PATH. No native Windows/Linux job, live client, real-home installation, or hook delivery has run. These remain acceptance gates.

## Documentation pass

- Added: Milestone 1 public CLI, internal package, explicit catalog, and public subprocess suite.
- Changed: Milestone 1 source/test registry plus script instructions, API/file maps, script known issues/testing guidance, ExecPlan, and feature handoff reflect implemented behavior. Later milestones remain unimplemented.
- Split or moved: None. Retained research stays at the user-requested `docs/` location.
- Deduplicated: Accepted decisions live in the closed refinement ticket; execution requirements are incorporated in the self-contained ExecPlan.
- Index updates: Distribution map includes the closed refinement ticket. Existing canonical file-map wording is updated; memory INDEX remains unchanged because no memory file was added, removed, renamed, or repurposed.
- Remaining documentation quality TODOs: None.

Canonical targets are [repository instructions](../../.agents/instructions/repo.md), type `Agent Instruction`, and [the file map](../../.agents/memory/FILE_MAP.md), type `Agent Memory`. Frontmatter and unrelated content are preserved. OKF authoring uses the [profile branch](../../.agents/skills/okf-authoring/references/profile.md); the source-summary branch is not applicable.


## Retained implementation artifacts

- `/private/tmp/agent-assets-m3`: unfinished original M3 worktree and private branch. Do not clean it.
- `/private/tmp/agent-assets-probes/docs/agent-asset-installer/prerequisites.md`: observed local prerequisites and native gates, not yet promoted.
- `/private/tmp/agent-assets-probes/docs/agent-asset-installer/provider-runtime-audit.md`: canonical/provider loader, state, and registration anchors for M4, not yet promoted.
- `docs/agent-asset-installer/catalog-audit.md`: corrected M2 audit already committed; the older temporary audit is superseded.
- `/private/tmp/agent-assets-routing.json` and `/private/tmp/agent-assets-review-failure.txt`: applied model routing and failed review's preserved output/context.

The user confirms this Mac has Codex only. `flock` is needed for the aggregate repository test suite, not the selected skill-only installer. No dependency has been installed.
