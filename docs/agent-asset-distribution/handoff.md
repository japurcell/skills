# Agent Asset Distribution Handoff

## Status

Wayfinding and implementation planning are complete. The user accepted all three test boundaries on 2026-09-29, then explicitly instructed not to start implementation yet. All seven implementation milestones remain open. No source, tests, scaffolding, or live installation has started. The [closed contract](tickets/choose-distribution-contract.md) remains authoritative and the [implementation ExecPlan](../agent-asset-installer/ExecPlan.md) records acceptance and the hold.

## Next step

Wait for the user's explicit request to start implementation. Do not write source, tests, or scaffolding while the hold applies. The public CLI/file effects, Bash/PowerShell entry points, and native discovery/hook execution are accepted test seams; do not ask again. When the user requests implementation, load `exec-plans` and `tdd`, then execute milestone 1: one pinned skill installed into a disposable team repository. Do not recreate the plan or reopen settled distribution choices.

## Important boundaries

- The user explicitly excluded a rollback feature. Restoring the currently recorded immutable revision is supported; a rollback command or retained installation history is not part of the contract.
- Keep this effort and its cited findings under `docs/agent-asset-distribution/`, as the user requested. Use [the map](map.md) as the closed decision index, [the recommendation](recommendation.md) for comparative evidence, and [the source inventory](local-inventory.md) for current code constraints.
- The user authorized the grilling/research fallback without the unavailable `domain-modeling` skill on 2026-09-29. Do not ask for that authorization again. Missing workflow dependencies still need explicit handling in the future distribution catalog.
- Acceptance of test boundaries does not authorize implementation. The user's explicit hold overrides the earlier proposed next step. Native publication and real-home mutations have not been requested.

## Implementation constraints and durable learnings

- The plan chooses one Python 3.11+ lifecycle engine with shell/PowerShell compatibility entry points. It covers catalog/dependencies, immutable provenance, owned files/configuration, branch updates and recorded restoration, pruning, provider adapters, personal adoption, and OS/client acceptance.
- Native local mode cannot hide edits to tracked configuration. Refuse the whole operation unless a verified native local override expresses it. Gemini has no documented project `settings.local.json`; never invent that path or bypass project trust with a system layer.
- Missing workflow dependencies must fail selection before writes. The missing `domain-modeling` dependency remains relevant; the interview fallback is not a portable distribution dependency policy.
- Tool Guardian blocked two oversized plan patches before mutation: `46899 bytes exceeds limit 32768 bytes` and `129 segments exceeds limit 128 segments`. Smaller independent patches succeeded. Keep future document mutations below both limits; do not disable the guard.

## Verification

The acceptance/hold update passes `rtk git diff --check` and read-only validation of 15 Markdown files, 69 local links, accepted test scope, the explicit implementation hold, and seven synchronized open milestones. Only this handoff and the ExecPlan changed. Prior planning OKF lint passed; canonical documents remain unchanged and their routing remains valid. Implementation acceptance remains not met; no implementation tests have run.

No live client installation was run. Codex hosted/cloud customization, Gemini extension-packaged agent maturity, and uniform native-plugin pinning remain unverified research limits. The local release-policy probe did not inspect remote hosting; see the source inventory's scoped findings.

## Documentation pass

- Added: None.
- Changed: This feature-scoped handoff and the ExecPlan's acceptance/hold state. No canonical knowledge changed.
- Split or moved: None. Retained research stays at the user-requested `docs/` location.
- Deduplicated: Replaced pending test-confirmation guidance with accepted boundaries and the explicit implementation hold.
- Index updates: None. Existing canonical routing remains valid; no memory document was added, removed, renamed, or repurposed.
- Remaining documentation quality TODOs: None.

Canonical targets are [repository instructions](../../.agents/instructions/repo.md), type `Agent Instruction`, and [the file map](../../.agents/memory/FILE_MAP.md), type `Agent Memory`. Frontmatter and unrelated content are preserved. OKF authoring uses the [profile branch](../../.agents/skills/okf-authoring/references/profile.md); the source-summary branch is not applicable.
