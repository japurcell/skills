# T2b. Reject unexpected links after a retained helper runs

**Owner:** M2 implementer. **Prerequisite:** the direct command and installer candidate at `7f16d86b`. Work on `work/skill-arch-m2` in its existing worktree. Read this assignment from the rewritten plan on `work/skill-hook-architecture`. The [M2 contract](2-direct-reindex.md) defines the manual and hook interfaces.

## Reproduce through the installer

From the candidate checkout root run the existing retained-helper control:

    rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests -p test_install.py -k retained_noop

The coordinator reran this control on the candidate during the rewrite. One test ran and passed. In `InstallerTests` beside `test_retained_noop_indexer_cannot_accept_stale_inventory`, use its disposable copied bundle and physical target path. Apply the installer, save the generated index, and replace only the installed legacy helper with a successful no-op. Repeat with `--apply --index-reviewed --keep-existing .agents/skills/brain/scripts/auto-index-brain.py`. The control with the correct inventory must succeed. Append a paragraph containing `[extra](outside-inventory.md)` to that index and repeat. Assert nonzero exit, a verification diagnostic, and byte-for-byte preservation of the helper and the index on failure.

Observed on the candidate on 2026-11-19: both invocations exited zero, reported a verified index and left the extra link in place. The installer selects the right helper. The trusted verifier in the generated `reindex.py` ignores lines outside its full-bullet pattern.

## Repair and stop

Edit the inventory verification in `hooks/families/brain.py`, then regenerate the declared outputs with `rtk proxy python3 scripts/generate-hooks.py --write`. Compare the complete link inventory, including multiplicity, with targets computed under the existing vault lock. Preserve the intended tolerance for harmless label, heading or ordering differences in a retained index. Handle additional link-bearing text or reject an unsupported link structure explicitly. Keep verification read-only. After generation, copy the updated portable `auto-index-brain.py` and `reindex.py` from `skills/default/brain-install/assets/skills/brain/scripts/` into `.agents/skills/brain/scripts/`. Those repository-local peers are checked by the installer's parity test and are outside the generator manifest. Rerun the following checks.

    rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests -p test_install.py
    rtk proxy python3 scripts/tests/hooks/test-brain-hooks.py
    rtk proxy python3 scripts/generate-hooks.py --check

Stop when the new public regression changes from red to green, the valid control still succeeds, the existing stale/missing cases pass and generated files are current. Record the revision, exits, platform and skips. The coordinator owns integration and Windows qualification. If an attempted fix rejects a valid retained index, retain that fixture, narrow the verifier and repeat both cases.
