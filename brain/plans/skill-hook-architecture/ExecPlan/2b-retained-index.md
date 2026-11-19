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

## Result

On Darwin 27.2.0, starting from candidate `7f16d86b` and rewritten plan merge `bbd5dbea`, the retained-noop control passed (one test, exit 0). The new installer regression first failed because the extra paragraph link yielded exit 0 and `Installation complete; brain/index.md verified`, instead of the required failure. After the repair it passed, including its reordered inventory, custom label and heading control and byte-preservation assertions.

The installer suite passed 30 tests (exit 0); the hook suite passed 27 tests with one skip (exit 0); generator check reported 15 current files (exit 0). An isolated Bash default installation and its Doctor and file readback passed; evidence is in `/tmp/verify-skills.17NToO/evidence`. That separate journey predates the final verifier-only adjustment. Provider execution, PowerShell, Windows and integrated proof remain coordinator work. Reflection found no additional durable note: the public regression and verifier enforce the discovered constraint.
