# Agent Asset Distribution Handoff

## Status

Wayfinding is complete. All four tickets are closed, with no remaining contract question or fog. [Choose the Distribution Contract](tickets/choose-distribution-contract.md) is the authority for the user's approved choices. The contract has not been implemented or live-tested.

## Next step

When implementation work is requested, create an implementation ExecPlan under `docs/` from the closed contract. Use `exec-plans` before source edits and `tdd` for source design or implementation. The plan must cover the asset catalog and declared dependencies, ownership/provenance records, provider adapters, existing personal-install adoption, and public-process validation across the approved operating systems and product surfaces. Do not reopen settled contract choices.

## Important boundaries

- The user explicitly excluded a rollback feature. Restoring the currently recorded immutable revision is supported; a rollback command or retained installation history is not part of the contract.
- Keep this effort and its cited findings under `docs/agent-asset-distribution/`, as the user requested. Use [the map](map.md) as the closed decision index, [the recommendation](recommendation.md) for comparative evidence, and [the source inventory](local-inventory.md) for current code constraints.
- The user authorized the grilling/research fallback without the unavailable `domain-modeling` skill on 2026-09-29. Do not ask for that authorization again. Missing workflow dependencies still need explicit handling in the future distribution catalog.
- This completed effort authorized research and planning. Installer changes, native publication, and mutation of installed user directories belong to the next effort.

## Verification

`rtk proxy ./scripts/lint-okf.py` exited `0`, and `rtk git diff --check` passed. A read-only Markdown validator checked 14 files and 63 local links, all four closed resolutions, exact dependency filenames, the complete named decision index, and the retained `docs/` location. The scoped canonical diff contains exactly the two authorized routing documents listed below.

No live client installation was run. Codex hosted/cloud customization, Gemini extension-packaged agent maturity, and uniform native-plugin pinning remain unverified research limits. The local release-policy probe did not inspect remote hosting; see the source inventory's scoped findings.

## Documentation pass

- Added: This feature-scoped handoff. No canonical knowledge document was added.
- Changed: Decision ticket, map, recommendation, inventory, routing record, and the existing canonical distribution-routing entries.
- Split or moved: None in the resumed interview. The effort already resides in the user-requested `docs/` location.
- Deduplicated: Confirmed choices became one resolution in the decision ticket. Removed obsolete pending-interview guidance and duplicate validation history.
- Index updates: `FILE_MAP.md`. No memory document was added, removed, renamed, or repurposed, so `INDEX.md` needs no change.
- Remaining documentation quality TODOs: None.

Canonical targets are [repository instructions](../../.agents/instructions/repo.md), type `Agent Instruction`, and [the file map](../../.agents/memory/FILE_MAP.md), type `Agent Memory`. Frontmatter and unrelated content are preserved. OKF authoring uses the [profile branch](../../.agents/skills/okf-authoring/references/profile.md); the source-summary branch is not applicable.
