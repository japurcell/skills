# Agent Asset Distribution Handoff

## Status

All eight decision/research tickets are closed. Architecture, strict offline `status --check`, checkout policy, and three test seams are accepted. The user explicitly requested full implementation through `execplan-implement` on 2026-09-29, lifting the earlier hold. Milestone 1 is in progress; milestones 2 through 7 remain open. The base branch is `codex/research-agent-distribution-options`. Implementers use isolated unpushed worktrees; integration is serialized.

## Next step

Implement milestone 1 through the public CLI seam with one failing subprocess behavior at a time. Integrate its clean tested branch, remove its worktree, then dispatch a fresh implementer for milestone 2. Follow the task graph and acceptance gates in [the ExecPlan](../agent-asset-installer/ExecPlan.md). Complete all milestones without reopening settled decisions. Never claim live client or native OS evidence that was not run.

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

`rtk proxy ./scripts/lint-okf.py` and `rtk git diff --check` pass. A read-only validator checks 23 Markdown files, 93 local links, eight closed ticket resolutions, no remaining planning question, the explicit hold, seven synchronized open implementation milestones, and the exact six-document scope. Only planning documents and one file-map phrase changed. No implementation tests have run. Research inspected first-party documentation and code without executing third-party installers or clients. Some citations use moving upstream `main`; release evidence is distinguished from inspected source.

No live client installation was run. Codex hosted/cloud customization, Gemini extension-packaged agent maturity, and uniform native-plugin pinning remain unverified research limits. The local release-policy probe did not inspect remote hosting; see the source inventory's scoped findings.

## Documentation pass

- Added: None.
- Changed: Refinement ticket, decision map, comparison, feature handoff, and ExecPlan to reflect accepted decisions; file-map wording remains independent of proposal status.
- Split or moved: None. Retained research stays at the user-requested `docs/` location.
- Deduplicated: Accepted decisions live in the closed refinement ticket; execution requirements are incorporated in the self-contained ExecPlan.
- Index updates: Distribution map includes the closed refinement ticket. Existing canonical file-map wording is updated; memory INDEX remains unchanged because no memory file was added, removed, renamed, or repurposed.
- Remaining documentation quality TODOs: None.

Canonical targets are [repository instructions](../../.agents/instructions/repo.md), type `Agent Instruction`, and [the file map](../../.agents/memory/FILE_MAP.md), type `Agent Memory`. Frontmatter and unrelated content are preserved. OKF authoring uses the [profile branch](../../.agents/skills/okf-authoring/references/profile.md); the source-summary branch is not applicable.
