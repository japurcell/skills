# M2. Direct brain reindex

Status: in progress
Acceptance: not met

## Tasks and prerequisites

The existing implementation is on `work/skill-arch-m2` at `7f16d86b`. Its rendered manual command is `reindex.py PROJECT`. The installer invokes the packaged `reindex.py PROJECT --verify` after the selected helper. The candidate adds the render target in `hooks/manifest.py` and ships both portable and repository-local commands.

**T2b, retained-index verification.** The M2 implementer owns the [repair assignment](2b-retained-index.md). The coordinator reproduced its failure against the actual installer. Stop after the public regression and freshness checks on the candidate.

**T2c, integrate and qualify.** After T2b passes, the coordinator integrates the corrected product changes, preserving these plan files. Compare fresh installation with the retained-helper route through the public installer, exercise generated hooks and the relocated direct command, and record native Windows results from the Windows runner. Run the combined bundle again once M7 lands.

## Source and interfaces

- `hooks/families/brain.py`
- `skills/default/brain-install/scripts/install.py`
- `skills/default/brain-install/assets/skills/brain/SKILL.md`
- `scripts/tests/hooks/test-brain-hooks.py`

## Manual and hook callers

Ship a standalone direct command in the portable brain skill, generated from the existing inventory owner. It accepts an explicit repository directory, including a directory without Git, and operates only on its immediate brain vault. It reads no event from stdin and reports failure with a nonzero exit. The installed manual calls this command even when the user has retained an older hook indexer. Existing provider registrations, standalone hook files, root discovery and nonblocking failure responses keep their contracts.

## Ownership of writes

Use the existing pinned vault, writer lock, traversal limits, curated-index rules and atomic publication. Missing or unwritable vaults fail. On a current index, check vault-directory writability with private temporary entries under that same lock, exercising create, replace and cleanup without touching index.md or changing its mtime. The probe establishes permissions on the vault directory for entries created by this process. Existing index.md can have additional replacement restrictions, for example through sticky-directory ownership or Windows delete permissions. If the inventory needs to change, the actual replacement must succeed; report a failure and preserve the previous index if the OS rejects it. An unchanged result claims only a current inventory and a writable vault directory. Report failures and clean up only temporary entries owned by the command.

## Installer compatibility

A clean installation runs the direct command. If --keep-existing retains a different hook indexer, run it once with the legacy Codex event. Choose the path before execution. After completion, use the trusted bundled inventory implementation in read-only verification mode against the explicit root. Under the vault lock, compute the expected current inventory and compare the actual root index’s Markdown link targets, including the curated-index and codebase rules. Require all and only the intended inventory entries and actual starter navigation. A stale result, invalid index, helper failure or timeout fails installation. Verification never repairs the output and never overwrites the retained custom file.

## Acceptance

Install without hooks, retain only a legacy indexer, add a root note and follow the installed manual. Verify the new link. An old index containing every starter link must fail after a custom no-op leaves out a new note. Cover removed notes, a nested root with only a parent vault, an unchanged index with stable mtime, a busy lock and a read-only vault with a writable pre-existing lock. Use a nonprivileged account for the latter. Exercise both generated provider hooks and a relocated direct command.

## Verification

Run from the checkout root. Each command must exit zero. Inspect the files or output specified above.

- `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests`
- `rtk proxy python3 scripts/tests/hooks/test-brain-hooks.py`
- `rtk proxy python3 scripts/generate-hooks.py --check`

## Progress

- [x] (2026-11-19) [milestone-2] Candidate 7f16d86b implements explicit-root indexing, retained-helper selection and read-only verification.
- [x] (2026-11-19) [milestone-2] Reproduced successful installation with an extra non-inventory link on the candidate.
- [x] (2026-11-19) [milestone-2] T2b verified at `658ab7e8` and integrated at `ebb09bb4`. The public installer rejects the extra link and preserves both files.
- [x] (2026-11-19) [milestone-2] T2c passed on macOS with integrated M7, generated-output freshness, standalone hooks and disposable Bash and PowerShell installs.
- [ ] [milestone-2] Qualify native Windows permission behavior.

## Candidate evidence

On macOS the worker recorded the direct command adding and removing a note, retaining the mtime of a current index and refusing a nested root without its own vault. At uid 501 a held lock and an unwritable vault with a writable lock both failed. The candidate record reports installer and hook suites with four and one skips respectively, and 15 current generator outputs. The worker reran the direct test after adding the removal assertion. The coordinator separately observed the extra-link false success through the installed retained-helper path. Native Windows and integrated proof are outstanding.
