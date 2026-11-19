# M6. Skill tree copying

Status: open
Acceptance: not met

## Assignment

T6 belongs to the milestone implementer. Work from the repository root on a branch based on the committed plan. The committed plan is the only prerequisite. Reproduce any defect through the caller before editing. Stop when the behavior below is delivered, checks are recorded and any native evidence gap is named.

## Source and interfaces

- `scripts/install.sh`
- `scripts/install.ps1`
- `scripts/addy-install.sh`
- `scripts/rebase-skill-references.py`

## Policy and callers

One implementation determines skill traversal, artifact exclusion and prune order. Keep two explicit installation behaviors. The Bash and PowerShell main installers overlay selected skills, prune their current exclusions and stale artifacts, and rebase references. Addy replaces its selected skill destination and applies its existing test-file and artifact pruning, retaining allowed root README and eval content. Keep the shared helper’s existing argument combinations and exit behavior for these callers. Other copied assets retain their current owners.

## Native operations

Keep platform-specific link classification, junction handling, mode restoration and copy primitives at the filesystem adapter. The policy must classify an entry before descent. Excluded cache subtrees never reach traversal or the copier. Preserve existing merge, replace, ownership and failure-recovery rules, including read-only trees and destination links.

## Acceptance

For each public installer, install and then reinstall the same fixture containing a root README, eval data, a test script, an excluded cache directory and a destination-only note. Main installers remove README and eval exclusions while preserving the unrelated note. Addy retains permitted README and eval data and replaces the old destination-only note. Verify link targets and modes by readback and prove exclusions were never traversed. Exercise PowerShell on native Windows for junction behavior.

## Verification

Run from the checkout root. Each command must exit zero. Inspect the files or output specified above.

- `rtk proxy bash scripts/tests/installers/test-addy-install.sh`
- `rtk proxy bash scripts/tests/installers/test-install.sh`
- `rtk proxy pwsh -NoProfile -File scripts/tests/installers/test-install.ps1`

## Progress

- [ ] [milestone-6] Implement T6 and exercise the public entry points.
- [ ] [milestone-6] Verify integrated behavior and record platform evidence.
