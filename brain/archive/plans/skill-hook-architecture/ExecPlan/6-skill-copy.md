# M6. Skill tree copying

Status: done
Acceptance: met

## Tasks and prerequisites

The M6 worktree `work/skill-arch-m6` points at the original plan commit `66e3a80e`. The earlier Addy fixture pass is baseline evidence only.

**T6a, qualify the filesystem adapter.** The installer maintainer and a Windows runner compare a disposable prototype with the existing `Copy-Skills` path. Have the Python traversal classify links/reparse points without following them, omit excluded subtrees before enumeration, and produce an ordered stream of operations for a skill. Keep the PowerShell process alive for one skill to perform native link/junction creation, copying and mode handling. Feed a single operation sequence using structured JSON and literal paths, with success/failure reported by the native adapter. Compare the destination tree, link and junction targets, modes and failure cleanup with the existing installer. Stop after recording native results. If the candidate cannot preserve a behavior, keep the existing caller active, record the failed case and revise the adapter before switching it. [Assignment](6a-adapter.md)

**T6b, migrate callers.** With the two profiles below and T6a's adapter contract proven, extend `filtered_entries` and `copy_filtered` in the shared helper to own traversal, prune order and profiles. Reuse the POSIX copy batching and existing native PowerShell file operations. Bind Bash and PowerShell main to overlay and Addy to replace. Preserve existing helper options including prune-only and copy-command invocations. Remove skill-specific duplicate recursion only after its caller passes the same fixture. Stop after reinstall and failure recovery through each public installer. [Assignment](6b-migration.md)

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

- [x] (2026-11-19) [milestone-6] Real Windows junction and POSIX mode qualification passed before switching. [Windows prototype run](https://github.com/japurcell/skills/actions/runs/44493917647/job/135456168341)
- [x] (2026-11-19) [milestone-6] Integrated shared traversal and both profiles at `1b34cefc`. Bash, Addy and PowerShell reinstall and readback passed on macOS.
- [x] (2026-11-19) [milestone-6] The production Windows installer passed the junction and destination-preservation checks at `a482bbc0`. The [local evidence](6b-migration.md) records disposable real-asset selection, refresh and provider configuration. [Windows run](https://github.com/japurcell/skills/actions/runs/44496566199/job/135465141445)
