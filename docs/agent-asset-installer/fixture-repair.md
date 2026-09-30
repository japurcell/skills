# Aggregate Fixture Repair Notes

The aggregate test runner uses exact path assertions, so shell fixtures created
with `mktemp -d` should resolve the created directory through `pwd -P` before
comparing paths. On macOS, the temporary directory can be returned through
`/var` while scripts resolve the same location through `/private/var`.

Tests that create logs or repositories must use a disposable system temporary
directory rather than writing under repository-owned `.agents/scratchpad`.
Constrained worktrees can make that repository path unavailable, and the
existing cleanup should remove the temporary directory when the test finishes.

Python 3.14 warns when a dynamically loaded module's import name disagrees with
its `ModuleSpec.parent`. Give test-loaded helpers a consistent package-qualified
module name and register the matching sibling helper in `sys.modules`; this
preserves relative imports without assigning conflicting package metadata.

Tests using `subprocess.Popen` with pipes should close stdin to signal EOF and
close stdout and stderr after collecting the needed response. Put pipe cleanup
in `finally` so assertion failures do not leave descriptors open.

Observed on macOS with Python 3.14.6: before repair, `test-repo-root.sh` failed
on `/var` versus `/private/var`, `test_helpers.py` failed creating a scratchpad
fixture, and the probe suite passed while emitting two unclosed-reader warnings.
After repair, the root test passes, all 14 helper tests pass with deprecation
warnings treated as errors, and all 10 probe tests pass with resource warnings
treated as errors.

Orchestration correction: the worker initially used the base checkout because subsequent shell calls inherited the default working directory. Its four owned files were copied by verified SHA-256 into the assigned private worktree; only the exact three tracked base test files and copied note were restored or removed. Other edits were preserved. Every subsequent command explicitly sets its worktree and checks its branch before mutation.
