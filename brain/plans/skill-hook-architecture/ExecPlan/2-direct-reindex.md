# M2. Direct brain reindex

Status: in progress
Acceptance: not met

## Assignment

T2 belongs to the milestone implementer. Work from the repository root on a branch based on the committed plan. The committed plan is the only prerequisite. Reproduce any defect through the caller before editing. Stop when the behavior below is delivered, checks are recorded and any native evidence gap is named.

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

- [x] (2026-11-19) [milestone-2] Implement direct reindex, retained-helper selection and trusted inventory verification; exercise installed direct and stale retained helper.
- [ ] [milestone-2] Complete integrated and native Windows verification, and review remaining acceptance coverage.

## Observed evidence

- Disposable CLI reproduction: a hook invocation with no event exited zero and omitted a newly added note. The installed direct command now adds and removes that link, preserves the unchanged index mtime, and rejects a nested root without its own vault.
- Installer suite: 51 tests passed, four skipped; hook suite: 27 tests passed, one skipped. Generator check reports 15 current files. The new direct test was rerun after its deletion assertion and passed.
- On macOS as uid 501, a held writer lock and an unwritable vault with an existing writable lock both returned failure. Native Windows and final integrated proof remain outstanding.
- Session reflection: the stale-helper risk is enforced by the trusted verifier; no additional durable note was identified.
