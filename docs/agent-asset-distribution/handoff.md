# Agent Asset Distribution Handoff

## Status

Wayfinding and implementation planning are complete. All four decision tickets remain closed. [Choose the Distribution Contract](tickets/choose-distribution-contract.md) remains the authority for approved choices. The separate [implementation ExecPlan](../agent-asset-installer/ExecPlan.md) defines seven milestones. No source implementation or live installation has started.

## Next step

Confirm the proposed test seams with the user before writing tests: the public installer/updater subprocess CLI and its file/configuration effects, existing Bash/PowerShell entry points, and native discovery plus registered hook execution. The `tdd` skill requires explicitly agreed seams. This confirmation has not yet been received. When implementation is authorized and seams are accepted, load `exec-plans` and `tdd`, then execute milestone 1: one pinned skill installed into a disposable team repository. Update the plan and this handoff as work proceeds. Do not recreate the plan or reopen settled distribution choices.

## Important boundaries

- The user explicitly excluded a rollback feature. Restoring the currently recorded immutable revision is supported; a rollback command or retained installation history is not part of the contract.
- Keep this effort and its cited findings under `docs/agent-asset-distribution/`, as the user requested. Use [the map](map.md) as the closed decision index, [the recommendation](recommendation.md) for comparative evidence, and [the source inventory](local-inventory.md) for current code constraints.
- The user authorized the grilling/research fallback without the unavailable `domain-modeling` skill on 2026-09-29. Do not ask for that authorization again. Missing workflow dependencies still need explicit handling in the future distribution catalog.
- This resumed session completes the inherited planning step only. Installer changes belong to execution of the separate plan. Native publication and real-home mutations have not been requested.

## Implementation constraints and durable learnings

- The plan chooses one Python 3.11+ lifecycle engine with shell/PowerShell compatibility entry points. It covers catalog/dependencies, immutable provenance, owned files/configuration, branch updates and recorded restoration, pruning, provider adapters, personal adoption, and OS/client acceptance.
- Native local mode cannot hide edits to tracked configuration. Refuse the whole operation unless a verified native local override expresses it. Gemini has no documented project `settings.local.json`; never invent that path or bypass project trust with a system layer.
- Missing workflow dependencies must fail selection before writes. The missing `domain-modeling` dependency remains relevant; the interview fallback is not a portable distribution dependency policy.
- Tool Guardian blocked two oversized plan patches before mutation: `46899 bytes exceeds limit 32768 bytes` and `129 segments exceeds limit 128 segments`. Smaller independent patches succeeded. Keep future document mutations below both limits; do not disable the guard.

## Verification

`rtk proxy ./scripts/lint-okf.py` exits `0`, and `rtk git diff --check` passes. A read-only validator checks 15 Markdown files and 69 local links, all required plan sections, seven synchronized open milestones, and four closed decision resolutions. The canonical diff changes only the two routing documents listed below. Implementation acceptance remains not met; no future test command listed in the plan has run.

No live client installation was run. Codex hosted/cloud customization, Gemini extension-packaged agent maturity, and uniform native-plugin pinning remain unverified research limits. The local release-policy probe did not inspect remote hosting; see the source inventory's scoped findings.

## Documentation pass

- Added: The separate implementation ExecPlan. No canonical knowledge document was added.
- Changed: This feature-scoped handoff, current map/recommendation routing, and the two canonical routing entries.
- Split or moved: None. Retained research stays at the user-requested `docs/` location.
- Deduplicated: Replaced obsolete next-step guidance with the implementation plan and current resume gate.
- Index updates: `FILE_MAP.md`. No memory document was added, removed, renamed, or repurposed, so `INDEX.md` needs no change.
- Remaining documentation quality TODOs: None.

Canonical targets are [repository instructions](../../.agents/instructions/repo.md), type `Agent Instruction`, and [the file map](../../.agents/memory/FILE_MAP.md), type `Agent Memory`. Frontmatter and unrelated content are preserved. OKF authoring uses the [profile branch](../../.agents/skills/okf-authoring/references/profile.md); the source-summary branch is not applicable.
