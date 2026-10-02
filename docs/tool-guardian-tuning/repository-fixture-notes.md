# Repository Fixture Notes

The pre-change `scripts/test-all.py` run passed 39 of 41 suites and exposed two repository-fixture assumptions. On macOS, `mktemp -d` can return a logical `/var/folders/...` path while `git rev-parse --show-toplevel` returns its physical `/private/var/folders/...` path. The Git-root fixture now compares against `pwd -P`; its fallback assertion still compares the exact `pwd` result.

The audit rotation fixture now puts its primary log, shadow log, lock, and backups in a disposable system temporary directory. It continues to check rotation for both logs and the `[mode=shadow]` entry. Provider helper modules now load under unique, registered package names whose specs supply the relative-import package, avoiding mismatched `__package__` warnings.

Evidence: `/private/tmp/tool-guardian-test-all.log` records the original Git-root path mismatch and the audit fixture's `PermissionError` while creating `.agents/scratchpad/test-artifacts`; it also records the `__package__ != __spec__.parent` warnings. Post-change validation passed with `bash scripts/test-repo-root.sh` and `python3 -W error::DeprecationWarning scripts/test_helpers.py` (16 tests).
