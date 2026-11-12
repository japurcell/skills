# Iteration 2: Standards and Spec review evidence

## Frozen review scope

- Branch under review: `codex/remove-hooks`
- Base and merge base: `5db7440017e081b4d391c92f28d325b2fccf95a0`
- Target commit: `a22ea7685f855f1e3033927efed42c6213b8ae5a`
- Reviewed commit range: `b295b31d` removal baseline, `84c0707c` iteration-1 plan evidence, `a22ea768` fixer commit.
- Excluded unrelated user edit: `skills/default/execplan-implement/SKILL.md`
- Source snapshot: `/tmp/retire-hooks-step7/iteration-2/source`
- Included-file list: `/tmp/retire-hooks-step7/iteration-2/included-files.txt`
- Snapshot SHA-256: `4c8b56f2510e2c5972fb003701cd4e5752f58702d4c51c15dfb589792ec5d1f3`
- Patch SHA-256: `de7d2cb2615532e95a1881578c42572d96015b99a2653c5b4dd95d0996adfe09`
- Diff: `git diff --binary 5db7440017e081b4d391c92f28d325b2fccf95a0...a22ea7685f855f1e3033927efed42c6213b8ae5a -- :(exclude)skills/default/execplan-implement/SKILL.md`
- Metadata: `/tmp/retire-hooks-step7/iteration-2/metadata.json`
- Captured UTC: `2026-11-12T07:19:12.445501+00:00`

## Review reports

- Standards report: `/tmp/retire-hooks-step7/iteration-2/standards-report.md`
- Spec report: `/tmp/retire-hooks-step7/iteration-2/spec-report.md`
- Both reviews were static; no tests were run. The disposable provider and gate results in the active ExecPlan were supplied by the coordinator/fixer and were not reproduced by these reviewers.

## Findings and disposition

- **Standards - Low, stale active plan:** The frozen target still dispatched T8a-T8c even though those changes were present. This finding was resolved by the current plan update, which marks T8a-T8c complete and makes the next unfinished action explicit. The finding reflects the frozen snapshot, not the current plan state.
- **Standards - Resolved:** Gemini array formatting and identical retired receipt factoring satisfy the two iteration-1 findings.
- **Spec - P2, installation manifest left behind:** The guide directed deleting only payload paths in `installation.json`'s `files` and `launchers` maps, followed by empty directories. The manifest is created separately by the legacy installer and is not listed in its own maps, so it remains at the bundle root. It is no longer executable after payload removal, but retirement leaves scanner-owned metadata behind.

### Accepted T8e resolution

The documentation implementer must state that all manifest paths are relative and confined within the bundle before deletion. Remove verified manifest-listed payloads, remove the root `installation.json` as the final ownership record, then remove empty directories. Preserve the bundle when its inventory, path confinement, ownership, or hashes are ambiguous. Do not use recursive or wildcard deletion, search user repositories, mutate user repositories automatically, or restore scanner runtime.

The third and final independent review must verify the updated path-confinement and cleanup sequence.
